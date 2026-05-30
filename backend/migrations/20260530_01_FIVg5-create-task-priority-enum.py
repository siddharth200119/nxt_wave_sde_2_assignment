"""
create-task-priority-enum
"""

from yoyo import step

__depends__ = {'20260529_04_fONH5-create-refresh-tokens-table'}

steps = [
    step(
        "CREATE TYPE task_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH');",
        "DROP TYPE IF EXISTS task_priority;"
    )
]
