#!/usr/bin/env python3
"""
tests/test_reqifio.py

Unit tests for the reqifio package using the Python 3 standard library.
"""

import os
import tempfile
import sqlite3
import unittest
from xml.etree import ElementTree as ET

# Import modules from our reqifio package.
from reqifio import reqif_parser, reqif_writer, sqlite_adapter, command, model

# Minimal sample ReqIF content including CORE-CONTENT with a header and a requirement.
SAMPLE_REQIF_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF>
  <REQ-IF-HEADER>
    <TITLE>Test Document</TITLE>
    <CREATOR>UnitTest</CREATOR>
  </REQ-IF-HEADER>
  <CORE-CONTENT>
    <REQUIREMENTS>
      <REQ-IF-REQUISITE>
        <ID>REQ-001</ID>
        <TITLE>Initial Requirement</TITLE>
        <DESCRIPTION>Initial description.</DESCRIPTION>
      </REQ-IF-REQUISITE>
    </REQUIREMENTS>
    <SPEC-OBJECTS></SPEC-OBJECTS>
    <SPEC-RELATIONS></SPEC-RELATIONS>
    <SPEC-TYPES></SPEC-TYPES>
  </CORE-CONTENT>
</REQ-IF>
"""


class TestReqifParsing(unittest.TestCase):
    def test_parse_reqif_file(self):
        # Write the sample XML to a temporary file.
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".reqif", mode="w", encoding="utf-8"
        ) as temp:
            temp.write(SAMPLE_REQIF_CONTENT)
            temp_path = temp.name

        try:
            # Parse file.
            doc = reqif_parser.parse_reqif_file(temp_path)
            self.assertEqual(doc.header.get("TITLE"), "Test Document")
            self.assertEqual(len(doc.requirements), 1)
            self.assertEqual(doc.requirements[0].req_id, "REQ-001")
        finally:
            os.remove(temp_path)


class TestReqifWriting(unittest.TestCase):
    def test_write_reqif_file(self):
        # Create a simple ReqIFDocument.
        doc = model.ReqIFDocument(header={"TITLE": "Write Test", "CREATOR": "UnitTest"})
        req = model.Requirement(req_id="REQ-002", title="Write Req", description="Desc")
        doc.add_requirement(req)

        # Write to a temporary file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".reqif") as temp:
            temp_path = temp.name

        try:
            reqif_writer.write_reqif_file(doc, temp_path)
            # Reparse the file to check the written content.
            tree = ET.parse(temp_path)
            root = tree.getroot()
            header = root.find("REQ-IF-HEADER")
            self.assertIsNotNone(header)
            title_elem = header.find("TITLE")
            self.assertEqual(title_elem.text, "Write Test")
        finally:
            os.remove(temp_path)


class TestSqliteAdapter(unittest.TestCase):
    def test_db_write_and_read(self):
        # Create a document with one requirement.
        doc = model.ReqIFDocument(header={"TITLE": "DB Test"})
        req = model.Requirement(req_id="REQ-003", title="DB Req", description="DB Desc")
        doc.add_requirement(req)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp:
            db_path = temp.name

        try:
            sqlite_adapter.write_doc_to_db(doc, db_path)
            doc_from_db = sqlite_adapter.read_doc_from_db(db_path)
            self.assertEqual(doc_from_db.header.get("TITLE"), "DB Test")
            self.assertEqual(len(doc_from_db.requirements), 1)
            self.assertEqual(doc_from_db.requirements[0].req_id, "REQ-003")
        finally:
            os.remove(db_path)


class TestCommandManager(unittest.TestCase):
    def test_undo_redo(self):
        # Create an empty document.
        doc = model.ReqIFDocument(header={"TITLE": "Command Test"})
        cmd_mgr = command.CommandManager()

        # Add a requirement.
        req = model.Requirement(
            req_id="REQ-004", title="Cmd Req", description="Cmd Desc"
        )
        add_cmd = command.AddRequirementCommand(doc, req)
        cmd_mgr.execute_command(add_cmd)
        self.assertEqual(len(doc.requirements), 1)

        # Undo add.
        cmd_mgr.undo()
        self.assertEqual(len(doc.requirements), 0)

        # Redo add.
        cmd_mgr.redo()
        self.assertEqual(len(doc.requirements), 1)

        # Update the requirement.
        update_cmd = command.UpdateRequirementCommand(
            doc, "REQ-004", new_title="Updated Cmd Req"
        )
        cmd_mgr.execute_command(update_cmd)
        self.assertEqual(doc.get_requirement("REQ-004").title, "Updated Cmd Req")

        # Undo update.
        cmd_mgr.undo()
        self.assertEqual(doc.get_requirement("REQ-004").title, "Cmd Req")


if __name__ == "__main__":
    unittest.main()
