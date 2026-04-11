# ⚙️ AAW CI/CD Agent

**Repo Name:** `aaw-cicd-agent`  
**Role:** Automation

## Primary Capabilities

- GitHub Actions workflow YAML creation
- Asset minification (CSS/JS)
- Automated build monitoring

## Description

The CI/CD Agent automates the build, test, and deploy lifecycle for every project. It generates GitHub Actions workflow YAML files that trigger on push/PR events, runs asset minification pipelines to optimize CSS and JS for production, and monitors build status — alerting when pipelines break or degrade.

## Inputs

- Project repository structure from Deployment Agent
- Build requirements (minification targets, test commands)
- Notification preferences (email, Slack, etc.)

## Outputs

- `.github/workflows/` YAML files
- Minified CSS/JS assets
- Build status reports and alerts

## Integration Points

- Receives data from: **Deployment Agent**
- Feeds data to: **Testing Agent**, **Analytics Agent**
