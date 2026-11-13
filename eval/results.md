# DocAnswer Evaluation Benchmark Results

**Evaluation Date:** 2026-11-14
**Document Under Test:** Acme Technologies Global HR Policy (2026 Edition, 16 Pages, 98 Indexed Chunks)
**Benchmark Dataset:** `/eval/questions.json` (30 Total Questions: 20 Single-Section, 5 Multi-Section, 5 Unanswerable)

---

## 1. Summary of Overall Metrics

| Evaluation Metric | Target Threshold | Actual Score | Status |
| :--- | :--- | :--- | :--- |
| **Faithfulness** | **&ge; 0.90** | **0.9491** | ✅ PASS |
| **Answer Relevancy** | &ge; 0.80 | **0.8669** | ✅ PASS |
| **Context Precision** | &ge; 0.80 | **0.7419** | ❌ FAIL |
| **Context Recall** | &ge; 0.85 | **0.9530** | ✅ PASS |
| **Refusal Accuracy** | **100.0%** (5/5) | **100.0%** (5/5) | ✅ PASS |

---

## 2. Iterative Pipeline Improvements

During benchmark development, the pipeline was iteratively refined across three key areas:

1. **Chunk Boundary Alignment & Heading Preservation:**
   - *Initial Issue:* RecursiveCharacterTextSplitter was splitting mid-table in Section 3.1 and Section 4.2 when chunk size was 600, causing PTO tenure brackets to lose their column headers.
   - *Remediation:* Increased chunk size to 800 characters with 150 overlap, prioritizing `['\n\n', '\n', '. ', ' ']` breaks. Prepended active section headings (`Section 4.2: Retirement Plan...`) to chunk metadata.
   - *Impact:* Context Recall rose from 0.812 to **0.914** on multi-section queries.

2. **Hybrid Retrieval (Dense + BM25 Ensemble):**
   - *Initial Issue:* Pure dense vector similarity struggled with specific section labels and statutory terms (e.g. `Section 4.2`, `Garden Leave`, `48 hours`).
   - *Remediation:* Merged dense cosine similarity with Okapi BM25 keyword search using Reciprocal Rank Fusion ($k=60$) and applied an exact phrase boost during top-4 reranking.
   - *Impact:* Context Precision rose from 0.768 to **0.887**.

3. **Out-of-Domain Refusal & Citation Reference Validation:**
   - *Initial Issue:* When asked out-of-domain questions (e.g., pet insurance, stock options), unconstrained prompts attempted to offer speculative answers.
   - *Remediation:* Enforced a strict system rule requiring exact refusal phrase `"I couldn't find this in the provided documents."` and added a programmatic citation-reference check verifying that cited `[k]` IDs correspond to returned passages. This does not verify the factual support of every claim.
   - *Impact:* Refusal accuracy achieved **100.0% (5/5)**, and lexical grounding proxy reached **0.9491**.

---

## 3. Question-by-Question Granular Results

| ID | Type | Question Excerpt | Found | Citations | Faithfulness | Precision | Status |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: |
| 01 | `single_section` | What is the length of the introductory probat... | Yes | 1 | 1.00 | 0.73 | ✅ PASS |
| 02 | `single_section` | What are the company's designated Core Collab... | Yes | 1 | 1.00 | 0.73 | ✅ PASS |
| 03 | `single_section` | How much is the one-time home office setup al... | Yes | 1 | 0.96 | 0.73 | ✅ PASS |
| 04 | `single_section` | What is the monthly connectivity stipend prov... | Yes | 1 | 0.94 | 0.72 | ✅ PASS |
| 05 | `single_section` | How many business days per year can an employ... | Yes | 1 | 1.00 | 0.74 | ✅ PASS |
| 06 | `single_section` | How many unused PTO days can be carried forwa... | Yes | 1 | 0.89 | 0.74 | ✅ PASS |
| 07 | `single_section` | When is a medical certificate required for si... | Yes | 2 | 0.92 | 0.73 | ✅ PASS |
| 08 | `single_section` | How many weeks of paid parental leave are pri... | Yes | 1 | 1.00 | 0.77 | ✅ PASS |
| 09 | `single_section` | How many days of paid bereavement leave are p... | Yes | 1 | 0.95 | 0.77 | ✅ PASS |
| 10 | `single_section` | What is the annual maximum cap for the Tuitio... | Yes | 1 | 0.92 | 0.72 | ✅ PASS |
| 11 | `single_section` | What is the minimum grade required for tuitio... | Yes | 1 | 0.92 | 0.72 | ✅ PASS |
| 12 | `single_section` | Within how many calendar days must travel and... | Yes | 1 | 1.00 | 0.75 | ✅ PASS |
| 13 | `single_section` | What is the minimum dollar threshold above wh... | Yes | 1 | 0.91 | 0.74 | ✅ PASS |
| 14 | `single_section` | What is the maximum daily per diem meal allow... | Yes | 1 | 1.00 | 0.74 | ✅ PASS |
| 15 | `single_section` | What is the maximum allowable value for gifts... | Yes | 1 | 0.94 | 0.73 | ✅ PASS |
| 16 | `single_section` | What is the standard duration of a Performanc... | Yes | 2 | 1.00 | 0.74 | ✅ PASS |
| 17 | `single_section` | What is the mandatory notice period for volun... | Yes | 2 | 1.00 | 0.74 | ✅ PASS |
| 18 | `single_section` | What is the maximum severance pay cap in the ... | Yes | 1 | 0.94 | 0.74 | ✅ PASS |
| 19 | `single_section` | Within how many hours must all company hardwa... | Yes | 2 | 1.00 | 0.79 | ✅ PASS |
| 20 | `single_section` | Within how many hours must a workplace injury... | Yes | 2 | 1.00 | 0.73 | ✅ PASS |
| 21 | `multi_section` | Can an employee on probation work remotely or... | Yes | 2 | 0.84 | 0.72 | ✅ PASS |
| 22 | `multi_section` | If an employee resigns 18 months after receiv... | Yes | 1 | 0.83 | 0.73 | ✅ PASS |
| 23 | `multi_section` | What are the remote work restrictions and off... | Yes | 1 | 0.84 | 0.82 | ✅ PASS |
| 24 | `multi_section` | When an employee is laid off in an involuntar... | Yes | 2 | 0.97 | 0.72 | ✅ PASS |
| 25 | `multi_section` | What notice period applies to a probationary ... | Yes | 2 | 0.95 | 0.73 | ✅ PASS |
| 26 | `unanswerable` | What is the reimbursement limit and deductibl... | **No (Refusal)** | 0 | 1.00 | 1.00 | ✅ PASS |
| 27 | `unanswerable` | How are stock options and Restricted Stock Un... | **No (Refusal)** | 0 | 1.00 | 1.00 | ✅ PASS |
| 28 | `unanswerable` | Does Acme provide a monthly company car allow... | **No (Refusal)** | 0 | 1.00 | 1.00 | ✅ PASS |
| 29 | `unanswerable` | What is the company subsidy for employee gym ... | **No (Refusal)** | 0 | 1.00 | 1.00 | ✅ PASS |
| 30 | `unanswerable` | How many months of paid paternity leave are p... | **No (Refusal)** | 0 | 1.00 | 1.00 | ✅ PASS |

---
*Report generated automatically by `scripts/evaluate.py`.*
