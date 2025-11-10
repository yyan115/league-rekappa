import React, { useState } from 'react';
import SearchForm from './components/SearchForm';
import PostcardCarousel from './components/PostcardCarousel';
import './App.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const [rateLimitMessage, setRateLimitMessage] = useState('');

  const getRankClass = (rank) => {
    if (!rank) return 'gold';
    const rankLower = rank.toLowerCase();
    if (rankLower.includes('iron')) return 'iron';
    if (rankLower.includes('bronze')) return 'bronze';
    if (rankLower.includes('silver')) return 'silver';
    if (rankLower.includes('gold')) return 'gold';
    if (rankLower.includes('platinum')) return 'platinum';
    if (rankLower.includes('emerald')) return 'emerald';
    if (rankLower.includes('diamond')) return 'diamond';
    if (rankLower.includes('master')) return 'master';
    if (rankLower.includes('grandmaster')) return 'grandmaster';
    if (rankLower.includes('challenger')) return 'challenger';
    return 'gold';
  };

  const handleAnalyze = async (summonerName, region, forceRefresh = false) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setProgressMessage('Starting...');
    setRateLimitMessage('');

    // Save last search
    sessionStorage.setItem('lastSearch', JSON.stringify({ summonerName, region }));

    try {
      // Check cache first
      const cacheKey = `${summonerName.toLowerCase()}_${region}`;
      const cached = sessionStorage.getItem(cacheKey);
      console.log(`Cache check: key="${cacheKey}", found=${!!cached}, forceRefresh=${forceRefresh}`);

      if (cached && !forceRefresh) {
        setProgressMessage('Regenerating roasts...');
        const cachedData = JSON.parse(cached);

        // Get previously used topics to avoid repetition
        const usedTopics = cachedData.used_topics || [];

        // Re-generate roasts with cached stats
        const response = await fetch('/api/regenerate-roasts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            your_stats: cachedData.your_stats,
            your_rank: cachedData.your_rank,
            achievements: cachedData.achievements,
            used_topics: usedTopics
          }),
        });

        const data = await response.json();

        // Update cache with new used_topics
        const newUsedTopics = [...usedTopics, ...(data.used_topics || [])];
        cachedData.used_topics = newUsedTopics;
        sessionStorage.setItem(cacheKey, JSON.stringify(cachedData));

        setResults({
          ...cachedData,
          postcards: data.postcards
        });
        setLoading(false);
        return;
      }

      const requestBody = {
        summoner_name: summonerName,
        region: region
      };

      // Use fetch with streaming
      const response = await fetch('/api/analyze-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));

              if (data.progress) {
                setProgressMessage(data.progress);
              }

              if (data.rate_limit) {
                setRateLimitMessage(data.rate_limit);
              } else {
                setRateLimitMessage('');
              }

              if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
              }

              if (data.result) {
                setResults(data.result);

                // Cache the result
                const cacheKey = `${summonerName.toLowerCase()}_${region}`;
                const cacheData = {
                  your_stats: data.result.your_stats,
                  your_rank: data.result.your_rank,
                  achievements: data.result.achievements || [],
                  used_topics: data.result.used_topics || []
                };
                sessionStorage.setItem(cacheKey, JSON.stringify(cacheData));

                setLoading(false);
                setProgressMessage('');
                return;
              }
            } catch (e) {
              console.error('Parse error:', e);
            }
          }
        }
      }

    } catch (err) {
      setError(err.message);
      setLoading(false);
      console.error('Analysis error:', err);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">LEAGUE REKAP-PA</h1>
          <div className="subtitle">2025 SEASON RECAP</div>
          <p className="description">
            Your ranked stats for 2025, roasted (maybe).
          </p>
        </header>

        <SearchForm onAnalyze={handleAnalyze} loading={loading} />

        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p className="progress-message">{progressMessage || 'Starting...'}</p>
            {rateLimitMessage && (
              <p className="rate-limit-message">{rateLimitMessage}</p>
            )}
            <p className="loading-detail">This may take 1-2 minutes</p>
          </div>
        )}

        {results && (
          <div className="results-container">
            <div className="results-header">
              <h2>Your 2025 Recap</h2>
              <p className="results-subheader">
                Current Rank: <span className={`rank-badge ${getRankClass(results.your_rank)}`}>{results.your_rank}</span>
              </p>
              <button
                className="roast-again-btn"
                onClick={() => {
                  const lastSearch = sessionStorage.getItem('lastSearch');
                  if (lastSearch) {
                    const { summonerName, region } = JSON.parse(lastSearch);
                    handleAnalyze(summonerName, region, false);
                  }
                }}
              >
                ROAST ME AGAIN
              </button>
            </div>

            <PostcardCarousel
              postcards={results.postcards}
            />
          </div>
        )}

        <footer className="footer">
          <p>Powered by AWS Bedrock & Riot Games API</p>
          <p className="footer-small">Rift Rewind Hackathon 2025</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
