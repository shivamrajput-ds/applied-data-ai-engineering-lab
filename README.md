# Applied Data & AI Engineering Lab

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python\&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Engineering-150458?logo=pandas\&logoColor=white)](https://pandas.pydata.org/)
[![pytest](https://img.shields.io/badge/pytest-Testing-0A9EDC?logo=pytest\&logoColor=white)](https://pytest.org/)
[![uv](https://img.shields.io/badge/uv-Environment%20%26%20Dependencies-DE5FE9)](https://docs.astral.sh/uv/)
[![Status](https://img.shields.io/badge/Lab-Active-success)](#current-status)

> A hands-on engineering lab for converting realistic Data, Machine Learning, Applied AI, and backend requirements into clean, testable, reliable, and scalable systems.

This repository focuses on **engineering problem solving** rather than isolated syntax practice or algorithm drills.

Each engineering situation evolves through:

**Requirements → Assumptions → Design → Implementation → Testing → Edge Cases → Reliability → Scaling → System Design**

---

## Why This Repository Exists

Knowing Python, Pandas, SQL, FastAPI, Docker, MLflow, RAG frameworks, and ML libraries individually is different from receiving an unfamiliar requirement and building a reliable system from scratch.

This lab is designed to strengthen that second skill.

The focus is on learning how to:

* understand real-world requirements
* identify inputs, outputs, constraints, and assumptions
* discover failure modes
* design maintainable components
* write reliable implementation code
* handle malformed and duplicate data
* build testable systems
* make processing idempotent
* track processing state
* design safe retries
* isolate failures
* reason about memory and scale
* make justified architecture trade-offs
* avoid unnecessary overengineering

---

# Current Engineering Situations

| #  | Engineering Situation                                                               | Area                      | Level   | Status      |
| -- | ----------------------------------------------------------------------------------- | ------------------------- | ------- | ----------- |
| 01 | [Transaction Ingestion Pipeline](./engineering-situation-01-transaction-ingestion/) | Python / Data Engineering | Level 2 | In Progress |

Future situations will progressively move across ML Systems, APIs, SQL, RAG, Agentic AI, production reliability, and system design.

---

# Engineering Workflow

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
Write Tests
        ↓
Introduce Edge Cases
        ↓
Improve Reliability
        ↓
Handle Scale
        ↓
Design the Larger System
        ↓
Evaluate Trade-offs
```

> **Build the simplest correct solution for the current requirement, then evolve it only when new constraints justify additional complexity.**

---

# Engineering Situation 01

## Transaction Ingestion Pipeline

📂 [Open Situation 01](./engineering-situation-01-transaction-ingestion/)

### Situation

A fraud-detection ML team receives transaction files from upstream clients.

Incoming files cannot be assumed to be perfectly clean, unique, or reliable.

Possible problems include:

* exact duplicate records
* conflicting records sharing the same transaction ID
* missing identifiers
* invalid amounts
* unsupported currencies
* malformed timestamps
* duplicate file delivery
* failed processing attempts
* multiple files waiting for processing
* one malformed file among otherwise valid files

The goal is to evolve a simple Pandas validation script into a more reliable **batch ingestion component**.

---

# Transaction Schema

Each valid transaction contains:

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
txn_1001,cust_201,1250.50,INR,2026-09-01T09:15:00
txn_1002,cust_202,499.99,USD,2026-09-01T09:18:25
```

---

# Validation Layer

The pipeline currently validates:

* required transaction identifiers
* customer identifiers
* numeric transaction amounts
* positive amounts
* configurable currencies
* ISO timestamps
* exact duplicates
* conflicting duplicate transactions

Every record receives a `rejection_reason`.

Example reasons:

```text
duplicate record
conflicting duplicate
invalid transaction id
invalid customer id
invalid amount
invalid currency
invalid timestamp
```

---

## Exact Duplicate

Two records contain the same transaction ID and the same transaction data:

```text
txn_1001, cust_201, 1250.50, INR, ...
txn_1001, cust_201, 1250.50, INR, ...
```

The repeated record is treated as an exact duplicate.

---

## Conflicting Duplicate

The same transaction ID appears with different transaction data:

```text
txn_7001, cust_701, 1000.00, INR, ...
txn_7001, cust_701, 2500.00, INR, ...
```

This is treated differently from an exact duplicate because the pipeline cannot safely determine which version represents the real transaction.

---

# Record-Level Data Flow

```text
Incoming Transactions
        ↓
    validate_data()
        ↓
Validated DataFrame
        ↓
┌──────────────────────────────┐
│                              │
rejection_reason == ""     rejection_reason != ""
│                              │
↓                              ↓
Clean Records               Rejected Records
```

This keeps malformed records from unnecessarily crashing the complete transaction batch.

---

# Idempotent File Processing

The pipeline also handles repeated delivery of the same file.

Example:

```text
Client sends file
      ↓
Pipeline processes it
      ↓
Client/network retries
      ↓
Same file arrives again
```

Without protection, the same data could be processed repeatedly.

The current implementation calculates a **SHA-256 content hash** for every input file.

```text
Incoming File
      ↓
Calculate SHA-256
      ↓
Lookup Processing History
      ↓
Already Completed?
   ├── Yes → Skip
   └── No  → Process
```

---

## Why Content Hashing?

Filename alone is not a reliable identity.

These situations are possible:

```text
same filename + different content
```

and:

```text
different filename + same content
```

A SHA-256 hash fingerprints the actual file bytes.

The file is hashed incrementally in chunks instead of loading the whole file into memory purely for hashing.

---

# Processing State Lifecycle

A lightweight JSON state store tracks file processing history.

Each file hash can move through:

```text
NEW
 ↓
PROCESSING
 ├────────→ COMPLETED
 │
 └────────→ FAILED
```

Current behaviour:

| State      | Behaviour                    |
| ---------- | ---------------------------- |
| New        | Start processing             |
| Processing | Work has started             |
| Completed  | Skip repeated processing     |
| Failed     | Allow the file to be retried |

Example state:

```json
{
  "file_hash_here": {
    "file_name": "client_a_day1.csv",
    "status": "Completed"
  }
}
```

---

# Failure + Retry Behaviour

A processing attempt first persists:

```text
Processing
```

If all validation and output operations succeed:

```text
Processing
    ↓
Completed
```

If an exception occurs:

```text
Processing
    ↓
Failed
```

A failed file can be submitted again.

```text
Failed
  ↓
Retry
  ↓
Processing
  ↓
Completed
```

This behaviour has been manually verified with an intentionally failing transaction file.

---

# Multiple-File Batch Processing

The ingestion component now discovers multiple files from:

```text
data/raw/
```

Example:

```text
data/raw/
├── client_a_day1.csv
├── client_b_day1.csv
├── client_c_day1.csv
└── client_d_bad_schema.csv
```

Each file is handled independently.

Conceptually:

```text
Discover Raw Files
        ↓
For Each File
        ↓
Calculate Hash
        ↓
Check Previous Status
        ↓
┌───────────────────────────────┐
│                               │
Completed                    New / Failed
│                               │
Skip                        Processing
                                ↓
                             Process
                          ┌─────┴─────┐
                          ↓           ↓
                     Completed      Failed
```

---

# Failure Isolation

A major reliability requirement is:

> **One malformed file must not prevent unrelated files from being processed.**

This behaviour is now working.

Example batch:

```text
client_a_day1.csv       → Completed
client_b_day1.csv       → Completed
client_c_day1.csv       → Completed
client_d_bad_schema.csv → Failed
```

The fourth file intentionally has a schema problem.

Its failure does not stop the successfully processed files.

On another run:

```text
client_a → already processed, skip
client_b → already processed, skip
client_c → already processed, skip
client_d → retry because previous status = Failed
```

This combines:

* file-level idempotency
* retry behaviour
* state persistence
* failure isolation

---

# Per-File Outputs

Each successfully processed input file produces its own outputs rather than allowing later files to overwrite previous results.

Target structure:

```text
data/processed/
├── client_a_day1_clean.csv
├── client_a_day1_rejected.csv
├── client_b_day1_clean.csv
├── client_b_day1_rejected.csv
├── client_c_day1_clean.csv
└── client_c_day1_rejected.csv
```

This preserves traceability between:

```text
input file
    ↓
clean output
    ↓
rejected output
```

---

# Current Architecture

```text
                         ┌────────────────────┐
                         │     data/raw/      │
                         │ Multiple CSV Files │
                         └─────────┬──────────┘
                                   │
                                   ↓
                         Discover Input Files
                                   │
                                   ↓
                            SHA-256 Hash
                                   │
                                   ↓
                       ┌──────────────────────┐
                       │ Processing History   │
                       │ processed_files.json │
                       └──────────┬───────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
             Already Completed              New / Failed
                   │                             │
                 Skip                        Processing
                                                 │
                                                 ↓
                                          Read CSV File
                                                 │
                                                 ↓
                                           validate_data()
                                                 │
                         ┌───────────────────────┴───────────────────────┐
                         │                                               │
                         ↓                                               ↓
                    Clean Records                                 Rejected Records
                         │                                               │
                         ↓                                               ↓
                  Per-File Clean CSV                            Per-File Reject CSV
                         │
                         ↓
                     Completed

Any file-level exception
        ↓
      Failed
        ↓
Other files continue processing
```

---

# Current Repository Structure

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
    │   │   ├── client_a_day1.csv
    │   │   ├── client_b_day1.csv
    │   │   ├── client_c_day1.csv
    │   │   └── client_d_bad_schema.csv
    │   │
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

---

# Testing

The project uses `pytest`.

Current validation tests cover cases such as:

* duplicate records
* unsupported currencies
* negative amounts
* non-numeric amounts
* missing customer IDs
* whitespace-only customer IDs
* invalid timestamps
* invalid transaction IDs

Run:

```bash
uv run pytest -v
```

Manual reliability scenarios have also been used to verify:

```text
same completed file → skipped

failed file → retried

successful retry → Completed

one malformed file → Failed

other files → continue processing
```

---

# Current Constraints

The implementation intentionally remains simple.

```text
Execution      Single machine
Processing     Single process
Input          CSV files
Library        Pandas
State Store    JSON file
Storage        Local filesystem
Concurrency    None
```

Distributed systems are not introduced yet because the current requirements do not justify them.

---

# Engineering Principles Practiced

1. **Understand before implementing.**
2. **Do not invent unnecessary business rules.**
3. **Make assumptions explicit.**
4. **Treat malformed input as expected.**
5. **Do not let one bad record crash a whole batch.**
6. **Do not let one bad file stop unrelated files.**
7. **Distinguish exact duplicates from conflicting records.**
8. **Use configuration for changing business rules.**
9. **Design retries to be idempotent.**
10. **Persist important processing state.**
11. **Track intermediate processing states.**
12. **Separate file-level failure from row-level rejection.**
13. **Avoid unnecessary infrastructure.**
14. **Scale only when the existing design reaches a real constraint.**

---

# Development Setup

This repository uses [`uv`](https://docs.astral.sh/uv/) for environment and dependency management.

## Create Environment

```bash
uv venv .venv
```

## Activate — Git Bash / Windows

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

A skill is not marked **Strong** or **Independent** after a single engineering situation.

---

# Current Status

```text
Engineering Situation: 01
Title: Transaction Ingestion Pipeline
Level: 2
Status: In Progress

COMPLETED
────────────────────────────────────────────
✓ Core transaction validation
✓ Configurable currency validation
✓ Rejection-reason tracking
✓ Clean/rejected separation
✓ Exact duplicate detection
✓ Conflicting duplicate detection
✓ pytest validation coverage
✓ SHA-256 file fingerprinting
✓ Persistent processing history
✓ Idempotent processing
✓ Processing state persistence
✓ Failed-file retry
✓ Completed-file skip
✓ Multiple-file discovery
✓ Multiple-file processing
✓ Failure isolation
✓ Per-input-file output separation

CURRENT CHECKPOINT
────────────────────────────────────────────
Multiple-file resilient batch processing

NEXT
────────────────────────────────────────────
Schema validation
        ↓
Large-file / chunk processing
        ↓
Reliability tests
        ↓
Final scale & system-design round
```

---

# Remaining Work — Situation 01

Situation 01 is intentionally not finished yet.

The remaining engineering work includes:

### 1. File-Level Schema Validation

Before row validation starts, verify that required columns exist.

Example:

```text
Required:
transaction_id
customer_id
amount
currency
timestamp
```

A malformed schema should fail with a clear file-level reason instead of failing unexpectedly deep inside validation logic.

### 2. Large-File Processing

The current implementation uses:

```python
pd.read_csv(...)
```

which loads the file into memory.

The next scale constraint will introduce files that may not comfortably fit in RAM.

This will require reasoning about:

```text
chunked reads
memory usage
cross-chunk duplicate detection
output writing
state management
```

### 3. Reliability Testing

Important behaviours such as:

```text
Completed → skip
Failed → retry
one file fails → next file continues
```

should eventually be verified with automated tests rather than only manual runs.

### 4. Final System Design

The local implementation will finally be expanded conceptually to larger client volume and transaction throughput.

Only then will storage, workers, queues, databases, object storage, observability, and other architectural components be evaluated according to actual requirements.

---

# Future Lab Directions

After Situation 01, future engineering situations will cover different problem types, including:

* Python application logic
* concurrency and race conditions
* SQL analytics engineering
* ML training and inference systems
* prediction APIs
* asynchronous jobs
* model monitoring
* feature consistency
* RAG ingestion and retrieval
* hybrid search
* agent state and approval workflows
* caching
* production reliability
* MLOps
* architecture trade-offs

---

## Philosophy

> **Strong engineering is not knowing the maximum number of tools. It is being able to understand an unfamiliar problem, build the simplest correct solution, test its behaviour, handle failure safely, and evolve the design when the requirements change.**

---

## Repository

**GitHub:** [shivamrajput-ds/applied-data-ai-engineering-lab](https://github.com/shivamrajput-ds/applied-data-ai-engineering-lab)
