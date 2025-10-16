"""
reqifio/command.py

Implements the Command Pattern for CRUD operations on a ReqIFDocument.
Commands for adding, removing, and updating requirements are provided.
Undo/redo actions are managed via a CommandManager.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from .model import ReqIFDocument, Requirement


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
