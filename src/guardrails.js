const {
  hasPermission,
  getRole,
  PERMISSIONS
} = require("./rbac");

const MAX_TOOL_CALLS = 10;

const SENSITIVE_ACTIONS = {
  UPDATE_TASK: PERMISSIONS.UPDATE_TASK,
  ASSIGN_TASK: PERMISSIONS.ASSIGN_TASK
};

const PROMPT_INJECTION_PATTERNS = [
  /ignore\s+(all\s+)?previous\s+instructions/i,
  /ignore\s+(all\s+)?prior\s+instructions/i,
  /bypass\s+(the\s+)?permission/i,
  /bypass\s+(the\s+)?security/i,
  /disable\s+(the\s+)?guardrails/i,
  /override\s+(the\s+)?system/i,
  /reveal\s+(the\s+)?system\s+prompt/i,
  /show\s+(me\s+)?the\s+system\s+prompt/i,
  /forget\s+(all\s+)?previous\s+instructions/i
];

function detectPromptInjection(query) {
  if (!query || typeof query !== "string") {
    return false;
  }

  return PROMPT_INJECTION_PATTERNS.some(
    pattern => pattern.test(query)
  );
}

function validateEmployee(employeeId) {
  if (!employeeId) {
    return {
      allowed: false,
      reason: "Employee ID is required"
    };
  }

  const roleResult = getRole(employeeId);

  if (!roleResult.success) {
    return {
      allowed: false,
      reason: roleResult.error
    };
  }

  return {
    allowed: true,
    employeeId,
    role: roleResult.role
  };
}

function authorize(employeeId, permission) {
  return hasPermission(
    employeeId,
    permission
  );
}

function validateQuery(query) {
  if (
    typeof query !== "string" ||
    query.trim().length === 0
  ) {
    return {
      valid: false,
      reason: "Query must be a non-empty string"
    };
  }

  if (query.length > 5000) {
    return {
      valid: false,
      reason: "Query is too long"
    };
  }

  return {
    valid: true
  };
}

function createToolCallGuard() {
  let toolCallCount = 0;
  const executedCalls = new Set();

  return {
    canCall(toolName, args = {}) {
      if (toolCallCount >= MAX_TOOL_CALLS) {
        return {
          allowed: false,
          reason: "Maximum tool-call limit reached"
        };
      }

      const callKey = `${toolName}:${JSON.stringify(args)}`;

      if (executedCalls.has(callKey)) {
        return {
          allowed: false,
          reason: "Duplicate tool call blocked"
        };
      }

      return {
        allowed: true
      };
    },

    recordCall(toolName, args = {}) {
      toolCallCount += 1;

      const callKey = `${toolName}:${JSON.stringify(args)}`;

      executedCalls.add(callKey);
    },

    getCount() {
      return toolCallCount;
    }
  };
}

function guardRequest({
  query,
  employeeId
}) {
  const queryResult = validateQuery(query);

  if (!queryResult.valid) {
    return {
      allowed: false,
      status: "invalid_input",
      message: queryResult.reason
    };
  }

  const employeeResult = validateEmployee(
    employeeId
  );

  if (!employeeResult.allowed) {
    return {
      allowed: false,
      status: "unauthorized",
      message: employeeResult.reason
    };
  }

  if (detectPromptInjection(query)) {
    return {
      allowed: false,
      status: "prompt_injection",
      message:
        "The request contains instructions that attempt to bypass system security or access controls."
    };
  }

  return {
    allowed: true,
    status: "authorized",
    employeeId,
    role: employeeResult.role
  };
}

module.exports = {
  MAX_TOOL_CALLS,
  SENSITIVE_ACTIONS,
  detectPromptInjection,
  validateEmployee,
  authorize,
  validateQuery,
  createToolCallGuard,
  guardRequest,
  PERMISSIONS
};