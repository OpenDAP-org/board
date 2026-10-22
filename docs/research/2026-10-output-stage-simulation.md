# Headphone output stage: simulation of the ADR 0012 conditions

- **Date:** 2026-10-22. Stock figures were captured on 2026-10-22.
- **Question:** [ADR 0012](../adr/0012-headphone-output-stage.md) accepted its output stage on three conditions that need simulation: (1) the TPS65131 inverter margin against the 80 % rule of BRD-049 under the worst-case output load; (2) current sharing between the paralleled OPA1622 halves; (3) the LT3045 / LT3094 headroom, dissipation and rejection of the TPS65131 switching ripple. Do they hold, and if not, what is the smallest compliant fix? Follow-up (§5), after the lead chose to keep the full ADR 0012 output: which documented inverting converter makes the −7 V pre-rail from VSYS with margin, and how must the LDO current limits and pre-rails change?
- **Inputs:**
  - [ADR 0012](../adr/0012-headphone-output-stage.md); [ADR 0014](../adr/0014-two-cell-battery.md) (2S pack: the TPS65131 now runs from the TPS62136 3.8 V rail, VSYS_LV);
  - [power tree v0](../specs/power-tree-v0.md) §4.1, §4.2, §4.10, §4.10.1, §4.11; [BOM v1](../specs/bom-v1.md) lines 19, 22–26, 37, 107–111 and D31;
  - [headphone output power research](2026-10-headphone-output-power.md) §4.5; [2S battery study](2026-10-battery-2s.md) §4;
  - part sheets in `libs/parts/` for TPS65131RGER, LT3045EDD#TRPBF, LT3094EDD#TRPBF, OPA1622IDRCR, CS43198-CNZR.
- **Netlists:** [`sim/output-stage/`](../../sim/output-stage/README.md). Every table below can be rerun from there.
- **Conventions:**
  - **UNVERIFIED** means no primary source was read in this session.
  - **Est.** marks an engineering estimate, to be replaced by measurement (T1-026).
  - "Worst stack" and "typical stack" are the two TPS65131 parameter sets of §2.1.
  - Percentages of the TPS65131 switch limit are against its **1.8 A minimum** (SLVS493E §6.5). BRD-049: continuous load ≤ 80 % of the rating; the worst-case trip of the protecting limiter ≤ 100 %.
  - Nothing here edits an ADR, the BOM, the power tree or a requirement.

> **How this was gathered, and its limits.**
>
> - **Read directly:** TI TPS65131 SLVS493E (Apr 2022, sha256 `e8360b95…0ed`, same file as the BOM), including the Figure 6-2, 6-4 and 8-11 plots; TI OPA1622 SBOS727B (May 2016, sha256 `505556d1…824`); ADI LT3045 Rev. D (11/22, sha256 `9132e595…ba6`) and LT3094 Rev. B (01/20, sha256 `c82438ca…94d`) through the LCSC mirror, including curves G45 and G47; TI TPS62136 SLVSDV2 (Mar 2017, sha256 `b445aeac…70a`); TI TPS62903 SLVSES3A (Mar 2021, sha256 `323bfe65…cee`); NXP/Nexperia PMEG2010AEH Rev. 03 (Mar 2007, LCSC mirror, sha256 `c1816d6b…e13`); Murata DFE252012F series sheet (LCSC mirror, sha256 `6175add0…51f`); TI LMR33630 SNVSAN3F (Nov 2020, sha256 `3b0920a4…04a`); TI application notes SNVA856B (*Working With Inverting Buck-Boost Converters*, Oct 2022) and SLVA317B (Oct 2012); Coilcraft XGL4020 Doc 1529 (02/19/26, sha256 `1e050d7e…c2c0`) and XAL4000 Doc 806 (02/25/26); TI product pages for TPS65131, OPA1622, TPS62903, TPS62913, LMR33630, LMR33620, LMR51420, LMR51430, LMR36506 and TPS62933; FindChips for TPS62903RPJR, LMR33630CRNXR, LMR33630BRNXR, LMR33630CDDAR, LMR33620CRNXR and XGL4020-222MEC.
> - **Models:** TI's **OPA1622 PSpice model** SBOM958 Rev. D (model "Final 1.5", 05JUL2022; `sbom958d.zip` sha256 `1bafa50b…9b8`) runs in ngspice 47 in PSpice compatibility mode. It is TI copyright and is not in the repository. **TI publishes no TPS65131 transient model** (none on the product page, none in SLVS493E §10.1), so the TPS65131 is a **switch-level model built here** from datasheet parameters (§2.1). TI's **LMR33630C unencrypted PSpice transient model** SNVMBG5 Rev. A ("Final 1.10", 31AUG2020, topologies Buck and Inverting Buck Boost; `SNVMBG5.zip` sha256 `bf3d8f3b…7c2`) runs in ngspice in PSpice compatibility mode (§5). It is TI copyright and is not in the repository. The LT3045 and LT3094 are not simulated: their figures come from the datasheets, and the ADI LTspice models were not used.
> - **Not covered:** web search was unavailable (session budget used up). No TPS62136 model was run, so its load-step droop is not simulated (§2.3). The OPA1622 model does not include the EN pin or temperature. Layout, ceramic DC-bias derating and inductor core loss are estimates. Nothing was built or measured.

---

## 1. Summary

1. **The TPS65131 inverter passes the 80 % rule only for the average load the ADR used, not for the load it actually switches.**
   - At its new fixed input (3.8 V, band 3.7–3.9 V) and 275 mA DC per rail, the inverter peaks at **1.11 A typical / 1.24 A worst stack = 61 % / 69 %** of the 1.8 A minimum limit. Eq. 4 of SLVS493E gives 1.22 A (68 %). This part of ADR 0012 holds.
   - But a full-scale sine is not a DC load. Each rail supplies a full-wave rectified current: 275 mA is its average; its **peak is 433 mA** (2 legs × 200 mA + quiescent, ADR 0012 numbers). The 10 µF output capacitors cannot bridge an audio half-cycle, so the converter follows the peak. The switch current limit acts cycle by cycle, on that peak.
   - At 433 mA the inverter needs **1.82 A (101 %) typical** at 3.8 V and cannot regulate at all in the worst stack. Audio-rate runs confirm it: **1.83 A at 100 Hz, 1.89 A at 1 kHz** (typical). Scaling TI's own typical curve (Figure 6-4) gives about 1.55 A (86 %, est.). **Fail** on every basis.
   - The **boost passes**: 56–65 % at 433 mA, 69–78 % even at 520 mA.
   - On the interim 1S pack (reference only), the worst stack cannot hold −7 V at 275 mA at VIN 3.0 V; typical is 75 %.
