const {
  getRole,
  getPermissions,
  hasPermission,
  PERMISSIONS
} = require("./rbac");

const employeeId = process.argv[2];

if (!employeeId) {
  console.log("Usage: node src/test_rbac.js <employee_id>");
  process.exit(1);
}

console.log("\nEmployee Role");
console.log("-------------");

console.log(
  JSON.stringify(
    getRole(employeeId),
    null,
    2
  )
);

console.log("\nEmployee Permissions");
console.log("--------------------");

console.log(
  JSON.stringify(
    getPermissions(employeeId),
    null,
    2
  )
);

console.log("\nVIEW_TASK");
console.log("---------");

console.log(
  JSON.stringify(
    hasPermission(
      employeeId,
      PERMISSIONS.VIEW_TASK
    ),
    null,
    2
  )
);

console.log("\nUPDATE_TASK");
console.log("-----------");

console.log(
  JSON.stringify(
    hasPermission(
      employeeId,
      PERMISSIONS.UPDATE_TASK
    ),
    null,
    2
  )
);

console.log("\nASSIGN_TASK");
console.log("-----------");

console.log(
  JSON.stringify(
    hasPermission(
      employeeId,
      PERMISSIONS.ASSIGN_TASK
    ),
    null,
    2
  )
);