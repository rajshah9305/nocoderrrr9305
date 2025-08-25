# 🚀 AI App Builder Pro

A fullstack platform that uses AI agents to automatically generate, design, and deploy web applications.

## ✨ Features

- **Multi-Agent AI System**: 6 specialized AI agents for complete app development
- **Real-time Generation**: Live progress tracking with WebSocket updates
- **Service Integrations**: AI models, deployment platforms, databases
- **Interactive Chat**: AI-powered assistance
- **Project Management**: Complete CRUD operations
- **Modern UI**: Responsive design with Tailwind CSS

## 🛠️ Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: Flask + SQLAlchemy + SocketIO
- **Database**: SQLite
- **AI**: Cerebras, OpenAI, Anthropic
- **Deployment**: Vercel

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd ai-app-builder-pro

# Install dependencies
npm install
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run development
npm run dev        # Frontend (localhost:5173)
python backend/app.py  # Backend (localhost:5000)
```

## 🌐 Deploy to Vercel

1. Push to GitHub
2. Connect repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically

### Required Environment Variables

```env
CEREBRAS_API_KEY=your_cerebras_key
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_secure_secret_key
```

## 📁 Project Structure

```
ai-app-builder-pro/
├── backend/           # Flask API
│   ├── models/        # Database models
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   └── app.py         # Main application
├── src/               # React frontend
│   ├── App.jsx        # Main component
│   ├── main.jsx       # Entry point
│   └── index.css      # Styles
├── public/            # Static assets
├── package.json       # Dependencies
├── requirements.txt   # Python packages
└── vercel.json        # Deployment config
```

## 🎯 Usage

1. **Describe** your app idea
2. **Generate** with AI agents
3. **Preview** in real-time
4. **Deploy** to production

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.