2. **The LT3045 / LT3094 current limit (≈ 401 mA programmed) is below the peak the amplifiers ask for.** By ADR 0012's own figures the LDO output peaks at 421 mA; by the TI OPA1622 model at about 510 mA (both channels, balanced 32 Ω, DAC full scale). A full-scale balanced 32 Ω sine on both channels therefore clips at the LDO limit, whatever the TPS65131 does. The 640 mW expectation of ADR 0012 cannot be met with the current RILIM.
3. **Current sharing works.** With the worst-case spread (±500 µV offset, 0.1 % gain resistors and 1 % ballast in the worst direction) at DAC full scale into balanced 32 Ω:
   - per-half peak currents **128 mA and 112 mA** (53.3 % / 46.7 %); largest instantaneous difference 25 mA;
   - DC circulation **1.3 mA** per half (BOM estimate: 1.3 mA);
   - dissipation **0.277 W and 0.245 W** per half, **0.52 W per package (+25 °C at θJA 47.6 °C/W)**;
   - no overshoot on a step into 400 pF or 10 nF per leg (model).
   The 1.0 Ω ballast value is adequate. The TI model is about 15 % optimistic on output current against SBOS727B Table 2 at 16 Ω (§3.1).
4. **The LDOs keep their headroom in typical conditions, and run out of it in the tolerance corner at the signal peak.**
   - Typical headroom is 0.94 V, 0.78–0.86 V at the signal peak, against ≈ 0.18–0.22 V typical dropout.
   - Worst corner: 0.60 V DC (pre-rail −3 %, LDO output +2 %), and 0.40 V at the signal peak on the negative rail, against a full-range maximum dropout of ≈ 0.38 V at 400 mA. That is at the edge.
   - Dissipation: 0.32 W typical, 0.41 W at maximum headroom, per LDO at 275 mA average (+11 to +14 °C).
   - Rejection of the 1.25–1.5 MHz ripple: ≈ 70 dB (LT3045) and ≈ 67 dB (LT3094) at 1 V headroom, from curves G45 / G47. The simulated 18–33 mVpp pre-rail ripple becomes ≈ 10–15 µVpp, out of band.
