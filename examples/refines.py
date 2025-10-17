#!/usr/bin/env python3
"""
Example: Demonstrating a "refines" relationship in a ReqIF Document.

In this example, we create two spec objects:
- A higher-level abstract requirement.
- A more detailed refined requirement.

We then create a SpecRelation with type "refines" to show that the refined requirement refines the abstract one.
"""

from reqifio import model

# Create a ReqIF document with a header.
doc = model.ReqIFDocument(header={"TITLE": "Refines Relationship Example"})

# Create an abstract (higher-level) requirement spec object.
abstract_req = model.SpecObject(
    spec_id="SPEC-100",
    type="Requirement",
    values={"description": "Abstract requirement that defines the high-level needs."},
)

# Create a refined (detailed) requirement spec object.
refined_req = model.SpecObject(
    spec_id="SPEC-101",
    type="Requirement",
    values={
        "description": "Refined requirement with detailed technical specifications."
    },
)

# Add spec objects to the document.
doc.add_spec_object(abstract_req)
doc.add_spec_object(refined_req)

# Create a spec relation representing the "refines" relationship.
refines_relation = model.SpecRelation(
    relation_id="REL-100",
    source_id=refined_req.spec_id,  # The refined element.
    target_id=abstract_req.spec_id,  # The abstract element.
    relation_type="refines",
    properties={},
)

# Add the relation to the document.
doc.add_spec_relation(refines_relation)

# Output the relationship.
print("Spec Objects:")
for obj in doc.spec_objects:
    print(f"  {obj.spec_id}: {obj.values}")
print("Spec Relations:")
for rel in doc.spec_relations:
    print(
        f"  {rel.relation_id}: {rel.source_id} -> {rel.target_id} (Type: {rel.relation_type})"
    )
