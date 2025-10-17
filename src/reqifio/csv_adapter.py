"""
csv_adapter.py

This module defines the CSVAdapter class which writes the complete ReqIF data model
to CSV files and reads them back. Each entity in the data model is stored in its own CSV file.
The design follows a table-per-entity approach similar to a relational schema.
"""

import os
import csv
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


class CSVAdapter:
    def __init__(self, folder_path: str):
        """
        Initialize the adapter with the folder path where CSV files will be stored.
        """
        self.folder = folder_path
        os.makedirs(self.folder, exist_ok=True)

    def write(self, reqif: ReqIF):
        """
        Write the complete ReqIF data model to CSV files.
        Each CSV file corresponds to one "table" in the data model.
        """
        # Write header
        self._write_csv(
            "header.csv",
            [
                "identifier",
                "creation_time",
                "repository_id",
                "reqif_tool_id",
                "reqif_version",
                "source_tool_id",
                "title",
            ],
            [
                {
                    "identifier": reqif.header.identifier,
                    "creation_time": reqif.header.creation_time.isoformat(),
                    "repository_id": reqif.header.repository_id,
                    "reqif_tool_id": reqif.header.reqif_tool_id,
                    "reqif_version": reqif.header.reqif_version,
                    "source_tool_id": reqif.header.source_tool_id,
                    "title": reqif.header.title,
                }
            ],
        )

        dt = reqif.core_content.reqif_content.data_types

        # Write DataType XHTML
        if dt.xhtml:
            self._write_csv(
                "datatype_xhtml.csv",
                ["identifier", "last_change", "long_name"],
                [
                    {
                        "identifier": dt.xhtml.identifier,
                        "last_change": (
                            dt.xhtml.last_change.isoformat()
                            if dt.xhtml.last_change
                            else ""
                        ),
                        "long_name": dt.xhtml.long_name,
                    }
                ],
            )

        # Write DataType Enumeration and its enum values
        if dt.enumeration:
            self._write_csv(
                "datatype_enumeration.csv",
                ["identifier", "last_change", "long_name"],
                [
                    {
                        "identifier": dt.enumeration.identifier,
                        "last_change": (
                            dt.enumeration.last_change.isoformat()
                            if dt.enumeration.last_change
                            else ""
                        ),
                        "long_name": dt.enumeration.long_name,
                    }
                ],
            )
            enum_val_rows = []
            for ev in dt.enumeration.enum_values:
                enum_val_rows.append(
                    {
                        "identifier": ev.identifier,
                        "enumeration_id": dt.enumeration.identifier,
                        "last_change": (
                            ev.last_change.isoformat() if ev.last_change else ""
                        ),
                        "long_name": ev.long_name,
                        "embedded_key": ev.embedded_value.key,
                        "embedded_other_content": ev.embedded_value.other_content,
                    }
                )
            self._write_csv(
                "enum_value.csv",
                [
                    "identifier",
                    "enumeration_id",
                    "last_change",
                    "long_name",
                    "embedded_key",
                    "embedded_other_content",
                ],
                enum_val_rows,
            )

        # Write additional data types if available.
        if dt.boolean:
            self._write_csv(
                "datatype_boolean.csv",
                ["identifier", "long_name"],
                [
                    {
                        "identifier": dt.boolean.identifier,
                        "long_name": dt.boolean.long_name,
                    }
                ],
            )
        if dt.date:
            self._write_csv(
                "datatype_date.csv",
                ["identifier", "long_name"],
                [{"identifier": dt.date.identifier, "long_name": dt.date.long_name}],
            )
        if dt.integer:
            self._write_csv(
                "datatype_integer.csv",
                ["identifier", "long_name"],
                [
                    {
                        "identifier": dt.integer.identifier,
                        "long_name": dt.integer.long_name,
                    }
                ],
            )
        if dt.real:
            self._write_csv(
                "datatype_real.csv",
                ["identifier", "long_name"],
                [{"identifier": dt.real.identifier, "long_name": dt.real.long_name}],
            )
        if dt.string:
            self._write_csv(
                "datatype_string.csv",
                ["identifier", "long_name"],
                [
                    {
                        "identifier": dt.string.identifier,
                        "long_name": dt.string.long_name,
                    }
                ],
            )

        # Write Spec Objects and their attributes.
        spec_obj_rows = []
        spec_obj_attr_rows = []
        for obj in reqif.core_content.reqif_content.spec_objects:
            spec_obj_rows.append(
                {
                    "identifier": obj.identifier,
                    "last_change": (
                        obj.last_change.isoformat() if obj.last_change else ""
                    ),
                    "long_name": obj.long_name,
                    "type_ref": obj.type_ref,
                }
            )
            for attr in obj.attributes:
                spec_obj_attr_rows.append(
                    {
                        "spec_object_id": obj.identifier,
                        "definition_ref": attr.definition_ref,
                        "value": attr.value,
                    }
                )
        self._write_csv(
            "spec_object.csv",
            ["identifier", "last_change", "long_name", "type_ref"],
            spec_obj_rows,
        )
        self._write_csv(
            "spec_object_attribute.csv",
            ["spec_object_id", "definition_ref", "value"],
            spec_obj_attr_rows,
        )

        # Write Specifications and spec hierarchies.
        spec_rows = []
        spec_hier_rows = []
        for spec in reqif.core_content.reqif_content.specifications:
            spec_rows.append(
                {
                    "identifier": spec.identifier,
                    "last_change": (
                        spec.last_change.isoformat() if spec.last_change else ""
                    ),
                    "long_name": spec.long_name,
                    "type_ref": spec.type_ref,
                }
            )
            for hier in spec.spec_hierarchies:
                spec_hier_rows.append(
                    {
                        "identifier": hier.identifier,
                        "specification_id": spec.identifier,
                        "last_change": (
                            hier.last_change.isoformat() if hier.last_change else ""
                        ),
                        "long_name": hier.long_name,
                        "is_editable": "1" if hier.is_editable else "0",
                        "object_ref": hier.object_ref,
                    }
                )
        self._write_csv(
            "specification.csv",
            ["identifier", "last_change", "long_name", "type_ref"],
            spec_rows,
        )
        self._write_csv(
            "spec_hierarchy.csv",
            [
                "identifier",
                "specification_id",
                "last_change",
                "long_name",
                "is_editable",
                "object_ref",
            ],
            spec_hier_rows,
        )

        # Write tool extensions (if any) as a single row.
        self._write_csv(
            "tool_extensions.csv",
            ["id", "content"],
            [
                {
                    "id": "1",
                    "content": reqif.tool_extensions if reqif.tool_extensions else "",
                }
            ],
        )

    def read(self) -> ReqIF:
        """
        Read the complete ReqIF data model from CSV files and reassemble it into a ReqIF instance.
        """
        # Read header.
        header_row = self._read_csv("header.csv")[0]
        header = ReqIFHeader(
            identifier=header_row["identifier"],
            creation_time=datetime.fromisoformat(header_row["creation_time"]),
            repository_id=header_row["repository_id"],
            reqif_tool_id=header_row["reqif_tool_id"],
            reqif_version=header_row["reqif_version"],
            source_tool_id=header_row["source_tool_id"],
            title=header_row["title"],
        )

        dt = DataTypes()
        # Read DataType XHTML.
        xhtml_rows = self._read_csv("datatype_xhtml.csv")
        if xhtml_rows:
            row = xhtml_rows[0]
            dt.xhtml = DataTypeDefinitionXHTML(
                identifier=row["identifier"],
                last_change=(
                    datetime.fromisoformat(row["last_change"])
                    if row["last_change"]
                    else None
                ),
                long_name=row["long_name"],
            )
        # Read DataType Enumeration.
        enum_rows = self._read_csv("datatype_enumeration.csv")
        if enum_rows:
            row = enum_rows[0]
            dt_enum = DataTypeDefinitionEnumeration(
                identifier=row["identifier"],
                last_change=(
                    datetime.fromisoformat(row["last_change"])
                    if row["last_change"]
                    else None
                ),
                long_name=row["long_name"],
                enum_values=[],
            )
            # Read corresponding enum values.
            for erow in self._read_csv("enum_value.csv"):
                if erow["enumeration_id"] == dt_enum.identifier:
                    ev = EnumValue(
                        identifier=erow["identifier"],
                        last_change=(
                            datetime.fromisoformat(erow["last_change"])
                            if erow["last_change"]
                            else None
                        ),
                        long_name=erow["long_name"],
                        embedded_value=EmbeddedValue(
                            key=erow["embedded_key"],
                            other_content=erow["embedded_other_content"],
                        ),
                    )
                    dt_enum.enum_values.append(ev)
            dt.enumeration = dt_enum

        # Additional data types.
        bool_rows = self._read_csv("datatype_boolean.csv")
        if bool_rows:
            row = bool_rows[0]
            dt.boolean = DataTypeDefinitionBoolean(
                identifier=row["identifier"], long_name=row["long_name"]
            )

        date_rows = self._read_csv("datatype_date.csv")
        if date_rows:
            row = date_rows[0]
            dt.date = DataTypeDefinitionDate(
                identifier=row["identifier"], long_name=row["long_name"]
            )

        int_rows = self._read_csv("datatype_integer.csv")
        if int_rows:
            row = int_rows[0]
            dt.integer = DataTypeDefinitionInteger(
                identifier=row["identifier"], long_name=row["long_name"]
            )

        real_rows = self._read_csv("datatype_real.csv")
        if real_rows:
            row = real_rows[0]
            dt.real = DataTypeDefinitionReal(
                identifier=row["identifier"], long_name=row["long_name"]
            )

        str_rows = self._read_csv("datatype_string.csv")
        if str_rows:
            row = str_rows[0]
            dt.string = DataTypeDefinitionString(
                identifier=row["identifier"], long_name=row["long_name"]
            )

        # Read Spec Objects and attributes.
        spec_objects = []
        spec_obj_rows = self._read_csv("spec_object.csv")
        spec_obj_attr_rows = self._read_csv("spec_object_attribute.csv")
        for sobj in spec_obj_rows:
            attrs = []
            for attr in spec_obj_attr_rows:
                if attr["spec_object_id"] == sobj["identifier"]:
                    attrs.append(
                        AttributeValue(
                            definition_ref=attr["definition_ref"], value=attr["value"]
                        )
                    )
            spec_objects.append(
                SpecObject(
                    identifier=sobj["identifier"],
                    last_change=(
                        datetime.fromisoformat(sobj["last_change"])
                        if sobj["last_change"]
                        else None
                    ),
                    long_name=sobj["long_name"],
                    type_ref=sobj["type_ref"],
                    attributes=attrs,
                )
            )

        # Read Specifications and spec hierarchies.
        specifications = []
        spec_rows = self._read_csv("specification.csv")
        spec_hier_rows = self._read_csv("spec_hierarchy.csv")
        for sperow in spec_rows:
            hierarchies = []
            for hrow in spec_hier_rows:
                if hrow["specification_id"] == sperow["identifier"]:
                    hierarchies.append(
                        SpecHierarchy(
                            identifier=hrow["identifier"],
                            last_change=(
                                datetime.fromisoformat(hrow["last_change"])
                                if hrow["last_change"]
                                else None
                            ),
                            long_name=hrow["long_name"],
                            is_editable=hrow["is_editable"] == "1",
                            object_ref=hrow["object_ref"],
                        )
                    )
            specifications.append(
                Specification(
                    identifier=sperow["identifier"],
                    last_change=(
                        datetime.fromisoformat(sperow["last_change"])
                        if sperow["last_change"]
                        else None
                    ),
                    long_name=sperow["long_name"],
                    type_ref=sperow["type_ref"],
                    spec_hierarchies=hierarchies,
                )
            )

        # Read tool extensions.
        tool_rows = self._read_csv("tool_extensions.csv")
        tool_extensions = tool_rows[0]["content"] if tool_rows else None

        reqif_content = ReqIFContent(
            data_types=dt, spec_objects=spec_objects, specifications=specifications
        )
        core_content = CoreContent(reqif_content=reqif_content)
        return ReqIF(
            header=header, core_content=core_content, tool_extensions=tool_extensions
        )

    def _write_csv(self, filename, fieldnames, rows):
        """
        Helper method to write rows to a CSV file with the given fieldnames.
        """
        file_path = os.path.join(self.folder, filename)
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def _read_csv(self, filename):
        """
        Helper method to read CSV file and return a list of dictionaries.
        Returns empty list if the file does not exist.
        """
        file_path = os.path.join(self.folder, filename)
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
