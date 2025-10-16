"""
reqifio/reqif_writer.py

Writes a ReqIFDocument (with extended schema elements) back to an XML file.
It constructs the XML tree for header, CORE-CONTENT with REQUIREMENTS, SPEC-OBJECTS,
SPEC-RELATIONS, and SPEC-TYPES.
"""

import xml.etree.ElementTree as ET
from .model import ReqIFDocument, Requirement, SpecObject, SpecRelation


def write_reqif_file(doc: ReqIFDocument, file_path: str):
    root = ET.Element("REQ-IF")

    # Write header
    header_elem = ET.SubElement(root, "REQ-IF-HEADER")
    for key, value in doc.header.items():
        elem = ET.SubElement(header_elem, key)
        elem.text = str(value)

    # CORE-CONTENT
    core_content = ET.SubElement(root, "CORE-CONTENT")

    # Write Requirements
    reqs_elem = ET.SubElement(core_content, "REQUIREMENTS")
    for req in doc.requirements:
        req_elem = ET.SubElement(reqs_elem, "REQ-IF-REQUISITE")
        id_elem = ET.SubElement(req_elem, "ID")
        id_elem.text = req.req_id
        title_elem = ET.SubElement(req_elem, "TITLE")
        title_elem.text = req.title
        desc_elem = ET.SubElement(req_elem, "DESCRIPTION")
        desc_elem.text = req.description
        # Additional attributes can be added if needed.

    # Write SpecObjects
    spec_objs_elem = ET.SubElement(core_content, "SPEC-OBJECTS")
    for obj in doc.spec_objects:
        obj_elem = ET.SubElement(spec_objs_elem, "SPEC-OBJECT")
        id_elem = ET.SubElement(obj_elem, "ID")
        id_elem.text = obj.spec_id
        type_elem = ET.SubElement(obj_elem, "TYPE")
        type_elem.text = obj.type
        # Write additional values
        if obj.values:
            values_elem = ET.SubElement(obj_elem, "VALUES")
            for key, value in obj.values.items():
                val_elem = ET.SubElement(values_elem, key)
                val_elem.text = str(value)

    # Write SpecRelations
    spec_rels_elem = ET.SubElement(core_content, "SPEC-RELATIONS")
    for rel in doc.spec_relations:
        rel_elem = ET.SubElement(spec_rels_elem, "SPEC-RELATION")
        id_elem = ET.SubElement(rel_elem, "ID")
        id_elem.text = rel.relation_id
        source_elem = ET.SubElement(rel_elem, "SOURCE-ID")
        source_elem.text = rel.source_id
        target_elem = ET.SubElement(rel_elem, "TARGET-ID")
        target_elem.text = rel.target_id
        type_elem = ET.SubElement(rel_elem, "RELATION-TYPE")
        type_elem.text = rel.relation_type
        if rel.properties:
            props_elem = ET.SubElement(rel_elem, "PROPERTIES")
            for key, value in rel.properties.items():
                prop_elem = ET.SubElement(props_elem, key)
                prop_elem.text = str(value)

    # Write SpecTypes (simplified)
    spec_types_elem = ET.SubElement(core_content, "SPEC-TYPES")
    for type_key, type_value in doc.spec_types.items():
        type_elem = ET.SubElement(spec_types_elem, type_key)
        type_elem.text = str(type_value)

    tree = ET.ElementTree(root)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
