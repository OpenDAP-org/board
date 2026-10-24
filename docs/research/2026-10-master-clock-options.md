# Master clock options: duty cycle, load and phase noise

- **Date:** 2026-10-24
- **Task:** E1.14 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md)
- **Outcome:** [ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md) (amends [ADR 0010](../adr/0010-audio-master-clock-source.md))
- **Simulation:** [`sim/mclk-divider/`](../../sim/mclk-divider/README.md), 20 checks, all pass

## 1. The problem

ADR 0010 feeds both CS43198 XTI/MCLK inputs from one 3.3 V-class NDK NSC5083D (NZ2520SDA) on
MCLK_3V1 through a passive attenuator. The attenuator study ([`sim/mclk-attenuator/`](../../sim/mclk-attenuator/README.md),
E1.6) found two faults that no passive values remove:

1. **Duty cycle.** The CS43198 needs 45–55 % at XTI (DS1156F2 §4.5.1 p. 35). The NZ2520SDA
   symmetry is specified at 40–60 % (catalogue 1703A, p. 1). A datasheet-compliant oscillator can
   therefore violate the DAC requirement before any circuit acts on it.
2. **Oscillator load.** The NZ2520SDA is rated for CL ≤ 15 pF with Tr/Tf ≤ 6 ns. Two XTI pins at
   their 10 pF maximum (DS1156F2 Table 3-11 p. 19) behind the attenuator exceed it with the
   weakest drive the catalogue allows (`xo-load` fails, 6.03–6.38 ns).

The constraints any answer keeps:

| Constraint | Value | Source |
|---|---|---|
| MCLK frequencies | 22.5792 and 24.576 MHz only | DS1156F2 §4.5.1 p. 35, Table 4-3 p. 36; BRD-023 |
| XTI levels | VIH ≥ 0.7·VL, VIL ≤ 0.3·VL, pin −0.3 to VL + 0.3 V, VL 1.66–1.94 V | DS1156F2 Table 3-11 p. 19, Table 3-2 p. 12 |
| XTI capacitance | 10 pF maximum, no minimum or typical | DS1156F2 Table 3-11 p. 19 |
| Duty at XTI | 45–55 % | DS1156F2 §4.5.1 p. 35 |
| Phase-noise mask (no PLL) | −95 dBc/Hz at 100 Hz, falling linearly in log f to −116 dBc/Hz at 100 kHz, flat to 10 MHz (read from the plot) | DS1156F2 Figure 4-11 p. 35 |
| Audio promise | the audiophile experience is never sacrificed | T1-040 |
| Supply | no part whose supply is unknown | ADR 0010 |

The mask is loose for a quartz oscillator: integrated from 100 Hz to 10 MHz it allows 46.3 ps RMS
at 24.576 MHz (`budget.py`). Every candidate below meets it. The decision therefore rests on the
duty cycle that the datasheets guarantee, the oscillator load, and how far below the mask the
clock sits, because T1-040 asks for the best audio result and not for the minimum.

## 2. Options studied

### 2.1 (a) An oscillator with a 45–55 % symmetry specification

Survey of Epson, Kyocera, ECS, NDK, SiTime, Abracon, Microchip and Crystek on 2026-10-24
(datasheets in the parts cache; stock read from Digi-Key search pages; Mouser timed out and LCSC
refused access during the survey, so those figures are not stated here unless read elsewhere).

