import boto3
import json
import os
from typing import Dict, Optional

class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        # Use cross-region inference profile instead of direct model ID
        # This is required as of late 2024
        self.model_id = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
    
    def generate_year_review_postcards(self, your_stats: Dict, your_rank: str, achievements: list, used_topics: list = None) -> tuple:
        """Generate 5-7 funny postcards for year-in-review mode

        Returns: (postcards, used_topics)
        """
        if used_topics is None:
            used_topics = []

        top_champ = your_stats.get('top_champions', [{}])[0].get('name', 'Unknown') if your_stats.get('top_champions') else 'Unknown'
        top_champ_games = your_stats.get('top_champions', [{}])[0].get('games', 0) if your_stats.get('top_champions') else 0
        top_champ_wr = your_stats.get('top_champions', [{}])[0].get('win_rate', 0) if your_stats.get('top_champions') else 0

        total_deaths = int(your_stats.get('avg_deaths', 0) * your_stats.get('total_games', 0))

        # Get top 3 champs for variety
        top_champs_str = ', '.join([f"{c['name']} ({c['win_rate']}% WR)" for c in your_stats.get('top_champions', [])[:3]])

        second_champ = your_stats.get('top_champions', [{}])[1] if len(your_stats.get('top_champions', [])) > 1 else {}
        second_champ_name = second_champ.get('name', 'Unknown')
        second_champ_wr = second_champ.get('win_rate', 0)
        second_champ_games = second_champ.get('games', 0)

        avoid_topics = ""
        if used_topics:
            avoid_topics = f"\n\nDON'T REPEAT THESE TOPICS (already roasted):\n{', '.join(used_topics)}\n\nPick DIFFERENT stats to roast."

        prompt = f"""Write 5-7 funny roasts about this player's 2025 ranked season. Match the exact tone and style of these examples:{avoid_topics}

IMPORTANT: The current year is 2025. Reference stats as being from 2025, not 2024.

EXAMPLES OF THE VIBE:
- "35% winrate on Yasuo after 50 games. They said you couldn't do it. They were right."
- "Lost 8 games in a row and queued up for a 9th. That's not int, that's commitment."
- "127 games in Silver II. Rome wasn't built in a day, but it didn't take this long either."
- "Tried 15 different champions. None of them worked. The common factor? Couldn't be you."
- "4.2 KDA in losses, 2.1 KDA in wins. You're an MVP for the wrong team."
- "Played 80 games on your main with 42% winrate. Practice makes... well, not perfect apparently."

THEIR STATS:
- Rank: {your_rank}
- Games played: {your_stats.get('total_games', 0)}
- Overall winrate: {your_stats.get('win_rate', 0)}%
- Most played: {top_champ} ({top_champ_games} games, {top_champ_wr}% WR)
- Second most: {second_champ_name} ({second_champ_games} games, {second_champ_wr}% WR)
- Worst loss streak: {your_stats.get('max_loss_streak', 0)} games
- Best win streak: {your_stats.get('max_win_streak', 0)} games
- KDA: {your_stats.get('kda', 0)}

Write roasts in the EXACT same style as the examples. Short, punchy, actually funny. Use their real stats. Don't explain the joke.

Return JSON object with:
- postcards: array of {{"title": "SHORT TITLE", "content": "the roast", "type": "roast"}}
- topics: array of strings describing what you roasted (e.g., ["main_champ_winrate", "loss_streak", "games_played"])

Output ONLY valid JSON in this format:
{{"postcards": [...], "topics": ["...", "..."]}}"""

        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 1.0
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text'].strip()

            # Clean up markdown
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()

            result = json.loads(content)

            # Handle both old format (array) and new format (object with postcards/topics)
            if isinstance(result, list):
                # Old format - just postcards array
                postcards = result
                topics = []
            else:
                # New format - object with postcards and topics
                postcards = result.get('postcards', [])
                topics = result.get('topics', [])

            return postcards, topics

        except Exception as e:
            print(f"Error generating year review postcards: {e}")
            # Fallback postcards
            return ([
                {
                    "title": "2025 RECAP",
                    "content": "Let's talk about your year.",
                    "type": "intro"
                },
                {
                    "title": "THE NUMBERS",
                    "content": f"{your_stats.get('total_games', 0)} games. {your_stats.get('win_rate', 0)}% winrate. {your_rank}.",
                    "stat": f"{your_rank}",
                    "type": "stat"
                },
                {
                    "title": f"{top_champ.upper()} MAIN",
                    "content": f"{top_champ_games} games on {top_champ}. {top_champ_wr}% winrate. They said you couldn't do it. They were right.",
                    "type": "roast"
                }
            ], [])

    def generate_comparison_postcards(self, your_stats: Dict, pro_stats: Dict, your_rank: str, pro_rank: str, pro_name: str, pro_team: str) -> list:
        """Generate 4-6 funny comparison postcards for pro comparison mode"""

        your_champ = your_stats.get('top_champions', [{}])[0].get('name', 'Unknown') if your_stats.get('top_champions') else 'Unknown'
        pro_champ = pro_stats.get('top_champions', [{}])[0].get('name', 'Unknown') if pro_stats.get('top_champions') else 'Unknown'

        prompt = f"""You're a SAVAGE League of Legends roaster. Generate 4-6 postcards comparing a player to pro player {pro_name} from {pro_team}.

YOUR STATS:
- Rank: {your_rank}
- Win rate: {your_stats.get('win_rate', 0)}%
- KDA: {your_stats.get('kda', 0)}
- CS/min: {your_stats.get('cs_per_min', 0)}
- Deaths/game: {your_stats.get('avg_deaths', 0)}
- Vision: {your_stats.get('avg_vision', 0)}
- Top champ: {your_champ}

{pro_name}'S STATS:
- Rank: {pro_rank}
- Win rate: {pro_stats.get('win_rate', 0)}%
- KDA: {pro_stats.get('kda', 0)}
- CS/min: {pro_stats.get('cs_per_min', 0)}
- Deaths/game: {pro_stats.get('avg_deaths', 0)}
- Vision: {pro_stats.get('avg_vision', 0)}
- Top champ: {pro_champ}

Generate postcards with these themes:
1. Intro (announcing the matchup)
2. Side-by-side stat comparison (be BRUTAL but funny)
3. Main roast (the gap is HUGE, make it hilarious)
4. Copium card (find ONE stat you're better at, hype it ironically)
5. Reality check (bring them back down)
6. Final verdict

Return ONLY a JSON array. Each postcard:
- title: Short catchy title
- content: The roast (1-3 sentences, MAX 250 characters)
- your_stat: Your stat value (optional)
- pro_stat: Pro's stat value (optional)
- type: "intro" or "comparison" or "roast" or "copium"

Example:
[
  {{"title": "You vs {pro_name}", "content": "You challenged {pro_name} from {pro_team}. This won't end well.", "type": "intro"}},
  {{"title": "Win Rate", "content": "{pro_name}: {pro_stats.get('win_rate', 0)}%. You: {your_stats.get('win_rate', 0)}%. Maybe stick to ARAM?", "your_stat": "{your_stats.get('win_rate', 0)}%", "pro_stat": "{pro_stats.get('win_rate', 0)}%", "type": "comparison"}},
  ...
]

Make it SAVAGE but FUNNY. This is for entertainment. Output ONLY the JSON array."""

        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 1.0
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text'].strip()

            # Clean up markdown
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()

            postcards = json.loads(content)
            return postcards

        except Exception as e:
            print(f"Error generating comparison postcards: {e}")
            # Fallback
            return [
                {
                    "title": f"You vs {pro_name}",
                    "content": f"You challenged {pro_name} from {pro_team}. Brave choice.",
                    "type": "intro"
                },
                {
                    "title": "The Gap",
                    "content": f"{pro_name} has {pro_stats.get('win_rate', 0)}% WR in {pro_rank}. You have {your_stats.get('win_rate', 0)}% in {your_rank}. Different games, really.",
                    "your_stat": f"{your_stats.get('win_rate', 0)}%",
                    "pro_stat": f"{pro_stats.get('win_rate', 0)}%",
                    "type": "comparison"
                }
            ]