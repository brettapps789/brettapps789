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
        name: "Filesystem & GitHub assistant",
        instructions: "You are a helpful assistant. You have access to a local filesystem and GitHub via MCP tools. You can read local files, create GitHub repositories, push files to them, and help users host web pages on GitHub Pages. When asked to create a web page and host it, create the repository, push an index.html (and any other necessary files), and instruct the user on how to enable GitHub Pages in their repository settings if you cannot do it directly.",
        mcpServers: [server, githubServer],
      });

      // Run the agent
      const result = await run(agent, prompt);
      
      return NextResponse.json({ output: result.finalOutput });
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
