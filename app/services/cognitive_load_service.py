"""
Cognitive Load Prediction Module.
Predicts learner's current cognitive load (LOW, MEDIUM, HIGH)
using non-invasive behavioral learning signals:
- response_time (seconds)
- accuracy (1.0 for correct, 0.0 for incorrect)
- attempts (1, 2, 3+)
- hints_used (0, 1, 2, 3)
- skipped (0 or 1)
- question_difficulty ('Easy', 'Medium', 'Hard')
- recent_performance (rolling accuracy 0.0 - 1.0)
- repeated_mistakes (count of consecutive errors on same concept)
- time_since_last_action (latency between clicks)

Implements both a transparent psychological heuristic scoring model
and an active Scikit-Learn Machine Learning Classifier.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class CognitiveLoadPredictor:
    def __init__(self):
        self.model = None
        self._init_and_train_ml_model()

    def _init_and_train_ml_model(self):
        """
        Trains a baseline Random Forest model on pedagogical interaction profiles
        representing Low, Medium, and High cognitive load regimes.
        """
        # Feature columns:
        # 0: response_time (sec)
        # 1: accuracy (0 or 1)
        # 2: attempts (1, 2, 3)
        # 3: hints_used (0, 1, 2, 3)
        # 4: skipped (0 or 1)
        # 5: difficulty_val (1: Easy, 2: Med, 3: Hard)
        # 6: recent_performance (0.0 to 1.0)
        # 7: repeated_mistakes (0 to 3)
        # 8: latency (sec)

        np.random.seed(42)
        X = []
        y = []

        # Regime 0: LOW cognitive load (Quick, confident, high accuracy, minimal hints)
        for _ in range(300):
            rt = np.random.uniform(3, 14)
            acc = 1.0 if np.random.rand() > 0.1 else 0.0
            attempts = 1
            hints = 0 if np.random.rand() > 0.08 else 1
            skipped = 0
            diff = np.random.choice([1, 2, 3])
            recent_perf = np.random.uniform(0.75, 1.0)
            rep_mistakes = 0
            lat = np.random.uniform(1, 8)
            X.append([rt, acc, attempts, hints, skipped, diff, recent_perf, rep_mistakes, lat])
            y.append("LOW")

        # Regime 1: MEDIUM cognitive load (Normal pace, occasional hint, steady progress)
        for _ in range(300):
            rt = np.random.uniform(12, 35)
            acc = 1.0 if np.random.rand() > 0.3 else 0.0
            attempts = np.random.choice([1, 2])
            hints = np.random.choice([0, 1])
            skipped = 0
            diff = np.random.choice([1, 2, 3])
            recent_perf = np.random.uniform(0.5, 0.8)
            rep_mistakes = np.random.choice([0, 1])
            lat = np.random.uniform(4, 18)
            X.append([rt, acc, attempts, hints, skipped, diff, recent_perf, rep_mistakes, lat])
            y.append("MEDIUM")

        # Regime 2: HIGH cognitive load (Long pauses, errors, multiple hints, multiple attempts)
        for _ in range(300):
            rt = np.random.uniform(25, 75)
            acc = 0.0 if np.random.rand() > 0.25 else 1.0
            attempts = np.random.choice([2, 3, 4])
            hints = np.random.choice([1, 2, 3])
            skipped = 1 if np.random.rand() > 0.8 else 0
            diff = np.random.choice([2, 3])
            recent_perf = np.random.uniform(0.1, 0.45)
            rep_mistakes = np.random.choice([1, 2, 3])
            lat = np.random.uniform(15, 60)
            X.append([rt, acc, attempts, hints, skipped, diff, recent_perf, rep_mistakes, lat])
            y.append("HIGH")

        X = np.array(X)
        self.model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
        self.model.fit(X, y)

    def _difficulty_to_num(self, difficulty: str) -> int:
        d = str(difficulty).lower()
        if "hard" in d:
            return 3
        if "easy" in d:
            return 1
        return 2

    def predict_load(
        self,
        response_time_seconds: float,
        is_correct: bool,
        attempts: int,
        hints_used: int,
        skipped: bool,
        question_difficulty: str,
        recent_performance: float,
        repeated_mistakes: int,
        time_since_last_action: float
    ) -> Dict[str, Any]:
        """
        Calculates cognitive load using both rule-based pedagogical heuristics
        and the trained Random Forest classifier.
        """
        diff_num = self._difficulty_to_num(question_difficulty)
        acc_num = 1.0 if is_correct else 0.0
        skip_num = 1.0 if skipped else 0.0

        # Feature vector for ML
        feature_vector = np.array([[
            max(0.5, response_time_seconds),
            acc_num,
            attempts,
            hints_used,
            skip_num,
            diff_num,
            recent_performance,
            repeated_mistakes,
            max(0.5, time_since_last_action)
        ]])

        # 1. ML Model Prediction
        ml_pred = self.model.predict(feature_vector)[0]
        ml_classes = list(self.model.classes_)
        ml_probs = self.model.predict_proba(feature_vector)[0]
        prob_dict = {ml_classes[i]: round(float(ml_probs[i]), 3) for i in range(len(ml_classes))}

        # 2. Transparent Rule-Based Pedagogical Score (0 - 100)
        # Base score starts in balanced medium zone (45)
        rule_score = 45.0
        factors = []

        # Factor A: Accuracy & Attempts
        if not is_correct:
            rule_score += 18.0
            factors.append("Incorrect answer (+18 load)")
        else:
            rule_score -= 12.0
            factors.append("Correct response (-12 load)")

        if attempts > 1:
            penalty = (attempts - 1) * 12.0
            rule_score += penalty
            factors.append(f"{attempts} attempts required (+{penalty:.0f} load)")

        # Factor B: Hint Usage
        if hints_used > 0:
            hint_penalty = hints_used * 10.0
            rule_score += hint_penalty
            factors.append(f"{hints_used} hint(s) consulted (+{hint_penalty:.0f} load)")
        elif is_correct and attempts == 1:
            rule_score -= 6.0
            factors.append("Solved independently without hints (-6 load)")

        # Factor C: Response Time
        # Expected response time based on difficulty: Easy ~ 12s, Med ~ 20s, Hard ~ 30s
        expected_time = {1: 12.0, 2: 20.0, 3: 30.0}.get(diff_num, 20.0)
        time_ratio = response_time_seconds / expected_time
        if time_ratio > 1.8:
            rule_score += 15.0
            factors.append(f"Extended deliberation time ({response_time_seconds:.1f}s vs {expected_time:.0f}s expected)")
        elif time_ratio < 0.6 and is_correct:
            rule_score -= 14.0
            factors.append(f"Rapid, confident response ({response_time_seconds:.1f}s)")

        # Factor D: Repeated Mistakes & Skips
        if repeated_mistakes > 0:
            rep_pen = repeated_mistakes * 12.0
            rule_score += rep_pen
            factors.append(f"{repeated_mistakes} recurring mistake(s) on concept")

        if skipped:
            rule_score += 25.0
            factors.append("Question was skipped (+25 load)")

        # Factor E: Recent Rolling Performance
        if recent_performance >= 0.85:
            rule_score -= 10.0
            factors.append(f"High recent performance trend ({recent_performance*100:.0f}%)")
        elif recent_performance < 0.4:
            rule_score += 12.0
            factors.append(f"Low recent performance trend ({recent_performance*100:.0f}%)")

        rule_score = max(5.0, min(95.0, rule_score))

        # Determine category based on rule score
        if rule_score < 38.0:
            final_load = "LOW"
        elif rule_score > 62.0:
            final_load = "HIGH"
        else:
            final_load = "MEDIUM"

        return {
            "predicted_load": final_load,
            "load_score": round(rule_score, 1),
            "ml_prediction": ml_pred,
            "probabilities": prob_dict,
            "contributing_factors": factors,
            "disclaimer": "Current learning load estimate reflects immediate mental effort on this concept, not intellectual ability."
        }

# Singleton instance
cognitive_predictor = CognitiveLoadPredictor()
