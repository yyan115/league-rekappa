import React, { useState, useEffect } from 'react';
import './SearchForm.css';

function SearchForm({ onAnalyze, loading }) {
  const [summonerName, setSummonerName] = useState('');
  const [region, setRegion] = useState('na1');
  const [proPlayers, setProPlayers] = useState({});
  const [selectedPro, setSelectedPro] = useState('');
  const [showProDropdown, setShowProDropdown] = useState(false);

  useEffect(() => {
    // Fetch pro player list on mount
    fetch('/api/pro-players')
      .then(res => res.json())
      .then(data => setProPlayers(data))
      .catch(err => console.error('Failed to load pro players:', err));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (summonerName.trim()) {
      onAnalyze(summonerName.trim(), region, selectedPro || null);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <input
            type="text"
            value={summonerName}
            onChange={(e) => setSummonerName(e.target.value)}
            placeholder="Enter Summoner Name (e.g., Name#TAG)"
            className="summoner-input"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <select
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="region-select"
            disabled={loading}
          >
            <option value="na1">NA</option>
            <option value="euw1">EUW</option>
            <option value="eun1">EUNE</option>
            <option value="kr">KR</option>
            <option value="br1">BR</option>
            <option value="la1">LAN</option>
            <option value="la2">LAS</option>
            <option value="oc1">OCE</option>
            <option value="sg2">SG</option>
            <option value="th2">TH</option>
            <option value="tw2">TW</option>
            <option value="vn2">VN</option>
            <option value="ph2">PH</option>
            <option value="tr1">TR</option>
            <option value="ru">RU</option>
            <option value="jp1">JP</option>
          </select>
        </div>

        {/* Pro player comparison - DISABLED FOR NOW
        <div className="form-group">
          <label className="pro-compare-toggle">
            <input
              type="checkbox"
              checked={showProDropdown}
              onChange={(e) => {
                setShowProDropdown(e.target.checked);
                if (!e.target.checked) setSelectedPro('');
              }}
              disabled={loading}
            />
            <span>Compare with a pro player</span>
          </label>
        </div>

        {showProDropdown && (
          <div className="form-group">
            <select
              value={selectedPro}
              onChange={(e) => setSelectedPro(e.target.value)}
              className="pro-select"
              disabled={loading}
            >
              <option value="">Select a pro player...</option>
              {Object.entries(proPlayers).map(([league, teams]) => (
                <optgroup key={league} label={league}>
                  {Object.entries(teams).map(([teamName, players]) =>
                    players.map(player => (
                      <option key={player.id} value={player.id}>
                        {player.name} ({teamName} - {player.role})
                      </option>
                    ))
                  )}
                </optgroup>
              ))}
            </select>
          </div>
        )}
        */}

        <button type="submit" className="analyze-button" disabled={loading}>
          {loading ? 'LOADING...' : 'ROAST ME'}
        </button>
      </form>
    </div>
  );
}

export default SearchForm;