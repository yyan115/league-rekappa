from typing import List, Dict, Optional
from datetime import datetime, timedelta
from riot_api import RiotAPIClient, get_rank_tier, compare_ranks, is_higher_rank
import statistics

def extract_players_from_matches(matches: List[Dict], your_puuid: str) -> List[Dict]:
    """Extract all players from match history (excluding yourself)"""
    players = {}
    
    for match in matches:
        if not match or 'info' not in match:
            continue
            
        for participant in match['info']['participants']:
            puuid = participant.get('puuid')
            
            if puuid == your_puuid or not puuid:
                continue
            
            if puuid not in players:
                players[puuid] = {
                    'puuid': puuid,
                    'summonerName': participant.get('summonerName'),
                    'summonerId': participant.get('summonerId'),
                    'role': participant.get('teamPosition'),
                    'matches_encountered': 0
                }
            
            players[puuid]['matches_encountered'] += 1
    
    return list(players.values())

def calculate_player_stats(matches: List[Dict], puuid: str) -> Dict:
    """Calculate aggregate stats for a player"""
    stats = {
        'total_games': 0,
        'wins': 0,
        'kills': [],
        'deaths': [],
        'assists': [],
        'cs': [],
        'game_durations': [],
        'vision_scores': [],
        'damage_share': [],
        'win_streaks': [],
        'loss_streaks': [],
        'champions': {}
    }
    
    current_win_streak = 0
    current_loss_streak = 0
    
    for match in matches:
        if not match or 'info' not in match:
            continue
        
        # Find this player in the match
        player_data = None
        for p in match['info']['participants']:
            if p.get('puuid') == puuid:
                player_data = p
                break
        
        if not player_data:
            continue
        
        stats['total_games'] += 1
        
        # Win/Loss tracking
        if player_data.get('win'):
            stats['wins'] += 1
            current_win_streak += 1
            if current_loss_streak > 0:
                stats['loss_streaks'].append(current_loss_streak)
                current_loss_streak = 0
        else:
            current_loss_streak += 1
            if current_win_streak > 0:
                stats['win_streaks'].append(current_win_streak)
                current_win_streak = 0
        
        # KDA stats
        stats['kills'].append(player_data.get('kills', 0))
        stats['deaths'].append(player_data.get('deaths', 0))
        stats['assists'].append(player_data.get('assists', 0))
        
        # CS stats
        total_cs = player_data.get('totalMinionsKilled', 0) + player_data.get('neutralMinionsKilled', 0)
        game_duration_min = match['info'].get('gameDuration', 0) / 60
        if game_duration_min > 0:
            stats['cs'].append(total_cs / game_duration_min)
            stats['game_durations'].append(game_duration_min)
        
        # Vision
        stats['vision_scores'].append(player_data.get('visionScore', 0))
        
        # Damage share
        team_id = player_data.get('teamId')
        team_damage = sum(p.get('totalDamageDealtToChampions', 0) 
                         for p in match['info']['participants'] 
                         if p.get('teamId') == team_id)
        player_damage = player_data.get('totalDamageDealtToChampions', 0)
        
        if team_damage > 0:
            stats['damage_share'].append((player_damage / team_damage) * 100)
        
        # Champion tracking
        champ = player_data.get('championName', 'Unknown')
        if champ not in stats['champions']:
            stats['champions'][champ] = {'games': 0, 'wins': 0}
        stats['champions'][champ]['games'] += 1
        if player_data.get('win'):
            stats['champions'][champ]['wins'] += 1
    
    # Add final streaks
    if current_win_streak > 0:
        stats['win_streaks'].append(current_win_streak)
    if current_loss_streak > 0:
        stats['loss_streaks'].append(current_loss_streak)
    
    return stats

