from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "work" / "notebooks" / "capstone.ipynb"

nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3"},
}

cells = [
    nbf.v4.new_markdown_cell("""# Capstone — Refresh / Content Opportunity Scoring

**Author:** Mehak Zahra  
**Question:** Which measurable content pages should an editor review first?  
**Scope:** Decision support on the 30,000-page anonymized starter slice; not a full-warehouse benchmark and not a causal claim."""),
    nbf.v4.new_code_cell("""from pathlib import Path
import json
import pandas as pd
from IPython.display import display

ROOT = next(p for p in [Path.cwd(), Path.cwd().parent, Path.cwd().parents[1]] if (p / 'scripts').exists())
DATA = ROOT / 'data' / 'raw' / 'content_refresh_anonymized.csv'
RESULTS = ROOT / 'outputs' / 'model_results.json'
assert DATA.exists() and RESULTS.exists(), 'Run python scripts/run_all.py first.'
df = pd.read_csv(DATA)
results = json.loads(RESULTS.read_text())
print(f'Repository root: {ROOT}')
print(f'Data shape: {df.shape[0]:,} rows × {df.shape[1]} columns')"""),
    nbf.v4.new_markdown_cell("""## 1. Question

The unit is one anonymized content page. The output is a score that ranks pages for human review. A content editor uses the queue to decide whether to refresh, expand, review CTR/engagement, or monitor. False positives waste review time; false negatives can leave meaningful decline unattended. Precision@50 matches a practical 50-page review batch."""),
    nbf.v4.new_code_cell("""question_frame = pd.Series({
    'unit': 'one anonymized content page',
    'output': 'ranked review queue with reason codes',
    'primary_metric': 'Precision@50',
    'human_action': 'review, then refresh / expand / inspect CTR or engagement / monitor',
})
display(question_frame.to_frame('definition'))"""),
    nbf.v4.new_markdown_cell("""## 2. Data

The study uses the bundled public-safe starter slice: 30,000 pages and 44 columns with trailing-90-day measures and two adjacent 30-day comparison windows. Repository documentation links it to warehouse release `flyrank_pseudonymized_warehouse_release_v20260703` (exported 2026-07-03; daily facts end 2026-06-30). The full warehouse has 78,835,655 daily content-performance rows, but **this analysis does not query that table**.

Excluded from features: pseudonymous IDs; `trend_direction` and `trend_pct`; and the last/previous 30-day impression, click, and session components. No names, domains, URLs, titles, keywords, or raw queries are present."""),
    nbf.v4.new_code_cell("""data_summary = pd.Series({
    'rows': len(df),
    'columns': df.shape[1],
    'unique_content_ids': df.content_id.nunique(),
    'client_groups': df.client_id.nunique(),
    'decline_proxy_rows': int(df.trend_direction.eq('down').sum()),
    'decline_proxy_rate': f\"{df.trend_direction.eq('down').mean():.2%}\",
})
display(data_summary.to_frame('value'))
assert len(df) == df.content_id.nunique()
assert not {'url', 'domain', 'title', 'query', 'client_name'} & set(df.columns)"""),
    nbf.v4.new_markdown_cell("""## 3. Methodology

The proxy is positive when `trend_direction == 'down'`, meaning last-30-day impressions are more than 20% below the previous 30 days. It is an observed current-window label, not a future or causal outcome.

The transparent baseline combines visibility (40%), update staleness (30%), position opportunity (25%), and content-depth gap (5%). Logistic regression, a constrained decision tree, and a 200-tree random forest use 18 numeric and eight categorical inputs (52 encoded columns). Seed 42 is fixed. Six of 32 client groups are held out entirely: 27,675 training pages and 2,325 test pages with no client overlap.

Direct label fields are excluded. However, trailing-90-day aggregate inputs overlap the component windows used by the contemporaneous proxy, so results support triage—not clean future prediction."""),
    nbf.v4.new_code_cell("""pred = pd.read_csv(ROOT / 'data' / 'processed' / 'model_predictions.csv')
train_clients = set(pred.loc[pred.split.eq('train'), 'client_id'])
test_clients = set(pred.loc[pred.split.eq('test'), 'client_id'])
test = pred[pred.split.eq('test')]
leakage_fields = {
    'trend_direction', 'trend_pct', 'impressions_last_30d', 'impressions_prev_30d',
    'clicks_last_30d', 'clicks_prev_30d', 'sessions_last_30d', 'sessions_prev_30d',
}
feature_fields = set(results['model_numeric_features'] + results['model_categorical_features'])
print('Training clients:', len(train_clients), '| Test clients:', len(test_clients))
print('Client overlap:', train_clients & test_clients)
print('Direct leakage fields in feature list:', leakage_fields & feature_fields)
print(f\"Test positive rate: {test.is_declining_label.mean():.2%} ({test.is_declining_label.sum():,}/{len(test):,})\")
assert train_clients.isdisjoint(test_clients)
assert leakage_fields.isdisjoint(feature_fields)"""),
    nbf.v4.new_markdown_cell("""## 4. Results (vs baseline)

All methods below use the same 2,325-page held-out-client test split. The random forest was selected by Precision@50. Its 0.74 means 37 of the top 50 pages carried the observed-decline proxy, compared with 12 of 50 for the baseline. The 3.08× lift is useful triage evidence, not proof that acting on those pages will cause recovery."""),
    nbf.v4.new_code_cell("""rows = []
for name, metrics in [('baseline_rules', results['baseline']), *results['models'].items()]:
    def metric(key):
        return metrics.get(key, metrics.get('baseline_' + key))
    rows.append({
        'method': name,
        'roc_auc': metric('roc_auc'),
        'average_precision': metric('average_precision'),
        'precision_at_50': metric('precision_at_50'),
        'recall': metric('recall'),
        'f1': metric('f1'),
    })
comparison = pd.DataFrame(rows).set_index('method').round(3)
display(comparison)
lift = comparison.loc['random_forest', 'precision_at_50'] / comparison.loc['baseline_rules', 'precision_at_50']
print(f'Precision@50 lift over baseline: {lift:.2f}×')"""),
    nbf.v4.new_markdown_cell("""## 5. Limitations

- The study uses the 30,000-page starter slice, not the complete 78.8M-row daily fact table.
- The label is a contemporaneous operational proxy, not future performance or refresh success.
- Trailing-90-day features overlap the proxy windows, preventing a clean forecast interpretation.
- Model selection and reporting use one grouped holdout; a second untouched confirmation set is needed.
- Zero-filled values may mix no activity with unavailable tracking in an unbalanced client panel.
- Impurity importance is not causal explanation, and no result predicts Google's algorithm.
- A prospective experiment is required to learn whether queue-guided actions improve outcomes."""),
    nbf.v4.new_code_cell("""importance = pd.DataFrame(results['best_model']['feature_importance_top']).head(10)
importance['importance'] = importance['importance'].round(3)
display(importance)"""),
    nbf.v4.new_markdown_cell("""## 6. Ranked recommendations

1. Review the top 50 high-confidence, high-exposure candidates first; confirm the decline and editorial context.
2. Route by reason code: inspect snippet/intent fit for low CTR, content coverage for thin pages, and experience/content fit for low engagement.
3. Keep human approval for publishing, pruning, redirects, and business-sensitive decisions.
4. Record reviewer decisions, actions, time cost, and later outcomes to build a better intervention label.
5. Before production, build non-overlapping historical feature and future target windows and reserve an untouched client-and-time confirmation set."""),
    nbf.v4.new_code_cell("""queue = pd.read_csv(ROOT / 'outputs' / 'refresh_queue.csv')
action_counts = queue['suggested_action'].value_counts().rename_axis('action').to_frame('pages')
display(action_counts)
display(queue[['final_rank', 'final_refresh_score', 'best_model_probability', 'suggested_action', 'confidence']].head(10))"""),
    nbf.v4.new_markdown_cell("""## 7. Artifacts the paper embeds

The deployed page embeds the exact comparison table, an accessible metric chart, the top feature-importance profile, and the action mix. Every chart has a text takeaway and tabular equivalent. Full paper: [GitHub Pages](https://mehkzhra.github.io/FlyRank-ML-Internship/). Repository: [GitHub](https://github.com/mehkzhra/FlyRank-ML-Internship).

## Self-check

- [x] Every section is filled with markdown reasoning and executable evidence
- [x] Model and baseline use the same held-out-client split
- [x] Direct leakage fields and pseudonymous IDs are excluded from features
- [x] Limitations distinguish contemporaneous triage from future prediction
- [x] No client names, URLs, or private queries are displayed
- [x] Claims use observed, measured, directional, and decision-support language"""),
]

nb["cells"] = cells
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUTPUT)
print(f"Wrote {OUTPUT}")
