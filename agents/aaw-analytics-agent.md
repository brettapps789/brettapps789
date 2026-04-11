# 📈 AAW Analytics Agent

**Repo Name:** `aaw-analytics-agent`  
**Role:** Performance Tracking

## Primary Capabilities

- Google Analytics/tracking script embedding
- KPI definition (Conversion/Bounce rates)
- Performance report generation

## Description

The Analytics Agent closes the feedback loop by instrumenting every deployed product with tracking. It embeds Google Analytics (GA4) and other tracking scripts, defines product-specific KPIs like conversion rate and bounce rate, and generates periodic performance reports that feed back into the Research and Market Analysis Agents for continuous improvement.

## Inputs

- Deployed site URL from Deployment Agent
- Google Analytics property ID
- KPI targets from Market Analysis Agent

## Outputs

- GA4 tracking script embed code
- KPI dashboard configuration
- Periodic performance reports (weekly/monthly)

## Integration Points

- Receives data from: **Deployment Agent**, **Testing Agent**, **CI/CD Agent**
- Feeds data back to: **Research Agent**, **Market Analysis Agent** (optimization loop)
