# The Climb - Who Passed You Up?

> **Rift Rewind Hackathon 2025**  
> League trajectory analyzer powered by AWS Bedrock & Riot Games API

![The Climb](https://img.shields.io/badge/League-Trajectory%20Analyzer-blue)
![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![React](https://img.shields.io/badge/React-18-blue)

## 🎯 The Concept

You're not Faker. Comparing yourself to Challenger players isn't actionable. 

**The Climb** analyzes players you actually matched with in early 2025 and shows you:
- 📈 Who climbed faster than you (and why)
- 📉 Who you're outpacing  
- 🤖 AI-powered insights on the behavioral differences that matter

### Why This Works

Instead of generic advice from watching pro players, you get:
- **Personal**: Based on YOUR actual games and opponents
- **Relevant**: Compares you to similar skill levels (1-2 ranks higher)
- **Actionable**: AI identifies specific behavioral changes, not just "play better"

---

## ✨ Features

### Core Analysis
- ✅ Trajectory comparison with players from your early 2025 games
- ✅ Statistical aggregation (KDA, CS, vision, win/loss streaks)
- ✅ Player categorization (climbed higher / fell behind / same pace)
- ✅ Champion pool and playstyle analysis

### AI-Powered Insights (AWS Bedrock + Claude 3.5 Sonnet)
- 🤖 Behavioral pattern analysis
- 🎯 Key difference identification
- 📋 Personalized action plans
- 🔥 Optional "roast mode" (for Roast Master 3000 prize)

### Smart Filtering
- ✅ 50+ games minimum requirement
- ✅ Active player check (played within 30 days)
- ✅ Role consistency validation
- ✅ Rank delta filtering (1-2 tiers higher)

---

## 🏗️ Architecture

```
User Input → Riot API → Data Processing → AWS Bedrock → Results
                ↓
        Match History Analysis
                ↓
        Player Categorization
                ↓
        Stats Aggregation
                ↓
        GenAI Insight Generation
```

### Tech Stack

**Backend:**
- Python 3.9+ with FastAPI
- Riot Games API (match-v5, summoner-v4, league-v4)
- AWS Bedrock (Claude 3.5 Sonnet v2)
- boto3 for AWS integration

**Frontend:**
- React 18
- Vite for dev server & bundling
- Modern CSS with glassmorphism effects

---

## 🚀 Quick Start

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup.

**TL;DR:**
```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Requirements:**
- Riot API key from https://developer.riotgames.com/
- AWS credentials with Bedrock access (Claude 3.5 Sonnet v2 enabled in us-east-1)

---

## 📊 How It Works

### 1. Data Collection
```python
# Get summoner → Match history → Extract all players
matches = riot_api.get_matches_since(puuid, "2025-01-01")
players = extract_players_from_matches(matches, your_puuid)
```

### 2. Player Categorization
```python
# Filter & categorize players
for player in players:
    if is_valid_comparison(player):  # 50+ games, active, same role
        current_rank = get_rank(player)
        if is_higher_rank(current_rank, your_rank):
            climbed_higher.append(player)
```

### 3. Stats Aggregation
```python
# Calculate behavioral metrics
stats = {
    'win_streaks': analyze_streaks(matches),
    'loss_streaks': analyze_streaks(matches, wins=False),
    'champion_diversity': calculate_diversity(champ_pool),
    'cs_per_min': avg_cs(matches),
    # ... more metrics
}
```

### 4. AI Insight Generation
```python
# AWS Bedrock analyzes patterns
insights = bedrock.generate_insights(
    your_stats=aggregate_stats(you),
    climber_stats=aggregate_stats(climbers),
    stuck_stats=aggregate_stats(stuck_players)
)
```

**Example AI Output:**
```json
{
  "what_climbers_do_better": "Climbers stop playing after 2-3 losses. You average 5-game loss streaks. They protect their mental and MMR by taking breaks.",
  "what_youre_doing_right": "Your CS is 0.5/min better than players who fell behind. Keep focusing on farming.",
  "the_one_key_difference": "Tilt control. The gap isn't mechanics—it's knowing when to stop.",
  "action_plan": [
    "Hard rule: Stop after 2 ranked losses in a row",
    "Track your loss streak average over next 20 games",
    "If you feel tilted, play ARAM or normals instead"
  ]
}
```

---

## 🎨 UI Preview

**Landing Page:**
- Clean, modern glassmorphism design
- Summoner name input + region selector
- Purple gradient theme matching League aesthetic

**Results Page:**
- Your rank badge with key stats
- "Players Who Passed You Up" cards
- "Players You Passed Up" cards  
- AI insights with actionable advice
- Optional roast mode

---

## 🏆 Hackathon Alignment

### Requirements Met
- ✅ Uses AWS AI services (Bedrock + Claude 3.5 Sonnet v2)
- ✅ Uses League API for match history
- ✅ Generates personalized end-of-year insights
- ✅ Goes beyond op.gg (peer trajectory comparison)
- ✅ Identifies growth areas through behavioral analysis
- ✅ Full-year match history analysis (January 2025+)

### Judging Criteria

**Insight Quality (25%):**  
AI identifies behavioral patterns (tilt control, champion pool, consistency) not just raw stats

**Technical Execution (25%):**  
Multi-API orchestration, sophisticated filtering, essential GenAI integration

**Creativity & UX (25%):**  
Novel "who passed you up" concept, clean UI, personal/memorable experience

**AWS Integration (25%):**  
Claude 3.5 Sonnet v2 via Bedrock is ESSENTIAL for insight generation (not cosmetic)

**Unique & Vibes (25%):**  
Fresh approach to coaching - compares you to similar players who succeeded, not pros

---

## 💡 Why GenAI Is Essential

**Without GenAI (just stats):**
```
Climbers: 7.2 CS/min, 3 loss streak avg
You: 6.4 CS/min, 5 loss streak avg
Stuck: 5.9 CS/min, 6 loss streak avg
```

**With GenAI (reasoning + action):**
```
The gap isn't CS (you're ahead of stuck players there).
It's tilt control. Climbers cut loss streaks early.

Action: After 2 losses, take a break. Your CS is good—
protect your mental and you'll climb.
```

The AI transforms raw data into **reasoning, prioritization, and actionable advice**.

---

## 📈 Special Prize Targets

- **Hidden Gem Detector**: Finding patterns in your past games you didn't notice
- **Roast Master 3000**: Optional roast feature comparing you to players who climbed past you
- **Model Whisperer**: Sophisticated prompt engineering for behavioral analysis

---

## 🔧 API Endpoints

### `POST /analyze`
Main analysis endpoint.

**Request:**
```json
{
  "summoner_name": "YourName",
  "region": "na1"
}
```

**Response:**
```json
{
  "status": "success",
  "your_rank": "GOLD II",
  "your_stats": {
    "win_rate": 52.3,
    "kda": 2.8,
    "cs_per_min": 6.4,
    "avg_loss_streak": 5,
    ...
  },
  "climbers": [...],
  "fell_behind": [...],
  "insights": {...},
  "roast": "..."
}
```

---

## 📝 Development Notes

### Rate Limits
- Development API key: 20 req/sec, 100 req/2min
- Analysis takes ~1-2 minutes for 50-100 matches
- Automatic retry logic with exponential backoff

### Optimizations
- Limits to 50 early matches for speed
- Caps climber/stuck analysis to top 5 each
- Caches summoner lookups
- Parallel match fetching possible (future enhancement)

### Known Limitations
- Requires 20+ ranked games from January 2025
- Development API keys expire in 24 hours
- AWS Bedrock requires us-east-1 region
- Role detection simplified for MVP

---

## 🚢 Deployment

### Backend
```bash
# Railway / Heroku / AWS
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
# Push to platform
```

### Frontend
```bash
npm run build
# Deploy dist/ folder to Vercel/Netlify
```

---

## 📜 License

MIT License - Open source for the hackathon and beyond!

---

## 🙏 Acknowledgments

- **AWS** for Bedrock access and hackathon support
- **Riot Games** for the comprehensive API and League of Legends
- **Devpost** for hosting the hackathon

---

## 👨‍💻 Author

Built for Rift Rewind Hackathon 2025  
Riot Games + AWS + Devpost

**Contact:** [Your info here]

---

Made with ❤️ and lots of ☕ in 48 hours
