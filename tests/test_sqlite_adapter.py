"""
test_sqlite_adapter.py

This module contains test cases for reading and writing the complete ReqIF data model
to a SQLite database using the SQLiteAdapter from sqlite_adapter.py.
"""

import os
import tempfile
import unittest
from datetime import datetime

from reqifio.model import (
    ReqIF,
    ReqIFHeader,
    CoreContent,
    ReqIFContent,
    DataTypes,
    DataTypeDefinitionXHTML,
    SpecObject,
    AttributeValue,
    Specification,
    SpecHierarchy,
)
from reqifio.sqlite_adapter import SQLiteAdapter


def create_sample_reqif():
    """
    Helper function to create a minimal ReqIF data model instance.
    """
    header = ReqIFHeader(
        identifier="header-1",
        creation_time=datetime.now(),
        repository_id="repo-1",
        reqif_tool_id="ToolA",
        reqif_version="1.0",
        source_tool_id="SourceA",
        title="Sample ReqIF",
    )

    # Create a minimal data types model with XHTML only.
    dt_xhtml = DataTypeDefinitionXHTML(
        identifier="dt_xhtml_1", last_change=datetime.now(), long_name="XHTMLString"
    )
    data_types = DataTypes(xhtml=dt_xhtml)

    # Create one Spec Object with one attribute.
    spec_obj = SpecObject(
        identifier="obj-1",
        last_change=datetime.now(),
        long_name="Requirement-1",
        type_ref="type-req",
        attributes=[AttributeValue(definition_ref="attr-1", value="Test Requirement")],
    )

    # Create one Specification with one spec hierarchy.
    spec_hierarchy = SpecHierarchy(
        identifier="hier-1",
        last_change=datetime.now(),
        long_name="Requirement-1",
        is_editable=True,
        object_ref="obj-1",
    )
    specification = Specification(
        identifier="spec-1",
        last_change=datetime.now(),
        long_name="Module-1",
        type_ref="spec-type-1",
        spec_hierarchies=[spec_hierarchy],
    )

    reqif_content = ReqIFContent(
        data_types=data_types, spec_objects=[spec_obj], specifications=[specification]
    )
    core_content = CoreContent(reqif_content=reqif_content)
    return ReqIF(
        header=header, core_content=core_content, tool_extensions="<extensions/>"
    )


class TestSQLiteAdapter(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()  # We only need the file path.
        self.adapter = SQLiteAdapter(self.db_path)
        self.adapter.create_schema()
        self.sample_reqif = create_sample_reqif()

    def tearDown(self):
        os.remove(self.db_path)

    def test_write_and_read(self):
        """Test writing a ReqIF model to SQLite and reading it back."""
        self.adapter.write(self.sample_reqif)
        reqif_read = self.adapter.read()

        # Verify header fields.
        self.assertEqual(
            reqif_read.header.identifier, self.sample_reqif.header.identifier
        )
        self.assertEqual(reqif_read.header.title, self.sample_reqif.header.title)

        # Verify DataType XHTML.
        self.assertIsNotNone(reqif_read.core_content.reqif_content.data_types.xhtml)
        self.assertEqual(
            reqif_read.core_content.reqif_content.data_types.xhtml.identifier,
            self.sample_reqif.core_content.reqif_content.data_types.xhtml.identifier,
        )

        # Verify Spec Objects count and values.
        self.assertEqual(
            len(reqif_read.core_content.reqif_content.spec_objects),
            len(self.sample_reqif.core_content.reqif_content.spec_objects),
        )
        obj_orig = self.sample_reqif.core_content.reqif_content.spec_objects[0]
        obj_read = reqif_read.core_content.reqif_content.spec_objects[0]
        self.assertEqual(obj_orig.identifier, obj_read.identifier)
        self.assertEqual(obj_orig.long_name, obj_read.long_name)
        self.assertEqual(len(obj_orig.attributes), len(obj_read.attributes))
        self.assertEqual(obj_orig.attributes[0].value, obj_read.attributes[0].value)

        # Verify Specifications and spec hierarchies.
        self.assertEqual(
            len(reqif_read.core_content.reqif_content.specifications),
            len(self.sample_reqif.core_content.reqif_content.specifications),
        )
        spec_orig = self.sample_reqif.core_content.reqif_content.specifications[0]
        spec_read = reqif_read.core_content.reqif_content.specifications[0]
        self.assertEqual(spec_orig.identifier, spec_read.identifier)
        self.assertEqual(
            len(spec_orig.spec_hierarchies), len(spec_read.spec_hierarchies)
        )
        self.assertEqual(
            spec_orig.spec_hierarchies[0].object_ref,
            spec_read.spec_hierarchies[0].object_ref,
        )

        # Verify tool extensions.
        self.assertEqual(reqif_read.tool_extensions, self.sample_reqif.tool_extensions)

    def test_schema_creation(self):
        """Test that schema creation runs without error and tables exist."""
        # Reconnect to the database and check that the header table exists.
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='reqif_header'"
        )
        table = c.fetchone()
        conn.close()
        self.assertIsNotNone(table)
        self.assertEqual(table[0], "reqif_header")


if __name__ == "__main__":
    unittest.main()
