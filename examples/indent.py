#!/usr/bin/env python3
"""
Example: Creating a SpecHierarchy in a ReqIF Document.
"""

from reqif_lib import model

# Create a new ReqIF document with a header.
doc = model.ReqIFDocument(header={"TITLE": "SpecHierarchy Example"})

# Create two spec objects.
parent_obj = model.SpecObject(
    spec_id="OBJ-001",
    type="Requirement",
    values={"description": "This is the parent object."},
)
child_obj = model.SpecObject(
    spec_id="OBJ-002",
    type="Requirement",
    values={"description": "This is the child object."},
)

# Add objects to the document.
doc.add_spec_object(parent_obj)
doc.add_spec_object(child_obj)

# Build the SpecHierarchy.
parent_hier = model.SpecHierarchy(hier_id="HIER-001", object_id=parent_obj.spec_id)
child_hier = model.SpecHierarchy(hier_id="HIER-002", object_id=child_obj.spec_id)

# Link the hierarchy: add child_hier as a child of parent_hier.
parent_hier.children.append(child_hier)

# Add the top-level hierarchy to the document.
doc.add_spec_hierarchy(parent_hier)


# Function to recursively print the hierarchy.
def print_hierarchy(hier, level=0):
    indent = " " * (level * 2)
    print(f"{indent}Hierarchy ID: {hier.hier_id}, Object ID: {hier.object_id}")
    for child in hier.children:
        print_hierarchy(child, level + 1)


# Print all hierarchy items in the document.
for hier in doc.spec_hierarchies:
    print_hierarchy(hier)
