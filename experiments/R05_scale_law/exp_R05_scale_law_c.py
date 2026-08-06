#!/usr/bin/env python3
"""
==========================================================================
R05c -- FIGURE 5, THE APPENDIX B NUMBERS, AND THE LATEX MACROS
==========================================================================
Consumes the frames of steps a and b IN MEMORY and emits:
  - results/R05_scale_law/figures/fig05_scale_law_orthogonality.png
  - results/R05_scale_law/tables/R05_claims.tex
  - the regenerated Appendix B numbers, logged and classified D0/D1/D2

By default this script IS the chain: it drives step a, then step b at both
budgets, on one executor and in one process, and reads their returned frames
directly. The submitted pipeline instead wrote CSVs in one script and reloaded
them in the next, which SPECS 1.6 forbids -- a CSV is a final medium of
diffusion, never a bridge between two stages of one computation, because the
round trip silently truncates. Each stage still writes its own CSV deliverable;
nothing reads them back.

`--from-csv` reloads the CSVs instead, for a reviewer who wants to rebuild the
figure without re-running the campaigns. That path is a documented degraded
mode: it is announced in the log, it is never used by run_experiment_R05.sh,
and its outputs are stamped.

THE CROSSOVER RULE USED HERE. The ramp branch is w >= w_delta_applied, the
crossover at the threshold the detector actually ran with. The alternative,
w >= w_star_predicted, is emitted by step b in its own columns and gives
exponents roughly 0.02-0.03 lower. Appendix B of v87 prints the applied-threshold
figures, and the model curves of Figure 5B are drawn with the applied threshold,
so that is the rule this script uses throughout. Both are reported.
==========================================================================
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import numpy as np
import pandas as pd
from experiments.common.fair_harness import setup_logging, disable_pandas_multithreading, save_fair_csv

disable_pandas_multithreading()

import os
import math
import time
import argparse
from concurrent.futures import ProcessPoolExecutor

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import gamma as gamma_function

from experiments.R05_scale_law import exp_R05_scale_law_a as step_a
from experiments.R05_scale_law import exp_R05_scale_law_b as step_b

# Palette of the submitted figure, preserved so the regenerated panel B carries
# the same colour-to-penalty mapping a reader of v87 already has.
COLOUR_DATA = "#04617b"
COLOUR_FIT = "#2E7D32"
COLOUR_GREY = "#546E7A"
COLOUR_BY_GAMMA = {2.0: "#e53935", 4.0: "#fb8c00", 8.0: "#43a047",
                   11.58: "#04617b", 20.0: "#5e35b1"}

# --- PUBLISHED VALUES OF v87, FOR CLASSIFICATION ONLY ---
# Every literal below is printed in the manuscript. None is a gate: the
# regenerated campaign is drawn from corrected 128-bit seeding and is expected
# to move. They populate the "published" column of a D0/D1/D2 table.
#   name -> (published value, decimals of the printed precision)
PUBLISHED = {
    "abrupt_slope": (23.7, 1),
    "abrupt_intercept": (38.0, 0),
    "sqrt_rule_fpr_pct": (31.0, 0),
    "scaling_median_error_pct": (5.4, 1),
    "recalib_margin_min_pct_2e5": (7.0, 0),
    "recalib_margin_max_pct_2e5": (29.0, 0),
    "lambda_iid_2e5": (129.5, 1),
    "grid_reach_wstar_2e5": (22.5, 1),
    "censoring_max_pct_2e5": (1.3, 1),
    "detection_min_pct_2e5": (98.7, 1),
    "lambda_over_gamma_min_2e5": (138.0, 0),
    "lambda_over_gamma_max_2e5": (167.0, 0),
    "sd_over_add_max_2e5": (3.2, 1),
    "med_over_add_min_2e5": (0.68, 2),
    "rho_w_share_pct_2e5": (58.0, 0),
    "exponent_min_2e5": (0.65, 2),
    "exponent_max_2e5": (0.71, 2),
    "model_exponent_min_2e5": (0.71, 2),
    "model_exponent_max_2e5": (0.73, 2),
    "lambda_iid_3e6": (303.0, 1),
    "grid_reach_wstar_3e6": (225.0, 1),
    "low_gamma_max_error_pct_3e6": (5.7, 1),
    "rho_w_share_pct_3e6": (78.0, 0),
    "recalib_margin_max_pct_3e6": (96.0, 0),
    "sixth_moment_gamma": (7.1, 1),
    "moment_margin_at_gamma_max": (0.8, 1),
    "lambda_iid_ladder_77k": (102.8, 1),
}


def classify_deviation(published, regenerated, decimals):
    """
    Classifies one regenerated value against its witness at the printing
    precision of the manuscript. D3 is never returned here: falsification of a
    qualitative claim is decided by the blocking gates of steps a and b, not by
    a rounding comparison.
    """
    if published == regenerated:
        return "D0"
    if round(float(published), decimals) == round(float(regenerated), decimals):
        return "D1"
    return "D2"


def standardised_t_even_moment(order, nu):
    """
    E[z^order] for a Student-t scaled to unit variance, order even and < nu.

    Closed form, so the integer-order moment conditions below carry no
    quadrature error at all.
    """
    if order >= nu:
        return float('inf')
    scale = ((nu - 2.0) / nu) ** (order / 2.0)
    return scale * (nu ** (order / 2.0)) * gamma_function((order + 1) / 2.0) \
        * gamma_function((nu - order) / 2.0) / (math.sqrt(math.pi) * gamma_function(nu / 2.0))


def garch_moment_functional(beta, order, alpha, nu):
    """
    E[(alpha z^2 + beta)^(order/2)], the functional whose value at 1 marks the
    boundary of E|eps_t|^order < infinity for a stationary GARCH(1,1)
    (Bollerslev 1986; Francq & Zakoian 2010, Theorem 2.9).

    Even integer orders are expanded exactly by the binomial theorem. Only the
    non-integer orders needed for the moment MARGIN fall back on quadrature, and
    the quadrature is validated against the exact expansion at order 6 before
    being trusted anywhere.
    """
    half = order / 2.0
    if float(half).is_integer():
        k = int(half)
        total = 0.0
        for j in range(k + 1):
            coefficient = math.comb(k, j)
            total += coefficient * (alpha ** j) * (beta ** (k - j)) * standardised_t_even_moment(2 * j, nu)
        return total

    scale = math.sqrt((nu - 2.0) / nu)
    normaliser = gamma_function((nu + 1) / 2.0) / (math.sqrt(nu * math.pi) * gamma_function(nu / 2.0))

    def integrand(x):
        return ((alpha * (scale * x) ** 2 + beta) ** half) * normaliser * (1.0 + x * x / nu) ** (-(nu + 1) / 2.0)

    value, _ = quad(integrand, -np.inf, np.inf, limit=800, epsabs=1e-12, epsrel=1e-12)
    return value


def moment_boundary(order, alpha, nu):
    """Returns (beta, Gamma) at which E|eps_t|^order ceases to be finite."""
    beta = brentq(lambda b: garch_moment_functional(b, order, alpha, nu) - 1.0,
                  1e-9, 1.0 - alpha - 1e-9, xtol=1e-12, rtol=8.9e-16)
    return beta, step_a.gamma_closed(alpha, beta)


def moment_margin(gamma_target, alpha, nu):
    """
    Largest delta such that E|eps_t|^(4+delta) < infinity at this penalty.

    Bounded above by the innovation tail: a standardized t_nu has no moment of
    order nu or beyond whatever the GARCH parameters are.
    """
    beta = step_a.solve_beta(gamma_target, alpha)
    ceiling = nu - 1e-6
    if garch_moment_functional(beta, ceiling, alpha, nu) < 1.0:
        return ceiling - 4.0, beta
    order = brentq(lambda p: garch_moment_functional(beta, p, alpha, nu) - 1.0,
                   4.0 - 1e-6, ceiling, xtol=1e-10)
    return order - 4.0, beta


def scaling_law_predictions(frame):
    """
    Attaches Eq. (5) of v87 to a ramp frame, evaluated at the threshold actually
    applied and with kappa set to zero -- "no fitted constant" in the strict
    sense: nothing in the prediction is estimated from the delays it predicts.
    """
    out = frame.copy()
    dmu = float(out.dmu_std_target.iloc[0])
    delta_p = float(out.delta_P.iloc[0])
    rho = delta_p / dmu
    lam = out.lambda_star_Data
    w = out.w

    crossover = out.w_delta_applied
    out["pred_full"] = np.where(
        w >= crossover,
        np.sqrt(2.0 * lam * w / dmu) + rho * w,
        lam / (dmu - delta_p) + (1.0 + rho) * w / 2.0)
    # The same law stripped of the dead-band term, which is how the
    # deterministic limit is usually stated. Its failure is the point.
    out["pred_no_dead_band"] = np.where(
        w >= 2.0 * lam / dmu,
        np.sqrt(2.0 * lam * w / dmu),
        lam / dmu + w / 2.0)
    out["ratio_full"] = out.ADD_Data / out.pred_full
    out["ratio_no_dead_band"] = out.ADD_Data / out.pred_no_dead_band
    out["sd_Data"] = out.SEM_Data * np.sqrt(out.n_drift * out.DetRate_Data)
    return out, rho


def appendix_b_numbers(frame, logger, budget):
    """
    Regenerates every quantity v87 app:scaling prints for one budget, and logs
    it. Returns a flat dict for the classification table and the macros.
    """
    enriched, rho = scaling_law_predictions(frame)
    lam_iid = float(enriched.lambda_iid_H.iloc[0])
    grouped = enriched.groupby("Gamma")

    saturated = enriched[enriched.w < enriched.w_delta_applied]
    near = enriched[(enriched.w >= enriched.w_delta_applied)
                    & (enriched.w < 2.0 * enriched.w_delta_applied)]
    far = enriched[enriched.w > 10.0 * enriched.w_delta_applied]

    numbers = {}
    numbers["lambda_iid"] = lam_iid
    numbers["horizon"] = int(enriched.mon_len.iloc[0])
    numbers["grid_reach_wstar"] = float(enriched.w_over_wstar_predicted.max())
    numbers["censoring_max_pct"] = 100.0 * float(enriched.censored_Data.max())
    numbers["detection_min_pct"] = 100.0 * float(enriched.DetRate_Data.min())
    numbers["fpr_min"] = float(grouped.FPR_Data_val.first().min())
    numbers["fpr_max"] = float(grouped.FPR_Data_val.first().max())

    ratio_by_gamma = grouped.lambda_star_Data.first() / grouped.lambda_star_Data.first().index
    numbers["lambda_over_gamma_min"] = float(ratio_by_gamma.min())
    numbers["lambda_over_gamma_max"] = float(ratio_by_gamma.max())
    margins = 100.0 * (ratio_by_gamma / lam_iid - 1.0)
    numbers["recalib_margin_min_pct"] = float(margins.min())
    numbers["recalib_margin_max_pct"] = float(margins.max())
    numbers["recalib_margins_by_gamma"] = [float(v) for v in margins]

    numbers["median_error_pct"] = 100.0 * float(np.median(abs(enriched.ratio_full - 1.0)))
    numbers["max_error_pct"] = 100.0 * float(abs(enriched.ratio_full - 1.0).max())
    numbers["no_dead_band_excess_min_pct"] = 100.0 * float(enriched.ratio_no_dead_band.min() - 1.0)
    numbers["no_dead_band_excess_max_pct"] = 100.0 * float(enriched.ratio_no_dead_band.max() - 1.0)

    low_gamma = enriched[enriched.Gamma <= 4.0 + 1e-9]
    numbers["low_gamma_median_error_pct"] = 100.0 * float(np.median(abs(low_gamma.ratio_full - 1.0)))
    numbers["low_gamma_max_error_pct"] = 100.0 * float(abs(low_gamma.ratio_full - 1.0).max())

    numbers["kappa_by_gamma"] = [float((sub.ADD_Data - sub.pred_full).mean())
                                 for _, sub in saturated.groupby("Gamma")]
    numbers["near_agreement_pct"] = 100.0 * float(abs(near.ratio_full - 1.0).max()) if len(near) else float('nan')
    numbers["far_below_min_pct"] = 100.0 * float(1.0 - far.ratio_full.max()) if len(far) else float('nan')
    numbers["far_below_max_pct"] = 100.0 * float(1.0 - far.ratio_full.min()) if len(far) else float('nan')

    sd_ratio = enriched.sd_Data / enriched.ADD_Data
    numbers["sd_over_add_max"] = float(sd_ratio.max())
    numbers["sd_over_add_max_gamma"] = float(enriched.loc[sd_ratio.idxmax(), "Gamma"])
    numbers["med_over_add_min"] = float((enriched.MED_Data / enriched.ADD_Data).min())
    med_ratio = enriched.MED_Data / enriched.pred_full
    numbers["med_below_min_pct"] = 100.0 * float(1.0 - med_ratio.max())
    numbers["med_below_max_pct"] = 100.0 * float(1.0 - med_ratio.min())

    exponents, model_exponents, exponents_predicted_rule = [], [], []
    for gamma_value, sub in grouped:
        ramp = sub[(sub.w >= sub.w_delta_applied) & sub.ADD_Data.notna()]
        ramp_alt = sub[(sub.w >= sub.w_star_predicted) & sub.ADD_Data.notna()]
        if len(ramp) >= 3:
            exponents.append(float(np.polyfit(np.log(ramp.w), np.log(ramp.ADD_Data), 1)[0]))
            model_exponents.append(float(np.polyfit(np.log(ramp.w), np.log(ramp.pred_full), 1)[0]))
        if len(ramp_alt) >= 3:
            exponents_predicted_rule.append(
                float(np.polyfit(np.log(ramp_alt.w), np.log(ramp_alt.ADD_Data), 1)[0]))
    numbers["exponent_min"] = min(exponents) if exponents else float('nan')
    numbers["exponent_max"] = max(exponents) if exponents else float('nan')
    numbers["model_exponent_min"] = min(model_exponents) if model_exponents else float('nan')
    numbers["model_exponent_max"] = max(model_exponents) if model_exponents else float('nan')
    numbers["exponent_min_predicted_rule"] = min(exponents_predicted_rule) if exponents_predicted_rule else float('nan')
    numbers["exponent_max_predicted_rule"] = max(exponents_predicted_rule) if exponents_predicted_rule else float('nan')
    numbers["low_gamma_exponents"] = [
        float(np.polyfit(np.log(sub[sub.w >= sub.w_delta_applied].w),
                         np.log(sub[sub.w >= sub.w_delta_applied].ADD_Data), 1)[0])
        for _, sub in low_gamma.groupby("Gamma")]

    widest = enriched.loc[enriched.w.idxmax()]
    numbers["rho_w_share_pct"] = 100.0 * rho * float(widest.w) / float(widest.pred_full)
    numbers["dead_band_turning_point_wstar"] = (1.0 - rho) ** 2 / rho ** 2

    logger.info(f"--- Appendix B, budget {budget} ---")
    logger.info(f"[appB] H = {numbers['horizon']}, lambda_iid_H = {lam_iid:.2f}, rho = {rho:.3f}, "
                f"grid reach {numbers['grid_reach_wstar']:.1f} w* "
                f"({numbers['grid_reach_wstar']/numbers['dead_band_turning_point_wstar']:.1f}x the "
                f"dead-band turning point of {numbers['dead_band_turning_point_wstar']:.0f} w*)")
    logger.info(f"[appB] censoring max {numbers['censoring_max_pct']:.2f}%, detection min "
                f"{numbers['detection_min_pct']:.2f}%, hold-out FPR "
                f"{numbers['fpr_min']:.3f} to {numbers['fpr_max']:.3f}")
    logger.info(f"[appB] lambda*/Gamma = {[round(v, 1) for v in ratio_by_gamma]} against "
                f"lambda_iid = {lam_iid:.1f}; departure from the rule "
                f"{numbers['recalib_margin_min_pct']:+.1f}% to {numbers['recalib_margin_max_pct']:+.1f}%")
    logger.info(f"[appB] Eq. (5) with kappa = 0: median error {numbers['median_error_pct']:.1f}%, "
                f"max {numbers['max_error_pct']:.1f}%; Gamma <= 4 median "
                f"{numbers['low_gamma_median_error_pct']:.1f}%, max {numbers['low_gamma_max_error_pct']:.1f}%")
    logger.info(f"[appB] dropping the rho*w term: measurement exceeds prediction by "
                f"{numbers['no_dead_band_excess_min_pct']:.0f}% to {numbers['no_dead_band_excess_max_pct']:.0f}%")
    logger.info(f"[appB] kappa on the saturated branch = "
                f"{[round(v) for v in numbers['kappa_by_gamma']]} steps at increasing Gamma")
    logger.info(f"[appB] near the crossover the two agree to {numbers['near_agreement_pct']:.0f}%; "
                f"on the far ramp the measurement falls {numbers['far_below_min_pct']:.0f}% to "
                f"{numbers['far_below_max_pct']:.0f}% below")
    logger.info(f"[appB] SD/ADD max {numbers['sd_over_add_max']:.2f} at Gamma = "
                f"{numbers['sd_over_add_max_gamma']:.0f}; MED/ADD min {numbers['med_over_add_min']:.2f}; "
                f"median sits {numbers['med_below_min_pct']:.0f}% to {numbers['med_below_max_pct']:.0f}% "
                f"below the prediction")
    logger.info(f"[appB] ramp exponents {numbers['exponent_min']:.2f}-{numbers['exponent_max']:.2f} "
                f"measured against {numbers['model_exponent_min']:.2f}-{numbers['model_exponent_max']:.2f} "
                f"predicted by Eq. (5) over the same range")
    logger.info(f"[appB] on the alternative rule w >= w*_predicted the measured exponents would be "
                f"{numbers['exponent_min_predicted_rule']:.2f}-{numbers['exponent_max_predicted_rule']:.2f}. "
                f"Both rules are in the CSV; v87 prints the applied-threshold figures above.")
    logger.info(f"[appB] rho*w carries {numbers['rho_w_share_pct']:.0f}% of the prediction at the "
                f"widest ramp")
    return numbers, enriched


def moment_boundary_report(logger):
    """
    The analytic side of control (e). Nothing here is measured: these are
    closed-form moment conditions on (alpha, beta, nu).
    """
    alpha, nu = step_a.ALPHA_GARCH, step_a.NU

    # Validate the quadrature branch against the exact binomial expansion before
    # any non-integer order is trusted. The two compute the same integral by
    # different routes, so agreement is a check of the numerics, not a tolerance
    # tuned on an observed gap.
    probe_beta = 0.85
    exact = garch_moment_functional(probe_beta, 6, alpha, nu)
    scale = math.sqrt((nu - 2.0) / nu)
    normaliser = gamma_function((nu + 1) / 2.0) / (math.sqrt(nu * math.pi) * gamma_function(nu / 2.0))
    numeric, _ = quad(lambda x: ((alpha * (scale * x) ** 2 + probe_beta) ** 3.0) * normaliser
                      * (1.0 + x * x / nu) ** (-(nu + 1) / 2.0),
                      -np.inf, np.inf, limit=800, epsabs=1e-12, epsrel=1e-12)
    if not math.isclose(exact, numeric, rel_tol=1e-9):
        raise AssertionError(
            f"Quadrature disagrees with the exact binomial expansion of E[(alpha z^2 + beta)^3]: "
            f"{numeric!r} vs {exact!r}. The non-integer moment margins cannot be trusted.")

    beta_six, gamma_six = moment_boundary(6, alpha, nu)
    beta_four, gamma_four = moment_boundary(4, alpha, nu)
    margin_max, _ = moment_margin(max(step_b.GAMMA_LIST), alpha, nu)

    logger.info("--- control (e): the moment boundary ---")
    logger.info(
        f"[control e] closed form at alpha = {alpha}, standardized t_{nu:g}: E[eps^6] is finite up "
        f"to beta = {beta_six:.6f}, i.e. Gamma = {gamma_six:.4f}. E[eps^4] survives much further, "
        f"to beta = {beta_four:.6f}, Gamma = {gamma_four:.4f}.")
    logger.info(
        f"[control e] largest finite moment order at Gamma = {max(step_b.GAMMA_LIST):.0f} is "
        f"4 + {margin_max:.4f}.")
    logger.info(
        "[control e] THIS EXPERIMENT SWEEPS NO nu. Every campaign runs standardized t_7, so no "
        "output of R05 can attribute the degradation of the recalibration rule to the loss of a "
        "moment: what R05 measures is that the departure from lambda_iid x Gamma grows with Gamma "
        "and with the horizon, and what the closed form above supplies is a boundary that happens "
        "to fall inside the same range of Gamma. The coincidence is an association. Establishing "
        "the mechanism would need an arm varying nu at fixed Gamma, and this experiment has none.")
    logger.info(
        "[control e] v87 app:scaling glosses E[eps^6] as 'the second moment of the monitored "
        "statistic eps^2'. E[eps^6] is the THIRD moment of eps^2; the second is E[eps^4], whose "
        f"boundary sits at Gamma = {gamma_four:.1f}, far outside the grid. The numeral 7.1 is "
        "reproduced; the description attached to it is not.")
    return dict(sixth_moment_gamma=gamma_six, sixth_moment_beta=beta_six,
                fourth_moment_gamma=gamma_four, fourth_moment_beta=beta_four,
                moment_margin_at_gamma_max=margin_max)


def plot_figure(abrupt, ramp_2e5, path, logger):
    """
    Figure 5: abrupt panel (A) and gradual panel (B).

    v87 sec:scaling_validation cites Figure~\\ref{fig:scale_law}B for the ramp
    result, so panel B must remain the gradual one; the assertion below states
    it rather than leaving it to the reading order of the code.

    Panel titles are bold and left-aligned per preamble S6, which the submitted
    figure did not do. That is a presentation deviation, Class C of
    docs/DEVIATIONS.md, and moves no number.
    """
    enriched, rho = scaling_law_predictions(ramp_2e5)
    dmu = float(enriched.dmu_std_target.iloc[0])
    delta_p = float(enriched.delta_P.iloc[0])

    plt.rcParams.update({
        "figure.dpi": 300, "font.family": "sans-serif", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.facecolor": "white", "figure.facecolor": "white",
        "mathtext.fontset": "stix",
    })
    figure, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(13.6, 5.0))

    # --- Panel A: abrupt scale shift ---
    ax_a.errorbar(abrupt.Gamma, abrupt.ADD_Data, yerr=abrupt.SEM_Data, fmt="o-",
                  color=COLOUR_DATA, ms=5, lw=1.8, capsize=2.5,
                  label=fr"Data ($\varepsilon^2$), DetRate $\geq$ {100*abrupt.DetRate_Data.min():.0f}%",
                  zorder=3)
    slope, intercept = np.polyfit(abrupt.Gamma, abrupt.ADD_Data, 1)
    grid = np.linspace(abrupt.Gamma.min(), abrupt.Gamma.max(), 50)
    ax_a.plot(grid, slope * grid + intercept, "--", color=COLOUR_FIT, lw=1.6,
              label=fr"fit $\approx {slope:.1f}\,\Gamma + {intercept:.0f}$", zorder=2)
    ax_a.annotate("Concept (sign): blind to scale\n"
                  fr"DetRate $\approx$ {abrupt.DetRate_Concept.mean():.2f} $=$ FPR",
                  xy=(0.04, 0.84), xycoords="axes fraction", fontsize=9.5, color=COLOUR_GREY,
                  bbox=dict(boxstyle="round,pad=0.3", fc="#f2f2f2", ec=COLOUR_GREY, lw=0.8))
    ax_a.set_xlabel(r"GARCH penalty $\Gamma$")
    ax_a.set_ylabel("ADD (steps post-onset)")
    ax_a.set_title(r"(A) Abrupt scale drift: $\mathrm{ADD}\propto\Gamma$",
                   fontweight="bold", loc="left")
    ax_a.legend(frameon=False, fontsize=9.5, loc="lower right")
    ax_a.grid(alpha=0.25)

    # --- Panel B: gradual ramps ---
    for gamma_key in sorted(COLOUR_BY_GAMMA):
        sub = enriched[np.isclose(enriched.Gamma, gamma_key, atol=0.2)].sort_values("w")
        if sub.empty:
            continue
        colour = COLOUR_BY_GAMMA[gamma_key]
        ax_b.errorbar(sub.w, sub.ADD_Data, yerr=sub.SEM_Data, fmt="o", color=colour,
                      ms=4.5, lw=0, capsize=2, label=fr"$\Gamma={gamma_key:g}$", zorder=3)
        ax_b.plot(sub.w, sub.MED_Data, "x", color=colour, ms=4.5, mew=1.1, alpha=0.55, zorder=3)

        lam = float(sub.lambda_star_Data.iloc[0])
        crossover_applied = float(sub.w_delta_applied.iloc[0])
        crossover_predicted = float(sub.w_star_predicted.iloc[0])
        curve_w = np.logspace(np.log10(sub.w.min()), np.log10(sub.w.max()), 300)
        curve = np.where(curve_w >= crossover_applied,
                         np.sqrt(2.0 * lam * curve_w / dmu) + rho * curve_w,
                         lam / (dmu - delta_p) + (1.0 + rho) * curve_w / 2.0)
        ax_b.plot(curve_w, curve, "-", color=colour, lw=1.4, alpha=0.85, zorder=2)
        # The dotted vertical is the PREDICTED crossover, the only quantity
        # exactly proportional to Gamma, which is what the caption claims.
        ax_b.axvline(crossover_predicted, color=colour, ls=":", lw=1.0, alpha=0.6, zorder=1)

        ramp = sub[sub.w >= crossover_applied]
        if len(ramp) >= 2:
            exponent = float(np.polyfit(np.log(ramp.w), np.log(ramp.ADD_Data), 1)[0])
            ax_b.annotate(fr"$w^{{{exponent:.2f}}}$",
                          xy=(ramp.w.iloc[-1], ramp.ADD_Data.iloc[-1]),
                          xytext=(6, -2), textcoords="offset points",
                          fontsize=8.5, color=colour)
    ax_b.set_xscale("log")
    ax_b.set_yscale("log")
    ax_b.annotate(r"$\bullet$ mean   $\times$ median   |   lines: Eq. (5), no fitted constant"
                  "\n" r"dotted: predicted crossover $w^{*}(\Gamma)\propto\Gamma$",
                  xy=(0.03, 0.88), xycoords="axes fraction", fontsize=9, color=COLOUR_GREY,
                  bbox=dict(boxstyle="round,pad=0.3", fc="#f2f2f2", ec=COLOUR_GREY, lw=0.8))
    ax_b.annotate(r"Concept: blind at all $\Gamma$ (DetRate $=$ FPR)",
                  xy=(0.03, 0.03), xycoords="axes fraction", fontsize=9, color=COLOUR_GREY)
    ax_b.set_xlabel(r"drift width $w$ (steps)")
    ax_b.set_ylabel("ADD (steps post-onset)")
    ax_b.set_title(r"(B) Gradual scale drift: $\mathrm{ADD}\sim w^{1/2}$",
                   fontweight="bold", loc="left")
    ax_b.legend(frameon=False, fontsize=9.5, loc="lower right", title=r"Data ($\varepsilon^2$)")
    ax_b.grid(alpha=0.25, which="both")

    # get_title() defaults to the centre location, which is empty once the
    # titles are set with loc="left"; the panel letter lives in the left title.
    if "Gradual" not in ax_b.get_title(loc="left"):
        raise AssertionError(
            "Panel (B) is not the gradual-ramp panel. v87 sec:scaling_validation cites "
            "Figure fig:scale_law B for the ramp result, so swapping the panels would "
            "desynchronise the manuscript from the figure.")

    figure.tight_layout()
    figure.savefig(path, bbox_inches="tight")
    plt.close(figure)
    logger.info(f"Wrote {path.relative_to(BASE_DIR)} (panel A abrupt, panel B gradual)")


def emit_macros(path, abrupt, positive, fit, numbers_2e5, numbers_3e6, moments, ladder):
    """Writes R05_claims.tex. Every value is computed; none is a literal of v87."""
    lines = [
        "% Auto-generated by exp_R05_scale_law_c.py -- do not edit.",
        f"\\newcommand{{\\RFiveSeedsPerConfig}}{{{int(abrupt.n_drift.iloc[0])}}}",
        f"\\newcommand{{\\RFiveAlphaGarch}}{{{step_a.ALPHA_GARCH}}}",
        f"\\newcommand{{\\RFiveNu}}{{{step_a.NU:.0f}}}",
        f"\\newcommand{{\\RFiveDeltaMuMax}}{{{step_a.DMU_TARGET:.0f}}}",
        f"\\newcommand{{\\RFiveDeltaP}}{{{step_a.DELTA_P}}}",
        f"\\newcommand{{\\RFiveDeltaC}}{{{step_a.DELTA_C}}}",
        f"\\newcommand{{\\RFiveTargetFpr}}{{{step_a.TARGET_FPR*100:.0f}\\%}}",
        f"\\newcommand{{\\RFiveGammaRampMin}}{{{min(step_b.GAMMA_LIST):.0f}}}",
        f"\\newcommand{{\\RFiveGammaRampMax}}{{{max(step_b.GAMMA_LIST):.0f}}}",
        f"\\newcommand{{\\RFiveAbruptSlope}}{{{fit['slope']:.1f}}}",
        f"\\newcommand{{\\RFiveAbruptIntercept}}{{{fit['intercept']:.0f}}}",
        f"\\newcommand{{\\RFiveAbruptRSquared}}{{{fit['r_squared']:.4f}}}",
        f"\\newcommand{{\\RFiveAbruptMaxRelResidual}}{{{100*fit['max_rel_residual']:.0f}\\%}}",
        f"\\newcommand{{\\RFiveAbruptSlopeExGammaOne}}{{{fit['slope_ex_iid']:.1f}}}",
        f"\\newcommand{{\\RFiveAbruptInterceptExGammaOne}}{{{fit['intercept_ex_iid']:.0f}}}",
        f"\\newcommand{{\\RFiveSqrtRuleFpr}}{{{100*abrupt.FPR_rule_xSqrtGamma.max():.0f}\\%}}",
        f"\\newcommand{{\\RFiveScalingMedianError}}{{{numbers_2e5['median_error_pct']:.1f}\\%}}",
        f"\\newcommand{{\\RFiveRecalibMarginMinTwoEFive}}{{{numbers_2e5['recalib_margin_min_pct']:.0f}\\%}}",
        f"\\newcommand{{\\RFiveRecalibMarginMaxTwoEFive}}{{{numbers_2e5['recalib_margin_max_pct']:.0f}\\%}}",
        f"\\newcommand{{\\RFiveRecalibMarginMinThreeESix}}{{{numbers_3e6['recalib_margin_min_pct']:.0f}\\%}}",
        f"\\newcommand{{\\RFiveRecalibMarginMaxThreeESix}}{{{numbers_3e6['recalib_margin_max_pct']:.0f}\\%}}",
        f"\\newcommand{{\\RFiveConceptDetRate}}{{{abrupt.DetRate_Concept.iloc[0]:.4f}}}",
        f"\\newcommand{{\\RFiveConceptFpr}}{{{abrupt.FPR_Concept_val.iloc[0]:.4f}}}",
        f"\\newcommand{{\\RFiveConceptPositiveDetRate}}{{{positive.DetRate_Concept.iloc[0]:.4f}}}",
        f"\\newcommand{{\\RFiveConceptPositiveShift}}{{{positive.c.iloc[0]:.2f}}}",
        f"\\newcommand{{\\RFiveLambdaCAbrupt}}{{{abrupt.lambda_star_Concept.iloc[0]:.2f}}}",
        f"\\newcommand{{\\RFiveLambdaCRampTwoEFive}}{{{numbers_2e5['lambda_c']:.2f}}}",
        f"\\newcommand{{\\RFiveLambdaCRampThreeESix}}{{{numbers_3e6['lambda_c']:.2f}}}",
        f"\\newcommand{{\\RFiveLambdaIidTwoEFive}}{{{numbers_2e5['lambda_iid']:.1f}}}",
        f"\\newcommand{{\\RFiveLambdaIidThreeESix}}{{{numbers_3e6['lambda_iid']:.1f}}}",
        f"\\newcommand{{\\RFiveGridReachTwoEFive}}{{{numbers_2e5['grid_reach_wstar']:.1f}}}",
        f"\\newcommand{{\\RFiveGridReachThreeESix}}{{{numbers_3e6['grid_reach_wstar']:.1f}}}",
        f"\\newcommand{{\\RFiveExponentMinTwoEFive}}{{{numbers_2e5['exponent_min']:.2f}}}",
        f"\\newcommand{{\\RFiveExponentMaxTwoEFive}}{{{numbers_2e5['exponent_max']:.2f}}}",
        f"\\newcommand{{\\RFiveSixthMomentGamma}}{{{moments['sixth_moment_gamma']:.1f}}}",
        f"\\newcommand{{\\RFiveFourthMomentGamma}}{{{moments['fourth_moment_gamma']:.1f}}}",
        f"\\newcommand{{\\RFiveMomentMarginAtGammaMax}}{{{moments['moment_margin_at_gamma_max']:.1f}}}",
        f"\\newcommand{{\\RFiveLambdaIidLadderExponent}}{{{ladder.loglog_exponent_over_ladder.iloc[0]:.2f}}}",
    ]
    for _, row in ladder.iterrows():
        lines.append(
            f"\\newcommand{{\\RFiveLambdaIidAtH{int(row.H)}}}{{{row.lambda_iid_H:.1f}}}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def classification_table(regenerated, logger):
    """Prints the D0/D1/D2 degree of every published value. Asserts nothing."""
    logger.info("--- Deviation classification against v87 (published -> regenerated) ---")
    logger.info(f"{'quantity':<34} {'published':>10} {'regenerated':>12} {'degree':>7}  source")
    rows = []
    for key, (published, decimals) in PUBLISHED.items():
        if key not in regenerated:
            continue
        value = regenerated[key]
        if value is None or (isinstance(value, float) and math.isnan(value)):
            continue
        # The raw value is passed, never a pre-rounded one: rounding first would
        # collapse D1 (moved below the printed precision) into D0 (bit-identical),
        # and D0 is a statement about float64 equality, not about printing.
        degree = classify_deviation(published, float(value), decimals)
        source = SOURCES.get(key, "")
        logger.info(f"{key:<34} {published:>10.2f} {float(value):>12.4f} {degree:>7}  {source}")
        rows.append(dict(quantity=key, published=published, regenerated=float(value),
                         printed_decimals=decimals, degree=degree, source_cell=source))
    return pd.DataFrame(rows)


SOURCES = {
    "abrupt_slope": "R05_abrupt_add_vs_gamma.csv, OLS of ADD_Data on Gamma",
    "abrupt_intercept": "R05_abrupt_add_vs_gamma.csv, OLS of ADD_Data on Gamma",
    "sqrt_rule_fpr_pct": "R05_abrupt_add_vs_gamma.csv, FPR_rule_xSqrtGamma max",
    "scaling_median_error_pct": "R05_ramp_multigamma_2e5.csv, ADD_Data vs Eq. (5)",
    "recalib_margin_min_pct_2e5": "R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma",
    "recalib_margin_max_pct_2e5": "R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma",
    "lambda_iid_2e5": "R05_ramp_multigamma_2e5.csv, lambda_iid_H",
    "grid_reach_wstar_2e5": "R05_ramp_multigamma_2e5.csv, w_over_wstar_predicted max",
    "censoring_max_pct_2e5": "R05_ramp_multigamma_2e5.csv, censored_Data max",
    "detection_min_pct_2e5": "R05_ramp_multigamma_2e5.csv, DetRate_Data min",
    "lambda_over_gamma_min_2e5": "R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma",
    "lambda_over_gamma_max_2e5": "R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma",
    "sd_over_add_max_2e5": "R05_ramp_multigamma_2e5.csv, SEM_Data and DetRate_Data",
    "med_over_add_min_2e5": "R05_ramp_multigamma_2e5.csv, MED_Data/ADD_Data",
    "rho_w_share_pct_2e5": "R05_ramp_multigamma_2e5.csv, widest w",
    "exponent_min_2e5": "R05_ramp_multigamma_2e5.csv, ramp fit on w_delta_applied",
    "exponent_max_2e5": "R05_ramp_multigamma_2e5.csv, ramp fit on w_delta_applied",
    "model_exponent_min_2e5": "R05_ramp_multigamma_2e5.csv, Eq. (5) fit on w_delta_applied",
    "model_exponent_max_2e5": "R05_ramp_multigamma_2e5.csv, Eq. (5) fit on w_delta_applied",
    "lambda_iid_3e6": "R05_ramp_multigamma_3e6.csv, lambda_iid_H",
    "grid_reach_wstar_3e6": "R05_ramp_multigamma_3e6.csv, w_over_wstar_predicted max",
    "low_gamma_max_error_pct_3e6": "R05_ramp_multigamma_3e6.csv, Gamma <= 4 vs Eq. (5)",
    "rho_w_share_pct_3e6": "R05_ramp_multigamma_3e6.csv, widest w",
    "recalib_margin_max_pct_3e6": "R05_ramp_multigamma_3e6.csv, lambda_star_Data/Gamma",
    "sixth_moment_gamma": "closed form, no Monte Carlo",
    "moment_margin_at_gamma_max": "closed form, no Monte Carlo",
    "lambda_iid_ladder_77k": "R05_lambda_iid_horizon.csv, H = 77000",
}


def load_from_csv(data_dir, suffix, logger):
    """Degraded standalone path: rebuild from the CSVs rather than from memory."""
    logger.warning(
        "--from-csv: the frames are being RELOADED from disk rather than received from steps a "
        "and b in memory. This path exists so a reviewer can rebuild the figure without "
        "re-running the campaigns; run_experiment_R05.sh never uses it. Outputs are stamped "
        "'_fromcsv' so no artefact of this run can be mistaken for one of the chain.")
    read = lambda name: pd.read_csv(data_dir / f"{name}{suffix}.csv", float_precision='round_trip')
    return (read("R05_abrupt_add_vs_gamma"), read("R05_concept_positive_control"),
            read("R05_ramp_multigamma_2e5"), read("R05_ramp_multigamma_3e6"),
            read("R05_lambda_iid_horizon"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-csv", action="store_true",
                        help="Degraded path: reload the step a/b CSVs instead of driving them in memory.")
    parser.add_argument("--fast", action="store_true",
                        help="Degraded smoke path, outputs stamped '_fast'")
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count())
    args = parser.parse_args()

    if args.fast:
        step_b.apply_fast_profile()
    suffix = "_fast" if args.fast else ""
    out_suffix = suffix + ("_fromcsv" if args.from_csv else "")

    results_dir = BASE_DIR / "results" / "R05_scale_law"
    data_dir = results_dir / "data"
    figures_dir = results_dir / "figures"
    tables_dir = results_dir / "tables"
    logs_dir = BASE_DIR / "logs" / "R05_scale_law"
    for d in (data_dir, figures_dir, tables_dir, logs_dir):
        d.mkdir(parents=True, exist_ok=True)

    name = f"exp_R05_scale_law_c{out_suffix}"
    logger = setup_logging(logs_dir / f"{name}.log", name)
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "matplotlib"])

    started = time.time()
    if args.from_csv:
        abrupt, positive, ramp_2e5, ramp_3e6, ladder = load_from_csv(data_dir, suffix, logger)
        _, fit = step_a.certify(abrupt, positive, logger)
    else:
        logger.info("Driving steps a and b in this process; their frames are received in memory "
                    "and no CSV is read back (SPECS 1.6).")
        with ProcessPoolExecutor(max_workers=args.n_jobs) as executor:
            logger_a = step_a.make_logger(args.fast, args.n_jobs)
            abrupt, positive, fit = step_a.run_stage(executor, logger_a, fast=args.fast)

            logger_2e5 = step_b.make_logger("2e5", args.fast, args.n_jobs)
            ramp_2e5, _ = step_b.run_stage(executor, logger_2e5, "2e5", ladder=False, fast=args.fast)

            logger_3e6 = step_b.make_logger("3e6", args.fast, args.n_jobs)
            ramp_3e6, ladder = step_b.run_stage(executor, logger_3e6, "3e6", ladder=True, fast=args.fast)

    numbers_2e5, _ = appendix_b_numbers(ramp_2e5, logger, "2e5")
    numbers_3e6, _ = appendix_b_numbers(ramp_3e6, logger, "3e6")
    numbers_2e5["lambda_c"] = float(ramp_2e5.lambda_star_Concept.iloc[0])
    numbers_3e6["lambda_c"] = float(ramp_3e6.lambda_star_Concept.iloc[0])
    moments = moment_boundary_report(logger)

    # Control (f): the budget effect, side by side, which is the comparison v87
    # rests its "degrades with the monitoring horizon" clause on.
    logger.info("--- control (f): the budget effect on the recalibration rule ---")
    logger.info(f"[control f] margins by Gamma at 2e5: "
                f"{[round(v, 1) for v in numbers_2e5['recalib_margins_by_gamma']]}")
    logger.info(f"[control f] margins by Gamma at 3e6: "
                f"{[round(v, 1) for v in numbers_3e6['recalib_margins_by_gamma']]}")
    logger.info(
        f"[control f] the span widens from "
        f"[{numbers_2e5['recalib_margin_min_pct']:+.1f}, {numbers_2e5['recalib_margin_max_pct']:+.1f}]% "
        f"at H = {numbers_2e5['horizon']} to "
        f"[{numbers_3e6['recalib_margin_min_pct']:+.1f}, {numbers_3e6['recalib_margin_max_pct']:+.1f}]% "
        f"at H = {numbers_3e6['horizon']}. The degradation with the horizon that v87 asserts is "
        f"{'visible' if numbers_3e6['recalib_margin_max_pct'] > numbers_2e5['recalib_margin_max_pct'] else 'NOT visible'} "
        f"in these two budgets.")

    figure_path = figures_dir / f"fig05_scale_law_orthogonality{out_suffix}.png"
    plot_figure(abrupt, ramp_2e5, figure_path, logger)

    macros_path = tables_dir / f"R05_claims{out_suffix}.tex"
    emit_macros(macros_path, abrupt, positive, fit, numbers_2e5, numbers_3e6, moments, ladder)
    logger.info(f"Wrote {macros_path.relative_to(BASE_DIR)}")

    ladder_shortest = ladder[ladder.H == ladder.H.min()]
    regenerated = {
        "abrupt_slope": fit["slope"],
        "abrupt_intercept": fit["intercept"],
        "sqrt_rule_fpr_pct": 100.0 * float(abrupt.FPR_rule_xSqrtGamma.max()),
        "scaling_median_error_pct": numbers_2e5["median_error_pct"],
        "recalib_margin_min_pct_2e5": numbers_2e5["recalib_margin_min_pct"],
        "recalib_margin_max_pct_2e5": numbers_2e5["recalib_margin_max_pct"],
        "lambda_iid_2e5": numbers_2e5["lambda_iid"],
        "grid_reach_wstar_2e5": numbers_2e5["grid_reach_wstar"],
        "censoring_max_pct_2e5": numbers_2e5["censoring_max_pct"],
        "detection_min_pct_2e5": numbers_2e5["detection_min_pct"],
        "lambda_over_gamma_min_2e5": numbers_2e5["lambda_over_gamma_min"],
        "lambda_over_gamma_max_2e5": numbers_2e5["lambda_over_gamma_max"],
        "sd_over_add_max_2e5": numbers_2e5["sd_over_add_max"],
        "med_over_add_min_2e5": numbers_2e5["med_over_add_min"],
        "rho_w_share_pct_2e5": numbers_2e5["rho_w_share_pct"],
        "exponent_min_2e5": numbers_2e5["exponent_min"],
        "exponent_max_2e5": numbers_2e5["exponent_max"],
        "model_exponent_min_2e5": numbers_2e5["model_exponent_min"],
        "model_exponent_max_2e5": numbers_2e5["model_exponent_max"],
        "lambda_iid_3e6": numbers_3e6["lambda_iid"],
        "grid_reach_wstar_3e6": numbers_3e6["grid_reach_wstar"],
        "low_gamma_max_error_pct_3e6": numbers_3e6["low_gamma_max_error_pct"],
        "rho_w_share_pct_3e6": numbers_3e6["rho_w_share_pct"],
        "recalib_margin_max_pct_3e6": numbers_3e6["recalib_margin_max_pct"],
        "sixth_moment_gamma": moments["sixth_moment_gamma"],
        "moment_margin_at_gamma_max": moments["moment_margin_at_gamma_max"],
    }
    # The 102.8 of v87 belongs to H = 77,000 and to no other horizon, so the
    # comparison is only offered when the ladder actually visited it. Under
    # --fast the ladder runs at toy horizons and the row is withheld rather than
    # classified against a value it does not correspond to.
    if int(ladder_shortest.H.iloc[0]) == step_b.LADDER_HORIZONS[0] and not args.fast:
        regenerated["lambda_iid_ladder_77k"] = float(ladder_shortest.lambda_iid_H.iloc[0])
    else:
        logger.warning(
            "Ladder shortest horizon is %d, not the 77000 that v87's 102.8 refers to; the "
            "comparison is withheld rather than made against a mismatched horizon.",
            int(ladder_shortest.H.iloc[0]))
    table = classification_table(regenerated, logger)
    table_path = data_dir / f"R05_deviation_classification{out_suffix}.csv"
    save_fair_csv(table, table_path)
    logger.info(f"Wrote {table_path.relative_to(BASE_DIR)} ({len(table)} rows)")
    logger.info(f"Degrees: {dict(table.degree.value_counts())}")
    logger.info(f"Step c elapsed: {time.time() - started:.1f} s")


if __name__ == "__main__":
    main()
