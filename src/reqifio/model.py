"""
reqifio/model.py

Defines the internal data model for a ReqIF document.
The complete schema includes:
 - Header
 - Requirements
 - SpecObjects (detailed system elements)
 - SpecRelations (relationships between SpecObjects)
 - SpecTypes (definition of types for SpecObjects and Requirements)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Requirement:
    req_id: str
    title: str
    description: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpecObject:
    spec_id: str
    type: str
    values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpecRelation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReqIFDocument:
    header: Dict[str, Any] = field(default_factory=dict)
    requirements: List[Requirement] = field(default_factory=list)
    spec_objects: List[SpecObject] = field(default_factory=list)
    spec_relations: List[SpecRelation] = field(default_factory=list)
    spec_types: Dict[str, Any] = field(
        default_factory=dict
    )  # Simplified spec types storage

    def add_requirement(self, requirement: Requirement):
        self.requirements.append(requirement)

    def remove_requirement(self, req_id: str):
        self.requirements = [r for r in self.requirements if r.req_id != req_id]

    def get_requirement(self, req_id: str) -> Requirement:
        for req in self.requirements:
            if req.req_id == req_id:
                return req
        raise KeyError(f"Requirement with id {req_id} not found.")

    def add_spec_object(self, spec_obj: SpecObject):
        self.spec_objects.append(spec_obj)

    def remove_spec_object(self, spec_id: str):
        self.spec_objects = [o for o in self.spec_objects if o.spec_id != spec_id]

    def get_spec_object(self, spec_id: str) -> SpecObject:
        for obj in self.spec_objects:
            if obj.spec_id == spec_id:
                return obj
        raise KeyError(f"SpecObject with id {spec_id} not found.")

    def add_spec_relation(self, spec_rel: SpecRelation):
        self.spec_relations.append(spec_rel)

    def remove_spec_relation(self, relation_id: str):
        self.spec_relations = [
            r for r in self.spec_relations if r.relation_id != relation_id
        ]

    def get_spec_relation(self, relation_id: str) -> SpecRelation:
        for rel in self.spec_relations:
            if rel.relation_id == relation_id:
                return rel
        raise KeyError(f"SpecRelation with id {relation_id} not found.")
