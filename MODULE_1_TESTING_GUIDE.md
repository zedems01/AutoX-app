# Module 1 - Testing Guide: Prometheus, Grafana & Loki Integration

## ✅ What Has Been Implemented

### Backend (1.1)
- ✅ Added Prometheus metrics to FastAPI (`main.py`)
- ✅ Exposed `/metrics` endpoint
- ✅ Library already installed: `prometheus-fastapi-instrumentator` & `prometheus-client`
- ✅ **NEW:** Custom workflow metrics for business logic tracking
- ✅ **NEW:** Agent execution metrics with timing and status
- ✅ **NEW:** Authentication, validation, and publication metrics

### Monitoring Stack (1.3)
- ✅ Created `docker-compose.monitoring.yml` for Prometheus, Grafana, Loki & Promtail
- ✅ Configured Prometheus scraping (`monitoring/prometheus/prometheus.yml`)
- ✅ Auto-provisioned Grafana datasources (Prometheus & Loki)
- ✅ **NEW:** Loki for centralized log aggregation
- ✅ **NEW:** Promtail for log collection from backend
- ✅ **NEW:** Pre-configured custom metrics dashboard
- ✅ Created comprehensive monitoring documentation

## 🚀 How to Test (1.4)

### Step 1: Start the Backend
```bash
# Navigate to project root
cd X_agent_team

# Start backend (if not already running)
docker-compose up -d backend

# Or run locally
cd x_automation_app/backend
uvicorn app.main:app --reload
```

### Step 2: Verify Metrics Endpoint
Open browser or use curl:
```bash
curl http://localhost:8000/metrics
```

**Expected Output:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/health",status="200"} 1
...
```

### Step 3: Start Monitoring Stack
```bash
# From project root
docker-compose -f docker-compose.monitoring.yml up -d
```

**Check containers:**
```bash
docker ps | grep autox
```

You should see:
- `autox-prometheus`
- `autox-grafana`
- `autox-loki`
- `autox-promtail`

### Step 4: Access Prometheus
1. Open: http://localhost:9090
2. Go to **Status → Targets**
3. Verify `autox-backend` is **UP** (may take 10-15 seconds)

**If target is DOWN:**
- Windows/Mac: Ensure backend uses `host.docker.internal:8000`
- Linux: Change to `172.17.0.1:8000` in `monitoring/prometheus/prometheus.yml`

### Step 5: Query Metrics in Prometheus
Go to **Graph** tab and try these queries:

1. **Total requests:**
   ```promql
   http_requests_total
   ```

2. **Request rate (last 5 minutes):**
   ```promql
   rate(http_requests_total[5m])
   ```

3. **Requests by path:**
   ```promql
   sum(rate(http_requests_total[1m])) by (handler)
   ```

### Step 6: Access Grafana
1. Open: http://localhost:3001
2. Login:
   - **Username:** `admin`
   - **Password:** `admin`
3. Skip password change (or change it)

### Step 7: Verify Datasources
1. Go to **Connections → Data Sources**
2. Click on **Prometheus**
3. Scroll down and click **Save & Test**
4. Should see: ✅ "Data source is working"
5. Go back and click on **Loki**
6. Click **Save & Test**
7. Should see: ✅ "Data source is working"

### Step 8: View Pre-configured Dashboards

#### AutoX Custom Metrics Dashboard (Auto-loaded)
The custom metrics dashboard is automatically provisioned! To view it:
1. Go to **Dashboards → Browse**
2. Look for **"AutoX Custom Metrics"**
3. Click to open

This dashboard includes:
- Workflow start rate and active workflows
- Agent execution times (95th percentile)
- Agent invocation rates
- Error rates by component
- Publication rates
- Validation request/response rates
- Active WebSocket connections

#### Option A: Import Additional Pre-built Dashboard
1. Go to **Dashboards → New → Import**
2. Enter dashboard ID: `16110` (FastAPI Observability)
3. Click **Load**
4. Select **Prometheus** as datasource
5. Click **Import**

#### Option B: Create Custom Dashboard
1. Go to **Dashboards → New → New Dashboard**
2. Click **Add visualization**
3. Select **Prometheus** datasource
4. Enter query:
   ```promql
   sum(rate(http_requests_total[5m])) by (handler, method)
   ```
5. Change visualization type to **Time series** or **Bar chart**
6. Click **Apply**
7. Save dashboard (name it "AutoX Backend Metrics")

### Step 9: Generate Traffic and Monitor
1. Make some requests to backend:
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Multiple requests
   for i in {1..20}; do curl http://localhost:8000/health; done
   ```

