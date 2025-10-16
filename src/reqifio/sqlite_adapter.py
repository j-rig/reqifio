"""
reqifio/sqlite_adapter.py

Stores and retrieves the full ReqIF schema in an SQLite database using the sqlite3 library.
Added tables include those for header, requirements, spec_objects, spec_relations, and spec_types.
"""

import sqlite3
from .model import ReqIFDocument, Requirement, SpecObject, SpecRelation


def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS header (
            key TEXT PRIMARY KEY,
            the_value TEXT
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS requirements (
            req_id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS spec_objects (
            spec_id TEXT PRIMARY KEY,
            type TEXT,
            the_values TEXT
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS spec_relations (
            relation_id TEXT PRIMARY KEY,
            source_id TEXT,
            target_id TEXT,
            relation_type TEXT,
            properties TEXT
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS spec_types (
            type_key TEXT PRIMARY KEY,
            type_value TEXT
        )
    """
    )
    conn.commit()


def write_doc_to_db(doc: ReqIFDocument, db_path: str):
    conn = sqlite3.connect(db_path)
    init_db(conn)
    cur = conn.cursor()

    # Store header
    cur.execute("DELETE FROM header")
    for key, value in doc.header.items():
        cur.execute(
            "INSERT INTO header (key, the_value) VALUES (?, ?)", (key, str(value))
        )

    # Store requirements
    cur.execute("DELETE FROM requirements")
    for req in doc.requirements:
        cur.execute(
            "INSERT INTO requirements (req_id, title, description) VALUES (?, ?, ?)",
            (req.req_id, req.title, req.description),
        )

    # Store spec_objects
    cur.execute("DELETE FROM spec_objects")
    for obj in doc.spec_objects:
        cur.execute(
            "INSERT INTO spec_objects (spec_id, type, the_values) VALUES (?, ?, ?)",
            (obj.spec_id, obj.type, repr(obj.values)),
        )

    # Store spec_relations
    cur.execute("DELETE FROM spec_relations")
    for rel in doc.spec_relations:
        cur.execute(
            "INSERT INTO spec_relations (relation_id, source_id, target_id, relation_type, properties) VALUES (?, ?, ?, ?, ?)",
            (
                rel.relation_id,
                rel.source_id,
                rel.target_id,
                rel.relation_type,
                repr(rel.properties),
            ),
        )

    # Store spec_types
    cur.execute("DELETE FROM spec_types")
    for key, value in doc.spec_types.items():
        cur.execute(
            "INSERT INTO spec_types (type_key, type_value) VALUES (?, ?)",
            (key, str(value)),
        )

    conn.commit()
    conn.close()


def read_doc_from_db(db_path: str) -> ReqIFDocument:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    doc = ReqIFDocument()

    # Read header
    cur.execute("SELECT key, the_value FROM header")
    for key, value in cur.fetchall():
        doc.header[key] = value

    # Read requirements
    cur.execute("SELECT req_id, title, description FROM requirements")
    for req_id, title, description in cur.fetchall():
        doc.add_requirement(
            Requirement(req_id=req_id, title=title, description=description)
        )

    # Read spec_objects
    cur.execute("SELECT spec_id, type, the_values FROM spec_objects")
    for spec_id, type_text, values_str in cur.fetchall():
        # In a real implementation, use json.loads for safe serialization.
        values = eval(values_str)
        doc.add_spec_object(SpecObject(spec_id=spec_id, type=type_text, values=values))

    # Read spec_relations
    cur.execute(
        "SELECT relation_id, source_id, target_id, relation_type, properties FROM spec_relations"
    )
    for relation_id, source_id, target_id, relation_type, props_str in cur.fetchall():
        properties = eval(props_str)
        doc.add_spec_relation(
            SpecRelation(
                relation_id=relation_id,
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                properties=properties,
            )
        )

    # Read spec_types
    cur.execute("SELECT type_key, type_value FROM spec_types")
    for type_key, type_value in cur.fetchall():
        doc.spec_types[type_key] = type_value

    conn.close()
    return doc
