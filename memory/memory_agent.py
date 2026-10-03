import re
from memory.memory_store import MemoryStore
from tools.project_tools import get_project, get_projects, get_tasks, get_project_updates

store = MemoryStore()


def extract_project_id(text):
    matches = re.findall(r"\bP\d{3}\b", text.upper())
    return matches[0] if matches else None


def extract_priority_project(text):
    match = re.search(
        r"(?:project\s+)?(P\d{3})\s+(?:is|should be)\s+(?:my\s+)?priority",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).upper()

    match = re.search(
        r"(?:my\s+priority\s+(?:is|should be)\s+)(P\d{3})",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).upper()

    return None


def is_priority_update(text):
    text_lower = text.lower()

    return (
        "priority" in text_lower
        and (
            "remember" in text_lower
            or "no longer" in text_lower
            or "not my priority" in text_lower
            or "priority now" in text_lower
            or "priority is" in text_lower
        )
    )


def handle_memory_update(user_id, text):
    project_id = extract_priority_project(text)

    if "no longer" in text.lower() or "not my priority" in text.lower():
        if project_id:
            store.remove_memory(
                user_id,
                "preference",
                "priority_project"
            )

            store.add_memory(
                user_id,
                "preference",
                "priority_project",
                project_id,
                project_id
            )

            return (
                f"Updated your priority project. "
                f"{project_id} is now your priority."
            )

    if project_id and is_priority_update(text):
        store.add_memory(
            user_id,
            "preference",
            "priority_project",
            project_id,
            project_id
        )

        return f"Remembered that {project_id} is your priority project."

    return None


def resolve_project_reference(user_id, conversation_id, text):
    project_id = extract_project_id(text)

    if project_id:
        return project_id

    text_lower = text.lower()

    references = [
        "that project",
        "the previous project",
        "previous project",
        "this project"
    ]

    if any(reference in text_lower for reference in references):
        return store.get_last_project(
            user_id,
            conversation_id
        )

    return None


def get_priority_project(user_id):
    memories = store.get_user_memories(user_id)

    for memory in memories:
        if (
            memory.get("memory_type") == "preference"
            and memory.get("key") == "priority_project"
        ):
            return memory.get("project_id") or memory.get("value")

    return None


def analyze_project(project_id):
    project = get_project(project_id)

    if "error" in project:
        return f"I could not find project {project_id}."

    tasks = get_tasks(project_id)
    updates = get_project_updates(project_id)

    return {
        "project": project,
        "task_count": len(tasks),
        "updates": updates
    }


def process_message(user_id, conversation_id, text):
    store.add_conversation(
        user_id,
        conversation_id,
        "user",
        text
    )

    memory_response = handle_memory_update(
        user_id,
        text
    )

    if memory_response:
        store.add_conversation(
            user_id,
            conversation_id,
            "assistant",
            memory_response
        )

        return {
            "response": memory_response,
            "memory_used": [],
            "project": None
        }

    project_id = resolve_project_reference(
        user_id,
        conversation_id,
        text
    )

    if project_id:
        result = analyze_project(project_id)

        if isinstance(result, str):
            response = result
        else:
            response = (
                f"Project {project_id} is {result['project'].get('status')}. "
                f"It has {result['task_count']} tasks and "
                f"{len(result['updates'])} project updates."
            )

        store.add_conversation(
            user_id,
            conversation_id,
            "assistant",
            response
        )

        return {
            "response": response,
            "memory_used": [],
            "project": project_id
        }

    priority_project = get_priority_project(user_id)

    if (
        "what should i focus" in text.lower()
        or "what should i work" in text.lower()
        or "my priority" in text.lower()
    ):
        if priority_project:
            response = (
                f"Based on your saved preference, "
                f"you should focus on {priority_project}."
            )
        else:
            response = "I do not have a saved priority project for you."

        relevant = store.get_relevant_memories(
            user_id,
            text
        )

        store.add_conversation(
            user_id,
            conversation_id,
            "assistant",
            response
        )

        return {
            "response": response,
            "memory_used": relevant,
            "project": priority_project
        }

    relevant = store.get_relevant_memories(
        user_id,
        text
    )

    response = "I can answer using the current conversation context or relevant saved memories."

    store.add_conversation(
        user_id,
        conversation_id,
        "assistant",
        response
    )

    return {
        "response": response,
        "memory_used": relevant,
        "project": None
    }