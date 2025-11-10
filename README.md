# League Rekap-pa

**Rift Rewind Hackathon 2025**

A League of Legends year-in-review application that analyzes your 2025 ranked season and generates AI-powered roasts based on your gameplay statistics.

## Overview

League Rekap-pa is an end-of-year recap tool that fetches your recent ranked match history, analyzes your performance statistics, and uses AWS Bedrock (Claude 3.5 Sonnet) to generate humorous roasts presented as shareable postcards. Think Spotify Wrapped, but for League of Legends... and it roasts you.

## Inspiration and Evolution

This project went through several iterations before arriving at its current form. The original concept was to build an AI helper that would review player statistics and provide climbing advice. However, large language models proved too unreliable for this task, often providing mediocre or incorrect strategic advice.

The focus then shifted to comparative analysis - comparing player stats against slightly higher-ranked players to identify improvement areas. This approach ran into API rate limiting issues when trying to fetch data for multiple players.

After experimenting with pro player comparisons, it became clear that the statistical gap between casual players and professionals was so vast that the comparisons were more humorous than instructive. This led to the final concept: leaning fully into entertainment by generating witty roasts based on the player's own statistics, without comparison to others.

The result is a tool that's designed to be funny rather than instructive. LLMs excel at dry humor and "so stupid it's funny" observations, which pairs well with the absurdities found in ranked gameplay statistics.

## Features

- **2025 Season Analysis**: Analyzes up to 100 of your most recent ranked games from the 2025 season
- **AI-Generated Roasts**: Powered by AWS Bedrock (Claude 3.5 Sonnet v2) for natural language generation
- **Postcard Format**: Results presented as 5-7 shareable postcards with different roast angles
- **Real-time Progress**: Streaming updates via Server-Sent Events during analysis
- **Share Functionality**: Download postcards as images, copy to clipboard, or share directly to social media
- **Smart Caching**: Regenerate new roasts without re-fetching match data
- **Rate Limit Handling**: Automatic countdown timers when hitting Riot API rate limits
- **Multi-Region Support**: Works with all major League of Legends regions

## Technology Stack

### Frontend
- **React 18**: Modern UI framework with hooks
- **Vite**: Fast build tool and development server
- **html2canvas**: Client-side screenshot generation for sharing
- **CSS3**: Custom styling with glassmorphism effects and League-inspired design

### Backend
- **FastAPI**: High-performance Python web framework with async support
- **AWS Bedrock**: Claude 3.5 Sonnet v2 for AI text generation
- **boto3**: AWS SDK for Python
- **Riot Games API**: Match history, summoner data, and rank information
- **Server-Sent Events**: Real-time progress streaming to frontend

### Infrastructure
- **Vercel**: Frontend hosting (serverless)
- **Railway**: Backend hosting with automatic deployments
- **Environment-based CORS**: Configurable origin allowlist for security

## How It Works

```
1. User inputs summoner name (Name#TAG format) and region
2. Backend fetches summoner PUUID from Riot Account API
3. Backend retrieves current rank from League API
4. Backend fetches up to 100 ranked solo/duo matches from 2025
5. Statistics calculated: winrate, KDA, champion pool, streaks, etc.
6. Stats sent to AWS Bedrock with carefully crafted prompts
7. Claude 3.5 Sonnet generates 5-7 roast postcards
8. Frontend displays results in carousel format with sharing options
```

### Statistics Analyzed

- Total games played and overall win rate
- Most played champions and their individual win rates
- KDA (Kills/Deaths/Assists) averages
- Longest win streaks and loss streaks
- Current rank and tier
- Champion pool diversity
- Average CS per minute (when available)

### Roast Style

The AI is prompted to generate roasts in two styles:

- **Dry wit**: "35% winrate on Yasuo after 50 games. They said you couldn't do it. They were right."
- **Dad joke energy**: "6 deaths per game. You're not feeding, you're running a charity buffet."

