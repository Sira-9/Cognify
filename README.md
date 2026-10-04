# Cognify 🧠

An intelligent, full-stack adaptive learning platform that teaches students from selected topics or uploaded study materials, continuously analyzes their learning behavior, predicts their current cognitive load, and dynamically adapts both teaching style and difficulty.

---

## 🌟 Key Features

1. **Authentication & Student Profiles**
   - Clean sign up and login with PBKDF2 password hashing and secure token management.
   - Preserves learning history, streaks, concept diagnostic, and topic mastery.
   - Includes a 1-click **Instant Demo Account** for rapid testing.

2. **Dual-Path Dashboard**
   - **Option A: Learn a Topic** — Curated computer science subjects (Operating Systems, Data Structures, Computer Architecture, C++, C) or custom AI topic generation.
   - **Option B: Upload My Study Material** — Supports PDF, PPT/PPTX, DOC/DOCX, and TXT with file type, size, and integrity validation.
   - Real-time Metrics HUD: Overall progress %, learning streak, questions solved, accuracy %, and live cognitive load status.

3. **AI Pedagogical Engine**
   - Structured learning sequences from **Basic → Intermediate → Advanced**.
   - Teaches **one concept at a time** with:
     - Clear explanation
     - Key architectural points checklist
     - Visual ASCII / architecture layout diagram
     - Real-world analogy
     - Concrete implementation example
     - Key takeaway & common misconceptions

4. **Mini Quiz & Escalating Support Scaffolding**
   - Concept-grounded questions with Easy, Medium, and Hard difficulty levels.
   - Immediate feedback with explanation (does not spoil answer prematurely on retry).
   - **4-Tier Escalating Support Drawer**:
     - *Tier 1:* Subtle Concept Nudge
     - *Tier 2:* Detailed Structural Clue & Formula
     - *Tier 3:* Guided Step-by-Step Breakdown
     - *Tier 4:* Full Worked Example Walkthrough

5. **Non-Invasive Behavioral Signal Collection & Cognitive Load Modeling**
   - Collects 9 measurable behavior signals:
     - Response time (seconds)
     - First-pass accuracy
     - Number of attempts
     - Hint usage & tiers
     - Questions skipped
     - Question difficulty weight
     - Rolling recent performance
     - Repeated errors on the same concept
     - Latency between interactions
   - Dual-engine prediction:
     - Transparent rule-based psychological heuristic model (Sweller's Cognitive Load Theory)
     - Scikit-Learn `RandomForestClassifier` predicting probability distributions for **LOW**, **MEDIUM**, and **HIGH** cognitive load.
   - Live visual indicator and driver explanations.

6. **Adaptive Learning Engine**
   - Calibrates both **Content Difficulty** AND **Teaching Style**:
     - **Low Cognitive Load:** Accelerates pacing, elevates difficulty to Hard, introduces advanced system trade-offs.
     - **Medium Cognitive Load:** Maintains optimal challenge (Desirable Difficulty), consolidates memory with standard practice.
     - **High Cognitive Load:** Slows down lesson, reduces difficulty to Easy, activates concrete analogies, worked examples, and multi-tier scaffolding.
   - Fatigue protection: Recommends a 2-minute break if high load persists across 3 consecutive interactions.

7. **Multi-Dimensional Mastery Check & Progress Analytics**
   - Rigorous evaluation across accuracy, difficulty weighting, hint independence, and concept coverage.
   - Generates Mastery Summary certificate, strengths, mastered concepts (✓), targeted review recommendations (⚠), and next topic progression.
---
## 📸 Application Preview

### Login & Authentication


---
## 🛠️ Technology Stack

* **Backend:** Python, FastAPI
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite
* **Data Validation:** Pydantic
* **Machine Learning:** Scikit-learn
* **AI Integration:** Gemini API and Offline Heuristic Engine
---

## 🚀 Quickstart Guide

### 1. Requirements
- Python 3.10+ (Standard Python runtime)

### 2. Run the Application
From the project directory:
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

### 3. Run Automated Integration Tests
To execute the automated end-to-end tests:
```bash
python tests/test_flow.py
python tests/test_mastery_completion.py
```

---

## 📁 Project Structure

```
adaptive_learn_ai/
├── run.py                          # Server launcher
├── README.md                       # Documentation
├── adaptive_learn.db               # SQLite database
├── app/
│   ├── config.py                   # App configuration & settings
│   ├── database.py                 # SQLite schema & database transactions
│   ├── models.py                   # Pydantic validation schemas
│   ├── data/
│   │   └── seed_data.py            # Rich curated computer science topics
│   ├── services/
│   │   ├── auth_service.py         # Authentication & token hashing
│   │   ├── file_parser_service.py  # PDF, PPTX, DOCX, TXT extractor & validator
│   │   ├── content_analyzer_service.py # Pedagogical concept extractor
│   │   ├── ai_service.py           # Modular AI engine (Gemini API & Offline Heuristic Engine)
│   │   ├── cognitive_load_service.py # ML & Rule-based Cognitive Load Predictor
│   │   ├── adaptive_engine_service.py # Calibrates teaching style & difficulty
│   │   └── mastery_service.py      # Multi-dimensional topic mastery engine
│   └── main.py                     # FastAPI application & REST endpoints
├── static/
│   ├── index.html                  # Single-page application interface
│   ├── css/styles.css              # Custom styling, load gauges & animations
│   └── js/
│       ├── api.js                  # Frontend API client
│       ├── state.js                # Reactive store & behavior tracker
│       └── app.js                  # Views, controllers, timers & quiz engine
├── sample_materials/               # Ready-to-use study files for testing
│   ├── operating_systems_paging.txt
│   ├── computer_networks_tcp_ip.docx
│   └── machine_learning_foundations.pptx
└── tests/
    ├── test_flow.py                # End-to-end learning loop integration test
    └── test_mastery_completion.py  # Full mastery completion test
```
