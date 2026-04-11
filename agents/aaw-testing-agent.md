# 🧪 AAW Testing Agent

**Repo Name:** `aaw-testing-agent`  
**Role:** Quality Assurance

## Primary Capabilities

- Broken link & responsiveness audits
- Stripe payment flow simulation
- Accessibility (WCAG) checks

## Description

The Testing Agent is the final quality gate before any product goes live. It scans for broken links across all pages, validates responsive layouts on multiple viewport sizes, simulates end-to-end Stripe payment flows to confirm checkout works correctly, and audits pages against WCAG 2.1 accessibility standards.

## Inputs

- Deployed site URL from Deployment Agent
- Stripe test-mode credentials from Integration Agent
- WCAG compliance level target (A, AA, AAA)

## Outputs

- Broken link report
- Responsive layout audit (mobile/tablet/desktop)
- Stripe payment simulation results
- WCAG accessibility audit report

## Integration Points

- Receives data from: **Deployment Agent**, **Integration Agent**, **CI/CD Agent**
- Feeds data to: **Analytics Agent**, **CI/CD Agent** (on failure triggers)
