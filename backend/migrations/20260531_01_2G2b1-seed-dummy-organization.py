"""
seed-dummy-organization
"""

from yoyo import step

__depends__ = {'20260530_03_l4n1S-create-tasks-table'}

steps = [
    step(
        "INSERT INTO organizations (id, name) VALUES ('d3b07384-d113-4956-a5d2-6c3b6f000000', 'Dummy Organization') ON CONFLICT (id) DO NOTHING",
        "DELETE FROM organizations WHERE id = 'd3b07384-d113-4956-a5d2-6c3b6f000000'"
    )
]
