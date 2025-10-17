import unittest
from reqifio.model import ReqIFDocument, SpecRelation, SpecObject


class TestSpecRelations(unittest.TestCase):
    def setUp(self):
        self.doc = ReqIFDocument(header={"TITLE": "Relation Test"})
        # Create two SpecObjects for establishing a relation
        self.source = SpecObject(
            spec_id="OBJ-001", type="Requirement", values={"desc": "Source Object"}
        )
        self.target = SpecObject(
            spec_id="OBJ-002", type="Requirement", values={"desc": "Target Object"}
        )
        self.doc.add_spec_object(self.source)
        self.doc.add_spec_object(self.target)

    def test_add_relation(self):
        # Create and add a relation linking source and target
        relation = SpecRelation(
            relation_id="REL-001",
            source_id=self.source.spec_id,
            target_id=self.target.spec_id,
            relation_type="satisfies",
            properties={"detail": "Source satisfies Target"},
        )
        self.doc.add_spec_relation(relation)

        # Verify the relation has been added correctly
        self.assertEqual(len(self.doc.spec_relations), 1)
        added_relation = self.doc.spec_relations[0]
        self.assertEqual(added_relation.relation_id, "REL-001")
        self.assertEqual(added_relation.source_id, "OBJ-001")
        self.assertEqual(added_relation.target_id, "OBJ-002")
        self.assertEqual(added_relation.relation_type, "satisfies")
        self.assertEqual(added_relation.properties["detail"], "Source satisfies Target")

    def test_remove_relation(self):
        # Add a relation and then remove it
        relation = SpecRelation(
            relation_id="REL-002",
            source_id=self.source.spec_id,
            target_id=self.target.spec_id,
            relation_type="verifies",
            properties={"detail": "Source verifies Target"},
        )
        self.doc.add_spec_relation(relation)
        self.doc.remove_spec_relation("REL-002")

        # Verify that the relation list is empty after removal
        self.assertEqual(len(self.doc.spec_relations), 0)


if __name__ == "__main__":
    unittest.main()
