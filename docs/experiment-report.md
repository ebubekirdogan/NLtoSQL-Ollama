# Experiment Report: Prompt Strategy Comparison

This report documents the first experiment conducted as part of the CNC Text-to-SQL project: a comparison between **zero-shot** and **few-shot** prompting strategies for SQL generation.

## Objective

To measure whether providing the LLM with a small number of solved examples (few-shot) improves SQL generation accuracy compared to giving it only the task description and schema (zero-shot), using the same local model (Qwen2.5-Coder:7b) for both.

## Methodology

### Test Set

A fixed set of 14 natural language questions was created, covering five categories of increasing complexity:

| Category | Description | Count |
|---|---|---|
| Basic | Single table, no filtering | 3 |
| Medium | Single table with aggregation/filtering | 3 |
| Join | Requires joining two tables | 3 |
| Date-filtered | Requires filtering by a date range | 2 |
| Unanswerable | References data that does not exist in the schema | 3 |

Each question was paired with a reference SQL query (except unanswerable questions, which have no valid reference).

### Execution

Every question was run through both strategies using the same self-correction pipeline (up to 3 retry attempts on SQL execution errors), so both strategies were evaluated under identical conditions. This produced 28 total runs (14 questions × 2 strategies).

### Evaluation

Two separate metrics were tracked:

- **Execution accuracy**: whether the generated SQL ran without errors.
- **Result accuracy**: whether the query's result matched the expected (reference) answer.

Result accuracy was verified manually for each of the 28 generated queries, rather than through automated row-matching. An initial automated matching approach (comparing result sets via value overlap) was tested first but was found to produce false positives — for example, a query using the wrong aggregation logic (missing `GROUP BY`/`SUM`, effectively finding a single event instead of a total) coincidentally returned the same top result as the correct query, due to the small size of the test dataset. This was caught and corrected manually, and is discussed further under Findings.

### Few-shot Examples Used

Three examples were included in the few-shot prompt, covering a simple count, a single-table aggregation, and a join-based aggregation. None of the examples involved date filtering.

## Results

### Overall

| Strategy | Execution Accuracy | Result Accuracy |
|---|---|---|
| Zero-shot | 14/14 (100%) | 10/14 (71.4%) |
| Few-shot | 14/14 (100%) | 11/14 (78.6%) |

Both strategies produced syntactically valid, executable SQL in every case. The difference in performance is entirely attributable to logical/semantic correctness, not execution errors.

### By Category

| Category | Zero-shot | Few-shot |
|---|---|---|
| Basic | 3/3 | 3/3 |
| Medium | 3/3 | 3/3 |
| Join | 1/3 | 2/3 |
| Date-filtered | 1/2 | 1/2 |
| Unanswerable | 2/3 | 2/3 |

### Unanswerable Question Handling

A fallback rule was added to both prompt strategies instructing the model to return a fixed sentinel value (`SELECT 'CANNOT_ANSWER' AS note;`) when a question could not be answered using the given schema.

| Strategy | Correctly triggered fallback |
|---|---|
| Zero-shot | 2/3 |
| Few-shot | 2/3 |

Both strategies triggered the fallback correctly in 2 out of 3 unanswerable cases, but not consistently on the same questions — indicating the fallback behavior is unreliable regardless of prompting strategy.

## Findings

**1. Few-shot outperformed zero-shot overall, with the largest gap in join-based queries (1/3 → 2/3).** This aligns with the content of the few-shot examples, one of which demonstrated a join-based aggregation pattern.

**2. The improvement from few-shot was localized to patterns present in the examples.** No improvement was observed on date-filtered queries, since none of the three few-shot examples demonstrated date filtering. Both strategies made the same aggregation error on the same date-filtered question (using `ORDER BY ... LIMIT 1` instead of `GROUP BY` + `SUM`, effectively finding a single event instead of a machine's total). This suggests few-shot prompting improves performance on the specific patterns it demonstrates, rather than producing a general improvement in reasoning.

**3. A recurring logic error was identified: omitting `GROUP BY` when aggregating "total" or "most" across a table.** This occurred in both strategies (question 7 and 10) and represents a systematic weakness rather than a random failure — both queries were syntactically valid and executed successfully, but answered a different question than the one asked (a single longest event, rather than the total across events for each machine). This is an example of a "silent logic error": the query runs without error but returns a misleading result.

**4. The unanswerable-question fallback is not fully reliable.** Both strategies failed to trigger the fallback on at least one clearly unanswerable question, instead generating a plausible-looking but unrelated query. This is a known risk with LLM-based systems (the model defaulting to the closest available data rather than recognizing the absence of relevant data) and is not resolved by prompting strategy alone.

**5. A methodological finding: automated result-matching using value overlap is not reliable on small datasets.** A query with genuinely incorrect logic can coincidentally return the same result as the correct query when the underlying dataset is small. This experiment's results were therefore verified manually rather than relying solely on automated matching.

## Conclusion

Few-shot prompting provided a modest but real improvement in SQL generation accuracy (71.4% → 78.6%), concentrated specifically in query patterns demonstrated by the examples (joins). It did not improve performance on patterns absent from the examples (date filtering) or on the reliability of unanswerable-question detection. This suggests that, for this system, few-shot prompting acts as a targeted pattern-matching aid rather than a general accuracy booster, and that prompt design should prioritize including examples that cover the range of query patterns the system is expected to handle.