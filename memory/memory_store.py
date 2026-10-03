import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE_DIR / "data" / "agent_memory"
MEMORIES_FILE = MEMORY_DIR / "memories.json"
CONVERSATIONS_FILE = MEMORY_DIR / "conversations.json"

MEMORY_DIR.mkdir(parents=True, exist_ok=True)

if not MEMORIES_FILE.exists():
    MEMORIES_FILE.write_text("[]", encoding="utf-8")

if not CONVERSATIONS_FILE.exists():
    CONVERSATIONS_FILE.write_text("[]", encoding="utf-8")


def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def now():
    return datetime.now().isoformat(timespec="seconds")


class MemoryStore:

    def __init__(self):
        self.memories = load_json(MEMORIES_FILE)
        self.conversations = load_json(CONVERSATIONS_FILE)

    def save(self):
        save_json(MEMORIES_FILE, self.memories)
        save_json(CONVERSATIONS_FILE, self.conversations)

    def add_memory(self, user_id, memory_type, key, value, project_id=None):
        existing = None

        for memory in self.memories:
            if (
                memory.get("user_id") == user_id
                and memory.get("memory_type") == memory_type
                and memory.get("key") == key
                and memory.get("status") == "active"
            ):
                existing = memory
                break

        if existing:
            existing["value"] = value
            existing["project_id"] = project_id
            existing["updated_at"] = now()
        else:
            memory_id = f"M{len(self.memories) + 1:04d}"

            self.memories.append(
                {
                    "memory_id": memory_id,
                    "user_id": user_id,
                    "memory_type": memory_type,
                    "key": key,
                    "value": value,
                    "project_id": project_id,
                    "status": "active",
                    "created_at": now(),
                    "updated_at": now()
                }
            )

        self.save()

    def update_memory(self, user_id, memory_type, key, value, project_id=None):
        return self.add_memory(
            user_id,
            memory_type,
            key,
            value,
            project_id
        )

    def remove_memory(self, user_id, memory_type, key):
        changed = False

        for memory in self.memories:
            if (
                memory.get("user_id") == user_id
                and memory.get("memory_type") == memory_type
                and memory.get("key") == key
                and memory.get("status") == "active"
            ):
                memory["status"] = "inactive"
                memory["updated_at"] = now()
                changed = True

        if changed:
            self.save()

        return changed

    def get_user_memories(self, user_id):
        return [
            memory
            for memory in self.memories
            if memory.get("user_id") == user_id
            and memory.get("status") == "active"
        ]

    def get_relevant_memories(self, user_id, query):
        query_lower = query.lower()
        memories = self.get_user_memories(user_id)

        relevant = []

        for memory in memories:
            value = str(memory.get("value", "")).lower()
            key = str(memory.get("key", "")).lower()
            project_id = str(memory.get("project_id", "")).lower()

            if (
                key in query_lower
                or value in query_lower
                or project_id in query_lower
                or any(word in query_lower for word in value.split())
            ):
                relevant.append(memory)

        return relevant

    def add_conversation(self, user_id, conversation_id, role, content):
        conversation = None

        for item in self.conversations:
            if (
                item.get("user_id") == user_id
                and item.get("conversation_id") == conversation_id
            ):
                conversation = item
                break

        if conversation is None:
            conversation = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "messages": [],
                "updated_at": now()
            }
            self.conversations.append(conversation)

        conversation["messages"].append(
            {
                "role": role,
                "content": content,
                "timestamp": now()
            }
        )

        conversation["updated_at"] = now()

        self.save()

    def get_conversation(self, user_id, conversation_id):
        for conversation in self.conversations:
            if (
                conversation.get("user_id") == user_id
                and conversation.get("conversation_id") == conversation_id
            ):
                return conversation

        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "messages": []
        }

    def get_last_project(self, user_id, conversation_id):
        conversation = self.get_conversation(
            user_id,
            conversation_id
        )

        messages = conversation.get("messages", [])

        for message in reversed(messages):
            content = str(message.get("content", ""))

            words = content.upper().replace(",", " ").replace(".", " ").split()

            for word in words:
                if word.startswith("P") and len(word) == 4 and word[1:].isdigit():
                    return word

        return None