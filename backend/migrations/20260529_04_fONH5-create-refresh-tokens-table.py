"""
create_refresh_tokens_table
"""

from yoyo import step

__depends__ = {"20260529_03_bPGVH-create-users-table"}

steps = [
    step(
        "CREATE TABLE refresh_tokens ("
        "    id UUID PRIMARY KEY,"
        "    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,"
        "    token_hash TEXT NOT NULL,"
        "    expires_at TIMESTAMPTZ NOT NULL,"
        "    revoked BOOLEAN NOT NULL DEFAULT FALSE,"
        "    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
        ")",
        "DROP TABLE refresh_tokens"
    )
]