| Part (22.5792 / 24.576 MHz) | Supply | Symmetry | Phase noise, typical | Jitter | Digi-Key, 2026-10-24 |
|---|---|---|---|---|---|
| **Kyocera KC2520K22.5792C1GE00 / KC2520K24.5760C1GE00** (2520) | 1.6–3.63 V | 45–55 % at 50 % VCC | at 25 MHz, VCC not stated: −119 @ 100 Hz, −143 @ 1 kHz, −157 @ 10 kHz, −160 @ 100 kHz (Clock K-Series catalogue, October 2026, p. 3) | 1 ps max, 12 kHz–20 MHz | 923 / 5,474 @ $1.39 |
| ECS-2520MVLC-225.792-CN-TR / -245.7-CN-TR (2520) | 1.6–3.6 V | 45–55 % at ½ VDD | plot at 50 MHz, 3.3 V: −139.6 @ 1 kHz, −159.6 @ 100 kHz (datasheet p. 3); about −146 @ 1 kHz scaled to 24.576 MHz (calculated) | 150 fs typ at 50 MHz | 727 / 1,401 @ $1.27 |
| NDK NZ2520SH, NSC5004A-22.5792M / -24.576M (2520, 1.8 V code) | 1.8 V ± 0.18 V | 45–55 % at ½ VCC | not published at these frequencies | 90 fs typ, at 125 MHz only | 993 / 977 @ $2.94 |
| Epson SG2016CAN / SG-210STF | 1.6–3.63 V | 45–55 % | plot at 20 MHz, 1.8 V: about −135 @ 1 kHz (read by eye) | 0.32 ps, 12 kHz–5 MHz | 22.5792 MHz obsolete (0); 24.576 MHz SG-210STF 7,053 |
| SiTime SiT8008 / SiT1602 / SiT1618 (MEMS) | 1.8 V options | 45–55 % | SiT8008: no plot; SiT1602/1618: 22.5792 MHz not offered | 1.3 ps typ / 2 ps max | SiT8008 22.5792 and 24.576: stocked (programmed on order, inferred) |
| NDK NZ2520SDA (current, reference) | 3.3 V ± 0.33 V (NSC5083D) | **40–60 %** | 22.5792 MHz, 3.3 V: −164 @ 1 kHz, −169 @ 100 kHz | 43 fs at 49.152 MHz | 2,239 / 3,083 |

Reading:

- The best quartz part with a 45–55 % specification, the KC2520K, is 21 dB noisier than the
  NSC5083D at 1 kHz (−143 against −164 dBc/Hz) and about 15 dB noisier in the divided topology of
  §2.3. It stays 41 dB under the mask at 1 kHz.
- A 45–55 % oscillator meets the DAC limit with **no margin**: the symmetry is specified at
  50 % VCC at the oscillator pin, while the CS43198 threshold may lie anywhere between VIL and VIH
  and the edges are slowed by the net. The simulation model used for the attenuator gives 1–3 %
  of duty shift for 2 ns edges, which a 45–55 % source cannot absorb.
- One 15 pF-rated oscillator still cannot drive two 10 pF XTI pins plus traces. Option (a) needs a
  buffer per DAC (option (b)), which takes the duty guarantee away again (§2.2).
- MEMS parts publish no phase noise at 100 Hz, so the low end of the mask cannot be checked from
  their datasheets, and ADR 0010 already rejected them for the DAC clock.

Option (a) has one strong point: a 1.8 V part needs no level shifting and draws 2.5–3.5 mA
(KC2520K at 1.6–2.25 V) instead of up to 15 mA at 3.1 V. It is kept as the fallback if the
divider of §2.3 proves wrong on the bench.

### 2.2 (b) A buffer or level translator per DAC

A 1.8 V buffer behind the 3.1 V oscillator solves the level and the load: one input pin on the
oscillator, one output per DAC.

| Part | Additive jitter | Duty it guarantees | Notes | Availability (2026-10-24) |
|---|---|---|---|---|
| TI LMK1C1102 (1:2 LVCMOS, 1.8 V ± 5 %) | 17.5 fs typ, 50 fs max, 12 kHz–20 MHz at 1.8 V (SNAS791D p. 7) | ODC 45–55 % **only with a 50 % input** (SNAS791D p. 6) | CLKIN 3.6 V absolute (3.3 V-tolerant), ROUT 60 Ω, propagation delay ≤ 3 ns at 1.8 V | LCSC C2859546 (PWR) 6,568 @ $1.12; Arrow 2,000; Mouser 3,952 (ADQFR) via FindChips |
| TI CDCLVC1102 | < 100 fs at 3.3 V | pulse skew ≤ 180 ps at 3.3 V (SCAS895B p. 7) | 2.5 or 3.3 V only, VIN ≤ VDD + 0.5 V: its output cannot drive a 1.8 V XTI | not checked |
| TI/Nexperia LVC, AUP, AXC single gates and translators | not published | not specified (only tpd minimum and maximum) | AXC translators have no specified pulse skew; LVC at 1.8 V spreads tpd over several ns | — |

