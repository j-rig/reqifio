"""
reqif_parser.py

This module defines the ReqIFParser class which reads a ReqIF XML file and
parses it into our Python data model. We utilize xml.etree.ElementTree for XML processing.
"""

from xml.etree import ElementTree as ET
from .model import (
    ReqIF,
    ReqIFHeader,
    parse_datetime,
    DataTypeDefinitionXHTML,
    DataTypeDefinitionEnumeration,
    EnumValue,
    EmbeddedValue,
    DataTypes,
    ReqIFContent,
    CoreContent,
    SpecObject,
    Specification,
    SpecHierarchy,
)
from .model import SpecObjectType, SpecificationType, AttributeValue
from datetime import datetime
from typing import Optional, List


class ReqIFParser:
    def __init__(self, xml_file: str):
        """
        Initialize the parser with the path to the XML file.
        """
        self.xml_file = xml_file
        self.ns = {
            "reqif": "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd",
            "xhtml": "http://www.w3.org/1999/xhtml",
            "reqif-xhtml": "http://www.w3.org/1999/xhtml",
        }

    def parse(self) -> ReqIF:
        """
        Parse the XML file and return a ReqIF object containing the data.
        """
        tree = ET.parse(self.xml_file)
        root = tree.getroot()

        header = self._parse_header(
            root.find("./reqif:THE-HEADER/reqif:REQ-IF-HEADER", self.ns)
        )
        content = self._parse_core_content(root.find("./reqif:CORE-CONTENT", self.ns))
        tool_extensions = root.find("./reqif:TOOL-EXTENSIONS", self.ns)
        tool_extensions_str = (
            ET.tostring(tool_extensions, encoding="unicode")
            if tool_extensions is not None
            else None
        )

        return ReqIF(
            header=header, core_content=content, tool_extensions=tool_extensions_str
        )

    def _parse_header(self, header_elem: ET.Element) -> ReqIFHeader:
        """
        Parse the ReqIF header part.
        """
        identifier = header_elem.attrib.get("IDENTIFIER")
        creation_time = parse_datetime(
            header_elem.findtext("reqif:CREATION-TIME", default="", namespaces=self.ns)
        )
        repository_id = header_elem.findtext(
            "reqif:REPOSITORY-ID", default="", namespaces=self.ns
        )
        reqif_tool_id = header_elem.findtext(
            "reqif:REQ-IF-TOOL-ID", default="", namespaces=self.ns
        )
        reqif_version = header_elem.findtext(
            "reqif:REQ-IF-VERSION", default="", namespaces=self.ns
        )
        source_tool_id = header_elem.findtext(
            "reqif:SOURCE-TOOL-ID", default="", namespaces=self.ns
        )
        title = header_elem.findtext("reqif:TITLE", default="", namespaces=self.ns)

        return ReqIFHeader(
            identifier=identifier,
            creation_time=creation_time,
            repository_id=repository_id,
            reqif_tool_id=reqif_tool_id,
            reqif_version=reqif_version,
            source_tool_id=source_tool_id,
            title=title,
        )

    def _parse_core_content(self, core_elem: ET.Element) -> CoreContent:
        """
        Parse the CORE-CONTENT element.
        """
        reqif_content_elem = core_elem.find("reqif:REQ-IF-CONTENT", self.ns)
        reqif_content = self._parse_reqif_content(reqif_content_elem)
        return CoreContent(reqif_content=reqif_content)

    def _parse_reqif_content(self, content_elem: ET.Element) -> ReqIFContent:
        """
        Parse the REQ-IF-CONTENT element.
        For this example, we only parse DataTypes, SpecObjects, and Specifications.
        """
        data_types = self._parse_data_types(
            content_elem.find("reqif:DATATYPES", self.ns)
        )
        spec_objects = self._parse_spec_objects(
            content_elem.find("reqif:SPEC-OBJECTS", self.ns)
        )
        specifications = self._parse_specifications(
            content_elem.find("reqif:SPECIFICATIONS", self.ns)
        )
        # Skipping Spec Types parsing for brevity.
        return ReqIFContent(
            data_types=data_types,
            spec_objects=spec_objects,
            specifications=specifications,
        )

    def _parse_data_types(self, datatypes_elem: Optional[ET.Element]) -> DataTypes:
        """
        Parse the DATATYPES element.
        """
        data_types = DataTypes()
        if datatypes_elem is None:
            return data_types

        for child in datatypes_elem:
            tag = self._strip_ns(child.tag)
            if tag == "DATATYPE-DEFINITION-XHTML":
                dt = DataTypeDefinitionXHTML(
                    identifier=child.attrib.get("IDENTIFIER"),
                    last_change=(
                        parse_datetime(child.attrib.get("LAST-CHANGE"))
                        if "LAST-CHANGE" in child.attrib
                        else None
                    ),
                    long_name=child.attrib.get("LONG-NAME"),
                )
                data_types.xhtml = dt
            elif tag == "DATATYPE-DEFINITION-ENUMERATION":
                dt_enum = DataTypeDefinitionEnumeration(
                    identifier=child.attrib.get("IDENTIFIER"),
                    last_change=(
                        parse_datetime(child.attrib.get("LAST-CHANGE"))
                        if "LAST-CHANGE" in child.attrib
                        else None
                    ),
                    long_name=child.attrib.get("LONG-NAME"),
                )
                specified_values = child.find("reqif:SPECIFIED-VALUES", self.ns)
                if specified_values is not None:
                    for enum_elem in specified_values.findall(
                        "reqif:ENUM-VALUE", self.ns
                    ):
                        embedded = enum_elem.find(
                            "reqif:PROPERTIES/reqif:EMBEDDED-VALUE", self.ns
                        )
                        ev = EnumValue(
                            identifier=enum_elem.attrib.get("IDENTIFIER"),
                            last_change=(
                                parse_datetime(enum_elem.attrib.get("LAST-CHANGE"))
                                if "LAST-CHANGE" in enum_elem.attrib
                                else None
                            ),
                            long_name=enum_elem.attrib.get("LONG-NAME"),
                            embedded_value=EmbeddedValue(
                                key=embedded.attrib.get("KEY"),
                                other_content=embedded.attrib.get("OTHER-CONTENT"),
                            ),
                        )
                        dt_enum.enum_values.append(ev)
                data_types.enumeration = dt_enum
            elif tag == "DATATYPE-DEFINITION-BOOLEAN":
                from .model import DataTypeDefinitionBoolean

                data_types.boolean = DataTypeDefinitionBoolean(
                    identifier=child.attrib.get("IDENTIFIER"),
                    long_name=child.attrib.get("LONG-NAME"),
                )
            elif tag == "DATATYPE-DEFINITION-DATE":
                from .model import DataTypeDefinitionDate

                data_types.date = DataTypeDefinitionDate(
                    identifier=child.attrib.get("IDENTIFIER"),
                    long_name=child.attrib.get("LONG-NAME"),
                )
            elif tag == "DATATYPE-DEFINITION-INTEGER":
                from .model import DataTypeDefinitionInteger

                data_types.integer = DataTypeDefinitionInteger(
                    identifier=child.attrib.get("IDENTIFIER"),
                    long_name=child.attrib.get("LONG-NAME"),
                )
            elif tag == "DATATYPE-DEFINITION-REAL":
                from .model import DataTypeDefinitionReal

                data_types.real = DataTypeDefinitionReal(
                    identifier=child.attrib.get("IDENTIFIER"),
                    long_name=child.attrib.get("LONG-NAME"),
                )
            elif tag == "DATATYPE-DEFINITION-STRING":
                from .model import DataTypeDefinitionString

                data_types.string = DataTypeDefinitionString(
                    identifier=child.attrib.get("IDENTIFIER"),
                    long_name=child.attrib.get("LONG-NAME"),
                )
        return data_types

    def _parse_spec_objects(
        self, spec_objects_elem: Optional[ET.Element]
    ) -> List[SpecObject]:
        """
        Parse the SPEC-OBJECTS element with our example SPEC-OBJECT.
        """
        spec_objects = []
        if spec_objects_elem is None:
            return spec_objects

        for obj_elem in spec_objects_elem.findall("reqif:SPEC-OBJECT", self.ns):
            identifier = obj_elem.attrib.get("IDENTIFIER")
            last_change = (
                parse_datetime(obj_elem.attrib.get("LAST-CHANGE"))
                if "LAST-CHANGE" in obj_elem.attrib
                else None
            )
            long_name = obj_elem.attrib.get("LONG-NAME")
            type_ref_elem = obj_elem.find(
                "reqif:TYPE/reqif:SPEC-OBJECT-TYPE-REF", self.ns
            )
            type_ref = type_ref_elem.text if type_ref_elem is not None else ""

            attributes = []
            values_elem = obj_elem.find("reqif:VALUES", self.ns)
            if values_elem is not None:
                for attr_elem in values_elem:
                    # Depending on attribute type: here we simply extract the textual content.
                    definition_elem = attr_elem.find(
                        "reqif:DEFINITION/reqif:ATTRIBUTE-DEFINITION-XHTML-REF", self.ns
                    )
                    def_ref = (
                        definition_elem.text if definition_elem is not None else ""
                    )
                    the_value_elem = attr_elem.find("reqif:THE-VALUE", self.ns)
                    # Assume the value is contained within the first child element (like xhtml:div)
                    value = ""
                    if the_value_elem is not None and len(the_value_elem):
                        value = the_value_elem[0].text
                    attributes.append(
                        AttributeValue(definition_ref=def_ref, value=value)
                    )

            spec_objects.append(
                SpecObject(
                    identifier=identifier,
                    last_change=last_change,
                    long_name=long_name,
                    attributes=attributes,
                    type_ref=type_ref,
                )
            )
        return spec_objects

    def _parse_specifications(
        self, spec_elem: Optional[ET.Element]
    ) -> List[Specification]:
        """
        Parse the SPECIFICATIONS element with our example SPECIFICATION.
        """
        specifications = []
        if spec_elem is None:
            return specifications

        for spec in spec_elem.findall("reqif:SPECIFICATION", self.ns):
            identifier = spec.attrib.get("IDENTIFIER")
            last_change = (
                parse_datetime(spec.attrib.get("LAST-CHANGE"))
                if "LAST-CHANGE" in spec.attrib
                else None
            )
            long_name = spec.attrib.get("LONG-NAME")
            type_ref_elem = spec.find(
                "reqif:TYPE/reqif:SPECIFICATION-TYPE-REF", self.ns
            )
            type_ref = type_ref_elem.text if type_ref_elem is not None else ""
            spec_hierarchies = []
            children_elem = spec.find("reqif:CHILDREN", self.ns)
            if children_elem is not None:
                for hier in children_elem.findall("reqif:SPEC-HIERARCHY", self.ns):
                    obj_elem = hier.find("reqif:OBJECT/reqif:SPEC-OBJECT-REF", self.ns)
                    object_ref = obj_elem.text if obj_elem is not None else ""
                    is_editable = (
                        hier.attrib.get("IS-EDITABLE", "false").lower() == "true"
                    )
                    spec_hierarchies.append(
                        SpecHierarchy(
                            identifier=hier.attrib.get("IDENTIFIER"),
                            last_change=(
                                parse_datetime(hier.attrib.get("LAST-CHANGE"))
                                if "LAST-CHANGE" in hier.attrib
                                else None
                            ),
                            long_name=hier.attrib.get("LONG-NAME"),
                            is_editable=is_editable,
                            object_ref=object_ref,
                        )
                    )
            specifications.append(
                Specification(
                    identifier=identifier,
                    last_change=last_change,
                    long_name=long_name,
                    type_ref=type_ref,
                    spec_hierarchies=spec_hierarchies,
                )
            )
        return specifications

    def _strip_ns(self, tag: str) -> str:
        """
        Helper method to strip the namespace.
        """
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag
