"""
create_user_role_enum
"""

from yoyo import step

__depends__ = {"20260529_01_94mJb-create-organizations-table"}

steps = [
    step(
        "CREATE TYPE user_role AS ENUM ("
        "    'ADMIN',"
        "    'MANAGER',"
        "    'MEMBER'"
        ")",
        "DROP TYPE user_role"
    )
]
