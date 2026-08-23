# Applied Data & AI Engineering Lab

> A hands-on engineering practice repository for turning realistic Data, Machine Learning, Applied AI, and backend requirements into clean, testable, reliable, and scalable systems.

This repository is focused on **engineering problem solving**, not isolated syntax practice or algorithm drills.

Each exercise starts with an unfamiliar real-world situation and progresses through:

**Requirements → Assumptions → Design → Implementation → Testing → Edge Cases → System Design → Scaling**

---

## Repository Goal

Knowing Python, Pandas, SQL, FastAPI, MLflow, Docker, RAG frameworks, or ML libraries individually is different from being able to receive an unfamiliar requirement and convert it into a maintainable engineering solution.

This lab is designed to strengthen that second skill.

The focus is on learning how to:

* understand ambiguous requirements
* identify inputs, outputs, constraints, and failure modes
* design appropriate components
* write maintainable implementation code
* handle malformed or unexpected input
* build testable systems
* reason about reliability and scalability
* make justified architecture trade-offs
* avoid unnecessary overengineering

---

## Current Engineering Situations

| #  | Engineering Situation                                                               | Area                      | Level   | Status      |
| -- | ----------------------------------------------------------------------------------- | ------------------------- | ------- | ----------- |
| 01 | [Transaction Ingestion Pipeline](./engineering-situation-01-transaction-ingestion/) | Data Engineering / Python | Level 2 | In Progress |

More situations will be added progressively across Data Engineering, ML Systems, APIs, RAG, Agentic AI, MLOps, and System Design.

---

## Engineering Areas Covered

The lab progressively covers:

### Python Engineering

* validation engines
* configuration management
* batch processors
* retries
* caching
* rule engines
* plugin-style components
* logging
* file-processing services

### Data Engineering

* ingestion pipelines
* schema validation
* deduplication
* data-quality checks
* incremental processing
* idempotency
* Parquet pipelines
* partitioning
* changing schemas
* late-arriving data

### SQL & Analytics Engineering

* joins
* CTEs
* window functions
* ranking
* funnels
* cohort analysis
* retention
* rolling metrics
* deduplication
* analytical query design

### Machine Learning Systems

* reusable preprocessing
* training pipelines
* batch prediction
* real-time inference
* feature consistency
* model versioning
* experiment tracking
* model monitoring
* threshold configuration
* drift detection

### Backend Engineering for Data/AI

* FastAPI services
* request and response schemas
* upload-processing APIs
* asynchronous jobs
* validation
* exception handling
* dependency structure
* API versioning
* health endpoints

### NLP & RAG Systems

* document ingestion
* chunking
* metadata filtering
* retrieval
* hybrid search
* reranking
* citation tracking
* evaluation
* caching
* document updates

### Agentic AI Systems

* routing
* tool execution
* state management
* retries
* human approval
* audit trails
* agent permissions
* deterministic + LLM workflows

### Production & MLOps

* Docker
* testing
* CI/CD reasoning
* structured logging
* configuration
* experiment tracking
* model versioning
* monitoring
* rollback
* reliability

---

# Engineering Workflow

Each situation follows roughly the same engineering lifecycle:

```text
Understand Requirements
        ↓
Identify Inputs / Outputs
        ↓
Clarify Assumptions
        ↓
Identify Failure Modes
        ↓
Design Components
        ↓
Implement Core Logic
        ↓
Handle Edge Cases
        ↓
Write Tests
        ↓
Review Design
        ↓
Scale the Same System
        ↓
Evaluate Trade-offs
```

The goal is not to introduce complex infrastructure unnecessarily.

The preferred approach is:

> **Use the simplest design that correctly satisfies the current requirements, then evolve it only when new constraints justify additional complexity.**

---

# Engineering Situation 01

## Transaction Ingestion Pipeline

📂 [Open Engineering Situation 01](./engineering-situation-01-transaction-ingestion/)

