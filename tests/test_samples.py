#!/usr/bin/env python3
"""
tests/test_samples.py

Unit tests for the reqifio package using the Python 3 standard library.
"""

import os
import tempfile
import unittest
import os.path

# Import modules from our reqifio package.
from reqifio.reqif_parser import ReqIFParser
from reqifio.reqif_writer import ReqIFWriter
from reqifio.csv_adapter import CSVAdapter

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")


# parser = ReqIFParser(self.reqif_file)
#         reqif_model = parser.parse()
class TestReqifParsing(unittest.TestCase):
    def test_parse_reqif_file_a(self):
        parser = ReqIFParser(os.path.join(SAMPLE_DIR, "model1.reqif"))
        reqif_model = parser.parse()
        adapter = CSVAdapter(os.path.join("/tmp", "reqifio", "model1.reqif"))
        adapter.write(reqif_model)

    def test_parse_reqif_file_b(self):
        parser = ReqIFParser(os.path.join(SAMPLE_DIR, "Sample.reqif"))
        reqif_model = parser.parse()
        adapter = CSVAdapter(os.path.join("/tmp", "reqifio", "Sample.reqif"))
        adapter.write(reqif_model)

    def test_parse_reqif_file_c(self):
        parser = ReqIFParser(os.path.join(SAMPLE_DIR, "Sample1.reqif"))
        reqif_model = parser.parse()
        adapter = CSVAdapter(os.path.join("/tmp", "reqifio", "Sample1.reqif"))
        adapter.write(reqif_model)

    def test_parse_reqif_file_d(self):
        parser = ReqIFParser(os.path.join(SAMPLE_DIR, "Sample2.reqif"))
        reqif_model = parser.parse()
        adapter = CSVAdapter(os.path.join("/tmp", "reqifio", "Sample2.reqif"))
        adapter.write(reqif_model)

    def test_parse_reqif_file_e(self):
        parser = ReqIFParser(os.path.join(SAMPLE_DIR, "Sample3.reqif"))
        reqif_model = parser.parse()
        adapter = CSVAdapter(os.path.join("/tmp", "reqifio", "Sample3.reqif"))
        adapter.write(reqif_model)

    # def test_parse_reqif_file_e(self):
    #     parser = ReqIFParser(os.path.join(SAMPLE_DIR, "reqif_testfile.reqif"))
    #     reqif_model = parser.parse()
    #     adapter = CSVAdapter(os.path.join("/tmp", "reqifio", "reqif_testfile.reqif"))
    #     adapter.write(reqif_model)


if __name__ == "__main__":
    unittest.main()
