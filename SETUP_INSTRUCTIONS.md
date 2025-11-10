# The Climb - Setup Instructions

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+
- Node.js 18+
- Riot Games API Key
- AWS Account with Bedrock access

---

## Step 1: Get Riot API Key (2 minutes)

1. Go to https://developer.riotgames.com/
2. Sign in with your Riot account
3. Click "REGISTER PRODUCT" or go to your dashboard
4. You'll immediately get a Development API key (expires in 24 hours)
5. Copy your key that looks like: `RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

**Note:** Development keys have rate limits (20 requests/sec, 100 requests/2min). This is enough for the hackathon!

---

## Step 2: Get AWS Credentials (3 minutes)

### Option A: AWS Academy / Student Account
If you have AWS Academy access from the hackathon:
1. Log into AWS Academy
2. Go to "AWS Details"
3. Copy your credentials

### Option B: Regular AWS Account
1. Log into AWS Console: https://console.aws.amazon.com/
2. Go to IAM → Users → Your User → Security Credentials
3. Create Access Key
4. Copy Access Key ID and Secret Access Key

### Enable Bedrock Access
1. Go to AWS Bedrock console: https://console.aws.amazon.com/bedrock/
2. Select region: **us-east-1** (important!)
3. Go to "Model access" in the left sidebar
4. Click "Enable specific models"
5. Enable: **Claude 3.5 Sonnet v2**
6. Wait ~2 minutes for access to be granted

---

## Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your credentials
# Use nano, vim, or any text editor:
nano .env
```

**Edit your `.env` file to look like this:**
```
RIOT_API_KEY=RGAPI-your-actual-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
DEFAULT_REGION=na1
```

**Save and close the file.**

```bash
# Test the backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal window open!**

---

## Step 4: Frontend Setup

Open a **NEW terminal window**:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

---

## Step 5: Test It!

1. Open your browser to: http://localhost:3000
2. Enter a summoner name (try your own or: "Doublelift")
3. Select region (default: NA)
4. Click "Analyze My Climb"
5. Wait 1-2 minutes for analysis

---

## Troubleshooting

### "Summoner not found"
- Check spelling and capitalization
- Make sure the region is correct
- Try a different summoner name

### "403 Forbidden" from Riot API
- Your API key expired (get a new one)
- Wrong API key in .env file

### "Rate limit exceeded"
- Wait a few minutes
- Development keys have rate limits

### AWS Bedrock errors
- Make sure you enabled Claude 3.5 Sonnet v2
- Check your AWS region is us-east-1
- Verify your AWS credentials are correct

### Backend won't start
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## Testing with Your Own Account

1. Must have played ranked games in 2025
2. Need at least 20 ranked games from January 2025 onwards
3. Analysis takes ~1-2 minutes (fetching match data)

---

## Production Deployment (Optional)

### Backend (Railway / Heroku / AWS)
```bash
# Add Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy to platform of choice
```

### Frontend (Vercel / Netlify)
```bash
npm run build
# Deploy the 'dist' folder
```

---

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /analyze` - Main analysis endpoint

**Example request:**
```json
{
  "summoner_name": "YourName",
  "region": "na1"
}
```

---

## File Structure

```
the-climb/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── riot_api.py          # Riot API client
│   ├── analysis.py          # Stats processing
│   ├── bedrock_client.py    # AWS Bedrock/Claude
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SearchForm.jsx
│   │   │   └── Results.jsx
│   ├── package.json
│   └── index.html
└── README.md
```

---

## Need Help?

Check the main README.md for more details on the project architecture and features.

Good luck with the hackathon! 🚀
