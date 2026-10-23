'''Minimal ORM-like models for testing purposes.'''

from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    """Simple Task model used in tests.

    The real application uses raw SQLite rows mapped to ``TaskOut`` pydantic model.
    For the purpose of the regression test we expose a lightweight ``Task`` class
    with the fields that the test accesses.
    """

    id: str
    title: str
    priority: str
    status: str
    user_id: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[str] = None
    created_at: Optional[str] = None
