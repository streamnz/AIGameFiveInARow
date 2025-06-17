import React from 'react';
import { useNavigate } from 'react-router-dom';
import './About.css';

const About = () => {
    const navigate = useNavigate();

    const handleAvatarClick = () => {
        navigate('/resume');
    };

    const techStack = [
        {
            category: "Frontend Technologies",
            icon: "🖥️",
            technologies: [
                { name: "React 18", description: "Modern frontend framework with component-based architecture" },
                { name: "JavaScript ES6+", description: "Modern JavaScript syntax and features" },
                { name: "CSS3 & Animations", description: "Responsive design with 3D animation effects" },
                { name: "Axios", description: "HTTP client for API request management" },
                { name: "Socket.IO Client", description: "Real-time bidirectional communication" }
            ]
        },
        {
            category: "Backend Technologies",
            icon: "⚙️",
            technologies: [
                { name: "Flask", description: "Lightweight Python web framework" },
                { name: "Golang", description: "High-performance backend services and microservices" },
                { name: "Flask-SocketIO", description: "WebSocket real-time communication" },
                { name: "SQLAlchemy", description: "Python ORM for database operations" },
                { name: "JWT", description: "JSON Web Token authentication" },
                { name: "RESTful API", description: "Standardized API interface design" }
            ]
        },
        {
            category: "Database",
            icon: "🗄️",
            technologies: [
                { name: "MySQL", description: "Relational database management system" },
                { name: "Vector Database", description: "Vector database for AI model support" }
            ]
        },
        {
            category: "AI & Machine Learning",
            icon: "🤖",
            technologies: [
                { name: "DeepSeek API", description: "Intelligent Gomoku AI opponent" },
                { name: "OpenAI GPT", description: "Large language model integration" },
                { name: "Llama 3", description: "Local large model deployment" },
                { name: "LangChain", description: "AI application development framework" }
            ]
        },
        {
            category: "Cloud Services & Deployment",
            icon: "☁️",
            technologies: [
                { name: "AWS EC2", description: "Cloud server deployment" },
                { name: "AWS Amplify", description: "Frontend hosting and CI/CD" },
                { name: "AWS SES", description: "Email service integration" },
                { name: "AWS ELB", description: "Load balancer" },
                { name: "Gunicorn", description: "WSGI HTTP server" }
            ]
        },
        {
            category: "Development Tools",
            icon: "🛠️",
            technologies: [
                { name: "Git & GitHub", description: "Version control and code management" },
                { name: "Docker", description: "Containerized deployment" },
                { name: "Nginx", description: "Reverse proxy server" },
                { name: "npm & pip", description: "Package management tools" }
            ]
        }
    ];

    return (
        <div className="about-page">
            <div className="about-container">

                <div className="about-content">
                    {/* Header Section */}
                    <div className="about-header">
                        <div className="author-info">
                            <div className="avatar">
                                <div 
                                    className="avatar-placeholder clickable-avatar" 
                                    onClick={handleAvatarClick}
                                    title="Click to view my resume"
                                >
                                    H
                                </div>
                            </div>
                            <div className="author-details">
                                <h1 className="author-name">ChengHao</h1>
                                <p className="author-title">Full Stack Developer | AI Application Developer</p>
                                <div className="contact-links">
                                    <a 
                                        href="https://www.linkedin.com/in/haostreamnz/" 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="contact-link linkedin"
                                    >
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                                        </svg>
                                        LinkedIn
                                    </a>
                                    <a 
                                        href="https://github.com/streamnz/StreamNZ" 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="contact-link github"
                                    >
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                        </svg>
                                        GitHub
                                    </a>
                                    <a 
                                        href="mailto:hao.streamnz@gmail.com"
                                        className="contact-link email"
                                    >
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                                            <polyline points="22,6 12,13 2,6"/>
                                        </svg>
                                        Email
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Project Description */}
                    <div className="project-description">
                        <h2>🎮 StreamNZ Gomoku AI Platform</h2>
                        <p>
                            This is an intelligent Gomoku battle platform developed with modern web technology stack, 
                            integrating multiple AI models and cloud services. The project demonstrates full-stack 
                            development capabilities from frontend interaction design to backend architecture, 
                            from AI model integration to cloud deployment. It's particularly suitable for showcasing 
                            technical expertise and project experience in job applications.
                        </p>
                    </div>

                    {/* Tech Stack Grid */}
                    <div className="tech-stack-section">
                        <h2>🛠️ Technology Stack</h2>
                        <div className="tech-grid">
                            {techStack.map((category, index) => (
                                <div key={index} className="tech-category">
                                    <div className="category-header">
                                        <span className="category-icon">{category.icon}</span>
                                        <h3>{category.category}</h3>
                                    </div>
                                    <div className="tech-list">
                                        {category.technologies.map((tech, techIndex) => (
                                            <div key={techIndex} className="tech-item">
                                                <div className="tech-name">{tech.name}</div>
                                                <div className="tech-description">{tech.description}</div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Key Features */}
                    <div className="features-highlight">
                        <h2>✨ Key Features</h2>
                        <div className="features-list">
                            <div className="feature-item">
                                <span className="feature-icon">🎯</span>
                                <div>
                                    <strong>Intelligent AI Battle</strong>
                                    <p>Integration of multiple AI models: DeepSeek, OpenAI, Llama3</p>
                                </div>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">⚡</span>
                                <div>
                                    <strong>Real-time Communication</strong>
                                    <p>Low-latency real-time gaming experience via WebSocket</p>
                                </div>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">🔐</span>
                                <div>
                                    <strong>Secure Authentication</strong>
                                    <p>Complete user system with JWT token + email verification</p>
                                </div>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">☁️</span>
                                <div>
                                    <strong>Cloud Deployment</strong>
                                    <p>Production-grade deployment with full AWS services support</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="about-footer">
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About; 