import json
import sys
from unittest.mock import MagicMock, patch

import pytest
from jupytercad import CadDocument
from mcp.server.fastmcp import FastMCP

from jupytercad_mcp.server import get_mcp_server, main


def test_get_mcp_server():
    """
    Test that get_mcp_server returns a FastMCP instance
    and that the expected tools are registered.
    """
    mcp = get_mcp_server()
    assert isinstance(mcp, FastMCP)

    # Check that the server has the expected name
    assert mcp.name == "JupyterCAD MCP Server"

    tool_names = [tool.name for tool in mcp._tool_manager.list_tools()]

    # Check that the 'get_current_cad_design' tool is registered
    assert "get_current_cad_design" in tool_names

    # Check that all the exposed CadDocument methods are registered as tools
    exposed_methods = [
        "remove",
        "rename",
        "add_annotation",
        "remove_annotation",
        "add_step_file",
        "add_occ_shape",
        "add_box",
        "add_cone",
        "add_cylinder",
        "add_sphere",
        "add_torus",
        "cut",
        "fuse",
        "intersect",
        "chamfer",
        "fillet",
        "set_visible",
        "set_color",
    ]
    for method_name in exposed_methods:
        assert method_name in tool_names


def test_get_current_cad_design(tmp_path):
    """
    Test the get_current_cad_design tool.
    """
    mcp = get_mcp_server()
    get_current_cad_design_tool = next(
        tool for tool in mcp._tool_manager.list_tools() if tool.name == "get_current_cad_design"
    )

    # Create a dummy jcad file
    doc = CadDocument()
    jcad_file = tmp_path / "test.jcad"
    doc.save(str(jcad_file))

    # Run the tool
    content_from_tool = get_current_cad_design_tool.fn(jcad_path=str(jcad_file))
    content_from_file = jcad_file.read_text()

    # Check the result
    assert content_from_tool == content_from_file
    assert "objects" in json.loads(content_from_tool)


def test_exposed_add_box(tmp_path):
    """
    Test that an exposed method like add_box works correctly.
    """
    mcp = get_mcp_server()
    add_box_tool = next(tool for tool in mcp._tool_manager.list_tools() if tool.name == "add_box")

    # Create a dummy jcad file
    doc = CadDocument()
    jcad_file = tmp_path / "test.jcad"
    doc.save(str(jcad_file))

    # Run the tool
    box_name = "MyBox"
    add_box_tool.fn(jcad_path=str(jcad_file), name=box_name, length=1, width=2, height=3)

    # Check if the file was updated
    updated_doc = CadDocument.import_from_file(str(jcad_file))
    assert box_name in updated_doc.objects


@patch("jupytercad_mcp.server.argparse.ArgumentParser")
def test_main_default_transport(mock_argparse):
    """
    Test that main() uses "stdio" transport by default.
    """
    # Mock argument parsing
    mock_args = MagicMock()
    mock_args.transport = "stdio"
    mock_parser = mock_argparse.return_value
    mock_parser.parse_args.return_value = mock_args

    # Mock server
    mock_mcp = MagicMock()
    with patch("jupytercad_mcp.server.get_mcp_server", return_value=mock_mcp) as mock_get_mcp_server:
        main()
        mock_get_mcp_server.assert_called_once()
        mock_mcp.run.assert_called_once_with(transport="stdio")


@pytest.mark.parametrize("transport", ["stdio", "streamable-http"])
@patch("jupytercad_mcp.server.argparse.ArgumentParser")
def test_main_transport_args(mock_argparse, transport):
    """
    Test that main() correctly uses the "transport" argument.
    """
    # Mock argument parsing
    sys.argv = ["", transport]
    mock_args = MagicMock()
    mock_args.transport = transport
    mock_parser = mock_argparse.return_value
    mock_parser.parse_args.return_value = mock_args

    # Mock server
    mock_mcp = MagicMock()
    with patch("jupytercad_mcp.server.get_mcp_server", return_value=mock_mcp) as mock_get_mcp_server:
        main()
        mock_get_mcp_server.assert_called_once()
        mock_mcp.run.assert_called_once_with(transport=transport)

    # Clean up sys.argv
    sys.argv = [""]
