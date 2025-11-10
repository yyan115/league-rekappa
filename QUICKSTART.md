# 🔑 WHAT YOU NEED TO DO NOW

## Quick Checklist (10 minutes)

### ✅ Step 1: Get Riot API Key (2 min)
1. Go to: https://developer.riotgames.com/
2. Sign in with your Riot account
3. Get your Development API Key (free, instant)
4. Copy the key (looks like: `RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### ✅ Step 2: Get AWS Credentials (5 min)

**Option A: If you have AWS Academy/Educational account**
1. Log into AWS Academy
2. Find your AWS credentials
3. Copy Access Key ID and Secret Access Key

**Option B: If you have regular AWS account**
1. Go to: https://console.aws.amazon.com/
2. IAM → Users → Your User → Security Credentials
3. Create Access Key
4. Copy Access Key ID and Secret Access Key

**CRITICAL: Enable Bedrock Access**
1. Go to: https://console.aws.amazon.com/bedrock/
2. Choose region: **us-east-1** (MUST be this region!)
3. Click "Model access" in sidebar
4. Click "Enable specific models"
5. Find and enable: **Claude 3.5 Sonnet v2**
6. Wait 1-2 minutes for activation

### ✅ Step 3: Configure Backend (3 min)
```bash
cd backend
cp .env.example .env
nano .env  # or use any text editor
```

**Fill in your .env file:**
```
RIOT_API_KEY=RGAPI-your-actual-key-here
AWS_ACCESS_KEY_ID=AKIA...your-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1
DEFAULT_REGION=na1
```

Save and close!

### ✅ Step 4: Run It!
```bash
# In terminal 1 (backend)
cd backend
pip install -r requirements.txt
python main.py

# In terminal 2 (frontend)
cd frontend
npm install
npm run dev
```

Open browser: http://localhost:3000

---

## If Something Goes Wrong

### Riot API Issues
- **"403 Forbidden"** → Wrong API key, get a new one
- **"404 Not Found"** → Check summoner name spelling & region
- **"Rate Limited"** → Wait 2 minutes, dev keys have limits

### AWS Bedrock Issues
- **"Access Denied"** → You didn't enable Claude 3.5 Sonnet v2
- **"Invalid Region"** → Must use us-east-1
- **"Credentials Error"** → Double-check keys in .env

### Install Issues
```bash
# Python issues
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Node issues
rm -rf node_modules package-lock.json
npm install
```

---

## Files You Got

```
the-climb/
├── backend/              ← Python FastAPI server
│   ├── main.py
│   ├── riot_api.py
│   ├── analysis.py
│   ├── bedrock_client.py
│   ├── requirements.txt
│   └── .env.example     ← COPY THIS TO .env AND FILL IN
│
├── frontend/            ← React web app
│   ├── src/
│   ├── package.json
│   └── index.html
│
├── README.md            ← Full documentation
├── SETUP_INSTRUCTIONS.md ← Detailed setup guide
├── METHODOLOGY_WRITEUP.md ← For hackathon submission
├── DEMO_VIDEO_SCRIPT.md   ← Script for your demo video
└── start.sh             ← Quick start script (Unix/Mac)
```

---

## What Each File Does

**Backend:**
- `main.py` - Main API server, handles requests
- `riot_api.py` - Talks to Riot Games API
- `analysis.py` - Calculates stats & categorizes players
- `bedrock_client.py` - Generates AI insights via AWS

**Frontend:**
- `App.jsx` - Main app component
- `SearchForm.jsx` - Input form
- `Results.jsx` - Shows analysis results

---

## Testing Checklist

Before demo video:
- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Can enter summoner name
- [ ] Analysis completes successfully
- [ ] Results display correctly
- [ ] AI insights look good

---

## Next Steps

1. **Get it running locally** (follow steps above)
2. **Test with your own summoner** (or use "Doublelift", "Sneaky")
3. **Record demo video** (see DEMO_VIDEO_SCRIPT.md)
4. **Deploy** (optional - Railway/Heroku for backend, Vercel for frontend)
5. **Submit to Devpost** before Nov 10, 10pm GMT!

---

## Quick Start Commands

**Easy mode (Unix/Mac):**
```bash
./start.sh
```

**Manual mode:**
```bash
# Terminal 1
cd backend && python main.py

# Terminal 2  
cd frontend && npm run dev
```

---

## Got 2 Days - Priority Order

**Day 1 (TODAY):**
1. ✅ Get API keys (10 min)
2. ✅ Get it running locally (20 min)
3. ✅ Test with real summoner (5 min)
4. ✅ Fix any issues (1-2 hours)

**Day 2 (TOMORROW):**
1. Record demo video (30 min)
2. Deploy if desired (1 hour)
3. Write submission text (30 min)
4. Submit to Devpost!

---

## Support Resources

- **Riot API Docs:** https://developer.riotgames.com/apis
- **AWS Bedrock Docs:** https://docs.aws.amazon.com/bedrock/
- **Hackathon Details:** https://riftrewind.devpost.com/

---

## One More Thing

The entire codebase is ready. No TODOs, no placeholders.
Just add your API keys and run it.

**YOU GOT THIS! 🚀**

Good luck with the hackathon!
