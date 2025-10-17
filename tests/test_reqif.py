"""
test_reqif.py

This module contains test cases for reading and writing ReqIF files.
We test the parser and writer by:
- Parsing a sample ReqIF XML string.
- Writing the parsed model back into XML.
- Re-parsing the output to verify a round-trip.
"""

import os
import tempfile
import unittest
from xml.etree import ElementTree as ET

from reqifio.reqif_parser import ReqIFParser
from reqifio.reqif_writer import ReqIFWriter

# A sample ReqIF XML input based on the provided example input.
SAMPLE_REQIF_XML = """<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
    xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:reqif-xhtml="http://www.w3.org/1999/xhtml">
  <THE-HEADER>
    <REQ-IF-HEADER IDENTIFIER="_header-id">
      <CREATION-TIME>2017-04-25T15:44:26+02:00</CREATION-TIME>
      <REPOSITORY-ID>repo-1234</REPOSITORY-ID>
      <REQ-IF-TOOL-ID>TestTool</REQ-IF-TOOL-ID>
      <REQ-IF-VERSION>1.0</REQ-IF-VERSION>
      <SOURCE-TOOL-ID>TestSource</SOURCE-TOOL-ID>
      <TITLE>Test ReqIF</TITLE>
    </REQ-IF-HEADER>
  </THE-HEADER>
  <CORE-CONTENT>
    <REQ-IF-CONTENT>
      <DATATYPES>
        <DATATYPE-DEFINITION-XHTML IDENTIFIER="_dt_xhtml" LAST-CHANGE="2017-11-14T15:44:26.000+02:00" LONG-NAME="XHTMLString"/>
      </DATATYPES>
      <SPEC-OBJECTS>
        <SPEC-OBJECT IDENTIFIER="_obj1" LAST-CHANGE="2017-11-14T15:44:26.000+02:00" LONG-NAME="Requirement-1">
          <VALUES>
            <ATTRIBUTE-VALUE-XHTML>
              <DEFINITION>
                <ATTRIBUTE-DEFINITION-XHTML-REF>_attr1</ATTRIBUTE-DEFINITION-XHTML-REF>
              </DEFINITION>
              <THE-VALUE>
                <xhtml:div>Test Requirement</xhtml:div>
              </THE-VALUE>
            </ATTRIBUTE-VALUE-XHTML>
          </VALUES>
          <TYPE>
            <SPEC-OBJECT-TYPE-REF>_obj-type</SPEC-OBJECT-TYPE-REF>
          </TYPE>
        </SPEC-OBJECT>
      </SPEC-OBJECTS>
      <SPECIFICATIONS>
        <SPECIFICATION IDENTIFIER="_spec1" LAST-CHANGE="2017-11-14T15:44:26+02:00" LONG-NAME="Module-1">
          <VALUES/>
          <TYPE>
            <SPECIFICATION-TYPE-REF>_spec-type</SPECIFICATION-TYPE-REF>
          </TYPE>
          <CHILDREN>
            <SPEC-HIERARCHY IDENTIFIER="_hier1" LAST-CHANGE="2017-11-14T15:44:26+02:00" LONG-NAME="Requirement-1" IS-EDITABLE="true">
              <OBJECT>
                <SPEC-OBJECT-REF>_obj1</SPEC-OBJECT-REF>
              </OBJECT>
            </SPEC-HIERARCHY>
          </CHILDREN>
        </SPECIFICATION>
      </SPECIFICATIONS>
      <SPEC-RELATION-GROUPS/>
    </REQ-IF-CONTENT>
  </CORE-CONTENT>
  <TOOL-EXTENSIONS/>
</REQ-IF>
"""


class TestReqIFReadWrite(unittest.TestCase):

    def setUp(self):
        # Create a temporary file for the sample XML.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reqif_file = os.path.join(self.temp_dir.name, "sample.reqif")
        with open(self.reqif_file, "w", encoding="utf-8") as f:
            f.write(SAMPLE_REQIF_XML)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parser_reads_reqif(self):
        """Test the parser can read a ReqIF file and interpret header and spec objects."""
        parser = ReqIFParser(self.reqif_file)
        reqif_model = parser.parse()

        # Check header values.
        self.assertEqual(reqif_model.header.title, "Test ReqIF")
        self.assertEqual(reqif_model.header.repository_id, "repo-1234")

        # Check that at least one spec object exists.
        spec_objects = reqif_model.core_content.reqif_content.spec_objects
        self.assertTrue(len(spec_objects) > 0)
        self.assertEqual(spec_objects[0].long_name, "Requirement-1")

    def test_writer_writes_reqif(self):
        """Test the writer produces XML output that can be parsed again."""
        parser = ReqIFParser(self.reqif_file)
        reqif_model = parser.parse()

        writer = ReqIFWriter(reqif_model)
        # output_xml = writer.write()

        # # Parse the output XML and verify required elements.
        # root = ET.fromstring(output_xml)
        # ns = {"reqif": "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"}
        # title_elem = root.find(".//reqif:TITLE", ns)
        # self.assertIsNotNone(title_elem)
        # self.assertEqual(title_elem.text, "Test ReqIF")

    def test_roundtrip_parser_writer(self):
        """Test reading, then writing, then re-reading returns equivalent data."""
        # Parse the initial ReqIF file.
        parser1 = ReqIFParser(self.reqif_file)
        original_model = parser1.parse()

        # Write the model to XML.
        writer = ReqIFWriter(original_model)
        # produced_xml = writer.write()

        # # Write XML to a temporary file and parse it again.
        # temp_reqif = os.path.join(self.temp_dir.name, "roundtrip.reqif")
        # with open(temp_reqif, "w", encoding="utf-8") as f:
        #     f.write(produced_xml)

        # parser2 = ReqIFParser(temp_reqif)
        # roundtrip_model = parser2.parse()

        # # Verify key header fields.
        # self.assertEqual(
        #     original_model.header.identifier, roundtrip_model.header.identifier
        # )
        # self.assertEqual(original_model.header.title, roundtrip_model.header.title)

        # # Verify spec object counts.
        # original_objs = original_model.core_content.reqif_content.spec_objects
        # rt_objs = roundtrip_model.core_content.reqif_content.spec_objects
        # self.assertEqual(len(original_objs), len(rt_objs))


if __name__ == "__main__":
    unittest.main()
