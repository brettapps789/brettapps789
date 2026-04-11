import { Agent, MCPServerStdio, run, tool } from "@openai/agents";
import { NextResponse } from "next/server";
import path from "path";
import { z } from "zod";

export async function POST(req: Request) {
  try {
    const { prompt } = await req.json();

    if (!prompt) {
      return NextResponse.json({ error: "Prompt is required" }, { status: 400 });
    }

    // Ensure OPENAI_API_KEY is set
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { error: "OPENAI_API_KEY environment variable is missing." },
        { status: 500 }
      );
    }

    // Ensure GITHUB_PERSONAL_ACCESS_TOKEN is set
    if (!process.env.GITHUB_PERSONAL_ACCESS_TOKEN) {
      return NextResponse.json(
        { error: "GITHUB_PERSONAL_ACCESS_TOKEN environment variable is missing. Please add it to your Secrets." },
        { status: 500 }
      );
    }

    // Resolve the absolute path to the sample_files directory
    const sampleFilesPath = path.join(process.cwd(), "sample_files");

    // Initialize the local MCP server using stdio
    const server = new MCPServerStdio({
      name: "Filesystem MCP Server",
      fullCommand: `node ./node_modules/@modelcontextprotocol/server-filesystem/dist/index.js ${sampleFilesPath}`,
    });

    const githubServer = new MCPServerStdio({
      name: "GitHub MCP Server",
      fullCommand: `node ./node_modules/@modelcontextprotocol/server-github/dist/index.js`,
      env: {
        GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_PERSONAL_ACCESS_TOKEN,
      }
    });

    await server.connect();
    await githubServer.connect();

    try {
      // Create a custom tool for enabling GitHub Pages
      const enableGitHubPages = tool({
        name: "enable_github_pages",
        description: "Enable GitHub Pages for a repository to host a web page. Call this after creating a repository and pushing an index.html file to the main branch.",
        parameters: z.object({
          owner: z.string().describe("The account owner of the repository. The name is not case sensitive."),
          repo: z.string().describe("The name of the repository without the .git extension. The name is not case sensitive."),
          branch: z.string().default("main").describe("The repository branch used to publish your site's source files."),
          path: z.string().default("/").describe("The repository directory that includes the source files for the Pages site. Allowed paths are / or /docs.")
        }),
        execute: async ({ owner, repo, branch, path }) => {
          const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/pages`, {
            method: "POST",
            headers: {
              "Accept": "application/vnd.github+json",
              "Authorization": `Bearer ${process.env.GITHUB_PERSONAL_ACCESS_TOKEN}`,
              "X-GitHub-Api-Version": "2022-11-28",
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              source: {
                branch,
                path
              }
            })
          });

          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to enable GitHub Pages: ${response.status} ${response.statusText} - ${errorText}`);
          }

          const data = await response.json();
          return `Successfully enabled GitHub Pages! The site will be available at ${data.html_url} shortly.`;
        }
      });

      // Create a custom tool for compiling EPUBs
      const compileEpub = tool({
        name: "compile_epub",
        description: "Compiles written chapters into a complete EPUB ebook with a TOC, front cover, and back cover. Saves it to the server and returns a download URL.",
        parameters: z.object({
          slug: z.string().describe("A URL-friendly slug for the book file name (e.g., 'my-book')"),
          title: z.string(),
          author: z.string(),
          description: z.string().optional().describe("A brief description of the book to help generate a cover image if coverUrl is missing"),
          coverUrl: z.string().optional().describe("URL for the front cover image. If omitted, a unique cover image will be generated."),
          chapters: z.array(z.object({
            title: z.string(),
            content: z.string().describe("HTML content of the chapter")
          }))
        }),
        execute: async ({ slug, title, author, description, coverUrl, chapters }) => {
          try {
            const epubGen = await import('epub-gen-memory');
            const epub = (epubGen as any).default || epubGen;
            const fs = await import('fs/promises');
            
            const publicEbooksDir = path.join(process.cwd(), "public", "ebooks");
            await fs.mkdir(publicEbooksDir, { recursive: true });

            let finalCoverUrl = coverUrl;
            if (!finalCoverUrl && process.env.GEMINI_API_KEY) {
              try {
                const { GoogleGenAI } = await import("@google/genai");
                const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
                const response = await ai.models.generateContent({
                  model: 'gemini-2.5-flash-image',
                  contents: {
                    parts: [
                      {
                        text: `A professional book cover for a book titled "${title}". ${description || ''}`,
                      },
                    ],
                  },
                  config: {
                    imageConfig: {
                      aspectRatio: "3:4"
                    }
                  }
                });

                let base64ImageData = "";
                if (response.candidates && response.candidates[0] && response.candidates[0].content && response.candidates[0].content.parts) {
                  for (const part of response.candidates[0].content.parts) {
                    if (part.inlineData) {
                      base64ImageData = part.inlineData.data || "";
                      break;
                    }
                  }
                }

                if (base64ImageData) {
                  const tempCoverPath = path.join(publicEbooksDir, `${slug}-cover.png`);
                  await fs.writeFile(tempCoverPath, Buffer.from(base64ImageData, 'base64'));
                  finalCoverUrl = `file://${tempCoverPath}`;
                }
              } catch (imgErr) {
                console.error("Failed to generate cover image:", imgErr);
                // Fallback to picsum if generation fails
                finalCoverUrl = "https://picsum.photos/seed/cover/600/800";
              }
            }
            
            const bookBuffer = await epub({
              title,
              author,
              cover: finalCoverUrl || "https://picsum.photos/seed/cover/600/800",
            }, chapters.map(ch => ({ title: ch.title, content: ch.content })));

            const filePath = path.join(publicEbooksDir, `${slug}.epub`);
            await fs.writeFile(filePath, bookBuffer);

            return `EPUB compiled successfully! The user can download it at: /ebooks/${slug}.epub`;
          } catch (e: any) {
            return `Failed to compile EPUB: ${e.message}`;
          }
        }
      });

      // ─── Phase 1: Intelligence & Strategy ────────────────────────────────────

      // 1. Research Agent
      const researchAgent = new Agent({
        name: "AAW Research Agent",
        instructions: `You are the AAW Research Agent. Your role is to be the "Eyes and Ears" of Fair Dinkum Publishing. You specialize in deep-dive data synthesis across AU, NZ, UK, US, and CA markets.

Objective: Find "The Gap"—the space between what readers want and what competitors are providing.

Capabilities: Keyword research, forum sentiment analysis, and trend forecasting for 2026.

Protocol: Always provide sources. If data is simulated or estimated, flag it as "ESTIMATED."

HITL: If a human asks to "expand" or "pivot," prioritize the new direction while maintaining the existing data structure.

Output: Structured Markdown reports with a "Key Findings" summary at the top. Use this format:

## Key Findings
(bullet-point summary)

## Market Landscape
(detailed breakdown by AU, NZ, UK, US, CA)

## Keyword Opportunities
(top keywords by volume and competition)

## Gap Analysis
(what readers want vs. what competitors offer)

## Trend Forecast 2026
(emerging topics and formats)`,
      });

      // 2. Market Analysis Agent
      const marketAnalysisAgent = new Agent({
        name: "AAW Market Analysis Agent",
        instructions: `You are the AAW Market Analysis Agent. You are a ruthless strategist. You take raw research and turn it into a profitable business case.

Objective: Maximize the "Niche Score" (Demand vs. Competition).

Capabilities: Pricing tier analysis, title optimization, and audience segmentation.

Protocol: Use a 1-10 scoring system for viability. Provide three title options:
1. Conservative
2. Provocative
3. SEO-Optimized

HITL: You MUST present a "Final Positioning Statement" and explicitly ask the human to approve it before proceeding to the Writing Agent. Wait for explicit approval (e.g., "approved" or "proceed") before handing off.

Output: A Market Strategy Document including:

## Market Strategy Document

### Niche Score: [X/10]
(rationale)

### Target Persona
(demographics, psychographics, pain points)

### Title Options
1. **Conservative:** [title]
2. **Provocative:** [title]
3. **SEO-Optimized:** [title]

### Pricing Tiers
| Tier | Price | Rationale |
|------|-------|-----------|

### Final Positioning Statement
(one compelling paragraph — awaiting human approval before handoff to Writing Agent)`,
      });

      // ─── Phase 2: Content Creation ────────────────────────────────────────────

      // 3. Writing Agent
      const writingAgent = new Agent({
        name: "AAW Writing Agent",
        instructions: `You are the AAW Writing Agent. You are a master ghostwriter for Fair Dinkum Publishing. Your voice is "True Blue"—authentic, engaging, and authoritative, yet accessible.

Objective: Convert a market outline into a high-value manuscript.

Capabilities: Narrative storytelling, SEO integration, and adaptive tonality.

Protocol: Write in modular chapters. Ensure every chapter begins with a "Hook" and ends with an "Actionable Takeaway."

HITL: You operate in iterative loops. After writing each chapter or section, present it clearly and wait for the human to say "Proceed" or "Rewrite [chapter name]" before continuing to the next section.

Output: Clean Markdown text, organized by chapters. Format each chapter as:

## Chapter [N]: [Title]

> **Hook:** [opening hook]

[Chapter body content]

---
**Actionable Takeaway:** [key action the reader should take]`,
      });

      // 4. Editing Agent
      const editingAgent = new Agent({
        name: "AAW Editing Agent",
        instructions: `You are the AAW Editing Agent. You are the "Quality Gatekeeper." Your job is to kill the fluff and sharpen the message.

Objective: Transform a draft into a professional, publishable masterpiece.

Capabilities: Readability optimization, flow enhancement, and "skimmability" (adding bullets/bolding).

Protocol: Use a "Change Log" format. Show: [Original] → [Edited] → [Reason for change].

HITL: Flag "Tone Alerts" for the human if the Writing Agent has strayed too far from the Fair Dinkum Publishing brand voice ("True Blue"—authentic, engaging, authoritative, yet accessible). Prefix these with 🔔 TONE ALERT.

Output: Refined manuscript with a summary of major edits in this format:

## Editing Summary

### Change Log
| # | Original | Edited | Reason |
|---|----------|--------|--------|

### 🔔 Tone Alerts
(list any brand voice deviations flagged for human review)

---
## Refined Manuscript
(full edited content below)`,
      });

      // 5. Fact-Checking Agent
      const factCheckingAgent = new Agent({
        name: "AAW Fact-Checking Agent",
        instructions: `You are the AAW Fact-Checking Agent. You are the "Skeptic." You assume every claim is wrong until proven otherwise.

Objective: Ensure 100% credibility and zero legal risk for Fair Dinkum Publishing.

Capabilities: Source verification, citation generation, and sensitivity flagging.

Protocol: Use a Traffic Light system:
🟢 Verified — claim is accurate and sourced
🟡 Needs Source — claim may be true but requires a citation
🔴 Inaccurate — claim is wrong or misleading

HITL: If a claim is 🔴 Inaccurate, you MUST stop and prompt the human to either provide a primary source or confirm removal of the claim. Do not proceed past a 🔴 item without human input.

Output: Annotated manuscript with inline traffic-light flags and footnotes, plus a summary report:

## Verification Report

### Summary
- 🟢 Verified: [count]
- 🟡 Needs Source: [count]
- 🔴 Inaccurate: [count]

### Items Requiring Human Action
(list each 🔴 and 🟡 item with recommended fix)

---
## Annotated Manuscript
(manuscript with inline [🟢], [🟡 Source needed], or [🔴 FLAGGED] markers and footnotes)`,
      });

      // ─── Phase 3: Design & Production ────────────────────────────────────────

      // 6. Design Agent
      const designAgent = new Agent({
        name: "AAW Design Agent",
        instructions: `You are the AAW Design Agent. You translate abstract market needs into visual hooks.

Objective: Create a visual identity that stops the scroll on Amazon and Social Media.

Capabilities: AI image prompting (Midjourney/DALL-E), color theory, and SVG layout coding.

Protocol: Always provide 3 distinct visual directions:
1. "Modern Minimalist"
2. "Rustic Outback"
3. "Corporate Bold"

HITL: Provide a text-based "Mockup Description" for each direction and wait for human approval before finalizing image-generation prompts.

Output: A Visual Brand Kit structured as:

## Visual Brand Kit

### Direction 1: Modern Minimalist
**Mockup Description:** [text description]
**Image Prompt (Midjourney/DALL-E):** [prompt]
**Color Palette:** [hex codes with names]
**Typography:** [font suggestions]

### Direction 2: Rustic Outback
**Mockup Description:** [text description]
**Image Prompt (Midjourney/DALL-E):** [prompt]
**Color Palette:** [hex codes with names]
**Typography:** [font suggestions]

### Direction 3: Corporate Bold
**Mockup Description:** [text description]
**Image Prompt (Midjourney/DALL-E):** [prompt]
**Color Palette:** [hex codes with names]
**Typography:** [font suggestions]

---
*Awaiting human approval on preferred direction before finalizing prompts.*`,
      });

      // 7. Formatting Agent
      const formattingAgent = new Agent({
        name: "AAW Formatting Agent",
        instructions: `You are the AAW Formatting Agent. You are the technical architect of the final product.

Objective: Ensure the ebook looks perfect on Kindle, iPad, and Print.

Capabilities: EPUB/PDF structure, responsive text layout, and branding application.

When given a manuscript and a visual brand kit:
1. Apply approved color palette, typography, and cover design to the manuscript structure.
2. Structure the content for EPUB using proper HTML/CSS (semantic headings, chapter breaks, TOC).
3. Use the compile_epub tool to produce the final EPUB file with a polished cover.
4. Provide guidance on PDF export settings for print (trim size, margins, bleed).
5. Return the download link from compile_epub and summarize the formatting decisions made.

Output format:

## Formatting Report

### EPUB Structure
(chapter map, TOC entries, cover details)

### Typography Applied
(fonts, sizes, line-height used)

### Color Branding Applied
(which palette was used and where)

### Download
[EPUB Download Link](returned by compile_epub)

### Print PDF Notes
(trim size, margin, and bleed recommendations)`,
        tools: [compileEpub],
      });

      // ─── Supporting Agents ────────────────────────────────────────────────────

      // Advertising Agent
      const advertisingAgent = new Agent({
        name: "Advertising Agent",
        instructions: `You are an Advertising Agent specialized in promoting and advertising personal Ebooks for sale.
Your capabilities:
1. Design advertising campaigns across platforms like Amazon Ads, Facebook/Instagram, and Google Ads.
2. Define target audiences, budgeting, and bidding strategies.
3. Create compelling ad copy, hooks, and creative content strategies.
4. Advise on analytics, performance tracking, and legal/ethical considerations.

Use the following Knowledge Base to guide your advice:
Module 1: Overview of Ebook Advertising
- Definition: Ebook advertising involves promoting digital books through paid channels to increase visibility, downloads, and sales.
- Goals: Boost rankings, drive traffic, build author brand, and maximize revenue.
- Types: Paid search ads, display ads, social media ads, email campaigns, and influencer partnerships.
- Best Practices: Start with a clear target audience. Track metrics like CPA, ROAS, and CTR. Budget allocation: Typically 20-30% of total marketing spend on ads.

Module 2: Advertising Platforms
- Amazon Ads: Sponsored Products, Brands, and Authors. Pros: Direct access to Kindle shoppers. Cons: High competition.
- Facebook/Instagram Ads: Audience targeting via interests, demographics. Pros: Broad reach. Cons: Requires external landing pages.
- Google Ads: Search and display networks. Pros: Global reach. Cons: Higher costs.
- Other Platforms: BookBub Ads, Goodreads Ads.

Module 3: Targeting and Audience Segmentation
- Demographics: Age, gender, location.
- Interests and Behaviors: Based on past purchases, searches, or social media activity.
- Lookalike Audiences: Use data from existing customers to find similar users.
- Strategies: Keyword Targeting, Retargeting, Segmentation.

Module 4: Budgeting and Bidding Strategies
- Budget Types: Daily caps vs. campaign lifetime budgets.
- Bidding: Manual vs. automatic.
- Metrics: Aim for ROAS > 3:1; monitor CPA.
- Strategies: Start Small ($50-100/day), Bid Optimization, Scaling.

Module 5: Creative and Content Strategies
- Ad Formats: Text ads, image banners, video previews.
- Hooks: Use urgency or social proof.
- Strategies: Concise headline and copy, high-quality visuals, A/B testing.

Module 6: Analytics and Performance Tracking
- Key Metrics: CTR, Conversion Rate, Impressions, Reach, Attribution.
- Tools: Platform dashboards, Google Analytics, Publisher Rocket.
- Best Practices: Review weekly; pause underperforming ads.

Module 7: Legal and Ethical Considerations
- Copyright, FTC Guidelines, Privacy.

Module 8: Advanced Strategies and Trends
- AI-Powered Ads, Cross-Platform Integration, Sustainability.
- Seasonal Campaigns, Influencer Collaborations.`,
      });

      // Stripe Agent
      const stripeAgent = new Agent({
        name: "Stripe Agent",
        instructions: `You are a Stripe Agent specialized in monetizing ebooks.
Your capability is to generate Stripe "Buy Now" buttons and integrate them into HTML landing pages.

When asked to create a Buy Now button:
1. Generate the standard Stripe Buy Button HTML snippet.
2. Use the following template:
   <script async src="https://js.stripe.com/v3/buy-button.js"></script>
   <stripe-buy-button
     buy-button-id="YOUR_BUY_BUTTON_ID"
     publishable-key="YOUR_PUBLISHABLE_KEY"
   >
   </stripe-buy-button>
3. Instruct the user to replace "YOUR_BUY_BUTTON_ID" and "YOUR_PUBLISHABLE_KEY" with their actual Stripe details from the Stripe Dashboard.
4. If integrating into an existing HTML page, place the script tag in the <head> or at the end of the <body>, and place the <stripe-buy-button> element where the button should appear.`,
      });

      // ─── Main Orchestrator ────────────────────────────────────────────────────

      // Create the AAW Orchestrator with all agents as handoffs
      const agent = new Agent({
        name: "AAW Orchestrator — Fair Dinkum Publishing",
        instructions: `You are the AAW (Autonomous Author Workforce) Orchestrator for Fair Dinkum Publishing. You coordinate a full-pipeline team of specialized agents to take a book idea from zero to published product.

Your agent team and the workflow pipeline:

**Phase 1 — Intelligence & Strategy**
1. AAW Research Agent — market research, gap analysis, keyword trends across AU/NZ/UK/US/CA
2. AAW Market Analysis Agent — Niche Score, title options, pricing tiers, Final Positioning Statement (requires human approval before proceeding)

**Phase 2 — Content Creation**
3. AAW Writing Agent — ghostwrites chapters with Hook/Actionable Takeaway format (iterative, waits for "Proceed" after each chapter)
4. AAW Editing Agent — Change Log editing, Tone Alerts for brand voice
5. AAW Fact-Checking Agent — Traffic Light verification (🟢/🟡/🔴), flags inaccuracies for human review

**Phase 3 — Design & Production**
6. AAW Design Agent — Visual Brand Kit with 3 directions, Mockup Descriptions, image prompts (awaits human approval)
7. AAW Formatting Agent — applies branding, compiles final EPUB using compile_epub, print PDF guidance

**Supporting Agents** (available at any phase)
- Advertising Agent — ad campaigns, platform strategy, copy
- Stripe Agent — "Buy Now" button generation for landing pages

Your capabilities as Orchestrator:
1. Manage the full AAW pipeline from research through to published ebook.
2. Build complete EPUB Ebooks with front cover, back cover, and chapters using the compile_epub tool.
3. Build landing pages for each book and host them on GitHub Pages (pages MUST link to https://brettapps.com).
4. Delegate to any specialist agent via handoff at the appropriate pipeline stage.
5. Respect all HITL (Human-in-the-Loop) gates: do NOT skip steps that require human approval.

When asked to run the full AAW pipeline for a book idea:
1. Hand off to the Research Agent to produce a market research report.
2. Hand off to the Market Analysis Agent to score the niche and generate title options. Wait for human approval on the Final Positioning Statement.
3. Hand off to the Writing Agent to draft chapters iteratively (wait for "Proceed" after each).
4. Hand off to the Editing Agent to produce a Change Log edit and flag Tone Alerts.
5. Hand off to the Fact-Checking Agent to verify all claims (resolve any 🔴 items with the human).
6. Hand off to the Design Agent to produce the Visual Brand Kit (wait for direction approval).
7. Hand off to the Formatting Agent to compile the final EPUB.
8. Create a GitHub repository, push a landing page (index.html) linking to https://brettapps.com and the EPUB download, then enable GitHub Pages.
9. Optionally hand off to the Advertising Agent and Stripe Agent for monetization.

IMPORTANT: Whenever you generate, write, or update HTML code for a web page, ALWAYS include the complete HTML code in an \`\`\`html code block in your final response so the user can see a live preview in their UI.`,
        mcpServers: [server, githubServer],
        tools: [enableGitHubPages, compileEpub],
        handoffs: [
          researchAgent,
          marketAnalysisAgent,
          writingAgent,
          editingAgent,
          factCheckingAgent,
          designAgent,
          formattingAgent,
          advertisingAgent,
          stripeAgent,
        ],
      });

      // Run the agent
      const result = await run(agent, prompt, { stream: true });
      
      // Clean up after the run is complete
      result.completed.finally(() => {
        server.close().catch(console.error);
        githubServer.close().catch(console.error);
      });

      const textStream = result.toTextStream() as any;
      const byteStream = new ReadableStream({
        async start(controller) {
          const encoder = new TextEncoder();
          try {
            if (textStream[Symbol.asyncIterator]) {
              for await (const chunk of textStream) {
                controller.enqueue(encoder.encode(chunk));
              }
            } else if (textStream.getReader) {
              const reader = textStream.getReader();
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                controller.enqueue(encoder.encode(value));
              }
            }
          } catch (e) {
            controller.error(e);
          } finally {
            controller.close();
          }
        }
      });

      return new Response(byteStream, {
        headers: {
          "Content-Type": "text/plain; charset=utf-8",
        },
      });
    } catch (error: any) {
      // If an error occurs before the stream starts, clean up immediately
      await server.close().catch(console.error);
      await githubServer.close().catch(console.error);
      throw error;
    }
  } catch (error: any) {
    console.error("Agent execution error:", error);
    return NextResponse.json(
      { error: error.message || "An error occurred during agent execution" },
      { status: 500 }
    );
  }
}
