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

                {/* What's Next Section */}
                <div className="whats-next-section">
                    <div className="section-header">
                        <span className="section-tag rocket-tag">🚀 What's Next</span>
                        <h2 className="section-title gradient-text">
                            Building the Future of Web3 Gaming
                        </h2>
                        <p className="section-subtitle">
                            We're designing a Web3-native platform where creativity meets decentralization
                        </p>
                    </div>

                    {/* Genesis Airdrop Banner */}
                    <div className="genesis-banner genesis-banner-3d">
                        <div className="banner-content">
                            <div className="banner-icon">🎁</div>
                            <div className="banner-text">
                                <h3>Genesis Airdrop Now Live</h3>
                                <p>Defeat our AI in battle and earn exclusive reward tokens!</p>
                                <span className="banner-highlight">
                                    Early tokens will be redeemable when blockchain integration goes live
                                </span>
                            </div>
                            <div className="banner-cta">
                                <button className="airdrop-button" onClick={onGetStarted}>
                                    Start Earning
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Vision Cards */}
                    <div className="vision-section">
                        <div className="vision-header">
                            <span className="section-tag">🔮 Our Vision</span>
                        </div>
                        <div className="vision-grid">
                            <div className="vision-card vision-card-3d">
                                <div className="vision-icon">🔄</div>
                                <h4>Decentralized Reward Tokens</h4>
                                <p>Earn tokens by interacting with the platform — trade them freely with others via peer-to-peer transactions.</p>
                            </div>
                            <div className="vision-card vision-card-3d">
                                <div className="vision-icon">🏛️</div>
                                <h4>Centralized Exchange Access</h4>
                                <p>An easy-to-use exchange inside our platform to help users buy, sell, or convert their tokens securely.</p>
                            </div>
                            <div className="vision-card vision-card-3d">
                                <div className="vision-icon">📚</div>
                                <h4>NovelVerse.io – Read. Watch. Earn.</h4>
                                <p>AI-generated novel and video platform rewarding users with reading tokens for immersive stories and content.</p>
                            </div>
                            <div className="vision-card vision-card-3d">
                                <div className="vision-icon">⛓️</div>
                                <h4>Cross-Chain Support</h4>
                                <p>Seamless swap between STREAM tokens and major cryptocurrencies like ETH, BTC, or USDT.</p>
                            </div>
                        </div>
                    </div>

                    {/* Token Utility Section */}
                    <div className="token-utility-section">
                        <div className="utility-header">
                            <span className="section-tag">🎯 Token Utility</span>
                            <h3>More Than Just a Coin</h3>
                        </div>
                        <div className="utility-grid">
                            <div className="utility-item utility-item-3d">
                                <div className="utility-icon">🔓</div>
                                <span>Unlock novel chapters, videos, and game modes</span>
                            </div>
                            <div className="utility-item utility-item-3d">
                                <div className="utility-icon">🤖</div>
                                <span>Access premium AI characters and storylines</span>
                            </div>
                            <div className="utility-item utility-item-3d">
                                <div className="utility-icon">📈</div>
                                <span>Trade or hold for future platform growth</span>
                            </div>
                            <div className="utility-item utility-item-3d">
                                <div className="utility-icon">🌐</div>
                                <span>Participate in a self-sustaining content economy</span>
                            </div>
                        </div>
                    </div>

                    {/* Closing Message */}
                    <div className="closing-section">
                        <div className="closing-content">
                            <div className="closing-icon">🌱</div>
                            <h3>We're just getting started</h3>
                            <p>Stay tuned and be among the first to shape the next generation of decentralized storytelling and digital experiences.</p>
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