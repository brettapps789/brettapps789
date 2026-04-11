# ✅ AAW Fact-Checking Agent

**Repo Name:** `aaw-fact-checking-agent`  
**Role:** Accuracy & Trust

## Primary Capabilities

- Claim verification & cross-referencing
- Adding citations and legal disclaimers
- Flagging inaccuracies for human review

## Description

The Fact-Checking Agent ensures all published content meets accuracy and compliance standards. It cross-references claims against authoritative sources, inserts proper citations, appends legal disclaimers where required, and flags anything that needs human review before publication.

## Inputs

- Edited manuscript from Editing Agent
- Domain-specific source libraries
- Legal/compliance requirements

## Outputs

- Verified manuscript with inline citations
- List of flagged claims requiring human review
- Legal disclaimer text

## Integration Points

- Receives data from: **Editing Agent**
- Feeds data to: **Formatting Agent**, **SEO Agent**