2. Refresh Grafana dashboard
3. You should see metrics update!

## 📊 Key Metrics to Monitor

### Standard HTTP Metrics (from prometheus-fastapi-instrumentator)
- `http_requests_total` - Total requests by method, path, status
- `http_request_duration_seconds` - Request latency
- `http_requests_in_progress` - Concurrent requests

### Custom Workflow Metrics
- `autox_workflow_starts_total` - Total workflows started (by mode, destination, content type)
- `autox_workflow_completions_total` - Completed workflows (by status, mode)
- `autox_workflow_duration_seconds` - Workflow execution time
- `autox_active_workflows` - Currently active workflows

### Agent Metrics
- `autox_agent_execution_seconds` - Time spent in each agent (histogram)
- `autox_agent_invocations_total` - Agent invocations (by name, status)

### Authentication Metrics
- `autox_login_attempts_total` - Login attempts (by type, status)
- `autox_session_validations_total` - Session validations (by status)

### Content Generation Metrics
- `autox_topics_selected_total` - Topics selected (by type)
- `autox_content_drafts_total` - Content drafts generated (by type, length)
- `autox_images_generated_total` - Images generated (by status)
- `autox_publications_total` - Publications (by destination, status)

### Human-in-the-Loop Metrics
- `autox_validation_requests_total` - Validation requests (by step)
- `autox_validation_responses_total` - Validation responses (by step, action)
- `autox_validation_response_seconds` - Time to validation response

### Error & WebSocket Metrics
- `autox_errors_total` - Errors encountered (by type, component)
- `autox_active_websockets` - Active WebSocket connections
- `autox_websocket_disconnections_total` - WebSocket disconnections (by reason)

### Sample Queries

**HTTP Error Rate:**
```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
```

