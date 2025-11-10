from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import json
import time
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta

from riot_api import RiotAPIClient, get_rank_tier
from analysis import (
    calculate_player_stats,
    aggregate_stats,
    detect_achievements
)
from bedrock_client import BedrockClient
from pro_players import PRO_PLAYERS, get_pro_by_id, get_all_teams

# Load environment variables
load_dotenv()

app = FastAPI(title="Roast Player API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
riot_client = RiotAPIClient(
    api_key=os.getenv('RIOT_API_KEY'),
    region=os.getenv('DEFAULT_REGION', 'na1')
)
bedrock_client = BedrockClient()

class AnalysisRequest(BaseModel):
    summoner_name: str
    region: Optional[str] = "na1"
    pro_player_id: Optional[str] = None  # Optional pro player comparison

class PostcardResponse(BaseModel):
    status: str
    mode: str  # "year_review" or "pro_comparison"
    your_rank: str
    your_stats: Dict
    pro_stats: Optional[Dict] = None
    pro_info: Optional[Dict] = None
    postcards: List[Dict]  # List of postcard data

@app.get("/")
async def root():
    return {
        "message": "Roast Player API - League Year in Review",
        "status": "running",
        "endpoints": {
            "analyze": "/analyze",
            "pro_players": "/pro-players",
            "health": "/health"
        }
    }

@app.get("/pro-players")
async def get_pro_players():
    """Get list of all pro players organized by league/team"""
    teams_by_league = get_all_teams()

    # Organize players by league and team
    organized = {}
    for league in ['LCK', 'LEC', 'LCS', 'LTA']:
        organized[league] = {}

    for pro_id, pro_data in PRO_PLAYERS.items():
        league = pro_data['league']
        team = pro_data['team']

        if league not in organized:
            organized[league] = {}
        if team not in organized[league]:
            organized[league][team] = []

        organized[league][team].append({
            'id': pro_id,
            'name': pro_data['name'],
            'role': pro_data['role'],
            'riot_id': pro_data['riot_id']
        })

    return organized

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/regenerate-roasts")
async def regenerate_roasts(request: dict):
    """Regenerate roasts from cached stats"""
    try:
        your_stats = request.get('your_stats')
        your_rank = request.get('your_rank')
        achievements = request.get('achievements', [])
        used_topics = request.get('used_topics', [])

        postcards, new_topics = bedrock_client.generate_year_review_postcards(
            your_stats,
            your_rank,
            achievements,
            used_topics
        )

        return {"postcards": postcards, "used_topics": new_topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-stream")
async def analyze_player_stream(request: AnalysisRequest):
    """Streaming version with progress updates"""
    rate_limit_message = {"message": None}

    def rate_limit_callback(seconds):
        msg = f"Rate limited. Waiting {seconds}s..."
        rate_limit_message["message"] = msg
        print(f"[CALLBACK] Rate limit callback triggered: {msg}")

    async def generate():
        try:
            summoner_name = request.summoner_name
            region = request.region or "na1"
            pro_player_id = request.pro_player_id

            # Set callback for rate limits
            riot_client.rate_limit_callback = rate_limit_callback

            # Update riot client region if needed
            if region != riot_client.region:
                riot_client.region = region
                riot_client.base_url = f"https://{region}.api.riotgames.com"

                # Update routing (account-v1 and match-v5 are different!)
                account_routing = {
                    'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
                    'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
                    'kr': 'asia', 'jp1': 'asia',
                    'oc1': 'asia', 'sg2': 'asia', 'th2': 'asia', 'tw2': 'asia', 'vn2': 'asia', 'ph2': 'asia',
                }
                match_routing = {
                    'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
                    'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
                    'kr': 'asia', 'jp1': 'asia',
                    'oc1': 'sea', 'sg2': 'sea', 'th2': 'sea', 'tw2': 'sea', 'vn2': 'sea', 'ph2': 'sea',
                }
                riot_client.account_routing = account_routing.get(region, 'americas')
                riot_client.match_routing = match_routing.get(region, 'americas')
                riot_client.regional_url = f"https://{riot_client.match_routing}.api.riotgames.com"

            yield f"data: {json.dumps({'progress': 'Looking up summoner...', 'status': 'running'})}\n\n"

            # 1. Get summoner info
            summoner = riot_client.get_summoner_by_name(summoner_name)
            if not summoner:
                yield f"data: {json.dumps({'error': f'Summoner not found. Use format: Name#TAG'})}\n\n"
                return

            if 'puuid' not in summoner:
                yield f"data: {json.dumps({'error': 'Invalid summoner data received'})}\n\n"
                return

            puuid = summoner['puuid']

            yield f"data: {json.dumps({'progress': 'Getting current rank...', 'status': 'running'})}\n\n"

            # 2. Get current rank
            rank_info = riot_client.get_rank_by_puuid(puuid)
            your_rank = get_rank_tier(rank_info)

            if not your_rank:
                yield f"data: {json.dumps({'error': 'Player has no ranked games this season'})}\n\n"
                return

            yield f"data: {json.dumps({'progress': 'Fetching match history...', 'status': 'running'})}\n\n"

            # 3. Get match history
            start_of_year = int(datetime(2025, 1, 1).timestamp())
            match_ids = riot_client.get_match_ids(puuid, count=100, start_time=start_of_year)
            print(f"DEBUG: Found {len(match_ids)} matches from 2025. PUUID: {puuid}, Region: {region}, Match Routing: {riot_client.match_routing}")

            if len(match_ids) < 10:
                yield f"data: {json.dumps({'error': 'Not enough ranked games from 2025 (need at least 10)'})}\n\n"
                return

            # 4. Get match details with per-match progress
            matches = []
            total_matches = min(len(match_ids), 100)
            current_progress = ""
            last_rate_limit_time = 0

            for idx, match_id in enumerate(match_ids[:100], 1):
                current_progress = f'Analyzing matches ({idx}/{total_matches})...'
                yield f"data: {json.dumps({'progress': current_progress, 'status': 'running'})}\n\n"

                # Call get_match_details - it will return None immediately if rate limited
                match_detail = riot_client.get_match_details(match_id)

                # Check if we got rate limited (riot_client.pending_rate_limit will be set)
                if riot_client.pending_rate_limit:
                    wait_seconds = riot_client.pending_rate_limit
                    print(f"[YIELD] Rate limited! Showing countdown on frontend...")

                    # Countdown while yielding updates
                    for remaining in range(wait_seconds, 0, -1):
                        rate_msg = f'Rate limited. Waiting {remaining}s...'
                        yield f"data: {json.dumps({'progress': current_progress, 'rate_limit': rate_msg, 'status': 'running'})}\n\n"
                        time.sleep(1)

                    # Clear the rate limit and retry the call
                    riot_client.pending_rate_limit = None
                    rate_limit_message["message"] = None
                    match_detail = riot_client.get_match_details(match_id)

                if match_detail and match_detail['info'].get('queueId') == 420:
                    matches.append(match_detail)

            if len(matches) < 10:
                yield f"data: {json.dumps({'error': 'Not enough valid ranked games found'})}\n\n"
                return

            # Calculate stats
            your_raw_stats = calculate_player_stats(matches, puuid)
            your_aggregated = aggregate_stats(your_raw_stats)
            achievements = detect_achievements(your_raw_stats, your_aggregated)

            yield f"data: {json.dumps({'progress': 'Generating roasts...', 'status': 'running'})}\n\n"

            # Generate postcards
            postcards, used_topics = bedrock_client.generate_year_review_postcards(
                your_aggregated,
                your_rank,
                achievements
            )

            # Send final result
            result = {
                'status': 'success',
                'mode': 'year_review',
                'your_rank': your_rank,
                'your_stats': your_aggregated,
                'achievements': achievements,
                'postcards': postcards,
                'used_topics': used_topics
            }

            yield f"data: {json.dumps({'result': result})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/analyze", response_model=PostcardResponse)
async def analyze_player(request: AnalysisRequest):
    """
    Main analysis endpoint
    Generates year-in-review OR pro comparison based on request
    """
    try:
        summoner_name = request.summoner_name
        region = request.region or "na1"
        pro_player_id = request.pro_player_id

        # Update riot client region if needed
        if region != riot_client.region:
            riot_client.region = region
            riot_client.base_url = f"https://{region}.api.riotgames.com"

            # Update routing (account-v1 and match-v5 are different!)
            account_routing = {
                'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
                'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
                'kr': 'asia', 'jp1': 'asia',
                'oc1': 'asia', 'sg2': 'asia', 'th2': 'asia', 'tw2': 'asia', 'vn2': 'asia', 'ph2': 'asia',
            }
            match_routing = {
                'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
                'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
                'kr': 'asia', 'jp1': 'asia',
                'oc1': 'sea', 'sg2': 'sea', 'th2': 'sea', 'tw2': 'sea', 'vn2': 'sea', 'ph2': 'sea',
            }
            riot_client.account_routing = account_routing.get(region, 'americas')
            riot_client.match_routing = match_routing.get(region, 'americas')
            riot_client.regional_url = f"https://{riot_client.match_routing}.api.riotgames.com"

        print(f"[1/5] Looking up summoner: {summoner_name}")
        # 1. Get summoner info
        summoner = riot_client.get_summoner_by_name(summoner_name)
        if not summoner:
            raise HTTPException(status_code=404, detail=f"Summoner '{summoner_name}' not found. Make sure to use format: Name#TAG (e.g., Doublelift#NA1)")

        if 'puuid' not in summoner:
            raise HTTPException(status_code=500, detail=f"Invalid summoner data received. Keys: {list(summoner.keys())}")

        puuid = summoner['puuid']

        # 2. Get current rank using PUUID directly
        print(f"[2/5] Getting current rank...")
        rank_info = riot_client.get_rank_by_puuid(puuid)
        your_rank = get_rank_tier(rank_info)

        if not your_rank:
            raise HTTPException(status_code=400, detail="Player has no ranked games this season")

        # 3. Get match history
        print(f"[3/5] Fetching match history...")
        start_of_year = int(datetime(2025, 1, 1).timestamp())
        match_ids = riot_client.get_match_ids(puuid, count=100, start_time=start_of_year)

        if len(match_ids) < 10:
            raise HTTPException(status_code=400, detail="Not enough ranked games from 2025 (need at least 10)")

        # 4. Get match details
        print(f"[4/5] Analyzing {len(match_ids)} matches...")
        matches = []
        for match_id in match_ids[:100]:
            match_detail = riot_client.get_match_details(match_id)
            if match_detail and match_detail['info'].get('queueId') == 420:  # Ranked Solo
                matches.append(match_detail)

        if len(matches) < 10:
            raise HTTPException(status_code=400, detail="Not enough valid ranked games found")

        # Calculate your stats
        your_raw_stats = calculate_player_stats(matches, puuid)
        your_aggregated = aggregate_stats(your_raw_stats)

        # Detect achievements/badges
        achievements = detect_achievements(your_raw_stats, your_aggregated)

        # MODE SELECTION: Pro comparison or Year review
        mode = "pro_comparison" if pro_player_id else "year_review"

        if mode == "pro_comparison":
            print(f"[5/5] Comparing with pro player...")
            # Get pro player info
            pro_info = get_pro_by_id(pro_player_id)
            if not pro_info:
                raise HTTPException(status_code=404, detail=f"Pro player '{pro_player_id}' not found")

            # Fetch pro player stats
            pro_region = pro_info['region']
            pro_riot_id = pro_info['riot_id']

            # Update region for pro if needed
            if pro_region != riot_client.region:
                riot_client.region = pro_region
                riot_client.base_url = f"https://{pro_region}.api.riotgames.com"

                # Update routing (account-v1 and match-v5 are different!)
                account_routing = {
                    'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
                    'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
                    'kr': 'asia', 'jp1': 'asia',
                    'oc1': 'asia', 'sg2': 'asia', 'th2': 'asia', 'tw2': 'asia', 'vn2': 'asia', 'ph2': 'asia',
                }
                match_routing = {
                    'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
                    'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
                    'kr': 'asia', 'jp1': 'asia',
                    'oc1': 'sea', 'sg2': 'sea', 'th2': 'sea', 'tw2': 'sea', 'vn2': 'sea', 'ph2': 'sea',
                }
                riot_client.account_routing = account_routing.get(pro_region, 'americas')
                riot_client.match_routing = match_routing.get(pro_region, 'americas')
                riot_client.regional_url = f"https://{riot_client.match_routing}.api.riotgames.com"

            pro_summoner = riot_client.get_summoner_by_name(pro_riot_id)
            if not pro_summoner:
                raise HTTPException(status_code=404, detail=f"Pro player account '{pro_riot_id}' not found")

            pro_puuid = pro_summoner['puuid']
            pro_rank_info = riot_client.get_rank_by_puuid(pro_puuid)
            pro_rank = get_rank_tier(pro_rank_info) or "Unknown"

            # Get pro match history
            pro_match_ids = riot_client.get_match_ids(pro_puuid, count=100, start_time=start_of_year)
            pro_matches = []
            for match_id in pro_match_ids[:100]:
                match_detail = riot_client.get_match_details(match_id)
                if match_detail and match_detail['info'].get('queueId') == 420:
                    pro_matches.append(match_detail)

            if len(pro_matches) < 5:
                raise HTTPException(status_code=400, detail=f"{pro_info['name']} doesn't have enough ranked games")

            pro_raw_stats = calculate_player_stats(pro_matches, pro_puuid)
            pro_aggregated = aggregate_stats(pro_raw_stats)

            # Generate comparison postcards
            postcards = bedrock_client.generate_comparison_postcards(
                your_aggregated,
                pro_aggregated,
                your_rank,
                pro_rank,
                pro_info['name'],
                pro_info['team']
            )

            return PostcardResponse(
                status="success",
                mode="pro_comparison",
                your_rank=your_rank,
                your_stats=your_aggregated,
                pro_stats=pro_aggregated,
                pro_info={
                    'name': pro_info['name'],
                    'team': pro_info['team'],
                    'role': pro_info['role'],
                    'rank': pro_rank
                },
                postcards=postcards
            )

        else:  # year_review mode
            print(f"[5/5] Generating year review postcards...")

            # Generate year review postcards
            postcards = bedrock_client.generate_year_review_postcards(
                your_aggregated,
                your_rank,
                achievements
            )

            return PostcardResponse(
                status="success",
                mode="year_review",
                your_rank=your_rank,
                your_stats=your_aggregated,
                postcards=postcards
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)