<<<<<<< HEAD
# LangChain Research Agent

An autonomous research agent built with LangChain, LangGraph, FastAPI, Google Docs, and n8n integration. Automatically searches, synthesizes, and generates comprehensive research reports with citations.

## 🚀 Features

- **Autonomous Research**: Automated web search, content extraction, and synthesis
- **LangGraph Workflow**: Modular, stateful research pipeline with error handling
- **Google Docs Integration**: Automatic report generation in Google Docs
- **n8n Automation**: Workflow automation for notifications and storage
- **RESTful API**: FastAPI-based API with async support
- **Multi-user Support**: Handle multiple concurrent research requests
- **Citation Management**: Automatic citation generation in APA format
- **Monitoring**: LangSmith integration for workflow observability

## 📋 Prerequisites

- Python 3.9+
- OpenAI API key
- Google Cloud Project with Docs & Drive API enabled
- n8n instance (optional but recommended)
- LangSmith account (optional, for monitoring)

## 🛠️ Installation

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <your-repo-url>
cd langchain-research-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google service account JSON
- `N8N_WEBHOOK_URL`: Your n8n webhook URL (optional)
- `LANGCHAIN_API_KEY`: LangSmith API key (optional)

### 3. Setup Google Cloud Credentials

1. Create a Google Cloud Project
2. Enable Google Docs API and Google Drive API
3. Create a service account
4. Download the JSON key file
5. Set path in `.env`: `GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json`
6. Share your Google Drive folder with the service account email

### 4. Setup n8n Workflow (Optional)

1. Create a new workflow in n8n
2. Add a Webhook node as trigger
3. Add Google Sheets/Email/Slack nodes for notifications
4. Copy webhook URL to `.env`

## 🚀 Running the Application

### Development Mode

```bash
# Run with uvicorn
python app/main.py

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using gunicorn with uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

## 📡 API Endpoints

### Create Research Job

```bash
POST /api/v1/research
```

Request body:
```json
{
  "query": "What are the latest developments in quantum computing?",
  "user_id": "user123",
  "max_results": 10,
  "include_citations": true
}
```

Response:
```json
{
  "job_id": "abc-123-def",
  "status": "pending",
  "query": "What are the latest developments in quantum computing?",
  "created_at": "2025-01-28T10:00:00"
}
```

### Get Job Status

```bash
GET /api/v1/research/{job_id}
```

### Check Health

```bash
GET /api/v1/health
```

### List All Jobs

```bash
GET /api/v1/jobs?limit=10&offset=0
```

## 🏗️ Architecture

```
┌─────────────┐
│   FastAPI   │
│     API     │
└──────┬──────┘
       │
┌──────▼──────────────────────────────┐
│        LangGraph Workflow           │
├─────────────────────────────────────┤
│  1. Query Intake                    │
│  2. Web Search (DuckDuckGo)         │
│  3. Content Filter (Relevance)      │
│  4. Content Extraction (Scraping)   │
│  5. Synthesizer (LLM)               │
│  6. Citation Handler                │
│  7. Report Generator                │
│  8. Error Handler                   │
└──────┬──────────────────────────────┘
       │
┌──────▼──────────┐     ┌──────────────┐
│  Google Docs    │     │     n8n      │
│   Integration   │     │   Workflow   │
└─────────────────┘     └──────────────┘
```

## 📁 Project Structure

```
langchain-research-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── research_agent/
│   │   ├── graph.py            # LangGraph workflow
│   │   ├── nodes.py            # Workflow nodes
│   │   ├── state.py            # State management
│   │   └── tools.py            # Research tools
│   ├── services/
│   │   ├── google_docs.py      # Google Docs integration
│   │   ├── n8n_client.py       # n8n client
│   │   └── llm_service.py      # LLM wrapper
│   ├── utils/
│   │   ├── logger.py           # Logging
│   │   └── error_handlers.py  # Error handling
│   └── api/
│       └── routes.py           # API routes
├── tests/
│   └── test_api.py            # API tests
├── logs/                       # Application logs
├── .env                        # Environment variables
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py -v
```

## 🚢 Deployment

### Railway

1. Create new project on Railway
2. Connect GitHub repository
3. Add environment variables
4. Deploy automatically

### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Create `vercel.json`:
```json
{
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```
3. Deploy: `vercel --prod`

### Google Cloud Platform

```bash
# Build and deploy to Cloud Run
gcloud run deploy research-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Monitoring

### LangSmith

View workflow traces in LangSmith dashboard:
1. Go to https://smith.langchain.com
2. Select your project
3. View traces for each research job

### Application Logs

```bash
# View logs
tail -f logs/app.log

# View specific job logs
grep "job_id" logs/app.log
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | Model name (e.g., gpt-4-turbo-preview) | No |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google service account JSON | Yes |
| `N8N_WEBHOOK_URL` | n8n webhook URL | No |
| `LANGCHAIN_API_KEY` | LangSmith API key | No |
| `MAX_SEARCH_RESULTS` | Maximum search results | No |
| `MAX_CONTENT_LENGTH` | Max content length per page | No |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

**Issue**: Google Docs API authentication fails
- **Solution**: Verify service account JSON path and permissions

**Issue**: Search returns no results
- **Solution**: Check internet connectivity and DuckDuckGo availability

**Issue**: LangSmith traces not appearing
- **Solution**: Verify `LANGCHAIN_API_KEY` and `LANGCHAIN_TRACING_V2=true`

**Issue**: n8n webhook timeout
- **Solution**: Increase timeout in `app/services/n8n_client.py`

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check documentation at `/docs` endpoint
- Review logs in `logs/app.log`

## 🎯 Roadmap

- [ ] Add database persistence (PostgreSQL/MongoDB)
- [ ] Implement rate limiting and authentication
- [ ] Add React frontend dashboard
- [ ] Support for multiple LLM providers
- [ ] Advanced citation formats (MLA, Chicago)
- [ ] PDF report generation
- [ ] Collaborative research features
- [ ] Advanced search filters and ranking

---

Built with ❤️ using LangChain, FastAPI, and modern Python tools
=======
# Research-Agent-with-Automated-Report-Generation-and-Google-Docs-Workflow
>>>>>>> 939978c77287c2d63307e4e6c25a07e18c47dc55
