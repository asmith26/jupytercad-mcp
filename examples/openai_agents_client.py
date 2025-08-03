"""An example of how to use the JupyterCAD MCP server with the openai-agents library."""

import asyncio
import sys
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
                "command": "uvx",
                "args": ["--with", "jupytercad-mcp", "jupytercad-mcp"],
            },
            cache_tools_list=True,
        )
    elif TRANSPORT == "streamable-http":
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
        instructions=f"""You are a JupyterCAD assistant. Your primary goal is to help users create and modify CAD designs in the file at {JCAD_PATH}.

To ensure accuracy, you MUST follow this workflow:
1.  **Inspect the Design:** Always start by using the `get_current_cad_design` tool to understand the current state of the CAD file.
2.  **Analyze and Plan:** Review the user's request and the current design to determine the necessary steps and tools.
3.  **Execute:** Use the available tools to perform the requested actions. For complex requests, use `get_current_cad_design` at intermediate steps to verify progress.

**Important Guidelines:**
- If the user's request is ambiguous or unclear, ask for clarification before proceeding.
- Your responses should be based on the successful execution of tools.

For inspiration, you can review example JupyterCAD designs at:
- https://raw.githubusercontent.com/jupytercad/JupyterCAD/refs/heads/main/examples/screwdriver.jcad
- https://raw.githubusercontent.com/jupytercad/JupyterCAD/refs/heads/main/examples/pawn.jcad
- https://raw.githubusercontent.com/jupytercad/JupyterCAD/refs/heads/main/examples/pad.jcad
- https://raw.githubusercontent.com/jupytercad/JupyterCAD/refs/heads/main/examples/Gear.jcad
- https://raw.githubusercontent.com/jupytercad/JupyterCAD/refs/heads/main/examples/ArchDetail.jcad
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
                message = "Add a box with width/height/depth 1."
                print(f"Running: {message}")
                result = await Runner.run(starting_agent=agent, input=message)
                print(result.final_output)


if __name__ == "__main__":
    print("\n=== CONFIG ===")
    print(f"TRANSPORT: {TRANSPORT}")
    print(f"MODEL: {MODEL.model}")
    print(f"USE_REPL: {USE_REPL}")
    print(f"JCAD_PATH: {JCAD_PATH}")
    print(f"USE_MLFLOW_TRACING: {USE_MLFLOW_TRACING}")

    if USE_MLFLOW_TRACING:
        print("\n    *** WARNING: to use MLFlow tracing you need to first run `mlflow ui` (or `make mlflow-ui`). ***\n")
        import mlflow
        # Use mlflow for tracing
        mlflow.openai.autolog()
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("OpenAI-Agents Client")
    print("=== End: CONFIG ===\n")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
