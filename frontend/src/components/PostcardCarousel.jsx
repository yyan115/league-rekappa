import React, { useState } from 'react';
import './PostcardCarousel.css';

function PostcardCarousel({ postcards, mode, proInfo }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const nextCard = () => {
    setCurrentIndex((prev) => (prev + 1) % postcards.length);
  };

  const prevCard = () => {
    setCurrentIndex((prev) => (prev - 1 + postcards.length) % postcards.length);
  };

  const goToCard = (index) => {
    setCurrentIndex(index);
  };

  if (!postcards || postcards.length === 0) {
    return <div className="no-postcards">No postcards generated</div>;
  }

  const currentCard = postcards[currentIndex];

  return (
    <div className="postcard-carousel">
      <div className="postcard-wrapper">
        <div className={`postcard postcard-${currentCard.type || 'default'}`}>
          {/* Header */}
          <div className="postcard-header">
            <h2 className="postcard-title">{currentCard.title}</h2>
            {mode === 'pro_comparison' && proInfo && currentIndex === 0 && (
              <div className="pro-badge">
                {proInfo.name} - {proInfo.team}
              </div>
            )}
          </div>

          {/* Content */}
          <div className="postcard-content">
            <p className="postcard-text">{currentCard.content}</p>

            {/* Stats display for comparison cards */}
            {currentCard.type === 'comparison' && (
              <div className="stat-comparison">
                <div className="stat-box your-stat">
                  <span className="stat-label">You</span>
                  <span className="stat-value">{currentCard.your_stat || '-'}</span>
                </div>
                <div className="stat-divider">VS</div>
                <div className="stat-box pro-stat">
                  <span className="stat-label">{proInfo?.name || 'Pro'}</span>
                  <span className="stat-value">{currentCard.pro_stat || '-'}</span>
                </div>
              </div>
            )}

            {/* Single stat highlight */}
            {currentCard.stat && currentCard.type !== 'comparison' && (
              <div className="stat-highlight">
                {currentCard.stat}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="postcard-footer">
            <span className="card-number">
              {currentIndex + 1} / {postcards.length}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="carousel-nav">
        <button
          className="nav-btn prev-btn"
          onClick={prevCard}
          disabled={currentIndex === 0}
        >
          ←
        </button>

        <div className="carousel-dots">
          {postcards.map((_, index) => (
            <button
              key={index}
              className={`dot ${index === currentIndex ? 'active' : ''}`}
              onClick={() => goToCard(index)}
            />
          ))}
        </div>

        <button
          className="nav-btn next-btn"
          onClick={nextCard}
          disabled={currentIndex === postcards.length - 1}
        >
          →
        </button>
      </div>

      {/* Share button */}
      <div className="share-section">
        <button className="share-btn" onClick={() => {
          // TODO: Implement screenshot/share functionality
          alert('Screenshot this card to share with friends!');
        }}>
          SHARE THIS CARD
        </button>
      </div>
    </div>
  );
}

export default PostcardCarousel;
