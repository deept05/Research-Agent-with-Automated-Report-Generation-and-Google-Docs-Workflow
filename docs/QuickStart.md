# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] OpenAI API key
- [ ] Google Cloud account (for Docs API)
- [ ] Git installed

## Step-by-Step Setup

### 1. Clone and Install (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd langchain-research-agent

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys (3 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**Minimum required configuration**:
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

**Optional but recommended**:
```bash
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/...
```

### 3. Setup Google Docs (5 minutes)

#### Option A: Skip Google Docs (for testing)
You can test without Google Docs integration - reports will be in memory only.

#### Option B: Full Setup

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Create new project: "Research Agent"

2. **Enable APIs**
   - Enable Google Docs API
   - Enable Google Drive API

3. **Create Service Account**
   - Go to IAM & Admin → Service Accounts
   - Create Service Account: "research-agent-sa"
   - Grant role: "Editor"
   - Create JSON key → Download

4. **Configure Credentials**
   ```bash
   # Move downloaded JSON to project root
   mv ~/Downloads/service-account-key.json ./service-account.json
   
   # Update .env
   GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
   ```

5. **Create Google Drive Folder (Optional)**
   - Create folder in Google Drive
   - Share with service account email
   - Copy folder ID from URL
   - Add to .env: `GOOGLE_DOCS_FOLDER_ID=your-folder-id`

### 4. Run the Application

```bash
# Start the server
python app/main.py

# You should see:
# INFO:     Started server process
# INFO:     Application startup complete
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Test the API (2 minutes)

#### Option 1: Using cURL

```bash
# Create a research job
curl -X POST "http://localhost:8000/api/v1/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is LangChain?",
    "max_results": 5,
    "include_citations": true
  }'

# Response:
# {
#   "job_id": "abc-123-def",
#   "status": "pending",
#   "query": "What is LangChain?"
# }

# Check job status
curl "http://localhost:8000/api/v1/research/abc-123-def"
```

#### Option 2: Using Python

```python
import requests
import time

# Create research job
response = requests.post(
    "http://localhost:8000/api/v1/research",
    json={
        "query": "What are the benefits of AI agents?",
        "max_results": 5
    }
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# Poll for completion
while True:
    status_response = requests.get(
        f"http://localhost:8000/api/v1/research/{job_id}"
    )
    data = status_response.json()
    
    print(f"Status: {data['status']}")
    
    if data["status"] == "completed":
        print(f"Google Doc: {data['google_doc_url']}")
        print(f"Summary: {data['summary']}")
        break
    elif data["status"] == "failed":
        print(f"Error: {data['error_message']}")
        break
    
    time.sleep(5)
```

#### Option 3: Using the Interactive API Docs

1. Open browser: http://localhost:8000/docs
2. Click on `POST /api/v1/research`
3. Click "Try it out"
4. Enter your query
5. Click "Execute"
6. Copy the `job_id` from response
7. Use `GET /api/v1/research/{job_id}` to check status

### 6. View Results

The API response will include:
- `job_id`: Unique identifier
- `status`: pending/processing/completed/failed
- `google_doc_url`: Link to generated Google Doc (if configured)
- `summary`: Brief summary of findings
- `created_at`: Timestamp

## Common Issues & Solutions

### Issue: "OpenAI API key not found"
**Solution**: Make sure `OPENAI_API_KEY` is set in `.env` file

### Issue: "Google Docs service not initialized"
**Solution**: 
- Check if `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Verify the JSON file exists
- Ensure APIs are enabled in Google Cloud Console

### Issue: "Module not found"
**Solution**: Make sure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Port already in use"
**Solution**: Change port in `.env` or kill existing process
```bash
# Change port
PORT=8001

# Or kill existing process (Unix/Mac)
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Search returns no results
**Solution**: 
- Check internet connection
- Verify DuckDuckGo is accessible
- Try a different query

## Next Steps

### 1. Setup n8n Automation (Optional)

Create an n8n workflow to:
- Receive webhook when research completes
- Store data in Google Sheets
- Send email notifications
- Post to Slack

**Basic n8n Workflow**:
```
Webhook (POST) 
  → Google Sheets (Append Row)
  → Gmail (Send Email)
  → Slack (Post Message)
```

Copy your webhook URL to `.env`:
```bash
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/abc123
```

### 2. Enable LangSmith Monitoring

1. Sign up at https://smith.langchain.com
2. Get API key from settings
3. Add to `.env`:
```bash
LANGCHAIN_API_KEY=your-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=research-agent
```

View traces at: https://smith.langchain.com

### 3. Deploy to Production

Choose your platform:

**Railway** (Easiest):
```bash
# Install Railway CLI
npm i -g railway

# Login and deploy
railway login
railway init
railway up
```

**Vercel** (Serverless):
```bash
npm i -g vercel
vercel --prod
```

**Google Cloud Run** (Scalable):
```bash
gcloud run deploy research-agent \
  --source . \
  --platform managed \
  --region us-central1
```

### 4. Build a Frontend

Create a simple web interface:
```bash
cd frontend
npx create-react-app research-dashboard
cd research-dashboard
npm start
```

Sample React component:
```jsx
function ResearchForm() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    const response = await fetch('http://localhost:8000/api/v1/research', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query, max_results: 10})
    });
    const data = await response.json();
    setResult(data);
  };

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <button onClick={handleSubmit}>Research</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
```

## Testing

Run the test suite:
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=app tests/
```

## Getting Help

- **Documentation**: Check `/docs` endpoint for API documentation
- **Logs**: View `logs/app.log` for detailed logs
- **Issues**: Open an issue on GitHub
- **LangSmith**: Check traces for workflow debugging

## Example Queries to Try

1. "What are the latest developments in quantum computing?"
2. "Explain the benefits and risks of artificial intelligence"
3. "How does blockchain technology work?"
4. "What is the current state of renewable energy?"
5. "Compare different machine learning frameworks"

## Performance Tips

- **Parallel processing**: The system handles multiple requests concurrently
- **Caching**: Results are cached for 1 hour by default
- **Rate limiting**: Default is 10 requests per minute
- **Timeout**: Web scraping has 10-second timeout per page

## Security Best Practices

1. **Never commit `.env`** - It contains secrets
2. **Use environment variables** in production
3. **Rotate API keys** regularly
4. **Limit CORS origins** in production
5. **Use HTTPS** for production deployments
6. **Enable authentication** for public APIs

## Monitoring Production

Monitor these metrics:
- Request rate (requests/minute)
- Average response time
- Error rate
- Queue depth
- Google API usage
- LLM token usage

Use tools like:
- **Prometheus + Grafana**: Metrics and dashboards
- **Sentry**: Error tracking
- **LangSmith**: Workflow observability
- **Google Cloud Monitoring**: Infrastructure metrics

---

🎉 **Congratulations!** You now have a working research agent. Start with simple queries and gradually explore advanced features.

For detailed documentation, see `README.md` and `docs/architecture.md`.