import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from starlette.testclient import TestClient
from app.main import app
from app.database import db_session

client = TestClient(app)

def test_full_mastery_cycle():
    print("\n--- Testing Full Mastery Completion Flow ---")
    reg_res = client.post("/api/auth/register", json={
        "name": "Mastery Student",
        "email": f"mastery_{id(app)}@cognify.ai",
        "password": "Password123!"
    })
    token = reg_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Use topic with 2 concepts (e.g. C++ Exception Handling)
    curated = client.get("/api/topics/curated").json()
    cpp_topic = next((t for t in curated if "C++" in t["subject"]), curated[-1])
    
    start_res = client.post("/api/learning/start", json={"topic_id": cpp_topic["id"]}, headers=headers)
    session_data = start_res.json()
    session_id = session_data["session_id"]
    total_concepts = session_data["total_concepts"]

    with db_session() as conn:
        row = conn.cursor().execute("SELECT concepts_json FROM topics WHERE id = ?", (cpp_topic["id"],)).fetchone()
        concepts = json.loads(row["concepts_json"])

    # Cycle through each concept, answering questions correctly
    for c_idx in range(total_concepts):
        concept = concepts[c_idx]
        q = concept["questions"][0]
        
        # Submit correct answer
        ans_res = client.post("/api/learning/answer", json={
            "session_id": session_id,
            "concept_id": concept["id"],
            "question_id": q["id"],
            "selected_option_index": q["correct_index"],
            "response_time_seconds": 8.0,
            "attempts": 1,
            "hints_used": 0,
            "skipped": False,
            "time_since_last_action": 2.0
        }, headers=headers)
        assert ans_res.status_code == 200
        assert ans_res.json()["is_correct"] is True

        # Advance
        next_res = client.post("/api/learning/next-concept", json={"session_id": session_id}, headers=headers)
        assert next_res.status_code == 200
        next_data = next_res.json()

        if c_idx == total_concepts - 1:
            assert next_data["completed"] is True
            m_res = next_data["mastery_result"]
            print(f"Final Mastery Result -> Mastered: {m_res['is_mastered']}, Score: {m_res['mastery_score']}%")
            assert m_res["is_mastered"] is True
            assert len(m_res["concepts_mastered"]) >= 2
            print(f"Mastered concepts: {m_res['concepts_mastered']}")
            print(f"Summary: {m_res['summary_text']}")
            print(f"Next recommended: {m_res['recommendations']['suggested_next_topic']}")

    print("\n FULL MASTERY CYCLE TEST PASSED!")

if __name__ == "__main__":
    test_full_mastery_cycle()
