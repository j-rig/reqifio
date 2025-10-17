import unittest
from copy import deepcopy
from reqifio.model import ReqIFDocument, Requirement, SpecHierarchy, SpecRelation
from reqifio.command import (
    AddRequirementCommand,
    RemoveRequirementCommand,
    UpdateRequirementCommand,
    MoveNodeCommand,
    AddNodeRelationshipCommand,
    RemoveNodeRelationshipCommand,
    CommandManager,
    search_hierarchy,
)


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.doc = ReqIFDocument(header={"TITLE": "Test Document"})
        # Create a simple requirement and hierarchy node.
        self.req = Requirement(
            req_id="REQ-001", title="Test Req", description="Test description"
        )
        self.doc.add_requirement(self.req)

        # Create SpecHierarchy items.
        self.parent_obj = Requirement(
            req_id="REQ-002", title="Parent Req", description="Parent"
        )
        self.child_obj = Requirement(
            req_id="REQ-003", title="Child Req", description="Child"
        )
        self.doc.add_requirement(self.parent_obj)
        self.doc.add_requirement(self.child_obj)
        self.parent_hier = SpecHierarchy(
            hier_id="HIER-001", object_id=self.parent_obj.req_id
        )
        self.child_hier = SpecHierarchy(
            hier_id="HIER-002", object_id=self.child_obj.req_id
        )
        self.parent_hier.children.append(self.child_hier)
        self.doc.add_spec_hierarchy(self.parent_hier)

        # Create an empty list for spec_relations if not already present.
        # (SpecRelation objects are assumed to be defined in model.)
        self.doc.spec_relations = (
            self.doc.spec_relations if hasattr(self.doc, "spec_relations") else []
        )

    def test_add_requirement_command(self):
        new_req = Requirement(req_id="REQ-004", title="New Req", description="New Desc")
        cmd = AddRequirementCommand(self.doc, new_req)
        cmd.execute()
        self.assertTrue(any(r.req_id == "REQ-004" for r in self.doc.requirements))
        cmd.undo()
        self.assertFalse(any(r.req_id == "REQ-004" for r in self.doc.requirements))

    def test_remove_requirement_command(self):
        cmd = RemoveRequirementCommand(self.doc, "REQ-001")
        cmd.execute()
        with self.assertRaises(Exception):
            self.doc.get_requirement("REQ-001")
        cmd.undo()
        restored = self.doc.get_requirement("REQ-001")
        self.assertEqual(restored.title, "Test Req")

    def test_update_requirement_command(self):
        cmd = UpdateRequirementCommand(self.doc, "REQ-001", new_title="Updated Title")
        cmd.execute()
        updated_req = self.doc.get_requirement("REQ-001")
        self.assertEqual(updated_req.title, "Updated Title")
        cmd.undo()
        original_req = self.doc.get_requirement("REQ-001")
        self.assertEqual(original_req.title, "Test Req")

    def test_move_node_command(self):
        # Assume child_hier is initially under parent_hier.
        self.assertEqual(len(self.parent_hier.children), 1)
        # Move child_hier to top level.
        cmd = MoveNodeCommand(self.doc, "HIER-002", new_parent_id=None)
        cmd.execute()
        self.assertFalse(
            any(child.hier_id == "HIER-002" for child in self.parent_hier.children)
        )
        self.assertTrue(
            any(node.hier_id == "HIER-002" for node in self.doc.spec_hierarchies)
        )
        cmd.undo()
        # Child should be reattached to parent.
        _, parent = search_hierarchy(self.doc.spec_hierarchies, "HIER-002")
        self.assertEqual(parent.hier_id, "HIER-001")

    def test_add_remove_node_relationship_command(self):
        # Create a SpecRelation linking two requirements (simulate node relationship).
        relation = SpecRelation(
            relation_id="REL-001",
            source_id="REQ-002",
            target_id="REQ-003",
            relation_type="child-of",
            properties={"info": "Test link"},
        )
        add_cmd = AddNodeRelationshipCommand(self.doc, relation)
        add_cmd.execute()
        self.assertTrue(
            any(r.relation_id == "REL-001" for r in self.doc.spec_relations)
        )
        add_cmd.undo()
        self.assertFalse(
            any(r.relation_id == "REL-001" for r in self.doc.spec_relations)
        )

        # Now test removal.
        self.doc.spec_relations.append(relation)
        remove_cmd = RemoveNodeRelationshipCommand(self.doc, "REL-001")
        remove_cmd.execute()
        self.assertFalse(
            any(r.relation_id == "REL-001" for r in self.doc.spec_relations)
        )
        remove_cmd.undo()
        self.assertTrue(
            any(r.relation_id == "REL-001" for r in self.doc.spec_relations)
        )

    def test_command_manager_undo_redo(self):
        mgr = CommandManager()
        # Execute two commands.
        add_cmd = AddRequirementCommand(
            self.doc,
            Requirement(req_id="REQ-005", title="CmdMgr Req", description="CmdMgr"),
        )
        mgr.execute_command(add_cmd)
        self.assertTrue(any(r.req_id == "REQ-005" for r in self.doc.requirements))
        mgr.undo()
        self.assertFalse(any(r.req_id == "REQ-005" for r in self.doc.requirements))
        mgr.redo()
        self.assertTrue(any(r.req_id == "REQ-005" for r in self.doc.requirements))


if __name__ == "__main__":
    unittest.main()
