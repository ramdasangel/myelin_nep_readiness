"""
SRI constants, question codes, scoring maps, and banding thresholds.
Derived from the three instrument PDFs:
  - SRI-SystemReadinessInstrument.pdf
  - SRI-EcosystemReadinessInstrument.pdf
  - SET.pdf
"""

# ═══════════════════════════════════════════════════════════════════
#  INSTRUMENT 1: System Readiness Audit (Binary, 0-20)
#  Respondents: Principal + VP + Academic Coordinator
#  setCode: SRI001
# ═══════════════════════════════════════════════════════════════════

SRI_SET_CODE = "SRI001"

# Section A: Teacher Enablement (E1-E5)
TEACHER_ENABLEMENT_CODES = {
    "E1": {
        "question_id": "69bd342915f45d288fc1e142",
        "text": "Does the school timetable include a formally scheduled weekly planning period for teachers?",
        "why": "Protected time is precondition for D3/D4 practice.",
    },
    "E2": {
        "question_id": "69bd342915f45d288fc1e143",
        "text": "Is there a recurring academic review meeting (minimum monthly) focused on teaching-learning quality?",
        "why": "Signals structured pedagogical review.",
    },
    "E3": {
        "question_id": "69bd342915f45d288fc1e144",
        "text": "Do teachers have structured access to student performance insights beyond marks?",
        "why": "Enables diagnostic teaching.",
    },
    "E4": {
        "question_id": "69bd342915f45d288fc1e145",
        "text": "Is there a defined mechanism to protect instructional time from administrative interruptions?",
        "why": "Reduces friction load.",
    },
    "E5": {
        "question_id": "69bd342915f45d288fc1e146",
        "text": "Has leadership issued a documented directive encouraging instructional experimentation?",
        "why": "Legitimises adaptive practice.",
    },
}

# Section B: Leadership Routines (R1-R5)
LEADERSHIP_ROUTINE_CODES = {
    "R1": {
        "question_id": "69bd342915f45d288fc1e147",
        "text": "Does the school use a structured classroom observation framework aligned to instructional depth?",
        "why": "Links monitoring to practice depth.",
    },
    "R2": {
        "question_id": "69bd342915f45d288fc1e148",
        "text": "Is there a defined observation calendar with minimum frequency expectations?",
        "why": "Ensures review consistency.",
    },
    "R3": {
        "question_id": "69bd342915f45d288fc1e149",
        "text": "Is written or structured feedback provided after observations using a consistent format?",
        "why": "Institutionalises instructional improvement.",
    },
    "R4": {
        "question_id": "69bd342915f45d288fc1e14a",
        "text": "Does the school maintain a documented teacher-level intervention tracking mechanism?",
        "why": "Enables follow-through on improvement.",
    },
    "R5": {
        "question_id": "69bd342915f45d288fc1e14b",
        "text": "Does the principal have access to a consolidated academic review dashboard?",
        "why": "Ensures oversight visibility.",
    },
}

# All SRI question IDs in order (E1-E5, R1-R5)
SRI_QUESTION_IDS = [v["question_id"] for v in TEACHER_ENABLEMENT_CODES.values()] + \
                   [v["question_id"] for v in LEADERSHIP_ROUTINE_CODES.values()]

# Binary response mapping: option index → 0 or 1
# SRI001 uses Yes/No (2 options). selectedOption 0 = Yes = 1, selectedOption 1 = No = 0
SRI_BINARY_MAP = {0: 1, 1: 0}

# System Readiness Audit scoring
#   EnablementIndex = (E1+E2+E3+E4+E5) / 5
#   TeacherEnablement(0-10) = 10 × EnablementIndex
#   RoutineIndex = (R1+R2+R3+R4+R5) / 5
#   LeadershipRoutines(0-10) = 10 × RoutineIndex
#   SystemReadiness(0-20) = TeacherEnablement + LeadershipRoutines

SRI_INTERPRETATION_BANDS = {
    "structural_absence":          (0, 5),
    "emerging_structure":          (6, 10),
    "partially_institutionalised": (11, 15),
    "operationalised_structure":   (16, 20),
}


# ═══════════════════════════════════════════════════════════════════
#  INSTRUMENT 2: Parent Validation Signal (Likert, 0-7)
#  Respondents: Parents (anonymous)
#  NOT YET in database — future collection
# ═══════════════════════════════════════════════════════════════════

PARENT_LIKERT_MAP = {
    # selectedOption index → score
    0: 0.00,   # Strongly Disagree
    1: 0.25,   # Disagree
    2: 0.50,   # Neutral
    3: 0.75,   # Agree
    4: 1.00,   # Strongly Agree
}

