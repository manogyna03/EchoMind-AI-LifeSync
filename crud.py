import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.database import db_session
from app.schemas import (
    TaskCreate, TaskUpdate, TaskOut,
    ScheduleCreate, ScheduleOut,
    MemoryCreate, MemoryOut,
    ReminderCreate, ReminderOut,
    PurchaseCreate, PurchaseOut,
    DeviceOut
)


from .constants import SYSTEM_USER_UUID



def now_iso() -> str:
    return datetime.now().isoformat()


# ---------------- Tasks CRUD ----------------
def get_tasks(status: Optional[str] = None, user_id: str = SYSTEM_USER_UUID) -> List[TaskOut]:
    # Determine if the user_id column exists in tasks table
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tasks);")
        cols = [row["name"] for row in cursor.fetchall()]
        has_user = "user_id" in cols
    # Perform query with appropriate filtering
    with db_session() as conn:
        cursor = conn.cursor()
        if status:
            if has_user:
                cursor.execute(
                    "SELECT * FROM tasks WHERE status = ? AND user_id = ? ORDER BY created_at DESC",
                    (status, user_id)
                )
            else:
                cursor.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                )
        else:
            if has_user:
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,)
                )
            else:
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            TaskOut(
                id=r["id"],
                title=r["title"],
                description=r["description"] or "",
                category=r["category"] or "general",
                priority=r["priority"] or "medium",
                status=r["status"] or "pending",
                due_date=r["due_date"] or "",
                created_at=r["created_at"]
            )
            for r in rows
        ]
    with db_session() as conn:
        cursor = conn.cursor()
        # Detect if user_id column exists
        cursor.execute("PRAGMA table_info(tasks);")
        cols = [row["name"] for row in cursor.fetchall()]
        has_user = "user_id" in cols
        if status:
            if has_user:
                cursor.execute("SELECT * FROM tasks WHERE status = ? AND user_id = ? ORDER BY created_at DESC", (status, user_id))
            else:
                cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            if has_user:
                cursor.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            else:
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            TaskOut(
                id=r["id"],
                title=r["title"],
                description=r["description"] or "",
                category=r["category"] or "general",
                priority=r["priority"] or "medium",
                status=r["status"] or "pending",
                due_date=r["due_date"] or "",
                created_at=r["created_at"]
            )
            for r in rows
        ]
    with db_session() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            TaskOut(
                id=r["id"],
                title=r["title"],
                description=r["description"] or "",
                category=r["category"] or "general",
                priority=r["priority"] or "medium",
                status=r["status"] or "pending",
                due_date=r["due_date"] or "",
                created_at=r["created_at"]
            )
            for r in rows
        ]


def get_task(task_id: str) -> Optional[TaskOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return TaskOut(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            category=row["category"] or "general",
            priority=row["priority"] or "medium",
            status=row["status"] or "pending",
            due_date=row["due_date"] or "",
            created_at=row["created_at"]
        )


def create_task(data: TaskCreate) -> TaskOut:
    task_id = str(uuid.uuid4())
    created = now_iso()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (id, title, description, category, priority, status, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            data.title.strip(),
            data.description or "",
            data.category or "general",
            data.priority or "medium",
            data.status or "pending",
            data.due_date or "",
            created
        ))
    return get_task(task_id)


def update_task(task_id: str, data: TaskUpdate) -> Optional[TaskOut]:
    existing = get_task(task_id)
    if not existing:
        return None
    updates = {}
    if data.title is not None:
        updates["title"] = data.title.strip()
    if data.description is not None:
        updates["description"] = data.description
    if data.category is not None:
        updates["category"] = data.category
    if data.priority is not None:
        updates["priority"] = data.priority
    if data.status is not None:
        updates["status"] = data.status
    if data.due_date is not None:
        updates["due_date"] = data.due_date

    if updates:
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [task_id]
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
    return get_task(task_id)


def delete_task(task_id: str) -> bool:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


