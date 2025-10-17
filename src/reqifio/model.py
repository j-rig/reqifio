"""
model.py

This module defines the data model for the ReqIF file.
Each class maps to parts of the ReqIF XML structure.
We use dataclasses to keep definitions concise and clear.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


def parse_datetime(dt_str: str) -> datetime:
    # Remove the colon in the timezone for datetime.fromisoformat if necessary
    # e.g., "2017-04-25T15:44:26.000+02:00" -> "2017-04-25T15:44:26.000+0200"
    # if dt_str[-3] == ":":
    #     dt_str = dt_str[:-3] + dt_str[-2:]
    # print(dt_str)
    return datetime.fromisoformat(dt_str)


@dataclass
class ReqIFHeader:
    identifier: str
    creation_time: datetime
    repository_id: str
    reqif_tool_id: str
    reqif_version: str
    source_tool_id: str
    title: str


@dataclass
class DataTypeDefinitionXHTML:
    identifier: str
    last_change: Optional[datetime]
    long_name: str


@dataclass
class EmbeddedValue:
    key: str
    other_content: str


@dataclass
class EnumValue:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    embedded_value: EmbeddedValue


@dataclass
class DataTypeDefinitionEnumeration:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    enum_values: List[EnumValue] = field(default_factory=list)


@dataclass
class DataTypeDefinitionBoolean:
    identifier: str
    long_name: str


@dataclass
class DataTypeDefinitionDate:
    identifier: str
    long_name: str


@dataclass
class DataTypeDefinitionInteger:
    identifier: str
    long_name: str


@dataclass
class DataTypeDefinitionReal:
    identifier: str
    long_name: str


@dataclass
class DataTypeDefinitionString:
    identifier: str
    long_name: str


@dataclass
class DataTypes:
    xhtml: Optional[DataTypeDefinitionXHTML] = None
    enumeration: Optional[DataTypeDefinitionEnumeration] = None
    boolean: Optional[DataTypeDefinitionBoolean] = None
    date: Optional[DataTypeDefinitionDate] = None
    integer: Optional[DataTypeDefinitionInteger] = None
    real: Optional[DataTypeDefinitionReal] = None
    string: Optional[DataTypeDefinitionString] = None


# For brevity, we combine attribute definitions in the spec-type parts.
@dataclass
class AttributeDefinition:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    is_editable: bool


@dataclass
class AttributeDefinitionXHTML(AttributeDefinition):
    datatype_ref: str


@dataclass
class AttributeDefinitionEnumeration(AttributeDefinition):
    datatype_ref: str
    multi_valued: bool


@dataclass
class AttributeDefinitionBoolean(AttributeDefinition):
    datatype_ref: str


@dataclass
class AttributeDefinitionDate(AttributeDefinition):
    datatype_ref: str


@dataclass
class AttributeDefinitionInteger(AttributeDefinition):
    datatype_ref: str


@dataclass
class AttributeDefinitionReal(AttributeDefinition):
    datatype_ref: str


@dataclass
class AttributeDefinitionString(AttributeDefinition):
    datatype_ref: str


@dataclass
class SpecObjectType:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    attribute_definitions: List[AttributeDefinition] = field(default_factory=list)


@dataclass
class SpecificationType:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    attribute_definitions: List[AttributeDefinition] = field(default_factory=list)


@dataclass
class AttributeValue:
    # A simple attribute value that contains the definition reference and value as a string.
    definition_ref: str
    value: str


@dataclass
class SpecObject:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    attributes: List[AttributeValue] = field(default_factory=list)
    type_ref: str = ""


@dataclass
class SpecHierarchy:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    is_editable: bool
    object_ref: str


@dataclass
class Specification:
    identifier: str
    last_change: Optional[datetime]
    long_name: str
    type_ref: str
    spec_hierarchies: List[SpecHierarchy] = field(default_factory=list)


@dataclass
class ReqIFContent:
    data_types: DataTypes
    spec_object_types: List[SpecObjectType] = field(default_factory=list)
    specification_types: List[SpecificationType] = field(default_factory=list)
    spec_objects: List[SpecObject] = field(default_factory=list)
    specifications: List[Specification] = field(default_factory=list)


@dataclass
class CoreContent:
    reqif_content: ReqIFContent


@dataclass
class ReqIF:
    header: ReqIFHeader
    core_content: CoreContent
    tool_extensions: Optional[str] = (
        None  # Placeholder for any tool-specific extensions.
    )
