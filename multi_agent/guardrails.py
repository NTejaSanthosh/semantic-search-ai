import json
import re
from enum import Enum


MAX_TOOL_CALLS = 10
MAX_QUERY_LENGTH = 5000


class GuardrailStatus(str, Enum):

    ALLOWED = "allowed"
    INVALID_INPUT = "invalid_input"
    UNAUTHORIZED = "unauthorized"
    PROMPT_INJECTION = "prompt_injection"
    TOOL_LIMIT = "tool_limit"
    DUPLICATE_CALL = "duplicate_call"
    TOOL_ERROR = "tool_error"


PROMPT_INJECTION_PATTERNS = [

    r"ignore\s+(all\s+)?previous\s+instructions",

    r"ignore\s+(all\s+)?prior\s+instructions",

    r"bypass\s+(the\s+)?permission",

    r"bypass\s+(the\s+)?security",

    r"disable\s+(the\s+)?guardrails",

    r"override\s+(the\s+)?system",

    r"reveal\s+(the\s+)?system\s+prompt",

    r"show\s+(me\s+)?the\s+system\s+prompt",

    r"forget\s+(all\s+)?previous\s+instructions",

    r"ignore\s+your\s+rules",

    r"disregard\s+(all\s+)?instructions"
]


def validate_query(query):

    if not isinstance(
        query,
        str
    ):

        return {
            "allowed": False,
            "status": GuardrailStatus.INVALID_INPUT.value,
            "reason": "Query must be a string"
        }

    if not query.strip():

        return {
            "allowed": False,
            "status": GuardrailStatus.INVALID_INPUT.value,
            "reason": "Query must not be empty"
        }

    if len(query) > MAX_QUERY_LENGTH:

        return {
            "allowed": False,
            "status": GuardrailStatus.INVALID_INPUT.value,
            "reason": (
                "Query exceeds the maximum allowed length"
            )
        }

    return {
        "allowed": True,
        "status": GuardrailStatus.ALLOWED.value
    }


def detect_prompt_injection(query):

    if not isinstance(
        query,
        str
    ):

        return False

    for pattern in PROMPT_INJECTION_PATTERNS:

        if re.search(
            pattern,
            query,
            re.IGNORECASE
        ):

            return True

    return False


def validate_employee_id(employee_id):

    if not isinstance(
        employee_id,
        str
    ):

        return {
            "allowed": False,
            "status": GuardrailStatus.UNAUTHORIZED.value,
            "reason": "Employee ID is required"
        }

    if not employee_id.strip():

        return {
            "allowed": False,
            "status": GuardrailStatus.UNAUTHORIZED.value,
            "reason": "Employee ID is required"
        }

    if not re.fullmatch(
        r"E\d+",
        employee_id.strip().upper()
    ):

        return {
            "allowed": False,
            "status": GuardrailStatus.UNAUTHORIZED.value,
            "reason": "Invalid employee ID format"
        }

    return {
        "allowed": True
    }


def guard_request(
    query,
    employee_id
):

    query_result = validate_query(
        query
    )

    if not query_result["allowed"]:
        return query_result

    employee_result = validate_employee_id(
        employee_id
    )

    if not employee_result["allowed"]:
        return employee_result

    if detect_prompt_injection(
        query
    ):

        return {
            "allowed": False,
            "status": GuardrailStatus.PROMPT_INJECTION.value,
            "reason": (
                "The request contains instructions "
                "that attempt to bypass system "
                "security or access controls"
            )
        }

    return {
        "allowed": True,
        "status": GuardrailStatus.ALLOWED.value
    }


class ToolCallGuard:

    def __init__(
        self,
        max_calls=MAX_TOOL_CALLS
    ):

        self.max_calls = max_calls
        self.call_count = 0
        self.executed_calls = set()

    def _create_call_key(
        self,
        tool_name,
        arguments
    ):

        normalized_arguments = json.dumps(
            arguments,
            sort_keys=True,
            default=str
        )

        return (
            tool_name,
            normalized_arguments
        )

    def can_call(
        self,
        tool_name,
        arguments=None
    ):

        if arguments is None:
            arguments = {}

        if self.call_count >= self.max_calls:

            return {
                "allowed": False,
                "status": GuardrailStatus.TOOL_LIMIT.value,
                "reason": (
                    "Maximum tool-call limit reached"
                )
            }

        call_key = self._create_call_key(
            tool_name,
            arguments
        )

        if call_key in self.executed_calls:

            return {
                "allowed": False,
                "status": GuardrailStatus.DUPLICATE_CALL.value,
                "reason": "Duplicate tool call blocked"
            }

        return {
            "allowed": True,
            "status": GuardrailStatus.ALLOWED.value
        }

    def record_call(
        self,
        tool_name,
        arguments=None
    ):

        if arguments is None:
            arguments = {}

        call_key = self._create_call_key(
            tool_name,
            arguments
        )

        self.executed_calls.add(
            call_key
        )

        self.call_count += 1

    def get_call_count(self):

        return self.call_count