**Average Response Time:**
```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

**Workflow Success Rate:**
```promql
sum(rate(autox_workflow_completions_total{status="success"}[5m])) / sum(rate(autox_workflow_completions_total[5m])) * 100
```

**Agent Performance (95th percentile):**
```promql
histogram_quantile(0.95, sum(rate(autox_agent_execution_seconds_bucket[5m])) by (le, agent_name))
```

**Error Rate by Component:**
```promql
sum(rate(autox_errors_total[5m])) by (component, error_type)
```

**Publication Success Rate:**
```promql
sum(rate(autox_publications_total{status="success"}[5m])) / sum(rate(autox_publications_total[5m])) * 100
```

## 📝 Working with Loki (Logs)

### Accessing Logs in Grafana
1. Go to **Explore** (compass icon in left sidebar)
2. Select **Loki** as datasource
3. Use LogQL queries to search logs

### Sample LogQL Queries

**All backend logs:**
```logql
{job="autox-backend"}
```

**Error logs only:**
```logql
{job="autox-backend", level="ERROR"}
```

**Logs for specific thread:**
```logql
{job="autox-backend"} |= "thread_id: YOUR_THREAD_ID"
```

**Logs containing "workflow":**
```logql
{job="autox-backend"} |~ "(?i)workflow"
```

**Agent-specific logs:**
```logql
{job="autox-backend"} |~ "(writer|publicator|image_generator)"
```

**Count errors in last hour:**
```logql
sum(count_over_time({job="autox-backend", level="ERROR"}[1h]))
```

### Creating a Logs Dashboard
1. Go to **Dashboards → New → New Dashboard**
2. Click **Add visualization**
3. Select **Loki** datasource
4. Enter LogQL query (e.g., `{job="autox-backend"}`)
5. Choose visualization:
   - **Logs** - For log stream view
   - **Time series** - For log counts over time
   - **Table** - For structured log view
6. Click **Apply** and **Save**

### Correlating Logs with Metrics
Create a dashboard with both:
1. **Metrics panel** (Prometheus): Show error rate
2. **Logs panel** (Loki): Show error logs
3. Use same time range to correlate issues

Example workflow:
- See spike in `autox_errors_total` metric
- Check Loki logs for that time period
- Filter by component/thread_id to debug

## 🎨 Creating Custom Dashboards

### Dashboard Best Practices
1. **Group related metrics** - Use rows to organize panels
2. **Use variables** - Add template variables for filtering (e.g., agent_name)
3. **Set appropriate refresh rates** - 5s for real-time, 1m for historical
4. **Add descriptions** - Use panel descriptions to explain metrics
5. **Use alerts** - Configure alert rules for critical metrics

### Example: Creating an Agent Performance Dashboard

#### Step 1: Create Dashboard
1. Go to **Dashboards → New → New Dashboard**
2. Click **Add visualization**

#### Step 2: Add Agent Execution Time Panel
1. Select **Prometheus** datasource
2. Query:
   ```promql
   histogram_quantile(0.95, sum(rate(autox_agent_execution_seconds_bucket[5m])) by (le, agent_name))
   ```
3. Legend: `{{agent_name}} (p95)`
4. Panel title: "Agent Execution Time (95th percentile)"
5. Unit: seconds
6. Visualization: Time series
7. Click **Apply**

#### Step 3: Add Agent Success Rate Panel
1. Click **Add → Visualization**
2. Query:
   ```promql
   sum(rate(autox_agent_invocations_total{status="success"}[5m])) by (agent_name) / 
   sum(rate(autox_agent_invocations_total[5m])) by (agent_name) * 100
   ```
3. Legend: `{{agent_name}}`
4. Panel title: "Agent Success Rate (%)"
5. Unit: percent (0-100)
6. Visualization: Stat or Gauge
7. Click **Apply**

#### Step 4: Add Agent Logs Panel
1. Click **Add → Visualization**
2. Select **Loki** datasource
3. Query:
   ```logql
   {job="autox-backend"} |~ "(writer|publicator|image_generator|quality_assurer)"
   ```
4. Panel title: "Agent Logs"
5. Visualization: Logs
6. Click **Apply**

#### Step 5: Add Variables (Optional)
1. Click **Dashboard settings** (gear icon)
2. Go to **Variables → Add variable**
3. Name: `agent_name`
4. Type: Query
5. Datasource: Prometheus
6. Query: `label_values(autox_agent_invocations_total, agent_name)`
7. Save variable
8. Update panel queries to use `$agent_name` filter

#### Step 6: Save Dashboard
1. Click **Save dashboard** (disk icon)
2. Name: "AutoX Agent Performance"
3. Add tags: `autox`, `agents`, `performance`
4. Click **Save**

### Example: Creating a Workflow Monitoring Dashboard

**Panels to include:**
1. **Workflow Start Rate** (Time series)
   ```promql
   sum(rate(autox_workflow_starts_total[5m])) by (autonomous_mode, content_type)
   ```

2. **Active Workflows** (Gauge)
   ```promql
   autox_active_workflows
   ```

3. **Workflow Success Rate** (Stat)
   ```promql
   sum(rate(autox_workflow_completions_total{status="success"}[5m])) / 
   sum(rate(autox_workflow_completions_total[5m])) * 100
   ```

4. **Workflow Duration** (Heatmap)
   ```promql
   sum(rate(autox_workflow_duration_seconds_bucket[5m])) by (le)
   ```

5. **Workflow Logs** (Logs panel with Loki)
   ```logql
   {job="autox-backend"} |~ "WORKFLOW"
   ```

### Exporting/Importing Dashboards
**Export:**
1. Open dashboard
2. Click **Share** (share icon)
3. Go to **Export** tab
4. Click **Save to file**

**Import:**
1. Go to **Dashboards → New → Import**
2. Upload JSON file or paste JSON
3. Select datasources
4. Click **Import**

## 🐛 Troubleshooting

### Backend target DOWN in Prometheus
**Problem:** Prometheus can't scrape backend

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check Docker network:
   ```bash
   docker network ls
   docker network inspect bridge
   ```
3. On **Windows/Mac**: Use `host.docker.internal:8000`
4. On **Linux**: Use `172.17.0.1:8000` or add to same network

### No data in Grafana
1. Check time range (top right) - set to "Last 5 minutes"
2. Verify Prometheus is scraping: http://localhost:9090/targets
3. Test query in Prometheus first
4. Refresh dashboard

### No logs in Loki
**Problem:** Loki shows no logs or "No data"

**Solutions:**
1. Check Promtail is running: `docker logs autox-promtail`
2. Verify log files exist: `ls -la x_automation_app/backend/app/logs/`
3. Check Promtail config: `monitoring/promtail/promtail-config.yaml`
4. Ensure backend is generating logs (make some API calls)
5. Check Loki is reachable: `curl http://localhost:3100/ready`
6. Restart Promtail: `docker restart autox-promtail`

