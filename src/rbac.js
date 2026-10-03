const fs = require("fs");
const path = require("path");
const { PERMISSIONS } = require("./permissions");

const employeesPath = path.join(
  __dirname,
  "..",
  "data",
  "project_management",
  "employees.json"
);

const rolesPath = path.join(
  __dirname,
  "..",
  "data",
  "project_management",
  "roles.json"
);

function loadEmployees() {
  const data = fs.readFileSync(employeesPath, "utf8");
  return JSON.parse(data);
}

function loadRoles() {
  const data = fs.readFileSync(rolesPath, "utf8");
  return JSON.parse(data);
}

function getEmployee(employeeId) {
  const employees = loadEmployees();

  return employees.find(
    employee => employee.employee_id === employeeId
  );
}

function getRole(employeeId) {
  const employee = getEmployee(employeeId);

  if (!employee) {
    return {
      success: false,
      error: "Employee not found"
    };
  }

  if (!employee.role) {
    return {
      success: false,
      error: "Employee role is not configured"
    };
  }

  return {
    success: true,
    employeeId: employee.employee_id,
    name: employee.name,
    role: employee.role
  };
}

function hasPermission(employeeId, permission) {
  if (!Object.values(PERMISSIONS).includes(permission)) {
    return {
      allowed: false,
      reason: "Invalid permission"
    };
  }

  const employee = getEmployee(employeeId);

  if (!employee) {
    return {
      allowed: false,
      reason: "Employee not found"
    };
  }

  if (!employee.role) {
    return {
      allowed: false,
      reason: "Employee role is not configured"
    };
  }

  const roles = loadRoles();
  const role = roles[employee.role];

  if (!role) {
    return {
      allowed: false,
      employeeId,
      role: employee.role,
      reason: "Role is not configured"
    };
  }

  const allowed = role.permissions.includes(permission);

  return {
    allowed,
    employeeId,
    role: employee.role,
    permission,
    reason: allowed
      ? "Permission granted"
      : "Permission denied"
  };
}

function getPermissions(employeeId) {
  const employee = getEmployee(employeeId);

  if (!employee) {
    return {
      success: false,
      error: "Employee not found",
      permissions: []
    };
  }

  if (!employee.role) {
    return {
      success: false,
      error: "Employee role is not configured",
      permissions: []
    };
  }

  const roles = loadRoles();
  const role = roles[employee.role];

  if (!role) {
    return {
      success: false,
      error: "Role is not configured",
      permissions: []
    };
  }

  return {
    success: true,
    employeeId,
    role: employee.role,
    permissions: role.permissions
  };
}

module.exports = {
  getEmployee,
  getRole,
  hasPermission,
  getPermissions,
  PERMISSIONS
};