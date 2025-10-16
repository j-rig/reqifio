#!/usr/bin/env python3
"""
tests/test_csv_adapter.py

Unit tests for the CSV adapter in the reqifio package.
"""

import os
import tempfile
import unittest
from reqifio import model, csv_adapter


class TestCsvAdapter(unittest.TestCase):
    def setUp(self):
        # Create a sample ReqIFDocument with all elements.
        self.doc = model.ReqIFDocument(
            header={"TITLE": "CSV Test", "CREATOR": "UnitTest"}
        )
        self.doc.add_requirement(
            model.Requirement(
                req_id="REQ-CSV-1",
                title="CSV Requirement",
                description="Testing CSV export/import.",
                attributes={"priority": "high"},
            )
        )
        self.doc.add_spec_object(
            model.SpecObject(
                spec_id="SPEC-CSV-1",
                type="TestObject",
                values={"value": "123", "unit": "ms"},
            )
        )
        self.doc.add_spec_relation(
            model.SpecRelation(
                relation_id="REL-CSV-1",
                source_id="SPEC-CSV-1",
                target_id="REQ-CSV-1",
                relation_type="satisfies",
                properties={"trace": "yes"},
            )
        )
        self.doc.spec_types["CustomType"] = "A custom type definition"

    def test_write_and_read_csv(self):
        # Write the test document to a temporary directory.
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_adapter.write_doc_to_csv(self.doc, temp_dir)

            # Ensure all expected CSV files exist.
            expected_files = [
                "header.csv",
                "requirements.csv",
                "spec_objects.csv",
                "spec_relations.csv",
                "spec_types.csv",
            ]
            for f in expected_files:
                self.assertTrue(
                    os.path.exists(os.path.join(temp_dir, f)),
                    f"{f} should exist in {temp_dir}",
                )

            # Read document back from CSV files.
            doc_from_csv = csv_adapter.read_doc_from_csv(temp_dir)

            # Verify header data.
            self.assertEqual(doc_from_csv.header.get("TITLE"), "CSV Test")
            self.assertEqual(doc_from_csv.header.get("CREATOR"), "UnitTest")

            # Verify requirements.
            self.assertEqual(len(doc_from_csv.requirements), 1)
            req = doc_from_csv.requirements[0]
            self.assertEqual(req.req_id, "REQ-CSV-1")
            self.assertEqual(req.attributes["priority"], "high")

            # Verify spec objects.
            self.assertEqual(len(doc_from_csv.spec_objects), 1)
            spec_obj = doc_from_csv.spec_objects[0]
            self.assertEqual(spec_obj.spec_id, "SPEC-CSV-1")
            self.assertEqual(spec_obj.values["unit"], "ms")

            # Verify spec relations.
            self.assertEqual(len(doc_from_csv.spec_relations), 1)
            spec_rel = doc_from_csv.spec_relations[0]
            self.assertEqual(spec_rel.relation_id, "REL-CSV-1")
            self.assertEqual(spec_rel.properties["trace"], "yes")

            # Verify spec types.
            self.assertIn("CustomType", doc_from_csv.spec_types)
            self.assertEqual(
                doc_from_csv.spec_types["CustomType"], "A custom type definition"
            )


if __name__ == "__main__":
    unittest.main()
