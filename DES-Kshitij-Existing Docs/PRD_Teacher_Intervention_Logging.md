# Product Requirements Document (PRD)

## Teacher Intervention Choice Selection & Daily Logging System

**Project:** क्षितिज (Kshitij) - NEP-2020 Readiness Index  
**Module:** Practice Logging & Reflection (Weeks 4-6)  
**Version:** 1.0  
**Date:** January 2026  
**Author:** Myelin Team

---

## 1. Overview

### 1.1 Purpose

This module enables teachers participating in Micro-Intervention 1 to:
1. Select 3-5 intervention tasks aligned with NEP Foundational Principles
2. Log daily practice of selected interventions over a 21-day period
3. Track their progress and reflect on classroom implementation

### 1.2 Context

As part of Project Kshitij's execution framework:
- **Week 3 (Feb 2-8):** Micro-Intervention 1 workshops introduce teachers to 12 intervention tasks
- **Weeks 4-6 (Feb 9-29):** Teachers practice selected interventions and log daily (~10 min/day)
- This module captures **Practice Trajectory Signals** for the NEP-2020 Readiness Index

### 1.3 Design Principles

- **Trust-based reflection** over surveillance
- **Simplicity** — minimal friction for daily logging
- **Bilingual support** — English and Marathi toggle
- **Mobile-friendly** — teachers may log from phones

---

## 2. User Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US-1 | Teacher | Select 3-5 intervention tasks from 12 options | I can focus on specific practices during the reflection period |
| US-2 | Teacher | See my selected tasks organized by Foundational Principle | I understand how my choices align with NEP goals |
| US-3 | Teacher | Log daily whether I practiced each selected intervention | I can track my consistency |
| US-4 | Teacher | Add optional comments for each daily log | I can capture reflections and context |
| US-5 | Teacher | Change my selected interventions mid-cycle | I can adapt if some tasks don't fit my context |
| US-6 | Teacher | View my progress over the 21-day period | I can see patterns in my practice |
| US-7 | Teacher | Toggle between English and Marathi | I can use the interface in my preferred language |
| US-8 | Admin | View aggregated logging data | I can identify practice consistency and FP-specific patterns |

---

## 3. Functional Requirements

### 3.1 Screen 1: Intervention Choice Selection

**Purpose:** Teacher selects 3-5 intervention tasks from 12 available options

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Display all 12 intervention tasks grouped by Foundational Principle (FP) | Must |
| FR-1.2 | Each task shows: Task number, English label, English description | Must |
| FR-1.3 | Toggle to show Marathi label and description | Must |
| FR-1.4 | Teacher can select minimum 3, maximum 5 tasks | Must |
| FR-1.5 | Show running count of selected tasks (e.g., "3 of 5 selected") | Must |
| FR-1.6 | Validate selection count before allowing submission | Must |
| FR-1.7 | Show confirmation modal before saving selection | Should |
| FR-1.8 | Allow teacher to modify selection at any time during the 21-day period | Must |
| FR-1.9 | If modifying, show warning that this affects logging consistency | Should |
| FR-1.10 | Save selection with timestamp | Must |

**Data Captured:**
- Teacher ID
- Selected task IDs (array of 3-5)
- Selection timestamp
- Modification history (if changed)

---

### 3.2 Screen 2: Daily Logging

**Purpose:** Teacher logs daily practice of selected interventions

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Display only the teacher's selected interventions (3-5 tasks) | Must |
| FR-2.2 | Show current date prominently | Must |
| FR-2.3 | For each task, provide checkbox to mark "Done today" | Must |
| FR-2.4 | For each task, provide optional text field for comment (max 280 chars) | Must |
| FR-2.5 | Show task label in current language (toggle available) | Must |
| FR-2.6 | Auto-save on checkbox change (no submit button needed) | Should |
| FR-2.7 | Show visual feedback on save (checkmark animation) | Should |
| FR-2.8 | Allow logging for current day only (no backdating) | Must |
| FR-2.9 | Show mini-progress indicator (days logged / 21) | Should |
| FR-2.10 | Link to "Change my selections" (Screen 1) | Must |
| FR-2.11 | Show encouragement message based on streak | Nice |

**Data Captured:**
- Teacher ID
- Date
- For each selected task:
  - Task ID
  - Completed (boolean)
  - Comment (string, optional)
- Timestamp

---

### 3.3 Screen 3: Progress Dashboard (Main View)

