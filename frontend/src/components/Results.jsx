import React from 'react';
import './Results.css';

function Results({ data }) {
  const { your_rank, your_stats, climbers, fell_behind, insights, roast } = data;

  return (
    <div className="results">
      {/* Your Rank */}
      <div className="rank-card">
        <h2>Your Current Rank</h2>
        <div className="rank-badge">{your_rank}</div>
        <div className="stats-grid">
          <div className="stat">
            <span className="stat-label">Win Rate</span>
            <span className="stat-value">{your_stats.win_rate}%</span>
          </div>
          <div className="stat">
            <span className="stat-label">KDA</span>
            <span className="stat-value">{your_stats.kda}</span>
          </div>
          <div className="stat">
            <span className="stat-label">CS/min</span>
            <span className="stat-value">{your_stats.cs_per_min}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Games</span>
            <span className="stat-value">{your_stats.total_games}</span>
          </div>
        </div>
      </div>

      {/* Roast */}
      {roast && (
        <div className="roast-card">
          <h3>🔥 Reality Check</h3>
          <p className="roast-text">{roast}</p>
        </div>
      )}

      {/* Climbers */}
      {climbers && climbers.length > 0 && (
        <div className="player-card climbers">
          <h3>📈 Players Who Passed You Up</h3>
          <p className="card-subtitle">
            These players were similar rank to you in early 2025, but climbed higher
          </p>
          <div className="player-list">
            {climbers.map((player, idx) => (
              <div key={idx} className="player-item climber">
                <div className="player-info">
                  <span className="player-name">{player.name}</span>
                  <span className="player-rank climbed">{player.rank}</span>
                </div>
                <span className="encounter-count">Played {player.encountered}x</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fell Behind */}
      {fell_behind && fell_behind.length > 0 && (
        <div className="player-card fell-behind">
          <h3>📉 Players You Passed Up</h3>
          <p className="card-subtitle">
            You're climbing faster than these players you matched with
          </p>
          <div className="player-list">
            {fell_behind.map((player, idx) => (
              <div key={idx} className="player-item fell">
                <div className="player-info">
                  <span className="player-name">{player.name}</span>
                  <span className="player-rank fell-rank">{player.rank}</span>
                </div>
                <span className="encounter-count">Played {player.encountered}x</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Insights */}
      {insights && (
        <div className="insights-section">
          <h2 className="insights-title">🤖 AI Analysis</h2>
          
          <div className="insight-card positive">
            <h4>✅ What You're Doing Right</h4>
            <p>{insights.what_youre_doing_right}</p>
          </div>

          <div className="insight-card negative">
            <h4>⚠️ What Climbers Do Better</h4>
            <p>{insights.what_climbers_do_better}</p>
          </div>

          <div className="insight-card key">
            <h4>🎯 The One Key Difference</h4>
            <p>{insights.the_one_key_difference}</p>
          </div>

          <div className="action-plan">
            <h4>📋 Your Action Plan</h4>
            <ul>
              {insights.action_plan && insights.action_plan.map((action, idx) => (
                <li key={idx}>{action}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Top Champions */}
      {your_stats.top_champions && your_stats.top_champions.length > 0 && (
        <div className="champions-card">
          <h3>🏆 Your Top Champions</h3>
          <div className="champions-list">
            {your_stats.top_champions.map((champ, idx) => (
              <div key={idx} className="champion-item">
                <span className="champ-name">{champ.name}</span>
                <span className="champ-stats">
                  {champ.games} games • {champ.win_rate}% WR
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Results;
