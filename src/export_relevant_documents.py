import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_FILE = ROOT / "data" / "documents.json"
OUTPUT_FILE = ROOT / "results" / "relevant_documents_full.txt"

DOCUMENT_IDS = {
    "HR_017",
    "HR_018",
    "HR_019",
    "HR_020",
    "HR_021",
    "HR_022",
    "HR_023",
    "HR_024",
    "HR_025",
    "HR_026",
    "HR_027",
    "HR_028",
    "HR_029",
    "HR_030",
    "HR_031",
    "HR_032",
    "HR_033",
    "HR_034",
    "HR_035",
    "HR_036",
    "HR_037",
    "HR_038",
    "HR_039",
    "HR_040",
    "HR_041",
    "HR_042",
    "HR_043",
    "HR_044",
    "HR_045",
    "HR_046",
    "HR_047",
    "HR_048",
    "HR_049",
    "HR_050",
    "HR_051",
    "HR_052",
    "HR_069",
    "HR_070",
    "HR_071",
    "HR_072",
    "HR_073",
    "HR_074",
    "HR_075",
    "HR_076",
    "HR_077",
    "HR_079",
    "HR_080",
    "HR_081",
    "HR_082",
    "HR_083",
    "HR_087",
    "HR_088",
    "HR_089",
    "HR_090",
    "HR_091",
    "HR_092"
}

with open(
    DOCUMENTS_FILE,
    "r",
    encoding="utf-8"
) as file:
    documents = json.load(file)

documents_by_id = {
    document["doc_id"]: document
    for document in documents
}

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    for doc_id in sorted(DOCUMENT_IDS):
        document = documents_by_id.get(doc_id)

        if not document:
            continue

        file.write("=" * 100 + "\n")
        file.write(f"{doc_id}\n")
        file.write("=" * 100 + "\n")
        file.write(document.get("text", ""))
        file.write("\n\n")

print(f"Saved to: {OUTPUT_FILE}")