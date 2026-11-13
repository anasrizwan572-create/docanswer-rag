import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

smoke_questions = [
    "What is the length of the introductory probationary period for new hires?",
    "What are the designated Core Collaboration Hours and timezone?",
    "How much is the one-time home office setup allowance for remote workers?",
    "If an employee resigns 18 months after tuition reimbursement, what clawback applies?",
    "What is the reimbursement limit for pet health insurance and veterinary care?"
]

print("=" * 75)
print("                   DOCANSWER 5-QUESTION SMOKE TEST")
print("=" * 75)

for idx, q in enumerate(smoke_questions, 1):
    res = client.post("/api/query", json={"question": q})
    data = res.json()
    status_code = res.status_code
    found = data.get("found")
    conf = data.get("confidence")
    ans = data.get("answer", "")
    cits = data.get("citations", [])

    print(f"\n[Test {idx}] {q}")
    print(f"Status Code: {status_code} | Found: {found} | Confidence: {conf}")
    print(f"Answer: {ans[:150]}...")
    print(f"Citations Returned: {len(cits)}")
    for c in cits:
        print(f"  [{c['id']}] {c['section']} (Page {c['page']}) — Relevance: {c['score']}")
    print("-" * 75)

print("\n✅ Smoke test completed successfully!")