A buffer passes the oscillator's 40–60 % through and adds its own distortion. The best-specified
part, the LMK1C1102, guarantees 45–55 % only for an ideal 50 % input, so (b) alone, or (a) plus
(b), still has no datasheet-guaranteed duty at XTI.

### 2.3 (c) An oscillator at twice the frequency, divided by two

A D flip-flop with Q̅ fed back to D toggles on every rising clock edge. The output period is
exactly two oscillator periods, whatever the oscillator symmetry. The output high time is one
oscillator period plus tPHL − tPLH of the flip-flop, so the duty error is
(tPHL − tPLH) / T_MCLK.

**Oscillators.** The NZ2520SDA family covers 20–50 MHz (catalogue 1703A p. 1), and the catalogue
tabulates 49.152 MHz itself: at 3.3 V, −158 dBc/Hz at 1 kHz, −172 dBc/Hz at 100 kHz, 43 fs RMS
(12 kHz–20 MHz). An ideal divide-by-two lowers phase noise by 6.02 dB: −164 and −178 dBc/Hz at
24.576 MHz. The 24.576 MHz NSC5083D of ADR 0010 has no published phase noise, so the 48 kHz family
becomes better documented, not worse. NSC5083D-45.158M: Digi-Key 2,741 @ $2.94; NSC5083D-49.152M:
Digi-Key 3,404 @ $2.94 (2026-10-24). Digi-Key labels the first "45.158 MHz"; a third-party listing
names it 45.1584 MHz; the exact frequency on an NDK document is **UNVERIFIED**.

**Flip-flop.** The divider must run from 1.8 V (so its output meets the XTI limits directly), take
a 3.1 V clock input, and have a tight tPHL − tPLH from its datasheet alone.

| Flip-flop at VCC 1.8 V | CLK → Q, min–max | Bound on tPHL − tPLH | Duty bound at 24.576 MHz | 3.3 V input |
|---|---|---|---|---|
| **TI SN74AUC1G74** | 1.0–1.7 ns at CL 15 pF; 1.5–2.4 ns at 30 pF (SCES537D pp. 4–5) | 0.7 ns (15 pF) | **50 ± 1.7 %** | VI up to 3.6 V at any VCC (p. 3) |
| TI SN74AUC1G80 | 0.3–1.9 ns at 15 pF (SCES388K p. 4) | 1.6 ns | 50 ± 3.9 % | yes |
| TI SN74LVC1G74 | 4.8–13.4 ns (SCES794G p. 7) | 8.6 ns | 50 ± 21 % | yes |

The bound treats tPLH and tPHL as independent anywhere in the specified range, which is
pessimistic: both come from the same output stage on the same clock edge. It is still the only
bound the datasheets support. The SN74AUC1G74 also has Q and Q̅ on separate pins (Q̅ to D, Q to
the DAC), CLR to hold the divider in a known state, Ioff, fclock ≤ 250 MHz and tw ≥ 1 ns at 1.8 V
(SCES537D p. 4). TI lists it Active; Digi-Key SN74AUC1G74DCUR 24,658 @ $0.62, Mouser 3,269 (via
FindChips), LCSC C2677720 170 @ $0.43 (2026-10-24).