### Loki connection error in Grafana
1. Verify Loki datasource URL: `http://loki:3100`
2. Check Loki container is running: `docker ps | grep loki`
3. Test Loki API: `curl http://localhost:3100/loki/api/v1/labels`

### Port conflicts
- Prometheus: 9090 (change in docker-compose if needed)
- Grafana: 3001 (to avoid conflict with Next.js on 3000)
- Loki: 3100
- Promtail: 9080

## ✅ Testing Checklist

### Basic Setup
- [ ] Backend `/metrics` endpoint accessible
- [ ] Prometheus container running
- [ ] Grafana container running
- [ ] Loki container running
- [ ] Promtail container running
- [ ] Prometheus targets show backend as UP
- [ ] Can query metrics in Prometheus UI
- [ ] Grafana Prometheus datasource connected
- [ ] Grafana Loki datasource connected

### Metrics Testing
- [ ] Can see standard HTTP metrics (`http_requests_total`)
- [ ] Can see custom workflow metrics (`autox_workflow_starts_total`)
- [ ] Can see agent metrics (`autox_agent_execution_seconds`)
- [ ] AutoX Custom Metrics dashboard loads
- [ ] Generated traffic and saw metrics update

### Logs Testing
- [ ] Can query logs in Grafana Explore with Loki
- [ ] Logs show correct timestamps and levels
- [ ] Can filter logs by level (ERROR, INFO, etc.)
- [ ] Can search logs by thread_id
- [ ] Promtail is collecting logs from backend

### Dashboard Testing
- [ ] Created at least one custom dashboard
- [ ] Dashboard shows both metrics and logs
- [ ] Can export/import dashboards
- [ ] Dashboard auto-refreshes

## 🔄 Next Steps

Once Module 1 is validated:
1. **Optional:** Add frontend metrics (Module 1.2 - we skipped this initially)
2. Move to **Module 2:** Set up Jenkins
3. Test monitoring with current Railway deployment
4. Commit changes to Git

## 📝 Production Notes

Before deploying to production:
- Change Grafana admin password
- Restrict access to Prometheus/Grafana (use reverse proxy)
- Configure alerting rules
- Set up data retention policies
- Consider authenticated `/metrics` endpoint

## 🛑 Stopping Monitoring

```bash
# Stop monitoring stack
docker-compose -f docker-compose.monitoring.yml down

# Stop and remove all data
docker-compose -f docker-compose.monitoring.yml down -v
```

## 📚 Resources

- [Prometheus Query Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/)
- [FastAPI Instrumentator Docs](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- Pre-built Grafana Dashboards: https://grafana.com/grafana/dashboards/

---

**Need Help?** Check `monitoring/README.md` for detailed documentation.

