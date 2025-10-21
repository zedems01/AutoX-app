# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AutoX Content Creator** is an autonomous AI agent team system for real-time, trend-driven content creation. The system uses LangGraph for agent orchestration, FastAPI for the backend, and Next.js for the frontend. It analyzes trending topics on X (Twitter), performs research, generates content, and can publish directly to X.

## Development Commands

### Backend Development
```bash
cd x_automation_app/backend
uv sync                    # Install dependencies
cp env.template .env      # Configure environment variables
source .venv/bin/activate # Activate virtual environment (Windows: .venv\Scripts\activate)
uvicorn app.main:app --reload  # Start development server (http://localhost:8000)
```

### Frontend Development
```bash
cd x_automation_app/frontend
npm install               # Install dependencies
npm run dev              # Start development server (http://localhost:3000)
```

### Testing

#### Backend Tests
```bash
cd x_automation_app/backend
./run_tests.sh           # Run all tests
./run_tests.sh coverage  # Run with coverage report
./run_tests.sh api       # Run API tests only
./run_tests.sh integration # Run integration tests
./run_tests.sh fast      # Run fast tests (skip integration)
pytest --cov=app --cov-report=html  # Alternative coverage command
```

#### Frontend Tests
```bash
cd x_automation_app/frontend
npm test                # Run Jest tests
npm run test:coverage   # Run with coverage
```

### Docker Development
```bash
# Start full stack
docker compose up --build -d

# Start with monitoring
docker-compose up --build -d
docker-compose -f docker-compose.monitoring.yml up -d  # Monitoring stack

# Access services:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

### Monitoring & Observability
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Check metrics endpoint
curl http://localhost:8000/metrics

# View logs
docker logs autox-backend
docker logs autox-prometheus
docker logs autox-grafana
```

## Architecture & Key Components

### Backend Architecture
- **FastAPI**: REST API with WebSocket support for real-time updates
- **LangGraph**: Agent orchestration and stateful workflow management
- **Pydantic**: Data validation and serialization
- **Prometheus Metrics**: 40+ custom business and operational metrics
- **Structured Logging**: Thread-correlated logs for debugging

### Frontend Architecture
- **Next.js 15** (App Router): React framework with TypeScript
- **Shadcn/UI + Tailwind CSS**: Modern component library
- **React Context**: Global state management (auth, workflow)
- **TanStack Query**: Server state management and caching
- **React Hook Form + Zod**: Form validation

### Agent Workflow System
The core system uses LangGraph to orchestrate specialized agents:

1. **Trend Harvester**: Identifies trending topics on X
2. **Tweet Searcher**: Gathers relevant tweets for sentiment analysis
3. **Opinion Analyzer**: Analyzes public opinion and sentiment
4. **Writer**: Creates content drafts (tweets, threads, articles)
5. **Quality Assurer**: Reviews and refines content, generates image prompts
6. **Image Generator**: Creates AI-generated images
7. **Publicator**: Publishes content to X
8. **Deep Research Sub-Graph**: Performs web research for comprehensive information
9. **Human Validation Nodes**: Pause workflow for user approval/review

### State Management
- **LangGraph State**: Centralized state management across agents
- **OverallState**: Comprehensive state tracking workflow progress, user data, and outputs
- **Human-in-the-Loop**: Configurable validation checkpoints for user oversight

## Important Patterns & Conventions

### Backend Patterns
- **Environment Configuration**: Use `settings` module for environment variables
- **Error Handling**: Structured logging with thread ID correlation
- **Metrics Integration**: All major operations track timing, success/failure rates
- **WebSocket Streaming**: Real-time workflow updates to frontend
- **Async/Await**: All I/O operations are asynchronous
- **Dependency Injection**: Environment-based configuration throughout

### Frontend Patterns
- **Type Safety**: Comprehensive TypeScript definitions for all API responses
- **Component Composition**: Prefer composition over inheritance
- **Server State**: Use TanStack Query for API calls with caching
- **Client State**: Use React Context for global state (auth, workflow)
- **Form Validation**: React Hook Form + Zod for type-safe form handling

### API Design
- **RESTful Endpoints**: Standard HTTP methods with appropriate status codes
- **WebSocket Streaming**: Real-time workflow progress updates
- **Structured Responses**: Consistent JSON response format with Pydantic models
- **Error Handling**: Comprehensive error responses with appropriate HTTP status codes

## Key Files & Locations

