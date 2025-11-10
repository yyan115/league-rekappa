import requests
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

class RiotAPIClient:
    def __init__(self, api_key: str, region: str = "na1", rate_limit_callback=None):
        self.api_key = api_key
        self.region = region
        self.rate_limit_callback = rate_limit_callback

        # Regional routing - different for account-v1 vs match-v5!
        # account-v1: americas, asia, europe (3 values)
        # match-v5: americas, asia, europe, sea (4 values)

        # Account API routing (for PUUID lookups)
        account_routing = {
            'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
            'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
            'kr': 'asia', 'jp1': 'asia',
            'oc1': 'asia', 'sg2': 'asia', 'th2': 'asia', 'tw2': 'asia', 'vn2': 'asia', 'ph2': 'asia',
        }

        # Match API routing (for match history)
        match_routing = {
            'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
            'euw1': 'europe', 'eun1': 'europe', 'tr1': 'europe', 'ru': 'europe',
            'kr': 'asia', 'jp1': 'asia',
            'oc1': 'sea', 'sg2': 'sea', 'th2': 'sea', 'tw2': 'sea', 'vn2': 'sea', 'ph2': 'sea',
        }

        self.account_routing = account_routing.get(region, 'americas')
        self.match_routing = match_routing.get(region, 'americas')
        self.regional_url = f"https://{self.match_routing}.api.riotgames.com"

        # Platform endpoint (just use region directly)
        self.base_url = f"https://{region}.api.riotgames.com"
        
        # Cache for summoner IDs (since we need to get them from puuid now)
        self._summoner_cache = {}
        
    def _make_request(self, url: str, retries: int = 3) -> Optional[Dict]:
        """Make API request with retry logic"""
        headers = {"X-Riot-Token": self.api_key}
        
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    retry_after = int(response.headers.get('Retry-After', 1))
                    print(f"[RATE_LIMIT] Waiting {retry_after} seconds...")
                    if self.rate_limit_callback:
                        self.rate_limit_callback(retry_after)
                    time.sleep(retry_after)
                elif response.status_code == 404:
                    return None
                else:
                    print(f"Error {response.status_code}: {response.text}")
                    return None
            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(1)
        
        return None
    
    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """Get account info by Riot ID (new format: GameName#TAG)"""
        account_url = f"https://{self.account_routing}.api.riotgames.com"
        url = f"{account_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        print(f"DEBUG: Calling account API: {url}")
        return self._make_request(url)
    
    def get_summoner_by_puuid(self, puuid: str) -> Optional[Dict]:
        """Get summoner info by PUUID - includes workaround for missing ID"""
        # Check cache first
        if puuid in self._summoner_cache:
            return self._summoner_cache[puuid]
        
        url = f"{self.base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        result = self._make_request(url)
        
        if result:
            # NEW: If 'id' is missing, we need to get it from league entries
            if 'id' not in result:
                print(f"INFO: Summoner ID missing from API, fetching via alternative method...")
                # Try to get it from league entries by searching with PUUID
                # This is a workaround - we'll get the encrypted ID from match history participants
                result['id'] = None  # Mark as unknown for now
                result['_needs_id_lookup'] = True
            
            # Cache it
            self._summoner_cache[puuid] = result
        
        return result
    
    def get_summoner_id_from_match(self, puuid: str) -> Optional[str]:
        """Workaround: Get encrypted summoner ID from a recent match"""
        # Get a recent match
        match_ids = self.get_match_ids(puuid, count=1)
        if not match_ids:
            return None
        
        # Get match details
        match = self.get_match_details(match_ids[0])
        if not match:
            return None
        
        # Find the participant with this PUUID and get their summonerId
        for participant in match['info']['participants']:
            if participant.get('puuid') == puuid:
                return participant.get('summonerId')
        
        return None
    
    def get_summoner_by_name(self, summoner_name: str) -> Optional[Dict]:
        """Get summoner info by name - handles Riot ID format (Name#TAG)"""
        # Must be in Riot ID format (Name#TAG)
        if '#' not in summoner_name:
            # Add default tag based on region
            default_tags = {
                'na1': 'NA1',
                'euw1': 'EUW',
                'eun1': 'EUNE',
                'kr': 'KR',
                'br1': 'BR1',
                'la1': 'LAN',
                'la2': 'LAS',
                'oc1': 'OCE',
                'tr1': 'TR1',
                'ru': 'RU',
                'jp1': 'JP1',
                'sg2': 'SG2',
                'th2': 'TH2',
                'tw2': 'TW2',
                'vn2': 'VN2',
                'ph2': 'PH2',
            }
            tag = default_tags.get(self.region, 'NA1')
            summoner_name = f"{summoner_name}#{tag}"
            print(f"INFO: No # found, trying with default tag: {summoner_name}")
        
        parts = summoner_name.split('#')
        game_name = parts[0]
        tag_line = parts[1] if len(parts) > 1 else 'NA1'
        
        # Get account info (has PUUID)
        account = self.get_account_by_riot_id(game_name, tag_line)
        if not account:
            return None
        
        puuid = account['puuid']
        
        # Get summoner info
        summoner = self.get_summoner_by_puuid(puuid)
        if not summoner:
            return None
        
        # If ID is missing, try to get it from a match
        if summoner.get('_needs_id_lookup'):
            summoner_id = self.get_summoner_id_from_match(puuid)
            if summoner_id:
                summoner['id'] = summoner_id
                del summoner['_needs_id_lookup']
                print(f"INFO: Successfully retrieved summoner ID from match history")
            else:
                print(f"WARNING: Could not retrieve summoner ID")
        
        return summoner
    
    def get_match_ids(self, puuid: str, count: int = 100, start_time: Optional[int] = None) -> List[str]:
        """Get match IDs for a player"""
        url = f"{self.regional_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}&type=ranked"
        if start_time:
            url += f"&startTime={start_time}"

        print(f"DEBUG: Fetching match IDs from: {url}")
        result = self._make_request(url)
        print(f"DEBUG: Got {len(result) if result else 0} match IDs")
        return result if result else []
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed match information"""
        url = f"{self.regional_url}/lol/match/v5/matches/{match_id}"
        return self._make_request(url)
    
    def get_rank(self, summoner_id: str) -> Optional[List[Dict]]:
        """Get rank information for a summoner (OLD method, prefer get_rank_by_puuid)"""
        if not summoner_id:
            print("ERROR: Cannot get rank - summoner ID is None")
            return None
        
        url = f"{self.base_url}/lol/league/v4/entries/by-summoner/{summoner_id}"
        return self._make_request(url)
    
    def get_rank_by_puuid(self, puuid: str) -> Optional[List[Dict]]:
        """Get rank information using PUUID directly (NEW method - preferred)"""
        if not puuid:
            print("ERROR: Cannot get rank - PUUID is None")
            return None
        
        url = f"{self.base_url}/lol/league/v4/entries/by-puuid/{puuid}"
        return self._make_request(url)
    
    def get_champion_mastery(self, puuid: str) -> Optional[List[Dict]]:
        """Get champion mastery for a player"""
        url = f"{self.base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        return self._make_request(url)

def get_rank_tier(rank_info: List[Dict]) -> Optional[str]:
    """Extract ranked tier from rank info (for Ranked Solo/Duo)"""
    if not rank_info:
        return None
    
    for queue in rank_info:
        if queue.get('queueType') == 'RANKED_SOLO_5x5':
            tier = queue.get('tier', '')
            division = queue.get('rank', '')
            return f"{tier} {division}"
    
    return None

def compare_ranks(rank1: str, rank2: str) -> int:
    """Compare two ranks. Returns 1 if rank1 > rank2, -1 if rank1 < rank2, 0 if equal"""
    tier_order = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    division_order = ['IV', 'III', 'II', 'I']
    
    if not rank1 or not rank2:
        return 0
    
    # Parse ranks
    parts1 = rank1.split()
    parts2 = rank2.split()
    
    if len(parts1) < 2 or len(parts2) < 2:
        return 0
    
    tier1, div1 = parts1[0], parts1[1]
    tier2, div2 = parts2[0], parts2[1]
    
    # Compare tiers
    try:
        tier1_idx = tier_order.index(tier1)
        tier2_idx = tier_order.index(tier2)
        
        if tier1_idx > tier2_idx:
            return 1
        elif tier1_idx < tier2_idx:
            return -1
        
        # Same tier, compare divisions
        if div1 in division_order and div2 in division_order:
            div1_idx = division_order.index(div1)
            div2_idx = division_order.index(div2)
            
            if div1_idx < div2_idx:  # Lower index = higher division
                return 1
            elif div1_idx > div2_idx:
                return -1
        
        return 0
    except (ValueError, IndexError):
        return 0

def is_higher_rank(rank: str, base_rank: str, min_tiers: int = 1, max_tiers: int = 2) -> bool:
    """Check if rank is 1-2 tiers higher than base_rank"""
    tier_order = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    
    if not rank or not base_rank:
        return False
    
    rank_tier = rank.split()[0]
    base_tier = base_rank.split()[0]
    
    try:
        rank_idx = tier_order.index(rank_tier)
        base_idx = tier_order.index(base_tier)
        
        diff = rank_idx - base_idx
        return min_tiers <= diff <= max_tiers
    except (ValueError, IndexError):
        return False