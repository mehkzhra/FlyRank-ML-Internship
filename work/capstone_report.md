# Which Content Pages Should Be Reviewed First? An Honest Refresh-Priority Study

**Author:** Mehak Zahra  
**Lane:** Refresh / Content Opportunity Scoring  
**Repository:** [mehkzhra/FlyRank-ML-Internship](https://github.com/mehkzhra/FlyRank-ML-Internship)  
**Analysis date:** 5 September 2026

## Abstract

This study asks which measurable content pages an editor should review first when review capacity is limited. I analyzed the 30,000-page anonymized starter slice associated with the FlyRank ML Internship dataset and defined an observed-decline proxy from the supplied 30-day comparison. I compared a transparent four-part rule score with logistic regression, a decision tree, and a random forest, using a client-group holdout so all six test clients were unseen during training. On the same 2,325-page test split, the selected random forest reached Precision@50 of 0.74 versus 0.24 for the rule baseline, while ROC AUC improved from 0.627 to 0.750. The result supports a human-reviewed triage queue; it does not show that refreshing a page causes recovery or that the model predicts future search performance.

## Introduction / problem statement

A content editor cannot inspect 30,000 pages at once. The decision is therefore not “will this page certainly improve?” but “which pages deserve scarce review time first?” One row represents one anonymized content page; the output is a ranked queue with reason codes, and the human action is to inspect the page before choosing refresh, expansion, CTR review, engagement review, or monitoring.

A false positive costs editor time. A false negative can leave a meaningful decline unreviewed. Precision@50 matches a practical batch of 50 reviews, while ROC AUC and average precision show whether performance extends beyond one cutoff.

## Data

The analysis uses `data/raw/content_refresh_anonymized.csv`, the bundled public-safe starter release: 30,000 rows and 44 fields at one-row-per-content-page grain. Its measures include trailing 90-day search and engagement aggregates and two adjacent 30-day comparison windows. The repository documentation connects this slice to `flyrank_pseudonymized_warehouse_release_v20260703`, exported 3 July 2026; the full warehouse contains 78,835,655 daily content-performance rows spanning 27 January 2025 through 30 June 2026. **This experiment did not query that full fact table and is not a 79-million-row benchmark.**

All 30,000 rows passed the reference preparation filters (`impressions_90d > 0`, `content_age_days >= 90`, unique content ID). The sample has 16,262 observed decline-proxy rows (54.21%). The held-out test split has 2,325 pages across six client groups, including 909 positives (39.10%).

No raw names, domains, URLs, titles, keywords, or queries are used or displayed. Pseudonymous content/client IDs are used only to preserve row identity and create the grouped split, never as model features. Direct label fields and components—`trend_direction`, `trend_pct`, `impressions_last_30d`, `impressions_prev_30d`, and their click/session counterparts—are excluded from the feature matrix.

## Methodology

### Label and assumptions

The binary proxy is `is_declining_label = 1` when supplied `trend_direction` is `down`: last-30-day impressions are more than 20% below the preceding 30 days. It describes an observed current-window decline, not a future outcome or the success of a refresh. The working assumption is only that current decline plus measurable opportunity is useful for prioritizing human review.

### Features

The pipeline builds 52 encoded columns from 18 numeric fields and eight categorical fields. Numeric inputs cover search-market attributes; content length; logged trailing-90-day impressions, clicks, sessions, and AI sessions; active-day counts; age and update recency; CTR; average position; and engagement/scroll/AI-traffic rates. Categorical inputs cover competition, content type, intent, age/freshness/length/impression/position tiers. Missing numeric values are filled with zero after type coercion; categorical blanks become `unknown`.

### Baseline and models

The baseline score is transparent: 40% visibility percentile + 30% freshness-risk percentile + 25% position opportunity + 5% depth gap. The candidates are logistic regression, a depth-limited decision tree, and a 200-tree random forest. All use fixed seed 42; the selected model maximizes Precision@50, then average precision and ROC AUC as tie-breakers.

### Validation and leakage checks

The split holds out 20% of the 32 client groups: 26 clients (27,675 rows) for training and six clients (2,325 rows) for testing, with no group overlap. Baseline and models are evaluated on exactly those test rows. IDs and direct label-derived columns are absent from the feature matrix.

One residual limitation remains: `impressions_90d`, `clicks_90d`, `sessions_90d`, active-day counts, and ratios summarize a 90-day interval that overlaps the two 30-day periods defining the proxy. This does not directly give the answer to the model, but it prevents a clean future-prediction interpretation. The analysis is therefore contemporaneous triage, not forecasting.

## Results

| Method | ROC AUC | Average precision | Precision@50 | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Rule baseline | 0.627 | 0.468 | 0.240 | 0.189 | 0.274 |
| Logistic regression | 0.700 | 0.522 | 0.400 | 0.567 | 0.566 |
| Decision tree | 0.742 | 0.575 | 0.660 | 0.716 | 0.634 |
| **Random forest** | **0.750** | **0.618** | **0.740** | **0.744** | **0.640** |

The random forest identifies 37 observed-decline pages among its first 50; the baseline identifies 12. That is a 50-percentage-point absolute gain and 3.08× the baseline precision at the chosen operating point. The result also exceeds both the 39.10% test-split positive rate and the 54.21% full-sample rate, but model selection and evaluation use the same holdout, so a second untouched confirmation set is still needed.

The most influential random-forest inputs are days with impressions (0.158), logged 90-day impressions (0.129), average position (0.109), and content age (0.095). These are model-specific impurity importances, not causal effects. The model is better at separating proxy-positive from proxy-negative pages overall (ROC AUC 0.750), but its thresholded precision is 0.561, so automated action would still generate many false positives.

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

