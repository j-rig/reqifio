"""
reqifio/reqif_parser.py

Parses a ReqIF XML file into the internal model (ReqIFDocument).
Supports extended sections such as CORE-CONTENT which includes SPEC-OBJECTS, SPEC-RELATIONS,
and SPEC-TYPES as per a fuller subset of the ReqIF schema.
"""

import xml.etree.ElementTree as ET
from .model import ReqIFDocument, Requirement, SpecObject, SpecRelation


def parse_reqif_file(file_path: str) -> ReqIFDocument:
    tree = ET.parse(file_path)
    root = tree.getroot()

    doc = ReqIFDocument()

    # Parse header (assumed under REQ-IF-HEADER)
    header_elem = root.find("REQ-IF-HEADER")
    if header_elem is not None:
        for child in header_elem:
            doc.header[child.tag] = child.text

    # Parse core content (SPEC-OBJECTS, SPEC-RELATIONS, SPEC-TYPES)
    core_content = root.find("CORE-CONTENT")
    if core_content is not None:
        # Parse Requirements (alternative representation)
        reqs_elem = core_content.find("REQUIREMENTS")
        if reqs_elem is not None:
            for req_elem in reqs_elem.findall("REQ-IF-REQUISITE"):
                req_id = (
                    req_elem.find("ID").text
                    if req_elem.find("ID") is not None
                    else "unknown"
                )
                title = (
                    req_elem.find("TITLE").text
                    if req_elem.find("TITLE") is not None
                    else ""
                )
                description = (
                    req_elem.find("DESCRIPTION").text
                    if req_elem.find("DESCRIPTION") is not None
                    else ""
                )
                req = Requirement(req_id=req_id, title=title, description=description)
                doc.add_requirement(req)

        # Parse SpecObjects
        spec_objs_elem = core_content.find("SPEC-OBJECTS")
        if spec_objs_elem is not None:
            for obj_elem in spec_objs_elem.findall("SPEC-OBJECT"):
                spec_id = (
                    obj_elem.find("ID").text
                    if obj_elem.find("ID") is not None
                    else "unknown"
                )
                type_text = (
                    obj_elem.find("TYPE").text
                    if obj_elem.find("TYPE") is not None
                    else ""
                )
                # Parse additional values (if any)
                values = {}
                values_elem = obj_elem.find("VALUES")
                if values_elem is not None:
                    for val in values_elem:
                        values[val.tag] = val.text
                spec_obj = SpecObject(spec_id=spec_id, type=type_text, values=values)
                doc.add_spec_object(spec_obj)

        # Parse SpecRelations
        spec_rels_elem = core_content.find("SPEC-RELATIONS")
        if spec_rels_elem is not None:
            for rel_elem in spec_rels_elem.findall("SPEC-RELATION"):
                relation_id = (
                    rel_elem.find("ID").text
                    if rel_elem.find("ID") is not None
                    else "unknown"
                )
                source_id = (
                    rel_elem.find("SOURCE-ID").text
                    if rel_elem.find("SOURCE-ID") is not None
                    else ""
                )
                target_id = (
                    rel_elem.find("TARGET-ID").text
                    if rel_elem.find("TARGET-ID") is not None
                    else ""
                )
                relation_type = (
                    rel_elem.find("RELATION-TYPE").text
                    if rel_elem.find("RELATION-TYPE") is not None
                    else ""
                )
                properties = {}
                props_elem = rel_elem.find("PROPERTIES")
                if props_elem is not None:
                    for prop in props_elem:
                        properties[prop.tag] = prop.text
                spec_rel = SpecRelation(
                    relation_id=relation_id,
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=relation_type,
                    properties=properties,
                )
                doc.add_spec_relation(spec_rel)

        # Parse SpecTypes (a simplified representation)
        spec_types_elem = core_content.find("SPEC-TYPES")
        if spec_types_elem is not None:
            for type_elem in spec_types_elem:
                # Using tag name as key and its text value for demonstration.
                doc.spec_types[type_elem.tag] = type_elem.text

    # Fallback for legacy files: If CORE-CONTENT not found, try top-level REQUIREMENTS.
    if not doc.requirements:
        requirements_elem = root.find("REQUIREMENTS")
        if requirements_elem is not None:
            for req_elem in requirements_elem.findall("REQ-IF-REQUISITE"):
                req_id = (
                    req_elem.find("ID").text
                    if req_elem.find("ID") is not None
                    else "unknown"
                )
                title = (
                    req_elem.find("TITLE").text
                    if req_elem.find("TITLE") is not None
                    else ""
                )
                description = (
                    req_elem.find("DESCRIPTION").text
                    if req_elem.find("DESCRIPTION") is not None
                    else ""
                )
                req = Requirement(req_id=req_id, title=title, description=description)
                doc.add_requirement(req)

    return doc
