from typing import Dict, Any, List, Optional
from app.data.seed_data import DEMO_TOPICS
from app.services.ai_service import get_ai_service

class ContentAnalyzerService:
    def __init__(self):
        self.ai_service = get_ai_service()

    def get_seed_topics(self) -> List[Dict[str, Any]]:
        return DEMO_TOPICS

    def find_seed_topic(self, subject: str, topic_name: str) -> Optional[Dict[str, Any]]:
        subj_clean = subject.strip().lower()
        topic_clean = topic_name.strip().lower()
        
        for item in DEMO_TOPICS:
            if item["subject"].lower() == subj_clean and item["topic_name"].lower() == topic_clean:
                return item
            # Also partial match
            if topic_clean in item["topic_name"].lower() or item["topic_name"].lower() in topic_clean:
                return item
        return None

    def analyze_topic_request(self, subject: str, topic_name: str, difficulty_preference: str = "Intermediate") -> Dict[str, Any]:
        # 1. First check if it matches one of our rich pre-populated topics
        seed = self.find_seed_topic(subject, topic_name)
        if seed:
            return {
                "subject": seed["subject"],
                "topic_name": seed["topic_name"],
                "description": seed["description"],
                "difficulty_level": difficulty_preference.lower(),
                "concepts": seed["concepts"],
                "is_curated": True
            }

        # 2. Otherwise generate structured pedagogical concepts via AI Service
        synthetic_text = f"""
Subject: {subject}
Topic: {topic_name}
Difficulty Preference: {difficulty_preference}

Overview:
{topic_name} is an important domain in {subject}.
Core Foundations:
Understanding the foundational principles of {topic_name} requires mastering core mechanics, invariants, and fundamental operations.
Architectural Design & Invariants:
In practical systems, {topic_name} relies on specific rules to ensure high reliability, predictable execution, and scalable performance.
Advanced Trade-offs & Optimization:
Under high workload conditions or edge cases, {topic_name} requires balancing computational throughput against resource consumption.
"""
        concepts = self.ai_service.generate_concepts_from_text(synthetic_text, topic_name)
        return {
            "subject": subject,
            "topic_name": topic_name,
            "description": f"Comprehensive, AI-guided adaptive learning curriculum for {topic_name} ({subject}).",
            "difficulty_level": difficulty_preference.lower(),
            "concepts": concepts,
            "is_curated": False
        }

    def analyze_uploaded_material(self, extracted_text: str, filename: str) -> Dict[str, Any]:
        # Derive title from filename
        title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
        concepts = self.ai_service.generate_concepts_from_text(extracted_text, title)
        
        return {
            "subject": "Custom Uploaded Material",
            "topic_name": title,
            "description": f"Curriculum generated from '{filename}' with grounded concepts and adaptive quizzes.",
            "difficulty_level": "intermediate",
            "concepts": concepts,
            "extracted_length": len(extracted_text),
            "is_curated": False
        }
