#!/usr/bin/env python3
"""
Example: Representing a Parent–Child Relationship in a ReqIF Document

This example creates a ReqIF document, adds two spec objects (a parent and a child),
and then uses a spec relation of type "child-of" to indicate that one is the child of the other.
"""

from reqifio import model

# Create a ReqIF document with a header.
doc = model.ReqIFDocument(header={"TITLE": "Parent-Child Example"})

# Create a parent spec object.
parent = model.SpecObject(
    spec_id="SPEC-001",
    type="Requirement",
    values={"description": "This is the parent requirement."},
)

# Create a child spec object.
child = model.SpecObject(
    spec_id="SPEC-002",
    type="Requirement",
    values={"description": "This is the child requirement."},
)

# Add the spec objects to the document.
doc.add_spec_object(parent)
doc.add_spec_object(child)

# Create a spec relation to represent the parent–child relationship.
# Here, the child object's ID is the source and the parent object's ID is the target.
relation = model.SpecRelation(
    relation_id="REL-001",
    source_id=child.spec_id,
    target_id=parent.spec_id,
    relation_type="child-of",  # Industry-standard or custom relation type.
    properties={},
)

# Add the relation to the document.
doc.add_spec_relation(relation)

# Demonstrate the stored hierarchy.
print("Document Header:", doc.header)
print("Spec Objects:")
for obj in doc.spec_objects:
    print(f"  {obj.spec_id}: {obj.values}")
print("Spec Relations:")
for rel in doc.spec_relations:
    print(
        f"  {rel.relation_id}: {rel.source_id} -> {rel.target_id} (Type: {rel.relation_type})"
    )
