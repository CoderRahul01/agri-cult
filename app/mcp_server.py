"""
MCP Server Entry Point for Agri-Cult.
This script allows the Agentic Agriculture RAG to be used as a Model Context Protocol (MCP) server.
"""

import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import Notification, Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from app.services.graph.workflow import app_graph
from app.core.config import settings, logger

# Initialize MCP Server
server = Server("agri-cult-service")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available agricultural tools."""
    return [
        types.Tool(
            name="query_agri_expert",
            description="Ask an expert advisor about citrus diseases or government agricultural schemes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The farmer's question or concern."},
                    "session_id": {"type": "string", "description": "Optional session ID for memory context."}
                },
                "required": ["question"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle agricultural tool calls."""
    if name == "query_agri_expert":
        if not arguments or "question" not in arguments:
            raise ValueError("Missing 'question' argument")
        
        question = arguments["question"]
        session_id = arguments.get("session_id", "mcp-default")
        
        try:
            logger.info(f"MCP Call: {question}")
            initial_state = {"question": question}
            config = {"configurable": {"thread_id": session_id}}
            
            # Invoke the graph
            final_state = await asyncio.to_thread(app_graph.invoke, initial_state, config=config)
            
            answer = final_state.get("answer", "No answer generated.")
            sources = final_state.get("sources", [])
            
            source_text = "\n\nSources:"
            for s in sources:
                source_text += f"\n- {s.get('document')} (Page {s.get('page')})"
            
            return [
                types.TextContent(
                    type="text",
                    text=f"{answer}{source_text}"
                )
            ]
        except Exception as e:
            logger.error(f"MCP Tool Error: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="agri-cult-service",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=Notification(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ImportError:
        print("Error: 'mcp' library not found. Please install it with 'pip install mcp'.")
