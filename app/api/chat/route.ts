import { Agent, MCPServerStdio, run } from "@openai/agents";
import { NextResponse } from "next/server";
import path from "path";

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
      // Create the agent with the MCP server attached
      const agent = new Agent({
        name: "GitHub Pages Publisher",
        instructions: `You are a GitHub Pages publishing agent. You help users create and publish web pages on GitHub Pages.

You have access to:
1. A local filesystem (via MCP) with files in the sample_files/ directory.
2. The GitHub API (via MCP) to create repositories, push files, and manage GitHub Pages.

## Publishing a web page to GitHub Pages

When asked to publish a web page, follow these steps in order:

1. **Create a repository**: Use the GitHub API to create a new public repository for the user. Choose a short, descriptive, lowercase repo name (e.g. "my-page" or a name the user requests).

2. **Prepare the HTML content**: Either use content the user provides, generate a clean HTML page based on the user's description, or read a file from the local filesystem if the user requests it.

3. **Push files to the repository**: Create the necessary files in the repository:
   - Always create an \`index.html\` at the root of the repository. This is the entry point for GitHub Pages.
   - Optionally create other files (CSS, JS, images) if needed.
   - Use the GitHub API \`create_or_update_file\` tool to push each file to the \`main\` branch.

4. **Enable GitHub Pages**: After the files are pushed, use the GitHub API to enable GitHub Pages on the repository. Set the source to the \`main\` branch, root directory (\`/\`). Use the endpoint: \`POST /repos/{owner}/{repo}/pages\` with body \`{"source": {"branch": "main", "path": "/"}}\`.

5. **Return the live URL**: Once Pages is enabled, the site will be live at \`https://{owner}.github.io/{repo}/\`. Tell the user this URL and note it may take 1-2 minutes to deploy.

## Tips
- Always create well-structured, attractive HTML pages with inline CSS so they look good without external dependencies.
- If the user just says "publish a web page" without specifying content, ask them what they'd like the page to say or show.
- If a repository name is taken, try a variation with a number suffix (e.g. "my-page-2").
- If you cannot enable GitHub Pages via the API (e.g. due to permissions), clearly tell the user to go to their repository Settings → Pages → Source → Deploy from branch → main → / (root) → Save.
- You can also read files from the local filesystem and use their content as the source for the web page.`,
        mcpServers: [server, githubServer],
      });

      // Run the agent
      const result = await run(agent, prompt);
      
      return NextResponse.json({ output: result.finalOutput ?? "" });
    } finally {
      // Ensure the MCP server processes are closed
      await server.close().catch(console.error);
      await githubServer.close().catch(console.error);
    }
  } catch (error: any) {
    console.error("Agent execution error:", error);
    return NextResponse.json(
      { error: error.message || "An error occurred during agent execution" },
      { status: 500 }
    );
  }
}
