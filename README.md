# Applied Data & AI Engineering Lab

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python\&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Engineering-150458?logo=pandas\&logoColor=white)](https://pandas.pydata.org/)
[![pytest](https://img.shields.io/badge/pytest-Testing-0A9EDC?logo=pytest\&logoColor=white)](https://pytest.org/)
[![uv](https://img.shields.io/badge/uv-Package%20Management-DE5FE9)](https://docs.astral.sh/uv/)
[![Status](https://img.shields.io/badge/Lab-Active-success)](#current-status)

> A hands-on engineering lab for turning realistic Data, Machine Learning, Applied AI, and backend requirements into clean, testable, reliable, and scalable systems.

This repository focuses on **engineering problem solving**, not isolated syntax exercises or algorithm drills.

Every situation begins with an unfamiliar requirement and evolves through:

**Requirements → Assumptions → Design → Implementation → Testing → Edge Cases → Reliability → System Design → Scaling**

---

## Repository Goal

Knowing Python, Pandas, SQL, FastAPI, MLflow, Docker, RAG frameworks, and ML libraries individually is different from being able to receive an unfamiliar engineering requirement and build a sensible solution from scratch.

This lab exists to strengthen that second skill.

The focus is on learning how to:

* understand ambiguous requirements
* define inputs, outputs, constraints, and assumptions
* identify realistic failure modes
* design maintainable components
* write reliable implementation code
* handle malformed and duplicate data
* build testable systems
* design idempotent processing
* reason about retries and failures
* make justified architecture decisions
* scale systems only when requirements demand it
* avoid unnecessary overengineering

---

# Current Engineering Situations

| #  | Engineering Situation                                                               | Area                      | Level   | Status      |
| -- | ----------------------------------------------------------------------------------- | ------------------------- | ------- | ----------- |
| 01 | [Transaction Ingestion Pipeline](./engineering-situation-01-transaction-ingestion/) | Python / Data Engineering | Level 2 | In Progress |

More situations will progressively cover ML Systems, APIs, SQL, RAG, Agentic AI, production reliability, and system design.

---

# Engineering Workflow

Each situation follows an iterative engineering lifecycle:

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
Test Important Behaviour
        ↓
Introduce Hidden Edge Cases
        ↓
Improve Reliability
        ↓
Design for Larger Scale
        ↓
Evaluate Trade-offs
```

The objective is not to build the most complicated architecture.

> **Build the simplest correct system for the current requirements, then evolve it only when new constraints justify the complexity.**

---

# Engineering Situation 01

## Transaction Ingestion Pipeline

📂 [Open Situation 01](./engineering-situation-01-transaction-ingestion/)

### Situation

A fraud-detection ML team receives transaction data from an upstream system.

The incoming data cannot be trusted to always be clean or unique.

Possible issues include:

* exact duplicate transactions
* conflicting records with the same transaction ID
* missing transaction IDs
* missing customer IDs
* invalid transaction amounts
* unsupported currencies
* malformed timestamps
* repeated delivery of an already processed file

The ingestion component must validate the incoming data and prepare reliable outputs for downstream ML workflows.

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

The pipeline currently supports:

* required identifier validation
* configurable currency validation
* numeric amount validation
* rejection of non-positive amounts
* ISO timestamp validation
* exact duplicate detection
* conflicting duplicate detection
* separation of valid and rejected records
* preservation of rejection reasons
* processing malformed rows without crashing the entire batch
* duplicate-file detection using content hashing
* skipping a file that has already been successfully processed

---

# Validation Behaviour

Examples of rejection reasons currently tracked:

```text
duplicate record
conflicting duplicate
invalid transaction id
invalid customer id
invalid amount
invalid currency
invalid timestamp
```

### Exact Duplicate

```text
txn_1001, cust_201, 1250.50, INR, ...
txn_1001, cust_201, 1250.50, INR, ...
```

The repeated record is treated as a duplicate.

### Conflicting Duplicate

```text
txn_7001, cust_701, 1000.00, INR, ...
txn_7001, cust_701, 2500.00, INR, ...
```

The same transaction ID refers to different transaction data.

This is treated separately from a normal duplicate because the system cannot safely determine which version is correct.

---

# Current Data Flow

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
Clean Records             Rejected Records
│                             │
↓                             ↓
clean_transactions.csv    reject_transactions.csv
```

---

# Idempotent File Processing

The pipeline is being extended beyond row-level validation to handle repeated file delivery safely.

A common real-world scenario is:

```text
Upstream sends file
        ↓
Pipeline processes it
        ↓
Network / client retry
        ↓
Same file arrives again
```

Without idempotency, the same input could be processed multiple times.

The current implementation uses a **SHA-256 content hash** as a file fingerprint.

```text
Incoming File
      ↓
Calculate SHA-256
      ↓
Check Processing State
      ↓
Already Completed?
   ├── Yes → Skip
   └── No  → Process
```

---

## Why Hash the File?

Filename alone is not enough.

Two files can have:

```text
same filename
different content
```

or:

```text
different filename
same content
```

A content hash provides a fingerprint derived from the actual file bytes.

The file is hashed incrementally in chunks rather than loading the complete file into memory.

---

# Processing State

A lightweight JSON state file currently tracks processed input files.

Conceptually:

```json
{
  "file_hash_here": {
    "file_name": "raw_transactions_day1.csv",
    "status": "Completed"
  }
}
```

Current behaviour:

```text
New hash
    ↓
Process file
    ↓
Completed
    ↓
Persist file hash and status
```

If the same successfully processed content arrives again:

```text
Same SHA-256
      ↓
Status = Completed
      ↓
Skip duplicate processing
```

---

# Reliability Work In Progress

The next reliability stage will evolve processing state into:

```text
NEW
 ↓
PROCESSING
 ├──→ COMPLETED
 │
 └──→ FAILED
```

Expected behaviour:

| State      | Behaviour              |
| ---------- | ---------------------- |
| New file   | Process                |
| Processing | Track active execution |
| Completed  | Skip repeated file     |
| Failed     | Allow retry            |

Future work in the same engineering situation will also introduce:

* failed-file retry handling
* processing multiple files
* failure isolation between files
* large-file processing
* chunk-based CSV ingestion
* stronger state management
* storage trade-offs
* final scale/system-design analysis

---

# Current Architecture

```text
data/raw/
    │
    ↓
Incoming CSV
    │
    ├──→ SHA-256 Hash
    │       ↓
    │   Processing State
    │       ↓
    │   Completed?
    │    ├─ Yes → Skip
    │    └─ No
    │
    ↓
validate_data()
    │
    ├──→ Clean Records
    │       ↓
    │   clean_transactions.csv
    │
    └──→ Rejected Records
            ↓
        reject_transactions.csv
```

---

# Repository Structure

```text
applied-data-ai-engineering-lab/
│
├── README.md
├── .gitignore
│
└── engineering-situation-01-transaction-ingestion/
    │
    ├── data/
    │   ├── raw/
    │   └── processed/
    │
    ├── tests/
    │   └── test_validation.py
    │
    ├── main.py
    ├── processed_files.json
    ├── pyproject.toml
    └── uv.lock
```

Each future engineering situation will live in its own directory with its own implementation, tests, and architecture evolution.

---

# Testing

The project uses `pytest`.

Current tests cover important validation behaviour including:

* duplicate records
* invalid currencies
* negative amounts
* non-numeric amounts
* missing customer IDs
* whitespace-only customer IDs
* invalid timestamps
* invalid transaction IDs
* valid transaction behaviour

Run tests with:

```bash
uv run pytest -v
```

The goal is not to maximize the number of tests.

The goal is to verify important engineering behaviour and expose failure modes before scaling the design.

---

# Development Setup

This repository uses [`uv`](https://docs.astral.sh/uv/) for Python dependency and virtual-environment management.

## Create Environment

```bash
uv venv .venv
```

## Activate

Git Bash on Windows:

```bash
source .venv/Scripts/activate
```

## Install Dependencies

```bash
uv sync
```

## Run Situation 01

```bash
cd engineering-situation-01-transaction-ingestion
uv run python main.py
```

## Run Tests

```bash
uv run pytest -v
```

---

# Engineering Principles

1. **Understand the requirement before coding.**
2. **Do not invent business rules that were never specified.**
3. **Make assumptions explicit.**
4. **Treat malformed input as an expected condition.**
5. **Do not let one bad record unnecessarily crash an entire batch.**
6. **Distinguish exact duplicates from conflicting data.**
7. **Prefer independently testable components.**
8. **Use configuration where business behaviour can change.**
9. **Design retries to be safe and idempotent.**
10. **Persist important processing state instead of relying only on memory.**
11. **Optimize based on real constraints rather than hypothetical scale.**
12. **Avoid unnecessary abstractions and premature microservices.**
13. **Architecture choices must be justified through requirements and trade-offs.**

---

# Code Review Dimensions

Every implementation is reviewed across:

| Area                | Main Question                                                       |
| ------------------- | ------------------------------------------------------------------- |
| Correctness         | Does it satisfy the actual requirement?                             |
| Design              | Are responsibilities separated appropriately?                       |
| Readability         | Can another engineer understand it quickly?                         |
| Robustness          | What happens when input or execution fails?                         |
| Performance         | Is it suitable for the current scale?                               |
| Maintainability     | Can future requirements be added safely?                            |
| Testability         | Can behaviour be verified independently?                            |
| Production Concerns | Are configuration, retries, state, logging and failures considered? |

---

# Complexity Progression

| Level   | Focus                                   |
| ------- | --------------------------------------- |
| Level 1 | Single component                        |
| Level 2 | Multiple functions / classes            |
| Level 3 | Multiple modules / components           |
| Level 4 | Service-level architecture              |
| Level 5 | Production-like reliability and scaling |

The repository begins at **Level 2**, assuming familiarity with Python, Data Science, Machine Learning, APIs, and common engineering tooling.

---

# Areas This Lab Will Cover

### Python Engineering

* batch processing
* configuration
* caching
* retries
* rule engines
* file processing
* concurrency
* race conditions

### Data Engineering

* validation
* schema evolution
* deduplication
* idempotency
* chunk processing
* incremental ingestion
* Parquet
* partitioning
* late-arriving data

### SQL & Analytics Engineering

* CTEs
* joins
* window functions
* funnels
* cohorts
* retention
* rolling metrics
* query design

### Machine Learning Systems

* preprocessing pipelines
* training pipelines
* batch inference
* online inference
* feature consistency
* monitoring
* drift detection
* model versioning

### Backend for Data & AI

* FastAPI
* uploads
* asynchronous jobs
* request/response contracts
* dependency failures
* API versioning
* health checks

### NLP & RAG

* ingestion
* chunking
* retrieval
* metadata filters
* hybrid search
* reranking
* citations
* evaluation
* caching

### Agentic AI

* routing
* tool execution
* state
* retries
* human approval
* permissions
* audit trails

### Production & MLOps

* Docker
* CI/CD
* MLflow
* configuration
* structured logging
* model versioning
* monitoring
* rollback
* reliability

---

# Progress Tracker

Ratings are based only on engineering work actually completed.

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
| System Design        | Developing        |
| Scalability Thinking | Developing        |

No skill is marked **Strong** or **Independent** after a single exercise.

---

# Current Status

```text
Engineering Situation: 01
Title: Transaction Ingestion Pipeline
Level: 2
Status: In Progress

Completed:
✓ Core transaction validation
✓ Configurable currency validation
✓ Rejection-reason tracking
✓ Clean/rejected data separation
✓ Exact duplicate detection
✓ Conflicting duplicate detection
✓ pytest validation coverage
✓ SHA-256 file fingerprinting
✓ Persistent processing state
✓ Basic idempotent processing
✓ Skip already completed files

Current Stage:
Processing State Lifecycle
        ↓
Failure & Retry Handling
        ↓
Multiple File Processing
        ↓
Large File / Chunk Processing
        ↓
Final System Design
```

---

# Upcoming Engineering Directions

Future situations will progressively introduce:

* resilient file-processing systems
* concurrency and race-condition handling
* incremental ingestion
* large-file pipelines
* prediction APIs
* asynchronous ML jobs
* batch and online inference
* feature consistency
* model monitoring
* experiment tracking
* RAG ingestion and retrieval
* hybrid search
* agent approval workflows
* production reliability
* architecture and scaling trade-offs

---

## Philosophy

> **Strong engineering is not knowing the maximum number of tools. It is being able to understand an unfamiliar problem, choose appropriate tools, build the simplest correct solution, test it, handle failure, and evolve the design as requirements change.**

---

### Repository

**GitHub:** [shivamrajput-ds/applied-data-ai-engineering-lab](https://github.com/shivamrajput-ds/applied-data-ai-engineering-lab)
