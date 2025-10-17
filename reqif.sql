-- Table for header key-value pairs.
CREATE TABLE header (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Table for requirements.
CREATE TABLE requirements (
    req_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT
);

-- Table for spec objects.
CREATE TABLE spec_objects (
    spec_id TEXT PRIMARY KEY,
    type TEXT,
    values TEXT  -- Dictionary values are stored as text (repr format)
);

-- Table for spec relations.
CREATE TABLE spec_relations (
    relation_id TEXT PRIMARY KEY,
    source_id TEXT,
    target_id TEXT,
    relation_type TEXT,
    properties TEXT  -- Dictionary properties are stored as text (repr format)
);

-- Table for spec types.
CREATE TABLE spec_types (
    type_key TEXT PRIMARY KEY,
    type_value TEXT
);

-- Table for spec hierarchy.
CREATE TABLE IF NOT EXISTS spec_hierarchy (
    hier_id TEXT PRIMARY KEY,
    object_id TEXT,
    parent_hier_id TEXT
);