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

        # Only warn about sample size if we got 99-100 games (means we hit the limit and they likely played more)
        sample_warning = ""
        total_games = your_stats.get('total_games', 0)
        if total_games >= 99:
            sample_warning = f"\n\nIMPORTANT: We only grabbed their last 100 games from 2025, so they likely played way more than {total_games} total. Don't roast them about only playing {total_games} games."

        prompt = f"""Write 5-7 funny roasts about this player's 2025 ranked season. Mix dry wit with occasional dad joke energy - the kind that's so stupid it's funny.{avoid_topics}{sample_warning}

IMPORTANT: The current year is 2025. Reference stats as being from 2025, not 2024.

EXAMPLES OF THE VIBE:
- "35% winrate on Yasuo after 50 games. They said you couldn't do it. They were right." (dry wit)
- "Lost 8 games in a row and queued up for a 9th. That's not int, that's commitment." (dry wit)
- "127 games in Silver II. Rome wasn't built in a day, but it didn't take this long either." (dry wit)
- "6 deaths per game. You're not feeding, you're running a charity buffet." (dad joke energy)
- "Played 15 different champions. Turns out the problem follows you around." (dry wit)
- "42% winrate on your main. At least you're consistently inconsistent." (dad joke wordplay)

THEIR STATS:
- Rank: {your_rank}
- Games analyzed: {your_stats.get('total_games', 0)}
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