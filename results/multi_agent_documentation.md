# Multi-Agent Collaboration - Project Management System

## 1. Objective

The objective of this implementation is to understand how multiple specialized AI agents can collaborate to solve project management queries.

Instead of using one agent for every task, the system separates responsibilities into specialized agents and introduces a Coordinator Agent.

## 2. Architecture

The system contains four agents:

1. Coordinator Agent
2. Project Agent
3. Task Agent
4. Employee / Workload Agent

The Coordinator receives the user query, determines which specialized agents are required, executes them in an appropriate order, passes relevant results between agents, and combines the results into the final response.

## 3. Project Agent

The Project Agent handles:

- Project information
- Project status
- Project risk
- Project metrics
- Project updates

## 4. Task Agent

The Task Agent handles:

- Task information
- Overdue tasks
- Completed tasks
- Pending tasks
- In-progress tasks
- Task status

## 5. Employee / Workload Agent

The Employee / Workload Agent handles:

- Employee information
- Task ownership
- Employee workload
- Task count
- Estimated hours
- Actual hours

## 6. Coordinator Agent

The Coordinator Agent:

1. Receives the user query.
2. Determines which specialized agents are required.
3. Selects the execution order.
4. Passes project information to the Task Agent when required.
5. Passes task information to the Employee Agent when required.
6. Collects the results.
7. Combines the results into a final answer.

## 7. Collaboration Flow

Example query:

"Which risky projects have overdue tasks and who is responsible for them?"

The flow is:

User Query
→ Coordinator Agent
→ Project Agent
→ Risky Projects
→ Task Agent
→ Overdue Tasks
→ Employee Agent
→ Responsible Employees
→ Coordinator Agent
→ Final Answer

## 8. Test Cases

### T01 - Single Agent

Query:

"What is the risk level of P006?"

Expected agents:

Project Agent

### T02 - Single Agent

Query:

"Show me the overdue tasks in P006."

Expected agents:

Task Agent

### T03 - Single Agent

Query:

"Which employees have high workload?"

Expected agents:

Employee / Workload Agent

### T04 - Multiple Agents

Query:

"Which projects have overdue tasks?"

Expected agents:

Project Agent and Task Agent

### T05 - Multiple Agent Collaboration

Query:

"Which risky projects have overdue tasks and who is responsible for them?"

Expected agents:

Project Agent, Task Agent and Employee / Workload Agent

### T06 - Ambiguous Query

Query:

"What is happening with P006?"

The Coordinator decides which agents can provide useful project and task context.

## 9. Key Learning

The main difference between a single-agent and multi-agent architecture is specialization and collaboration.

Instead of one agent handling every responsibility, each specialized agent focuses on a specific domain and the Coordinator manages the overall problem-solving process.

## 10. Conclusion

The Multi-Agent Project Management system demonstrates how specialized agents can collaborate through a Coordinator Agent to solve simple, multi-domain and ambiguous project management queries.