### Situation

A fraud-detection ML team receives a daily transaction file from an upstream system.

The incoming data cannot be assumed to be perfectly clean.

Possible issues include:

* duplicate transactions
* missing transaction IDs
* missing customer IDs
* invalid transaction amounts
* unsupported currencies
* malformed timestamps
* conflicting records sharing the same transaction ID

The ingestion component must validate the incoming batch before the data can be consumed by downstream ML workflows.

---

## Input Schema

Each transaction contains:

```text
transaction_id
customer_id
amount
currency
timestamp
```

Example:

```csv
transaction_id,customer_id,amount,currency,timestamp
txn_1001,cust_201,1250.50,INR,2026-08-22T09:15:00
txn_1002,cust_202,499.99,USD,2026-08-22T09:18:25
```

---

## Functional Requirements

The pipeline must:

* validate required identifiers
* validate transaction amounts
* reject non-positive amounts
* validate supported currencies
* validate timestamps
* detect duplicate transaction IDs
* distinguish clean and rejected records
* preserve rejection reasons
* continue processing when individual rows are malformed

Conceptually:

```text
Raw Transactions
        ↓
Validation
        ↓
┌────────────────────┐
│                    │
Valid Records    Rejected Records
                      ↓
               Rejection Reason
```

---

## Initial Constraints

```text
Execution       Single machine
Processing      Single process
File size       Fits in memory
Volume          ~50,000 rows per file
Primary tool    Pandas
```

At this scale, introducing distributed processing or additional infrastructure would be unnecessary.

---

## Current Implementation

The current implementation includes:

* CSV loading
* exact duplicate detection
* transaction ID validation
* customer ID validation
* numeric amount validation
* configurable currency validation
* ISO timestamp validation
* rejection-reason tracking
* clean/rejected dataset separation

Example rejection reasons:

```text
duplicate_record
invalid transaction id
invalid customer id
invalid amount
invalid currency
invalid timestamp
```

---

## Current Data Flow

```text
raw_transactions.csv
        ↓
   validate_data()
        ↓
Validated DataFrame
        ↓
┌─────────────────────────────┐
│                             │
rejection_reason == ""    rejection_reason != ""
│                             │
↓                             ↓
clean_transactions.csv    reject_transactions.csv
```

---

# Repository Structure

```text
applied-data-ai-engineering-lab/
│
├── README.md
│
├── engineering-situation-01-transaction-ingestion/
│   │
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   │
│   ├── tests/
│   │
│   ├── main.py
│   ├── pyproject.toml
│   └── uv.lock
│
└── future engineering situations...
```

Each engineering situation lives in its own directory so that requirements, implementation, tests, and later architecture extensions remain isolated and easy to explore.

---

# Development Setup

This repository uses `uv` for Python environment and dependency management.

## Create Virtual Environment

```bash
uv venv .venv
```

## Activate Environment

Git Bash / Windows:

```bash
source .venv/Scripts/activate
```

## Install Dependencies

```bash
uv sync
```

## Run an Engineering Situation

Example:

```bash
cd engineering-situation-01-transaction-ingestion
uv run python main.py
```

---

# Testing Philosophy

Testing is introduced after the initial implementation rather than writing large test suites before the requirements are understood.

Depending on the situation, tests may cover:

* happy path
* invalid input
* missing values
* duplicate records
* malformed schemas
* boundary conditions
* dependency failure
* idempotency
* large input
* unexpected upstream behavior

The goal is not simply to achieve a high test count.

The goal is to verify important engineering behavior.

---

# Code Review Dimensions

Implementations are evaluated across:

