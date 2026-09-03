# T7 v2: CAMERA-READY CANDIDATE RECONCILIATION & ANCHOR CERTIFICATION

**Role:** You are acting as `candidate_auditor`. Execute all steps autonomously without truncating or guessing.

## Execution Sequence

### Step 1: Clean Working Tree Reset
Run via `bash`:
```bash
git checkout ac5f849 -- docs/camera_ready_candidates/
rm -f docs/camera_ready_candidates/ANCHOR_VERIFICATION.md
```

### Step 2: Restore Lost Files
Restore the 11 lost files from `ac5f849` identified in `docs/camera_ready_candidates/RECONCILIATION.md` §1.3:
```bash
for f in R09_v87_arl0_censoring.md R09_v87_delay_parity_scope.md R09_v87_stream_counts.md R11_v87_figure11_caption.md R13_v87_frozen_null_scope.md R14_v87_reliable_range_scope.md R14_v87_synthetic_control_strength.md R16_v87_boundary_sensitivity.md R16_v87_dating_algorithm.md R17_v87_persistence_collapse_mechanism.md R17_v87_warmup_resolution.md R17_v87_warmup_restoration_scope.md; do
  git show ac5f849:docs/camera_ready_candidates/$f > docs/camera_ready_candidates/$f
done
```

### Step 3: Surgical Anchor & Header Repairs
Edit candidate files using `edit` or `write_file` to fix all 9 known broken anchors and missing headers:
1. **`R04b_v87_efficiency_crossing.md`:** Anchor to `overtakes it below a measured $\nu^{\star} \approx 4.9$ degrees of freedom, precisely where parametric estimation is most fragile`.
2. **`R04b_v87_estimation_cost.md`:** Anchor to `so the extra $0.3$ degrees of freedom is what a finite warm-up costs the parametric route`.
3. **`R04b_v87_oracle_tracks_analytic.md`:** Anchor to `an \emph{oracle} arm standardized by the true GARCH parameters crosses at $4.6$, on the analytic prediction, so the extra`.
4. **`R02b_v87_iid_arm_rejection.md`:** Fix anchor string to `already over-reject on the i.i.d.\ arm ($9.2\%$)`. Fix prose to cite 8th moment of residuals ($\nu \le 8$), NOT fourth moment.
5. **`R15_v87_*.md` (4 files):** Append `>>> END OF BLOCK` terminators.
6. **`R07_v87_*.md` (3 files):** Replace `\RSeven...` with literal numbers (`2.9 \times 10^{-3}`, etc.).
7. **Two-Family Headers:** Enforce `PARKED`, `Trigger: Acceptance notification of 14 November 2026`, and `Register entry:` across all files.

### Step 4: Machine Verification Gate
Run:
```bash
python experiments/common/verify_camera_ready.py
```
**You are FORBIDDEN from concluding until this command exits with code 0.**