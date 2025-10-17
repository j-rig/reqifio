"""
reqifio/command.py

Implements the Command Pattern for CRUD operations on a ReqIFDocument.
Commands for adding, removing, and updating requirements are provided.
Undo/redo actions are managed via a CommandManager.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from .model import ReqIFDocument, Requirement, SpecHierarchy, SpecRelation


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class AddRequirementCommand(Command):
    def __init__(self, doc: ReqIFDocument, requirement: Requirement):
        self.doc = doc
        self.requirement = requirement

    def execute(self):
        self.doc.add_requirement(self.requirement)

    def undo(self):
        self.doc.remove_requirement(self.requirement.req_id)


class RemoveRequirementCommand(Command):
    def __init__(self, doc: ReqIFDocument, req_id: str):
        self.doc = doc
        self.req_id = req_id
        self.removed_requirement = None

    def execute(self):
        try:
            self.removed_requirement = deepcopy(self.doc.get_requirement(self.req_id))
            self.doc.remove_requirement(self.req_id)
        except KeyError:
            raise Exception(f"Requirement with id {self.req_id} not found.")

    def undo(self):
        if self.removed_requirement:
            self.doc.add_requirement(self.removed_requirement)


class UpdateRequirementCommand(Command):
    def __init__(
        self,
        doc: ReqIFDocument,
        req_id: str,
        new_title: str = None,
        new_description: str = None,
    ):
        self.doc = doc
        self.req_id = req_id
        self.new_title = new_title
        self.new_description = new_description
        self.old_requirement = None

    def execute(self):
        try:
            req = self.doc.get_requirement(self.req_id)
            self.old_requirement = deepcopy(req)
            if self.new_title is not None:
                req.title = self.new_title
            if self.new_description is not None:
                req.description = self.new_description
        except KeyError:
            raise Exception(f"Requirement with id {self.req_id} not found.")

    def undo(self):
        if self.old_requirement:
            self.doc.remove_requirement(self.req_id)
            self.doc.add_requirement(self.old_requirement)


def search_hierarchy(hierarchy_list, node_id, parent=None):
    """
    Recursively searches for a SpecHierarchy node by node_id.
    Returns a tuple (node, parent) if found; otherwise (None, None).
    """
    for node in hierarchy_list:
        if node.hier_id == node_id:
            return node, parent
        found, par = search_hierarchy(node.children, node_id, node)
        if found:
            return found, par
    return None, None


class MoveNodeCommand(Command):
    def __init__(self, document, node_id, new_parent_id):
        """
        Args:
            document: The ReqIF document that holds the SpecHierarchy.
            node_id: The hierarchy node identifier to move.
            new_parent_id: The identifier of the new parent node (None for top-level).
        """
        self.document = document
        self.node_id = node_id
        self.new_parent_id = new_parent_id
        self.old_parent = None
        self.node = None

    def execute(self):
        # Find the node and its current parent.
        self.node, self.old_parent = search_hierarchy(
            self.document.spec_hierarchies, self.node_id
        )
        if not self.node:
            raise ValueError(f"Node {self.node_id} not found.")

        # Remove the node from its old parent's children list or from top-level.
        if self.old_parent:
            self.old_parent.children = [
                child
                for child in self.old_parent.children
                if child.hier_id != self.node_id
            ]
        else:
            self.document.spec_hierarchies = [
                n for n in self.document.spec_hierarchies if n.hier_id != self.node_id
            ]

        # Attach the node to the new parent (if provided) or as top-level.
        if self.new_parent_id:
            new_parent, _ = search_hierarchy(
                self.document.spec_hierarchies, self.new_parent_id
            )
            if not new_parent:
                raise ValueError(f"New parent {self.new_parent_id} not found.")
            new_parent.children.append(self.node)
        else:
            self.document.spec_hierarchies.append(self.node)

    def undo(self):
        # Remove from current location.
        if self.new_parent_id:
            new_parent, _ = search_hierarchy(
                self.document.spec_hierarchies, self.new_parent_id
            )
            if new_parent:
                new_parent.children = [
                    child
                    for child in new_parent.children
                    if child.hier_id != self.node_id
                ]
        else:
            self.document.spec_hierarchies = [
                n for n in self.document.spec_hierarchies if n.hier_id != self.node_id
            ]

        # Reattach the node to its original parent (or as top-level if none).
        if self.old_parent:
            self.old_parent.children.append(self.node)
        else:
            self.document.spec_hierarchies.append(self.node)


class AddNodeRelationshipCommand(Command):
    def __init__(self, document, relation: SpecRelation):
        """
        Args:
            document: The ReqIF document containing node relationships.
            relation: The SpecRelation connecting two node identifiers.
        """
        self.document = document
        self.relation = relation
        self.executed = False

    def execute(self):
        self.document.spec_relations.append(self.relation)
        self.executed = True

    def undo(self):
        if self.executed:
            self.document.spec_relations = [
                r
                for r in self.document.spec_relations
                if r.relation_id != self.relation.relation_id
            ]


class RemoveNodeRelationshipCommand(Command):
    def __init__(self, document, relation_id: str):
        """
        Args:
            document: The ReqIF document containing node relationships.
            relation_id: The identifier of the SpecRelation to remove.
        """
        self.document = document
        self.relation_id = relation_id
        self.removed_relation = None

    def execute(self):
        for r in self.document.spec_relations:
            if r.relation_id == self.relation_id:
                self.removed_relation = r
                break
        if not self.removed_relation:
            raise ValueError(f"Relationship {self.relation_id} not found.")
        self.document.spec_relations = [
            r for r in self.document.spec_relations if r.relation_id != self.relation_id
        ]

    def undo(self):
        if self.removed_relation:
            self.document.spec_relations.append(self.removed_relation)


class CommandManager:
    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def execute_command(self, command: Command):
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            raise Exception("No commands to undo.")
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self):
        if not self._redo_stack:
            raise Exception("No commands to redo.")
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
