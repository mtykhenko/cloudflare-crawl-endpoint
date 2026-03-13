# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

**cloudflare-crawl-site** is a web application for crawling websites using Cloudflare's Browser Rendering API. It consists of a React frontend and Python FastAPI backend, both containerized with Docker for easy deployment.

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic
- **Configuration**: pydantic-settings
- **Server**: Uvicorn

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Markdown Rendering**: react-markdown
- **Styling**: CSS Modules

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx (for frontend)

## Project Structure

```
crawl-site/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── models.py          # Pydantic models for validation
│   │   ├── cloudflare_client.py # Cloudflare API integration
│   │   ├── config.py          # Configuration management
│   │   ├── api/               # API layer (routes and handlers)
│   │   │   ├── __init__.py
│   │   │   ├── routes.py      # API route definitions
│   │   │   └── exception_handlers.py # Custom exception handlers
│   │   └── services/          # Business logic layer
│   │       ├── __init__.py
│   │       └── crawl_service.py # Crawl operations service
│   ├── tests/                 # Backend tests (to be implemented)
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend container definition
│   └── .env.example          # Environment variables template
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── CrawlForm.jsx        # URL/depth input form
│   │   │   ├── CrawlForm.css        # Form styles
│   │   │   ├── StatusIndicator.jsx  # Crawl progress display
│   │   │   ├── StatusIndicator.css  # Status styles
│   │   │   ├── MarkdownViewer.jsx   # Results viewer
│   │   │   ├── MarkdownViewer.css   # Viewer styles
│   │   │   ├── ErrorDisplay.jsx     # Error handling UI
│   │   │   └── ErrorDisplay.css     # Error styles
│   │   ├── services/
│   │   │   └── api.js        # Backend API client
│   │   ├── App.jsx           # Main application component
│   │   ├── App.css           # Global styles
│   │   └── main.jsx          # React entry point
│   ├── public/               # Static assets
│   ├── index.html            # HTML template
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── Dockerfile            # Frontend container definition
│   ├── nginx.conf            # Nginx configuration
│   └── .env.example          # Environment variables template
├── .bob/                     # Bob AI configuration
├── docker-compose.yml        # Multi-container orchestration
├── .gitignore               # Git ignore patterns
├── README.md                # User documentation
├── ARCHITECTURE.md          # Architecture documentation
└── AGENTS.md               # This file

Total Files: 40+
```

## Key Components

### Backend Components

1. **main.py**: FastAPI application entry point
   - Configures CORS middleware
   - Registers API routes from [`routes.py`](backend/app/api/routes.py)
   - Registers exception handlers from [`exception_handlers.py`](backend/app/api/exception_handlers.py)
   - Sets up logging configuration

2. **api/routes.py**: API route definitions
   - `GET /api/health`: Health check endpoint
   - `POST /api/crawl`: Initiate crawl job (returns 202 Accepted)
   - `GET /api/crawl/{job_id}`: Get job status and results
   - Uses [`CrawlService`](backend/app/services/crawl_service.py) for business logic
   - Comprehensive error handling and logging

3. **api/exception_handlers.py**: Custom exception handlers
   - [`cloudflare_api_error_handler()`](backend/app/api/exception_handlers.py): Maps Cloudflare errors to HTTP status codes
   - [`validation_exception_handler()`](backend/app/api/exception_handlers.py): Handles request validation errors
   - [`global_exception_handler()`](backend/app/api/exception_handlers.py): Catches unhandled exceptions
   - Provides consistent error response format

4. **services/crawl_service.py**: Business logic layer
   - [`CrawlService`](backend/app/services/crawl_service.py) class manages crawl operations
   - [`initiate_crawl()`](backend/app/services/crawl_service.py): Initiates new crawl jobs
   - [`get_crawl_status()`](backend/app/services/crawl_service.py): Retrieves job status and results
   - Separates business logic from API layer

