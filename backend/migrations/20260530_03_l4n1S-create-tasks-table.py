"""
create-tasks-table
"""

from yoyo import step

__depends__ = {'20260530_02_7Egwn-create-task-status-enum'}

steps = [
    step(
        "CREATE TABLE tasks ("
        "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),"
        "    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,"
        "    title VARCHAR(255) NOT NULL,"
        "    description TEXT,"
        "    priority task_priority NOT NULL DEFAULT 'MEDIUM',"
        "    status task_status NOT NULL DEFAULT 'TODO',"
        "    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,"
        "    due_date TIMESTAMPTZ,"
        "    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),"
        "    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
        ");",
        "DROP TABLE IF EXISTS tasks;"
    ),
    step(
        "CREATE INDEX idx_tasks_status ON tasks(status);"
        "CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);"
        "CREATE INDEX idx_tasks_due_date ON tasks(due_date);"
        "CREATE INDEX idx_tasks_organization_id ON tasks(organization_id);",
        
        "DROP INDEX IF EXISTS idx_tasks_organization_id;"
        "DROP INDEX IF EXISTS idx_tasks_due_date;"
        "DROP INDEX IF EXISTS idx_tasks_assignee_id;"
        "DROP INDEX IF EXISTS idx_tasks_status;"
    )
]