The quality varies due to LLM unpredictability, but that's part of the charm - you never quite know what you'll get.

## Project Structure

```
roast-player/
├── backend/
│   ├── main.py                 # FastAPI application and endpoints
│   ├── riot_api.py             # Riot Games API client
│   ├── bedrock_client.py       # AWS Bedrock integration
│   ├── analysis.py             # Statistics calculation and aggregation
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variable template
│   └── railway.json            # Railway deployment configuration
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── App.css             # Global styles
│   │   └── components/
│   │       ├── SearchForm.jsx          # Summoner search input
│   │       ├── SearchForm.css
│   │       ├── PostcardCarousel.jsx    # Results display
│   │       └── PostcardCarousel.css
│   ├── index.html
│   ├── package.json            # npm dependencies
│   └── vercel.json             # Vercel deployment configuration
│
└── README.md                   # This file
```

## Setup and Deployment

### Prerequisites

1. **Riot Games API Key**
   - Register at https://developer.riotgames.com/
   - Development keys expire after 24 hours
   - Production keys available upon application approval

2. **AWS Account with Bedrock Access**
   - Claude 3.5 Sonnet must be enabled in us-east-1 region
   - IAM credentials with bedrock:InvokeModel permissions
   - Note: Bedrock may require requesting access for first-time users

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env file with your API keys:
#   RIOT_API_KEY=your_riot_key
#   AWS_ACCESS_KEY_ID=your_aws_key
#   AWS_SECRET_ACCESS_KEY=your_aws_secret
#   AWS_REGION=us-east-1
#   ALLOWED_ORIGINS=http://localhost:5173

uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173
```

### Production Deployment

**Backend (Railway):**
1. Create account at https://railway.app
2. Create new project from GitHub repository
3. Set root directory to `/backend`
4. Configure environment variables (same as .env above, plus `PORT=$PORT`)
5. Railway auto-detects Python and deploys
6. Copy your Railway URL (e.g., `https://your-app.railway.app`)

**Frontend (Vercel):**
1. Update `frontend/vercel.json` with your Railway URL:
   ```json
   {
     "rewrites": [{
       "source": "/api/:path*",
       "destination": "https://your-railway-app.railway.app/:path*"
     }]
   }
   ```
2. Create account at https://vercel.com
3. Import GitHub repository
4. Set root directory to `/frontend`
5. Deploy (no environment variables needed)
6. Update Railway's `ALLOWED_ORIGINS` to include Vercel URL

### API Rate Limits
The Riot Games API imposes strict rate limits (20 requests per second, 100 requests per 2 minutes for development keys). This constrains the application to analyzing a maximum of 100 recent games. This creates several issues:

- Users who played 500+ games in 2025 only see analysis of their most recent 100
- The AI may incorrectly assume total game counts or champion mastery
- Despite explicit prompting, the model sometimes makes assumptions about data it doesn't have

The application handles rate limits gracefully with countdown timers and automatic retries, but the fundamental constraint remains.

## Future Improvements

Given more time and resources, potential enhancements include:

1. **Roast Quality**: Fine-tuning the model, experimenting with different models, or more sophisticated prompt engineering
2. **Visual Enhancement**: Adding champion icons, memes, or GIFs to postcards for more shareability
3. **Pro Player Comparison**: Implementing the comparison feature properly with reliable data sources
4. **Extended Analysis**: Finding ways to analyze more than 100 games (perhaps with production API key)
5. **Social Features**: Leaderboards, shared roasts gallery, friend comparisons

## License

MIT License - Built for Rift Rewind Hackathon 2025

## Acknowledgments

- AWS for Bedrock access and Claude 3.5 Sonnet
- Riot Games for the comprehensive API
- Devpost for hosting the Rift Rewind Hackathon

---

Built for Rift Rewind Hackathon 2025 | Riot Games + AWS + Devpost
