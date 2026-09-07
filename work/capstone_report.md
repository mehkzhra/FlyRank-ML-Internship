# Which Content Pages Should Be Reviewed First? An Honest Refresh-Priority Study

**Author:** Mehak Zahra  
**Lane:** Refresh / Content Opportunity Scoring  
**Repository:** [mehkzhra/FlyRank-ML-Internship](https://github.com/mehkzhra/FlyRank-ML-Internship)  
**Analysis date:** 5 September 2026

## Abstract

This study asks which measurable FlyRank content pages an editor should review first when review capacity is limited. I analyzed a public-safe 30,000-page internship slice and used the supplied 30-day comparison to define an observed-decline proxy. I compared a frozen low-CTR visibility rule with Logistic Regression and Random Forest on the same 6,163-page holdout containing seven entirely unseen client groups. The simple rule achieved Precision@50 of 0.78, compared with 0.74 for Logistic Regression and 0.60 for Random Forest; the negative modeling result kept the transparent rule as the operational queue. The output is a human-reviewed FlyRank content triage playbook, not a forecast of Google's algorithm or evidence that refreshing a page causes recovery.

## Introduction / problem statement

FlyRank content teams can have thousands of measurable pages but limited editorial review time. The decision is therefore not “will this page certainly improve?” but “which pages deserve scarce review time first, and which review route fits each one?” One row represents one anonymized content page; the output is a ranked queue with reason codes, and a FlyRank content editor or SEO analyst privately checks page, query, SERP, analytics, seasonality, and business context before acting.

A false positive costs editor time. A false negative can leave a meaningful decline unreviewed. Precision@50 matches a practical batch of 50 reviews, while ROC AUC and average precision show whether performance extends beyond one cutoff.

## Data

The analysis uses `data/raw/content_refresh_anonymized.csv`, the bundled public-safe starter release: 30,000 rows and 44 fields at one-row-per-content-page grain. Its measures include trailing 90-day search and engagement aggregates and two adjacent 30-day comparison windows. The repository documentation connects this slice to `flyrank_pseudonymized_warehouse_release_v20260703`, exported 3 July 2026; the full warehouse contains 78,835,655 daily content-performance rows spanning 27 January 2025 through 30 June 2026. **This experiment did not query that full fact table and is not a 79-million-row benchmark.**

The sample has 16,262 observed decline-proxy rows (54.21%). The grouped test split has 6,163 pages across seven entirely unseen client groups, with a 51.10% positive base rate.

No raw names, domains, URLs, titles, keywords, or queries are used or displayed. Pseudonymous content/client IDs are used only to preserve row identity and create the grouped split, never as model features. Direct label fields and components—`trend_direction`, `trend_pct`, `impressions_last_30d`, `impressions_prev_30d`, and their click/session counterparts—are excluded from the feature matrix.

## Methodology

### Label and assumptions

The binary proxy is `is_declining_label = 1` when supplied `trend_direction` is `down`: last-30-day impressions are more than 20% below the preceding 30 days. It describes an observed current-window decline, not a future outcome or the success of a refresh. The working assumption is only that current decline plus measurable opportunity is useful for prioritizing human review.

### Features

The learned models use 17 numeric and eight categorical source fields covering safe search-market context, content depth, trailing activity, active-day counts, age, update recency, CTR, average position, engagement, scroll, AI-traffic rate, and transparent tiers. Numeric missing values use median imputation plus missingness indicators; categories use most-frequent imputation and one-hot encoding.

### Baseline and models

The frozen baseline multiplies visibility percentile, position-1-to-20 opportunity, a CTR gap below 0.50%, and a 100-impression eligibility gate. Logistic Regression is the readable learned comparison; a constrained 250-tree Random Forest tests whether non-linear complexity earns its place. Seed 42 is fixed and Precision@50 is the primary metric.

### Validation and leakage checks

The split holds out 20% of the 32 client groups: 25 clients (23,837 rows) for training and seven clients (6,163 rows) for testing, with no group overlap. Baseline and models are evaluated on exactly those test rows. IDs and direct label-derived columns are absent from the feature matrix. A deliberate `trend_pct` leak drove grouped ROC AUC to 0.999; it was removed before reporting the honest result.

One residual limitation remains: `impressions_90d`, `clicks_90d`, `sessions_90d`, active-day counts, and ratios summarize a 90-day interval that overlaps the two 30-day periods defining the proxy. This does not directly give the answer to the model, but it prevents a clean future-prediction interpretation. The analysis is therefore contemporaneous triage, not forecasting.

## Results

| Method | ROC AUC | Average precision | Precision@50 | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| **Frozen rule baseline** | 0.562 | 0.561 | **0.780** | 0.033 | 0.063 |
| Logistic regression | 0.580 | 0.577 | 0.740 | 0.633 | 0.596 |
| Random forest | **0.612** | **0.596** | 0.600 | 0.611 | **0.602** |

The frozen rule identifies 39 observed-decline pages among its first 50, compared with 37 for Logistic Regression and 30 for Random Forest. Logistic Regression improves Precision@10 from 0.70 to 0.80, while Random Forest has the best overall ROC AUC. Neither learned model beats the rule at the chosen operational cutoff, so the playbook keeps the transparent rule instead of rewarding complexity.

For Logistic Regression, the largest held-out permutation AUC drops come from active impression days (0.0476), active session days (0.0419), content age (0.0260), and average position (0.0173). These are predictive importance measures, not causal effects. The modest grouped performance and concrete false positives/negatives support human review rather than automated action.

## Limitations & honest framing

1. The sample is 30,000 pages, not the complete 78.8M-row daily table; representativeness is not established.
2. The target is an operational, contemporaneous decline proxy—not future performance and not refresh success.
3. Trailing-90-day features overlap the proxy's component windows, so this is triage rather than a leakage-clean forecast.
4. One grouped holdout tests client transfer better than a random row split, but hyperparameter/model selection on that same holdout can make the reported result optimistic.
5. Different client histories form an unbalanced panel, and missing/zero-filled analytics can mean either no activity or unavailable tracking.
6. Feature importance describes how this fitted model splits the sample; it does not establish why pages declined.
7. No causal claim is made. A prospective experiment would be needed to learn whether acting on the queue improves outcomes.

## Ranked recommendations

1. **Review high-confidence, high-exposure candidates first.** Start with the top 50, confirm that the decline is real, and check editorial/business context before changing content.
2. **Route by reason code.** Review visible low-CTR pages for snippet/intent fit; send thin visible pages to expansion review; inspect low-engagement pages for experience and content-fit issues; monitor weak-evidence cases.
3. **Keep a human approval gate.** Never auto-publish, prune, redirect, or promise recovery from this score.
4. **Capture review outcomes.** Record accepted/rejected recommendations, action taken, review time, and later performance so the next label reflects intervention outcomes rather than current decline alone.
5. **Upgrade validation before production.** Build non-overlapping historical feature and future target windows from the daily warehouse, reserve a final untouched time/client test set, and compare against the same fixed baseline.

## Reproducibility

```bash
git clone https://github.com/mehkzhra/FlyRank-ML-Internship.git
cd FlyRank-ML-Internship
python -m pip install -r requirements.txt
python scripts/run_all.py
jupyter nbconvert --to notebook --execute work/notebooks/capstone.ipynb \
  --output capstone.ipynb --output-dir work/notebooks
```

Random seed: 42. Core dependencies are pinned in `requirements.txt`. Inspect the [capstone notebook](https://github.com/mehkzhra/FlyRank-ML-Internship/blob/main/work/notebooks/capstone.ipynb), [pipeline scripts](https://github.com/mehkzhra/FlyRank-ML-Internship/tree/main/scripts), and [generated report](https://github.com/mehkzhra/FlyRank-ML-Internship/blob/main/outputs/model_report.md).

## Acknowledgments & data credit

Author: **Mehak Zahra**. Built on the [FlyRank ML Internship dataset](https://flyrank.ai/). I acknowledge the FlyRank internship team for the anonymized starter data, dataset documentation, reference pipeline, and public-safety guidance. The analysis, interpretation, limitations, and recommendations on this page are presented as the author's internship capstone work.
