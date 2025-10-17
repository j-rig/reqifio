#!/usr/bin/env python3
"""
tests/test_reqifio.py

Unit tests for the reqifio package using the Python 3 standard library.
"""

import os
import tempfile
import sqlite3
import unittest
import os.path
from xml.etree import ElementTree as ET

# Import modules from our reqifio package.
from reqifio import (
    reqif_parser,
    reqif_writer,
    sqlite_adapter,
    command,
    model,
    csv_adapter,
)

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")


class TestReqifParsing(unittest.TestCase):
    def test_parse_reqif_file_a(self):
        doc = reqif_parser.parse_reqif_file(os.path.join(SAMPLE_DIR, "model1.reqif"))
        csv_adapter.write_doc_to_csv(
            doc, os.path.join("/tmp", "reqifio", "model1.reqif")
        )

    def test_parse_reqif_file_b(self):
        doc = reqif_parser.parse_reqif_file(os.path.join(SAMPLE_DIR, "Sample.reqif"))
        csv_adapter.write_doc_to_csv(
            doc, os.path.join("/tmp", "reqifio", "Sample.reqif")
        )

    def test_parse_reqif_file_c(self):
        doc = reqif_parser.parse_reqif_file(os.path.join(SAMPLE_DIR, "Sample1.reqif"))
        csv_adapter.write_doc_to_csv(
            doc, os.path.join("/tmp", "reqifio", "Sample1.reqif")
        )

    def test_parse_reqif_file_d(self):
        doc = reqif_parser.parse_reqif_file(os.path.join(SAMPLE_DIR, "Sample2.reqif"))
        csv_adapter.write_doc_to_csv(
            doc, os.path.join("/tmp", "reqifio", "Sample2.reqif")
        )

    def test_parse_reqif_file_e(self):
        doc = reqif_parser.parse_reqif_file(os.path.join(SAMPLE_DIR, "Sample3.reqif"))
        csv_adapter.write_doc_to_csv(
            doc, os.path.join("/tmp", "reqifio", "Sample3.reqif")
        )


if __name__ == "__main__":
    unittest.main()