PARENT_QUESTION_CODES = {
    "P1": {
        "text_en": "I understand what my child is expected to learn beyond examination marks.",
        "text_mr": "माझ्या पाल्याला परीक्षेतील गुणांपलीकडे काय शिकायला हवे, याची मला कल्पना आहे.",
        "why": "Measures clarity of learning intent communication.",
    },
    "P2": {
        "text_en": "I receive structured feedback that helps me understand my child's strengths and areas of improvement.",
        "text_mr": "मला शाळेकडून पाल्याची बलस्थाने आणि कुठे सुधारणा करावी लागेल हे विस्तृत आणि स्पष्टपणे कळवले जाते.",
        "why": "Validates transparency of assessment practice.",
    },
    "P3": {
        "text_en": "My child is asked to explain reasoning or solve problems in different ways.",
        "text_mr": "माझ्या पाल्याला शिक्षणाबाबत शिक्षक योग्य अध्यापनीय निर्णय घेतात यावर माझा विश्वास आहे.",
        "why": "Signals perceived cognitive demand shift.",
    },
    "P4": {
        "text_en": "I trust my child's teacher to make instructional decisions in the best interest of learning.",
        "text_mr": "माझ्या पाल्याला शिक्षणाबाबत शिक्षक योग्य निर्णय घेतात यावर माझा विश्वास आहे.",
        "why": "Trust is ecosystem validation.",
    },
    "P5": {
        "text_en": "The school provides meaningful academic communication opportunities with parents.",
        "text_mr": "शाळा पालकांना शैक्षणिक विषयांवर अर्थपूर्ण संवादाची संधी उपलब्ध करून देते.",
        "why": "Validates communication loop existence.",
    },
}

# ParentIndex = mean(P1..P5)   each in [0,1]
# ParentReadiness(0-7) = 7 × ParentIndex

PARENT_INTERPRETATION_BANDS = {
    "weak_parent_alignment":       (0, 2),
    "partial_visibility":          (2, 4),
    "strong_communication_trust":  (4, 6),
    "high_ecosystem_validation":   (6, 7),
}

# Sampling rules
PARENT_MIN_RESPONSE_RATE = 0.30  # 30%


# ═══════════════════════════════════════════════════════════════════
#  INSTRUMENT 3: SET — Structured Explanation of Translation
#  Derived from orientation + practice depth + diagnostic areas
# ═══════════════════════════════════════════════════════════════════

# --- Foundational Philosophies ---
FP_NAMES = {
    "FP1": "Each Child is Unique",
    "FP2": "Holistic & Experiential Learning",
    "FP3": "Teacher as Reflective Practitioner",
    "FP4": "Assessment for Learning",
    "FP5": "Collaboration & Community",
}

# --- Practice Depth levels ---
DEPTH_LEVELS = {
    "D1": "Procedural",
    "D2": "Responsive",
    "D3": "Diagnostic",
    "D4": "Adaptive",
}
DEPTH_NUMERIC = {"D1": 1, "D2": 2, "D3": 3, "D4": 4}

# --- SET1: Orientation Alignment × Practice Depth ---

# Banding thresholds for orientation strength
ORIENTATION_BANDS = {
    "high":   lambda p: p >= 0.30,
    "medium": lambda p: 0.15 <= p < 0.30,
    "low":    lambda p: p < 0.15,
}

# Banding thresholds for practice depth
DEPTH_BANDS = {
    "low":  lambda d: d < 2.2,
    "mid":  lambda d: 2.2 <= d < 3.0,
    "high": lambda d: d >= 3.0,
}

# SET1 alignment states
ALIGNMENT_STATES = {
    "intent_high_translation_low":  "Leader High + Teacher High + Depth Low",
    "teacher_led_intent":           "Teacher High + Leader Low",
    "leader_led_intent":            "Leader High + Teacher Low",
    "low_attention_zone":           "Both Low",
    "intent_translation_aligned":   "Both High + Depth High",
}


# --- SET2: Practice Depth × Practice Diagnostics (Areas) ---

# Teacher areas (A1-A4) and their sub-areas
TEACHER_AREAS = {
    "A1": {
        "name": "Continuous Learning Diagnostics",
        "subareas": ["Access", "Usability", "FollowThrough", "CollectiveUse", "StudentClarity"],
    },
    "A2": {
        "name": "Teacher Development & Growth",
        "subareas": ["Structure", "Safety", "PeerLearning", "Experimentation", "GrowthCulture"],
    },
    "A3": {
        "name": "Holistic Progress Card (HPC) Enablement",
        "subareas": ["Understanding", "Clarity", "Time", "Use", "StudentRole"],
    },
    "A4": {
        "name": "Parent & Community Support (Teacher Experience)",
        "subareas": ["Communication", "Guidance", "Facilitation", "Recognition"],
    },
}

# Leader areas (B1-B4) and their sub-areas
LEADER_AREAS = {
    "B1": {
        "name": "NEP Governance & Ownership",
        "subareas": ["OwnershipClarity", "TranslationToAction", "ResponsibilityDistribution"],
    },
    "B2": {
        "name": "Data-Informed Decision Culture",
        "subareas": ["ReviewPractice", "DecisionUse", "ChangeSupport"],
    },
    "B3": {
        "name": "Teacher Development Culture",
        "subareas": ["PLCRegularity", "Safety", "ExperimentationProtection"],
    },
    "B4": {
        "name": "HPC & Reporting Culture",
        "subareas": ["PurposeClarity", "ParentOrientation", "TeacherSupport"],
    },
}