# ---------------- Schedule CRUD ----------------
def get_schedules(user_id: str = SYSTEM_USER_UUID) -> List[ScheduleOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        # Detect if user_id column exists
        cursor.execute("PRAGMA table_info(schedule_events);")
        cols = [row["name"] for row in cursor.fetchall()]
        has_user = "user_id" in cols
        if has_user:
            cursor.execute("SELECT * FROM schedule_events WHERE user_id = ? ORDER BY event_date ASC, start_time ASC", (user_id,))
        else:
            cursor.execute("SELECT * FROM schedule_events ORDER BY event_date ASC, start_time ASC")
        rows = cursor.fetchall()
        return [
            ScheduleOut(
                id=r["id"],
                title=r["title"],
                event_date=r["event_date"],
                start_time=r["start_time"],
                duration_mins=r["duration_mins"],
                location=r["location"] or "",
                category=r["category"] or "general",
                is_completed=bool(r["is_completed"]),
                created_at=r["created_at"]
            )
            for r in rows
        ]


def create_schedule(data: ScheduleCreate) -> ScheduleOut:
    event_id = str(uuid.uuid4())
    created = now_iso()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO schedule_events (id, title, event_date, start_time, duration_mins, location, category, is_completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            event_id,
            data.title.strip(),
            data.event_date,
            data.start_time,
            data.duration_mins or 30,
            data.location or "",
            data.category or "general",
            created
        ))
    return ScheduleOut(
        id=event_id,
        title=data.title,
        event_date=data.event_date,
        start_time=data.start_time,
        duration_mins=data.duration_mins or 30,
        location=data.location or "",
        category=data.category or "general",
        is_completed=False,
        created_at=created
    )