### Backend Core Files
- `x_automation_app/backend/app/main.py`: FastAPI application entrypoint
- `x_automation_app/backend/app/agents/`: LangGraph workflow definitions and agent logic
- `x_automation_app/backend/app/utils/`: Utilities, schemas, logging configuration
- `x_automation_app/backend/app/settings.py`: Environment configuration
- `x_automation_app/backend/app/logs/`: Application logs (for Promtail/Loki)

### Frontend Core Files
- `x_automation_app/frontend/src/app/`: Next.js pages and API routes
- `x_automation_app/frontend/src/components/`: Reusable UI components
- `x_automation_app/frontend/src/contexts/`: React Context providers
- `x_automation_app/frontend/src/lib/`: API client and utilities

### Monitoring & Configuration
- `monitoring/`: Complete observability stack configuration
- `docker-compose.monitoring.yml`: Prometheus, Grafana, Loki, Promtail
- `monitoring/METRICS_REFERENCE.md`: Comprehensive metrics documentation
- `x_automation_app/backend/run_tests.sh`: Test runner with multiple options

## Environment Configuration

### Required Environment Variables (.env)
```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key

# X/Twitter Integration
X_API_KEY=your_x_api_key
USER_PROXY=your_proxy_config

# AWS (for image uploads)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-east-1

# Optional
LANGSMITH_API_KEY=your_langsmith_key  # For tracing
```

## Testing Approach

### Backend Testing Strategy
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: API endpoint and workflow testing
- **Mocking**: External dependencies (X API, LLM providers) are mocked
- **Coverage**: Aim for >80% code coverage
- **Test Categories**: Use markers to differentiate test types (integration, fast, etc.)

### Frontend Testing Strategy
- **Component Tests**: React Testing Library for component behavior
- **Integration Tests**: API client and user flow testing
- **Type Checking**: TypeScript for compile-time validation

## Monitoring & Observability

### Metrics Available
- **Workflow Metrics**: Start/completion rates, duration, active workflows
- **Agent Metrics**: Execution time, invocation counts, success rates
- **Authentication Metrics**: Login attempts, session validations
- **Content Metrics**: Generation rates, publication success, validation responses
- **Error Metrics**: Error rates by component and type
- **WebSocket Metrics**: Connection counts, disconnection reasons

### Log Management
- **Structured Logging**: JSON format with timestamps, levels, thread IDs
- **Log Aggregation**: Loki + Promtail for centralized log management
- **Log Correlation**: Thread IDs for tracing workflow execution

### Key Queries
- **Workflow Success Rate**: `sum(rate(autox_workflow_completions_total{status="success"}[5m])) / sum(rate(autox_workflow_completions_total[5m])) * 100`
- **Agent Performance**: `histogram_quantile(0.95, sum(rate(autox_agent_execution_seconds_bucket[5m])) by (le, agent_name))`
- **Error Rate**: `sum(rate(autox_errors_total[5m])) by (component)`

## Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Use strict mode, prefer explicit typing
- **Components**: Keep components small and focused
- **Error Handling**: Never swallow exceptions, always log with context

### Git Workflow
- **Branch Naming**: Use descriptive names (feature/auth, fix/validation)
- **Commit Messages**: Conventional commits format
- **Testing**: Ensure all tests pass before committing
- **Documentation**: Update relevant docs for API changes

### Performance Considerations
- **Async Operations**: Use async/await for all I/O
- **Database Queries**: Optimize queries, use connection pooling
- **Frontend**: Implement proper loading states and error boundaries
- **Monitoring**: Monitor key metrics and set up alerts

## Troubleshooting

### Common Issues
- **Backend won't start**: Check environment variables and dependencies
- **WebSocket connection issues**: Verify CORS configuration
- **Agent workflow stalls**: Check logs for agent errors or validation timeouts
- **Monitoring data missing**: Ensure Prometheus can scrape backend metrics

### Debugging Tips
- **Backend Logs**: Check `app/logs/` directory or use Grafana/Loki
- **Workflow Issues**: Use thread ID correlation in logs
- **Frontend Issues**: Check browser console and network tab
- **API Issues**: Use backend metrics endpoint to verify functionality

## Deployment

### Development
- Use Docker Compose for local development
- Enable hot reload for both frontend and backend
- Use monitoring stack for observability

### Production Considerations
- Configure proper environment variables
- Set up reverse proxy (nginx) for SSL termination
- Configure database backup and retention
- Set up monitoring alerts and notifications
- Use proper secret management (AWS Secrets Manager, etc.)