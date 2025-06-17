import React from 'react';
import './Resume.css';

const Resume = () => {
    const skills = {
        'Programming Languages': ['Java', 'Python', 'Go', 'TypeScript', 'JavaScript', 'Solidity'],
        'Backend / Serverless': ['Spring Boot', 'Django', 'FastAPI', 'Node.js', 'AWS Lambda', 'RESTful APIs'],
        'Frontend': ['React.js', 'Vue.js', 'HTML5', 'CSS3', 'Tailwind', 'Bootstrap'],
        'Database Systems': ['MySQL', 'MongoDB', 'Oracle', 'Redis', 'Elasticsearch'],
        'Cloud / DevOps': ['AWS (Lambda, EC2, S3, RDS, Cognito)', 'Docker', 'Kubernetes', 'CI/CD', 'Git', 'GitHub Actions'],
        'AI / Web3': ['OpenAI API', 'LangChain', 'FAISS', 'Prompt Engineering', 'Ethereum', 'Smart Contracts', 'Web3.js', 'DeFi', 'MEV Strategies'],
        'Languages (Human)': ['Mandarin (native)', 'English (fluent)']
    };

    return (
        <div className="resume-container">
            <div className="resume-header">
                <h1>ChengHao</h1>
                <h2>Software Engineer</h2>
                <div className="contact-info">
                    <p>📧 hao.streamnz@gmail.com</p>
                    <p>📍 Auckland, New Zealand</p>
                    <p>🔗 <a href="https://www.linkedin.com/in/iamhaocheng/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
                    <p>💻 <a href="https://github.com/streamnz" target="_blank" rel="noopener noreferrer">GitHub</a></p>
                </div>
            </div>

            <div className="resume-section">
                <h3>Professional Summary</h3>
                <p>
                    Software Engineer with 9+ years of experience in backend development, currently completing a Master of Software Engineering in New Zealand.
                    Skilled in Java, Python, and Go, with hands‑on expertise in building scalable microservices, AI‑powered platforms, and cloud‑native systems using
                    AWS and Docker. Currently interning at an AI startup, applying OpenAI, LangChain, and VectorDB in production. Holder of New Zealand Resident
                    Visa and actively seeking full‑time opportunities in backend or full‑stack roles.
                </p>
            </div>

            <div className="resume-section">
                <h3>Technical Skills</h3>
                <div className="skills-grid">
                    {Object.entries(skills).map(([category, items]) => (
                        <div key={category} className="skill-category">
                            <h4>{category}</h4>
                            <ul>
                                {items.map((skill, index) => (
                                    <li key={index}>{skill}</li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Resume; 