def aggregate_stats(stats: Dict) -> Dict:
    """Calculate averages and aggregates from raw stats"""
    def safe_avg(lst):
        return statistics.mean(lst) if lst else 0
    
    def safe_max(lst):
        return max(lst) if lst else 0
    
    win_rate = (stats['wins'] / stats['total_games'] * 100) if stats['total_games'] > 0 else 0
    
    # KDA calculation
    avg_kills = safe_avg(stats['kills'])
    avg_deaths = safe_avg(stats['deaths'])
    avg_assists = safe_avg(stats['assists'])
    kda = ((avg_kills + avg_assists) / avg_deaths) if avg_deaths > 0 else avg_kills + avg_assists
    
    # Champion diversity (Herfindahl index)
    total_games = stats['total_games']
    champ_diversity = 0
    if total_games > 0:
        for champ_data in stats['champions'].values():
            share = champ_data['games'] / total_games
            champ_diversity += share * share
        champ_diversity = 1 - champ_diversity  # 0 = one-trick, 1 = completely diverse
    
    # Top 3 champions
    top_champs = sorted(
        stats['champions'].items(),
        key=lambda x: x[1]['games'],
        reverse=True
    )[:3]
    
    return {
        'total_games': stats['total_games'],
        'win_rate': round(win_rate, 1),
        'avg_kills': round(avg_kills, 1),
        'avg_deaths': round(avg_deaths, 1),
        'avg_assists': round(avg_assists, 1),
        'kda': round(kda, 2),
        'cs_per_min': round(safe_avg(stats['cs']), 1),
        'avg_vision': round(safe_avg(stats['vision_scores']), 1),
        'avg_damage_share': round(safe_avg(stats['damage_share']), 1),
        'avg_win_streak': round(safe_avg(stats['win_streaks']), 1) if stats['win_streaks'] else 0,
        'max_win_streak': safe_max(stats['win_streaks']),
        'avg_loss_streak': round(safe_avg(stats['loss_streaks']), 1) if stats['loss_streaks'] else 0,
        'max_loss_streak': safe_max(stats['loss_streaks']),
        'champion_diversity': round(champ_diversity, 2),
        'top_champions': [
            {
                'name': name,
                'games': data['games'],
                'win_rate': round((data['wins'] / data['games'] * 100), 1) if data['games'] > 0 else 0
            }
            for name, data in top_champs
        ]
    }

def is_valid_comparison(riot_client: RiotAPIClient, player: Dict, your_role: str) -> bool:
    """Check if player is valid for comparison"""
    try:
        # Get recent matches
        match_ids = riot_client.get_match_ids(player['puuid'], count=100)
        
        if len(match_ids) < 50:
            return False
        
        # Check recency (last game within 30 days)
        if match_ids:
            recent_match = riot_client.get_match_details(match_ids[0])
            if recent_match:
                game_timestamp = recent_match['info'].get('gameCreation', 0) / 1000
                days_ago = (datetime.now().timestamp() - game_timestamp) / 86400
                if days_ago > 30:
                    return False
        
        # Check role consistency (simplified - would need full match analysis)
        # For MVP, we'll just check if they played your role in encounters
        return True
        
    except Exception as e:
        print(f"Error validating player: {e}")
        return False

def detect_achievements(raw_stats: Dict, aggregated: Dict) -> List[Dict]:
    """Detect funny achievement badges based on stats"""
    achievements = []

    # Death-related
    if aggregated['avg_deaths'] > 8:
        achievements.append({
            'name': 'The Inter',
            'description': f"Died {aggregated['avg_deaths']} times per game on average"
        })

    # Vision-related
    if aggregated['avg_vision'] < 15:
        achievements.append({
            'name': 'Vision Allergic',
            'description': f"Only {aggregated['avg_vision']} vision score per game"
        })

    # Loss streak
    if aggregated['max_loss_streak'] >= 7:
        achievements.append({
            'name': 'Tilt Master',
            'description': f"Lost {aggregated['max_loss_streak']} games in a row"
        })

    # One-trick
    if aggregated['champion_diversity'] < 0.3 and aggregated['top_champions']:
        top_champ = aggregated['top_champions'][0]['name']
        achievements.append({
            'name': f'{top_champ} Specialist',
            'description': f"One-tricked {top_champ} ({aggregated['top_champions'][0]['games']} games)"
        })

    # High games played
    if aggregated['total_games'] > 200:
        achievements.append({
            'name': 'No Life',
            'description': f"{aggregated['total_games']} ranked games this year"
        })

    # Low CS
    if aggregated['cs_per_min'] < 5:
        achievements.append({
            'name': 'Minion Hater',
            'description': f"Only {aggregated['cs_per_min']} CS/min"
        })

    # High KDA but low winrate (KDA player)
    if aggregated['kda'] > 3.5 and aggregated['win_rate'] < 48:
        achievements.append({
            'name': 'KDA Player',
            'description': f"{aggregated['kda']} KDA but {aggregated['win_rate']}% winrate"
        })

    # Low winrate on main
    if aggregated['top_champions'] and aggregated['top_champions'][0]['win_rate'] < 45:
        achievements.append({
            'name': 'Dedicated Loser',
            'description': f"{aggregated['top_champions'][0]['win_rate']}% WR on {aggregated['top_champions'][0]['name']}"
        })

    return achievements