**Purpose:** Teacher views their selection and 21-day logging history

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Show teacher's selected interventions with FP tags | Must |
| FR-3.2 | Display tabular view: Tasks on rows, Dates (1-21) on columns | Must |
| FR-3.3 | Each cell shows checkbox icon (filled = done, empty = not done, gray = future) | Must |
| FR-3.4 | Hover on cell shows comment as tooltip (if comment exists) | Must |
| FR-3.5 | Click on cell shows comment in modal/popover (mobile-friendly) | Should |
| FR-3.6 | Show completion percentage per task | Should |
| FR-3.7 | Show overall completion percentage | Should |
| FR-3.8 | Highlight current day column | Must |
| FR-3.9 | Horizontal scroll for date columns on smaller screens | Must |
| FR-3.10 | Language toggle affects task labels | Must |
| FR-3.11 | Export data option (CSV) for teacher's own records | Nice |
| FR-3.12 | Link to daily logging (Screen 2) | Must |
| FR-3.13 | Link to change selections (Screen 1) | Must |

**Visual States for Cells:**
- ✅ Green filled checkbox — Done, with comment
- ☑️ Green outline checkbox — Done, no comment
- ⬜ Empty checkbox — Not done (past date)
- 🔲 Gray checkbox — Future date (not yet loggable)

---

## 4. Intervention Task Master Data

### 4.1 Complete Task List

| ID | English Label | English Description | Marathi Label | Marathi Description | FP |
|----|---------------|---------------------|---------------|---------------------|-----|
| T01 | Notice One Learner | Pick one student today and notice how they engage (not marks) | एका विद्यार्थ्याकडे लक्ष द्या | आज एका विद्यार्थ्याची निवड करा आणि तो कसा सहभागी होतो ते पहा (गुण नाही) | FP-1 |
| T02 | One Adjustment | Make one small adjustment (pace, example, grouping) for a learner | एक छोटा बदल करा | एका विद्यार्थ्यासाठी एक छोटा बदल करा (वेग, उदाहरण, गट) | FP-1 |
| T03 | Change One Example | Replace one textbook example with a real-life/contextual one | एक उदाहरण बदला | पाठ्यपुस्तकातील एक उदाहरण वास्तविक जीवनाशी जोडा | FP-2 |
| T04 | Ask a Why / How | Ask at least one "why" or "how" question during teaching | का / कसे विचारा | शिकवताना किमान एक "का" किंवा "कसे" प्रश्न विचारा | FP-2 |
| T05 | End-of-Class Reflection | At end of class, mentally note one thing that worked / didn't | तासाअखेरीस चिंतन | तासाच्या शेवटी एक गोष्ट जी चांगली झाली / नाही ती लक्षात ठेवा | FP-3 |
| T06 | Try One Small Change | Try one change in the next class based on your reflection | एक नवीन प्रयत्न करा | तुमच्या चिंतनावर आधारित पुढच्या तासात एक बदल करा | FP-3 |
| T07 | Quick Check | Ask 2–3 students to explain an answer in their own words | झटपट तपासणी | २-३ विद्यार्थ्यांना त्यांच्या शब्दात उत्तर समजावून सांगायला सांगा | FP-4 |
| T08 | Spot One Pattern | Notice one common mistake or misunderstanding today | एक नमुना ओळखा | आज एक सामान्य चूक किंवा गैरसमज लक्षात घ्या | FP-4 |
| T09 | Teacher Touchpoint | Share one classroom moment with another teacher | शिक्षक संवाद | एका वर्गातील क्षण दुसऱ्या शिक्षकासोबत शेअर करा | FP-5 |
| T10 | Parent Signal | Share one positive learning observation with a parent (informal) | पालक संवाद | पालकांसोबत एक सकारात्मक शिक्षण निरीक्षण शेअर करा (अनौपचारिक) | FP-5 |
| T11 | Student Voice | Ask one student: "What helped you learn today?" | विद्यार्थ्याचा आवाज | एका विद्यार्थ्याला विचारा: "आज तुला शिकायला काय मदत झाली?" | FP-1 |
| T12 | Pause & Name | Pause once and name what students are doing well in learning | थांबा आणि सांगा | एकदा थांबा आणि विद्यार्थी शिकण्यात काय चांगले करत आहेत ते सांगा | FP-4 |

### 4.2 Tasks by Foundational Principle

| FP | Theme (English) | Theme (Marathi) | Task IDs |
|----|-----------------|-----------------|----------|
| FP-1 | Every Child is Unique | हर बच्चा अनूठा है | T01, T02, T11 |
| FP-2 | Holistic & Experiential Learning | समग्र एवं अनुभवात्मक शिक्षा | T03, T04 |
| FP-3 | Reflective Practitioner | चिंतनशील शिक्षक | T05, T06 |
| FP-4 | Assessment for Learning | सीखने के लिए आकलन | T07, T08, T12 |
| FP-5 | Collaboration | सहभागिता | T09, T10 |

---

## 5. UI/UX Specifications

### 5.1 Design System

