"""
reqifio/csv_adapter.py

This module provides functions to export and import a full ReqIFDocument
to/from CSV files using Python's standard library.

It writes separate CSV files for:
  - Header (header.csv)
  - Requirements (requirements.csv)
  - SpecObjects (spec_objects.csv)
  - SpecRelations (spec_relations.csv)
  - SpecTypes (spec_types.csv)

The adapter serializes dictionary fields using repr() for simplicity.
"""

import csv
import os
from .model import ReqIFDocument, Requirement, SpecObject, SpecRelation


def write_doc_to_csv(doc: ReqIFDocument, folder_path: str):
    """
    Writes the provided ReqIFDocument into CSV files in the specified folder.

    Args:
        doc: The ReqIFDocument to export.
        folder_path: Directory where CSV files will be written.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Write header to header.csv (key, value).
    header_file = os.path.join(folder_path, "header.csv")
    with open(header_file, "w", newline="", encoding="utf-8") as hf:
        writer = csv.writer(hf)
        writer.writerow(["key", "value"])
        for key, value in doc.header.items():
            writer.writerow([key, value])

    # Write requirements to requirements.csv.
    req_file = os.path.join(folder_path, "requirements.csv")
    with open(req_file, "w", newline="", encoding="utf-8") as rf:
        writer = csv.writer(rf)
        writer.writerow(["req_id", "title", "description", "attributes"])
        for req in doc.requirements:
            writer.writerow(
                [req.req_id, req.title, req.description, repr(req.attributes)]
            )

    # Write spec_objects to spec_objects.csv.
    spec_obj_file = os.path.join(folder_path, "spec_objects.csv")
    with open(spec_obj_file, "w", newline="", encoding="utf-8") as sof:
        writer = csv.writer(sof)
        writer.writerow(["spec_id", "type", "values"])
        for obj in doc.spec_objects:
            writer.writerow([obj.spec_id, obj.type, repr(obj.values)])

    # Write spec_relations to spec_relations.csv.
    spec_rel_file = os.path.join(folder_path, "spec_relations.csv")
    with open(spec_rel_file, "w", newline="", encoding="utf-8") as srf:
        writer = csv.writer(srf)
        writer.writerow(
            ["relation_id", "source_id", "target_id", "relation_type", "properties"]
        )
        for rel in doc.spec_relations:
            writer.writerow(
                [
                    rel.relation_id,
                    rel.source_id,
                    rel.target_id,
                    rel.relation_type,
                    repr(rel.properties),
                ]
            )

    # Write spec_types to spec_types.csv.
    spec_types_file = os.path.join(folder_path, "spec_types.csv")
    with open(spec_types_file, "w", newline="", encoding="utf-8") as stf:
        writer = csv.writer(stf)
        writer.writerow(["type_key", "type_value"])
        for key, value in doc.spec_types.items():
            writer.writerow([key, value])


def read_doc_from_csv(folder_path: str) -> ReqIFDocument:
    """
    Reads a ReqIFDocument from CSV files in the specified folder.

    The function expects files named:
      header.csv, requirements.csv, spec_objects.csv,
      spec_relations.csv, spec_types.csv.

    Args:
        folder_path: Directory containing the CSV files.

    Returns:
        A populated ReqIFDocument instance.
    """
    doc = ReqIFDocument()

    # Read header.
    header_file = os.path.join(folder_path, "header.csv")
    with open(header_file, "r", newline="", encoding="utf-8") as hf:
        reader = csv.DictReader(hf)
        for row in reader:
            doc.header[row["key"]] = row["value"]

    # Read requirements.
    req_file = os.path.join(folder_path, "requirements.csv")
    with open(req_file, "r", newline="", encoding="utf-8") as rf:
        reader = csv.DictReader(rf)
        for row in reader:
            req = Requirement(
                req_id=row["req_id"],
                title=row["title"],
                description=row["description"],
                attributes=eval(
                    row["attributes"]
                ),  # Note: using eval() for demo purposes.
            )
            doc.add_requirement(req)

    # Read spec_objects.
    spec_obj_file = os.path.join(folder_path, "spec_objects.csv")
    with open(spec_obj_file, "r", newline="", encoding="utf-8") as sof:
        reader = csv.DictReader(sof)
        for row in reader:
            obj = SpecObject(
                spec_id=row["spec_id"], type=row["type"], values=eval(row["values"])
            )
            doc.add_spec_object(obj)

    # Read spec_relations.
    spec_rel_file = os.path.join(folder_path, "spec_relations.csv")
    with open(spec_rel_file, "r", newline="", encoding="utf-8") as srf:
        reader = csv.DictReader(srf)
        for row in reader:
            rel = SpecRelation(
                relation_id=row["relation_id"],
                source_id=row["source_id"],
                target_id=row["target_id"],
                relation_type=row["relation_type"],
                properties=eval(row["properties"]),
            )
            doc.add_spec_relation(rel)

    # Read spec_types.
    spec_types_file = os.path.join(folder_path, "spec_types.csv")
    with open(spec_types_file, "r", newline="", encoding="utf-8") as stf:
        reader = csv.DictReader(stf)
        for row in reader:
            doc.spec_types[row["type_key"]] = row["type_value"]

    return doc
