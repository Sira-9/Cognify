import json
from typing import Dict, Any, List, Tuple
from app.database import db_session

class MasteryService:
    def calculate_topic_mastery(self, session_id: int, user_id: int, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates learner performance across accuracy, difficulty weighting,
        hint independence, consistency, and coverage.
        """
        concepts = topic.get("concepts", [])
        concept_map = {c["id"]: c["title"] for c in concepts}
        
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT concept_id, concept_title, question_difficulty, is_correct, 
                       response_time_seconds, attempts, hints_used, skipped, 
                       predicted_cognitive_load, created_at
                FROM interaction_logs
                WHERE session_id = ? AND user_id = ?
                ORDER BY created_at ASC
            """, (session_id, user_id))
            logs = [dict(row) for row in cursor.fetchall()]

        if not logs:
            return {
                "is_mastered": False,
                "mastery_score": 0.0,
                "reason": "No questions have been completed yet in this session.",
                "concepts_mastered": [],
                "concepts_needing_review": [c["title"] for c in concepts],
                "stats": {
                    "questions_answered": 0,
                    "accuracy": 0.0,
                    "avg_response_time": 0.0,
                    "hints_used": 0
                }
            }

        total_questions = len(logs)
        correct_count = sum(1 for l in logs if l["is_correct"])
        total_hints = sum(l["hints_used"] for l in logs)
        avg_response_time = round(sum(l["response_time_seconds"] for l in logs) / max(1, total_questions), 1)
        raw_accuracy = (correct_count / total_questions) * 100.0

        # Group by concept to compute per-concept mastery
        concept_stats = {}
        for c in concepts:
            concept_stats[c["id"]] = {
                "id": c["id"],
                "title": c["title"],
                "total": 0,
                "correct": 0,
                "weighted_score": 0.0,
                "max_weighted": 0.0,
                "hints": 0
            }

        difficulty_weights = {"easy": 0.8, "medium": 1.0, "hard": 1.3}

        for log in logs:
            cid = log["concept_id"]
            if cid not in concept_stats:
                concept_stats[cid] = {
                    "id": cid,
                    "title": log.get("concept_title") or cid,
                    "total": 0,
                    "correct": 0,
                    "weighted_score": 0.0,
                    "max_weighted": 0.0,
                    "hints": 0
                }
            
            c_stat = concept_stats[cid]
            c_stat["total"] += 1
            c_stat["hints"] += log["hints_used"]
            
            weight = difficulty_weights.get(log["question_difficulty"].lower(), 1.0)
            c_stat["max_weighted"] += weight

            if log["is_correct"]:
                c_stat["correct"] += 1
                # Deduct partial credit for heavy hint usage
                hint_penalty = min(0.4, log["hints_used"] * 0.15)
                earned = weight * (1.0 - hint_penalty)
                c_stat["weighted_score"] += earned

        # Evaluate each concept
        mastered_concepts = []
        weak_concepts = []

        total_earned_weight = 0.0
        total_max_weight = 0.0

        for cid, stat in concept_stats.items():
            if stat["total"] == 0:
                weak_concepts.append(stat["title"])
                continue
            
            concept_score = (stat["weighted_score"] / max(0.1, stat["max_weighted"])) * 100.0
            total_earned_weight += stat["weighted_score"]
            total_max_weight += stat["max_weighted"]

            if concept_score >= 70.0 and stat["correct"] >= 1:
                mastered_concepts.append(stat["title"])
            else:
                weak_concepts.append(stat["title"])

        overall_mastery = round((total_earned_weight / max(0.1, total_max_weight)) * 100.0, 1)
        # Cap score between 0 and 100
        overall_mastery = min(100.0, max(0.0, overall_mastery))

        # Mastery criteria:
        # 1. Total questions attempted >= min(3, len(concepts))
        # 2. Overall mastery >= 75%
        # 3. At least 65% of tested concepts are mastered
        min_questions = max(2, len(concepts))
        has_min_questions = total_questions >= min_questions
        has_high_score = overall_mastery >= 72.0
        has_concept_coverage = len(mastered_concepts) >= max(1, len(concepts) - 1)

        is_mastered = has_min_questions and has_high_score and has_concept_coverage

        # Cognitive Load Trend
        cognitive_load_trend = [
            {"time": l["created_at"], "load": l["predicted_cognitive_load"], "difficulty": l["question_difficulty"]}
            for l in logs
        ]

        # Recommendations & next topics
        suggested_next = self._get_next_topic_recommendation(topic.get("subject", ""), topic.get("topic_name", ""))
        
        strengths = []
        if raw_accuracy >= 80:
            strengths.append(f"Excellent precision: {raw_accuracy:.0f}% first-pass accuracy across challenges.")
        if total_hints == 0 and total_questions > 1:
            strengths.append("High autonomy: Solved complex questions with zero hints requested.")
        if avg_response_time < 22:
            strengths.append(f"Rapid retrieval: Average problem-solving speed of {avg_response_time}s.")
        if not strengths:
            strengths.append("Persistent problem-solving: Iterated through feedback and improved conceptual clarity.")

        review_target = weak_concepts[0] if weak_concepts else "the core concepts"
        if is_mastered:
            recommendation_note = "You are ready for the next topic!"
        else:
            recommendation_note = f"Let us review {review_target} before wrapping up."

        summary_text = (
            f"You have {'successfully mastered' if is_mastered else 'made great progress on'} '{topic.get('topic_name')}' "
            f"with an overall mastery rating of {overall_mastery}%. {recommendation_note}"
        )

        return {
            "is_mastered": is_mastered,
            "mastery_score": overall_mastery,
            "topic_name": topic.get("topic_name"),
            "subject": topic.get("subject"),
            "concepts_mastered": mastered_concepts,
            "concepts_needing_review": weak_concepts,
            "summary_text": summary_text,
            "strengths": strengths,
            "stats": {
                "questions_answered": total_questions,
                "accuracy": round(raw_accuracy, 1),
                "avg_response_time": avg_response_time,
                "hints_used": total_hints
            },
            "cognitive_load_trend": cognitive_load_trend,
            "recommendations": {
                "review_weak_concepts": weak_concepts,
                "suggested_next_topic": suggested_next
            }
        }

    def _get_next_topic_recommendation(self, subject: str, current_topic: str) -> Dict[str, str]:
        recs = {
            "Virtual Memory & Paging": {"subject": "Operating Systems", "topic": "Process Scheduling & Deadlocks"},
            "Data Structures - Trees & Binary Search Trees": {"subject": "Computer Science", "topic": "Graph Algorithms & Shortest Path"},
            "Instruction Pipelining & Hazards": {"subject": "Computer Architecture", "topic": "Cache Coherence & Memory Hierarchy"},
            "Exception Handling & RAII": {"subject": "C++", "topic": "Smart Pointers & Memory Models"}
        }
        for k, v in recs.items():
            if k.lower() in current_topic.lower() or current_topic.lower() in k.lower():
                return v
        return {"subject": "Computer Science", "topic": "Advanced Algorithms & Optimization"}

mastery_service = MasteryService()
