# VSYS bucks and MaskROM entry: simulation

- **Date:** 2026-10-22.
- **Question:** the [BOM v1 cross-validation](2026-10-bom-v1-cross-validation.md) (§9, "No simulation") left two items for SPICE or bench work. (1) The 5 V source for HAT_5V and the USB-C source: compensation, stability, load steps, ripple and the BRD-049 current margins. The cross-validation named a TPS61088 boost; BOM v1.1 made it a TPS61089; with the 2S battery of [ADR 0014](../adr/0014-two-cell-battery.md) (BOM v1.5) it is now a **TPS62903 buck** from VSYS 6.0–8.8 V, and a **TPS62136** pre-regulator makes the 3.8 V VSYS_LV rail for the former 1S tree. Both bucks are checked here. (2) The MaskROM entry of BRD-035 / [ADR 0009](../adr/0009-bom-v1-decisions.md) (Main + Volume − held at power-on): is eMMC_D0 held low through the BootROM's eMMC attempt across tolerances, and are normal boots unaffected?
- **Inputs:**
  - [BOM v1](../specs/bom-v1.md) v1.5 lines 35, 77, 78, 91, 92, 97, 98, 113–115 and §9 D10, D18; [power tree v0](../specs/power-tree-v0.md) §3, §4.6, §6.1, §6.5;
  - [2S battery study](2026-10-battery-2s.md) §4.2, §4.4; [ADR 0014](../adr/0014-two-cell-battery.md); [ADR 0009](../adr/0009-bom-v1-decisions.md);
  - [pin plan](2026-10-pin-multiplexing-v0.md) §3.10; t1 [controls and status LED spec](https://github.com/opendap-project/t1/blob/main/docs/specs/controls-and-status-led.md) §1.2–§1.3;
  - part sheets in `libs/parts/`: TPS62903 (via BOM), TPS62136 (via BOM), TPS61089RNRR, XAL4020-152MEC, RK809-5, RK3566, TPS3839G18DBZR, SN74LVC1G57DCKR, SN74LVC1G58DCKR, BAT54, DMG1012T-7, PTS815SJM250SMTRLFS, KLMBG2JETD-B041.
- **Netlists:** [`sim/vsys-bucks/`](../../sim/vsys-bucks/README.md) and [`sim/maskrom/`](../../sim/maskrom/README.md). Every table below can be rerun from there.
- **Conventions:**
  - **UNVERIFIED** means no primary source was read in this session. **Est.** marks an engineering estimate, to be replaced by measurement (T1-026).
  - BRD-049: continuous load ≤ 80 % of a converter's rating; the worst-case trip of the protecting limiter ≤ 100 %.
  - Inductor peak currents use the minimum inductance (−20 %) and the highest input, VSYS 9.9 V (the charger OVP ceiling of the 2S study §4.2), unless stated.
  - "Dip" is the drop below the regulated (PWM) level after the load rises; "over" is the rise above it after the load falls. Settling is to ±0.5 % on the 1 µs average (ripple removed).
  - CO is the **effective** output capacitance after DC bias.
  - Nothing here edits an ADR, the BOM, the power tree or a requirement.

> **How this was gathered, and its limits.**
>
> - **Read directly:** TI TPS62903 SLVSES3A (March 2021, sha256 `323bfe65…50dcee`), TPS62136 SLVSDV2 (March 2017, `b445aeac…13a70a`, no later revision on the PDF), TPS61089 SLVSD38C (August 2021, `863eda98…ce061e0d`, same file as the BOM), TPS3839 SBVS193D (July 2015, `a1894023…072621b`), TPS3808 SBVS050N (revised August 2026, `74d889c0…d86eed`), SN74LVC1G57 SCES414P (`078364de…44af24`), SN74LVC1G58 SCES415N (`c9f14665…e8a`), Rockchip RK809 datasheet Rev 1.01 (2018-08-28, `3f9b42ed…908062f`, same file as the parts library); the TI product pages of TPS62903, TPS62136 and TPS61089 (model listings).
> - **Models:** TI's **TPS62136 PSpice Unencrypted Transient Model** (SLVMC09, "Final 1.1", 20MAR2017) runs in ngspice 47 in PSpice compatibility mode. TI's **TPS62903** models are an **encrypted** PSpice model (SLVMDN8, "Final 1.00", 09AUG2021) and a SIMPLIS model (SLVMDP3): neither runs in ngspice. The TPS62903 is therefore simulated with an **open generic DCS-Control-class model** written here, calibrated against TI's TPS62136 model (§2). The MaskROM circuit uses behavioural models built from datasheet thresholds (§5). No vendor model is in the repository.
> - **Not covered:** the RK3566 BootROM boot order and timing are not published by Rockchip (no RK3566 datasheet or TRM chapter read gives them); the RK809-5 OTP sequence is not public; the JEDEC eMMC standard (JESD84-B51) and the Samsung KLMBG2JETD datasheet (NDA) were not read. These appear as parameters with corners. The TPS61089 boost was not simulated (it left the design before results existed). Stock was not re-captured (the FindChips pages for TPS3808 parsed unreliably). The machine was shared, so runs were limited to three ngspice processes. Nothing was built or measured.

---

## 1. Summary

**TPS62903, HAT_5V / USB-C source, 5.1 V at 1.6 A (BOM line 91, generic model): margins, load steps and ripple pass; phase margin ≥ 45° is not demonstrated at low VSYS; one value to change.**

1. **BRD-049 current margins hold.** Load 1.6 A = 53 % of 3 A. Inductor peak 2.22 A at 9.9 V with L −20 % = **55 % of the 4.0 A minimum high-side limit**, 25 % of the XGL4020-102MEC 8.8 A Isat (30 % drop). Simulated step peak 2.3–2.8 A (≤ 70 %). With both eFuses at their 1.66 A ceilings the limit (4.0–5.5 A, ≤ 5.8 A with the 50 ns overshoot of Eq. 2) bounds the fault below Isat.
2. **Load step 0.1 → 1.6 A with ≈ 10 µF effective (the BOM's single 22 µF):** dip **68 mV at VSYS 8.8 V, 143 mV at 6.6 V, 167 mV at 6.0 V**; overshoot 86–123 mV; settling 9 µs (up) and 20–23 µs (down). Lowest output 4.93 V; with the −1.25 % VSET tolerance 4.87 V, above the 4.75 V USB VBUS minimum. Highest, with the model's overshoot error (up to 30 % low) and a power-save offset like the TPS62136's (+1.6 %, est.): about 5.42 V, below 5.5 V. In the calibration the generic model overstates the dip at low headroom (§2.3), so the dips are upper bounds.
3. **Ripple:** 5.5–6.9 mVpp in PWM at 1.6 A; **15–23 mVpp in power save** at 0.1 A.
4. **Loop:** the generic model gives crossover 178–197 kHz and phase margin 50–63° with 10 µF effective. Against TI's TPS62136 model the same generic model is **10–12° optimistic** (§2.3). Corrected, the TPS62903 margin is **≈ 38–40° at VSYS 6.0 V** and ≈ 51–53° at 8.8 V (10 µF), and lower with more capacitance (≈ 34–36° / 43–45° at 20 µF). **Phase margin ≥ 45° is therefore not shown at low VSYS.** The part is internally compensated: the only lever is the L–C pair, and TI lists 1 µH with 10–100 µF nominal as stable (SLVSES3A Table 8-3). Closure needs TI's SIMPLIS model (SLVMDP3, does not run in ngspice) or a bench Bode plot (§6).
5. **Recommended: keep one 22 µF, but a part with ≥ 12 µF effective at 5.1 V** (est. a 1206, 25 V X7R). A 22 µF 0805 sits at the 10 µF effective minimum of SLVSES3A §6.3 at 5.1 V bias (est.). Two 22 µF (≈ 20 µF) cut the dip to 50–128 mV and halve the PWM ripple (3.0–3.4 mVpp), but lower the model's phase margin by 4–8°; keep that option until the bench Bode plot.

**TPS62136, VSYS_LV 3.8 V pre-regulator at 2.0 A peak (BOM line 113, TI's model): pass; one BOM figure to correct.**

1. **Load step 0.1 → 2.0 A (TI model, 30 µF effective):** in auto PFM/PWM (the BOM setting) VSYS_LV stays within **3.788–3.883 V** (light-load level 3.855–3.861 V, +1.6 %; dip to 3.79 V; back to the light-load level plus 10–22 mV); settling 9–20 µs. In forced PWM: dip 42 mV, overshoot 57–58 mV, settling 8 µs. That band is inside the input range of every part on VSYS_LV (the MCLK LDO needs ≥ 3.4 V; the RK860-0 sits inside the 3.5–4.4 V the T1 uses for it).
2. **Loop (TI model):** crossover **232–234 kHz, phase margin 49° at VSYS 6.0 V and 54° at 8.8 V** (1.6 A, 30 µF effective). **Pass** (≥ 45°). The internal 15 pF feed-forward with 442 kΩ / 100 kΩ puts its zero at 24 kHz and its pole at 130 kHz; no external capacitor is needed.
3. **The BOM's inductor ripple figure (line 114) is low by 2.5×.** SLVSDV2 Eq. 10 uses 100 ns; the on-time of Eq. 1 (250 ns × VIN / (VIN − VOUT)) gives ΔIL = 250 ns × VIN / L, and TI's model agrees (§4.2). Peak at 2.0 A, 9.9 V, L −20 %: **3.03 A, not 2.41 A** = 63 % of the 4.8 A minimum limit and 40 % of the 7.5 A Isat (30 % drop). Still compliant.
4. **Power save covers most of playback.** The PFM boundary is ΔIL / 2 = 0.5–0.8 A, so VSYS_LV runs in power save at typical playback loads, with 15–22 mVpp ripple and a load-dependent burst frequency. VSYS_LV reaches the DAC_VP switch (line 50) unregulated; the CS43198 VP rejection of that ripple is **UNVERIFIED** and is a bench item (forced PWM, MODE high, is the fallback at a few mA of quiescent cost).
5. **Start-up:** VSYS_LV is up ≤ 0.45 ms after VSYS (200–300 µs delay + 150 µs ramp, SS/TR open) and vcc3v3_sys ≤ 1.25 ms later (TPS62826). Both are always on, so they come up at battery attach, long before any PWRON press: they do not enter the MaskROM timing.

**MaskROM entry (BOM lines 35, 78, 97, 98): two holes in the circuit as designed; fix with values in §5.6.**

1. **Normal boot is not affected.** With Main only (or Main + Volume +), eMMC_D0 is never forced (simulated, all corners).
2. **Hole 1: the window is too short to be guaranteed.** As designed, D0 is held low until **110–340 ms after RESETB** (TPS3839 td 120–350 ms from vcc_1v8). The BootROM's eMMC attempt has no published timing, and an eMMC may take up to 1 s to initialise after CMD1 (JEDEC limit, **UNVERIFIED** here) before the first D0-dependent step. The BOM's own condition ("the BootROM must sample eMMC_D0 before 120 ms") cannot be shown.
3. **Hole 2: the window reopens at every resume.** vcc_1v8 is off in suspend (power tree §3). The TPS3839 senses it, so each resume reopens the window: waking with Main while Volume − is held (the screenshot / power-menu combination, controls spec §1.3) forces **D0 low for 120–350 ms during resume** (simulated), which can corrupt eMMC traffic.
4. **The D0 tap costs HS200 margin.** With the FET off, 100 Ω plus the FET output capacitance (25 pF assumed at low VDS) removes about **0.18 V of both the high and the low margin** at mid-bit at 200 MHz (est. interconnect). 1 kΩ costs ≤ 0.04 V and still holds D0 at ≤ 0.32 V against a 4.7 kΩ pull-up (VIL 0.63 V).
5. **Levels hold, with thin margin at cold.** The pressed PWRON_N level through the BAT54 is 307 mV at −20 °C with the 20 kΩ pull-up, against the 350 mV VT− minimum (43 mV margin); 100 kΩ gives 261 mV (89 mV). The PWRON idle-voltage concern of BOM line 78 is closed: In2 stays above VT+ max for any VCC_RTC ≥ 0.6 V, below the RK809's own 1.26 V VIH.
6. **Fix (§5.6):** window supervisor **TPS3839G18 on vcc_1v8 → TPS3808G01 on vcca1v8_pmu** (SENSE divider 280 kΩ / 100 kΩ, 1.54 V; **CT 390 nF** → td 1.21–3.43 s; RESET pull-up 100 kΩ); PWRON_N pull-up **20 kΩ → 100 kΩ**; D0 series resistor **100 Ω → 1 kΩ** at the D0 trace; optional 100 kΩ gate pull-down on the DMG1012T. Simulated: D0 held 1.20–3.42 s after RESETB, nothing at resume, normal boot untouched.

---

## 2. Models and calibration

### 2.1 TI TPS62136 transient model

SLVMC09 is a behavioural PSpice model (DCS-Control loop, AEE on-time, soft start, HICCUP current limit, power save, 15 pF internal feed-forward capacitor). It runs unchanged in ngspice 47 with `ngbehavior=psa`. Its on-time matches SLVSDV2 Eq. 1: at VIN 8.8 V the simulated inductor ripple at 1.5 µH is 1.47 A, against 250 ns × 8.8 V / 1.5 µH = 1.47 A.

### 2.2 Generic model (TPS62903)

`dcs-buck-generic.lib` is written for this study: constant on-time from the datasheet equation, a ripple-emulation ramp from (V<sub>SW</sub> − V<sub>OS</sub>), a valley comparator, a slow integrator for DC accuracy (clamped to ±20 mV), an on-time extension when the error is large, minimum off-time, high-side peak and low-side valley limits, and power save (low side off at zero current). Power-stage values come from the datasheets. Four constants are not published by TI and were set by calibration against TI's TPS62136 model with TPS62136 parameters: ripple gain KR = 0.02, ramp time constant 2 µs, integrator 2·10⁴ s⁻¹, on-time extension threshold 5 mV. The same constants are used for the TPS62903, with its own on-time (SLVSES3A Eq. 5, 100 ns × VIN / (VIN − VOUT), AEE at 2.5 MHz), switches (62 / 22 mΩ typ, 111 mΩ max high side) and limits (4.0 / 4.6 / 5.5 A high side, 4.4 A low side). Whether TI's TPS62903 loop uses the same internal constants as the TPS62136 is **UNVERIFIED**: the generic results for the TPS62903 are indicative, and the decisive stability statement is TI's L–C table.

### 2.3 Calibration: generic against TI, TPS62136 values

Load step 0.1 → 2.0 A, L 1.5 µH, 30 µF effective, 14.3 mΩ DCR (`run.py check` and `run.py step136`). Dip and overshoot are against the PWM level (3.794 V); "LL level" is the light-load (0.1 A) output.

| Case | Model | LL level (V) | Lowest (V) | Highest (V) | Dip / over (mV) | Ripple 0.1 A / 2.0 A (mVpp) | Settle up / down (µs) | IL peak / steady (A) |
|---|---|---|---|---|---|---|---|---|
| 7.4 V, forced PWM | TI | 3.794 | 3.752 | 3.851 | 42 / 57 | 5.5 / 5.0 | 8.3 / 8.2 | 2.79 / 2.60 |
| | generic | 3.794 | 3.755 | 3.834 | 39 / 40 | 5.7 / 5.2 | 8.9 / 8.8 | 2.67 / 2.58 |
| 8.8 V, forced PWM | TI | 3.794 | 3.752 | 3.852 | 42 / 58 | 6.7 / 6.1 | 8.3 / 8.2 | 2.89 / 2.73 |
| | generic | 3.794 | 3.756 | 3.847 | 38 / 53 | 6.9 / 6.1 | 8.8 / 9.3 | 2.79 / 2.70 |
| 6.0 V, auto PFM | TI | 3.855 | 3.790 | 3.865 | 4 / 71 | 15.0 / 4.3 | 9.2 / 1.5 | 2.74 / 2.48 |
| | generic | 3.792 | 3.751 | 3.842 | 43 / 48 | 16.5 / 4.4 | 7.2 / 11.4 | 2.79 / 2.45 |
| 8.8 V, auto PFM | TI | 3.861 | 3.788 | 3.883 | 7 / 89 | 22.5 / 6.1 | 20.1 / 29.3 | 2.78 / 2.72 |
| | generic | 3.790 | 3.768 | 3.845 | 26 / 51 | 23.8 / 6.2 | 28.7 / 62.5 | 2.84 / 2.70 |
| 4.6 V (0.8 V headroom), auto PFM | TI | 3.857 | 3.779 | 3.892 | 15 / 99 | 17.5 / 9.7 | 19.1 / 33.2 | 2.79 / 2.45 |
| | generic | 3.792 | 3.670 | 3.868 | 124 / 74 | 17.3 / 4.2 | 14.7 / 19.5 | 2.88 / 2.28 |

| Loop, 1.6 A, forced PWM | TI crossover / phase margin | Generic crossover / phase margin |
|---|---|---|
| 6.0 V | 232 kHz / 49° | 259 kHz / 59° |
| 8.8 V | 234 kHz / 54° | 268 kHz / 66° |

What the comparison shows:

- In PWM the generic model reproduces TI's dip (within 10 %), ripple (5 %), settling (10 %) and inductor peak (5 %). It **under-reads the overshoot by up to 30 %**.
- TI's model regulates **1.6–1.8 % high in power save**; the generic model regulates at the set point. Highest voltages from the generic model must add that offset.
- At low headroom the generic model **overstates the dip**: from the light-load level, 122 mV against TI's 78 mV at 0.8 V headroom.
- In the loop, the generic model's crossover is 12–15 % high and its **phase margin 10–12° optimistic**. The loop-gain magnitudes agree within about 1 dB below 100 kHz. Both models show the same shape: gain above 0 dB through the L–C resonance, where the phase swings through ±180°.
- So the generic model is used for the TPS62903 with three corrections stated where they apply: overshoot +30 %, a power-save offset, and phase margin −10 to −12°.

---

## 3. TPS62903 5.1 V buck (HAT_5V and USB-C source)

### 3.1 Design values against the datasheet

| Item | BOM v1.5 (line 91–92, 115) | SLVSES3A | Check |
|---|---|---|---|
| Input | VSYS 6.0–8.8 V (OVP ≈ 9.9 V) | 3–17 V (§6.3) | OK |
| Output | VSET 95.3 kΩ → 5.1 V | Table 7-2; ±1.25 % over −40–150 °C (§6.5) | 5.036–5.164 V |
| Mode | S-CONF 26.1 kΩ: VSET, 2.5 MHz, auto PFM/PWM with AEE, discharge on | Table 7-1 | OK |
| Frequency (AEE) | — | Eq. 4: 10 × VOUT × (VIN − VOUT) / VIN² MHz | 1.28 MHz at 6.0 V, 1.76 at 6.6, 2.44 at 8.8, 2.50 at 9.9 V |
| Minimum off-time | — | 80 ns typ (§7.4.4) | With the Eq. 5 on-time, t<sub>OFF</sub> = 100 ns × VIN / VOUT ≥ 100 ns (118 ns at 6.0 V): not reached in steady state |
| Inductor | XGL4020-102MEC, 1.0 µH | Nominal 1 µH, in Table 8-4 | OK |
| COUT | 22 µF, "≥ 10 µF effective" | 10–100 µF effective at 2.5 MHz (§6.3); Table 8-3 pairs 1 µH with 10–100 µF nominal | **Marginal**: a 22 µF 0805 at 5.1 V is ≈ 9–12 µF (est.) |
| Feedback / feed-forward | VSET (internal divider) | No external divider, so no external feed-forward; the 3 pF internal capacitor of Eq. 17–18 applies to the external-divider mode only | Nothing to set |

Compensation: the TPS62903 is internally compensated (DCS-Control, SLVSES3A §8.2.2.7); the only design freedoms are the L–C pair (Table 8-3) and, in external-divider mode, a feed-forward capacitor. With VSET there is nothing to compute beyond the L–C corner: f<sub>LC</sub> = 1 / (2π √(1 µH × 10 µF)) = 50 kHz (10 µF) or 36 kHz (20 µF).

### 3.2 Load steps (generic model)

0.1 → 1.6 → 0.1 A, 1 A/µs, auto PFM/PWM (`run.py step903`).

| VSYS | CO eff. | Dip (mV) | Lowest (V) | Over (mV) | Settle up / down (µs) | Ripple at 0.1 A / 1.6 A (mVpp) | IL peak in step / steady (A) |
|---|---|---|---|---|---|---|---|
| 6.0 V | 10 µF | 167 | 4.933 | 123 | 9 / 20 | 18.4 / 6.9 | 2.56 / 1.87 |
| 6.6 V | 10 µF | 143 | 4.957 | 108 | 9 / 20 | 15.5 / 5.8 | 2.78 / 1.91 |
| 8.8 V | 10 µF | 68 | 5.032 | 86 | 9 / 23 | 16.1 / 5.5 | 2.34 / 2.03 |
| 6.0 V | 20 µF | 128 | 4.972 | 96 | 15 / 45 | 17.1 / 3.4 | 2.69 / 1.87 |
| 6.6 V | 20 µF | 82 | 5.018 | 87 | 12 / 34 | 15.2 / 3.0 | 2.62 / 1.91 |
| 8.8 V | 20 µF | 50 | 5.051 | 77 | 13 / 43 | 16.4 / 3.3 | 2.47 / 2.03 |
| 6.0 V, L −20 %, RDS(on) and limit worst | 10 µF | 143 | 4.957 | 123 | 8 / 16 | 22.9 / 7.2 | 2.39 / 1.90 |
| 8.8 V, L −20 % | 10 µF | 53 | 5.047 | 80 | 3 / 23 | 18.7 / 6.6 | 2.39 / 2.14 |
| 7.4 V, forced PWM | 10 µF | 121 | 4.979 | 101 | 5 / 5 | 5.6 / 5.2 | 2.53 / 1.96 |

- The dip grows as VSYS falls because the headroom (VIN − VOUT) sets the inductor slew. At 6.0 V the generic model is pessimistic: at a comparable headroom (TPS62136 at 4.6 V in, 0.8 V headroom) it dips 1.6× more than TI's model from the light-load level (§2.3).
- The generic model under-reads overshoot by up to 30 % and does not model the power-save offset (§2.3).
- USB VBUS, lowest: 4.93 V; with the −1.25 % VSET tolerance, 4.87 V, above the 4.75 V minimum. Highest: 5.164 V (VSET +1.25 %) + 0.08 V (power-save offset, est. from the TPS62136's +1.6 %) + 0.16 V (123 mV overshoot +30 %) ≈ 5.42 V, below 5.5 V. The USB VBUS limits are **UNVERIFIED** in this session (USB specifications not read).

### 3.3 Loop gain (generic model)

Voltage injection in the sense path, 1.6 A, forced PWM (`run.py loop903`).

| VSYS | CO eff. | Crossover (model) | Phase margin (model) | Corrected by the §2.3 offset (est.) |
|---|---|---|---|---|
| 6.0 V | 10 µF | 178 kHz | 50° | ≈ 38–40° |
| 8.8 V | 10 µF | 197 kHz | 63° | ≈ 51–53° |
| 6.0 V | 20 µF | 103 kHz | 46° | ≈ 34–36° |
| 8.8 V | 20 µF | 114 kHz | 55° | ≈ 43–45° |

- Below the crossover the gain stays above 0 dB through the L–C resonance (36–50 kHz), where the phase swings through ±180°: the loop is conditionally stable in the model, as is usual for ripple-based control. TI's model of the TPS62136 shows the same shape (§2.3).
- Gain margin above crossover was not measured (the method loses accuracy near fSW / 5).
- The same model is 10–12° optimistic against TI's TPS62136 model (§2.3). Corrected: **≈ 38–40° at 6.0 V and ≈ 51–53° at 8.8 V with 10 µF; ≈ 34–36° and ≈ 43–45° with 20 µF.** At VSYS 6.0 V the corrected margin is below 45° with either capacitance. The correction is transferred from another part of the same family, so these figures are estimates.
- **Not demonstrated** against ≥ 45° at low VSYS. TI lists 1 µH with 10–100 µF nominal as stable pairs for its internal compensation (Table 8-3); TI's SIMPLIS model (SLVMDP3) or a bench Bode plot at VSYS 6.0 V and 1.6 A is the closure. More output capacitance lowers the margin in the model, so the capacitance should not grow beyond what the 10 µF minimum needs until then.

### 3.4 BRD-049 current margins

| Item | Rating (SLVSES3A, Coilcraft Doc 1529 via BOM) | Load | Use | Verdict |
|---|---|---|---|---|
| Converter output | 3 A | 1.6 A | 53 % | OK |
| Inductor ripple, 9.9 V, L −20 % | — | ΔIL = (VIN − VOUT) × T<sub>ON</sub> / L = 100 ns × VIN / L = 1.24 A (Eq. 5; Eq. 12 at 2.5 MHz gives the same within 3 %) | — | — |
| Peak switch current, 1.6 A | High-side limit 4.0 A min | 1.6 + 0.62 = 2.22 A | **55 %** | OK |
| Peak in a 0.1 → 1.6 A step (sim.) | 4.0 A min | 2.34–2.78 A | 59–70 % | OK |
| Inductor saturation | 8.8 A (30 % drop), 6.3 A (20 %) | 2.22 A | 25 % / 35 % | OK |
| Fault: both eFuses at 1.66 A | Limit 4.0–5.5 A; + (VIN − VOUT) / L × 50 ns = 0.30 A (Eq. 2) | ≤ 5.8 A | 66 % of Isat (30 %) | Bounded by the limit |
| Thermal | RθJA 73.5 °C/W (EVM) | ≈ 0.6 W (η 0.93, est., 2S study) | ≈ +44 °C (est.) | Board thermal model |

### 3.5 Recommendation

- **COUT: one 22 µF with ≥ 12 µF effective at 5.1 V** (est. a 1206, 25 V X7R; confirm on the maker's DC-bias curve). A 22 µF 0805 sits at the 10 µF effective minimum of SLVSES3A §6.3 at 5.1 V (est.). The eFuse input capacitors downstream add to it; the total at the output pins stays far below 100 µF.
- Two 22 µF (≈ 20 µF) give the lower dip and ripple of §3.2 at 4–8° less modelled phase margin: an option after the bench Bode plot, not before.
- Keep auto PFM/PWM with AEE (26.1 kΩ). If an audio HAT is sensitive to the 15–23 mVpp power-save ripple on HAT_5V, the forced-PWM setting with the same VSET and frequency is 32.4 kΩ (Table 7-1, #10); that choice is for the maintainers, after a measurement.

---

## 4. TPS62136 3.8 V pre-regulator (VSYS_LV)

### 4.1 Design values against the datasheet

| Item | BOM v1.5 (lines 113–115) | SLVSDV2 | Check |
|---|---|---|---|
| Input | VSYS 6.0–8.8 V (OVP ≈ 9.9 V) | 3–17 V | OK |
| Output | R1 / R2 = 442 kΩ / 100 kΩ → 3.794 V | VFB 0.7 V ±1 % (PWM), −1 / +2 % (PFM, CO,eff ≥ 47 µF) | 3.76–3.83 V in PWM; TI's model sits at 3.855–3.861 V in PFM at 0.1 A (+1.6–1.8 %) |
| Feed-forward | internal 15 pF | Eq. 14–15 | f<sub>zero</sub> = 1 / (2π × 442 kΩ × 15 pF) = **24.0 kHz**, f<sub>pole</sub> = (1 / 442 k + 1 / 100 k) / (2π × 15 pF) = **130 kHz**: zero below and pole near the crossover; no external capacitor needed |
| On-time, frequency | — | Eq. 1: 250 ns × VIN / (VIN − VOUT) | 680 ns / 0.93 MHz at 6.0 V; 440 ns / 0.98 MHz at 8.8 V |
| Inductor | XGL4020-152MEC, 1.5 µH | 0.7–2.9 µH effective; 1.5 µH nominal | OK |
| COUT | 2 × 22 µF 16 V | 12–200 µF effective; Table 2 standard 1.5 µH / 47 µF nominal | OK (≈ 25–30 µF effective, est.); downstream input capacitors add more |
| L–C corner | — | f<sub>LC</sub> = 1 / (2π √(1.5 µH × 30 µF)) | 24 kHz |

### 4.2 Inductor ripple: SLVSDV2 Eq. 10 against Eq. 1

Eq. 10 writes ΔIL(max) = VIN(max) / L(min) × 100 ns. From the on-time of Eq. 1, ΔIL = (VIN − VOUT) × T<sub>ON</sub> / L = **250 ns × VIN / L**. TI's model gives 1.47 A at 8.8 V and 1.5 µH, which matches 250 ns, not 100 ns (0.59 A). This note uses 250 ns:

| VSYS | ΔIL, 1.5 µH | ΔIL, 1.2 µH (−20 %) | Peak at 2.0 A, 1.2 µH | PFM boundary (ΔIL / 2, 1.5 µH) |
|---|---|---|---|---|
| 6.0 V | 1.00 A | 1.25 A | 2.63 A | 0.50 A |
| 8.8 V | 1.47 A | 1.83 A | 2.92 A | 0.73 A |
| 9.9 V | 1.65 A | 2.06 A | **3.03 A** | 0.83 A |

### 4.3 Load steps (TI model)

0.1 → 2.0 → 0.1 A, 1 A/µs (`run.py step136`).

| VSYS | Mode | Light-load level (V) | Lowest (V) | Highest (V) | Dip / over vs 3.794 V (mV) | Settle up / down (µs) | Ripple 0.1 A / 2.0 A (mVpp) | IL peak in step / steady (A) |
|---|---|---|---|---|---|---|---|---|
| 6.0 V | auto PFM (BOM) | 3.855 | 3.790 | 3.865 | 4 / 71 | 9 / 2 | 15.0 / 4.3 | 2.74 / 2.48 |
| 8.8 V | auto PFM (BOM) | 3.861 | 3.788 | 3.883 | 7 / 89 | 20 / 29 | 22.5 / 6.1 | 2.78 / 2.72 |
| 7.4 V | forced PWM | 3.794 | 3.752 | 3.851 | 42 / 57 | 8 / 8 | 5.5 / 5.0 | 2.79 / 2.60 |
| 8.8 V | forced PWM | 3.794 | 3.752 | 3.852 | 42 / 58 | 8 / 8 | 6.7 / 6.1 | 2.89 / 2.73 |

- In power save the step starts from the light-load level, 1.6–1.8 % above the PWM level (SLVSDV2 allows −1 / +2 % in PFM), so the dip below 3.794 V is only 4–7 mV; the total excursion is 75–95 mV.
- The highest voltage after the load release (3.883 V) is the light-load level plus 22 mV.
- 30 µF effective is below the 47 µF of the PFM accuracy condition (SLVSDV2 §7.5); the downstream input capacitors on VSYS_LV add to it (not modelled).

### 4.4 Loop gain (TI model)

Voltage injection between the output node and VOS / the divider, 1.6 A, forced PWM (`run.py loop136`).

| Frequency | 6.0 V: gain / phase | 8.8 V: gain / phase |
|---|---|---|
| 10 kHz | 16.9 dB / −10° | 16.9 dB / −10° |
| 20 kHz | 30.1 dB / +34° | 30.1 dB / +36° |
| 30 kHz | 27.0 dB / −112° | 27.2 dB / −111° |
| 50 kHz | 16.7 dB / −112° | 16.8 dB / −111° |
| 100 kHz | 8.7 dB / −115° | 8.8 dB / −113° |
| 150 kHz | 4.5 dB / −121° | 4.5 dB / −117° |
| 200 kHz | 1.6 dB / −127° | 1.6 dB / −121° |
| 250 kHz | −0.8 dB / −133° | −0.7 dB / −129° |
| 300 kHz | −2.2 dB / −130° | −2.6 dB / −132° |
| **Crossover / phase margin** | **232 kHz / 49°** | **234 kHz / 54°** |

- The peak near 20–30 kHz is the L–C resonance (24 kHz); the gain stays above 0 dB through it, so the phase swing there does not set the margin.
- The crossover sits at about fSW / 4, where a transient frequency-response measurement on a constant-on-time loop is approximate; gain margin was not measured.
- **Pass** against ≥ 45° at both ends of VSYS.

### 4.5 BRD-049 current margins

| Item | Rating | Load | Use | Verdict |
|---|---|---|---|---|
| Converter output | 4 A | 2.0 A peak (1.6 A continuous, est.) | 50 % | OK |
| Peak switch current at 2.0 A, 9.9 V, L −20 % | High-side limit 4.8 A min | 3.03 A | **63 %** (BOM line 114: 2.41 A, from Eq. 10) | OK; BOM figure to correct |
| Peak in a 0.1 → 2.0 A step (TI model, L nominal) | 4.8 A min | 2.74–2.89 A (≈ 3.1 A with L −20 %, est.) | 57–60 % (≈ 65 %) | OK |
| Inductor saturation | 7.5 A (30 % drop), 5.3 A (20 %) | 3.03 A | 40 % / 57 % | OK |
| Fault | Limit 4.8–6.5 A + (9.9 − 3.8) / 1.2 µH × 50 ns = 0.25 A (Eq. 7) | ≤ 6.75 A | 90 % of Isat (30 %) | Below Isat; HICCUP after 512 cycles |

### 4.6 Start-up into the 1S tree

EN is tied to VSYS (line 113). From VSYS present: start-up delay 200 µs typ, 300 µs max, then a 150 µs ramp with SS/TR open (SLVSDV2 §7.5, §9.4.6): **VSYS_LV within 0.45 ms**. The TPS62826 (EN on VSYS_LV) reaches 95 % 1.25 ms after its EN (SLVSEF9I, via the parts sheet): **vcc3v3_sys within ≈ 1.7 ms of VSYS**. Both rails are always on, so this happens once, at battery attach or first plug-in, and never between a PWRON press and RESETB.

One case to confirm in the schematic: if the RK809 is allowed to power on from its VDC input at plug-in (power tree §6.1 uses PWRON), its sequence could start before vcc3v3_sys feeds VCC5–VCC9; the RK809 datasheet gives no VDC debounce time (**UNVERIFIED**).

---

## 5. MaskROM entry (Main + Volume − at power-on)

### 5.1 The circuit as designed (BOM v1.5)

- **Main** (PTS815) → RK809 PWRON (internal 17 kΩ pull-up, 100 nF to GND per the RK809 application circuit).
- **BAT54** (line 78): cathode on PWRON, anode on gate-1 input In2, 20 kΩ pull-up to vcca1v8_pmu.
- **Volume −** on its own SARADC_VIN1 node (line 77), into gate-1 input In0.
- **SN74LVC1G57** (gate 1) → BOTH high when both pressed; **SN74LVC1G58** (gate 2) → high when BOTH and the window is open (line 98). Both on vcca1v8_pmu.
- **TPS3839G18** (line 97) on vcc_1v8: RESET (WINDOW_N) low for td = 120–350 ms after vcc_1v8 rises.
- **DMG1012T** (line 35) pulls **eMMC_D0** to GND through 100 Ω. A D0 held low makes the BootROM's eMMC attempt fail, so it falls through to SD and then to USB download (MaskROM), as the Radxa CM3 note states for a hard short (pin plan §3.10).

The strap here is not a sampled level: the BootROM uses D0 throughout its eMMC attempt (busy and start-bit detection, data). The requirement is that D0 stays below VIL from RESETB until the BootROM has given up on eMMC.

### 5.2 Timing budget

From the Main press (t = 0):

| Step | Time | Source |
|---|---|---|
| Contact chatter | ≤ 10 ms | PTS815 catalog p. B-43 (via parts sheet) |
| RK809 power-on after PWRON held low | **100 ms or 500 ms** (PWRON_ON_TIME, OTP) | RK809 Rev 1.01, PMIC_PWRON_KEY (0xF7) bit 7 (PDF p. 97); the RK809-5 OTP value is **UNVERIFIED** |
| Sequence: slots 2 ms apart | slot 1 → slot 5: 8 ms | RK809 Rev 1.01 §4.1, Table 4-1 (RK809-1; RK809-5 slots **UNVERIFIED**) |
| vcc_1v8 (BUCK5) | slot 1 (RK809-1) | **UNVERIFIED** for RK809-5 |
| vcca1v8_pmu (LDO8) | "off" in RK809-1; must be on for the SoC PMU domain | slot **UNVERIFIED**; modelled at slot 2 |
| RESETB high | "when the power up process is done" | delay not given; 2 ms after the last ramp used (**UNVERIFIED**) |
| BootROM: reset → eMMC attempt finished | not published | **UNVERIFIED**. Lower bound unknown; upper bound set by the eMMC's initialisation, up to 1 s after the first CMD1 (JESD84 limit, **UNVERIFIED**, standard not read) |
| Window as designed | vcc_1v8 + 120–350 ms → **RESETB + 110–340 ms** | SBVS193D td; simulated |
| Window proposed | vcca1v8_pmu + 1.21–3.43 s → **RESETB + 1.20–3.42 s** | SBVS050N td; simulated |

### 5.3 Simulation: cold power-on, normal boot, resume

`maskrom-cold.cir` and `maskrom-resume.cir`. Design A = BOM v1.5; design B = §5.6. D0 pull-up 4.7 kΩ (strongest assumed).

| Case | Design A (BOM) | Design B (proposal) |
|---|---|---|
| Main + Vol− at power-on, PWRON_ON_TIME 100 / 500 ms, td min / typ / max | D0 low until RESETB + **110 / 190 / 340 ms** (same for both key times) | D0 low until RESETB + **1,202 / 2,222 / 3,422 ms** |
| D0 level while forced | 0.04 V (100 Ω) | 0.32 V (1 kΩ), VIL 0.63 V |
| Main only (normal boot), all corners | D0 never forced; released 7 ms before RESETB as VCCQ rises | Same |
| Resume from suspend, woken with Main while Vol− held | **D0 forced 120 / 350 ms after vcc_1v8 returns** | Not forced (0 ms) |

- The button chatter ends ≥ 90 ms before the RK809 starts and has no effect on the window.
- If the user releases either button inside the window, D0 is released at once (gate 1 drops BOTH), so a user who releases after the T1 enumerates over USB leaves the eMMC free for the flashing tool.
- A bootable SD card takes precedence over USB download in the BootROM order (RK3568 datasheet §1.2.4 lists SD among the boot media; the order itself is **UNVERIFIED**): MaskROM entry needs the SD slot empty or unbootable.

### 5.4 Levels and tolerance

`maskrom-levels.cir`. Gate thresholds at VCC 1.65 V (SCES414P / SCES415N): VT+ 0.79–1.16 V, VT− 0.35–0.62 V; the worst value of each is used. The BAT54 is fitted to its maximum VF (240 mV at 0.1 mA, 320 mV at 1 mA); its temperature behaviour is a generic Schottky model (**UNVERIFIED** for this part below 25 °C).

| PWRON pressed: In2 (mV) | −20 °C | 0 °C | 25 °C | 70 °C | Margin to 350 mV at −20 °C |
|---|---|---|---|---|---|
| 20 kΩ pull-up (BOM), 67 µA | 307 | 274 | 233 | 158 | 43 mV |
| 47 kΩ, 29 µA | 283 | 248 | 204 | 126 | 67 mV |
| 100 kΩ, 14 µA | 261 | 224 | 178 | 98 | **89 mV** |

- A smaller diode current lowers VF, so the 0.1 mA datasheet point is an upper bound for any larger pull-up: the BOM's 20 kΩ choice (≈ 0.1 mA) is the least favourable of the three. The PTS815 is rated −20 to 70 °C, which bounds the cold corner.
- **PWRON released:** In2 is 1.14 V at VCC_RTC 0.5 V, 1.24 V at 0.7 V and 1.39 V at 1.0 V (20 kΩ, 25 °C). It is above the 1.16 V VT+ maximum for any VCC_RTC ≥ 0.6 V, and the RK809 itself needs PWRON ≥ 0.7 × VCC_1P8D ≈ 1.26 V to see it released. A comparator in place of the BAT54 (BOM line 78 note) is not needed.
- Volume − pressed is 0 V on its own node; the In0 margin is the full VT− (≥ 0.35 V).
- The window supervisor threshold must stay below the rail: as designed, the TPS3839G18 rising threshold is 1.687 V typ (SBVS193D) on a 1.8 V rail whose tolerance is **UNVERIFIED**; a rail sagging near 1.70 V reopens the window. The proposal sets the threshold by divider at 1.54 V (1.49–1.59 V with ±2 % VIT and 1 % resistors, plus ≤ 3 % hysteresis).

### 5.5 eMMC_D0 signal integrity with the tap off

`maskrom-d0-si.cir`: HS200 (200 MHz SDR, 5 ns unit interval), 1010 pattern, 33 Ω driver, 0.4 ns edges, 50 Ω line of 0.27 ns, 6 pF receiver, tap at the eMMC end through a 3 mm stub. All interconnect values are est.; the DMG1012T output capacitance is 9.68 pF at VDS 16 V (DS31783) and larger at low VDS (**UNVERIFIED**; 10 and 25 pF bracket it). Margins at mid-bit against VIH 1.125 V / VIL 0.63 V (0.625 / 0.35 × VCCQ, JESD84 values, **UNVERIFIED**):

| Series resistor | COSS | High at mid-bit (V) | High margin (V) | Low at mid-bit (V) | Low margin (V) |
|---|---|---|---|---|---|
| none | — | 1.768 | 0.643 | 0.032 | 0.598 |
| 1 kΩ | 25 pF | 1.727 | 0.602 | 0.044 | 0.586 |
| 470 Ω | 25 pF | 1.697 | 0.572 | 0.072 | 0.558 |
| 220 Ω | 25 pF | 1.654 | 0.529 | 0.130 | 0.500 |
| **100 Ω (BOM)** | 25 pF | 1.587 | **0.462** | 0.210 | **0.420** |
| 100 Ω | 10 pF | 1.700 | 0.575 | 0.100 | 0.530 |

With 100 Ω and 25 pF the edge also never reaches 90 % within the bit (10–90 % rise 6.5 ns). 1 kΩ keeps the tap below 0.04 V of margin loss.

Forcing strength with 1 kΩ: D0 = 1.8 V × 1 kΩ / (1 kΩ + R<sub>PU</sub>) = 0.32 V with a 4.7 kΩ pull-up, 0.16 V with 10 kΩ, against VIL 0.63 V. Neither 100 Ω nor 1 kΩ overrides a driver actively driving D0 high (a 33–50 Ω driver against 100 Ω still gives 1.2–1.4 V); the mechanism in both cases is that D0 never returns high when released (busy and start-bit detection), which is what a hard short does too. Contention current while the eMMC drives high: 12–15 mA with 100 Ω, 1.8 mA with 1 kΩ.

### 5.6 The fix, with values

| Item | As designed | Proposed | Why |
|---|---|---|---|
| Window supervisor (line 97) | TPS3839G18DBZR on vcc_1v8, td 120–350 ms | **TPS3808G01DBVR**: VDD and SENSE on **vcca1v8_pmu**, SENSE divider **280 kΩ / 100 kΩ** (1 %) → VIT 1.54 V; **CT 390 nF** X7R ±10 % → td = CT / 175 nF + 0.5 ms = 2.23 s typ, **1.21–3.43 s** with the SBVS050N spread (0.62–1.44 s at 180 nF, scaled; **UNVERIFIED** that the spread scales) and ±10 % CT; RESET open-drain with **100 kΩ** pull-up to vcca1v8_pmu; MR left open (internal 90 kΩ pull-up) | Covers a 1 s eMMC initialisation with ≥ 0.2 s to spare; vcca1v8_pmu stays on in suspend, so the window opens only at a cold power-on; threshold 0.17 V below the 1.71 V (−5 %) rail |
| PWRON_N pull-up (line 78) | 20 kΩ | **100 kΩ** | Margin to VT− at −20 °C: 43 → 89 mV |
| D0 series resistor (lines 35/97) | 100 Ω | **1 kΩ**, placed on the D0 trace, stub ≤ 3 mm | HS200 margin loss 0.18 → 0.04 V; contention 1.8 mA |
| FET gate | — | 100 kΩ to GND (optional) | Holds the DMG1012T off while vcca1v8_pmu is down (the SN74LVC1G58 output is high-impedance unpowered, Ioff) |

Consequences to accept or reject (maintainers):

- Holding Main + Volume − during the first 1.2–3.4 s after RESETB disturbs any eMMC access then (BootROM, or U-Boot if the BootROM was quicker): that is the MaskROM request by definition. Blackbird OS is not running yet, so the runtime screenshot and power-menu combinations are unaffected.
- A warm restart that keeps vcca1v8_pmu up does not reopen the window: MaskROM through the buttons needs a full power-off, as the controls spec says ("held at power-on"); software can still reboot into the loader.
- The TPS3808G01 is a different part from the TPS3839 (SOT-23-6 vs SOT-23-3); stock was not re-captured here (**UNVERIFIED**).

---

## 6. Not covered, and how

| Item | Status | How to close |
|---|---|---|
| TPS62903 with TI's own model, phase margin at low VSYS | TI's models are encrypted PSpice / SIMPLIS; generic model calibrated on TI's TPS62136 model (§2.3) gives ≈ 38–40° at 6.0 V (est.) | TI's SIMPLIS model SLVMDP3 (SIMPLIS / SIMetrix, not available here) or a bench Bode plot at VSYS 6.0 V, 1.6 A; load step on the first boards |
| TPS62903 / TPS62136 gain margin | Not measured (FRA above fSW / 5 is unreliable) | Bench |
| Ceramic DC-bias derating | Est. (10 µF effective for 22 µF at 5.1 V, 25–30 µF for 2 × 22 µF at 3.8 V) | Capacitor maker curves once the part numbers are fixed |
| CS43198 VP rejection of the VSYS_LV PFM ripple | **UNVERIFIED** | Measurement; MODE high as fallback |
| RK3566 BootROM order and eMMC timing | Not published | Bench: scope eMMC CLK / CMD / D0 from RESETB on the first board, with the slowest eMMC second source |
| RK809-5 OTP (slots, PWRON_ON_TIME) | Not public | Rockchip RK3566 hardware design guide or a measured power-up |
| VCC_RTC level, Vol− pull-up and filter | **UNVERIFIED** / not yet in the schematic | Schematic; the analysis holds for VCC_RTC ≥ 0.6 V |
| TPS61089 boost | Not simulated; replaced by the TPS62903 before results existed | — |
| Stock of TPS3808G01DBVR | Not captured | BOM update |

---

## 7. Sources

- TI TPS62903 datasheet SLVSES3A (March 2021): <https://www.ti.com/lit/ds/symlink/tps62903.pdf>; product page and models SLVMDN8 (PSpice, encrypted), SLVMDP3 (SIMPLIS): <https://www.ti.com/product/TPS62903>
- TI TPS62136 datasheet SLVSDV2 (March 2017): <https://www.ti.com/lit/ds/symlink/tps62136.pdf>; PSpice Unencrypted Transient Model SLVMC09: <https://www.ti.com/lit/zip/SLVMC09>
- TI TPS61089 datasheet SLVSD38C (August 2021): <https://www.ti.com/lit/ds/symlink/tps61089.pdf>; Unencrypted PSpice Transient Model SLVMBK5 (listed, not run): <https://www.ti.com/lit/zip/SLVMBK5>
- TI TPS3839 datasheet SBVS193D (July 2015): <https://www.ti.com/lit/ds/symlink/tps3839.pdf>
- TI TPS3808 datasheet SBVS050N (August 2026): <https://www.ti.com/lit/ds/symlink/tps3808.pdf>
- TI SN74LVC1G57 SCES414P (November 2016): <https://www.ti.com/lit/ds/symlink/sn74lvc1g57.pdf>; SN74LVC1G58 SCES415N (December 2013): <https://www.ti.com/lit/ds/symlink/sn74lvc1g58.pdf>
- Rockchip RK809 datasheet Rev 1.01 (2018-08-28): <https://rockchip.fr/RK809%20datasheet%20V1.01.pdf>
- Through the parts library (not re-read here): Nexperia BAT54 v.6; Diodes DMG1012T DS31783 Rev. 8-2; C&K PTS815 catalog B-43/B-44; Coilcraft XGL4020 Doc 1529 (via BOM v1.5); TI TPS62826 SLVSEF9I; Rockchip RK3568 datasheet Rev 1.0.
- Radxa CM3 v1.31A schematic, MaskROM note (via pin plan §3.10): <https://dl.radxa.com/cm3/docs/hw/RADXA_CM3_V1.31A_SCH_20221010.pdf>
