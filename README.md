# AI App Builder Pro

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
