import React from 'react';
import './LandingPage.css';

const LandingPage = ({ onGetStarted, loggedInUser }) => {
    return (
        <div className="landing-page">
            {/* Floating decorative elements */}
            <div className="floating-tokens">
                <div className="token token-1 token-3d">🎯</div>
                <div className="token token-2 token-3d">⚡</div>
                <div className="token token-3 token-3d">🎮</div>
                <div className="token token-4 token-3d">🏆</div>
                <div className="token token-5 token-3d">💎</div>
                <div className="token token-6 token-3d">🎲</div>
                <div className="token token-7 token-3d">⭐</div>
            </div>

            {/* Main content area */}
            <div className="landing-container">
                <div className="hero-section">
                    <h1 className="hero-title hero-3d">
                        Earn Crypto Rewards by Playing
                        <br />
                        <span className="gradient-text">Smart Strategy Games</span>
                    </h1>
                    
                    <p className="hero-subtitle">
                        Challenge AI opponents in exciting Gomoku battles, showcase your strategic thinking,
                        <br />
                        and win real ETH rewards
                    </p>

                    <div className="cta-section">
                        <button className="cta-button cta-button-3d" onClick={onGetStarted}>
                            <span className="button-text">
                                {loggedInUser ? 'Enter Game' : 'Get Started'}
                            </span>
                            <svg className="button-arrow" viewBox="0 0 8 16" width="18" height="18">
                                <path fillRule="evenodd" d="M7.5 8l-5 5L1 11.5 4.75 8 1 4.5 2.5 3l5 5z"/>
                            </svg>
                        </button>
                    </div>

                    {/* Game preview area */}
                    <div className="game-preview">
                        <div className="preview-board preview-board-3d">
                            <div className="board-grid board-3d">
                                {[...Array(25)].map((_, i) => (
                                    <div key={i} className="grid-cell grid-cell-3d">
                                        {i === 12 && <div className="piece black piece-3d"></div>}
                                        {i === 11 && <div className="piece white piece-3d"></div>}
                                        {i === 13 && <div className="piece white piece-3d"></div>}
                                        {i === 7 && <div className="piece black piece-3d"></div>}
                                        {i === 17 && <div className="piece black piece-3d"></div>}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Features showcase area */}
                <div className="features-section">
                    <div className="features-header">
                        <span className="section-tag">Game Features</span>
                        <h2 className="features-title">
                            Strategic battles deliver
                            <br />
                            real value returns in gaming
                        </h2>
                    </div>

                    <div className="features-grid">
                        <div className="feature-card feature-card-3d">
                            <div className="feature-icon feature-icon-3d">🤖</div>
                            <h3>AI Opponent Challenge</h3>
                            <p>Engage in strategic battles against intelligent AI and earn rewards for every victory</p>
                        </div>
                        <div className="feature-card feature-card-3d">
                            <div className="feature-icon feature-icon-3d">💰</div>
                            <h3>ETH Rewards</h3>
                            <p>Winners receive real Ethereum rewards, making every game valuable</p>
                        </div>
                        <div className="feature-card feature-card-3d">
                            <div className="feature-icon feature-icon-3d">⚡</div>
                            <h3>Real-time Battles</h3>
                            <p>Smooth real-time gameplay experience where every move matters</p>
                        </div>
                    </div>
                </div>

                {/* How to play instructions */}
                <div className="how-it-works">
                    <div className="steps-container">
                        <h3 className="section-title">How to Play</h3>
                        <div className="steps-grid">
                            <div className="step-item step-item-3d">
                                <div className="step-number step-number-3d">1</div>
                                <div className="step-content">
                                    <h4>Create Account</h4>
                                    <p>Register your gaming account and start your strategy journey</p>
                                </div>
                            </div>
                            <div className="step-item step-item-3d">
                                <div className="step-number step-number-3d">2</div>
                                <div className="step-content">
                                    <h4>Challenge AI</h4>
                                    <p>Engage in strategic duels with intelligent AI on the Gomoku board</p>
                                </div>
                            </div>
                            <div className="step-item step-item-3d">
                                <div className="step-number step-number-3d">3</div>
                                <div className="step-content">
                                    <h4>Earn Rewards</h4>
                                    <p>Win battles, earn ETH rewards, and climb the leaderboard</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LandingPage; 