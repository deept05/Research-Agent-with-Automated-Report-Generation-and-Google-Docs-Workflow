# Architecture Documentation

## System Overview

The LangChain Research Agent is a production-grade autonomous research system that automates the entire research workflow from query to published Google Doc.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  (Web Browser, API Client, Mobile App, CLI)                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                      FastAPI Server                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Endpoints (/research, /health, /jobs)          │   │
│  │  - Request Validation (Pydantic)                     │   │
│  │  - Background Task Queue                             │   │
│  │  - Error Handling & Logging                          │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   LangGraph Workflow                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  State Machine:                                        │  │
│  │  1. Query Intake → Validate & Initialize              │  │
│  │  2. Web Search → DuckDuckGo Search                    │  │
│  │  3. Content Filter → Relevance Ranking                │  │
│  │  4. Content Extraction → Web Scraping                 │  │
│  │  5. Synthesizer → LLM-based Synthesis                 │  │
│  │  6. Citation Handler → Format Citations               │  │
│  │  7. Report Generator → Markdown Report                │  │
│  │  8. Error Handler → Error Recovery                    │  │
│  └──────────────────────────────────────────────────────┘  │
└──────┬────────────────────────────────────────┬─────────────┘
       │                                        │
       │                                        │
┌──────▼─────────────┐              ┌──────────▼──────────┐
│  Google Docs API   │              │   n8n Workflow      │
│  - Create Document │              │   - Webhook Trigger │
│  - Format Content  │              │   - Notifications   │
│  - Set Permissions │              │   - Data Storage    │
│  - Share Link      │              │   - Email/Slack     │
└────────────────────┘              └─────────────────────┘
```

## Component Details

### 1. API Layer (FastAPI)

**Purpose**: Handle HTTP requests, validation, and background task management

**Key Components**:
- `app/main.py`: Application entry point
- `app/api/routes.py`: REST endpoints
- `app/models/schemas.py`: Request/response models

**Features**:
- Async request handling
- Background task processing
- CORS middleware
- Exception handling
- API documentation (Swagger/ReDoc)

**Endpoints**:
```
POST   /api/v1/research          - Create research job
GET    /api/v1/research/{job_id} - Get job details
GET    /api/v1/research/{job_id}/status - Get job status
GET    /api/v1/jobs               - List all jobs
GET    /api/v1/health             - Health check
```

### 2. Research Agent (LangGraph)

**Purpose**: Orchestrate multi-step research workflow with state management

**Key Components**:
- `app/research_agent/graph.py`: Workflow definition
- `app/research_agent/nodes.py`: Individual processing nodes
- `app/research_agent/state.py`: State management
- `app/research_agent/tools.py`: Research tools

**Workflow Nodes**:

1. **Query Intake Node**
   - Validates query format
   - Initializes state
   - Logs job start

2. **Web Search Node**
   - Uses DuckDuckGo search
   - Fetches top N results
   - Extracts title, URL, snippet

3. **Content Filter Node**
   - Ranks by relevance
   - Filters low-quality results
   - Scores based on query match

4. **Content Extraction Node**
   - Scrapes full page content
   - Converts HTML to text
   - Handles timeouts/errors

5. **Synthesizer Node**
   - LLM-based content synthesis
   - Combines multiple sources
   - Generates coherent summary

6. **Citation Handler Node**
   - Formats citations (APA)
   - Tracks sources
   - Generates reference list

7. **Report Generator Node**
   - Creates structured report
   - Formats in markdown
   - Adds metadata

8. **Error Handler Node**
   - Catches workflow errors
   - Creates error report
   - Logs failures

**State Flow**:
```python
ResearchState {
    # Input
    query: str
    job_id: str
    max_results: int
    
    # Intermediate
    raw_search_results: List
    filtered_results: List
    extracted_content: List
    synthesized_content: str
    
    # Output
    report_markdown: str
    google_doc_url: str
    citations: List
    
    # Metadata
    current_step: str
    error_message: Optional[str]
}
```

### 3. Services Layer

#### Google Docs Service
**File**: `app/services/google_docs.py`

**Responsibilities**:
- Authenticate with service account
- Create new documents
- Insert formatted content
- Set permissions (public/private)
- Move to specific folders
- Generate shareable links

**Authentication Flow**:
1. Load service account credentials
2. Request OAuth2 tokens
3. Build Docs & Drive API clients
4. Execute API operations

#### n8n Client
**File**: `app/services/n8n_client.py`

**Responsibilities**:
- Trigger webhook workflows
- Send report metadata
- Handle async requests
- Manage timeouts/retries

**Workflow Triggers**:
```json
{
  "job_id": "abc-123",
  "google_doc_url": "https://docs.google.com/...",
  "report_title": "Research Report",
  "query": "Original query",
  "citations_count": 10
}
```

#### LLM Service
**File**: `app/services/llm_service.py`

**Responsibilities**:
- Abstract LLM provider
- Handle API calls
- Manage retries
- Token optimization

### 4. Utilities

#### Logger
**File**: `app/utils/logger.py`

**Features**:
- Colored console output
- File rotation (10 MB per file)
- Retention policy (30 days)
- Structured logging
- Per-job log filtering

#### Error Handlers
**File**: `app/utils/error_handlers.py`

**Custom Exceptions**:
- `SearchError`: Web search failures
- `ContentExtractionError`: Scraping failures
- `ReportGenerationError`: LLM/format errors
- `GoogleDocsError`: API failures
- `N8NError`: Webhook failures

## Data Flow

### Complete Request Flow

```
1. Client Request
   └─> POST /api/v1/research
       {query: "What is AI?"}