5. **Smallest compliant fix (first pass).** No inductor or input-voltage change brings the inverter under 80 % at the 433 mA peak: a low-DCR inductor gains 3–7 points, and VIN 5.0 V still gives 80–90 %. Two ways were left (§2.5): (a) a software output ceiling, ≈ 310–400 mW per channel balanced 32 Ω instead of 640 mW, or (b) a new negative pre-rail converter. The lead chose (b): a software cap is not acceptable on the audio path.
6. **Follow-up (§5): make −7 V with a TI LMR33630C as an inverting buck-boost from VSYS, and pair the LDOs.**
   - **Converter:** LMR33630C, 2.1 MHz, VQFN-HR (LMR33630CRNXR, Mouser 2,748 authorized, 2026-10-22). TI documents it in this topology: SNVA856B uses it as the worked example, and TI publishes an inverting transient model, SNVMBG5. Inductor: Coilcraft XGL4020-222ME (2.2 µH), the same family and land as the BOM's XGL4020-102ME. Output: 100 kΩ / 16.5 kΩ → −7.06 V.
   - **Simulated with TI's model** at VSYS 6.0 V, the worst case for current:
     - 433 mA rectified-sine peak at 1 kHz: inductor peak **1.80 A = 47 %** of the 3.85 A minimum high-side limit;
     - LDO current-limit case, 0.78 A DC: peak **2.13 A = 55 %**, valley 1.39 A = 48 % of the 2.9 A minimum valley limit.
   - **Voltage stress:** VIN to the IC ground is VSYS + |VOUT| ≤ 9.9 + 7.24 = 17.1 V, **48 % of the 36 V recommended maximum** (45 % of the 38 V absolute maximum).
   - **Ripple and start-up:** 6 mVpp ripple at 0.78 A; 0.11 V dip at the load step; no start-up overshoot beyond 0.1 %.
   - **The TPS65131 keeps only its boost (+7 V).** Its inverter is disabled: ENN and PSN to GND, inductor, diode and output capacitors not fitted (§5.4; TI does not document a single-output connection, **UNVERIFIED**).
   - **LDOs:** one 500 mA LT3045 / LT3094 cannot pass the ≈ 0.46 A design peak with margin while its limit stays within its 500 mA rating. Both ADI datasheets describe direct paralleling. **Two LT3045 and two LT3094**, SET pins tied (RSET 2 × 60.4 kΩ, CSET 2 × 0.47 µF, same 65 ms ramp), 20 mΩ trace ballast, RILIM **523 Ω** (LT3045) and **13.0 kΩ** (LT3094). Result: ±516–646 mA per rail, **+13 %** over the 457 mA design peak (+23 % over ADR 0012's 421 mA). The bound is the TPS65131 boost, at ≈ 99 % of 1.8 A worst stack (≈ 90 % typical) when the positive pair sits at its maximum limit.
   - **Pre-rails stay at ±7.0 V:** worst-corner headroom at the signal peak is 0.50 V (positive) and 0.65 V (negative), against ≤ 0.35 V maximum dropout at the per-LDO current. The −7.3 V option is not needed.

## 2. TPS65131 ±7 V pre-rails (question 1)

### 2.1 Model

No TI model exists, so `tps65131-switch-model.cir` models each converter at switch level:

- **Switch:** a conductance ramped over 5 ns, which gives conduction and transition loss.
  - Inverter PMOS: 440 mΩ typical, 620 mΩ maximum.
  - Boost NMOS: 200 mΩ typical, 300 mΩ maximum (SLVS493E §6.5; the table gives 230/300 mΩ at VPOS 5 V and 170/200 mΩ at 10 V).
- **Rectifier PMEG2010AEH:** diode fitted to the VF table (220 / 290 / 430 mV maximum at 10 mA / 100 mA / 1 A); Cd 70 pF maximum.
- **Inductor DFE252012F-4R7M:**
  - DCR 190 mΩ maximum, 160 mΩ typical;
  - L(I) falls 30 % at 2.1 A (rated) or 2.4 A (typical);
  - ±20 % tolerance (Murata sheet).
- **Output capacitance:** 10 µF effective per output, 5 mΩ ESR. This assumes the BOM's 4 × 4.7 µF 25 V X7R after DC-bias derating at 7 V (est.).
- **Control:**
  - fixed frequency, 1.25 MHz minimum or 1.38 MHz typical (§6.6); maximum duty 87.5 %;
  - cycle-by-cycle current limit, which can be disabled to read the unconstrained peak;
  - **peak-current-mode loop** with slope compensation. TI's control is a multiple-feedforward PWM (§7.3.2), not reproduced. Steady-state switch current depends on the power stage, not on the control law. Loop dynamics (sag depth, overshoot on recovery) are **not** representative.

Parameter stacks:

| Stack | Rds(on) inv / boost | DCR | L | Isat (−30 %) | fs | Diode |
|---|---|---|---|---|---|---|
| Worst | 620 / 300 mΩ | 190 mΩ | 3.76 µH (−20 %) | 2.1 A | 1.25 MHz | max VF |
| Typical | 440 / 200 mΩ | 160 mΩ | 4.7 µH | 2.4 A | 1.38 MHz | typ VF |

The worst stack stacks every limit at once. It is a bound, not an expected part.

### 2.2 Calibration against SLVS493E

The datasheet gives the maximum output current only as typical curves at 25 °C (Figures 6-2 and 6-4), presumably at the typical 1.95 A limit. With the typical stack, the model's output current at a 1.95 A switch peak (`sweep.py calibration`):

| Output | VIN | Model | SLVS493E curve (read) | Model vs curve |
|---|---|---|---|---|
| −4 V | 3.0 / 3.7 / 4.5 V | ≈ 500 / 632 / 737 mA | ≈ 440 / 690 / 850 mA | +14 / −8 / −13 % |
| −10 V | 3.0 / 3.7 / 4.5 V | 259 / 339 / 411 mA | ≈ 270 / 410 / 480 mA | −4 / −17 / −14 % |
| +5 V | 3.0 / 3.7 V | 838 / 1094 mA | ≈ 800 / 1020 mA | +5 / +7 % |
| +10 V | 3.0 / 3.7 V | 401 / 528 mA | ≈ 470 / 600 mA | −15 / −12 % |

Near the T1 operating point (inverter, 3.7 V) the model delivers 8–17 % less current than TI's typical part for the same switch peak. It is therefore **conservative**. The model's efficiency (≈ 80 % at −7 V, 275 mA, 3.8 V) matches the 0.8 the power tree assumed. For −7 V at 3.7–3.9 V, Figure 6-4 interpolates to about 525–565 mA. The typical-stack model reaches 1.95 A at about 455 mA.

### 2.3 Input voltage

ADR 0014 feeds the TPS65131 from VSYS_LV = 3.8 V (TPS62136). The TPS62136 regulates its feedback within ±1 % in PWM mode (SLVSDV2 §6.5). With 1 % divider resistors, the rail is about 3.72–3.88 V (est.). Load-step droop and the trace and filter drop at ≈ 2 A input current are not simulated (**UNVERIFIED**). The table therefore runs 3.6–3.9 V; 3.6 V stands for a droop of 0.2 V. The 1S rows (3.0, 3.3, 3.5 V) are the interim-pack reference; 4.2, 4.5 and 5.0 V test the "raise the input" fix.

### 2.4 Results

Loads per rail (both rails equal):

- **A, 275 mA DC:** the power tree §4.1 worst continuous average, the basis of ADR 0012 and Eq. 4.
- **B, 288 mA DC:** A plus the LDO ground current (≈ 13 mA, est. from the LT3045 / LT3094 ground-current tables).
- **C, 433 mA:** the instantaneous peak of the same full-scale sine: 2 × 200 mA + 20.8 mA amplifier quiescent + 12 mA LDO ground (est.).
- **D, 465 mA:** the hardware bound. The LT3094's programmed limit is ≈ 451 mA maximum (403 mA × 1.12, est., BOM D35), plus 14 mA ground current.

Inverter peak switch current, % of 1.8 A (`sweep.py margin`). "Lost" means the converter cannot hold −7 V with an unlimited switch current: the real part would sit at its limit and the rail would sag.

| VIN | A typ | A worst | B typ | B worst | C typ | C worst | D typ | D worst |
|---|---|---|---|---|---|---|---|---|
| 3.0 (1S ref.) | 1.35 A, 75 % | lost | 80 % | lost | lost | lost | lost | lost |
| 3.3 (1S ref.) | 68 % | 78 % | 72 % | 83 % | lost | lost | lost | lost |
| 3.5 (1S ref.) | 65 % | 74 % | 68 % | 78 % | 113 % | lost | 128 % | lost |
| 3.6 (droop) | 64 % | 72 % | 67 % | 75 % | 108 % | lost | 121 % | lost |
| **3.7** | 62 % | 70 % | 65 % | 74 % | **104 %** | lost | 115 % | lost |
| **3.8** | **1.11 A, 61 %** | **1.24 A, 69 %** | 64 % | 72 % | **1.82 A, 101 %** | lost | 111 % | lost |
| **3.9** | 60 % | 67 % | 63 % | 71 % | **98 %** | lost | 107 % | lost |
| 4.2 | 58 % | 64 % | 60 % | 67 % | 91 % | 106 % | 99 % | 118 % |
| 4.5 | 56 % | 62 % | 58 % | 65 % | 86 % | 98 % | 93 % | 107 % |
| 5.0 | 53 % | 59 % | 55 % | 62 % | 80 % | 90 % | 86 % | 97 % |

Boost peak switch current, % of 1.8 A: at 3.7–3.9 V, A 38–43 %, C 56–65 %, D 60–69 %. At 520 mA (the OPA1622-model peak, §3.2) it is **69–78 %** at 3.7–3.8 V. At 3.0 V (1S): C 75–83 %, D 81–91 %. **The boost passes in the 2S tree.**

**Audio-rate check** (`tps65131-audio-load.cir`, VIN 3.8 V, load C as a rectified sine, both channels in phase):

| Stack, tone | Switch limit off: peak | Limit at 1.8 A: −7 V rail range | Input current (avg) |
|---|---|---|---|
| Typical, 100 Hz | 1.83 A (102 %) | −6.40 to −8.41 V | 1.32 A |
| Typical, 1 kHz | 1.89 A (105 %) | −6.76 to −7.42 V | 1.32 A |
| Worst, 100 Hz | 2.50 A (139 %) | collapses (model) | 1.49 A |
| Worst, 1 kHz | 2.67 A (148 %) | −6.05 to −8.97 V | 1.54 A |

- The audio-rate peaks equal the DC peaks at load C: the converter tracks the waveform, so the instantaneous peak, not the average, is the load.
- When the limit engages, the rail sags during the peaks and overshoots on recovery. Both are shaped by this model's loop, not TI's.
- An overshoot beyond the TPS65131's +5 % overvoltage threshold (−7.34 V, §7.3.6) would shut the inverter down. Whether the real loop does this is **UNVERIFIED**.

**Load that meets the rule** (`sweep.py ceiling`, instantaneous load per rail on the inverter):

| VIN | 80 % (1.44 A), worst / typ | 100 % (1.8 A), worst / typ |
|---|---|---|
| 3.7 V | 0.310 / 0.348 A | 0.366 / 0.419 A |
| 3.8 V | 0.317 / 0.352 A | 0.377 / > 0.42 A |

Scaling Figure 6-4 directly (≈ 545 mA at 1.95 A, 3.8 V) gives ≈ 0.40 A for 80 % (est.).

**Verdict (question 1):**

| Case | Inverter | Boost |
|---|---|---|
| 275 mA average (ADR basis), 3.7–3.9 V | **Pass**: 60–62 % typ, 67–70 % worst | Pass: 38–43 % |
| 433 mA instantaneous peak of the same sine, 3.7–3.9 V | **Fail**: 98–104 % typ; cannot regulate in the worst stack; ≈ 86 % on TI's typical curve | Pass: 56–65 % |
| LDO current-limit bound (465 mA), ≤ 100 % rule | **Fail**: 107–115 % typ | Pass: 60–69 % |
| Interim 1S pack, 3.0 V | **Fail** even at 275 mA in the worst stack; 75 % typ | Pass at 275 mA (48–52 %) |

The inductor sees the same peaks. At load C its average current is ≈ 1.6–1.7 A (typical). That exceeds its 1.5 A ΔT 40 °C rating while the peak lasts, and the 1.8–2.2 A switch limit sits at or above its 2.1 A (−30 %) rating (BOM D31).

### 2.5 Fixes, quantified

| Fix | Effect at load C, 3.7–3.8 V | Compliant? | Cost |
|---|---|---|---|
| Low-DCR 4.7 µH inductor (DCR 50–60 mΩ, Isat ≥ 3.5 A, generic parameters, est.) | 94–96 % typ, 107–111 % worst | No | Larger inductor |
| Raise the TPS65131 input to 5.0 V (its maximum is 5.5 V) | 80 % typ, 90 % worst | No | A separate rail or a higher VSYS_LV |
| **(a) Software ceiling + RILIM change** | Instantaneous rail current ≤ 0.31 A (80 %, worst stack, 3.7 V). RILIM 475 Ω (LT3045, 316 mA) and 12.1 kΩ (LT3094, 310 mA) bound a software failure at ≈ 0.35 A max + ground ≤ 0.366 A (100 %) (est., spreads at these values not tabulated) | Yes | Balanced 32 Ω full-scale sine on both channels: ≈ 310 mW/ch (worst stack) to ≈ 400 mW/ch (typical stack), against 640 mW; SE 16 Ω ≈ 155 mW/ch; SE 32 Ω unaffected (124 mA peak). Music peaks above the ceiling clip |
| **(b) Negative pre-rail from a TPS62903 inverting buck-boost on VSYS** | IL ≈ 0.52 A / (1 − D) / 0.85 = 1.32 A average at VSYS 6.0 V (D = 0.54), plus 0.73 A half-ripple (2.2 µH, 1 MHz) ≈ **2.1 A = 51 % of 4.0 A** (est.) | Yes, if confirmed | One more TPS62903 (same part number as the 2S bucks; Mouser 2,589 authorized), inductor and capacitors. VIN-to-GND 15.8 V at VSYS 8.8 V = 93 % of 17 V (88 % of the 18 V absolute maximum). Inverting use is not described in SLVSES3A. Needs a simulation with TI's PSpice model SLVMDN8 and a review of the VSYS maximum |

The software ceiling of (a) and the output power it costs are figures for the maintainers. ADR 0014 item 3 rules out limits other than safety limits, and (a) is a safety limit only because the converter is undersized. Option (b) keeps the ADR 0012 output and moves the margin problem to a part with 2× the current rating.

## 3. Paralleled OPA1622 halves (question 2)

### 3.1 Model check

TI's model against SBOS727B Table 2 (±5 V, TI's difference amplifier, `opa1622-model-check.cir`):

