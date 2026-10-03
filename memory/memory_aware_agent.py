import json
import ollama
from memory.memory_store import MemoryStore

MODEL = "llama3.2"

store = MemoryStore()


def call_model(messages):
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        options={
            "temperature": 0.1,
            "num_predict": 800
        }
    )

    return response["message"]["content"]


def get_context(user_id, conversation_id):
    conversation = store.get_conversation(
        user_id,
        conversation_id
    )

    memories = store.get_user_memories(user_id)

    return {
        "conversation": conversation,
        "memories": memories
    }


def decide_memory_action(user_id, conversation_id, message):
    context = get_context(
        user_id,
        conversation_id
    )

    prompt = f"""
You are a memory decision component for an AI project management assistant.

Decide whether the user's message requires:
- remembering new information
- updating existing memory
- retrieving relevant memory
- using conversation context
- no memory operation

User ID:
{user_id}

Current conversation:
{json.dumps(context["conversation"], indent=2)}

Existing user memories:
{json.dumps(context["memories"], indent=2)}

User message:
{message}

Return ONLY valid JSON.

Use this format:

{{
  "action": "remember|update|retrieve|context|none",
  "key": "string",
  "value": "string",
  "reason": "string"
}}

Rules:
- Only store information that is useful for future conversations.
- Explicit requests such as "remember" should be stored.
- If the user changes an existing preference, update it.
- Retrieve memory only when it is relevant to the current request.
- Use conversation context for references such as "that project" or "the previous task".
- Do not retrieve unrelated memories.
- Never use memories belonging to another user.
- Do not invent memory.
"""

    raw = call_model(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    try:
        start = raw.find("{")
        end = raw.rfind("}")

        if start >= 0 and end > start:
            return json.loads(raw[start:end + 1])
    except Exception:
        pass

    return {
        "action": "none",
        "key": "",
        "value": "",
        "reason": "Unable to determine a memory operation."
    }


def process_message(user_id, conversation_id, message):
    store.add_conversation(
        user_id,
        conversation_id,
        "user",
        message
    )

    decision = decide_memory_action(
        user_id,
        conversation_id,
        message
    )

    action = decision.get("action")

    memory_used = []

    if action == "remember":
        key = decision.get("key") or "user_preference"
        value = decision.get("value")

        if value:
            store.add_memory(
                user_id,
                "preference",
                key,
                value
            )

            response = f"I'll remember that {value}."

        else:
            response = "I could not identify information to remember."

    elif action == "update":
        key = decision.get("key") or "user_preference"
        value = decision.get("value")

        if value:
            store.update_memory(
                user_id,
                "preference",
                key,
                value
            )

            response = f"Updated your saved preference to {value}."

        else:
            response = "I could not identify the updated preference."

    elif action == "retrieve":
        memory_used = store.get_relevant_memories(
            user_id,
            message
        )

        if memory_used:
            response = call_model(
                [
                    {
                        "role": "system",
                        "content": "Answer using only relevant user memory and conversation context."
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "message": message,
                                "memory": memory_used,
                                "conversation": store.get_conversation(
                                    user_id,
                                    conversation_id
                                )
                            },
                            indent=2
                        )
                    }
                ]
            )
        else:
            response = "I do not have relevant saved information for this request."

    elif action == "context":
        conversation = store.get_conversation(
            user_id,
            conversation_id
        )

        response = call_model(
            [
                {
                    "role": "system",
                    "content": "Use the current conversation context to resolve references. Do not use unrelated long-term memory."
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "message": message,
                            "conversation": conversation
                        },
                        indent=2
                    )
                }
            ]
        )

    else:
        response = call_model(
            [
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

    store.add_conversation(
        user_id,
        conversation_id,
        "assistant",
        response
    )

    return {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message": message,
        "memory_decision": decision,
        "memory_used": memory_used,
        "response": response
    }