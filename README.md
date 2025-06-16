# StreamNZ Gomoku AI Battle Platform

> A Gomoku (Five-in-a-Row) battle and analysis platform based on Flask + React + Socket.IO + multiple AI models (DeepSeek/Llama3), supporting both local and cloud deployment, compatible with AWS, Amplify, EC2, ELB, and more.

---

## Directory Structure

```
.
├── app.py                # Flask main app entry, WebSocket & API service
├── requirements.txt      # Python dependencies
├── config.py             # Config file
├── ai/                   # AI strategies (DeepSeek/Llama3/OpenAI, etc.)
├── websocket/            # WebSocket event handlers
├── controller/           # API routes
├── model/                # Data models
├── service/dao/utils/    # Business logic / Data access / Utilities
├── frontend/             # React frontend
│   ├── src/
│   │   ├── component/    # Main page components
│   │   ├── config/       # Frontend environment config
│   │   ├── interceptor/  # Axios interceptors
│   │   └── api/          # API call wrappers
│   ├── public/
│   └── package.json
└── LICENSE
```

---

## Quick Start

### 1. Backend (Flask)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables (for AI/DB/keys, if needed)
cp .env.example .env
# Edit .env and fill in API keys, etc.

# Start service (development mode)
python app.py

# For production, use gunicorn + eventlet
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5050 app:flask_app
```

### 2. Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Local development
npm start

# Build for production
npm run build
```

### 3. Configure Environment Variables

- Frontend environment variables (for Amplify/local):
  ```
  REACT_APP_API_BASE_URL=https://aigame.streamnz.com
  REACT_APP_SOCKET_URL=https://aigame.streamnz.com
  ```
- Backend CORS is open to all origins by default; for production, specify allowed domains.

---

## Main Features

- Gomoku battle (15x15 standard board)
- Human vs AI / AI vs AI
- Multiple AI model switching (DeepSeek/Llama3/OpenAI)
- Real-time WebSocket communication
- Smart move selection, threat detection, attack/defense analysis
- User registration/login/session management
- Rich frontend interaction and animation

---

## AI Capabilities

See [ai/README.md](ai/README.md)

- Supports DeepSeek/Llama3/OpenAI models
- Smart threat detection, opportunity analysis, auto fallback
- Supports both local and cloud inference
- Extensible for custom AI strategies

---

## CORS & Deployment

- Compatible with AWS ELB/ALB, Amplify, EC2, and other major cloud environments
- Backend supports global CORS (can be restricted as needed)
- Frontend supports custom API/Socket URLs for multi-domain deployment
- See [AWS_ELB_CORS_GUIDE.md](AWS_ELB_CORS_GUIDE.md) for details

---

## Dependencies

- Python 3.8+
- Flask, Flask-SocketIO, Flask-CORS, Flask-JWT-Extended, SQLAlchemy, eventlet, gunicorn, requests, openai, deepseek, etc.
- Node.js 18+, React 18+, socket.io-client, axios, etc.

---

## License

MIT License  
Copyright (c) 2024 luckyGuy

---

For detailed AI strategies, advanced development, cloud deployment, Nginx/ELB configuration, etc., please refer to subdirectory READMEs or contact the author. 