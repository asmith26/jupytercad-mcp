# jupytercad-mcp

MCP server for JupyterCAD, allowing you to control JupyterCAD with natural language!

Any suggestions/contributions very welcome.

## Usage

As per the example at [examples/openai_agents_client.py](examples/openai_agents_client.py), you should be able to add
this server to a MCP client in the usual way with a command like: 

```bash
uvx --with jupytercad-mcp jupytercad-mcp
```

The default transport mechanism is [`stdio`](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#stdio).
To use [`streamable-http`](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http) 

```bash
uvx --with jupytercad-mcp jupytercad-mcp streamable-http
```

### Example

An example at [examples/openai_agents_client.py](examples/openai_agents_client.py) has been created using the 
[OpenAI Agents SDK](https://github.com/openai/openai-agents-python). To run this:

1. Clone the repo `git clone git@github.com:asmith26/jupytercad-mcp.git` and `cd jupytercad-mcp`

2. [Install](https://openai.github.io/openai-agents-python/quickstart/#install-the-agents-sdk) the OpenAI Agents SDK. A 
   Makefile target exists to help with this: 

```bash
make setup-examples-env
```

3. Within [examples/openai_agents_client.py](examples/openai_agents_client.py#L13) update line 13 to configure a `MODEL`
   (see [models](https://openai.github.io/openai-agents-python/models/).
   
4. Run jupyter-lab from the examples directory

```bash
make jupyter-lab
```

5. Launch a new "CAD file" and rename it to **my_cad_design.jcad**. This matches the default `JCAD_PATH` defined in the 
   example, and will allow you to visualise the changes made by the JupyterCAD MCP server.

6. (Optional) The OpenAI Agents SDK includes support for [tracing](https://openai.github.io/openai-agents-python/tracing/),
   which records events during an agent run (e.g. LLM generations, tool calls, handoffs, guardrails). If you wish to
   enable this set `USE_MLFLOW_TRACING=True` and run:
   
```bash
make mlflow-ui
```

7. Run the default example with:

```bash
make example-openai-agents-client 
```

This should follow the example instruction: *"Add a box with width/height/depth 1"*

The example also includes an option to enable an interactive chat-like interface (using the OpenAI Agents SDK's [REPL 
utility](https://openai.github.io/openai-agents-python/repl/), achieved by setting `USE_REPL = True`).

To use `streambable-http`, you first need to start the MCP server (e.g. with: 

```bash
uvx --with jupytercad-mcp jupytercad-mcp streamable-http
```

You can then run [examples/openai_agents_client.py](examples/openai_agents_client.py) with `TRANSPORT = "streambable-http"`.

## Tools

The following tools are available:

- **get_current_cad_design**: Read the current content of a document (helpful for understanding the current state of a
  JCAD file before modifying it).
- **remove**: Remove an object from the document.
- **rename**: Rename an object in the document.
- **add_annotation**: Add an annotation to the document.
- **remove_annotation**: Remove an annotation from the document.
- **add_occ_shape**: Add an OpenCascade TopoDS shape to the document.
- **add_box**: Add a box to the document.
- **add_cone**: Add a cone to the document.
- **add_cylinder**: Add a cylinder to the document.
- **add_sphere**: Add a sphere to the document.
- **add_torus**: Add a torus to the document.
- **cut**: Apply a cut boolean operation between two objects.
- **fuse**: Apply a union boolean operation between two objects.
- **intersect**: Apply an intersection boolean operation between two objects.
- **chamfer**: Apply a chamfer operation on an object.
- **fillet**: Apply a fillet operation on an object.
- **set_visible**: Sets the visibility of an object.
- **set_color**: Sets the color of an object.
