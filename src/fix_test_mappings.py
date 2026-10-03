import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "test_questions.json"
OUTPUT_FILE = ROOT / "data" / "test_questions_corrected.json"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    questions = json.load(file)

corrected_mappings = {
    1: ["HR_001"],
    2: ["HR_002"],
    3: ["HR_002"],
    4: ["HR_004"],
    5: ["HR_005"],
    6: ["HR_006"],
    7: ["HR_007"],
    8: ["HR_008"],
    9: ["HR_009"],
    10: ["HR_010"],
    11: ["HR_011"],
    12: ["HR_012"],
    13: ["HR_013"],
    14: ["HR_014"],
    15: ["HR_015"],
    16: ["HR_016"],
    17: ["HR_017"],
    18: ["HR_017"],
    19: ["HR_017"],
    20: ["HR_038"],
    21: ["HR_019"],
    22: ["HR_050"],
    23: ["HR_049"],
    24: ["HR_046"],
    25: ["HR_048"],
    26: ["HR_056"],
    27: ["HR_087", "HR_088"],
    28: ["HR_087", "HR_088"],
    29: ["HR_089", "HR_090"],
    30: ["HR_069"],
    31: ["HR_071"],
    32: ["HR_076", "HR_077"],
    33: ["HR_076", "HR_077"],
    34: ["HR_079"],
    35: ["HR_079"],
    36: ["HR_079"],
    37: ["HR_034"],
    38: ["HR_035"],
    39: ["HR_036"],
    40: ["HR_035", "HR_036"]
}

for index, question in enumerate(questions, start=1):
    question["relevant_doc_ids"] = corrected_mappings[index]

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        questions,
        file,
        indent=2,
        ensure_ascii=False
    )

print(f"Saved corrected evaluation file to: {OUTPUT_FILE}")