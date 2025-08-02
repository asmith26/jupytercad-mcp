import argparse
import inspect
from functools import wraps
from typing import Any, Callable, Type, get_type_hints

from jupytercad import CadDocument
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="JupyterCAD MCP Server")


@mcp.tool()
def get_current_cad_design(path: str) -> str:
    """Read the current content of a JCAD (JupyterCAD) document.

    Use this tool to understand the current state of a JCAD file before modifying it.

    :param path: The path to the JCAD file.
    :return: The current content of the JCAD file.
    """
    with open(path, "r") as f:
        return f.read()


def expose_method(cls: Type[Any], method_name: str) -> Callable[..., Any]:
    """Expose a method of a class as an MCP tool."""
    method = getattr(cls, method_name)

    @wraps(method)
    def _wrapper(path: str, **kwargs: Any) -> None:
        # Load current .jcad document
        doc = CadDocument.load(path)

        # Update doc
        getattr(doc, method_name)(**kwargs)

        # Write updates to the same filepath
        doc.save(path)

    _wrapper.__doc__ = f"""{method.__doc__}

        Warning: This tool will update the JCAD document at the given path.
        To understand the current state of the document, you MUST first use the 'get_current_cad_design' tool.
        """

    # Remove 'self' from signature
    type_hints = get_type_hints(method, globalns=method.__globals__)
    orig_sig = inspect.signature(method)
    new_params = [
        param.replace(annotation=type_hints.get(param.name, param.annotation))
        for param in orig_sig.parameters.values()
        if param.name != "self"
    ]

    # Add 'path' to signature
    path_param = inspect.Parameter("path", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
    new_params.insert(0, path_param)
    _wrapper.__signature__ = orig_sig.replace(  # type: ignore
        parameters=new_params,
        return_annotation=inspect.Signature.empty,  # remove return type (to prevent pydantic errors)
    )

    # Register it with MCP
    tool_fn = mcp.tool()(_wrapper)
    return tool_fn


# Add CadDocument tools
expose_method(cls=CadDocument, method_name="remove")  # todo add docstring?
expose_method(cls=CadDocument, method_name="rename")  # todo add docstring?
expose_method(cls=CadDocument, method_name="add_annotation")
expose_method(cls=CadDocument, method_name="remove_annotation")
# expose_method(cls=CadDocument, method_name="add_step_file")  # omitted for simplicity (has `path` parameter)
expose_method(cls=CadDocument, method_name="add_occ_shape")
expose_method(cls=CadDocument, method_name="add_box")
expose_method(cls=CadDocument, method_name="add_cone")
expose_method(cls=CadDocument, method_name="add_cylinder")
expose_method(cls=CadDocument, method_name="add_sphere")
expose_method(cls=CadDocument, method_name="add_torus")
expose_method(cls=CadDocument, method_name="cut")
expose_method(cls=CadDocument, method_name="fuse")
expose_method(cls=CadDocument, method_name="intersect")
expose_method(cls=CadDocument, method_name="chamfer")
expose_method(cls=CadDocument, method_name="fillet")
# expose_method(cls=CadDocument, method_name="extrusion")  todo check
expose_method(cls=CadDocument, method_name="set_visible")  # todo add docstring?
expose_method(cls=CadDocument, method_name="set_color")  # todo add docstring?


def main() -> None:
    parser = argparse.ArgumentParser(description="Start an MCP server for JupyterCAD.")
    parser.add_argument(
        "transport",
        nargs="?",
        default="stdio",
        choices=["stdio", "streamable-http"],
        help="Transport type (stdio or streamable-http)",
    )
    args = parser.parse_args()

    # Run server
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
