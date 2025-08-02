import inspect
from unittest.mock import MagicMock, patch

import pytest
from jupytercad import CadDocument

from jupytercad_mcp.server import (
    expose_method,
    get_current_cad_design,
    main,
    mcp,
)


def test_get_current_cad_design(tmp_path):
    # Create a dummy file
    file_path = tmp_path / "test.jcad"
    file_content = '{"objects": []}'
    with open(file_path, "w") as f:
        f.write(file_content)

    # Call the tool
    result = get_current_cad_design(str(file_path))

    # Check the result
    assert result == file_content


@patch("jupytercad_mcp.server.CadDocument")
def test_expose_method(mock_cad_document):
    # Mock CadDocument and its methods
    mock_doc_instance = MagicMock()
    mock_cad_document.load.return_value = mock_doc_instance

    # Mock a method to be exposed
    mock_method = MagicMock(__name__="test_method", __doc__="Test docstring")
    mock_method.__globals__ = {}
    mock_method.__annotations__ = {}  # Add annotations to the mock
    CadDocument.test_method = mock_method

    # Expose the method
    wrapped_method = expose_method(CadDocument, "test_method")

    # Call the wrapped method
    path = "/fake/path.jcad"
    kwargs = {"arg1": "value1", "arg2": 2}
    wrapped_method(path, **kwargs)

    # Assertions
    mock_cad_document.load.assert_called_once_with(path)
    mock_doc_instance.test_method.assert_called_once_with(**kwargs)
    mock_doc_instance.save.assert_called_once_with(path)

    # Check signature
    sig = inspect.signature(wrapped_method)
    assert "path" in sig.parameters
    assert "self" not in sig.parameters
    assert sig.parameters["path"].annotation == str

    # Check docstring
    assert "Test docstring" in wrapped_method.__doc__
    assert "Warning: This tool will update the JCAD document" in wrapped_method.__doc__

    # Cleanup the mocked method to avoid affecting other tests
    del CadDocument.test_method


@pytest.mark.asyncio
async def test_expose_method_signature_real_method():
    # Test with a real method from CadDocument to ensure signature creation works
    # We need to unregister the tool if it was registered before to avoid errors
    if "add_box" in await mcp.list_tools():
        del (await mcp.list_tools())["add_box"]
    wrapped_add_box = expose_method(CadDocument, "add_box")
    sig = inspect.signature(wrapped_add_box)

    assert "path" in sig.parameters
    assert "self" not in sig.parameters
    assert "name" in sig.parameters
    assert "length" in sig.parameters
    assert "width" in sig.parameters
    assert "height" in sig.parameters
    assert sig.parameters["path"].annotation == str
    assert sig.parameters["length"].annotation == float


@patch("jupytercad_mcp.server.argparse.ArgumentParser")
@patch("jupytercad_mcp.server.mcp.run")
def test_main(mock_mcp_run, mock_arg_parser):
    # Mock argument parser
    mock_args = MagicMock()
    mock_args.transport = "stdio"
    mock_arg_parser.return_value.parse_args.return_value = mock_args

    # Call main
    main()

    # Assertions
    mock_arg_parser.return_value.add_argument.assert_called_once()
    mock_arg_parser.return_value.parse_args.assert_called_once()
    mock_mcp_run.assert_called_once_with(transport="stdio")


@patch("jupytercad_mcp.server.argparse.ArgumentParser")
@patch("jupytercad_mcp.server.mcp.run")
def test_main_http_transport(mock_mcp_run, mock_arg_parser):
    # Mock argument parser for http transport
    mock_args = MagicMock()
    mock_args.transport = "streamable-http"
    mock_arg_parser.return_value.parse_args.return_value = mock_args

    # Call main
    main()

    # Assertions
    mock_mcp_run.assert_called_once_with(transport="streamable-http")


@pytest.mark.asyncio
async def test_mcp_tools_are_registered():
    # Check if some of the tools are registered in the MCP instance
    tool_names = [t.name for t in await mcp.list_tools()]
    assert "get_current_cad_design" in tool_names
    assert "add_box" in tool_names
    assert "cut" in tool_names
    assert "set_color" in tool_names