| Load | Table 2: maximum before clipping | Model: last clean step | Model: clips at |
|---|---|---|---|
| 16 Ω | 95 mW = 1.74 V peak, 109 mA | 2.00 V peak, 125 mA (125 mW) | ≈ +2.2 / −2.05 V (≈ +138 / −128 mA) |
| 32 Ω | 150 mW = 3.10 V peak | 3.23 V peak (163 mW) | ≈ 3.26 V |

The model's output current limit follows the datasheet short-circuit figure (+145 / −132.6 mA, specified at ±18 V). At 16 Ω it delivers about 15 % more current than TI measured before clipping. Model output powers are therefore upper bounds. ADR 0012's 175–218 mA per leg remains the realistic figure.

### 3.2 Sharing

Setup (`opa1622-paralleled-halves.cir`):

- one balanced channel: L+ and L− legs, each two halves of one package;
- each half is its own difference amplifier (1.00 kΩ / 1.62 kΩ, 100 pF), with feedback before a 1.0 Ω ballast;
- ±6.04 V ideal rails; 32 Ω between legs; 400 pF per leg to ground;
- DAC at 4.90 Vpp typical full scale (`+1dB_EN` = 0, DS1156F2 Table 3-4), ideal source;
- worst spread: half A with +500 µV offset (SBOS727B maximum at 25 °C), resistors at +0.1 % gain and ballast at −1 %; half B the opposite.

| Case | Half A peak | Half B peak | Share A / B | Leg peak | Leg voltage | Balanced power | Dissipation A / B | Package |
|---|---|---|---|---|---|---|---|---|
| No spread, DAC 2.45 V peak | 120 mA | 120 mA | 50 / 50 % | 241 mA | 3.85 V | 926 mW | 0.261 / 0.261 W | 0.52 W |
| **Worst spread, 2.45 V peak** | **128 mA** | **112 mA** | **53.3 / 46.7 %** | 240 mA | 3.85 V | 926 mW | **0.277 / 0.245 W** | **0.52 W** |
| Worst spread, DAC max 2.57 V peak | 132 mA | 124 mA | 51.6 / 48.4 % | 248 mA | 3.98 V | 1.01 W (THD 0.5 %: current limit) | 0.274 / 0.246 W | 0.52 W |
| Worst spread, 2.0 V peak | 107 mA | 92 mA | 53.8 / 46.2 % | 196 mA | 3.14 V | 617 mW | 0.271 / 0.238 W | 0.51 W |
| Worst spread, no signal | +1.3 mA DC | −1.3 mA DC | — | 0 | 0.2 mV | 0 | 0.039 / 0.039 W | 0.08 W |