5. **cloudflare_client.py**: Async client for Cloudflare Browser Rendering API
   - Handles API authentication
   - Manages crawl initiation and status polling
   - Implements error handling and retry logic
   - Custom [`CloudflareAPIError`](backend/app/cloudflare_client.py) exception

6. **models.py**: Pydantic models for request/response validation
   - [`CrawlRequest`](backend/app/models.py): Input validation (URL, depth)
   - [`CrawlResponse`](backend/app/models.py): Crawl initiation response
   - [`JobStatusResponse`](backend/app/models.py): Status and results structure
   - [`CrawlResult`](backend/app/models.py): Individual page result
   - [`HealthResponse`](backend/app/models.py): Health check response
   - [`ErrorResponse`](backend/app/models.py): Error response format

7. **config.py**: Configuration management using pydantic-settings
   - Loads environment variables
   - Validates required credentials
   - Provides configuration properties

### Frontend Components

1. **CrawlForm.jsx**: User input form
   - URL validation
   - Depth selection (1-100)
   - Form submission handling

2. **StatusIndicator.jsx**: Real-time status display
   - Progress bar
   - Status badges
   - Browser time tracking

3. **MarkdownViewer.jsx**: Results display
   - Collapsible page sections
   - Markdown rendering
   - Copy to clipboard functionality

4. **ErrorDisplay.jsx**: Error handling UI
   - User-friendly error messages
   - Retry functionality
   - Error dismissal

5. **api.js**: Backend communication
   - Axios instance configuration
   - API method wrappers
   - Error transformation

## Development Guidelines

### Backend Development

1. **Adding New Endpoints**:
   - Define Pydantic models in [`models.py`](backend/app/models.py)
   - Add route handler in [`api/routes.py`](backend/app/api/routes.py)
   - Add business logic in [`services/`](backend/app/services/) if needed
   - Update API documentation with response models
   - Add appropriate error handling

2. **Adding Business Logic**:
   - Create service classes in [`services/`](backend/app/services/)
   - Keep services focused on single responsibility
   - Use dependency injection for clients
   - Add comprehensive logging
   - Handle exceptions appropriately

3. **Modifying Cloudflare Integration**:
   - Update [`cloudflare_client.py`](backend/app/cloudflare_client.py)
   - Maintain async/await pattern
   - Add comprehensive logging
   - Handle API errors gracefully with [`CloudflareAPIError`](backend/app/cloudflare_client.py)

4. **Adding Exception Handlers**:
   - Add handlers in [`api/exception_handlers.py`](backend/app/api/exception_handlers.py)
   - Register in [`main.py`](backend/app/main.py)
   - Map to appropriate HTTP status codes
   - Provide consistent error response format

5. **Configuration Changes**:
   - Update [`config.py`](backend/app/config.py) for new settings
   - Add to [`.env.example`](backend/.env.example)
   - Document in [`README.md`](README.md)

### Frontend Development

1. **Adding New Components**:
   - Create component in [`src/components/`](frontend/src/components/)
   - Create corresponding CSS file (e.g., `ComponentName.css`)
   - Import and use in [`App.jsx`](frontend/src/App.jsx)
   - Follow existing patterns (functional components with hooks)

2. **API Integration**:
   - Add methods to [`api.js`](frontend/src/services/api.js)
   - Use async/await pattern
   - Handle errors consistently
   - Transform errors to user-friendly messages
   - Update state management in components

3. **Styling**:
   - Use separate CSS files for each component
   - Follow existing color scheme and design patterns
   - Ensure responsive design
   - Test on mobile devices
   - Use CSS variables for consistency

### Docker Development

1. **Backend Container**:
   - Multi-stage build for optimization
   - Non-root user for security
   - Health check configured
   - Alpine base for small size

2. **Frontend Container**:
   - Build stage with Node
   - Serve stage with Nginx
   - Static asset optimization
   - Security headers configured

3. **Docker Compose**:
   - Service dependencies defined
   - Health checks configured
   - Network isolation
   - Volume mounts for development