2. API Validation
   └─> Pydantic validates request
   └─> Generate unique job_id
   └─> Return 202 Accepted

3. Background Processing
   └─> Initialize ResearchState
   └─> Execute LangGraph workflow
       ├─> Query Intake (validate)
       ├─> Web Search (DuckDuckGo)
       ├─> Content Filter (rank)
       ├─> Content Extraction (scrape)
       ├─> Synthesizer (LLM)
       ├─> Citation Handler (format)
       └─> Report Generator (markdown)

4. Google Docs Creation
   └─> Authenticate with service account
   └─> Create new document
   └─> Insert formatted content
   └─> Set permissions
   └─> Generate shareable link

5. n8n Workflow Trigger
   └─> Send webhook with metadata
   └─> n8n receives data
   └─> Execute automation steps
       ├─> Store in Google Sheets
       ├─> Send email notification
       └─> Post to Slack channel

6. Update Job Status
   └─> Mark job as completed
   └─> Store Google Doc URL
   └─> Update completion time

7. Client Polling
   └─> GET /api/v1/research/{job_id}
   └─> Receive completed report link
```

## State Management

### State Object Lifecycle

```
┌─────────────────┐
│  Initial State  │
│  - query        │
│  - job_id       │
│  - settings     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Search State   │
│  + raw_results  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter State   │
│  + filtered     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract State   │
│ + content       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Synthesis State │
│ + synthesized   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final State    │
│  + report_md    │
│  + citations    │
│  + google_url   │
└─────────────────┘
```

## Error Handling Strategy

### Three-Tier Error Handling

1. **Node-Level**: Try-catch in each node
   - Log error
   - Update state with error
   - Continue to error handler

2. **Workflow-Level**: Conditional edges
   - Check for errors after each node
   - Route to error_handler_node
   - Generate error report

3. **API-Level**: FastAPI exception handlers
   - Catch unhandled exceptions
   - Return proper HTTP status
   - Log full stack trace

### Error Recovery

```python
if state["error_message"]:
    # Attempt recovery
    if state["retry_count"] < MAX_RETRIES:
        state["retry_count"] += 1
        return retry_node
    else:
        return error_handler_node
```

## Scalability Considerations

### Current Implementation
- In-memory job storage (dict)
- Single-server deployment
- Synchronous Google Docs creation

### Production Enhancements

1. **Database Integration**
   - PostgreSQL for job persistence
   - Redis for caching
   - MongoDB for document storage

2. **Queue System**
   - Celery for async tasks
   - RabbitMQ/Redis as broker
   - Multiple worker processes

3. **Load Balancing**
   - Multiple FastAPI instances
   - Nginx reverse proxy
   - Horizontal scaling

4. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert rules

5. **Rate Limiting**
   - Token bucket algorithm
   - Per-user limits
   - API key authentication

## Security Considerations

### API Security
- Input validation (Pydantic)
- SQL injection prevention
- XSS protection
- CORS configuration

### Credentials Management
- Environment variables
- Secret managers (AWS/GCP)
- Encrypted storage
- Rotation policies

### Google API Security
- Service account isolation
- Principle of least privilege
- Scoped permissions
- Audit logging

## Deployment Options

### Option 1: Railway
- Git-based deployment
- Auto-scaling
- Environment management
- $5-20/month

### Option 2: Vercel
- Serverless functions
- Edge network
- Zero config
- Free tier available

### Option 3: Google Cloud Run
- Container-based
- Auto-scaling to zero
- Pay per request
- Easy CI/CD integration

### Option 4: AWS (ECS/Lambda)
- Full control
- Advanced networking
- Multiple services
- Complex but powerful

## Monitoring & Observability

### LangSmith Integration
- Trace every workflow execution
- View node transitions
- Debug failures
- Performance metrics

### Application Logs
- Structured JSON logs
- Log levels (DEBUG/INFO/WARN/ERROR)
- Request ID tracking
- Performance timing

### Health Checks
- `/api/v1/health` endpoint
- Service status checks
- Dependency validation

## Performance Optimization

### Current Performance
- Search: 2-5 seconds
- Content extraction: 5-10 seconds
- LLM synthesis: 10-20 seconds
- Total: 20-40 seconds per request

### Optimization Strategies
1. Parallel content extraction
2. LLM response streaming
3. Result caching
4. Async operations
5. Connection pooling

## Future Enhancements

1. **Advanced Search**
   - Multiple search engines
   - Academic paper search
   - Custom data sources

2. **Better Synthesis**
   - Multi-model ensemble
   - Fact verification
   - Contradiction detection

3. **Rich Reports**
   - Charts and graphs
   - Images and diagrams
   - Interactive elements

4. **Collaboration**
   - Shared research sessions
   - Comments and annotations
   - Version control

5. **AI Agents**
   - Planning agent
   - Quality checker
   - Editor agent