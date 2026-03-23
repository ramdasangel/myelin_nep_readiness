# Project Kshitij - Database ERD Documentation

## Overview
This document describes the Entity Relationship Diagram (ERD) for Project Kshitij (क्षितिज) - NEP-2020 Readiness Index system by Myelin.

---

## Complete ERD Diagram

```mermaid
erDiagram
    Schools ||--o{ SchoolBranches : "has many"
    Schools {
        ObjectId _id PK
        string SchoolName
        string SchoolCode
        string Board
        string Medium
        boolean IsActive
    }

    SchoolBranches ||--o{ Users : "has many"
    SchoolBranches ||--o{ Teachers : "has many"
    SchoolBranches ||--o{ Students : "has many"
    SchoolBranches {
        ObjectId _id PK
        ObjectId SchoolID FK
        string BranchName
        string BranchCode
        string Location
        string Address
        boolean IsActive
    }

    Users ||--o{ DiagnosticAttempt : "takes"
    Users ||--o{ UserTaskMapping : "assigned"
    Users ||--o{ UserDailyProgress : "logs"
    Users {
        ObjectId _id PK
        ObjectId BranchID FK
        string FirstName
        string LastName
        string Mobile
        string Email
        string Role
        boolean IsActive
    }

    Teachers {
        ObjectId _id PK
        ObjectId BranchID FK
        ObjectId UserID FK
        string FirstName
        string LastName
        string Mobile
        array Subjects
        array Classes
    }

    DiagnosticQuestionSet ||--o{ DiagnosticQuestion : "contains"
    DiagnosticQuestionSet ||--o{ DiagnosticAttempt : "attempted via"
    DiagnosticQuestionSet {
        ObjectId _id PK
        string questionSetCode UK
        string questionSetName
        string description
        string targetAudience
        string language
        int questionCount
        boolean isActive
    }

    DiagnosticQuestion {
        ObjectId _id PK
        ObjectId questionSetId FK
        string questionCode
        string questionText
        string questionType
        string category
        array options
        int correctOption
        int sortOrder
    }

    DiagnosticAttempt ||--o{ QuestionResponse : "contains"
    DiagnosticAttempt {
        ObjectId _id PK
        ObjectId userId FK
        ObjectId questionSetId FK
        string questionSetCode
        datetime startTime
        datetime endTime
        string status
        int score
    }

    QuestionResponse {
        ObjectId _id PK
        ObjectId attemptId FK
        ObjectId questionId FK
        string questionText
        string questionType
        string category
        int selectedOption
        string selectedOptionText
        boolean isCorrect
    }

    MicroInterventionTasks ||--o{ UserTaskMapping : "mapped to"
    MicroInterventionTasks {
        ObjectId _id PK
        string taskCode
        string taskTitle
        string taskDescription
        string category
        string frequency
        int points
        boolean isActive
    }

    UserTaskMapping ||--o{ UserDailyProgress : "tracked by"
    UserTaskMapping {
        ObjectId _id PK
        ObjectId userId FK
        ObjectId taskId FK
        string taskCode
        datetime selectedDate
        string status
    }

    UserDailyProgress {
        ObjectId _id PK
        ObjectId userId FK
        ObjectId taskMappingId FK
        date progressDate
        string status
        string notes
        int pointsEarned
    }
```

---

## Simplified Flow Diagram

```mermaid
flowchart TB
    subgraph Organization["🏫 Organization Structure"]
        SCH[Schools<br/>33 records]
        BR[SchoolBranches<br/>234 records]
        SCH --> BR
    end

    subgraph People["👥 People"]
        USR[Users<br/>3,056 records]
        TCH[Teachers<br/>16,123 records]
        STU[Students<br/>89,351 records]
        BR --> USR
        BR --> TCH
        BR --> STU
    end

    subgraph Assessment["📋 Kshitij Assessment"]
        QS[DiagnosticQuestionSet<br/>12 sets]
        DQ[DiagnosticQuestion<br/>191 questions]
        DA[DiagnosticAttempt<br/>1,308 attempts]
        QR[QuestionResponse<br/>27,823 responses]

        QS --> DQ
        QS --> DA
        USR --> DA
        DA --> QR
    end

    subgraph Intervention["🎯 Intervention Tasks"]
        MIT[MicroInterventionTasks<br/>12 tasks]
        UTM[UserTaskMapping<br/>3 mappings]
        UDP[UserDailyProgress<br/>3 records]

        MIT --> UTM
        USR --> UTM
        UTM --> UDP
    end

    style Organization fill:#e1f5fe
    style People fill:#fff3e0
    style Assessment fill:#e8f5e9
    style Intervention fill:#fce4ec
```

---

## Data Flow for NEP Readiness Assessment

