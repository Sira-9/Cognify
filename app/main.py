import os
import json
import time
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    BASE_DIR, UPLOADS_DIR, DB_PATH, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
)
from app.database import init_db, db_session
from app.models import (
    UserRegister, UserLogin, TopicCreate, StartSessionRequest,
    SubmitAnswerRequest, RequestHintRequest, CheckMasteryRequest
)
from app.services.auth_service import (
    register_user, authenticate_user, verify_token, get_user_by_id
)
from app.services.file_parser_service import (
    validate_uploaded_file, extract_content_from_file, FileValidationError
)
from app.services.content_analyzer_service import ContentAnalyzerService
from app.services.cognitive_load_service import cognitive_predictor
from app.services.adaptive_engine_service import adaptive_engine
from app.services.mastery_service import mastery_service
from app.data.seed_data import DEMO_TOPICS

# Initialize database
init_db()

app = FastAPI(
    title="Cognify",
    description="Intelligent Adaptive Learning Platform with Cognitive Load Prediction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

content_analyzer = ContentAnalyzerService()

# Seed default demo topics into the database if not present
def seed_initial_topics():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM topics WHERE user_id IS NULL")
        row = cursor.fetchone()
        if row and row["count"] == 0:
            for item in DEMO_TOPICS:
                cursor.execute("""
                    INSERT INTO topics (user_id, subject, topic_name, description, difficulty_level, concepts_json)
                    VALUES (NULL, ?, ?, ?, ?, ?)
                """, (
                    item["subject"],
                    item["topic_name"],
                    item["description"],
                    item["difficulty_level"],
                    json.dumps(item["concepts"])
                ))

seed_initial_topics()

# Auth dependency
def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication token required")
    token = authorization.replace("Bearer ", "").strip()
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User account not found")
    return user

# Optional auth dependency for guest/demo convenience
def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    if not authorization:
        return None
    try:
        token = authorization.replace("Bearer ", "").strip()
        payload = verify_token(token)
        if payload:
            return get_user_by_id(payload["user_id"])
    except Exception:
        pass
    return None


# -------------------------------------------------------------
# 1. AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------

@app.post("/api/auth/register")
def register(req: UserRegister):
    try:
        return register_user(req.name, req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Registration error: " + str(e))

@app.post("/api/auth/login")
def login(req: UserLogin):
    try:
        return authenticate_user(req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login error: " + str(e))

@app.get("/api/auth/me")
def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return user


# -------------------------------------------------------------
# 2. DASHBOARD & ANALYTICS ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/dashboard")
def get_dashboard(user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Recent sessions
        cursor.execute("""
            SELECT s.id as session_id, s.topic_id, s.current_concept_index, s.current_difficulty,
                   s.current_cognitive_load, s.is_completed, s.updated_at,
                   t.subject, t.topic_name, t.description, t.concepts_json
            FROM learning_sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE s.user_id = ?
            ORDER BY s.updated_at DESC
            LIMIT 5
        """, (user_id,))
        recent_sessions = []
        for r in cursor.fetchall():
            concepts = json.loads(r["concepts_json"])
            recent_sessions.append({
                "session_id": r["session_id"],
                "topic_id": r["topic_id"],
                "subject": r["subject"],
                "topic_name": r["topic_name"],
                "description": r["description"],
                "current_concept_index": r["current_concept_index"],
                "total_concepts": len(concepts),
                "current_difficulty": r["current_difficulty"],
                "current_cognitive_load": r["current_cognitive_load"],
                "is_completed": bool(r["is_completed"]),
                "last_active": r["updated_at"]
            })

        # Overall interaction stats
        cursor.execute("""
            SELECT COUNT(*) as total_questions,
                   SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_questions,
                   AVG(response_time_seconds) as avg_response_time,
                   SUM(hints_used) as total_hints
            FROM interaction_logs
            WHERE user_id = ?
        """, (user_id,))
        stats_row = cursor.fetchone()
        total_q = stats_row["total_questions"] or 0
        correct_q = stats_row["correct_questions"] or 0
        avg_rt = round(stats_row["avg_response_time"] or 0, 1)
        tot_hints = stats_row["total_hints"] or 0
        accuracy = round((correct_q / total_q * 100.0), 1) if total_q > 0 else 0.0

        # Topic-wise mastery records
        cursor.execute("""
            SELECT m.id, m.topic_id, m.mastery_score, m.is_mastered, 
                   m.mastered_concepts_json, m.weak_concepts_json, m.created_at,
                   t.subject, t.topic_name
            FROM mastery_records m
            JOIN topics t ON m.topic_id = t.id
            WHERE m.user_id = ?
            ORDER BY m.created_at DESC
        """, (user_id,))
        mastery_list = []
        all_mastered_concepts = set()
        all_weak_concepts = set()
        
        for m in cursor.fetchall():
            m_concepts = json.loads(m["mastered_concepts_json"] or "[]")
            w_concepts = json.loads(m["weak_concepts_json"] or "[]")
            for c in m_concepts:
                all_mastered_concepts.add(c)
            for w in w_concepts:
                if w not in all_mastered_concepts:
                    all_weak_concepts.add(w)

            mastery_list.append({
                "id": m["id"],
                "topic_id": m["topic_id"],
                "subject": m["subject"],
                "topic_name": m["topic_name"],
                "mastery_score": m["mastery_score"],
                "is_mastered": bool(m["is_mastered"]),
                "mastered_concepts": m_concepts,
                "weak_concepts": w_concepts,
                "date": m["created_at"]
            })

        # Latest cognitive load across recent logs
        cursor.execute("""
            SELECT predicted_cognitive_load, created_at
            FROM interaction_logs
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,))
        recent_load_logs = [dict(row) for row in cursor.fetchall()]
        current_load = recent_load_logs[0]["predicted_cognitive_load"] if recent_load_logs else "BALANCED"

        # Calculate overall progress %
        overall_progress = min(100.0, round((len(all_mastered_concepts) * 20.0), 1)) if all_mastered_concepts else (15.0 if total_q > 0 else 0.0)

    return {
        "user": user,
        "current_learning_streak": user["current_streak"] or 1,
        "overall_progress_percent": overall_progress,
        "current_cognitive_load": current_load,
        "total_questions_solved": total_q,
        "accuracy_percent": accuracy,
        "avg_response_time_seconds": avg_rt,
        "total_hints_used": tot_hints,
        "recent_sessions": recent_sessions,
        "topic_mastery_records": mastery_list,
        "strong_concepts": list(all_mastered_concepts)[:6],
        "weak_concepts": list(all_weak_concepts)[:6],
        "recent_load_trend": recent_load_logs
    }


# -------------------------------------------------------------
# 3. TOPIC SELECTION & GENERATION
# -------------------------------------------------------------

@app.get("/api/topics/curated")
def get_curated_topics():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject, topic_name, description, difficulty_level, concepts_json FROM topics WHERE user_id IS NULL")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            concepts = json.loads(r["concepts_json"])
            result.append({
                "id": r["id"],
                "subject": r["subject"],
                "topic_name": r["topic_name"],
                "description": r["description"],
                "difficulty_level": r["difficulty_level"],
                "concept_count": len(concepts),
                "concept_titles": [c["title"] for c in concepts]
            })
        return result

@app.post("/api/topics/create-or-select")
def create_or_select_topic(req: TopicCreate, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    
    # Check if this curated or existing topic is in database
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, subject, topic_name, description, difficulty_level, concepts_json 
            FROM topics 
            WHERE LOWER(subject) = LOWER(?) AND LOWER(topic_name) = LOWER(?)
        """, (req.subject.strip(), req.topic_name.strip()))
        existing = cursor.fetchone()
        
        if existing:
            return {
                "id": existing["id"],
                "subject": existing["subject"],
                "topic_name": existing["topic_name"],
                "description": existing["description"],
                "difficulty_level": existing["difficulty_level"],
                "concepts": json.loads(existing["concepts_json"])
            }

        # Otherwise analyze and generate new curriculum
        analysis = content_analyzer.analyze_topic_request(req.subject, req.topic_name, req.difficulty_preference)
        cursor.execute("""
            INSERT INTO topics (user_id, subject, topic_name, description, difficulty_level, concepts_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            analysis["subject"],
            analysis["topic_name"],
            analysis["description"],
            analysis["difficulty_level"],
            json.dumps(analysis["concepts"])
        ))
        new_id = cursor.lastrowid
        
        return {
            "id": new_id,
            "subject": analysis["subject"],
            "topic_name": analysis["topic_name"],
            "description": analysis["description"],
            "difficulty_level": analysis["difficulty_level"],
            "concepts": analysis["concepts"]
        }


# -------------------------------------------------------------
# 4. UPLOAD STUDY MATERIAL
# -------------------------------------------------------------

@app.post("/api/materials/upload")
async def upload_material(file: UploadFile = File(...), user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    
    # 1. Validate file extension
    filename = file.filename or "uploaded_material.txt"
    try:
        # Save temp file to inspect size
        dest_filename = f"user_{user_id}_{int(time.time())}_{Path(filename).name}"
        saved_path = UPLOADS_DIR / dest_filename
        
        file_size = 0
        with open(saved_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise FileValidationError(f"File exceeds maximum allowed size of {MAX_FILE_SIZE_MB} MB.")
                buffer.write(chunk)

        validate_uploaded_file(filename, file_size)
        extracted_text = extract_content_from_file(saved_path, filename)
        
        # 2. AI Content Analysis & Pedagogical Sequence Generation
        analysis = content_analyzer.analyze_uploaded_material(extracted_text, filename)

        # 3. Store in database
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO study_materials (user_id, filename, original_name, file_type, file_size, extracted_text, analysis_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                dest_filename,
                filename,
                Path(filename).suffix.lower(),
                file_size,
                extracted_text[:30000],  # store reasonable preview in db
                json.dumps(analysis)
            ))
            material_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO topics (user_id, subject, topic_name, description, material_id, difficulty_level, concepts_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                analysis["subject"],
                analysis["topic_name"],
                analysis["description"],
                material_id,
                analysis["difficulty_level"],
                json.dumps(analysis["concepts"])
            ))
            topic_id = cursor.lastrowid

        return {
            "success": True,
            "material_id": material_id,
            "topic_id": topic_id,
            "topic_name": analysis["topic_name"],
            "subject": analysis["subject"],
            "description": analysis["description"],
            "extracted_character_count": len(extracted_text),
            "concepts_count": len(analysis["concepts"]),
            "concepts": analysis["concepts"]
        }

    except FileValidationError as e:
        if saved_path.exists():
            try: saved_path.unlink()
            except: pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if saved_path.exists():
            try: saved_path.unlink()
            except: pass
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


# -------------------------------------------------------------
# 5. LEARNING & ADAPTIVE SESSIONS
# -------------------------------------------------------------

@app.post("/api/learning/start")
def start_learning_session(req: StartSessionRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Verify topic
        cursor.execute("SELECT id, subject, topic_name, description, difficulty_level, concepts_json FROM topics WHERE id = ?", (req.topic_id,))
        topic_row = cursor.fetchone()
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")

        concepts = json.loads(topic_row["concepts_json"])
        if not concepts:
            raise HTTPException(status_code=400, detail="Topic contains no pedagogical concepts.")

        # Check for existing unfinished session
        cursor.execute("""
            SELECT id, current_concept_index, current_difficulty, current_teaching_style, current_cognitive_load, consecutive_high_load_count
            FROM learning_sessions
            WHERE user_id = ? AND topic_id = ? AND is_completed = 0
            ORDER BY updated_at DESC LIMIT 1
        """, (user_id, req.topic_id))
        existing_session = cursor.fetchone()

        if existing_session:
            session_id = existing_session["id"]
            concept_idx = min(existing_session["current_concept_index"], len(concepts) - 1)
            difficulty = existing_session["current_difficulty"]
            style = existing_session["current_teaching_style"]
            cog_load = existing_session["current_cognitive_load"]
            consec_high = existing_session["consecutive_high_load_count"]
        else:
            # Create new session
            cursor.execute("""
                INSERT INTO learning_sessions (user_id, topic_id, current_concept_index, current_difficulty, current_teaching_style, current_cognitive_load)
                VALUES (?, ?, 0, 'Medium', 'Standard', 'BALANCED')
            """, (user_id, req.topic_id))
            session_id = cursor.lastrowid
            concept_idx = 0
            difficulty = "Medium"
            style = "Standard"
            cog_load = "BALANCED"
            consec_high = 0

        current_concept = concepts[concept_idx]

        # Select matching question by difficulty if possible, else first
        matching_q = None
        for q in current_concept.get("questions", []):
            if q.get("difficulty", "").lower() == difficulty.lower():
                matching_q = q
                break
        if not matching_q and current_concept.get("questions"):
            matching_q = current_concept["questions"][0]

        # Filter out correct_index from student payload before sending!
        student_question = None
        if matching_q:
            student_question = {
                "id": matching_q["id"],
                "difficulty": matching_q["difficulty"],
                "question": matching_q["question"],
                "options": matching_q["options"]
            }

        return {
            "session_id": session_id,
            "topic_id": req.topic_id,
            "topic_name": topic_row["topic_name"],
            "subject": topic_row["subject"],
            "total_concepts": len(concepts),
            "concept_index": concept_idx,
            "concept": {
                "id": current_concept["id"],
                "title": current_concept["title"],
                "difficulty_level": current_concept["difficulty_level"],
                "simple_explanation": current_concept["simple_explanation"],
                "important_points": current_concept["important_points"],
                "visual_representation": current_concept.get("visual_representation"),
                "real_world_analogy": current_concept.get("real_world_analogy"),
                "concrete_example": current_concept.get("concrete_example"),
                "key_takeaway": current_concept.get("key_takeaway"),
                "misconceptions": current_concept.get("misconceptions", [])
            },
            "current_difficulty": difficulty,
            "teaching_style": style,
            "current_cognitive_load": cog_load,
            "question": student_question,
            "consecutive_high_load_count": consec_high
        }

@app.post("/api/learning/hint")
def request_hint(req: RequestHintRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.topic_id, t.concepts_json 
            FROM learning_sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE s.id = ? AND s.user_id = ?
        """, (req.session_id, user_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")

        concepts = json.loads(row["concepts_json"])
        target_q = None
        for c in concepts:
            if c["id"] == req.concept_id:
                for q in c.get("questions", []):
                    if q["id"] == req.question_id:
                        target_q = q
                        break
        
        if not target_q:
            raise HTTPException(status_code=404, detail="Question not found")

        # Escalating support tiers:
        # Tier 1: Small hint
        # Tier 2: Detailed hint
        # Tier 3: Step-by-step reasoning / Explanation
        # Tier 4: Worked example walkthrough
        if req.hint_tier == 1:
            hint_content = target_q.get("hint_tier_1", "Focus on the foundational definition introduced in the key takeaway.")
            tier_name = "Tier 1: Subtle Concept Nudge"
        elif req.hint_tier == 2:
            hint_content = target_q.get("hint_tier_2", "Notice the specific relationship between the variables or operational stages.")
            tier_name = "Tier 2: Detailed Structural Clue"
        elif req.hint_tier == 3:
            hint_content = target_q.get("hint_tier_3", "Step-by-step logic: Break down what each option asserts.")
            tier_name = "Tier 3: Guided Step-by-Step Breakdown"
        else:
            hint_content = target_q.get("worked_example", target_q.get("explanation", "Complete worked solution unavailable."))
            tier_name = "Tier 4: Full Worked Example Walkthrough"

        return {
            "tier": req.hint_tier,
            "tier_name": tier_name,
            "hint": hint_content
        }

@app.post("/api/learning/answer")
def submit_answer(req: SubmitAnswerRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.topic_id, s.current_concept_index, s.current_difficulty, 
                   s.current_teaching_style, s.current_cognitive_load, s.consecutive_high_load_count,
                   t.concepts_json, t.topic_name, t.subject
            FROM learning_sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE s.id = ? AND s.user_id = ?
        """, (req.session_id, user_id))
        session_row = cursor.fetchone()
        if not session_row:
            raise HTTPException(status_code=404, detail="Session not found")

        concepts = json.loads(session_row["concepts_json"])
        
        # Locate target concept and question
        target_concept = None
        target_q = None
        for c in concepts:
            if c["id"] == req.concept_id:
                target_concept = c
                for q in c.get("questions", []):
                    if q["id"] == req.question_id:
                        target_q = q
                        break
                break

        if not target_concept or not target_q:
            raise HTTPException(status_code=404, detail="Concept or Question not found")

        # Evaluate correctness
        is_correct = (req.selected_option_index == target_q["correct_index"]) if not req.skipped else False
        correct_index = target_q["correct_index"]
        correct_option_text = target_q["options"][correct_index] if target_q.get("options") else ""

        # Fetch recent performance history for feature computation
        cursor.execute("""
            SELECT is_correct, predicted_cognitive_load
            FROM interaction_logs
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))
        recent_logs = cursor.fetchall()
        recent_correct = sum(1 for r in recent_logs if r["is_correct"])
        recent_performance = (recent_correct / len(recent_logs)) if recent_logs else 0.7

        # Check repeated mistakes on this concept
        cursor.execute("""
            SELECT COUNT(*) as error_count
            FROM interaction_logs
            WHERE user_id = ? AND concept_id = ? AND is_correct = 0
        """, (user_id, req.concept_id))
        err_row = cursor.fetchone()
        repeated_mistakes = err_row["error_count"] if err_row else 0
        if not is_correct and not req.skipped:
            repeated_mistakes += 1

        # -------------------------------------------------------------
        # PREDICT COGNITIVE LOAD
        # -------------------------------------------------------------
        load_result = cognitive_predictor.predict_load(
            response_time_seconds=req.response_time_seconds,
            is_correct=is_correct,
            attempts=req.attempts,
            hints_used=req.hints_used,
            skipped=req.skipped,
            question_difficulty=target_q.get("difficulty", session_row["current_difficulty"]),
            recent_performance=recent_performance,
            repeated_mistakes=repeated_mistakes,
            time_since_last_action=req.time_since_last_action
        )
        predicted_load = load_result["predicted_load"]

        # -------------------------------------------------------------
        # ADAPT LEARNING ENGINE
        # -------------------------------------------------------------
        consecutive_high = session_row["consecutive_high_load_count"] or 0
        adaptation = adaptive_engine.adapt(
            predicted_load=predicted_load,
            current_difficulty=session_row["current_difficulty"],
            consecutive_high_load_count=consecutive_high,
            concept=target_concept,
            is_correct=is_correct
        )

        # Update session state in database
        cursor.execute("""
            UPDATE learning_sessions
            SET current_difficulty = ?,
                current_teaching_style = ?,
                current_cognitive_load = ?,
                consecutive_high_load_count = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            adaptation["next_difficulty"],
            adaptation["teaching_style"],
            predicted_load,
            adaptation["consecutive_high_load_count"],
            req.session_id
        ))

        # Record interaction log
        cursor.execute("""
            INSERT INTO interaction_logs (
                session_id, user_id, concept_id, concept_title, question_id,
                question_difficulty, is_correct, response_time_seconds,
                attempts, hints_used, skipped, repeated_mistakes,
                time_since_last_action, predicted_cognitive_load, load_probability_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            req.session_id,
            user_id,
            req.concept_id,
            target_concept["title"],
            req.question_id,
            target_q.get("difficulty", session_row["current_difficulty"]),
            is_correct,
            req.response_time_seconds,
            req.attempts,
            req.hints_used,
            req.skipped,
            repeated_mistakes,
            req.time_since_last_action,
            predicted_load,
            json.dumps(load_result["probabilities"])
        ))

        # Check total interaction count in this session to evaluate whether mastery check is ready
        cursor.execute("SELECT COUNT(*) as session_log_count FROM interaction_logs WHERE session_id = ?", (req.session_id,))
        count_row = cursor.fetchone()
        session_log_count = count_row["session_log_count"] or 1

        # Check if student is ready to advance or needs retry
        can_advance = is_correct or req.attempts >= 3 or req.skipped

        # Construct feedback
        if is_correct:
            feedback_title = "Correct!"
            feedback_message = f"Spot on! {target_q.get('explanation', '')}"
        elif req.skipped:
            feedback_title = "Question Skipped"
            feedback_message = f"No problem. The correct concept is: '{correct_option_text}'. Let's adjust the pace and review."
        else:
            feedback_title = "Not quite right"
            # Do NOT spoil answer on first or second attempt if they can retry!
            if req.attempts < 3:
                feedback_message = f"That wasn't the right choice. Review this clue: {target_q.get('hint_tier_1', 'Think about the core rule.')} You can try again!"
            else:
                feedback_message = f"The correct answer is: '{correct_option_text}'. Reason: {target_q.get('explanation', '')}"

        return {
            "is_correct": is_correct,
            "correct_index": correct_index if (is_correct or req.attempts >= 3 or req.skipped) else None,
            "feedback_title": feedback_title,
            "feedback_message": feedback_message,
            "explanation": target_q.get("explanation") if (is_correct or req.attempts >= 3 or req.skipped) else None,
            "can_advance": can_advance,
            "can_retry": (not is_correct) and (req.attempts < 3) and (not req.skipped),
            "cognitive_load": {
                "predicted_load": predicted_load,
                "load_score": load_result["load_score"],
                "contributing_factors": load_result["contributing_factors"],
                "disclaimer": load_result["disclaimer"]
            },
            "adaptation": {
                "pedagogical_mode": adaptation["pedagogical_mode"],
                "teaching_style": adaptation["teaching_style"],
                "next_difficulty": adaptation["next_difficulty"],
                "rationale": adaptation["adaptation_rationale"],
                "adapted_explanation": adaptation["adapted_explanation"],
                "break_recommended": adaptation["break_recommended"]
            },
            "session_log_count": session_log_count
        }

@app.post("/api/learning/next-concept")
def advance_to_next_concept(req: CheckMasteryRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.topic_id, s.current_concept_index, s.current_difficulty,
                   t.concepts_json, t.topic_name, t.subject
            FROM learning_sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE s.id = ? AND s.user_id = ?
        """, (req.session_id, user_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")

        concepts = json.loads(row["concepts_json"])
        current_idx = row["current_concept_index"]
        next_idx = current_idx + 1

        if next_idx >= len(concepts):
            # All concepts visited! Trigger mastery evaluation
            topic_dict = {
                "topic_name": row["topic_name"],
                "subject": row["subject"],
                "concepts": concepts
            }
            mastery_result = mastery_service.calculate_topic_mastery(req.session_id, user_id, topic_dict)
            
            # Save mastery record
            cursor.execute("""
                INSERT INTO mastery_records (
                    user_id, topic_id, session_id, mastery_score, is_mastered,
                    mastered_concepts_json, weak_concepts_json, summary_text,
                    stats_json, cognitive_load_trend_json, recommendations_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                row["topic_id"],
                req.session_id,
                mastery_result["mastery_score"],
                mastery_result["is_mastered"],
                json.dumps(mastery_result["concepts_mastered"]),
                json.dumps(mastery_result["concepts_needing_review"]),
                mastery_result["summary_text"],
                json.dumps(mastery_result["stats"]),
                json.dumps(mastery_result["cognitive_load_trend"]),
                json.dumps(mastery_result["recommendations"])
            ))

            cursor.execute("UPDATE learning_sessions SET is_completed = 1 WHERE id = ?", (req.session_id,))

            return {
                "completed": True,
                "mastery_result": mastery_result
            }

        # Otherwise advance to next concept
        cursor.execute("UPDATE learning_sessions SET current_concept_index = ? WHERE id = ?", (next_idx, req.session_id))
        next_concept = concepts[next_idx]

        # Select question matching current difficulty
        current_diff = row["current_difficulty"]
        matching_q = None
        for q in next_concept.get("questions", []):
            if q.get("difficulty", "").lower() == current_diff.lower():
                matching_q = q
                break
        if not matching_q and next_concept.get("questions"):
            matching_q = next_concept["questions"][0]

        student_question = None
        if matching_q:
            student_question = {
                "id": matching_q["id"],
                "difficulty": matching_q["difficulty"],
                "question": matching_q["question"],
                "options": matching_q["options"]
            }

        return {
            "completed": False,
            "concept_index": next_idx,
            "total_concepts": len(concepts),
            "concept": {
                "id": next_concept["id"],
                "title": next_concept["title"],
                "difficulty_level": next_concept["difficulty_level"],
                "simple_explanation": next_concept["simple_explanation"],
                "important_points": next_concept["important_points"],
                "visual_representation": next_concept.get("visual_representation"),
                "real_world_analogy": next_concept.get("real_world_analogy"),
                "concrete_example": next_concept.get("concrete_example"),
                "key_takeaway": next_concept.get("key_takeaway"),
                "misconceptions": next_concept.get("misconceptions", [])
            },
            "question": student_question,
            "difficulty": current_diff
        }

@app.post("/api/learning/check-mastery")
def check_mastery(req: CheckMasteryRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"]
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.topic_id, t.concepts_json, t.topic_name, t.subject
            FROM learning_sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE s.id = ? AND s.user_id = ?
        """, (req.session_id, user_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")

        concepts = json.loads(row["concepts_json"])
        topic_dict = {
            "topic_name": row["topic_name"],
            "subject": row["subject"],
            "concepts": concepts
        }

        result = mastery_service.calculate_topic_mastery(req.session_id, user_id, topic_dict)

        # Save record
        cursor.execute("""
            INSERT INTO mastery_records (
                user_id, topic_id, session_id, mastery_score, is_mastered,
                mastered_concepts_json, weak_concepts_json, summary_text,
                stats_json, cognitive_load_trend_json, recommendations_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            row["topic_id"],
            req.session_id,
            result["mastery_score"],
            result["is_mastered"],
            json.dumps(result["concepts_mastered"]),
            json.dumps(result["concepts_needing_review"]),
            result["summary_text"],
            json.dumps(result["stats"]),
            json.dumps(result["cognitive_load_trend"]),
            json.dumps(result["recommendations"])
        ))

        if result["is_mastered"]:
            cursor.execute("UPDATE learning_sessions SET is_completed = 1 WHERE id = ?", (req.session_id,))

        return result


# -------------------------------------------------------------
# 6. STATIC FILES & ROOT
# -------------------------------------------------------------

static_path = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(str(static_path / "index.html"))