# Area/sub-area banding (same for teacher and leader)
AREA_BANDS = {
    "low":  lambda s: s < 2.5,
    "mid":  lambda s: 2.5 <= s <= 3.2,
    "high": lambda s: s > 3.2,
}

# FP → Diagnostic area explainability links (Teacher)
FP_TEACHER_AREA_LINKS = {
    "FP1": ["A1", "A3"],
    "FP2": ["A3", "A2"],
    "FP3": ["A2"],
    "FP4": ["A1", "A3"],
    "FP5": ["A4"],
}

# FP → Diagnostic area explainability links (Leader)
FP_LEADER_AREA_LINKS = {
    "FP1": ["B2", "B4"],
    "FP2": ["B1", "B4"],
    "FP3": ["B3"],
    "FP4": ["B2", "B4"],
    "FP5": ["B1", "B3"],
}


# --- SET Archetypes ---

CORE_ARCHETYPES = {
    "ARCH-01": {
        "set1_state": "intent_high_translation_low",
        "teacher_conditions": {"A1": "low", "A3": "low"},
        "leader_conditions": {"B4": "low"},
        "interpretation": "Shared holistic intent exists, but lack of shared language and usable tools limits classroom translation.",
    },
    "ARCH-02": {
        "set1_state": "intent_high_translation_low",
        "teacher_conditions": {"A2": "low"},
        "leader_conditions": {"B3": "low"},
        "interpretation": "Teachers reflect but hesitate to act due to low psychological and institutional safety.",
    },
    "ARCH-03": {
        "set1_state": "teacher_led_intent",
        "teacher_conditions": {"A3": "low"},
        "leader_conditions": {"B1": "low"},
        "interpretation": "Teachers move ahead of systems; leadership intent has not yet operationalised support structures.",
    },
    "ARCH-04": {
        "set1_state": "leader_led_intent",
        "teacher_conditions": {"A1": "low"},
        "leader_conditions": {"B2": "low"},
        "interpretation": "Leadership intent exists, but classroom enactment stalls due to weak diagnostic follow-through and decision coupling.",
    },
    "ARCH-05": {
        "set1_state": "low_attention_zone",
        "teacher_conditions": {"A1": "low", "A2": "low"},
        "leader_conditions": {"B1": "low", "B3": "low"},
        "interpretation": "NEP intent has not yet entered collective attention; foundational orientation work is required.",
    },
    "ARCH-06": {
        "set1_state": "intent_translation_aligned",
        "teacher_conditions": {"A1": "high", "A2": "high"},
        "leader_conditions": {"B2": "high", "B3": "high"},
        "interpretation": "Intent, enactment, and system conditions are coherently aligned; focus shifts to sustaining depth.",
    },
}

FP_ARCHETYPES = {
    "FP2-A": {
        "fp": "FP2",
        "set1_pattern": "high_orientation_low_depth",
        "conditions": {"A3": "low", "B4": "low"},
        "label": "Holistic intent without shared meaning",
    },
    "FP4-A": {
        "fp": "FP4",
        "set1_pattern": "medium_orientation_low_depth",
        "conditions": {"A1": "low", "B2": "low"},
        "label": "Assessment valued, diagnostics weak",
    },
    "FP3-A": {
        "fp": "FP3",
        "set1_pattern": "medium_orientation_mid_depth",
        "conditions": {"A2": "low", "B3": "low"},
        "label": "Reflection without safety",
    },
    "FP5-A": {
        "fp": "FP5",
        "set1_pattern": "low_orientation_low_depth",
        "conditions": {"A4": "low", "B1": "low"},
        "label": "Collaboration structurally unsupported",
    },
    "FP1-A": {
        "fp": "FP1",
        "set1_pattern": "high_orientation_mid_depth",
        "conditions": {"A1": "low", "A3": "low"},
        "label": "Learner uniqueness acknowledged but not operationalised",
    },
}

TENSION_ARCHETYPES = {
    "TENS-01": {
        "set1_signal": "teacher_led_intent",
        "teacher_conditions": {"A2": "high"},
        "leader_conditions": {"B3": "low"},
        "description": "Teachers willing to grow, but PLC and experimentation not institutionally protected.",
    },
    "TENS-02": {
        "set1_signal": "leader_led_intent",
        "teacher_conditions": {"A1": "low"},
        "leader_conditions": {"B2": "high"},
        "description": "Systems generate data, but teachers lack tools/time to act.",
    },
    "TENS-03": {
        "set1_signal": "intent_translation_aligned",
        "teacher_conditions": {"A3": "low"},
        "leader_conditions": {"B4": "low"},
        "description": "Both sides value holistic progress, but reporting remains compliance-oriented.",
    },
}
