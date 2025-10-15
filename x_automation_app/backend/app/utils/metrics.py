"""
Custom Prometheus metrics for AutoX workflow monitoring.

This module defines business-specific metrics to track workflow performance,
agent execution, and user interactions beyond standard HTTP metrics.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time
from typing import Callable, Any


# ============================================================================
# WORKFLOW METRICS
# ============================================================================

# Counter: Total workflows started
WORKFLOW_STARTS_TOTAL = Counter(
    'autox_workflow_starts_total',
    'Total number of workflows started',
    ['autonomous_mode', 'output_destination', 'content_type']
)

# Counter: Workflow completions (success/failure)
WORKFLOW_COMPLETIONS_TOTAL = Counter(
    'autox_workflow_completions_total',
    'Total number of completed workflows',
    ['status', 'autonomous_mode']  # status: success, error, cancelled
)

# Histogram: Workflow execution time
WORKFLOW_DURATION_SECONDS = Histogram(
    'autox_workflow_duration_seconds',
    'Time spent executing entire workflow',
    ['autonomous_mode', 'output_destination'],
    buckets=(10, 30, 60, 120, 300, 600, 1200, 1800, 3600)  # 10s to 1h
)

# Gauge: Active workflows
ACTIVE_WORKFLOWS = Gauge(
    'autox_active_workflows',
    'Number of currently active workflow threads'
)


# ============================================================================
# AGENT METRICS
# ============================================================================

# Histogram: Agent execution time
AGENT_EXECUTION_TIME = Histogram(
    'autox_agent_execution_seconds',
    'Time spent in each agent node',
    ['agent_name', 'status'],  # status: success, error
    buckets=(0.5, 1, 2, 5, 10, 30, 60, 120, 300)  # 0.5s to 5min
)

# Counter: Agent invocations
AGENT_INVOCATIONS_TOTAL = Counter(
    'autox_agent_invocations_total',
    'Total number of agent node invocations',
    ['agent_name', 'status']
)


# ============================================================================
# AUTHENTICATION METRICS
# ============================================================================

# Counter: Login attempts
LOGIN_ATTEMPTS_TOTAL = Counter(
    'autox_login_attempts_total',
    'Total number of login attempts',
    ['login_type', 'status']  # login_type: normal, demo; status: success, failure
)

# Counter: Session validations
SESSION_VALIDATIONS_TOTAL = Counter(
    'autox_session_validations_total',
    'Total number of session validation attempts',
    ['status']  # status: valid, invalid, error
)


# ============================================================================
# CONTENT GENERATION METRICS
# ============================================================================

# Counter: Topics selected
TOPICS_SELECTED_TOTAL = Counter(
    'autox_topics_selected_total',
    'Total number of topics selected (trending or custom)',
    ['topic_type']  # topic_type: trending, custom
)

# Counter: Content drafts generated
CONTENT_DRAFTS_TOTAL = Counter(
    'autox_content_drafts_total',
    'Total number of content drafts generated',
    ['content_type', 'content_length']
)

# Counter: Images generated
IMAGES_GENERATED_TOTAL = Counter(
    'autox_images_generated_total',
    'Total number of images generated',
    ['status']  # status: success, failure
)

# Counter: Publications
PUBLICATIONS_TOTAL = Counter(
    'autox_publications_total',
    'Total number of content publications',
    ['destination', 'status']  # destination: X, draft; status: success, failure
)


# ============================================================================
# HUMAN-IN-THE-LOOP METRICS
# ============================================================================

# Counter: Validation requests
VALIDATION_REQUESTS_TOTAL = Counter(
    'autox_validation_requests_total',
    'Total number of human validation requests',
    ['validation_step']  # step: topic_selection, content_validation, image_validation
)

# Counter: Validation responses
VALIDATION_RESPONSES_TOTAL = Counter(
    'autox_validation_responses_total',
    'Total number of validation responses',
    ['validation_step', 'action']  # action: approve, edit, reject
)

# Histogram: Time to validation (how long user takes to respond)
VALIDATION_RESPONSE_TIME = Histogram(
    'autox_validation_response_seconds',
    'Time between validation request and user response',
    ['validation_step'],
    buckets=(5, 10, 30, 60, 300, 600, 1800, 3600)  # 5s to 1h
)


# ============================================================================
# RESEARCH METRICS
# ============================================================================

# Counter: Web searches performed
WEB_SEARCHES_TOTAL = Counter(
    'autox_web_searches_total',
    'Total number of web research queries executed',
    ['status']  # status: success, failure
)

# Counter: Tweet searches
TWEET_SEARCHES_TOTAL = Counter(
    'autox_tweet_searches_total',
    'Total number of tweet searches performed',
    ['status']
)

# Gauge: Research loop depth
RESEARCH_LOOP_DEPTH = Gauge(
    'autox_research_loop_depth',
    'Current research loop iteration count'
)


# ============================================================================
# ERROR METRICS
# ============================================================================

# Counter: Errors by type
ERRORS_TOTAL = Counter(
    'autox_errors_total',
    'Total number of errors encountered',
    ['error_type', 'component']  # component: agent, api, external
)


# ============================================================================
# WEBSOCKET METRICS
# ============================================================================

# Gauge: Active WebSocket connections
ACTIVE_WEBSOCKETS = Gauge(
    'autox_active_websockets',
    'Number of active WebSocket connections'
)

# Counter: WebSocket disconnections
WEBSOCKET_DISCONNECTIONS_TOTAL = Counter(
    'autox_websocket_disconnections_total',
    'Total number of WebSocket disconnections',
    ['reason']  # reason: client, error, timeout
)


# ============================================================================
# HELPER DECORATORS
# ============================================================================

def track_agent_execution(agent_name: str):
    """
    Decorator to automatically track agent execution time and status.
    
    Usage:
        @track_agent_execution("trend_harvester")
        def trend_harvester_node(state):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"
            
            try:
                AGENT_INVOCATIONS_TOTAL.labels(agent_name=agent_name, status="started").inc()
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                ERRORS_TOTAL.labels(error_type=type(e).__name__, component=f"agent_{agent_name}").inc()
                raise
            finally:
                duration = time.time() - start_time
                AGENT_EXECUTION_TIME.labels(agent_name=agent_name, status=status).observe(duration)
                AGENT_INVOCATIONS_TOTAL.labels(agent_name=agent_name, status=status).inc()
        
        return wrapper
    return decorator


def track_workflow_duration(autonomous_mode: bool, output_destination: str):
    """
    Context manager to track workflow duration.
    
    Usage:
        with track_workflow_duration(True, "PUBLISH_X"):
            # workflow execution
    """
    class WorkflowTimer:
        def __enter__(self):
            self.start_time = time.time()
            ACTIVE_WORKFLOWS.inc()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            WORKFLOW_DURATION_SECONDS.labels(
                autonomous_mode=str(autonomous_mode),
                output_destination=output_destination
            ).observe(duration)
            ACTIVE_WORKFLOWS.dec()
    
    return WorkflowTimer()

