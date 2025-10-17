"""
writer.py

This module defines the ReqIFWriter class which accepts a ReqIF
data model object and writes it out as an XML string in the ReqIF format.
"""

import xml.etree.ElementTree as ET
from .model import (
    ReqIF,
    ReqIFHeader,
    SpecObject,
    Specification,
    SpecHierarchy,
    DataTypes,
    DataTypeDefinitionXHTML,
    DataTypeDefinitionEnumeration,
    EnumValue,
    EmbeddedValue,
)
from datetime import datetime
from xml.dom import minidom


class ReqIFWriter:
    def __init__(self, reqif: ReqIF):
        """
        Initialize the writer with a ReqIF data model instance.
        """
        self.reqif = reqif
        self.ns = {
            "": "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd",
            "xhtml": "http://www.w3.org/1999/xhtml",
            "reqif-xhtml": "http://www.w3.org/1999/xhtml",
        }
        # Register namespaces for pretty output.
        for prefix, uri in self.ns.items():
            ET.register_namespace(prefix, uri)

    def write(self) -> str:
        """
        Write the ReqIF data model to an XML string.
        """
        root = ET.Element("REQ-IF", self.ns)

        # THE-HEADER
        the_header = ET.SubElement(root, "THE-HEADER")
        header_elem = ET.SubElement(
            the_header,
            "REQ-IF-HEADER",
            {
                "IDENTIFIER": self.reqif.header.identifier,
            },
        )
        self._create_sub_element(
            header_elem,
            "CREATION-TIME",
            self._format_datetime(self.reqif.header.creation_time),
        )
        self._create_sub_element(
            header_elem, "REPOSITORY-ID", self.reqif.header.repository_id
        )
        self._create_sub_element(
            header_elem, "REQ-IF-TOOL-ID", self.reqif.header.reqif_tool_id
        )
        self._create_sub_element(
            header_elem, "REQ-IF-VERSION", self.reqif.header.reqif_version
        )
        self._create_sub_element(
            header_elem, "SOURCE-TOOL-ID", self.reqif.header.source_tool_id
        )
        self._create_sub_element(header_elem, "TITLE", self.reqif.header.title)

        # CORE-CONTENT
        core_content = ET.SubElement(root, "CORE-CONTENT")
        reqif_content = ET.SubElement(core_content, "REQ-IF-CONTENT")
        # Write DataTypes (only XHTML and Enumeration for our example)
        if self.reqif.core_content.reqif_content.data_types:
            dt_elem = ET.SubElement(reqif_content, "DATATYPES")
            dt = self.reqif.core_content.reqif_content.data_types
            if dt.xhtml:
                ET.SubElement(
                    dt_elem,
                    "DATATYPE-DEFINITION-XHTML",
                    {
                        "IDENTIFIER": dt.xhtml.identifier,
                        "LAST-CHANGE": (
                            self._format_datetime(dt.xhtml.last_change)
                            if dt.xhtml.last_change
                            else ""
                        ),
                        "LONG-NAME": dt.xhtml.long_name,
                    },
                )
            if dt.enumeration:
                enum_elem = ET.SubElement(
                    dt_elem,
                    "DATATYPE-DEFINITION-ENUMERATION",
                    {
                        "IDENTIFIER": dt.enumeration.identifier,
                        "LAST-CHANGE": (
                            self._format_datetime(dt.enumeration.last_change)
                            if dt.enumeration.last_change
                            else ""
                        ),
                        "LONG-NAME": dt.enumeration.long_name,
                    },
                )
                specified_values = ET.SubElement(enum_elem, "SPECIFIED-VALUES")
                for ev in dt.enumeration.enum_values:
                    ev_elem = ET.SubElement(
                        specified_values,
                        "ENUM-VALUE",
                        {
                            "IDENTIFIER": ev.identifier,
                            "LAST-CHANGE": (
                                self._format_datetime(ev.last_change)
                                if ev.last_change
                                else ""
                            ),
                            "LONG-NAME": ev.long_name,
                        },
                    )
                    props = ET.SubElement(ev_elem, "PROPERTIES")
                    ET.SubElement(
                        props,
                        "EMBEDDED-VALUE",
                        {
                            "KEY": ev.embedded_value.key,
                            "OTHER-CONTENT": ev.embedded_value.other_content,
                        },
                    )
            # Additional DataTypes (Boolean, Date, Integer, Real, String) can be added similarly.

        # Write SPEC-OBJECTS
        spec_objects_elem = ET.SubElement(reqif_content, "SPEC-OBJECTS")
        for obj in self.reqif.core_content.reqif_content.spec_objects:
            so_elem = ET.SubElement(
                spec_objects_elem,
                "SPEC-OBJECT",
                {
                    "IDENTIFIER": obj.identifier,
                    "LAST-CHANGE": (
                        self._format_datetime(obj.last_change)
                        if obj.last_change
                        else ""
                    ),
                    "LONG-NAME": obj.long_name,
                },
            )
            values_elem = ET.SubElement(so_elem, "VALUES")
            for attr in obj.attributes:
                # Here we assume the attribute is an XHTML type value.
                attr_elem = ET.SubElement(values_elem, "ATTRIBUTE-VALUE-XHTML")
                def_elem = ET.SubElement(attr_elem, "DEFINITION")
                self._create_sub_element(
                    def_elem, "ATTRIBUTE-DEFINITION-XHTML-REF", attr.definition_ref
                )
                value_elem = ET.SubElement(attr_elem, "THE-VALUE")
                # Wrap value in an xhtml:div container.
                xhtml_div = ET.SubElement(
                    value_elem, "{http://www.w3.org/1999/xhtml}div"
                )
                xhtml_div.text = attr.value

            type_elem = ET.SubElement(so_elem, "TYPE")
            self._create_sub_element(type_elem, "SPEC-OBJECT-TYPE-REF", obj.type_ref)

        # Write SPECIFICATIONS
        specs_elem = ET.SubElement(reqif_content, "SPECIFICATIONS")
        for spec in self.reqif.core_content.reqif_content.specifications:
            spec_elem = ET.SubElement(
                specs_elem,
                "SPECIFICATION",
                {
                    "IDENTIFIER": spec.identifier,
                    "LAST-CHANGE": (
                        self._format_datetime(spec.last_change)
                        if spec.last_change
                        else ""
                    ),
                    "LONG-NAME": spec.long_name,
                },
            )
            ET.SubElement(spec_elem, "VALUES")  # Empty VALUES
            type_elem = ET.SubElement(spec_elem, "TYPE")
            self._create_sub_element(type_elem, "SPECIFICATION-TYPE-REF", spec.type_ref)
            children_elem = ET.SubElement(spec_elem, "CHILDREN")
            for hier in spec.spec_hierarchies:
                hier_elem = ET.SubElement(
                    children_elem,
                    "SPEC-HIERARCHY",
                    {
                        "IDENTIFIER": hier.identifier,
                        "LAST-CHANGE": (
                            self._format_datetime(hier.last_change)
                            if hier.last_change
                            else ""
                        ),
                        "LONG-NAME": hier.long_name,
                        "IS-EDITABLE": "true" if hier.is_editable else "false",
                    },
                )
                obj_elem = ET.SubElement(hier_elem, "OBJECT")
                self._create_sub_element(obj_elem, "SPEC-OBJECT-REF", hier.object_ref)

        # SPEC-RELATIONS and SPEC-RELATION-GROUPS can be added if needed.

        # TOOL-EXTENSIONS
        ET.SubElement(root, "TOOL-EXTENSIONS")  # Left empty.

        # Return pretty printed XML
        rough_string = ET.tostring(root, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def _create_sub_element(self, parent, tag, text):
        """
        Helper method to create a subelement with text content.
        """
        elem = ET.SubElement(parent, tag)
        elem.text = text
        return elem

    def _format_datetime(self, dt: datetime) -> str:
        """
        Format a datetime object back into the required string format.
        """
        # Using isoformat with timespec and adding a colon in timezone if needed.
        if dt.tzinfo:
            iso_str = dt.isoformat(timespec="milliseconds")
            # Add colon in timezone offset if missing.
            if len(iso_str) >= 26 and iso_str[-3] != ":":
                iso_str = iso_str[:-2] + ":" + iso_str[-2:]
            return iso_str
        else:
            return dt.isoformat(timespec="milliseconds")
