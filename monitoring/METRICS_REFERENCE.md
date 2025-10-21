# AutoX Metrics Reference

This document provides a comprehensive reference of all custom metrics exposed by the AutoX backend application.

## Metric Types

- **Counter**: Cumulative metric that only increases (e.g., total requests)
- **Gauge**: Metric that can go up or down (e.g., active connections)
- **Histogram**: Samples observations and counts them in configurable buckets (e.g., request duration)

## Workflow Metrics

### `autox_workflow_starts_total` (Counter)
Total number of workflows started.

**Labels:**
- `autonomous_mode`: "True" or "False"
- `output_destination`: "PUBLISH_X" or "GET_OUTPUTS"
- `content_type`: Type of content (e.g., "SINGLE_TWEET", "TWEET_THREAD", "Article")

**Example Query:**
```promql
# Total workflows started in last 5 minutes
rate(autox_workflow_starts_total[5m])

# Workflows by autonomous mode
sum(rate(autox_workflow_starts_total[5m])) by (autonomous_mode)
```

---

### `autox_workflow_completions_total` (Counter)
Total number of completed workflows.

**Labels:**
- `status`: "success", "error", or "cancelled"
- `autonomous_mode`: "True" or "False"

**Example Query:**
```promql
# Workflow success rate
sum(rate(autox_workflow_completions_total{status="success"}[5m])) / 
sum(rate(autox_workflow_completions_total[5m])) * 100
```

---

### `autox_workflow_duration_seconds` (Histogram)
Time spent executing entire workflow.

**Labels:**
- `autonomous_mode`: "True" or "False"
- `output_destination`: "PUBLISH_X" or "GET_OUTPUTS"

**Buckets:** 10s, 30s, 60s, 120s, 300s, 600s, 1200s, 1800s, 3600s

**Example Query:**
```promql
# 95th percentile workflow duration
histogram_quantile(0.95, sum(rate(autox_workflow_duration_seconds_bucket[5m])) by (le))

# Average workflow duration
rate(autox_workflow_duration_seconds_sum[5m]) / 
rate(autox_workflow_duration_seconds_count[5m])
```

---

### `autox_active_workflows` (Gauge)
Number of currently active workflow threads.

**Example Query:**
```promql
# Current active workflows
autox_active_workflows
```

---

## Agent Metrics

### `autox_agent_execution_seconds` (Histogram)
Time spent in each agent node.

**Labels:**
- `agent_name`: Name of the agent (e.g., "writer", "publicator", "image_generator")
- `status`: "success" or "error"

**Buckets:** 0.5s, 1s, 2s, 5s, 10s, 30s, 60s, 120s, 300s

**Example Query:**
```promql
# 95th percentile execution time by agent
histogram_quantile(0.95, sum(rate(autox_agent_execution_seconds_bucket[5m])) by (le, agent_name))

# Average execution time for writer agent
rate(autox_agent_execution_seconds_sum{agent_name="writer"}[5m]) / 
rate(autox_agent_execution_seconds_count{agent_name="writer"}[5m])
```

---

### `autox_agent_invocations_total` (Counter)
Total number of agent node invocations.

**Labels:**
- `agent_name`: Name of the agent
- `status`: "started", "success", or "error"

**Example Query:**
```promql
# Agent invocation rate
sum(rate(autox_agent_invocations_total{status="success"}[5m])) by (agent_name)

# Agent error rate
sum(rate(autox_agent_invocations_total{status="error"}[5m])) by (agent_name)
```

---

## Authentication Metrics

### `autox_login_attempts_total` (Counter)
Total number of login attempts.

**Labels:**
- `login_type`: "normal" or "demo"
- `status`: "success" or "failure"

**Example Query:**
```promql
# Login success rate
sum(rate(autox_login_attempts_total{status="success"}[5m])) / 
sum(rate(autox_login_attempts_total[5m])) * 100

# Failed login attempts
sum(rate(autox_login_attempts_total{status="failure"}[5m]))
```

---

### `autox_session_validations_total` (Counter)
Total number of session validation attempts.

**Labels:**
- `status`: "valid", "invalid", or "error"

**Example Query:**
```promql
# Invalid session rate
rate(autox_session_validations_total{status="invalid"}[5m])
```

---

## Content Generation Metrics

### `autox_topics_selected_total` (Counter)
Total number of topics selected.

**Labels:**
- `topic_type`: "trending", "custom", or "trending_auto"

**Example Query:**
```promql
# Topic selection rate by type
sum(rate(autox_topics_selected_total[5m])) by (topic_type)
```

---

### `autox_content_drafts_total` (Counter)
Total number of content drafts generated.

**Labels:**
- `content_type`: Type of content (e.g., "SINGLE_TWEET", "Article")
- `content_length`: "Short", "Medium", or "Long"

**Example Query:**
```promql
# Content draft generation rate
sum(rate(autox_content_drafts_total[5m])) by (content_type, content_length)
```

---

### `autox_images_generated_total` (Counter)
Total number of images generated.

