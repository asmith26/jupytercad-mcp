"""An example of how to use the JupyterCAD MCP server with the openai-agents library."""

import asyncio
from pathlib import Path

from agents import Agent, Runner, run_demo_loop, trace
from agents.mcp import MCPServer, MCPServerStdio, MCPServerStreamableHttp
from agents.model_settings import ModelSettings

# CONFIG
TRANSPORT = "stdio"
# MODEL = # see https://openai.github.io/openai-agents-python/models/
USE_REPL = False
USE_MLFLOW_TRACING = False
JCAD_PATH = Path(__file__).parent / "my_cad_design.jcad"


def get_mcp_server() -> MCPServer:
    if TRANSPORT == "stdio":
        return MCPServerStdio(
            name="jupytercad-mcp-stdio",
            params={
                "command": "uv",
                "args": ["run", "python", "../src/jupytercad_mcp/server.py"],
                #     "command": "uvx", todo
                #     "args": ["--with", "jupytercad-mcp", "jupytercad-mcp"],
            },
            cache_tools_list=True,
        )
    elif TRANSPORT == "streambable-http":
        return MCPServerStreamableHttp(
            name="jupytercad-mcp-streamable-http",
            params={
                "url": "http://localhost:8000/mcp",
            },
            cache_tools_list=True,
        )
    raise ValueError(f"Unknown transport: {TRANSPORT}")


def get_agent(mcp_server: MCPServer) -> Agent:
    return Agent(
        name="JupyterCAD Assistant",
        instructions=f"""You are a CAD assistant.

    Use the available tools to create/update the JupyterCAD document at path {JCAD_PATH} according to the user's instructions.

    To ensure successful updates, you MUST follow this workflow:
    1. Use the `get_current_cad_design` tool to read the JCAD file.
    2. Analyze the output from the tool to understand the existing objects.
    3. Based on the user's request and the existing design, use the available tools to complete the user's request.
    """,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
        model=MODEL,
    )


async def main() -> None:
    async with get_mcp_server() as mcp_server:
        with trace(workflow_name="jupytercad-mcp"):
            agent = get_agent(mcp_server=mcp_server)
            if USE_REPL:
                await run_demo_loop(agent)

            else:
                print("=== EXAMPLE ===")
                message = "Add a box with width/height/depth 1 and is positioned in the positive y direction."
                print(f"Running: {message}")
                result = await Runner.run(starting_agent=agent, input=message)
                print(result.final_output)


if __name__ == "__main__":
    if USE_MLFLOW_TRACING:
        import mlflow
        # Use mlflow for tracing
        mlflow.openai.autolog()
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("OpenAI-Agents Client")

    asyncio.run(main())
