import React, { useState } from 'react';
import './SearchForm.css';

function SearchForm({ onAnalyze, loading }) {
  const [summonerName, setSummonerName] = useState('');
  const [region, setRegion] = useState('na1');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (summonerName.trim()) {
      onAnalyze(summonerName.trim(), region);
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

        <button type="submit" className="analyze-button" disabled={loading}>
          {loading ? 'LOADING...' : 'ROAST ME'}
        </button>
      </form>
    </div>
  );
}

export default SearchForm;