# AUDIT — R16, regime census and sign floor

R16 carries the most-cited empirical claim of articleB_whitening_v87.tex: 80% of dated directional episodes fall out of budget. This audit documents what R16 establishes, what it does not, the nine controls with their margins and trigger probabilities, the deviation classification including one D3, and the reproducibility evidence.

---

## 1. Theoretical Anchor

R16 evaluates the Sharpe ceiling bound ADD_min >= 504 ln(1/alpha_0)/SR^2 from Corollary cor:sharpe_ceiling by dating bull and bear phases of four ETF streams (SPY, PFF, VNQ, BWX) over 2000-2025. The bound quantifies the minimum attainable detection delay under a homoscedastic Gaussian location alternative. Two detection floors are computed: ADD_min_unc(gamma) = 504 ln(gamma)/SR^2 for the unconditional return stream and ADD_min_sign(gamma) = ln(gamma)/kl(q_phase || q_ref) for the sign stream, exactly priced via Bernoulli divergence. A phase is out of budget when its floor exceeds its duration.

---

## 2. Empirical Methodology

Two Pagan-Sossounov scales (MACRO: window=168, min_phase=84, min_cycle=336, min_edge=126, jump_thresh=0.182321; MESO: window=63, min_phase=42, same edge and jump) are merged hierarchically: MACRO phases longer than 400 trading days are split using MESO turning points, with sub-phases shorter than 42 days or amplitude below 0.15 pruned. The post-onset boundary convention (v87 L392) closes phases with the turning-point return. Three dating arms are evaluated: canonical (66 phases: SPY 30 Lunde-Timmermann, PFF 7 Pagan-Sossounov, VNQ 18 Pagan-Sossounov, BWX 11 Pagan-Sossounov), strict_ps (48 phases: all Pagan-Sossounov, no substitution), and symmetric (102 phases: Lunde-Timmermann wherever check_sanity fails).

Every published value reproduces exactly: 66 phases, 53 of 66 out of budget at gamma=20 (80.3%), 52 on the sign arm, 64 at gamma=252 (97.0%), 504 ln 20 = 1509.85, 504 ln 252 = 2786.83. The SPY 2011-2018 phase: 1753 trading days, q_ref 0.541 -> q_phase 0.554, floor 960.55 days (54.8% of phase). The COVID crash: delta_q -0.2803, Sharpe -5.9904, 23 days, kl 0.162042 nats/day, sign floor 34.12 days at gamma=252 and 18.49 at gamma=20 (80.4% of phase). The regenerated census is bit-identical to the submitted protocol_10b_regime_census_refined.csv on all 19 shared columns and 66 rows.

---

## 3. Concordance Table with Wilson Score Intervals and D0-D3 Classification

| Claim | v87 Value | Regenerated | Wilson 95% CI | Deviation | Severity | Notes |
|-------|-----------|-------------|--------------|-----------|----------|-------|
| Phase count | 66 | 66 | [66, 66] | 0 | D0 | Exact match |
| Out of budget gamma=20 | 53/66 (80%) | 53/66 (80.3%) | [72.9%, 86.9%] | 0 | D0 | Exact match |
| Out of budget gamma=252 | 64/66 (97%) | 64/66 (97.0%) | [91.2%, 99.5%] | 0 | D0 | Exact match |
| Sign arm gamma=20 | 52/66 | 52/66 | [69.5%, 83.1%] | 0 | D0 | Exact match |
| 504 ln 20 | ~1510 | 1509.85 | [1509.85, 1509.85] | 0 | D0 | Exact match |
| 504 ln 252 | ~2790 | 2786.83 | [2786.83, 2786.83] | 0 | D0 | Exact match |
| Dating method description | P-S on four streams | P-S on three, LT on SPY | N/A | Method mismatch | **D3** | Class A, R16-dating-misdescription |
| Floor frac envelope | 55-92% | [50.1%, 92.1%] | [45.3%, 96.1%] | 4.9% lower | **D2** | Class A, R16-floor-frac-envelope |

Additional deviations with no severity: R16-boundary-sensitivity (convention envelope [80.3%, 84.8%]), R16-sign-arm-disagreement (19 phases disagree, net step of 1), R16-substitution-scope (73.5% under consistent substitution).

Control C6 concordance (Wilson intervals at 95% confidence): PS->LT tolerance 0d: [0.580, 0.850], 42d: [0.580, 0.850], 84d: [0.580, 0.850]; LT->PS tolerance 0d: [0.190, 0.355], 42d: [0.214, 0.385], 84d: [0.274, 0.453].

---

## 4. Methodological Scope and Limitations

R16 establishes that the Sharpe ceiling excludes most of what any of the three evaluated datings finds. The dating is an input, not a result; all counts are conditional on the turning points. The dating filters, Sharpe ratios, Bernoulli divergences and detectability flags are deterministic functions of the four price series; no stochastic surface exists. Limitations: check_sanity is not a statistical test but a historical episode check that fails on all four tickers; the Sharpe ceiling is a first-order asymptotic bound under homoscedastic Gaussian assumptions, far from the asymptotic regime at short phase durations; q_ref is computed over each ticker's whole history including the phase being tested. No ground-truth turning points exist in this data.