Follow **PragyaWorks Design System** (reference: pragyaworks-design-system.md)

**Colors:**
- Primary Orange: `#EF851D`
- Charcoal Gray (body text): `#5B5B5B`
- Medium Gray (secondary): `#ABABAB`
- Light Gray (backgrounds): `#F5F5F5`
- White: `#FFFFFF`
- Success Green: `#22C55E`
- Warning Amber: `#F59E0B`

**Typography:**
- Headings: Open Sans, Semi-Bold
- Body: Open Sans, Regular, 16px
- FP Tags: Open Sans, 12px, uppercase

**Components:**
- Cards with 8px border-radius, subtle shadow
- Buttons: 6px border-radius, 12px 24px padding
- Checkboxes: Custom styled with brand orange

### 5.2 Language Toggle

- Position: Top-right of content area
- Label: "EN | मराठी"
- Clicking toggles all task labels and descriptions
- Current language highlighted in orange
- Persist preference in localStorage

### 5.3 Responsive Breakpoints

- Desktop: 1200px+ (full table view)
- Tablet: 768px-1199px (horizontal scroll for table)
- Mobile: <768px (card-based view for logging, simplified table for dashboard)

---

## 6. Data Model

### 6.1 Teacher Selection

```json
{
  "teacher_id": "T12345",
  "school_id": "S001",
  "selected_tasks": ["T01", "T03", "T05", "T07", "T10"],
  "selection_date": "2025-02-09T10:30:00Z",
  "modification_history": [
    {
      "date": "2025-02-15T08:00:00Z",
      "previous_tasks": ["T01", "T03", "T05", "T07", "T09"],
      "new_tasks": ["T01", "T03", "T05", "T07", "T10"]
    }
  ]
}
```

### 6.2 Daily Log Entry

```json
{
  "teacher_id": "T12345",
  "log_date": "2025-02-10",
  "entries": [
    {
      "task_id": "T01",
      "completed": true,
      "comment": "Noticed Ramesh was very engaged during group work"
    },
    {
      "task_id": "T03",
      "completed": true,
      "comment": ""
    },
    {
      "task_id": "T05",
      "completed": false,
      "comment": ""
    }
  ],
  "logged_at": "2025-02-10T16:45:00Z"
}
```

---

## 7. Wireframes

