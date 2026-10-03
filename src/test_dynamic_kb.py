from dynamic_kb import (
    show_document_count,
    add_document,
    update_document,
    delete_document
)

print("=" * 70)
print("INITIAL KNOWLEDGE BASE")
print("=" * 70)

show_document_count()

print()
print("=" * 70)
print("ADDING TEST DOCUMENT")
print("=" * 70)

add_document(
    doc_id="HR_TEST_121",
    title="Work From Home Policy",
    category="HR",
    source="Test Document",
    text="Employees can work from home with prior approval from their manager. Remote work requests must follow the company's approval process."
)

show_document_count()

print()
print("=" * 70)
print("UPDATING TEST DOCUMENT")
print("=" * 70)

update_document(
    doc_id="HR_TEST_121",
    title="Updated Work From Home Policy",
    category="HR",
    source="Test Document",
    text="Employees can request remote work for approved personal circumstances. The request must be reviewed by both the manager and HR before the remote work arrangement begins."
)

show_document_count()

print()
print("=" * 70)
print("DELETING TEST DOCUMENT")
print("=" * 70)

delete_document("HR_TEST_121")

show_document_count()

print()
print("=" * 70)
print("DYNAMIC KNOWLEDGE BASE TEST COMPLETED")
print("=" * 70)