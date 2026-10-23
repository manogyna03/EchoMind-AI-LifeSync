import json
import uuid
from datetime import datetime, timedelta
from app.database import db_session


def seed_initial_data():
    """Populates realistic initial data for demonstration if tables are empty."""
    with db_session() as conn:
        cursor = conn.cursor()

        # 1. Seed Tasks if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM tasks")
        if cursor.fetchone()["cnt"] == 0:
            now = datetime.now()
            sample_tasks = [
                ("Prepare presentation for Alexa+ Hackathon demo", "Outline Model Context Protocol architecture and LifeSync engine.", "work", "high", "pending", (now + timedelta(days=1)).strftime("%Y-%m-%d")),
                ("Buy almond milk and organic ground coffee", "Simulated auto-replenishment candidate for Amazon pantry.", "shopping", "medium", "pending", now.strftime("%Y-%m-%d")),
                ("Review weekly personal budget and utility bills", "Check electricity and internet subscription breakdown.", "personal", "low", "completed", (now - timedelta(days=2)).strftime("%Y-%m-%d")),
                ("Call Dr. Mehta for annual preventive health checkup", "Confirm Tuesday appointment time and fasting requirements.", "health", "high", "pending", (now + timedelta(days=3)).strftime("%Y-%m-%d")),
                ("Sync EchoMind MCP Tools with Alexa+ endpoint", "Verify JSON-RPC 2.0 tool definitions for task creation and memory recall.", "work", "high", "in_progress", now.strftime("%Y-%m-%d")),
            ]
            for title, desc, cat, prio, stat, due in sample_tasks:
                cursor.execute("""
                    INSERT INTO tasks (id, title, description, category, priority, status, due_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), title, desc, cat, prio, stat, due, now.isoformat()))

        # 2. Seed Schedule if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM schedule_events")
        if cursor.fetchone()["cnt"] == 0:
            today_str = datetime.now().strftime("%Y-%m-%d")
            sample_events = [
                ("Morning Focus & LifeSync Review", today_str, "09:00 AM", 45, "Home Office", "personal", 1),
                ("Alexa+ Hackathon Architecture Sync", today_str, "11:30 AM", 60, "Virtual Conference", "work", 0),
                ("Healthy Lunch & Mindful Walk", today_str, "01:00 PM", 45, "Terrace Garden", "health", 0),
                ("EchoMind Voice Assistant Testing Session", today_str, "03:30 PM", 60, "Lab / Workstation", "work", 0),
                ("Evening Wind-down & Smart Home Automation", today_str, "08:00 PM", 30, "Living Room", "home", 0),
            ]
            for title, ev_date, start, dur, loc, cat, comp in sample_events:
                cursor.execute("""
                    INSERT INTO schedule_events (id, title, event_date, start_time, duration_mins, location, category, is_completed, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), title, ev_date, start, dur, loc, cat, comp, datetime.now().isoformat()))

        # 3. Seed Memory (LifeSync Long-Term Memory)
        cursor.execute("SELECT COUNT(*) as cnt FROM memory_items")
        if cursor.fetchone()["cnt"] == 0:
            sample_memories = [
                ("Coffee Preference", "Prefers single-origin pour-over with oat milk, unsweetened, served at 65°C.", "preference", 0.98),
                ("Work Focus Hours", "Peak cognitive energy window is between 09:30 AM and 01:00 PM. Avoid non-urgent interruptions.", "context", 0.95),
                ("Alexa+ Hackathon Submission Deadline", "Submission cut-off is October 23, 2026. Needs working demo video and zero-cost local runnable codebase.", "personal", 1.0),
                ("Emergency Contact", "Primary contact is Anita (Sister), phone ending in 4821.", "family", 1.0),
                ("Home Office Temperature", "Preferred ambient working temperature is 22°C (72°F) with moderate air circulation.", "preference", 0.92)
            ]
            for key, val, cat, conf in sample_memories:
                cursor.execute("""
                    INSERT INTO memory_items (id, key_topic, value_fact, category, confidence, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), key, val, cat, conf, datetime.now().isoformat()))

        # 4. Seed Reminders
        cursor.execute("SELECT COUNT(*) as cnt FROM reminders")
        if cursor.fetchone()["cnt"] == 0:
            sample_reminders = [
                ("Drink 500ml water and stretch shoulders", "Every 2 hours", "medium", 1, "health"),
                ("Submit Alexa+ MCP integration demo checklist", "Today at 06:00 PM", "high", 1, "work"),
                ("Take evening multivitamin and omega-3 supplement", "Tonight at 09:30 PM", "low", 1, "health"),
            ]
            for title, due, prio, act, cat in sample_reminders:
                cursor.execute("""
                    INSERT INTO reminders (id, title, due_time, priority, is_active, category, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), title, due, prio, act, cat, datetime.now().isoformat()))

        # 5. Seed Purchases (Simulated Alexa+ Commerce)
        cursor.execute("SELECT COUNT(*) as cnt FROM purchases")
        if cursor.fetchone()["cnt"] == 0:
            sample_purchases = [
                ("Organic Fair-Trade Dark Roast Coffee Beans (1kg)", 1, 650.00, "pending_approval", "Amazon Fresh"),
                ("Ergonomic Gel Wrist Rest for Mechanical Keyboard", 1, 499.00, "approved_ordered", "Amazon"),
                ("Microfiber Cleaning Cloths (Pack of 6)", 2, 249.00, "delivered", "Amazon Basics"),
            ]
            for item, qty, price, status, store in sample_purchases:
                cursor.execute("""
                    INSERT INTO purchases (id, item_name, quantity, estimated_price, status, store, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), item, qty, price, status, store, datetime.now().isoformat()))

        # 6. Seed Smart Devices (SIMULATED - Clearly labeled)
        cursor.execute("SELECT COUNT(*) as cnt FROM smart_devices")
        if cursor.fetchone()["cnt"] == 0:
            sample_devices = [
                ("dev_light_living", "[SIMULATION] Living Room Ambient Lights", "Living Room", "light", json.dumps({"power": True, "brightness": 75, "color": "warm_white"})),
                ("dev_thermo_main", "[SIMULATION] Eco Home Thermostat", "Hallway", "thermostat", json.dumps({"power": True, "target_temp": 22, "current_temp": 23, "mode": "cool"})),
                ("dev_lock_front", "[SIMULATION] Smart Front Door Lock", "Entryway", "lock", json.dumps({"locked": True, "battery": 94})),
                ("dev_plug_coffee", "[SIMULATION] Kitchen Coffee Maker Plug", "Kitchen", "plug", json.dumps({"power": False, "watts": 0})),
                ("dev_light_office", "[SIMULATION] Study Desk Task Light", "Office", "light", json.dumps({"power": True, "brightness": 90, "color": "daylight"})),
            ]
            for d_id, name, room, dtype, state_json in sample_devices:
                cursor.execute("""
                    INSERT INTO smart_devices (id, name, room, device_type, state_json, is_simulated, disclaimer)
                    VALUES (?, ?, ?, ?, ?, 1, 'Simulated device for Amazon Alexa+ testing without hardware requirement.')
                """, (d_id, name, room, dtype, state_json))
