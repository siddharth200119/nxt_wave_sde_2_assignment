"""
create-task-status-enum
"""

from yoyo import step

__depends__ = {'20260530_01_FIVg5-create-task-priority-enum'}

steps = [
    step(
        "CREATE TYPE task_status AS ENUM ('TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED');",
        "DROP TYPE IF EXISTS task_status;"
    )
]
