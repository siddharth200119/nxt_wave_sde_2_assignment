"""
create_organizations_table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        "CREATE TABLE organizations ("
        "    id UUID PRIMARY KEY,"
        "    name VARCHAR(255) NOT NULL,"
        "    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),"
        "    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
        ")",
        "DROP TABLE organizations"
    )
]