**One divider or two.** One AUC output driving both XTI pins fails the duty with the weakest output
the datasheet allows (56 Ω, from VOH ≥ 1.2 V at −8 mA): 41.8 % at 10 pF per pin (first run: 33 Ω per
branch, 20 mm, ±0.9 ns from the 30 pF column). One divider per DAC
keeps each output at ≤ 15 pF, the condition of the 0.7 ns bound, and passes (§3). The two dividers
share the oscillator net (two 2.5 pF inputs) and one CLR line.

**Supply of the dividers.** Supply noise modulates the propagation delay. The dividers get their
own rail, MCLK_1V8, from a TPS7A2018 (the part of BOM line 29; 10 µVrms, 10 Hz–100 kHz at 1 mA,
SBVS338H p. 7) on AUDIO_2V2, enabled by DAC_DIG_1V8 (VEN(HI) ≤ 0.9 V, SBVS338H p. 7). The clock
then reaches XTI only while the DAC's VL is up, which closes feature-block gap G3 for the clock
path.

## 3. Simulation

[`sim/mclk-divider/`](../../sim/mclk-divider/README.md), ngspice 47, 120 cases, 2026-10-24.
`odapkit sim run sim/mclk-divider`: **20 passed, 0 failed.** Values: RX 33 Ω at each oscillator,
100 kΩ pull-down on the oscillator net, RS 27 Ω at each divider output; oscillator to dividers
≤ 10 mm, each divider to its XTI ≤ 15 mm.

| Quantity, worst over corners | Value | Limit |
|---|---|---|
| Load on the oscillator net | 13.7 pF | ≤ 15 pF |
| Divider clock: lowest peak / highest valley | 2.845 / 0.209 V | ≥ 1.196 / ≤ 0.616 V |
| Divider clock: peak / valley | 3.146 / 0.000 V | ≤ 3.6 / ≥ −0.5 V |
| Divider clock: shortest pulse beyond VIH or VIL | 1.98 ns | ≥ 1 ns |
| Load on each divider output | 12.6 pF | ≤ 15 pF |
| XTI high / low | 1.737 / 0.023 V | ≥ 1.358 / ≤ 0.498 V |
| XTI peak / valley | 1.889 / −0.049 V | ≤ 1.96 / ≥ −0.3 V |
| XTI duty | **45.08–54.35 %** | 45–55 % |
| Re-crossings of VIL/VIH | 0 | 0 |

Corners: both frequencies; oscillator symmetry 40 and 60 %; oscillator drive 10, 30 and 181 Ω
(the last the weakest the catalogue allows); divider input 2.5 and 4 pF; tPHL − tPLH −0.7, 0 and
+0.7 ns; divider output 15 and 56 Ω; XTI 1, 4 and 10 pF; MCLK_3V1 3.054–3.147 V, MCLK_1V8
1.76–1.84 V, VL 1.66–1.94 V; switching points anywhere between VIL and VIH. The oscillator
symmetry has no effect on the XTI duty, as expected.

The thin duty margin (0.08 %) is the corner where every worst case stacks. Exploration: a 20 mm
branch gives 44.98 %, so 15 mm is a layout limit; RS 22 Ω overshoots to 2.026 V with a strong
output; RS 33 Ω gives 44.24 % at 20 mm.

## 4. Phase-noise and jitter budget

`sim/mclk-divider/budget.py`, at 24.576 MHz (the 45.1584 MHz oscillator is not tabulated; the
49.152 MHz figures are used for both, **UNVERIFIED**):

| Offset | Mask | Oscillator ÷ 2 | Divider supply term (est.) | Divider floor (est.) | Total | Margin |
|---|---|---|---|---|---|---|
| 1 kHz | −102.0 | −164.0 | −159.1 | −178.3 | −157.9 dBc/Hz | 55.9 dB |
| 100 kHz | −116.0 | −178.0 | −159.1 | −178.3 | −159.0 dBc/Hz | 43.0 dB |

| Jitter | Value |
|---|---|
| Oscillator, 12 kHz–20 MHz | 43 fs (catalogue) |
| Divider supply term | 32 fs (est.) |
| Divider floor | 50 fs (est.) |
| Total (RSS) | 73 fs |
| Allowed by the mask, 100 Hz–10 MHz | 46.3 ps, margin 56.0 dB |

