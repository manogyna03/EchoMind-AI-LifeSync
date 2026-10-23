from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# Task Schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")
    description: Optional[str] = ""
    category: Optional[str] = "general"
    priority: Optional[str] = "medium"  # low, medium, high
    status: Optional[str] = "pending"   # pending, in_progress, completed
    due_date: Optional[str] = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


class TaskOut(BaseModel):
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    due_date: str
    created_at: str


# Schedule Schemas
class ScheduleCreate(BaseModel):
    title: str
    event_date: str
    start_time: str
    duration_mins: Optional[int] = 30
    location: Optional[str] = ""
    category: Optional[str] = "general"


class ScheduleOut(BaseModel):
    id: str
    title: str
    event_date: str
    start_time: str
    duration_mins: int
    location: str
    category: str
    is_completed: bool
    created_at: str


# Memory Schemas
class MemoryCreate(BaseModel):
    key_topic: str
    value_fact: str
    category: Optional[str] = "personal"


class MemoryOut(BaseModel):
    id: str
    key_topic: str
    value_fact: str
    category: str
    confidence: float
    updated_at: str


# Reminder Schemas
class ReminderCreate(BaseModel):
    title: str
    due_time: str
    priority: Optional[str] = "medium"
    category: Optional[str] = "general"


class ReminderOut(BaseModel):
    id: str
    title: str
    due_time: str
    priority: str
    is_active: bool
    category: str
    created_at: str


# Purchase Schemas
class PurchaseCreate(BaseModel):
    item_name: str
    quantity: Optional[int] = 1
    estimated_price: Optional[float] = 0.0
    store: Optional[str] = "Amazon"


class PurchaseOut(BaseModel):
    id: str
    item_name: str
    quantity: int
    estimated_price: float
    status: str
    store: str
    created_at: str


# Smart Device Schemas
class DeviceStateUpdate(BaseModel):
    state: Dict[str, Any]


class DeviceOut(BaseModel):
    id: str
    name: str
    room: str
    device_type: str
    state: Dict[str, Any]
    is_simulated: bool = True
    disclaimer: str


# Assistant Interaction Schema
class AssistantRequest(BaseModel):
    message: str
    voice_mode: Optional[bool] = False


class AssistantResponse(BaseModel):
    reply: str
    speech_text: str
    intent_detected: str
    action_taken: Optional[Dict[str, Any]] = None
    target_section: Optional[str] = "assistant"