- **Imbalance:** at most 25 mA instantaneous (16 mA on positive peaks, 25 mA on negative peaks), with a 2.6 mA DC component.
  - The gain-resistor spread dominates. Offset alone gives the 1.3 mA DC circulation the BOM estimated.
  - Offset drift (2.5 µV/°C maximum, SBOS727B §6.5) adds ≈ 0.15 mV at 85 °C: negligible.
  - When the stronger half reaches its own limit (DAC maximum), the other half takes the rest. Sharing then improves, to 51.6 / 48.4 %.
- **Dissipation:** the hotter half takes 0.277 W, 13 % more than its twin. The package total stays at 0.52 W, the power tree's 0.5 W estimate: +25 °C at θJA 47.6 °C/W (SBOS727B §6.4), on a JEDEC board.
- **Stability:** a ±50 mV step at the DAC gives no measurable overshoot (< 0.1 %) with 400 pF or 10 nF per leg; the ballast isolates the load. This is a time-domain check on a macromodel, not a phase-margin measurement.
- **Rail current from the model:** one balanced channel draws 256 mA peak and 166 mA average per rail. Both channels in phase: **≈ 510 mA peak, ≈ 330 mA average per rail**, above ADR 0012's 421 / 275 mA. The model is optimistic on current (§3.1), so the real figure lies between the two. Either way it exceeds the ≈ 401 mA LDO limit (§4.3).

**Verdict (question 2):** current sharing with 1.0 Ω ballast is within ±3.3 % of an even split at full output in the worst case. Per-half dissipation stays at or below 0.28 W. The ballast value can stay. Measure THD+N, output impedance and sharing on the first board, as planned (research §6).

## 4. LT3045 / LT3094 ±6 V post-regulators (question 3)

Figures from LT3045 Rev. D and LT3094 Rev. B. The LDOs are not simulated; the pre-rail behaviour comes from §2.

### 4.1 Headroom

| | Positive (LT3045) | Negative (LT3094) |
|---|---|---|
| Pre-rail nominal (BOM line 111) | +6.975 V | −6.987 V |
| Pre-rail minimum magnitude (3 % DC accuracy, SLVS493E §6.5) | 6.77 V | 6.78 V |
| LDO output, maximum: 102 µA × 60.4 kΩ × 1.001 + 2 mV (p. 3 / p. 4) | 6.17 V | 6.17 V |
| Headroom, nominal / worst DC | 0.94 / 0.60 V | 0.95 / 0.61 V |
| Pre-rail dip at the signal peak (§2.4, 1 kHz, limit off; typical / worst) | 0.08 / 0.09 V | 0.17 / 0.21 V |
| **Headroom at the peak, typical / worst corner** | 0.86 / 0.51 V | **0.78 / 0.40 V** |
| Maximum dropout, full range, at ≈ 400 mA (interpolated) | ≈ 400 mV (350 at 300 mA, 450 at 500 mA) | ≈ 378 mV (280 at 100 mA, 410 at 500 mA) |
| Typical dropout | ≈ 215 mV (G14) | ≈ 180 mV (G14) |

Typical conditions leave about 0.6 V above dropout. The negative LDO's worst corner leaves ≈ 20 mV at the signal peak: at the edge. Raising both pre-rails by 0.2 V would restore the margin for ≈ 55 mW more LDO loss at 275 mA (est.). It moves the TPS65131 the wrong way (≈ +2 points), so it is noted, not proposed.

### 4.2 Dissipation

P = (VIN − VOUT) × IOUT + VIN × IGND (LT3045 p. 22). IGND is ≈ 9 mA at 275 mA, est. from the ground-current tables (4.3 mA typ at 100 mA, 15 mA at 500 mA, in dropout).

| Load (average) | Nominal headroom (0.94 V) | Maximum headroom (7.19 − 5.92 = 1.27 V) | Rise at θJA 34 °C/W |
|---|---|---|---|
| 275 mA (ADR 0012) | 0.32 W | 0.41 W | +11 / +14 °C |
| 330 mA (OPA1622 model, §3.2) | 0.38 W | 0.49 W | +13 / +17 °C |
| Idle, SE (10.4 mA + IGND 2.2–2.35 mA) | 25–27 mW | — | — |

Within rating. The ≈ 400 mA limit caps the signal-peak current (§4.3).

### 4.3 Current limit against the signal peak

- **Programmed limit:** 150 mA·kΩ / 374 Ω = 401 mA (LT3045, p. 20); 3.75 A·kΩ / 9.31 kΩ = 403 mA (LT3094, p. 5). The minimum is ≈ 360 mA (est., BOM D35).
- **Peak demand per rail at the LDO output:** 421 mA by ADR 0012's per-leg figure; ≈ 500 mA by the TI model.
- **Consequence:** the full-scale balanced 32 Ω sine on both channels is current-limited by the LDOs on every peak. That is clipping, and it takes the LDO out of regulation while it lasts.
- **Resolved in §5.3** with paired LDOs. A single LDO at its 500 mA point (300 Ω / 7.5 kΩ, 450–560 mA) would have a maximum trip of 110–112 % of its rating and a minimum of 450 mA, below the 457 mA design peak.

### 4.4 Rejection of the TPS65131 ripple

Simulated pre-rail ripple at the switching frequency (10 µF effective, 5 mΩ ESR, no ESL):

- 18–21 mVpp at 275 mA;
- 30–33 mVpp at 433 mA (typical stack).

| | LT3045 | LT3094 |
|---|---|---|
| Table, 1 MHz, 2 V headroom, 500 mA, CSET 0.47 µF | 76 dB | 74 dB |
| Curve at 1 V headroom, 1–2 MHz (G45 / G47, read) | ≈ 70 dB | ≈ 67 dB (1 MHz), ≈ 68 dB (2 MHz) |
| Curve at 0.5 V headroom (read) | ≈ 55–60 dB | ≈ 55–60 dB |
| Ripple at the amplifier, 33 mVpp in, 1 V headroom | ≈ 10 µVpp | ≈ 15 µVpp |
| Same, 0.5 V headroom | ≈ 33–59 µVpp | ≈ 33–59 µVpp |

The residue sits at 1.25–1.5 MHz, outside the audio band, before the OPA1622's own supply rejection. The power tree's 20 mVpp assumption (§4.2) holds at 275 mA. Layout can cost more than 30 dB at 1 MHz (LT3045 p. 18–19), so this rests on following the demo-board layout. In power-save mode (PSP/PSN high) the bursts can fall in band; this note does not change the power tree's analysis of that case.

