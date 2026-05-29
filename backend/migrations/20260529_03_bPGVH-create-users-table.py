"""
create_users_table
"""

from yoyo import step

__depends__ = {"20260529_02_o2cE6-create-user-role-enum"}

steps = [
    step(
        "CREATE TABLE users ("
        "    id UUID PRIMARY KEY,"
        "    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,"
        "    email VARCHAR(255) NOT NULL,"
        "    password_hash TEXT NOT NULL,"
        "    role user_role NOT NULL DEFAULT 'MEMBER',"
        "    is_active BOOLEAN NOT NULL DEFAULT TRUE,"
        "    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),"
        "    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),"
        "    CONSTRAINT uq_user_org_email UNIQUE (organization_id, email)"
        ")",
        "DROP TABLE users"
    )
]