| Area                | Question                                                         |
| ------------------- | ---------------------------------------------------------------- |
| Correctness         | Does the implementation satisfy the requirement?                 |
| Design              | Are responsibilities separated appropriately?                    |
| Readability         | Can another engineer understand the code quickly?                |
| Robustness          | What happens when input or dependencies fail?                    |
| Performance         | Is the implementation appropriate for the current scale?         |
| Maintainability     | Can new requirements be added safely?                            |
| Testability         | Can components be verified independently?                        |
| Production Concerns | Are logging, configuration, errors and observability considered? |

---

# Scaling Phase

Once a local implementation works correctly, the same engineering situation is expanded.

Example progression:

```text
Version 1
50,000 rows/day
Single-machine Pandas pipeline

        ↓

Version 2
Larger files / repeated ingestion

        ↓

Version 3
Higher throughput / reliability requirements

        ↓

Architecture and scaling decisions
```

The important question becomes:

> **What actually becomes the bottleneck, and what change is justified by the new requirement?**

Technologies are not introduced simply because they are popular.

---

# Engineering Principles

1. **Understand before implementing.**

2. **Do not invent business rules that were never specified.**

3. **Make assumptions explicit.**

4. **Treat malformed input as an expected engineering condition.**

5. **Do not let one bad record unnecessarily crash an entire batch.**

6. **Prefer testable functions and components.**

7. **Keep configuration separate from core logic when requirements may change.**

8. **Optimize based on real constraints, not hypothetical scale.**

9. **Avoid unnecessary abstractions and premature microservices.**

10. **Architecture decisions must be justified through requirements and trade-offs.**

---

# Complexity Progression

| Level   | Focus                                   |
| ------- | --------------------------------------- |
| Level 1 | Single component                        |
| Level 2 | Multiple functions / classes            |
| Level 3 | Multiple modules / components           |
| Level 4 | Service-level architecture              |
| Level 5 | Production-like reliability and scaling |

This repository begins at **Level 2**, assuming familiarity with programming, Data Science, Machine Learning, APIs, and common engineering tools.

---

# Tech Stack

Technologies will vary according to the situation.

Common tools may include:

![Python](https://img.shields.io/badge/Python-Engineering-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Engineering-purple)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![pytest](https://img.shields.io/badge/pytest-Testing-yellow)
![Docker](https://img.shields.io/badge/Docker-Containers-blue)
![MLflow](https://img.shields.io/badge/MLflow-MLOps-lightblue)

Additional tools may include:

* NumPy
* SQL
* scikit-learn
* Parquet
* MLflow
* FastAPI
* Docker
* pytest
* NLP / RAG tooling
* LangGraph

Not every situation uses every technology.

---

# Progress Tracker

| Skill Area           | Current Status    |
| -------------------- | ----------------- |
| Coding Design        | Developing        |
| Python Engineering   | Developing        |
| Data Engineering     | Developing        |
| SQL                  | Not Evaluated Yet |
| API Design           | Not Evaluated Yet |
| ML Systems           | Not Evaluated Yet |
| RAG Systems          | Not Evaluated Yet |
| Agentic Systems      | Not Evaluated Yet |
| Testing              | Developing        |
| System Design        | Not Evaluated Yet |
| Scalability Thinking | Developing        |

Ratings are based only on completed engineering exercises.

---

# Current Status

```text
Engineering Situation: 01
Title: Transaction Ingestion Pipeline
Level: 2
Status: In Progress

Current Stage:
Implementation → Validation Improvements → Testing
```

---

# Upcoming Directions

Future situations will progressively explore:

* resilient file ingestion
* incremental data pipelines
* large-file processing
* prediction APIs
* batch ML inference
* model monitoring
* feature consistency
* experiment tracking
* document ingestion
* hybrid RAG retrieval
* multi-tenant RAG systems
* agent approval workflows
* asynchronous ML jobs
* production reliability
* system scaling and architecture trade-offs

---

## Philosophy

This repository is built around one central idea:

> **Strong engineering is not knowing the maximum number of tools. It is knowing how to understand a problem, select the right tools, build the simplest correct solution, test it, and evolve it when the requirements change.**
