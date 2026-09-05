# Audit Report: R02 — Ljung-Box Whiteness on Multi-ETF GARCH Streams

## 1. Deviation table (D0-D3)

NOT RECOVERABLE FROM THE LOG.

## 2. Controls

NOT RECOVERABLE FROM THE LOG.

## 3. Test suite

```
$ pytest tests/test_R02_claims.py -v
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.3.3, pluggy-1.6.0
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-1.0
collecting ... collected 8 items

tests/test_R02_claims.py::test_stream_counts PASSED                      [ 12%]
tests/test_R02_claims.py::test_classifier_integrity PASSED               [ 25%]
tests/test_R02_claims.py::test_data_rejection_rates PASSED               [ 37%]
tests/test_R02_claims.py::test_distinct_p_concept PASSED                 [ 50%]
tests/test_R02_claims.py::test_independence_diagnostics PASSED           [ 62%]
tests/test_R02_claims.py::test_iid_arm_rejection_is_reported_not_asserted PASSED [ 75%]
tests/test_R02_claims.py::test_concept_level_covered_by_wilson PASSED    [ 87%]
tests/test_R02_claims.py::test_max_clustered_pvalue_below_manuscript_bound PASSED [100%]

============================== 8 passed in 0.70s ===============================
```

Command: `pytest tests/test_R02_claims.py -v`

8 passed.

## 4. Reproducibility digests

SHA-256 digests from log lines 19-22 (single run, 1 worker):

```
4c9eb8b339d5f0a98168eb73362660ccff41a3bca05de576a2afce2956418204  results/R02_whitening_ljungbox/data/R02_ljungbox_360streams.csv
5ca6496f5099e65f835eed5c626873ea447ae831b8c1af54319cfaf67d7fdbb1  results/R02_whitening_ljungbox/data/R02_independence_diagnostics.csv
90734624b5343f7ffccd06645a72666b5ad3c7508b8170809589c1cc4a508c5b  results/R02_whitening_ljungbox/figures/fig01_ljungbox_whiteness.png
c1f1d58c57f5352883025cab6b1bceaabc6dec4d1c5b79d0a7ef5ec363c2dcb8  results/R02_whitening_ljungbox/tables/R02_claims.tex
```

current tree, single run:

```
$ sha256sum results/R02_whitening_ljungbox/data/*.csv results/R02_whitening_ljungbox/figures/*.png results/R02_whitening_ljungbox/tables/*.tex
4c9eb8b339d5f0a98168eb73362660ccff41a3bca05de576a2afce2956418204  results/R02_whitening_ljungbox/data/R02_ljungbox_360streams.csv
5ca6496f5099e65f835eed5c626873ea447ae831b8c1af54319cfaf67d7fdbb1  results/R02_whitening_ljungbox/data/R02_independence_diagnostics.csv
90734624b5343f7ffccd06645a72666b5ad3c7508b8170809589c1cc4a508c5b  results/R02_whitening_ljungbox/figures/fig01_ljungbox_whiteness.png
c1f1d58c57f5352883025cab6b1bceaabc6dec4d1c5b79d0a7ef5ec363c2dcb8  results/R02_whitening_ljungbox/tables/R02_claims.tex
```

## 5. Design decisions taken outside the plan

NOT RECOVERABLE FROM THE LOG.

## 6. Open questions, left open

NOT RECOVERABLE FROM THE LOG.