The two divider terms are estimates, because TI publishes neither additive jitter nor supply
sensitivity for the AUC family:

- **Supply term:** TPS7A20 noise (10 µVrms over 10 Hz–100 kHz, taken flat: 31.6 nV/√Hz) times a
  delay sensitivity of 3.2 ns/V, bounded from SCES537D (CLK → Q maximum 2.5 ns at 1.4 V and
  1.7 ns at 1.65 V). This is a bound, not a typical value; it dominates the estimate.
- **Floor:** the LMK1C1102's 50 fs maximum at 1.8 V, used as an analogue for a CMOS stage.

Comparison at 1 kHz (dBc/Hz, near 24 MHz): ADR 0010 at 22.5792 MHz −164 (catalogue; 24.576 MHz
not published); this topology −164 from the oscillator and −157.9 with the estimated divider
bound; KC2520K −143; ECS-2520MVLC about −146 (scaled). The divided NDK stays 15–21 dB below every
oscillator with a 45–55 % specification, even with the pessimistic divider estimate.

## 5. Comparison

| | ADR 0010 (attenuator) | (a) 45–55 % XO at 1.8 V + (b) buffer | (b) buffer behind NSC5083D | **(c) 2 × f, one divider per DAC** |
|---|---|---|---|---|
| Duty at XTI from datasheets | none (40–60 %) | none (45–55 % source, 45–55 % ODC with ideal input) | none | **50 ± 1.7 %; 45.08–54.35 % simulated at XTI** |
| Oscillator load | fails (two 10 pF pins) | buffer: one pin | one pin | 13.7 pF ≤ 15 pF |
| Phase noise at 1 kHz | −164 (22.5792 MHz only) | −143 (KC2520K) | −164 + buffer | −164 (−157.9 with divider bound) |
| Margin to the mask at 1 kHz | 62 dB | 41 dB | about 62 dB | 56–62 dB |
| Power (one family running) | NSC5083D ≤ 15 mA at 3.1 V; attenuator 1.7 mA DC | KC2520K ≤ 3.5 mA at 1.8 V + LMK1C1102 (≤ 20 mA at 100 MHz) | NSC5083D + LMK1C1102 | NSC5083D ≤ 15 mA at 3.1 V + two dividers ≈ 8.9 mA at 1.8 V (typ, Cpd 44 pF, SCES537D p. 5) |
| Parts on the clock path | 2 XO + 10 attenuator passives | 2 XO + 1 buffer + passives | 2 XO + 1 buffer + passives | 2 XO + 2 dividers + 1 LDO + 10 passives (net +3) |
| Availability | stocked | stocked | stocked | stocked (§2.3) |
| Mainline / device tree | none | none | none | none |

Power for (c): each divider draws about Cpd·VCC·f_CLK + CL·VCC·f_Q =
44 pF × 1.8 V × 49.152 MHz + 12.6 pF × 1.8 V × 24.576 MHz ≈ 4.45 mA (Cpd is typical at 25 °C);
two dividers ≈ 8.9 mA at 1.8 V, ≈ 20 mW at AUDIO_2V2. Removing the attenuator saves its 1.7 mA DC
at 3.1 V (≈ 6.5 mW at VSYS_LV) and its switching load. Net ≈ +13 mW in playback (est.), about
1.5–2 % of screen-off playback power (power tree §4: the 42 mW pre-buck saving is 4–6 %). The
oscillator current at 49.152 MHz against 24.576 MHz is not published (the 15 mA maximum covers
the family).

Device tree: the CS43198 still sees a fixed 22.5792 or 24.576 MHz clock (`fixed-clock`, or
`gpio-gate-clock` with the ST lines); the 2× oscillators are not visible to the codec driver. No
mainline change.

## 6. Decision

