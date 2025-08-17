"""An example of how to use the JupyterCAD MCP server with the openai-agents library."""

import asyncio
from pathlib import Path

from agents import Agent, Runner, run_demo_loop, trace, set_trace_processors
from agents.mcp import MCPServer, MCPServerStdio, MCPServerStreamableHttp
from agents.model_settings import ModelSettings

# CONFIG
set_trace_processors([])  # disable OpenAI tracing
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
        instructions=f"""You are a JupyterCAD assistant. Your primary goal is to help users create and modify CAD designs in the file located at path={JCAD_PATH}, using the tools provided by the MCP server.

    You MUST:
    1. Think about the user's request: Think about the object the user has requested a JupyterCAD design for, and think about what tools/shapes/steps you can take to achieve the user's request.
    2. Execute with Verification: Use the available tools to perform the requested actions. Regularly use `get_current_cad_design` at intermediate steps to verify progress.
    3. **NEVER Fuse the Entire Object:** To keep the design easy to edit, group objects that correspond to individual parts together and give them meaningful names. Never fuse all objects into a single entity.
    4. Ensure All Parts Are Visible: Before finishing, confirm that every part of the object is visible.
    5. **NEVER set Color to `null`:** Use the string `"#808080"` for the default color of an object. (I repeat: NEVER use `null` for Color.)
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
    asyncio.run(main())
