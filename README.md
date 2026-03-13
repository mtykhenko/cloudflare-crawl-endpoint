# 🕷️ Web Crawler Application

A simple web application for crawling websites using Cloudflare's Browser Rendering API. Built with React frontend and Python FastAPI backend, fully containerized with Docker.

## ⚠️ Important Disclaimer

**This is a development/sandbox level implementation.** For production use, additional security measures, error handling, monitoring, authentication, rate limiting, and other production-grade considerations must be implemented. See the [Deployment](#-deployment) section for production considerations.

## 🤖 Built with IBM Bob

This application was developed using [IBM Bob](https://www.ibm.com/products/bob), an AI-powered coding assistant that helped architect, implement, and document this project following best practices and modern development patterns.

## ✨ Features

- **Simple Interface**: Easy-to-use form for entering URL and crawl depth
- **Real-time Status**: Live updates on crawl progress with polling
- **Markdown Rendering**: Beautiful display of crawled content in Markdown format
- **Cloudflare Integration**: Leverages Cloudflare Browser Rendering API for JavaScript-enabled crawling
- **Containerized**: Fully dockerized for easy deployment
- **Layered Architecture**: Clean separation of concerns with API, service, and client layers
- **Comprehensive Error Handling**: Detailed error messages with proper HTTP status codes
- **Type Safety**: Pydantic models for request/response validation
- **Interactive API Docs**: Auto-generated OpenAPI documentation with Swagger UI
- **Async Operations**: Non-blocking HTTP requests for better performance

## 🏗️ Architecture

- **Frontend**: React 18 + Vite + Axios
- **Backend**: Python 3.11 + FastAPI + httpx (async)
- **API**: Cloudflare Browser Rendering API
- **Deployment**: Docker + Docker Compose

### Backend Architecture

The backend follows a **layered architecture** pattern for maintainability and testability:

1. **API Layer** (`app/api/`):
   - Route handlers with OpenAPI documentation
   - Centralized exception handling
   - Request/response validation

2. **Service Layer** (`app/services/`):
   - Business logic and orchestration
   - Separation from HTTP concerns
   - Reusable across different interfaces

3. **Client Layer** (`app/cloudflare_client.py`):
   - External API integration
   - Error handling and retry logic
   - Async HTTP operations

4. **Models** (`app/models.py`):
   - Pydantic models for type safety
   - Automatic validation
   - OpenAPI schema generation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation and [AGENTS.md](AGENTS.md) for developer guidance.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Docker** or **Podman** installed
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)
   - [Podman Installation Guide](https://podman.io/getting-started/installation)

2. **Cloudflare Account** with Browser Rendering API access
   - Sign up at [Cloudflare](https://www.cloudflare.com/)
   - Enable Browser Rendering in your account

3. **Cloudflare API Credentials**
   - Account ID (found in Cloudflare Dashboard)
   - API Token with "Browser Rendering - Edit" permission

### Getting Cloudflare API Token

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Go to **My Profile** → **API Tokens**
3. Click **Create Token**
4. Use the **Custom Token** template
5. Add permission: **Account** → **Browser Rendering** → **Edit**
6. Click **Continue to Summary** → **Create Token**
7. Copy and save your token securely

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/mtykhenko/cloudflare-crawl-endpoint.git
cd cloudflare-crawl-endpoint
```

### 2. Configure Environment Variables

Create a `.env` file in the **backend** directory:

```bash
# Copy the example file
cp backend/.env.example backend/.env

# Edit with your credentials
nano backend/.env
```

Add your Cloudflare credentials:

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
PORT=8000
LOG_LEVEL=INFO
```

**Note**: The `.env` file should be in the `backend/` directory, not the project root.

### 3. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Development Setup

### Backend Development

The backend follows a layered architecture with clear separation of concerns:
- **API Layer** (`app/api/`): Route handlers and exception handling
- **Service Layer** (`app/services/`): Business logic and orchestration
- **Client Layer** (`app/cloudflare_client.py`): External API integration
- **Models** (`app/models.py`): Request/response validation with Pydantic

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your Cloudflare credentials

# Run development server with auto-reload
uvicorn app.main:app --reload --port 8000

# Or run with custom log level
uvicorn app.main:app --reload --port 8000 --log-level debug
```

Backend will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Run development server
npm run dev
```

Frontend will be available at http://localhost:3000

## 🐳 Docker Commands

### Using Docker Compose

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
```

### Using Podman Compose

```bash
# Start services
podman-compose up

# Start in background
podman-compose up -d

# Stop services
podman-compose down

# View logs
podman-compose logs -f
```

## 📖 Usage

1. **Enter URL**: Type the website URL you want to crawl (e.g., `https://example.com`)
2. **Set Depth**: Choose crawl depth (1-100) - how many link levels to follow
3. **Start Crawl**: Click "Start Crawl" button
4. **Monitor Progress**: Watch real-time status updates
5. **View Results**: Browse crawled pages in markdown format
6. **New Crawl**: Click "New Crawl" to start another crawl

### Example Crawl

- **URL**: `https://example.com`
- **Depth**: `2`
- **Result**: Crawls the homepage and all pages linked from it (up to 2 levels deep)

## 🔌 API Endpoints

The API follows RESTful principles with comprehensive error handling and validation.

### Health Check
```http
GET /api/health

Response: 200 OK
{
  "status": "healthy"
}
```

### Initiate Crawl
```http
POST /api/crawl
Content-Type: application/json

{
  "url": "https://example.com",
  "depth": 2
}

Response: 202 Accepted
{
  "job_id": "abc123...",
  "status": "running"
}

Error Responses:
- 400: Invalid request parameters
- 401: Invalid Cloudflare credentials
- 429: Rate limit exceeded
- 502: Cloudflare API error
```

### Get Crawl Status
```http
GET /api/crawl/{job_id}

Response: 200 OK
{
  "job_id": "abc123...",
  "status": "running",
  "total": 10,
  "finished": 5,
  "browser_seconds_used": 12.5,
  "results": [
    {
      "url": "https://example.com",
      "status": "completed",
      "markdown": "# Page Content...",
      "metadata": {
        "status": 200,
        "title": "Example Domain",
        "url": "https://example.com"
      }
    }
  ]
}

Error Responses:
- 404: Job not found
- 401: Invalid Cloudflare credentials
- 502: Cloudflare API error
```

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🛠️ Configuration

### Backend Configuration

Edit `backend/.env`:

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_token
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
PORT=8000
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Frontend Configuration

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## 📊 Cloudflare API Limits

### Free Tier
- **10 minutes** of browser time per day
- **Max pages per crawl**: 100,000
- **Max job runtime**: 7 days
- **Results retention**: 14 days

### Billing
- Browser rendering time is billed per second
- Non-rendered crawls (render: false) use Workers pricing
- JSON format uses Workers AI (additional charges)

## 🐛 Troubleshooting

### CORS Errors

**Problem**: Frontend can't connect to backend

**Solution**:
1. Check `CORS_ORIGINS` in backend `.env` file
2. Ensure it includes your frontend URL (e.g., `http://localhost:3000`)
3. For development with Vite, also add `http://localhost:5173`
4. Restart backend service: `docker-compose restart backend`

**Example `.env` configuration**:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Cloudflare API Errors

The application provides detailed error messages for common Cloudflare API issues:

**Problem**: 401 Unauthorized

**Error Message**: "Invalid Cloudflare credentials"

**Solution**:
1. Verify API token has "Browser Rendering - Edit" permission
2. Check Account ID is correct (found in Cloudflare Dashboard)
3. Ensure token hasn't expired
4. Regenerate token if necessary

**Problem**: 429 Rate Limit Exceeded

**Error Message**: "Rate limit exceeded. Please try again later."

**Solution**:
1. You've exceeded the free tier limit (10 minutes/day)
2. Wait for daily reset (midnight UTC)
3. Monitor browser time usage in the UI
4. Consider upgrading to a paid plan for higher limits

**Problem**: 502 Bad Gateway

**Error Message**: "Cloudflare API error"

**Solution**:
1. Check Cloudflare service status: https://www.cloudflarestatus.com/
2. Verify your account has Browser Rendering enabled
3. Check backend logs: `docker-compose logs backend`
4. Retry the request after a few moments

### Docker Build Failures

**Problem**: Build fails with dependency errors

**Solution**:
```bash
# Clear Docker cache and rebuild
docker-compose build --no-cache

# Remove old images and containers
docker system prune -a

# Rebuild and start fresh
docker-compose up --build
```

**Problem**: Port already in use

**Solution**:
```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Stop the conflicting service or change ports in docker-compose.yml
```

### Container Won't Start

**Problem**: Backend container exits immediately

**Solution**:
1. Check logs for detailed error:
   ```bash
   docker-compose logs backend
   ```

2. Common issues:
   - Missing `.env` file: `cp backend/.env.example backend/.env`
   - Invalid credentials in `.env`
   - Port 8000 already in use

3. Verify environment variables:
   ```bash
   docker-compose config
   ```

**Problem**: Frontend shows "Network Error"

**Solution**:
1. Ensure backend is running: `curl http://localhost:8000/api/health`
2. Check frontend environment: `cat frontend/.env`
3. Verify `VITE_API_URL` points to correct backend URL
4. Check browser console for detailed error messages

### Development Issues

**Problem**: Changes not reflected after rebuild

**Solution**:
```bash
# Stop all containers
docker-compose down

# Remove volumes (this will clear any cached data)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

**Problem**: Hot reload not working in development

**Solution**:
- For backend: Ensure you're using `--reload` flag with uvicorn
- For frontend: Check that Vite dev server is running (not production build)
- Verify file permissions if using Docker on Linux

## 🔒 Security Notes

- **Never commit** `.env` files to version control
- **Rotate API tokens** regularly
- **Use environment variables** for all secrets
- **Run containers** as non-root users (already configured)
- **Keep dependencies** updated

## 📁 Project Structure

```
crawl-site/
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models.py            # Pydantic models for validation
│   │   ├── cloudflare_client.py # Cloudflare API client
│   │   ├── config.py            # Configuration management
│   │   ├── api/                 # API layer
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # API route handlers
│   │   │   └── exception_handlers.py # Centralized error handling
│   │   └── services/            # Business logic layer
│   │       ├── __init__.py
│   │       └── crawl_service.py # Crawl operations service
│   ├── tests/                   # Backend tests (to be implemented)
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Backend container definition
│   └── .env.example            # Environment variables template
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── CrawlForm.jsx        # URL/depth input form
│   │   │   ├── CrawlForm.css
│   │   │   ├── StatusIndicator.jsx  # Crawl progress display
│   │   │   ├── StatusIndicator.css
│   │   │   ├── MarkdownViewer.jsx   # Results viewer
│   │   │   ├── MarkdownViewer.css
│   │   │   ├── ErrorDisplay.jsx     # Error handling UI
│   │   │   └── ErrorDisplay.css
│   │   ├── services/
│   │   │   └── api.js          # Backend API client
│   │   ├── App.jsx             # Main application component
│   │   ├── App.css             # Global styles
│   │   └── main.jsx            # React entry point
│   ├── public/                 # Static assets
│   ├── index.html              # HTML template
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── Dockerfile              # Frontend container definition
│   ├── nginx.conf              # Nginx configuration
│   └── .env.example            # Environment variables template
├── docker-compose.yml          # Multi-container orchestration
├── .gitignore                  # Git ignore patterns
├── README.md                   # This file - user documentation
├── ARCHITECTURE.md             # Architecture documentation
└── AGENTS.md                   # Developer guidance for AI agents
```

## 🧪 Testing

### Manual Testing

1. **Health Check**:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Initiate Crawl**:
   ```bash
   curl -X POST http://localhost:8000/api/crawl \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "depth": 2}'
   ```

3. **Check Status**:
   ```bash
   curl http://localhost:8000/api/crawl/{job_id}
   ```

### Frontend Testing

1. Open http://localhost:3000
2. Enter a test URL (e.g., `https://example.com`)
3. Set depth to 1 or 2
4. Click "Start Crawl"
5. Verify status updates appear
6. Check results are displayed correctly

## 🚢 Deployment

### Production Considerations

1. **Environment Variables**:
   - Use secrets management (e.g., Docker secrets, Kubernetes secrets, AWS Secrets Manager)
   - Never expose API tokens in logs or error messages
   - Rotate credentials regularly
   - Use different credentials for different environments

2. **Architecture & Scaling**:
   - Deploy backend and frontend separately for better scalability
   - Use load balancer (e.g., Nginx, AWS ALB) for multiple backend instances
   - Consider Redis for distributed job queue management
   - Implement rate limiting at API gateway level
   - Use CDN for frontend static assets

3. **Monitoring & Observability**:
   - Add application monitoring (e.g., Prometheus, Grafana, Datadog)
   - Set up log aggregation (e.g., ELK stack, CloudWatch)
   - Configure alerts for errors and performance issues
   - Monitor Cloudflare API usage and costs
   - Track response times and error rates

4. **Security**:
   - Use HTTPS/TLS in production (Let's Encrypt, AWS Certificate Manager)
   - Implement authentication and authorization if needed
   - Add request validation and sanitization (already implemented)
   - Set up firewall rules and security groups
   - Enable CORS only for trusted origins
   - Use security headers (CSP, HSTS, X-Frame-Options)
   - Regular security audits and dependency updates

5. **Database & Persistence** (Future Enhancement):
   - Add database for job history and user management
   - Implement proper session management
   - Store crawl results for later retrieval
   - Add caching layer for frequently accessed data

6. **CI/CD Pipeline**:
   - Automated testing (unit, integration, e2e)
   - Automated builds and deployments
   - Environment-specific configurations
   - Blue-green or canary deployments

## 📚 Additional Resources

### Documentation
- [Cloudflare Browser Rendering API](https://developers.cloudflare.com/browser-rendering/) - Official API documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Backend framework
- [React Documentation](https://react.dev/) - Frontend framework
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation
- [Vite Documentation](https://vitejs.dev/) - Build tool
- [Docker Documentation](https://docs.docker.com/) - Containerization

### Project Documentation
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Detailed architecture and design decisions
- [`AGENTS.md`](AGENTS.md) - Developer guidance for AI agents
- [`backend/.env.example`](backend/.env.example) - Environment variables template

### Related Technologies
- [httpx](https://www.python-httpx.org/) - Async HTTP client for Python
- [Axios](https://axios-http.com/) - HTTP client for JavaScript
- [react-markdown](https://github.com/remarkjs/react-markdown) - Markdown rendering

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 💬 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [Cloudflare API Documentation](https://developers.cloudflare.com/browser-rendering/)
3. Open an issue in the repository

## 🎯 Roadmap

### Completed ✅
- [x] Layered backend architecture (API → Service → Client)
- [x] Centralized exception handling
- [x] Comprehensive error messages
- [x] Type-safe request/response validation
- [x] Interactive API documentation
- [x] Async HTTP operations
- [x] Docker containerization

### Planned Enhancements 🚀
- [ ] Unit and integration tests
- [ ] Authentication and user management
- [ ] Job history with database persistence
- [ ] WebSocket for real-time updates (replace polling)
- [ ] Custom crawl configurations (headers, cookies, etc.)
- [ ] Export results to various formats (PDF, JSON, CSV)
- [ ] Scheduled/recurring crawls
- [ ] Crawl comparison and diff tools
- [ ] Rate limiting and quota management
- [ ] Multi-tenant support
- [ ] Crawl analytics and reporting

---

Built with ❤️ using React, FastAPI, and Cloudflare Browser Rendering API
