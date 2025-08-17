# jupytercad-mcp

An MCP server for JupyterCAD that allows you to control it using natural language.

https://github.com/user-attachments/assets/7edb31b2-2c80-4096-9d9c-048ae27c54e7

Suggestions and contributions are very welcome.

## Usage

> NOTE: the `jupytercad` dependency currently requires [this PR](https://github.com/jupytercad/JupyterCAD/pull/772) from JupyterCAD.

The default transport mechanism is [`stdio`](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#stdio). To start the server with `stdio`, use the following command:

```bash
uvx --with jupytercad-mcp jupytercad-mcp
```

To use the [`streamable-http`](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http) transport, use this command instead:

```bash
uvx --with jupytercad-mcp jupytercad-mcp streamable-http
```

### Example

An example using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) is available at [examples/openai_agents_client.py](examples/openai_agents_client.py). To run it, follow these steps:

1.  Clone the repository and navigate into the directory:
    ```bash
    git clone git@github.com:asmith26/jupytercad-mcp.git
    cd jupytercad-mcp
    ```

2.  Install the OpenAI Agents SDK. A Makefile target is provided for convenience:
    ```bash
    make setup-examples-env
    ```

3.  In [examples/openai_agents_client.py](examples/openai_agents_client.py#L13), update line 13 to configure a `MODEL` (see [supported models](https://openai.github.io/openai-agents-python/models/)).

4.  Run JupyterLab from the project's root directory:
    ```bash
    make jupyter-lab
    ```

5.  In JupyterLab, create a new "CAD file" and rename it to **my_cad_design.jcad**. This file path matches the default [`JCAD_PATH`](examples/openai_agents_client.py#L16) in the example, allowing you to visualise the changes made by the JupyterCAD MCP server.

6.  (Optional) The OpenAI Agents SDK supports [tracing](https://openai.github.io/openai-agents-python/tracing/) to record events like LLM generations and tool calls. To enable it, set [`USE_MLFLOW_TRACING=True`](examples/openai_agents_client.py#L15) and run the MLflow UI:
    ```bash
    make mlflow-ui
    ```

7.  Run the example with the default instruction, "Add a box with width/height/depth 1":
    ```bash
    make example-openai-agents-client
    ```

#### Interactive Chat Interface

The example includes an interactive chat interface using the OpenAI Agents SDK's 
[REPL utility](https://openai.github.io/openai-agents-python/repl/). To enable it, set [`USE_REPL=True`](examples/openai_agents_client.py#L14).

#### `streamable-http`

To use the `streamable-http` transport, first start the MCP server:
```bash
uvx --with jupytercad-mcp jupytercad-mcp streamable-http
```

Then, run the example with the `TRANSPORT` variable set to `"streamable-http"` in the [client example](examples/openai_agents_client.py#L12).

## Tools

The following tools are available:

- **get_current_cad_design**: Reads the current content of the JCAD document.
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