Option (c) with one divider per DAC: NSC5083D-45.158M and NSC5083D-49.152M on MCLK_3V1, two
SN74AUC1G74 on a new MCLK_1V8 rail, recorded in
[ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md). It is the only option
whose duty cycle at XTI follows from datasheet limits, it fixes the oscillator load, it keeps the
oscillator with the best published phase noise, and it costs about 13 mW and three net parts.

## 7. Open items and risks

1. **Divider phase between the DACs.** Two dividers on one clock can start in opposite phase: a
   constant offset of one oscillator period (20.3 ns at 49.152 MHz, 22.1 ns at 45.1584 MHz)
   between left and right. A common CLR released while the clock is stopped makes the start
   deterministic unless the oscillator emits runt pulses at start-up (**UNVERIFIED**). The effect
   of such an offset on the CS43198 in slave mode is **UNVERIFIED**; measure the inter-channel
   delay on the first boards.
2. **Divider additive noise.** Supply sensitivity and floor of the SN74AUC1G74 are estimates
   (§4). Measure the MCLK phase noise at XTI on the first boards, with the J-test and THD+N
   captures of ADR 0010.
3. **45.1584 MHz.** Phase noise not tabulated; exact frequency on an NDK document **UNVERIFIED**.
   LCSC has no stock of NSC5083D-45.158M (C17523715: 0) and 31 of NSC5083D-49.152M; Digi-Key is
   the source.
4. **Oscillator at 3.1 V.** As in ADR 0010, the catalogue phase noise is at 3.3 V.
5. **Layout limits.** Oscillators and dividers in one cluster, oscillator-to-divider trace
   ≤ 10 mm, each divider ≤ 15 mm from its XTI pin. Input capacitance of the AUC (4 pF bound) and
   of XTI (typical) are **UNVERIFIED**.
6. **Second source for the divider.** No other logic family found gives a comparable datasheet
   bound at 1.8 V (§2.3). The SN74AUC1G74 is single-sourced (TI), in four packages (DCU, YZP, RSE,
   DCT; DCT is Last Time Buy at Digi-Key).
7. **HAT master clock (BOM line 112).** The oscillator net has 1.3 pF of budget left. A HAT copy
   must come from its own divider or buffer and re-run this study.

## Sources

- Cirrus Logic, CS43198 data sheet DS1156F2 (December 2022), §4.5.1 and Figure 4-11 p. 35, Table 4-3
  p. 36, Table 3-2 p. 12, Table 3-11 p. 19.
- NDK, NZ2520SDA catalogue (2012E / 1703A), <https://www.ndk.com/images/products/catalog/c_NZ2520SDA_e.pdf>.
- NDK, NZ2520SH catalogue and specification NDKT02-00001 (sha256 `d62bc65f…39531`, `eab6fc9b…c258`).
- Texas Instruments, SN74AUC1G74 SCES537D (December 2003, revised June 2007), sha256
  `78ef342668836a8c3bffdb203769e9e4404e1914badcff849016b7ff429445c6`.
- Texas Instruments, SN74AUC1G80 SCES388K (revised January 2007); SN74LVC1G74 SCES794G (revised
  September 2021); LMK1C1102 SNAS791D (revised February 2022); CDCLVC1102 SCAS895B (revised
  February 2017); TPS7A20 SBVS338H.
- Kyocera, Clock K-Series catalogue (October 2026, sha256 `dbbf8022…a26f`) and part specifications
  KC2520K22.5792C1GE00 / KC2520K24.5760C1GE00.
- ECS, ECS-2520MVLC datasheet (sha256 `2e3d0e48…90ae`); Epson SG2016CAN catalogue Ver3.0;
  SiTime SiT8008, SiT1602, SiT1618 datasheets.
- Distributor stock read 2026-10-24: Digi-Key search pages; FindChips (Mouser, Arrow); LCSC
  through the JLCPCB parts search.
- [`sim/mclk-attenuator/`](../../sim/mclk-attenuator/README.md) and [`sim/mclk-divider/`](../../sim/mclk-divider/README.md).
