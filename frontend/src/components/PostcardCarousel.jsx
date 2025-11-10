import React, { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import './PostcardCarousel.css';

function PostcardCarousel({ postcards }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showShareMenu, setShowShareMenu] = useState(false);
  const postcardRef = useRef(null);

  const nextCard = () => {
    setCurrentIndex((prev) => (prev + 1) % postcards.length);
  };

  const prevCard = () => {
    setCurrentIndex((prev) => (prev - 1 + postcards.length) % postcards.length);
  };

  const goToCard = (index) => {
    setCurrentIndex(index);
  };

  const captureCard = async () => {
    if (!postcardRef.current) return null;

    try {
      // Create wrapper with background
      const wrapper = document.createElement('div');
      wrapper.style.cssText = `
        position: fixed;
        left: -9999px;
        top: -9999px;
        background: linear-gradient(180deg, #0a1428 0%, #010a13 100%);
        padding: 3rem 2rem;
        width: ${postcardRef.current.offsetWidth}px;
        min-height: ${postcardRef.current.offsetHeight}px;
      `;

      // Clone the postcard
      const clone = postcardRef.current.cloneNode(true);
      clone.style.clipPath = 'none';
      clone.style.background = 'transparent';
      wrapper.appendChild(clone);
      document.body.appendChild(wrapper);

      const canvas = await html2canvas(wrapper, {
        scale: 2,
        logging: false,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#0a1428',
      });

      // Clean up
      document.body.removeChild(wrapper);

      return canvas;
    } catch (error) {
      console.error('Failed to capture card:', error);
      return null;
    }
  };

  const downloadCard = async () => {
    const canvas = await captureCard();
    if (!canvas) {
      alert('Failed to capture card. Please try again.');
      return;
    }

    const link = document.createElement('a');
    link.download = `league-rekappa-2025-${currentIndex + 1}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    setShowShareMenu(false);
  };

  const copyToClipboard = async () => {
    const canvas = await captureCard();
    if (!canvas) {
      alert('Failed to capture card. Please try again.');
      return;
    }

    canvas.toBlob(async (blob) => {
      try {
        await navigator.clipboard.write([
          new ClipboardItem({ 'image/png': blob })
        ]);
        alert('Card copied to clipboard!');
        setShowShareMenu(false);
      } catch (err) {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard. Try downloading instead.');
      }
    });
  };

  const shareToTwitter = () => {
    const text = encodeURIComponent('Just got my 2025 ranked recap from League Rekap-pa Kappa');
    const url = encodeURIComponent(window.location.href);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
    setShowShareMenu(false);
  };

  const shareToFacebook = () => {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
    setShowShareMenu(false);
  };

  const nativeShare = async () => {
    const canvas = await captureCard();
    if (!canvas) {
      alert('Failed to capture card. Please try again.');
      return;
    }

    canvas.toBlob(async (blob) => {
      try {
        const file = new File([blob], 'league-rekappa-2025.png', { type: 'image/png' });
        await navigator.share({
          title: 'League Rekap-pa',
          text: 'Just got my 2025 ranked recap Kappa',
          files: [file]
        });
        setShowShareMenu(false);
      } catch (err) {
        console.error('Native share failed:', err);
      }
    });
  };

  if (!postcards || postcards.length === 0) {
    return <div className="no-postcards">No postcards generated</div>;
  }

  const currentCard = postcards[currentIndex];

  return (
    <div className="postcard-carousel">
      <div className="postcard-wrapper">
        <div ref={postcardRef} className={`postcard postcard-${currentCard.type || 'default'}`}>
          {/* Header */}
          <div className="postcard-header">
            <h2 className="postcard-title">{currentCard.title}</h2>
          </div>

          {/* Content */}
          <div className="postcard-content">
            <p className="postcard-text">{currentCard.content}</p>

            {/* Single stat highlight */}
            {currentCard.stat && (
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
        <button className="share-btn" onClick={() => setShowShareMenu(!showShareMenu)}>
          SHARE THIS CARD
        </button>

        {showShareMenu && (
          <div className="share-menu">
            <button className="share-option" onClick={downloadCard} title="Download Image">
              <span className="share-icon">↓</span>
            </button>
            <button className="share-option" onClick={copyToClipboard} title="Copy to Clipboard">
              <span className="share-icon">⧉</span>
            </button>
            <button className="share-option" onClick={shareToTwitter} title="Share to Twitter/X">
              <span className="share-icon">𝕏</span>
            </button>
            <button className="share-option" onClick={shareToFacebook} title="Share to Facebook">
              <span className="share-icon">f</span>
            </button>
            {navigator.share && (
              <button className="share-option" onClick={nativeShare} title="Share...">
                <span className="share-icon">↗</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default PostcardCarousel;