# ---------------- Memory CRUD ----------------
def get_memories(category: Optional[str] = None, user_id: str = SYSTEM_USER_UUID) -> List[MemoryOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        # Detect user_id column
        cursor.execute("PRAGMA table_info(memory_items);")
        cols = [row["name"] for row in cursor.fetchall()]
        has_user = "user_id" in cols
        if category:
            if has_user:
                cursor.execute("SELECT * FROM memory_items WHERE category = ? AND user_id = ? ORDER BY updated_at DESC", (category, user_id))
            else:
                cursor.execute("SELECT * FROM memory_items WHERE category = ? ORDER BY updated_at DESC", (category,))
        else:
            if has_user:
                cursor.execute("SELECT * FROM memory_items WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
            else:
                cursor.execute("SELECT * FROM memory_items ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        return [
            MemoryOut(
                id=r["id"],
                key_topic=r["key_topic"],
                value_fact=r["value_fact"],
                category=r["category"],
                confidence=r["confidence"],
                updated_at=r["updated_at"]
            )
            for r in rows
        ]


def create_memory(data: MemoryCreate) -> MemoryOut:
    mem_id = str(uuid.uuid4())
    updated = now_iso()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memory_items (id, key_topic, value_fact, category, confidence, updated_at)
            VALUES (?, ?, ?, ?, 1.0, ?)
        """, (mem_id, data.key_topic.strip(), data.value_fact.strip(), data.category or "personal", updated))
    return MemoryOut(
        id=mem_id,
        key_topic=data.key_topic,
        value_fact=data.value_fact,
        category=data.category or "personal",
        confidence=1.0,
        updated_at=updated
    )


# ---------------- Reminders CRUD ----------------
def get_reminders() -> List[ReminderOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            ReminderOut(
                id=r["id"],
                title=r["title"],
                due_time=r["due_time"],
                priority=r["priority"],
                is_active=bool(r["is_active"]),
                category=r["category"],
                created_at=r["created_at"]
            )
            for r in rows
        ]


def create_reminder(data: ReminderCreate) -> ReminderOut:
    rem_id = str(uuid.uuid4())
    created = now_iso()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (id, title, due_time, priority, is_active, category, created_at)
            VALUES (?, ?, ?, ?, 1, ?, ?)
        """, (rem_id, data.title.strip(), data.due_time, data.priority or "medium", data.category or "general", created))
    return ReminderOut(
        id=rem_id,
        title=data.title,
        due_time=data.due_time,
        priority=data.priority or "medium",
        is_active=True,
        category=data.category or "general",
        created_at=created
    )


def toggle_reminder(reminder_id: str) -> Optional[ReminderOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        if not row:
            return None
        new_val = 0 if row["is_active"] else 1
        cursor.execute("UPDATE reminders SET is_active = ? WHERE id = ?", (new_val, reminder_id))
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
        r = cursor.fetchone()
        return ReminderOut(
            id=r["id"],
            title=r["title"],
            due_time=r["due_time"],
            priority=r["priority"],
            is_active=bool(r["is_active"]),
            category=r["category"],
            created_at=r["created_at"]
        )


# ---------------- Purchases CRUD ----------------
def get_purchases() -> List[PurchaseOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM purchases ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            PurchaseOut(
                id=r["id"],
                item_name=r["item_name"],
                quantity=r["quantity"],
                estimated_price=r["estimated_price"],
                status=r["status"],
                store=r["store"],
                created_at=r["created_at"]
            )
            for r in rows
        ]


def create_purchase(data: PurchaseCreate) -> PurchaseOut:
    purch_id = str(uuid.uuid4())
    created = now_iso()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO purchases (id, item_name, quantity, estimated_price, status, store, created_at)
            VALUES (?, ?, ?, ?, 'pending_approval', ?, ?)
        """, (purch_id, data.item_name.strip(), data.quantity or 1, data.estimated_price or 0.0, data.store or "Amazon", created))
    return PurchaseOut(
        id=purch_id,
        item_name=data.item_name,
        quantity=data.quantity or 1,
        estimated_price=data.estimated_price or 0.0,
        status="pending_approval",
        store=data.store or "Amazon",
        created_at=created
    )


def approve_purchase(purchase_id: str) -> Optional[PurchaseOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE purchases SET status = 'approved_ordered' WHERE id = ?", (purchase_id,))
        if cursor.rowcount == 0:
            return None
        cursor.execute("SELECT * FROM purchases WHERE id = ?", (purchase_id,))
        r = cursor.fetchone()
        return PurchaseOut(
            id=r["id"],
            item_name=r["item_name"],
            quantity=r["quantity"],
            estimated_price=r["estimated_price"],
            status=r["status"],
            store=r["store"],
            created_at=r["created_at"]
        )


# ---------------- Smart Devices (Simulated) CRUD ----------------
def get_devices() -> List[DeviceOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM smart_devices ORDER BY name ASC")
        rows = cursor.fetchall()
        devices = []
        for r in rows:
            try:
                state = json.loads(r["state_json"])
            except Exception:
                state = {}
            devices.append(DeviceOut(
                id=r["id"],
                name=r["name"],
                room=r["room"],
                device_type=r["device_type"],
                state=state,
                is_simulated=bool(r["is_simulated"]),
                disclaimer=r["disclaimer"]
            ))
        return devices


def update_device_state(device_id: str, new_state: Dict[str, Any]) -> Optional[DeviceOut]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state_json FROM smart_devices WHERE id = ?", (device_id,))
        row = cursor.fetchone()
        if not row:
            return None
        try:
            curr_state = json.loads(row["state_json"])
        except Exception:
            curr_state = {}
        curr_state.update(new_state)
        updated_json = json.dumps(curr_state)
        cursor.execute("UPDATE smart_devices SET state_json = ? WHERE id = ?", (updated_json, device_id))
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM smart_devices WHERE id = ?", (device_id,))
        r = cursor.fetchone()
        return DeviceOut(
            id=r["id"],
            name=r["name"],
            room=r["room"],
            device_type=r["device_type"],
            state=json.loads(r["state_json"]),
            is_simulated=bool(r["is_simulated"]),
            disclaimer=r["disclaimer"]
        )
