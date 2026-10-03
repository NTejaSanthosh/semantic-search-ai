import json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


ROOT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = ROOT_DIR / "results"

input_file = RESULTS_DIR / "multi_agent_test_results.json"
output_file = RESULTS_DIR / "multi_agent_test_cases.xlsx"

with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

test_cases = data["results"]

workbook = Workbook()
sheet = workbook.active
sheet.title = "Multi-Agent Tests"

headers = [
    "Test ID",
    "Query",
    "Selected Agents",
    "Execution Order",
    "Status",
    "Final Answer"
]

sheet.append(headers)

for cell in sheet[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(
        horizontal="center",
        vertical="center"
    )

for test in test_cases:

    sheet.append([
        test.get("test_id", ""),
        test.get("query", ""),
        ", ".join(test.get("selected_agents", [])),
        " -> ".join(test.get("execution_order", [])),
        test.get("status", ""),
        test.get("final_answer", "")
    ])

for column in sheet.columns:

    max_length = 0
    column_letter = column[0].column_letter

    for cell in column:
        value = str(cell.value or "")

        if len(value) > max_length:
            max_length = len(value)

    sheet.column_dimensions[column_letter].width = min(
        max_length + 2,
        60
    )

for row in sheet.iter_rows():
    for cell in row:
        cell.alignment = Alignment(
            vertical="top",
            wrap_text=True
        )

workbook.save(output_file)

print("Excel report created:")
print(output_file)