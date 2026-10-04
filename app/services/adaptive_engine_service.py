from typing import Dict, Any, Optional

class AdaptiveLearningEngine:
    def adapt(
        self,
        predicted_load: str,
        current_difficulty: str,
        consecutive_high_load_count: int,
        concept: Dict[str, Any],
        is_correct: bool
    ) -> Dict[str, Any]:
        """
        Dynamically adapts both TEACHING STYLE and CONTENT DIFFICULTY
        based on the learner's predicted cognitive load.
        """
        predicted_load = predicted_load.upper()
        current_diff = current_difficulty.capitalize()

        if predicted_load == "LOW":
            # Learner has mental capacity to spare -> Accelerate & Challenge
            new_diff = "Hard" if current_diff == "Medium" else ("Medium" if current_diff == "Easy" else "Hard")
            teaching_style = "Accelerated & Deep-Dive"
            adaptation_rationale = (
                "You demonstrated rapid comprehension and minimal cognitive strain. "
                "The engine has elevated question difficulty to 'Hard' and introduced advanced edge-case perspectives."
            )
            pedagogical_mode = "CHALLENGE"
            break_recommended = False
            consecutive_high = 0

            adapted_explanation = (
                f"Advanced Extension for {concept.get('title', 'this concept')}:\\n"
                f"Since your retention is sharp, notice how {concept.get('title', '')} behaves under extreme load "
                f"or constrained resource environments. Always keep the core invariant in mind."
            )

        elif predicted_load == "HIGH":
            # Learner is experiencing friction / overload -> Slow down & Scaffold
            consecutive_high = consecutive_high_load_count + 1
            new_diff = "Easy" if current_diff in ["Hard", "Medium"] else "Easy"
            teaching_style = "Scaffolded & Intuitive Breakdown"
            adaptation_rationale = (
                "High mental effort detected. The engine slowed the learning pace, reduced question difficulty to 'Easy', "
                "and activated structured multi-tier hint scaffolding with worked examples."
            )
            pedagogical_mode = "SCAFFOLD"
            break_recommended = consecutive_high >= 3

            adapted_explanation = (
                f"Let's simplify {concept.get('title', 'this concept')}:\\n"
                f"Analogy: {concept.get('real_world_analogy', '')}\\n"
                f"Step-by-step insight: {concept.get('simple_explanation', '')}"
            )

        else:  # MEDIUM
            new_diff = current_diff
            teaching_style = "Balanced Practice & Reinforcement"
            adaptation_rationale = (
                "Optimal learning zone (Desirable Difficulty). Maintaining current difficulty and pacing "
                "to consolidate knowledge with targeted practice."
            )
            pedagogical_mode = "REINFORCE"
            break_recommended = False
            consecutive_high = 0

            adapted_explanation = (
                f"Key Takeaway for {concept.get('title', 'this concept')}:\\n"
                f"{concept.get('key_takeaway', '')}"
            )

        return {
            "next_difficulty": new_diff,
            "teaching_style": teaching_style,
            "pedagogical_mode": pedagogical_mode,
            "adaptation_rationale": adaptation_rationale,
            "adapted_explanation": adapted_explanation,
            "break_recommended": break_recommended,
            "consecutive_high_load_count": consecutive_high,
            "escalating_support": [
                {"tier": 1, "title": "Small Hint", "desc": "Subtle conceptual nudge"},
                {"tier": 2, "title": "Detailed Hint", "desc": "Direct clue and formula review"},
                {"tier": 3, "title": "Step-by-Step Explanation", "desc": "Guided reasoning walkthrough"},
                {"tier": 4, "title": "Worked Example", "desc": "Full sample solution step-by-step"}
            ]
        }

adaptive_engine = AdaptiveLearningEngine()
