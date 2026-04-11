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

    // Resolve the absolute path to the sample_files directory
    const sampleFilesPath = path.join(process.cwd(), "sample_files");

    // Initialize the local MCP server using stdio
    const server = new MCPServerStdio({
      name: "Filesystem MCP Server",
      fullCommand: `npx -y @modelcontextprotocol/server-filesystem ${sampleFilesPath}`,
    });

    await server.connect();

    try {
      // Create the agent with the MCP server attached
      const agent = new Agent({
        name: "Filesystem assistant",
        instructions: "You are a helpful assistant. Read files with the MCP tools before answering questions about the project or tasks. You have access to a local filesystem containing project information.",
        mcpServers: [server],
      });

      // Run the agent
      const result = await run(agent, prompt);
      
      return NextResponse.json({ output: result.finalOutput });
    } finally {
      // Ensure the MCP server process is closed
      await server.close();
    }
  } catch (error: any) {
    console.error("Agent execution error:", error);
    return NextResponse.json(
      { error: error.message || "An error occurred during agent execution" },
      { status: 500 }
    );
  }
}