**Labels:**
- `status`: "success" or "failure"

**Example Query:**
```promql
# Image generation success rate
sum(rate(autox_images_generated_total{status="success"}[5m])) / 
sum(rate(autox_images_generated_total[5m])) * 100
```

---

### `autox_publications_total` (Counter)
Total number of content publications.

**Labels:**
- `destination`: "X" or "draft"
- `status`: "success" or "failure"

**Example Query:**
```promql
# Publication rate by destination
sum(rate(autox_publications_total[5m])) by (destination, status)

# Publication success rate
sum(rate(autox_publications_total{status="success"}[5m])) / 
sum(rate(autox_publications_total[5m])) * 100
```

---

## Human-in-the-Loop Metrics

### `autox_validation_requests_total` (Counter)
Total number of human validation requests.

**Labels:**
- `validation_step`: "await_topic_selection", "await_content_validation", or "await_image_validation"

**Example Query:**
```promql
# Validation request rate by step
sum(rate(autox_validation_requests_total[5m])) by (validation_step)
```

---

### `autox_validation_responses_total` (Counter)
Total number of validation responses.

**Labels:**
- `validation_step`: "await_topic_selection", "await_content_validation", or "await_image_validation"
- `action`: "approve", "edit", or "reject"

**Example Query:**
```promql
# Validation response rate by action
sum(rate(autox_validation_responses_total[5m])) by (validation_step, action)

# Rejection rate
sum(rate(autox_validation_responses_total{action="reject"}[5m])) / 
sum(rate(autox_validation_responses_total[5m])) * 100
```

---

### `autox_validation_response_seconds` (Histogram)
Time between validation request and user response.

**Labels:**
- `validation_step`: Validation step name

**Buckets:** 5s, 10s, 30s, 60s, 300s, 600s, 1800s, 3600s

**Example Query:**
```promql
# 95th percentile validation response time
histogram_quantile(0.95, sum(rate(autox_validation_response_seconds_bucket[5m])) by (le, validation_step))
```

---

## Error Metrics

### `autox_errors_total` (Counter)
Total number of errors encountered.

**Labels:**
- `error_type`: Type of error (e.g., "ValueError", "HTTPException")
- `component`: Component where error occurred (e.g., "agent_writer", "workflow_start", "websocket")

**Example Query:**
```promql
# Error rate by component
sum(rate(autox_errors_total[5m])) by (component, error_type)

# Total error rate
sum(rate(autox_errors_total[5m]))
```

---

## WebSocket Metrics

### `autox_active_websockets` (Gauge)
Number of active WebSocket connections.

**Example Query:**
```promql
# Current active WebSocket connections
autox_active_websockets
```

---

### `autox_websocket_disconnections_total` (Counter)
Total number of WebSocket disconnections.

**Labels:**
- `reason`: "client", "error", or "timeout"

**Example Query:**
```promql
# WebSocket disconnection rate by reason
sum(rate(autox_websocket_disconnections_total[5m])) by (reason)
```

---

## Research Metrics (Defined but not yet instrumented)

### `autox_web_searches_total` (Counter)
Total number of web research queries executed.

**Labels:**
- `status`: "success" or "failure"

---

### `autox_tweet_searches_total` (Counter)
Total number of tweet searches performed.

**Labels:**
- `status`: "success" or "failure"

---

### `autox_research_loop_depth` (Gauge)
Current research loop iteration count.

---

## Alert Examples

### High Error Rate
```yaml
alert: HighErrorRate
expr: sum(rate(autox_errors_total[5m])) > 0.1
for: 5m
annotations:
  summary: "High error rate detected"
  description: "Error rate is {{ $value }} errors/sec"
```

### Workflow Failures
```yaml
alert: WorkflowFailures
expr: sum(rate(autox_workflow_completions_total{status="error"}[5m])) > 0
for: 2m
annotations:
  summary: "Workflows are failing"
  description: "{{ $value }} workflow failures per second"
```

### Slow Agent Performance
```yaml
alert: SlowAgentPerformance
expr: histogram_quantile(0.95, sum(rate(autox_agent_execution_seconds_bucket[5m])) by (le, agent_name)) > 120
for: 10m
labels:
  severity: warning
annotations:
  summary: "Agent {{ $labels.agent_name }} is slow"
  description: "95th percentile execution time is {{ $value }}s"
```

---

## Dashboard Recommendations

### Executive Dashboard
- Active workflows (gauge)
- Workflow completion rate (time series)
- Publication success rate (stat)
- Error rate (time series)
- Active users/sessions (gauge)

### Operations Dashboard
- Agent execution times (heatmap)
- Agent invocation rates (time series)
- Error breakdown by component (table)
- WebSocket connections (gauge)
- System resource usage (if available)

### Business Metrics Dashboard
- Content generation rate (time series)
- Publication destinations (pie chart)
- Topic selection trends (bar chart)
- Validation approval/rejection rates (stat)
- Average time to publication (stat)

---

## Additional Resources

- [Prometheus Query Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