```mermaid
flowchart LR
    subgraph Input
        U[User/Teacher]
        B[Branch Info]
    end

    subgraph QuestionSets["Question Sets (12)"]
        direction TB
        NEP["NEP Orientation<br/>1234, 7890"]
        TR["Teacher Readiness<br/>103"]
        LA["Leader Awareness<br/>104"]
        BE["Baseline English<br/>base001, base002"]
        BM["Baseline Marathi<br/>base003, base004"]
    end

    subgraph Response
        ATT[DiagnosticAttempt]
        RES[QuestionResponse]
    end

    subgraph Intervention
        TASK[12 Micro Tasks<br/>T01-T12]
        PROG[Daily Progress]
    end

    U --> ATT
    B --> ATT
    QuestionSets --> ATT
    ATT --> RES
    RES --> TASK
    TASK --> PROG
```

---

## Collection Details

### Organization Structure

| Collection | Records | Description |
|------------|---------|-------------|
| Schools | 33 | Parent organization/school entities |
| SchoolBranches | 234 | Individual school branches/locations |

### People

| Collection | Records | Description |
|------------|---------|-------------|
| Users | 3,056 | All user accounts (teachers, leaders, admins) |
| Teachers | 16,123 | Teacher-specific records with subject mappings |
| Students | 89,351 | Student records |

### Kshitij Assessment

| Collection | Records | Description |
|------------|---------|-------------|
| DiagnosticQuestionSet | 12 | Question set definitions |
| DiagnosticQuestion | 191 | Individual questions |
| DiagnosticAttempt | 1,308 | User attempts on question sets |
| QuestionResponse | 27,823 | Individual question responses |

### Intervention Tasks

| Collection | Records | Description |
|------------|---------|-------------|
| MicroInterventionTasks | 12 | Intervention task definitions (T01-T12) |
| UserTaskMapping | 3 | User-task assignments |
| UserDailyProgress | 3 | Daily progress logs |

---

## Question Sets Summary

| Code | Question Set Name | Responses |
|------|-------------------|-----------|
| 1234 | NEP-2020 school teacher orientation | 2,671 |
| 7890 | NEP-2020 school leadership orientation | 391 |
| 101 | Leadership Demo Test | 36 |
| 102 | Leadership Demo Test Marathi | 25 |
| 103 | राष्ट्रीय शैक्षणिक धोरण (एन. ई. पी.) बाबत शिक्षकांची तयारी | 10,945 |
| 104 | शाळा प्रमुखांची राष्ट्रीय शैक्षणिक धोरण (एन. ई. पी.) बाबत सजगता | 1,349 |
| base001 | Teacher - NEP-2020 Readiness – Enablement & Systems Baseline | 4,716 |
| base002 | Leader - NEP-2020 Readiness – Enablement & Systems Baseline | 367 |
| base003 | Teacher - NEP-2020 Readiness – Enablement & Systems Baseline (Marathi) | 6,704 |
| base004 | Leader - NEP-2020 Readiness – Enablement & Systems Baseline (Marathi) | 617 |
| 1000 | Teacher lens-NEP enablement & support Readiness | 2 |

**Total Responses: 27,823**

---

## Collection Relationship Summary

| Parent Collection | Child Collection | Relationship | Join Field |
|-------------------|------------------|--------------|------------|
| Schools | SchoolBranches | 1:Many | SchoolID |
| SchoolBranches | Users | 1:Many | BranchID |
| SchoolBranches | Teachers | 1:Many | BranchID |
| SchoolBranches | Students | 1:Many | BranchID |
| Users | DiagnosticAttempt | 1:Many | userId |
| DiagnosticQuestionSet | DiagnosticQuestion | 1:Many | questionSetId |
| DiagnosticQuestionSet | DiagnosticAttempt | 1:Many | questionSetCode |
| DiagnosticAttempt | QuestionResponse | 1:Many | attemptId |
| MicroInterventionTasks | UserTaskMapping | 1:Many | taskId |
| Users | UserTaskMapping | 1:Many | userId |
| UserTaskMapping | UserDailyProgress | 1:Many | taskMappingId |

---

## Category-wise Response Summary

| Category | Sets | Total Responses |
|----------|------|-----------------|
| NEP Orientation | 1234, 7890 | 3,062 |
| Teacher Readiness (Marathi) | 103 | 10,945 |
| Leader Awareness (Marathi) | 104 | 1,349 |
| Enablement Baseline (English) | base001, base002 | 5,083 |
| Enablement Baseline (Marathi) | base003, base004 | 7,321 |
| Demo Tests | 101, 102 | 61 |
| Other | 1000 | 2 |

---

*Generated on: 2026-02-08*
*Project: Kshitij (क्षितिज) - NEP-2020 Readiness Index*
