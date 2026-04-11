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

      // Create the Market Research Agent
      const marketResearchAgent = new Agent({
        name: "Market Research Agent",
        instructions: `You are a Market Research Agent specialized in researching top-selling Ebooks.
Your capabilities:
1. Analyze market trends, competitor profiles, and pricing strategies.
2. Provide insights on top-selling genres, keywords, and reader preferences.
3. Use the provided business context and knowledge base to guide your research.
You can use tools to search the web or analyze data if available, or rely on your knowledge base to provide market research reports.`,
      });

      // Create the Advertising Agent
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

      // Create the Stripe Agent
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

      // Create the agent with the MCP server attached
      const agent = new Agent({
        name: "Ebook Building AI Agent Workforce",
        instructions: `You are the Ebook Building AI Agent Workforce. You have access to a local filesystem, GitHub via MCP tools, and an EPUB compiler.
Your capabilities:
1. Build complete Epub Ebooks with front cover, back cover, and complete chapters hyperlinked to a TOC using the compile_epub tool.
2. Implement export to local drive by providing the user with the download link returned by compile_epub.
3. Build a landing page for each book and host it on GitHub Pages. The landing page MUST link to https://brettapps.com.
4. Delegate to the Market Research Agent to research top-selling Ebooks.
5. Delegate to the Advertising Agent to advertise personal Ebooks for sale.
6. Delegate to the Stripe Agent to create 'Buy Now' buttons for the ebook landing pages.

When asked to build an ebook:
1. First, outline the book and write the chapters (you can do this in memory or save them locally).
2. Compile the EPUB using compile_epub. If you don't have a cover URL, omit the coverUrl parameter and provide a description so the tool can generate a unique cover image using Gemini.
3. Create a GitHub repository for the book's landing page.
4. Push an index.html file to the repository. The HTML MUST include a link to https://brettapps.com and a link to download the EPUB (using the path returned by compile_epub).
5. Enable GitHub Pages for the repository.
6. IMPORTANT: Whenever you generate, write, or update HTML code for a web page, ALWAYS include the complete HTML code in an \`\`\`html code block in your final response so the user can see a live preview of it in their UI.

When asked to create a GitHub repository and host a web page (or similar requests):
1. Create the repository using the GitHub MCP server.
2. Generate the HTML content for the web page.
3. Push the index.html file to the repository's main branch.
4. Enable GitHub Pages using the enable_github_pages tool.
5. Provide the live GitHub Pages URL to the user.
6. ALWAYS include the complete HTML code in an \`\`\`html code block in your final response for the live preview.`,
        mcpServers: [server, githubServer],
        tools: [enableGitHubPages, compileEpub],
        handoffs: [marketResearchAgent, advertisingAgent, stripeAgent]
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