## 5. Follow-up: −7 V from an inverting buck-boost, paired LDOs

The lead chose §2.5 (b): keep the full ADR 0012 output. The TPS62903 candidate is dropped: SLVSES3A does not describe inverting use, and its 17 V input rating leaves no margin (§5.1). Requirements for the replacement:

- fed from VSYS, 6.0–8.8 V, up to ≈ 9.9 V at the charger's overvoltage limit (lead's figure);
- an inverting buck-boost that TI or ADI documents;
- **≥ 20 % margin** on the switch current at the 433 mA peak and at the chosen LDO current-limit case;
- **≥ 20 % margin** on VIN − VOUT against its maximum rating.

The +7 V pre-rail stays on the TPS65131 boost.

### 5.1 Candidates

In an inverting buck-boost (IBB) the IC's ground is the −7 V rail, so its VIN pin sees VSYS + |VOUT|: up to 9.9 + 7.24 = **17.1 V** with the output at +2.5 % tolerance (SNVA856B §4.1). The average inductor current is IOUT × (1 + |VOUT| / (VIN × η)), largest at the lowest VIN (SNVA856B Eq. 4–6).

| Part | Input rating (recommended / absolute) | VIN − VOUT use | Switch limits (min) | Inverting use documented by TI | Verdict |
|---|---|---|---|---|---|
| TPS62903 (SLVSES3A) | 17 / 18 V | 101 % / 95 % | HS 4.0 A | Not in SLVSES3A | Rejected: voltage |
| TPS62913 | 17 V (product page) | ≈ 100 % | — | Yes (TPS62913-IBB-EVM) | Rejected: voltage |
| **LMR33630C (SNVSAN3F)** | **36 / 38 V** | **48 % / 45 %** | **HS 3.85 A, valley 2.9 A** | **Yes:** SNVA856B worked example; TI "Inverting and Non-Inverting" transient models (SNVMBF9, SNVMBH1, SNVMBG5) | **Chosen** |
| LMR33620C | 36 / 38 V | 48 % / 45 % | HS 2.9 A, valley 1.95 A (SNVA856B §4.2) | Yes: same models family, SNVA856B | Pin-compatible fallback (§5.2) |
| LMR51430, LMR51420 | 36 V (product page) | ≈ 48 % | not read (3 A / 2 A parts) | No inverting model on the product page | Not evaluated (**UNVERIFIED**) |
| LMR36506 | 65 V (product page) | ≈ 26 % | 0.6 A part (product page); limits not read | Buck models only | Rejected: the 1.9 A inductor current of §5.2 is beyond a 0.6 A part (est.) |

The LMR33630 comes in three frequency versions. **C (2.1 MHz, 1.8–2.4 MHz)** is chosen: its beat with the TPS65131 (1.25–1.5 MHz) stays at or above 0.3 MHz. The B version (1.2–1.6 MHz) overlaps the TPS65131 range, so its beat could land in the audio band.

Stock (FindChips, 2026-10-22, authorized distributors):

- LMR33630CRNXR: Mouser 2,748, plus 885 of LMR33630CRNXT;
- LMR33630BRNXR: Arrow 2,750, Mouser 1,008;
- LMR33630CDDAR: Mouser 94 (DDA package);
- LMR33620CRNXR: Mouser 33,872.

Win Source and Vyrian also list stock; they are not authorized.

### 5.2 LMR33630C design and simulation

Circuit (`lmr33630-ibb.cir`, after SNVA856B Figure 3-1 and §5):

- VIN to VSYS; AGND and PGND to −7 V; inductor from SW to system ground;
- feedback 100 kΩ (ground to FB) / 16.5 kΩ (FB to −7 V): VOUT = −1.0 V × (1 + 100/16.5) = **−7.06 V** (VFB 0.985–1.015 V, SNVSAN3F §7.5); 22 pF feed-forward;
- 2 × 10 µF from VIN to −7 V and 4.7 µF from VIN to ground;
- output 3 × 22 µF 16 V X7R (≈ 30 µF effective at 7 V, est.); BOOT 100 nF; VCC 1 µF.
- **Inductor: Coilcraft XGL4020-222ME:** 2.2 µH ±20 %, 21.5 mΩ maximum, Isat 2.7 / 4.4 / 6.2 A at 10 / 20 / 30 % drop (Doc 1529).
  - Its 30 % point is above the 5.05 A maximum high-side limit, so a fault saturates it softly (BOM D31 lesson).
  - Same land as the BOM's XGL4020-102ME.
  - Authorized stock: not shown by FindChips (only Vyrian, a broker): **UNVERIFIED**. The XAL4020-222ME (5.6 A, 38.7 mΩ) is a same-land alternative.

Model: TI's unencrypted LMR33630C transient model (SNVMBG5), run with `FASTSS = 1`, which shortens the soft start to 0.8 ms (model note). ngspice needed `gmin = 1e-10` to find the operating point. Results at **VSYS = 6.0 V**, the highest-current corner:

| Case | Load on −7 V | Inductor peak (% of 3.85 A HS min) | Inductor valley (% of 2.9 A valley min) | −7 V range | Input power / efficiency |
|---|---|---|---|---|---|
| ADR 0012 full-scale sine, 1 kHz | 33 mA + 400 mA × \|sin\| (peak 433 mA) | **1.80 A, 47 %** | ≈ 0.7 A (est.) | −7.048 to −7.147 V | 2.12 W avg |
| LDO current-limit case | 0.78 A DC (covers both §5.3 options) | **2.13 A, 55 %** | **1.39 A, 48 %** | −7.060 to −7.066 V (**6 mVpp** ripple) | 5.89 W in, 5.51 W out: 94 % (model; real losses higher, est.) |

- **SNVA856B Eq. 6 cross-check** (η 0.85, L −20 %, fs 1.8 MHz minimum): 1.58 A peak at 433 mA, 2.22 A at 0.70 A, 2.4 A at 0.78 A (63 %).
  - At VSYS 9.9 V the average current is lower (× 1.84 instead of × 2.38) and the ripple higher (1.4 A pp). The peak at 0.78 A is ≈ 2.1 A.
  - Every case is ≤ 63 % of the high-side minimum, ≤ 55 % of the valley minimum, and ≤ 48 % of the voltage rating: **≥ 20 % margin everywhere**.
