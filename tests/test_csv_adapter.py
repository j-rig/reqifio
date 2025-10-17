"""
test_csv_adapter.py

This module contains test cases for reading and writing the complete ReqIF
data model to CSV files using the CSVAdapter from csv_adapter.py.
"""

import os
import shutil
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
from reqifio.csv_adapter import CSVAdapter


def create_sample_reqif():
    """
    Helper function to create a minimal ReqIF data model instance.
    """
    header = ReqIFHeader(
        identifier="header-1",
        creation_time=datetime.now(),
        repository_id="repo-1",
        reqif_tool_id="ToolCSV",
        reqif_version="1.0",
        source_tool_id="SourceCSV",
        title="Sample ReqIF CSV",
    )
    dt_xhtml = DataTypeDefinitionXHTML(
        identifier="dt_xhtml_1", last_change=datetime.now(), long_name="XHTMLString"
    )
    data_types = DataTypes(xhtml=dt_xhtml)
    spec_obj = SpecObject(
        identifier="obj-1",
        last_change=datetime.now(),
        long_name="Requirement-1",
        type_ref="type-req",
        attributes=[
            AttributeValue(definition_ref="attr-1", value="CSV Test Requirement")
        ],
    )
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
        long_name="Module-CSV",
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


class TestCSVAdapter(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to store CSV files.
        self.temp_dir = tempfile.mkdtemp()
        self.adapter = CSVAdapter(self.temp_dir)
        self.sample_reqif = create_sample_reqif()

    def tearDown(self):
        # Remove the temporary directory and its contents.
        shutil.rmtree(self.temp_dir)

    def test_write_and_read(self):
        """
        Test writing a ReqIF model to CSV files and reading it back.
        """
        # Write sample ReqIF data to CSV files.
        self.adapter.write(self.sample_reqif)

        # Read the data model back from CSV files.
        reqif_read = self.adapter.read()

        # Verify header values.
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

        # Verify Spec Objects and Attributes.
        self.assertEqual(
            len(reqif_read.core_content.reqif_content.spec_objects),
            len(self.sample_reqif.core_content.reqif_content.spec_objects),
        )
        orig_obj = self.sample_reqif.core_content.reqif_content.spec_objects[0]
        read_obj = reqif_read.core_content.reqif_content.spec_objects[0]
        self.assertEqual(orig_obj.identifier, read_obj.identifier)
        self.assertEqual(orig_obj.long_name, read_obj.long_name)
        self.assertEqual(len(orig_obj.attributes), len(read_obj.attributes))
        self.assertEqual(orig_obj.attributes[0].value, read_obj.attributes[0].value)

        # Verify Specifications and Spec Hierarchies.
        self.assertEqual(
            len(reqif_read.core_content.reqif_content.specifications),
            len(self.sample_reqif.core_content.reqif_content.specifications),
        )
        orig_spec = self.sample_reqif.core_content.reqif_content.specifications[0]
        read_spec = reqif_read.core_content.reqif_content.specifications[0]
        self.assertEqual(orig_spec.identifier, read_spec.identifier)
        self.assertEqual(
            len(orig_spec.spec_hierarchies), len(read_spec.spec_hierarchies)
        )
        self.assertEqual(
            orig_spec.spec_hierarchies[0].object_ref,
            read_spec.spec_hierarchies[0].object_ref,
        )

        # Verify tool extensions.
        self.assertEqual(reqif_read.tool_extensions, self.sample_reqif.tool_extensions)

    def test_csv_files_created(self):
        """
        Test that CSV files are created in the designated folder.
        """
        self.adapter.write(self.sample_reqif)
        expected_files = [
            "header.csv",
            "datatype_xhtml.csv",
            "datatype_enumeration.csv",
            "enum_value.csv",
            "datatype_boolean.csv",
            "datatype_date.csv",
            "datatype_integer.csv",
            "datatype_real.csv",
            "datatype_string.csv",
            "spec_object.csv",
            "spec_object_attribute.csv",
            "specification.csv",
            "spec_hierarchy.csv",
            "tool_extensions.csv",
        ]
        # Some files might not be generated if the data is not provided,
        # but header.csv, datatype_xhtml.csv, spec_object.csv, specification.csv, and tool_extensions.csv
        # are expected.
        necessary_files = [
            "header.csv",
            "datatype_xhtml.csv",
            "spec_object.csv",
            "specification.csv",
            "tool_extensions.csv",
        ]
        for fname in necessary_files:
            fpath = os.path.join(self.temp_dir, fname)
            self.assertTrue(os.path.exists(fpath), f"Expected file {fname} not found.")


if __name__ == "__main__":
    unittest.main()