### 7.1 Screen 1: Intervention Choice Selection

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [Myelin Logo]                                          EN | मराठी     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Select Your Intervention Tasks                                         │
│  Choose 3-5 tasks to practice over the next 21 days                    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ FP-1: Every Child is Unique                                     │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ [ ] T01: Notice One Learner                                     │   │
│  │     Pick one student today and notice how they engage           │   │
│  │                                                                  │   │
│  │ [ ] T02: One Adjustment                                         │   │
│  │     Make one small adjustment for a learner                     │   │
│  │                                                                  │   │
│  │ [ ] T11: Student Voice                                          │   │
│  │     Ask one student: "What helped you learn today?"             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ FP-2: Holistic & Experiential Learning                          │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ [✓] T03: Change One Example                                     │   │
│  │     Replace one textbook example with real-life one             │   │
│  │                                                                  │   │
│  │ [✓] T04: Ask a Why / How                                        │   │
│  │     Ask at least one "why" or "how" question                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ... (FP-3, FP-4, FP-5 sections) ...                                   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Selected: 2 of 3-5 tasks    [Need at least 1 more]             │   │
│  │                                                                  │   │
│  │                              [ Save My Choices ] (disabled)      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Screen 2: Daily Logging

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [Myelin Logo]                                          EN | मराठी     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Daily Practice Log                          Day 5 of 21 | Feb 13      │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ [✓] T03: Change One Example                            FP-2     │   │
│  │     Replace one textbook example with real-life one             │   │
│  │     ┌─────────────────────────────────────────────────────┐     │   │
│  │     │ Used example of local market for fractions...      │     │   │
│  │     └─────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ [✓] T04: Ask a Why / How                               FP-2     │   │
│  │     Ask at least one "why" or "how" question                    │   │
│  │     ┌─────────────────────────────────────────────────────┐     │   │
│  │     │ Add a comment (optional)...                        │     │   │
│  │     └─────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ [ ] T05: End-of-Class Reflection                       FP-3     │   │
│  │     At end of class, note one thing that worked / didn't        │   │
│  │     ┌─────────────────────────────────────────────────────┐     │   │
│  │     │ Add a comment (optional)...                        │     │   │
│  │     └─────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ... (remaining selected tasks) ...                                     │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│  [Change My Selections]                           ✓ Auto-saved         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Screen 3: Progress Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [Myelin Logo]                                          EN | मराठी     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  My Practice Progress                                                   │
│  21-Day Reflection Journey | Day 5 of 21                               │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Your Selected Tasks:                                             │   │
│  │ T03 (FP-2) | T04 (FP-2) | T05 (FP-3) | T07 (FP-4) | T10 (FP-5) │   │
│  │                                          [Change Selections]     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Progress Overview                                    76% Done    │   │
│  │ ████████████████████░░░░░░░░                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐
│  │ Task              │ 1  2  3  4  5* 6  7  8  ... 21 │ Done  │      │
│  ├───────────────────┼────────────────────────────────┼───────┤      │
│  │ T03: Change One   │ ✓  ✓  ✓  ✓  ✓  ○  ○  ○  ... ○  │ 5/5   │      │
│  │ Example           │ 💬    💬       💬                │ 100%  │      │
│  ├───────────────────┼────────────────────────────────┼───────┤      │
│  │ T04: Ask Why/How  │ ✓  ✓  ✗  ✓  ✓  ○  ○  ○  ... ○  │ 4/5   │      │
│  │                   │    💬                           │ 80%   │      │
│  ├───────────────────┼────────────────────────────────┼───────┤      │
│  │ T05: Reflection   │ ✓  ✗  ✓  ✗  ○  ○  ○  ○  ... ○  │ 2/4   │      │
│  │                   │ 💬    💬                        │ 50%   │      │
│  ├───────────────────┼────────────────────────────────┼───────┤      │
│  │ T07: Quick Check  │ ✓  ✓  ✓  ✓  ✓  ○  ○  ○  ... ○  │ 5/5   │      │
│  │                   │                                │ 100%  │      │
│  ├───────────────────┼────────────────────────────────┼───────┤      │
│  │ T10: Parent Signal│ ✗  ✗  ✓  ✗  ✓  ○  ○  ○  ... ○  │ 2/5   │      │
│  │                   │       💬    💬                  │ 40%   │      │
│  └───────────────────┴────────────────────────────────┴───────┘      │
│                                                                         │
│  Legend: ✓ Done  ✗ Not done  ○ Future  💬 Has comment  * Today         │
│                                                                         │
│  [Log Today's Practice]                              [Export CSV]       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Analytics & Reporting

### 8.1 Teacher-Level Metrics

- Completion rate per task (%)
- Overall completion rate (%)
- Streak count (consecutive days logged)
- Comment frequency
- Selection modification count

### 8.2 Aggregate Metrics (for Admin/Myelin)

- FP-wise task selection distribution
- Task-wise completion rates across teachers
- Practice consistency vs drop-off patterns
- Schools/clusters with high engagement
- Common friction points (low-completion tasks)

---

## 9. Technical Considerations

### 9.1 Platform

- **Frontend:** React component within Myelin portal
- **Backend:** Existing Myelin API infrastructure
- **Database:** PostgreSQL (or existing Myelin DB)

### 9.2 Offline Support

- Consider Progressive Web App (PWA) for offline logging
- Sync when connection restored
- Local storage fallback

### 9.3 Performance

- Lazy load task descriptions
- Pagination for dashboard table (if needed)
- Optimize for low-bandwidth scenarios (rural schools)

---

## 10. Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Design & PRD | Week 1 | PRD, Wireframes, UI Mockups |
| Development | Week 2-3 | Frontend screens, API integration |
| Testing | Week 4 | QA, UAT with sample teachers |
| Deployment | Before Feb 9 | Production release |

---

## 11. Success Criteria

| Metric | Target |
|--------|--------|
| Teacher adoption | 80% of workshop participants select tasks |
| Logging consistency | 60% teachers log at least 15 of 21 days |
| Comment engagement | 30% of log entries include comments |
| System uptime | 99.5% during logging period |

---

## 12. Open Questions

1. Should there be push notifications/reminders for daily logging?
2. Should teachers see peer comparison (gamification)?
3. Integration with HPC (Holistic Progress Card) system?
4. Admin dashboard requirements for school coordinators?

---

## 13. Appendix

### A. Foundational Principles Reference

| FP | Full Name | NEP-2020 Alignment |
|----|-----------|-------------------|
| FP-1 | Every Child is Unique | Recognizing individual differences, inclusive education |
| FP-2 | Holistic & Experiential Learning | Learning by doing, connecting to real life |
| FP-3 | Reflective Practitioner | Teacher self-reflection, continuous improvement |
| FP-4 | Assessment for Learning | Formative assessment, understanding over marks |
| FP-5 | Collaboration | Teacher-parent-community partnership |

### B. Related Documents

- Project Kshitij Execution Framework
- PragyaWorks Design System
- Myelin Portal Technical Documentation

---

*Document Version: 1.0*  
*Last Updated: January 2026*  
*Status: Draft for Review*
