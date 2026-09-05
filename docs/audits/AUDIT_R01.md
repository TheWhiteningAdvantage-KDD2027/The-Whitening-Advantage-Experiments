# Audit Report: R01 — Real World Backtest

## 1. Deviation table (D0-D3)

NOT RECOVERABLE FROM THE LOG.

## 2. Controls

NOT RECOVERABLE FROM THE LOG.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-0.3, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8
collected 5 items

tests/test_R01_claims.py::test_r01_models PASSED                         [ 20%]
tests/test_R01_claims.py::test_r01_trajectories PASSED                   [ 40%]
tests/test_R01_claims.py::test_r01_injection_summary PASSED              [ 60%]
tests/test_R01_claims.py::test_r01_placebo PASSED                        [ 80%]
tests/test_R01_claims.py::test_r01_magnitude_and_symmetry PASSED         [100%]

============================== 5 passed in 0.32s ===============================
```

5 passed in 0.32s.

## 4. Reproducibility digests

From `logs/R01_real_world_backtest/exp_R01_real_world_backtest.log` lines 29-41:

```
results/R01_real_world_backtest/
├── data/
│   ├── R01_garch_models.csv                [dfbef640404b3d13424e8a4825a38c04ac7db8ab6d100995b4784d3396c5d361]
│   ├── R01_covid_trajectories.csv          [733c0ff1700528a0c0f9ec2cd4860711be6264fa659da61dc05ae7c5069c71d6]
│   ├── R01_covid_alarms.csv                [c614e9952d968004b5bbc94c873657845c62d7279649b9a69dc43aae275aadd7]
│   ├── R01_symmetry_2020.csv               [edb0f663f9d3e3630c60d41832213819b4617141f2664065adbb445ca2db89c5]
│   ├── R01_injection_summary.csv           [e2205dd57d1c5c1e02f7ea13059c0c541a93f48fff91c5925c288998eb5b8c3b]
│   ├── R01_placebo_control.csv             [4b472fd3fe50da7612bce84a87d1e29154bb540609b88a7d5a471ecd83a1898d]
│   └── R01_magnitude_sweep.csv             [592e040468e55515217ce5a831f4289f220768adb5d4afe5e358c20b734667f3]
├── figures/
│   └── fig02_spy_in_the_wild.png           [9bc12be34b7f7bba919e7bb0c65bece4a2cfedc349aa616503393be8bf0e6254]
└── tables/
    └── R01_claims.tex                      [e61b39131ef894ce0eab9240754d27c3d47cfdaed4176142c5bf8f9e0c922619]
```

current tree, single run:
```
c614e9952d968004b5bbc94c873657845c62d7279649b9a69dc43aae275aadd7  results/R01_real_world_backtest/data/R01_covid_alarms.csv
733c0ff1700528a0c0f9ec2cd4860711be6264fa659da61dc05ae7c5069c71d6  results/R01_real_world_backtest/data/R01_covid_trajectories.csv
dfbef640404b3d13424e8a4825a38c04ac7db8ab6d100995b4784d3396c5d361  results/R01_real_world_backtest/data/R01_garch_models.csv
e2205dd57d1c5c1e02f7ea13059c0c541a93f48fff91c5925c288998eb5b8c3b  results/R01_real_world_backtest/data/R01_injection_summary.csv
592e040468e55515217ce5a831f4289f220768adb5d4afe5e358c20b734667f3  results/R01_real_world_backtest/data/R01_magnitude_sweep.csv
4b472fd3fe50da7612bce84a87d1e29154bb540609b88a7d5a471ecd83a1898d  results/R01_real_world_backtest/data/R01_placebo_control.csv
edb0f663f9d3e3630c60d41832213819b4617141f2664065adbb445ca2db89c5  results/R01_real_world_backtest/data/R01_symmetry_2020.csv
e61b39131ef894ce0eab9240754d27c3d47cfdaed4176142c5bf8f9e0c922619  results/R01_real_world_backtest/tables/R01_claims.tex
```

Command: `sha256sum results/R01_real_world_backtest/data/*.csv results/R01_real_world_backtest/tables/*.tex`

## 5. Design decisions taken outside the plan

NOT RECOVERABLE FROM THE LOG.

## 6. Open questions, left open

NOT RECOVERABLE FROM THE LOG.