## Common Tasks

### Running Locally

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with credentials
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Running with Docker

```bash
# Create .env file
cp backend/.env.example .env
# Edit .env with credentials

# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Testing

```bash
# Backend health check
curl http://localhost:8000/api/health

# Initiate crawl
curl -X POST http://localhost:8000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "depth": 2}'

# Check status
curl http://localhost:8000/api/crawl/{job_id}
```

## API Integration Details

### Cloudflare Browser Rendering API

- **Base URL**: `https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering`
- **Authentication**: Bearer token in Authorization header
- **Rate Limits**: 10 minutes browser time/day (free tier)
- **Max Pages**: 100,000 per crawl
- **Max Runtime**: 7 days per job

### Request Flow

1. User submits URL and depth via frontend
2. Frontend calls `POST /api/crawl`
3. Backend initiates Cloudflare crawl job
4. Backend returns job_id to frontend
5. Frontend polls `GET /api/crawl/{job_id}` every 3 seconds
6. Backend fetches status from Cloudflare
7. Results displayed when status is "completed"

## Security Considerations

1. **API Credentials**:
   - Never commit `.env` files
   - Use environment variables
   - Rotate tokens regularly

2. **CORS Configuration**:
   - Restrict to known origins
   - Update for production domains

3. **Input Validation**:
   - Pydantic models validate all inputs
   - URL scheme validation (http/https only)
   - Depth range validation (1-100)

4. **Container Security**:
   - Non-root users
   - Minimal base images (Alpine)
   - No secrets in images
   - Health checks configured

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Check `CORS_ORIGINS` in backend `.env`
   - Ensure frontend URL matches
   - Restart backend after changes

2. **Cloudflare API Errors**:
   - Verify API token permissions
   - Check account ID is correct
   - Monitor rate limits

3. **Docker Build Failures**:
   - Clear cache: `docker-compose build --no-cache`
   - Check Dockerfile syntax
   - Verify all files exist

4. **Container Networking**:
   - Ensure services on same network
   - Check port mappings
   - Verify health checks pass

## Future Enhancements

Potential improvements:
- Add authentication and user management
- Implement job history with database
- Add WebSocket for real-time updates
- Support custom crawl configurations
- Export results to multiple formats
- Scheduled crawls
- Crawl comparison tools
- Unit and integration tests
- CI/CD pipeline
- Monitoring and alerting

## Dependencies

### Backend Dependencies
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- httpx==0.26.0
- pydantic==2.5.3
- pydantic-settings==2.1.0
- python-dotenv==1.0.0

### Frontend Dependencies
- react@^18.2.0
- react-dom@^18.2.0
- axios@^1.6.5
- react-markdown@^9.0.1
- vite@^5.0.11
- @vitejs/plugin-react@^4.2.1

## Documentation

- **[`README.md`](README.md)**: User-facing documentation with setup instructions
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)**: Detailed architecture and design decisions
- **[`AGENTS.md`](AGENTS.md)**: This file - developer guidance for AI agents

## Notes for AI Agents

When working with this codebase:

1. **Maintain Consistency**: Follow existing patterns and conventions
2. **Update Documentation**: Keep all documentation files in sync
3. **Test Changes**: Verify both locally and in Docker
4. **Security First**: Never expose credentials or tokens
5. **Error Handling**: Add comprehensive error handling
6. **Logging**: Use appropriate log levels
7. **Type Safety**: Use Pydantic models and TypeScript where applicable
8. **Async Patterns**: Maintain async/await in backend
9. **Component Structure**: Keep components focused and reusable
10. **Docker Best Practices**: Multi-stage builds, non-root users, health checks

## Contact & Support

For questions or issues:
1. Check README.md troubleshooting section
2. Review Cloudflare API documentation
3. Check application logs
4. Verify environment configuration

---

Last Updated: 2026-03-13
Version: 1.1.0