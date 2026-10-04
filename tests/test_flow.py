import io
import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_adaptive_learning_flow():
    print("\n--- 1. Testing Registration & Authentication ---")
    reg_payload = {
        "name": "Integration Student",
        "email": f"test_student_{id(app)}@cognify.ai",
        "password": "Password123!"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    auth_data = reg_res.json()
    token = auth_data["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Registered user ID: {auth_data['user']['id']}, Token generated.")

    print("\n--- 2. Testing Curated Topics ---")
    topics_res = client.get("/api/topics/curated")
    assert topics_res.status_code == 200
    curated = topics_res.json()
    assert len(curated) >= 4, "Should have at least 4 curated topics"
    print(f"Loaded {len(curated)} curated topics. First: {curated[0]['topic_name']}")
    target_topic = curated[0]

    print("\n--- 3. Testing File Upload Validation ---")
    # Test invalid extension
    invalid_file = io.BytesIO(b"dummy executable file content")
    bad_res = client.post(
        "/api/materials/upload",
        files={"file": ("malicious.exe", invalid_file, "application/octet-stream")},
        headers=headers
    )
    assert bad_res.status_code == 400
    assert "Unsupported file type" in bad_res.json()["detail"]
    print("Invalid file type properly rejected with validation message.")

    # Test valid text upload
    valid_study_notes = (
        "# Operating System Virtual Memory Notes\n\n"
        "## Memory Virtualization Principles\n"
        "Virtual memory decouples logical address space from physical RAM.\n"
        "The Memory Management Unit hardware automatically maps Virtual Page Numbers to Physical Frame Numbers.\n"
        "The page offset is conserved throughout translation.\n\n"
        "## Hardware Translation Lookaside Buffer\n"
        "The TLB caches recent translations directly on the processor.\n"
        "A TLB hit avoids multi-level page table walks in system RAM.\n\n"
        "## Page Fault Handling & Eviction\n"
        "When a referenced page is not present in RAM, a hardware page fault trap triggers the OS kernel.\n"
        "The kernel retrieves the page from secondary storage and updates the page table entry.\n"
    )
    valid_file = io.BytesIO(valid_study_notes.encode("utf-8"))
    upload_res = client.post(
        "/api/materials/upload",
        files={"file": ("os_notes_lecture.txt", valid_file, "text/plain")},
        headers=headers
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    uploaded_data = upload_res.json()
    assert uploaded_data["concepts_count"] >= 2
    print(f"Uploaded file parsed! Grounded concepts extracted: {uploaded_data['concepts_count']}")

    print("\n--- 4. Testing Learning Session Launch ---")
    start_res = client.post(
        "/api/learning/start",
        json={"topic_id": target_topic["id"]},
        headers=headers
    )
    assert start_res.status_code == 200
    session_data = start_res.json()
    session_id = session_data["session_id"]
    concept_id = session_data["concept"]["id"]
    question_id = session_data["question"]["id"]
    print(f"Session started! Session ID: {session_id}, Concept: {session_data['concept']['title']}")

    print("\n--- 5. Testing Escalating Hint Tiers ---")
    # Tier 1 Hint
    h1 = client.post(
        "/api/learning/hint",
        json={"session_id": session_id, "concept_id": concept_id, "question_id": question_id, "hint_tier": 1},
        headers=headers
    )
    assert h1.status_code == 200
    assert "Tier 1" in h1.json()["tier_name"]

    # Tier 2 Hint
    h2 = client.post(
        "/api/learning/hint",
        json={"session_id": session_id, "concept_id": concept_id, "question_id": question_id, "hint_tier": 2},
        headers=headers
    )
    assert h2.status_code == 200
    assert "Tier 2" in h2.json()["tier_name"]
    print(f"Hint tier 1 & 2 retrieved successfully: {h1.json()['hint'][:40]}...")

    print("\n--- 6. Testing Quiz Submission & Cognitive Load Prediction ---")
    # Scenario A: High Cognitive Load (Long deliberation, multiple attempts, 2 hints)
    ans_high = client.post(
        "/api/learning/answer",
        json={
            "session_id": session_id,
            "concept_id": concept_id,
            "question_id": question_id,
            "selected_option_index": 0,  # potentially wrong or deliberate
            "response_time_seconds": 45.0,
            "attempts": 2,
            "hints_used": 2,
            "skipped": False,
            "time_since_last_action": 15.0
        },
        headers=headers
    )
    assert ans_high.status_code == 200
    high_data = ans_high.json()
    assert "cognitive_load" in high_data
    assert "adaptation" in high_data
    print(f"High Load Test Result -> Predicted Load: {high_data['cognitive_load']['predicted_load']}, "
          f"Adapted Style: {high_data['adaptation']['teaching_style']}")

    # Scenario B: Low Cognitive Load (Fast response 4.2s, 1 attempt, 0 hints, correct answer)
    from app.database import db_session
    with db_session() as conn:
        row = conn.cursor().execute("SELECT concepts_json FROM topics WHERE id = ?", (target_topic["id"],)).fetchone()
        raw_concepts = json.loads(row["concepts_json"])
        correct_idx = 0
        for c in raw_concepts:
            for q in c.get("questions", []):
                if q["id"] == question_id:
                    correct_idx = q["correct_index"]
                    break

    ans_low = client.post(
        "/api/learning/answer",
        json={
            "session_id": session_id,
            "concept_id": concept_id,
            "question_id": question_id,
            "selected_option_index": correct_idx,
            "response_time_seconds": 5.2,
            "attempts": 1,
            "hints_used": 0,
            "skipped": False,
            "time_since_last_action": 2.0
        },
        headers=headers
    )
    assert ans_low.status_code == 200
    low_data = ans_low.json()
    assert low_data["is_correct"] is True
    print(f"Low Load Test Result -> Predicted Load: {low_data['cognitive_load']['predicted_load']}, "
          f"Next Difficulty: {low_data['adaptation']['next_difficulty']}")

    print("\n--- 7. Testing Advancing Through Concepts ---")
    next_res = client.post(
        "/api/learning/next-concept",
        json={"session_id": session_id},
        headers=headers
    )
    assert next_res.status_code == 200
    next_data = next_res.json()
    print(f"Advanced concept! New index: {next_data.get('concept_index')}, Completed: {next_data.get('completed')}")

    print("\n--- 8. Testing Topic Mastery Check ---")
    mastery_res = client.post(
        "/api/learning/check-mastery",
        json={"session_id": session_id},
        headers=headers
    )
    assert mastery_res.status_code == 200
    mastery_data = mastery_res.json()
    assert "mastery_score" in mastery_data
    assert "concepts_mastered" in mastery_data
    assert "recommendations" in mastery_data
    print(f"Mastery Check -> Score: {mastery_data['mastery_score']}%, "
          f"Mastered: {mastery_data['is_mastered']}, "
          f"Next: {mastery_data['recommendations']['suggested_next_topic']['topic']}")

    print("\n--- 9. Testing Dashboard Metrics Aggregation ---")
    dash_res = client.get("/api/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_questions_solved"] >= 2
    assert dash_data["accuracy_percent"] > 0
    print(f"Dashboard verified! Total questions solved: {dash_data['total_questions_solved']}, "
          f"Accuracy: {dash_data['accuracy_percent']}%, Streak: {dash_data['current_learning_streak']} day(s)")

    print("\n ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_adaptive_learning_flow()
