# Monitoring Setup - Prometheus, Grafana & Loki

## Overview
This directory contains the complete observability stack for the X Automation App using:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation and querying
- **Promtail**: Log collection agent

## Structure
```
monitoring/
├── prometheus/
│   └── prometheus.yml          # Prometheus scrape configuration
├── grafana/
│   └── provisioning/
│       ├── datasources/        # Auto-provision datasources (Prometheus & Loki)
│       └── dashboards/         # Pre-configured dashboards
├── loki/
│   └── local-config.yaml       # Loki configuration
├── promtail/
│   └── promtail-config.yaml    # Log collection configuration
├── METRICS_REFERENCE.md        # Complete metrics documentation
└── README.md
```

## Quick Start

### 1. Start Monitoring Stack
```bash
# From project root
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Access Services
- **Prometheus UI**: http://localhost:9090
- **Grafana UI**: http://localhost:3001
  - Default credentials: `admin` / `admin`
- **Loki API**: http://localhost:3100
- **Backend Metrics**: http://localhost:8000/metrics

### 3. Verify Setup
**Metrics (Prometheus):**
1. Open Prometheus at http://localhost:9090/targets
2. Check that `autox-backend` target is UP
3. Test query: `autox_workflow_starts_total`

**Logs (Loki):**
1. Open Grafana → Explore
2. Select Loki datasource
3. Query: `{job="autox-backend"}`
4. Should see backend logs

## Grafana Dashboards

### Pre-configured Dashboards (Auto-loaded)
The following dashboards are automatically provisioned:
1. **AutoX Custom Metrics** - Business and workflow metrics
   - Workflow rates and durations
   - Agent performance
   - Publication metrics
   - Validation rates
   - Error tracking

### Import Additional Dashboards
1. Go to Grafana (http://localhost:3001)
2. Login (admin/admin)
3. Navigate to Dashboards → Import
4. Use these dashboard IDs:
   - **FastAPI Dashboard**: `16110` (FastAPI Observability)
   - **Node Exporter**: `1860` (if you add host metrics)
   - **Loki Dashboard**: `13639` (Loki & Promtail)

### Key Metrics to Monitor

**Standard HTTP Metrics:**
- **HTTP Request Rate**: `rate(http_requests_total[5m])`
- **Request Duration**: `http_request_duration_seconds`
- **Error Rate**: `rate(http_requests_total{status=~"5.."}[5m])`
- **Active Connections**: `http_requests_in_progress`

**Custom Workflow Metrics:**
- **Workflow Start Rate**: `rate(autox_workflow_starts_total[5m])`
- **Active Workflows**: `autox_active_workflows`
- **Agent Execution Time**: `histogram_quantile(0.95, sum(rate(autox_agent_execution_seconds_bucket[5m])) by (le, agent_name))`
- **Error Rate**: `sum(rate(autox_errors_total[5m])) by (component)`
- **Publication Success Rate**: `sum(rate(autox_publications_total{status="success"}[5m])) / sum(rate(autox_publications_total[5m]))`

**Log Queries (LogQL):**
- **All Logs**: `{job="autox-backend"}`
- **Error Logs**: `{job="autox-backend", level="ERROR"}`
- **Workflow Logs**: `{job="autox-backend"} |~ "WORKFLOW"`
- **Agent Logs**: `{job="autox-backend"} |~ "(writer|publicator|image_generator)"`

📖 **See [METRICS_REFERENCE.md](./METRICS_REFERENCE.md) for complete metrics documentation.**

## Configuration Notes

### Backend Metrics
The FastAPI app exposes metrics at `/metrics` endpoint using:
- `prometheus-fastapi-instrumentator` - Standard HTTP metrics
- `prometheus-client` - Custom business metrics

**Standard Metrics:**
- HTTP request counts by method, path, status
- Request duration histograms
- In-progress requests
- Application info

**Custom Metrics (40+ metrics):**
- Workflow lifecycle tracking
- Agent performance monitoring
- Authentication metrics
- Content generation metrics
- Human-in-the-loop validation metrics
- Error tracking by component
- WebSocket connection monitoring

### Prometheus Configuration
- Backend scraped every 5 seconds
- Target: `host.docker.internal:8000` (Docker Desktop)
- For Linux: Use `172.17.0.1:8000`
- For production: Use service name or static IP

### Loki Configuration
- Stores logs in filesystem (local development)
- Retention: Default (no limit in local config)
- API port: 3100
- For production: Configure remote storage and retention policies

### Promtail Configuration
- Collects logs from: `x_automation_app/backend/app/logs/*.log`
- Parses log format: `YYYY-MM-DD HH:MM:SS [LEVEL] message`
- Extracts labels: `level`, `thread_id`, `agent_name`
- Filters out HTTP request logs (already filtered in Python)

### Grafana Provisioning
- Datasources auto-configured: Prometheus & Loki
- Pre-loaded dashboard: AutoX Custom Metrics
- Dashboards can be added to `provisioning/dashboards/` directory
- Dashboard JSON format with UID for persistence

## Testing

### 1. Check Backend Metrics Endpoint
```bash
curl http://localhost:8000/metrics
```

Expected output:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/health",status="200"} 42
...
```

### 2. Query Prometheus
Go to http://localhost:9090/graph and run:
```promql
rate(http_requests_total[1m])
```

### 3. Create Grafana Dashboard
1. Go to Dashboards → New → New Dashboard
2. Add a panel with query:
   ```promql
   sum(rate(http_requests_total[5m])) by (method, path)
   ```
3. Save dashboard

## Troubleshooting

### Backend target is DOWN in Prometheus
- **Check**: Is backend running? `docker ps | grep autox-backend`
- **Fix**: Ensure backend is accessible at http://localhost:8000/health
- **Docker Desktop**: Use `host.docker.internal` instead of `localhost`
- **Linux**: Use `172.17.0.1` (Docker bridge IP) or host network mode

### No metrics showing in Grafana
- Verify Prometheus datasource is configured (Settings → Data Sources)
- Check Prometheus is scraping: http://localhost:9090/targets
- Refresh Grafana dashboard or adjust time range
- Generate traffic to backend to create metrics

### No logs in Loki
- **Check Promtail**: `docker logs autox-promtail`
- **Verify log files exist**: `ls -la x_automation_app/backend/app/logs/`
- **Test Loki**: `curl http://localhost:3100/ready`
- **Restart Promtail**: `docker restart autox-promtail`
- **Check log format**: Ensure logs match pattern in promtail-config.yaml

### Loki datasource error in Grafana
- Verify URL is `http://loki:3100` (not localhost)
- Check Loki container: `docker ps | grep loki`
- Test Loki API: `curl http://localhost:3100/loki/api/v1/labels`
- Ensure containers are on same network: `monitoring`

### Custom metrics not appearing
- **Check metrics endpoint**: `curl http://localhost:8000/metrics | grep autox_`
- **Verify instrumentation**: Check that workflow/agents are being executed
- **Wait for scrape**: Prometheus scrapes every 5 seconds
- **Check for errors**: `docker logs autox-prometheus`

### Permission errors
```bash
# Fix Grafana permissions
sudo chown -R 472:472 monitoring/grafana

# Fix Loki permissions
sudo chown -R 10001:10001 monitoring/loki
```

### Dashboard not loading
- Check dashboard JSON syntax
- Verify datasource UIDs match
- Re-import dashboard manually
- Check Grafana logs: `docker logs autox-grafana`

## Production Considerations

1. **Security**:
   - Change default Grafana credentials immediately
   - Restrict Prometheus/Grafana/Loki access (use reverse proxy with auth)
   - Enable authentication on `/metrics` endpoint
   - Use HTTPS for all services
   - Implement network policies to isolate monitoring stack

2. **Persistence & Backup**:
   - Volumes are configured for data persistence
   - Backup Grafana dashboards regularly (export as JSON)
   - Configure Prometheus retention (default: 15 days)
   - Set up Loki retention policies (default: unlimited)
   - Backup Prometheus data directory periodically

3. **Alerting**:
   - Configure Prometheus alerting rules (see METRICS_REFERENCE.md for examples)
   - Set up Grafana notifications (Slack, email, PagerDuty, etc.)
   - Create alerts for:
     - High error rates
     - Workflow failures
     - Slow agent performance
     - High memory/CPU usage
     - Log error spikes

4. **Scaling & Performance**:
   - For multi-instance backend, use Prometheus service discovery
   - Consider remote storage for Prometheus (Thanos, Cortex, Mimir)
   - Use Loki distributed mode for high log volumes
   - Configure log retention based on storage capacity
   - Monitor monitoring stack itself (meta-monitoring)

5. **Log Management**:
   - Configure log rotation in backend
   - Set Loki retention period based on compliance requirements
   - Use log compaction for older logs
   - Consider S3/GCS for long-term log storage

6. **Resource Limits**:
   - Set memory/CPU limits in docker-compose for production
   - Monitor Prometheus memory usage (can grow with cardinality)
   - Configure Loki ingestion limits
   - Set appropriate scrape intervals based on load

## Stopping Monitoring

```bash
# Stop services
docker-compose -f docker-compose.monitoring.yml down

# Stop and remove volumes (deletes all data)
docker-compose -f docker-compose.monitoring.yml down -v
```

## Next Steps

### Immediate
- [ ] Test the monitoring stack with real workflows
- [ ] Create custom dashboards for your specific use cases
- [ ] Set up alerts for critical metrics
- [ ] Configure log retention policies

### Short-term
- [ ] Add frontend metrics (Module 1.2)
- [ ] Configure Grafana notifications (Slack/email)
- [ ] Create SLO dashboards (Service Level Objectives)
- [ ] Document runbooks for common alerts

### Long-term
- [ ] Implement distributed tracing (Tempo/Jaeger)
- [ ] Set up remote storage for Prometheus
- [ ] Configure Loki for production scale
- [ ] Implement cost monitoring and optimization

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL Tutorial](https://grafana.com/docs/loki/latest/logql/)
- [Grafana Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [METRICS_REFERENCE.md](./METRICS_REFERENCE.md) - Complete metrics documentation


