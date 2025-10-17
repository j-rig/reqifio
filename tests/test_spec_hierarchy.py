import unittest
from reqifio.model import ReqIFDocument, SpecObject, SpecHierarchy


class TestSpecHierarchy(unittest.TestCase):
    def test_create_spec_hierarchy(self):
        # Create a new ReqIF document.
        doc = ReqIFDocument(header={"TITLE": "SpecHierarchy Test"})

        # Create SpecObjects.
        parent_obj = SpecObject(
            spec_id="OBJ-001", type="Requirement", values={"name": "Parent Object"}
        )
        child_obj = SpecObject(
            spec_id="OBJ-002", type="Requirement", values={"name": "Child Object"}
        )

        # Add SpecObjects to the document.
        doc.add_spec_object(parent_obj)
        doc.add_spec_object(child_obj)

        # Create SpecHierarchy items.
        parent_hier = SpecHierarchy(hier_id="HIER-001", object_id=parent_obj.spec_id)
        child_hier = SpecHierarchy(hier_id="HIER-002", object_id=child_obj.spec_id)

        # Nest child under parent.
        parent_hier.children.append(child_hier)
        doc.add_spec_hierarchy(parent_hier)

        # Assertions to verify the hierarchy.
        self.assertEqual(
            len(doc.spec_hierarchies),
            1,
            "There should be one top-level hierarchy node.",
        )
        self.assertEqual(
            doc.spec_hierarchies[0].hier_id,
            "HIER-001",
            "The top-level node should have ID 'HIER-001'.",
        )

        # Verify that the parent has one child.
        self.assertEqual(
            len(doc.spec_hierarchies[0].children),
            1,
            "Parent should have one child node.",
        )
        self.assertEqual(
            doc.spec_hierarchies[0].children[0].hier_id,
            "HIER-002",
            "Child node should have ID 'HIER-002'.",
        )
        self.assertEqual(
            doc.spec_hierarchies[0].children[0].object_id,
            "OBJ-002",
            "Child node should reference 'OBJ-002'.",
        )


if __name__ == "__main__":
    unittest.main()
