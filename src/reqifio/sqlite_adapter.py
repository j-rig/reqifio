"""
sqlite_adapter.py

This module defines the SQLiteAdapter class which writes the complete ReqIF data model
to a SQLite database and reads it back. The schema is created in separate tables for
the header, each data type, spec objects and specifications (with hierarchies and attributes).

Design:
- The adapter creates a new SQLite database (or uses an existing one) with a simple schema.
- Writing: The write() method inserts (or REPLACE) rows for each part of the model.
- Reading: The read() method reassembles the model by loading all tables and creating
  instances of the model classes.
"""

import sqlite3
from datetime import datetime
from .model import (
    ReqIF,
    ReqIFHeader,
    CoreContent,
    ReqIFContent,
    DataTypes,
    DataTypeDefinitionXHTML,
    DataTypeDefinitionEnumeration,
    EnumValue,
    EmbeddedValue,
    DataTypeDefinitionBoolean,
    DataTypeDefinitionDate,
    DataTypeDefinitionInteger,
    DataTypeDefinitionReal,
    DataTypeDefinitionString,
    SpecObject,
    AttributeValue,
    Specification,
    SpecHierarchy,
)


class SQLiteAdapter:
    def __init__(self, db_path: str):
        """
        Initialize the adapter with a path to the SQLite database.
        """
        self.db_path = db_path

    def create_schema(self):
        """
        Create the SQLite database schema with tables for each entity in the data model.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # ReqIF header.
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS reqif_header (
                identifier TEXT PRIMARY KEY,
                creation_time TEXT,
                repository_id TEXT,
                reqif_tool_id TEXT,
                reqif_version TEXT,
                source_tool_id TEXT,
                title TEXT
            )
        """
        )
        # DataTypes tables.
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS datatype_xhtml (
                identifier TEXT PRIMARY KEY,
                last_change TEXT,
                long_name TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS datatype_enumeration (
                identifier TEXT PRIMARY KEY,
                last_change TEXT,
                long_name TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS enum_value (
                identifier TEXT PRIMARY KEY,
                enumeration_id TEXT,
                last_change TEXT,
                long_name TEXT,
                embedded_key TEXT,
                embedded_other_content TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS datatype_boolean (
                identifier TEXT PRIMARY KEY,
                long_name TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS datatype_date (
                identifier TEXT PRIMARY KEY,
                long_name TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS datatype_integer (
                identifier TEXT PRIMARY KEY,
                long_name TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS datatype_real (
                identifier TEXT PRIMARY KEY,
                long_name TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS datatype_string (
                identifier TEXT PRIMARY KEY,
                long_name TEXT
            )
        """
        )
        # Spec Objects tables.
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS spec_object (
                identifier TEXT PRIMARY KEY,
                last_change TEXT,
                long_name TEXT,
                type_ref TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS spec_object_attribute (
                spec_object_id TEXT,
                definition_ref TEXT,
                value TEXT
            )
        """
        )
        # Specifications tables.
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS specification (
                identifier TEXT PRIMARY KEY,
                last_change TEXT,
                long_name TEXT,
                type_ref TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS spec_hierarchy (
                identifier TEXT PRIMARY KEY,
                specification_id TEXT,
                last_change TEXT,
                long_name TEXT,
                is_editable INTEGER,
                object_ref TEXT
            )
        """
        )
        # Tool extensions stored as a single row.
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_extensions (
                id INTEGER PRIMARY KEY,
                content TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def write(self, reqif: ReqIF):
        """
        Write the complete ReqIF data model to the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Write ReqIF header.
        c.execute(
            """
            INSERT OR REPLACE INTO reqif_header 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                reqif.header.identifier,
                reqif.header.creation_time.isoformat(),
                reqif.header.repository_id,
                reqif.header.reqif_tool_id,
                reqif.header.reqif_version,
                reqif.header.source_tool_id,
                reqif.header.title,
            ),
        )
        dt = reqif.core_content.reqif_content.data_types
        # Write DataType XHTML.
        if dt.xhtml:
            c.execute(
                """
                INSERT OR REPLACE INTO datatype_xhtml
                VALUES (?, ?, ?)
            """,
                (
                    dt.xhtml.identifier,
                    dt.xhtml.last_change.isoformat() if dt.xhtml.last_change else None,
                    dt.xhtml.long_name,
                ),
            )
        # Write DataType Enumeration and its enum_values.
        if dt.enumeration:
            c.execute(
                """
                INSERT OR REPLACE INTO datatype_enumeration
                VALUES (?, ?, ?)
            """,
                (
                    dt.enumeration.identifier,
                    (
                        dt.enumeration.last_change.isoformat()
                        if dt.enumeration.last_change
                        else None
                    ),
                    dt.enumeration.long_name,
                ),
            )
            for ev in dt.enumeration.enum_values:
                c.execute(
                    """
                    INSERT OR REPLACE INTO enum_value
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        ev.identifier,
                        dt.enumeration.identifier,
                        ev.last_change.isoformat() if ev.last_change else None,
                        ev.long_name,
                        ev.embedded_value.key,
                        ev.embedded_value.other_content,
                    ),
                )
        # Write additional data types.
        if dt.boolean:
            c.execute(
                """
                INSERT OR REPLACE INTO datatype_boolean
                VALUES (?, ?)
            """,
                (dt.boolean.identifier, dt.boolean.long_name),
            )
        if dt.date:
            c.execute(
                """
                INSERT OR REPLACE INTO datatype_date
                VALUES (?, ?)
            """,
                (dt.date.identifier, dt.date.long_name),
            )
        if dt.integer:
            c.execute(
                """
                INSERT OR REPLACE INTO datatype_integer
                VALUES (?, ?)
            """,
                (dt.integer.identifier, dt.integer.long_name),
            )
        if dt.real:
            c.execute(
                """
                INSERT OR REPLACE INTO datatype_real
                VALUES (?, ?)
            """,
                (dt.real.identifier, dt.real.long_name),
            )
        if dt.string:
            c.execute(
                """
                INSERT OR REPLACE INTO datatype_string
                VALUES (?, ?)
            """,
                (dt.string.identifier, dt.string.long_name),
            )
        # Write Spec Objects and their attributes.
        for obj in reqif.core_content.reqif_content.spec_objects:
            c.execute(
                """
                INSERT OR REPLACE INTO spec_object
                VALUES (?, ?, ?, ?)
            """,
                (
                    obj.identifier,
                    obj.last_change.isoformat() if obj.last_change else None,
                    obj.long_name,
                    obj.type_ref,
                ),
            )
            for attr in obj.attributes:
                c.execute(
                    """
                    INSERT INTO spec_object_attribute
                    VALUES (?, ?, ?)
                """,
                    (obj.identifier, attr.definition_ref, attr.value),
                )
        # Write Specifications and spec hierarchies.
        for spec in reqif.core_content.reqif_content.specifications:
            c.execute(
                """
                INSERT OR REPLACE INTO specification
                VALUES (?, ?, ?, ?)
            """,
                (
                    spec.identifier,
                    spec.last_change.isoformat() if spec.last_change else None,
                    spec.long_name,
                    spec.type_ref,
                ),
            )
            for hier in spec.spec_hierarchies:
                c.execute(
                    """
                    INSERT OR REPLACE INTO spec_hierarchy
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        hier.identifier,
                        spec.identifier,
                        hier.last_change.isoformat() if hier.last_change else None,
                        hier.long_name,
                        1 if hier.is_editable else 0,
                        hier.object_ref,
                    ),
                )
        # Write Tool Extensions.
        if reqif.tool_extensions:
            c.execute(
                """
                INSERT OR REPLACE INTO tool_extensions (id, content) VALUES (1, ?)
            """,
                (reqif.tool_extensions,),
            )
        conn.commit()
        conn.close()

    def read(self) -> ReqIF:
        """
        Read the complete ReqIF data model from the SQLite database and
        reassemble it into a ReqIF instance.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Read header.
        c.execute("SELECT * FROM reqif_header LIMIT 1")
        row = c.fetchone()
        header = ReqIFHeader(
            identifier=row[0],
            creation_time=datetime.fromisoformat(row[1]),
            repository_id=row[2],
            reqif_tool_id=row[3],
            reqif_version=row[4],
            source_tool_id=row[5],
            title=row[6],
        )
        # Read data types.
        dt = DataTypes()
        c.execute("SELECT * FROM datatype_xhtml LIMIT 1")
        row = c.fetchone()
        if row:
            dt.xhtml = DataTypeDefinitionXHTML(
                identifier=row[0],
                last_change=datetime.fromisoformat(row[1]) if row[1] else None,
                long_name=row[2],
            )
        c.execute("SELECT * FROM datatype_enumeration LIMIT 1")
        row = c.fetchone()
        if row:
            dt_enum = DataTypeDefinitionEnumeration(
                identifier=row[0],
                last_change=datetime.fromisoformat(row[1]) if row[1] else None,
                long_name=row[2],
                enum_values=[],
            )
            c.execute(
                "SELECT * FROM enum_value WHERE enumeration_id=?", (dt_enum.identifier,)
            )
            for erow in c.fetchall():
                ev = EnumValue(
                    identifier=erow[0],
                    last_change=datetime.fromisoformat(erow[2]) if erow[2] else None,
                    long_name=erow[3],
                    embedded_value=EmbeddedValue(key=erow[4], other_content=erow[5]),
                )
                dt_enum.enum_values.append(ev)
            dt.enumeration = dt_enum
        # Boolean.
        c.execute("SELECT * FROM datatype_boolean LIMIT 1")
        row = c.fetchone()
        if row:
            dt.boolean = DataTypeDefinitionBoolean(identifier=row[0], long_name=row[1])
        # Date.
        c.execute("SELECT * FROM datatype_date LIMIT 1")
        row = c.fetchone()
        if row:
            dt.date = DataTypeDefinitionDate(identifier=row[0], long_name=row[1])
        # Integer.
        c.execute("SELECT * FROM datatype_integer LIMIT 1")
        row = c.fetchone()
        if row:
            dt.integer = DataTypeDefinitionInteger(identifier=row[0], long_name=row[1])
        # Real.
        c.execute("SELECT * FROM datatype_real LIMIT 1")
        row = c.fetchone()
        if row:
            dt.real = DataTypeDefinitionReal(identifier=row[0], long_name=row[1])
        # String.
        c.execute("SELECT * FROM datatype_string LIMIT 1")
        row = c.fetchone()
        if row:
            dt.string = DataTypeDefinitionString(identifier=row[0], long_name=row[1])
        # Read Spec Objects.
        spec_objects = []
        c.execute("SELECT * FROM spec_object")
        for row in c.fetchall():
            attributes = []
            c.execute(
                "SELECT definition_ref, value FROM spec_object_attribute WHERE spec_object_id=?",
                (row[0],),
            )
            for arow in c.fetchall():
                attributes.append(AttributeValue(definition_ref=arow[0], value=arow[1]))
            spec_objects.append(
                SpecObject(
                    identifier=row[0],
                    last_change=datetime.fromisoformat(row[1]) if row[1] else None,
                    long_name=row[2],
                    type_ref=row[3],
                    attributes=attributes,
                )
            )
        # Read Specifications and their hierarchies.
        specifications = []
        c.execute("SELECT * FROM specification")
        spec_rows = c.fetchall()
        for spec_row in spec_rows:
            spec_id = spec_row[0]
            hierarchies = []
            c.execute(
                "SELECT * FROM spec_hierarchy WHERE specification_id=?", (spec_id,)
            )
            for hrow in c.fetchall():
                hierarchies.append(
                    SpecHierarchy(
                        identifier=hrow[0],
                        last_change=(
                            datetime.fromisoformat(hrow[2]) if hrow[2] else None
                        ),
                        long_name=hrow[3],
                        is_editable=bool(hrow[4]),
                        object_ref=hrow[5],
                    )
                )
            specifications.append(
                Specification(
                    identifier=spec_row[0],
                    last_change=(
                        datetime.fromisoformat(spec_row[1]) if spec_row[1] else None
                    ),
                    long_name=spec_row[2],
                    type_ref=spec_row[3],
                    spec_hierarchies=hierarchies,
                )
            )
        # Read tool extensions.
        c.execute("SELECT content FROM tool_extensions WHERE id=1")
        row = c.fetchone()
        tool_extensions = row[0] if row else None
        conn.close()

        reqif_content = ReqIFContent(
            data_types=dt, spec_objects=spec_objects, specifications=specifications
        )
        core_content = CoreContent(reqif_content=reqif_content)
        return ReqIF(
            header=header, core_content=core_content, tool_extensions=tool_extensions
        )
