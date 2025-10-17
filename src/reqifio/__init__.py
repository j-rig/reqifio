"""
reqifio/__init__.py

This module initializes the reqif_lib package. We expose the primary modules:
 - reqif_parser: Parsing ReqIF files (XML) into internal model.
 - reqif_writer: Writing internal model to ReqIF XML files.
 - sqlite_adapter: Conversion of internal model to a full SQL representation and vice versa.
 - csv_adapter: Conversion of internal model to a full CSV representation and vice versa.
 - command: Command pattern implementation for undo/redo of CRUD operations.
 - model: Internal data model representing the ReqIF schema.

The library complies with ReqIF 1.1 and industrial use cases while using only native Python libraries.
"""

from . import reqif_parser, reqif_writer, sqlite_adapter, csv_adapter, cli, model

__all__ = [
    "reqif_parser",
    "reqif_writer",
    "sqlite_adapter",
    "csv_adapter",
    "clai",
    "model",
]