- **LMR33620C as a fallback** (same package and pins), by Eq. 6 at 0.78 A: 2.4 A = 83 % of its 2.9 A high-side minimum, and ≈ 1.5 A = 77 % of its 1.95 A valley minimum.
  - It passes the ≤ 100 % limiter rule. At the 433–530 mA audio peak it runs at 54–63 %.
  - It is a second source, not the primary choice.
- **Light load:** the LMR33630 enters PFM. In the model the −7 V rail then sits at −7.157 V (+1.4 %) at 10 mA.
  - The real idle load (amplifier quiescent plus LDO ground current, ≈ 25–30 mA) may still be in PFM. The burst frequency may then fall in the audio band (**UNVERIFIED**).
  - The LDOs reject ≥ 100 dB at 1 kHz (LT3045 G41, LT3094 G43), so a 10 mV burst ripple becomes ≈ 0.1 µV.
- **Right-half-plane zero** (SNVA856B Eq. 7): 285 kHz at 6.0 V and 0.7 A, above the converter's internal-compensation crossover. The load-step response in the model settles without ringing: 0.11 V dip from the PFM level at the step.
- **Thermal:** not modelled; at 0.78 A the converter loss is ≈ 0.4–0.9 W (model to Eq. 6 with η 0.85, est.). The full-scale soak of open point 4 covers it.

### 5.3 LDO current limits and pairing

- **Design peak per rail at the LDO outputs.** SBOS727B Table 2 puts the clip point at ≈ 109 mA per half (16 Ω, ±5 V), so 218 mA per leg. Two channels in phase give 436 mA, plus 20.8 mA quiescent: **457 mA**. ADR 0012's 200 mA per leg gives 421 mA. The TI model gives ≈ 510 mA, an upper bound (§3.1).
- **One LT3045 / LT3094 per rail cannot be compliant.** To pass 457 mA with 20 % margin, the minimum limit must be ≥ 548 mA, above the 500 mA rating. The 500 mA point (300 Ω / 7.5 kΩ) gives 450–550 / 450–560 mA. Its minimum misses the peak, and its maximum is 110–112 % of the rating.
- **Two of each in parallel.** Both datasheets describe direct paralleling (LT3045 Rev. D p. 21, Figure 7; LT3094 Rev. B p. 25, Figure 15):
  - SET pins tied: RSET 2 × 60.4 kΩ in parallel (200 µA × 30.2 kΩ = 6.04 V);
  - CSET 2 × 0.47 µF (tSS ≈ 2.3 × 30.2 kΩ × 0.94 µF ≈ 65 ms, unchanged and equal on both rails);
  - IN pins tied; each OUT through a 20 mΩ PCB-trace ballast (better than 20 % sharing at full load, per both datasheets);
  - noise falls by √2.
- **The limit is set by the TPS65131 boost, not by the LDOs.** The positive pair's maximum trip must keep the boost at or below 100 % of 1.8 A. The worst stack at 3.7 V reaches that at ≈ 0.655 A (`tps65131-dc-load.cir` at 0.60–0.75 A: 90 / 99 / 108 / 118 %; typical stack 82 / 90 / 97 / 105 %).

| | Positive (2 × LT3045) | Negative (2 × LT3094) |
|---|---|---|
| RILIM per device | **523 Ω** (Yageo RC0603FR-07523RL class, 1 %) | **13.0 kΩ** (1 %) |
| Limit per device, nominal (min–max, est. spread) | 150 / 0.523 = 287 mA (258–315, ±10 %) | 3.75 / 13.0 = 288 mA (260–323, −10 / +12 %) |
| Pair limit | **516–631 mA** | **519–646 mA** |
| Margin over the 457 mA design peak / 421 mA ADR peak / 510 mA model | +13 % / +23 % / +1 % | +14 % / +23 % / +2 % |
| Converter load at the maximum trip (+ 2 × IGND ≈ 18 mA) | 0.65 A: TPS65131 boost **≈ 99 %** worst stack, ≈ 90 % typical (≤ 100 % rule: pass at its edge) | 0.66 A: LMR33630 ≈ 52 % (sim at 0.78 A: 55 %) |
| Per-device continuous load (330 mA average / 2, model) | 165 mA = 33 % of 500 mA | 165 mA = 33 % |
| Per-device maximum trip | 315 mA = 63 % of 500 mA | 323 mA = 65 % |

- **What protects what.** The OPA1622s protect themselves (output current limit, thermal shutdown at 175 °C, SBOS727B §7.3.2). The LDO limits protect the pre-rail converters and the LDOs.
- **The negative side alone** could take 11.0 kΩ (614–764 mA pair, +34 % over 457 mA; LMR33630 ≈ 63 %). Symmetric limits keep any overload clipping symmetric, so 13.0 kΩ is proposed.
- **Higher positive margin needs a stronger +7 V source.** The TPS65131 boost is now the binding part. One example is a buck-boost from VSYS, since VSYS crosses 7 V; it is not evaluated here.

### 5.4 Pre-rail voltages and dropout, both sides

Each device in a pair carries at most ≈ 0.31 A at the peak, assuming 60 / 40 sharing of 0.52 A. Full-range maximum dropout at that current: LT3045 ≤ 350 mV (300 mA point); LT3094 ≈ 350 mV (interpolated, 280 mV at 100 mA to 410 mV at 500 mA).

| | Positive (TPS65131 boost, +6.975 V) | Negative (LMR33630, −7.06 V) |
|---|---|---|
| Pre-rail minimum magnitude, DC | 6.77 V (3 % accuracy, SLVS493E) | 6.84 V (VFB −1.5 %, 1 % resistors) |
| Dip below setpoint at the signal peak (sim, 1 kHz) | 0.09 V (worst stack, §2.4) | 0.012 V (TI model) |
| Ballast drop at 0.31 A | 6 mV | 6 mV |
| LDO output maximum | 6.17 V | 6.17 V |
| **Headroom at the peak, worst corner** | **0.50 V** | **0.65 V** |
| Margin over maximum dropout | +0.15 V | +0.30 V |

The −7.3 V pre-rail is not needed: with the LMR33630's 1.5 % reference and the halved per-device current, the negative corner moves from 0.40 V against 0.38 V (§4.1) to 0.65 V against 0.35 V. The positive side stays at +6.975 V. Raising it would add boost current at its binding limit.

LDO dissipation per device at the 330 mA average model load: 0.165 A × 0.94–1.27 V + 7 V × ≈ 6 mA ≈ 0.20–0.25 W, +7 to +9 °C at 34 °C/W. Ripple rejection at 1.8–2.4 MHz: ≈ 72 dB (LT3045, G45) and ≈ 68 dB (LT3094, G47) at 1 V headroom. The simulated 6 mVpp becomes ≈ 2 µVpp.

