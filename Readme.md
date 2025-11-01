#🩺 GlucoSense — AI-Driven Smart Health Assistant
#🚀 Overview

GlucoSense is an AI-powered health monitoring and recommendation system designed for diabetic patients.
It integrates data from smartwatch sensors and periodic health forms, analyzes it using a local ML-powered Brain, and then generates personalized health suggestions via an LLM, which are reviewed by a doctor-in-the-loop before reaching the user.


#Architecture

┌────────────────────────────┐
│  Smartwatch (Mocked Data)  │
│  + Monthly User Form Data  │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│   Data Aggregator Layer    │
│  - collects hourly/daily    │
│  - merges form data         │
│  - outputs normalized JSON  │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│     Brain / Processing     │
│  - feature engineering      │
│  - spike detection backend  │
│  - ML model for risk score  │
│  - attaches “comments”      │
│  → produces daily insight   │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│     Reasoning Layer (LLM)  │
│  - builds contextual prompt │
│  - interprets and generates │
│    plain-language summary   │
│  - outputs safe suggestions │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Doctor Review Dashboard    │
│  - verifies or edits advice │
│  - stores approval status   │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│    Final Output to User    │
│  - approved suggestions     │
│  - risk summary             │
└────────────────────────────┘
