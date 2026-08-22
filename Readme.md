# Applied Data & AI Engineering Lab

A hands-on engineering practice repository focused on converting realistic Data Science, Machine Learning, Applied AI, and backend requirements into clean, testable, and scalable systems.

The goal of this repository is not to practice isolated syntax or algorithm questions.

Instead, each exercise starts with a practical engineering situation and follows the complete reasoning process:

**Requirements → Design → Implementation → Testing → Edge Cases → System Design → Scaling**

---

## Why This Repository Exists

Knowing individual tools such as Python, Pandas, FastAPI, MLflow, Docker, RAG frameworks, or SQL is different from being able to solve an unfamiliar engineering problem.

This repository is designed to strengthen that second skill.

Each engineering situation requires understanding the problem first, making assumptions explicit, designing appropriate components, writing the implementation, testing failure cases, and then thinking about how the same solution would evolve at larger scale.

---

## Areas Covered

The lab progressively covers:

* Python Application Engineering
* Data Engineering
* SQL and Analytics Engineering
* Machine Learning Systems
* FastAPI and Backend Engineering
* NLP and RAG Systems
* Agentic AI Workflows
* Testing and Reliability
* Production and MLOps Practices
* System Design
* Scalability and Architecture Trade-offs

---

## Engineering Approach

Each situation follows roughly this workflow:

```text
Understand Requirements
        ↓
Identify Inputs / Outputs
        ↓
Clarify Assumptions
        ↓
Design Components
        ↓
Implement Core Logic
        ↓
Handle Failures
        ↓
Write Tests
        ↓
Review Edge Cases
        ↓
Design for Scale
```

The emphasis is on choosing the simplest design that correctly satisfies the current requirements without unnecessary overengineering.

---

## Engineering Situation 01 — Transaction Ingestion Pipeline

### Problem

A fraud-detection ML team receives daily transaction data from an upstream system.

The raw data may contain:

* duplicate transactions
* missing identifiers
* invalid amounts
* unsupported currencies
* malformed timestamps
* conflicting transaction records

The ingestion component must validate and clean the incoming data before it is used by downstream ML workflows.

### Initial Requirements

Each transaction contains:

```text
transaction_id
customer_id
amount
currency
timestamp
```

The pipeline must:

* validate required fields
* validate transaction amounts
* validate supported currencies
* validate timestamps
* detect duplicate transaction IDs
* separate valid and rejected records
* preserve rejection reasons
* continue processing even when individual records are malformed

### Current Scale

```text
Single machine
Single process
~50,000 records per file
Input fits in memory
```

### Current Implementation

The first implementation uses Python and Pandas to:

* load raw CSV data
* remove duplicates
* validate currency values
* convert and validate transaction amounts
* validate transaction/customer identifiers
* validate timestamps
* generate clean and rejected datasets

The implementation is being improved incrementally as new reliability and edge-case requirements are introduced.

---

## Repository Structure

```text
applied-data-ai-engineering-lab/
│
├── README.md
│
├── engineering-situation-01-transaction-ingestion/
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
│
└── ...
```

Each future engineering situation will live in its own directory.

---

## Learning Principles

This repository follows a few rules:

1. Understand the requirement before writing code.
2. Avoid unnecessary abstractions.
3. Make important assumptions explicit.
4. Treat invalid input and dependency failures as normal engineering scenarios.
5. Write code that can be tested independently.
6. Improve the implementation only when requirements justify the additional complexity.
7. Evaluate performance and scalability based on actual constraints.
8. Prefer justified trade-offs over blindly choosing popular technologies.

---

## Tech Stack

Technologies will vary by situation and may include:

* Python
* Pandas
* NumPy
* SQL
* scikit-learn
* FastAPI
* pytest
* MLflow
* Docker
* Parquet
* NLP / RAG tooling
* LangGraph

Not every exercise uses every technology.

Tools are selected according to the problem rather than added unnecessarily.

---

## Progression

Exercises gradually increase in complexity:

```text
Level 1 → Single component
Level 2 → Multiple functions/classes
Level 3 → Multiple modules/components
Level 4 → Service-level architecture
Level 5 → Production-like systems with scale and reliability trade-offs
```

The repository begins from Level 2 because basic programming and Data/ML tooling fundamentals are already assumed.

---

## Current Status

```text
Engineering Situation 01
Transaction Ingestion Pipeline
Status: In Progress
Level: 2
```

More engineering situations will be added progressively across Data Engineering, ML Systems, APIs, RAG, Agentic AI, MLOps, and System Design.