### 5.5 Start-up, sequencing and the unused inverter

- **Order:**
  1. `HPA_RAIL_EN` enables the TPS65131 boost (ENP) and the LMR33630, through a level shifter to its EN. EN is referenced to the −7 V IC ground (SNVA856B §7.1, Figure 7-1; EN may go to VIN + 0.3 V, SNVSAN3F §7.1).
  2. The LDOs (`HPA_LDO_EN`) follow after both pre-rails settle.
  3. The OPA1622 EN comes last (power tree §6.2).
- **Timing:**
  - TPS65131: the current limit ramps in ≈ 1 ms (SLVS493E §7.3.5).
  - LMR33630 internal soft start: 2.9–6 ms (SNVSAN3F §7.5).
  - A fixed delay of **≥ 10 ms** from `HPA_RAIL_EN` to `HPA_LDO_EN` covers both. The LMR33630 PG flag is referenced to −7 V and would need its own level shifter.
- **Simulated start-up** (TI model, shortened soft start): −7 V reaches 90 % at 0.15 ms after soft start begins. It peaks at −7.166 V, 0.1 % beyond its no-load level; no overshoot toward the +5 % range.
  - The pre-rails ramp at different times. That is harmless: the LDOs are off, so the amplifier rails stay at 0 V.
  - The ±6 V ramp symmetry still comes only from the matched LDO soft starts (§4.2, unchanged with paired SET networks).
- **TPS65131 inverter half, unused:**
  - tie ENN and PSN to GND: the inverter's PMOS stays off and no DC path remains (SLVS493E §7.3.4);
  - keep INN on VIN with its input capacitor, within its ratings;
  - tie VNEG and FBN to AGND; leave OUTN open; leave out L2, D2, the output capacitors, R3/R4, C10 and CN (or keep CN as specified).
  - SLVS493E gives no single-output connection, so this is **UNVERIFIED**: confirm with TI (E2E) before layout.
  - The BOM loses one DFE252012F-4R7M, one PMEG2010AEH and 4 × 4.7 µF. It gains the LMR33630C, XGL4020-222ME, ≈ 7 capacitors, the level shifter, and one more LT3045 and LT3094 with their passives.

## 6. Open points

1. **Adopt §5** (LMR33630C IBB, paired LDOs, RILIM 523 Ω / 13.0 kΩ): the maintainers' decision, then BOM and power-tree updates by the lead. Confirm the TPS65131 single-output connection with TI, and the XGL4020-222ME authorized stock.
2. **Re-run this study on the chosen design.** Use TI's model where one exists. Measure the TPS65131 (or its replacement) at 3.7 V, −7 V and a 433–510 mA rectified-sine load on the first board.
3. **LDO RILIM spread** at 523 Ω and 13.0 kΩ is not tabulated (±10 % / −10 to +12 % assumed); the positive pair's maximum trip sets the TPS65131 boost at ≈ 99 % worst stack, so measure the boost at 0.65 A, 3.7 V on the first board.
4. **Measure the paralleled halves:** sharing, THD+N at 16 and 32 Ω, output impedance and a full-scale soak.
5. **TPS62136 droop** at the ≈ 2 A load steps of a full-scale sine (not simulated here; ADI/TI model or bench).
6. **Output capacitor DC bias:** the effective value of 4 × 4.7 µF 25 V X7R at 7 V sets the ripple of §4.4.
7. **LMR33630 in PFM at idle:** burst frequency and its residue at the amplifiers; whether a forced-PWM variant exists was not checked, so measure.

## 7. Sources

- Texas Instruments: TPS65131 SLVS493E (Apr 2022) <https://www.ti.com/lit/ds/symlink/tps65131.pdf>; OPA1622 SBOS727B (May 2016) <https://www.ti.com/lit/ds/symlink/opa1622.pdf>; TPS62136 SLVSDV2 (Mar 2017) <https://www.ti.com/lit/ds/symlink/tps62136.pdf>; TPS62903 SLVSES3A (Mar 2021) <https://www.ti.com/lit/ds/symlink/tps62903.pdf>; product pages <https://www.ti.com/product/TPS65131>, <https://www.ti.com/product/OPA1622>, <https://www.ti.com/product/TPS62903> (read 2026-10-22).
- TI simulation models: OPA1622 PSpice model SBOM958 Rev. D <https://www.ti.com/lit/zip/SBOM958> (used, not redistributed); OPA1622 TINA-TI model SBOM957 Rev. C (downloaded, not used); TPS62903 PSpice transient model SLVMDN8 <https://www.ti.com/lit/zip/SLVMDN8> (not used, for open point 1).
- Analog Devices: LT3045 Rev. D (11/22) and LT3094 Rev. B (01/20), through the LCSC mirror listed in the BOM Datasheets table (hashes match).
- Cirrus Logic: CS43198 DS1156F2, Table 3-4 (through the `libs/parts` sheet).
- Nexperia (NXP): PMEG2010AEH Rev. 03 (28 Mar 2007), <https://datasheet.lcsc.com/datasheet/pdf/0048ef3cc1cc47f2a46f601985c58027.pdf>.
- Murata: DFE252012F series sheet, <https://datasheet.lcsc.com/datasheet/pdf/5d5b9380ea91acc9a12416e10134b904.pdf>; LCSC listing C668313 (DCR 190 mΩ, Isat 2.1 A).
- TI LMR33630 SNVSAN3F (Nov 2020) <https://www.ti.com/lit/ds/symlink/lmr33630.pdf>; product page <https://www.ti.com/product/LMR33630>; application notes SNVA856B <https://www.ti.com/lit/an/snva856/snva856.pdf> and SLVA317B <https://www.ti.com/lit/an/slva317/slva317.pdf>; LMR33630C unencrypted inverting/non-inverting transient model SNVMBG5 <https://www.ti.com/lit/zip/SNVMBG5> (used, not redistributed), also SNVMBF9 (A) and SNVMBH1 (B).
- Coilcraft: XGL4020 Doc 1529 <https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf>; XAL4000 Doc 806 <https://www.coilcraft.com/getmedia/6adcb47d-8b55-416c-976e-1e22e0d2848c/xal4000.pdf>.
- Stock: FindChips, 2026-10-22: TPS62903RPJR (Mouser 2,589), LMR33630CRNXR (Mouser 2,748), LMR33630BRNXR (Arrow 2,750, Mouser 1,008), LMR33630CDDAR (Mouser 94), LMR33620CRNXR (Mouser 33,872), XGL4020-222MEC (Vyrian only, broker).
- Tools: ngspice 47 (Homebrew), XSPICE digital code models.
