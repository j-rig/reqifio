#!/usr/bin/env python3
"""
example.py

Demonstrates usage of the extended reqifio.
 - Parses a full ReqIF file.
 - Manipulates requirements via commands (with undo/redo).
 - Writes out the ReqIF XML file.
 - Persists the full schema to and from a SQLite database.
"""

from reqifio import reqif_parser, reqif_writer, sqlite_adapter, command, model

# Parse an extended ReqIF file.
doc = reqif_parser.parse_reqif_file("sample.reqif")

# Create a command manager.
cmd_manager = command.CommandManager()

# Add a new requirement.
new_req = model.Requirement(
    req_id="REQ-1001",
    title="New Requirement",
    description="This requirement was added using the command pattern.",
)
add_cmd = command.AddRequirementCommand(doc, new_req)
cmd_manager.execute_command(add_cmd)

# Update the new requirement.
update_cmd = command.UpdateRequirementCommand(
    doc, "REQ-1001", new_title="Updated Title"
)
cmd_manager.execute_command(update_cmd)

# Undo and redo operations.
cmd_manager.undo()
cmd_manager.redo()

# Write back to an XML file.
reqif_writer.write_reqif_file(doc, "modified.reqif")

# Save to an SQLite database.
sqlite_adapter.write_doc_to_db(doc, "reqif.db")

# Read document from the database.
doc_from_db = sqlite_adapter.read_doc_from_db("reqif.db")
print("Document retrieved from DB:", doc_from_db)
