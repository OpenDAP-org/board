# Headphone output power: closing the gap to the mid-range segment

- **Date:** 2026-10-22
- **Status:** Desk research, proposal. Nothing here was built, simulated or measured. It does not change the [BOM v1](../specs/bom-v1.md), the [power tree](../specs/power-tree-v0.md) or any ADR; adopting it needs the maintainers' confirmation, because it touches BRD-022 (Draft: "four OPA1622") and the audio stage.
- **Question:** the T1 promises a mid-range player delivered through execution, and the audiophile experience is never sacrificed. Does the current headphone stage deliver mid-range output power into low-impedance headphones, and if not, what is the least costly way to get there?
- **Inputs read:** [BOM v1](../specs/bom-v1.md) (v1.2, lines 18–19, 22–26, 36–37; open question 13), [power tree v0](../specs/power-tree-v0.md) §4.1, §4.2, §4.9, §4.10, board ADRs [0001](../adr/0001-cirrus-logic-dac-family.md) and [0009](../adr/0009-bom-v1-decisions.md), [board requirements](../requirements/README.md) (BRD-022, BRD-024, BRD-049, BRD-050), the T1 [battery-life analysis](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-battery-life-analysis.md) (§5 amplifier model, §6 scenarios, §10–11 category and thresholds), and the part sheets in `libs/parts` for OPA1622IDRCR, TPS65131RGER, TPS7A4901DGNR, TPS7A3001DGNR and CS43198-CNZR.
- **Datasheets read in this session** (TI and Cirrus PDFs downloaded and converted to text):
  - OPA1622 SBOS727B (§6.5, §8.2, Table 2, Figures 37–38);
  - CS43198 DS1156F2 (Table 3-4, §4.2.3);
  - TPA6120A2 SLOS431B (§7.1–7.6);
  - BUF634A SBOS948F (§7.5–7.6, §8.3.1);
  - OPA1656 SBOS901C, OPA1688 SBOS724A, OPA1612, INA1620 SBOS859B, OPA1692 (output current and quiescent current only).
- **Not obtained:** the ADI LT3045 and LT3094 datasheets and product pages (timeouts, as in BOM v1); the ADA4807 datasheet; the SG Micro SGM8262 datasheet. Figures for those parts are marked **UNVERIFIED**.
- **Stock:** JLCPCB parts API (= LCSC) on 2026-10-22. Other distributors not checked in this session.
- **Conventions:**
  - **UNVERIFIED** = no primary source read in this session.
  - **Est.** = engineering estimate, to be replaced by simulation and measurement (T1-026).
  - Powers are per channel, sine, at the onset of clipping, unless noted.

---

## 1. Summary

1. **The current stage is current-limited, and balanced barely helps.** The OPA1622 clips at about 97–109 mA peak per amplifier at ±5 V (SBOS727B Table 2). With one amplifier per leg, the 4.4 mm output reaches only **≈ 150–190 mW into 32 Ω**, against 125 mW from the 3.5 mm output.
2. **The gap to the segment is about 2 dB single-ended and 6 dB balanced at 32 Ω.**
   - Shanling M1 Plus: 195 / 660 mW (SE / balanced).
   - FiiO JM21 (2× CS43198): 245 / 700 mW.
3. **A second finding affects quality:** the power tree's 2.0 Vrms per DAC output needs the CS43198 `+1dB_EN` mode. That mode is specified at **−105 dB THD+N**, against −115 dB without it (DS1156F2 Table 3-4). The level should come from the amplifier gain instead.
4. **Recommendation (option A6, §5):**
   - Parallel both halves of one OPA1622 on each balanced leg: **six OPA1622 instead of four**.
   - Raise the amplifier rails from ±5.0 V to **±6.0 V**.
   - Swap the LDOs for the LT3045 / LT3094 pair already proposed in BOM v1.2.
   - Run the DAC without `+1dB_EN`, with an amplifier gain of about 1.6 (+4 dB).
5. **What A6 gives (est.):**
   - SE: **≈ 240 mW into 32 Ω** and ≈ 320 mW into 16 Ω.
   - Balanced: **≈ 640 mW into 32 Ω** (range 490–760 mW, depending on current sharing).
   - THD+N stays at OPA1622 and CS43198 datasheet levels.
6. **What A6 costs:**
   - **SE autonomy −11 %:** 12.8 → 11.4 h on the Adafruit 328 in the core session; 16.3 → 14.6 h on the 105060 commercial target, which is still 101 % of the category average.
   - **Balanced autonomy −27 % against the board plan**, or −11 % against the battery model, which already assumed eight enabled channels.
   - **PCB area:** ≈ +80–110 mm² (est.).
   - **Power design:** the ±6 V generator must be re-verified at ≈ 275 mA per rail (BRD-049).

---

## 2. The segment

Makers' figures, 32 Ω unless noted, at the THD+N limit each maker states (usually < 1 %). They are not independent measurements and not directly comparable with the datasheet-based figures below.

| Device | DAC · amplifier | SE 32 Ω | Balanced 32 Ω | 300 Ω SE / balanced | Source |
|---|---|---|---|---|---|
| Shanling M1 Plus (USD 209) | ES9069Q · 2× SGM8262 | 195 mW | 660 mW | — | Maker's figures via a retailer listing, provided by the maintainers. **Not re-read in this session (UNVERIFIED)** |
| **FiiO JM21** | **2× CS43198** · 2× SGM8262 | **245 mW** | **700 mW** | — | fiio.com/jm21, read 2026-10-22 |
| FiiO M21 (high gain) | 4× CS43198 · two-stage discrete | 290 mW | 720 mW | — | fiio.com/m21, read 2026-10-22 |
| FiiO M21 (super high gain) | same | 405 mW | 950 mW | 45 / 185 mW | same |
| HiBy R3Pro II | 2× CS43198 · 4× OPA1622 | "up to 480 mW" | — | — | store.hiby.com; load and output not stated |
| HiBy R6 III (2025) | 4× CS43198 | — | — | — | store.hiby.com: no power figure in text |

**Reading:**

- The mid-range bar for a 2× CS43198 player is **≈ 200–250 mW SE** and **≈ 650–700 mW balanced** into 32 Ω.
- The FiiO JM21 is the closest architectural neighbour (same DACs, same autonomy class in the battery analysis §10.3), and it reaches that bar.

---

## 3. Current T1 output (BOM v1.2)

### 3.1 Limits that set it

- **DAC level, per output** (DS1156F2 Table 3-4, HV_EN = 1, VP = 3.6 V). In mono mode one CS43198 drives one channel's two legs (§4.2.3).

  | `+1dB_EN` | Full scale, typ (min) | THD+N at 0 dB |
  |---|---|---|
  | 0 | 4.90 Vpp (4.66) = **1.73 Vrms** | −115 dB typ, −109 dB max |
  | 1 | 5.70 Vpp (5.42) = **2.02 Vrms** | **−105 dB typ** (no maximum given) |

- **Amplifier gain:** 1 in power tree §4.1. The TI application uses 1.095 (SBOS727B Eq. 8).
- **OPA1622 output current at ±5 V:**
  - TI's measured clip points are 95 mW into 16 Ω (109 mA peak) and 150 mW into 32 Ω (97 mA peak).
  - TI states that both are "limited by the output current capabilities of the amplifier" (SBOS727B Table 2, p. 24).
  - Short-circuit current is +145 / −130 mA at ±18 V, and it falls with temperature (§6.5, Figure 37).
  - **Design figure: ≈ 100 mA peak per amplifier.**
- **Swing:**
  - The 32 Ω clip point of Table 2 is 3.10 V peak on ±5 V, so ≈ 1.9 V of headroom at ≈ 100 mA (derived).
  - At low current the headroom is 0.8–0.9 V (§6.5).
- **Topology** (BOM line 19, power tree §4.1):
  - 4.4 mm: one OPA1622 per channel, one amplifier per leg.
  - 3.5 mm: one OPA1622 per channel, both halves paralleled (**UNVERIFIED**, not described in SBOS727B).

### 3.2 Output today

Based on the power tree's assumptions (gain 1, `+1dB_EN` = 1, 2.0 Vrms per leg).

| Output | 16 Ω | 32 Ω | 300 Ω | Limited by |
|---|---|---|---|---|
| 3.5 mm SE | ≈ 250 mW with paralleled halves (**UNVERIFIED**); 95 mW with one half | **125 mW** | 13 mW | DAC level × gain 1 (one half alone: current) |
| 4.4 mm balanced | ≈ 75–95 mW | **≈ 150–190 mW** | 53 mW | Current at 16 and 32 Ω: 97–109 mA per leg; DAC level at 300 Ω |

- Balanced into 32 Ω would be 500 mW at 4 Vrms differential, but that needs 177 mA peak per leg. One OPA1622 amplifier cannot supply it.
- **This is the root of the gap:** the 4.4 mm output delivers about the same current as the 3.5 mm output, so it adds only ≈ 1–2 dB.
- Without `+1dB_EN` (the −115 dB setting) and at gain 1, the SE output drops further, to 94 mW into 32 Ω and 10 mW into 300 Ω.

### 3.3 Gap to the segment (32 Ω)

| | T1 today | Shanling M1 Plus | FiiO JM21 | Gap |
|---|---|---|---|---|
| SE | 125 mW | 195 mW | 245 mW | −1.9 dB / −2.9 dB |
| Balanced | ≈ 150–190 mW | 660 mW | 700 mW | **−5.4 to −6.4 dB** / −5.7 to −6.7 dB |
| 300 Ω balanced | 53 mW | — | — | FiiO M21 super high gain: 185 mW (−5.4 dB) |

Into the 32 Ω headphones the segment is sold against, the T1's balanced output delivers about a quarter of the segment's power. It does not meet the mid-range promise.

---

## 4. Options

### 4.1 Common assumptions

**Output power (est.):** the swing and current limits of §3.1, scaled to each option's rails.

**Autonomy:** the battery analysis model (§5 there), with the same parameters and rail efficiency 0.75. Rows:

- **S1:** core session, SE 32 Ω, 1 mW per channel.
- **S2:** balanced 300 Ω, 1 mW per channel.
- **B32:** balanced 32 Ω IEMs, 1 mW per channel.

Runtimes are given on the Adafruit 328 (9.4 Wh) and on the 105060 commercial target (≈ 12 Wh). Category averages: 14.5 h SE, 11 h balanced (battery analysis §10.2).

**Baselines:**

- "Plan" = the board's ±5 V, four-amplifier balanced output (power tree §4.1).
- The battery model's typical case already assumed **eight** enabled channels for balanced (battery analysis §4.3), because the topology was not drawn then. Both baselines are shown.

**Rail currents:** full-scale continuous sine, both channels. A rail supplies 2·Ipk/π per balanced channel, plus quiescent current.

### 4.2 Overview

| Option | SE 16 / 32 / 300 Ω | Balanced 16 / 32 / 300 Ω | THD+N, noise (datasheet) | Amplifier Iq per rail, balanced | S1 / S2 typ draw | Verdict |
|---|---|---|---|---|---|---|
| **A0** Today (§3) | 250* / 125 / 13 mW | 85 / 170 / 53 mW | OPA1622 −116 dB (32 Ω, 10 mW); DAC −105 dB with `+1dB_EN` | 10.4 mA | 663 / 642 mW | Fails the segment |
| **A1** Rails ±6 V only | ≈ 250* / 160 / 26 mW | 85 / 170 / 102 mW | as A0 | 10.4 mA at ±6 V | 703 / 678 mW | Fails: 32 Ω stays current-limited |
| **A2** Gain switch only | as A1 at 32 Ω | 85 / 170 / up to 102 mW | adds an analog switch to the feedback network (distortion not characterised) | 10.4 mA | ≈ A0 | Fails: gain does not add current |
| **A5** Parallel halves per leg, ±5 V, LT3045/LT3094 | 300 / 150 / 26 mW | 300 / ≈ 600 / 64 mW | OPA1622 per half as A0; paralleling **UNVERIFIED** | 20.8 mA | 694 / 812 mW | Balanced close (−0.4 dB), SE short (−1.1 dB) |
| **A6** Parallel halves per leg, **±6 V**, LT3045/LT3094, gain 1.6 | **320 / 240 / 26 mW** | **320 / ≈ 640 / 102 mW** | as A5; DAC at −115 dB (`+1dB_EN` = 0) | 20.8 mA at ±6 V | **739 / 881 mW** | **Meets the segment** (recommended) |
| **B** OPA1622 half + BUF634A per leg, ±6.5 V | ≈ 300 / 240 / 30 mW | ≈ 300 / ≈ 650 / 110 mW | see §4.6: low-Iq mode HD3 −40 dBc open loop; wide mode 8.5 mA | 16.4 mA (low-Iq) or 44.4 mA (wide) | ≈ 720 / 840 mW (low-Iq, est.) | Rejected: quality or Iq |
| **C** TPA6120A2 | — | ≥ 700 mW class | −101 dB THD+N at 32 Ω, 10 mW (±5 V); SNR 116 dB at ±5 V | 46 mA (2 packages) | ≈ +0.6 W | Rejected: quality and Iq |
| **D** OPA1656 / OPA1688 / ADA4807 class | lower than OPA1622 | lower | — | — | — | Rejected: less output current |
| **E** SGM8262 (what the segment uses) | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | — | Rejected for now: no stock, no datasheet read |

\* SE 16 Ω relies on the paralleled halves already planned for 3.5 mm (**UNVERIFIED**).

### 4.3 A1: raise the rails only

- **Effect:** ±6 V raises the swing to ≈ 4.1 V peak at 100 mA (est.). That helps high-impedance loads (300 Ω balanced: 102 mW at gain 1.6).
- **Why it fails:** at 32 Ω the stage is still limited to ≈ 100 mA per leg, so balanced stays at ≈ 150–190 mW.
- **Cost:** about +40 mW in S1 (quiescent current × 1.2).

### 4.4 A2: switchable high gain

- **What the datasheet says:** TI notes that designers "choose to select the headphone amplifier gain by using a switch" (SBOS727B §8.2.2). A switch adds a part to the feedback network, with distortion that has not been characterised.
- **Why it fails:** gain raises the voltage, not the current. It closes nothing at 16–32 Ω.
- **Where it would help:** only above ≈ 150 Ω.
- **Verdict:** it is a separate product decision (an IEM low-gain mode, battery analysis lever 5), not a fix for this gap.

### 4.5 A5 and A6: parallel both OPA1622 halves on every balanced leg

**Topology:**

- Six OPA1622: four for 4.4 mm (one package per leg, both halves paralleled) and two for 3.5 mm (as planned).
- Each half is its own difference amplifier fed from the same CS43198 output pair. Each drives the leg through a ballast resistor of ≈ 0.5–1 Ω, with feedback taken before the ballast.
- Resistor values are doubled against the TI network (for example R1 = R3 = 1.0 kΩ, R2 = R4 ≈ 1.6 kΩ for gain 1.6, C1 = C2 ≈ 100 pF to keep the pole at ≈ 1 MHz, SBOS727B Eq. 9–11). Two networks in parallel then load each DAC pin as one TI network does today.
- **Offset circulation:** at most 2 × 500 µV × noise gain 2.6, across 2 × 1 Ω, ≈ 1.3 mA (est.). That is negligible.
- **Output impedance:** ≈ Rb / 2, so 0.25–0.5 Ω. The segment states < 1 Ω.
- SBOS727B does not describe paralleling. The approach needs simulation (TINA-TI model, **UNVERIFIED** availability) and measurement.

**Why it works:** each leg gets ≈ 2 × 100 mA. Derated for imperfect sharing, that is ≈ 175–218 mA (est.).

**Output (est.):**

| | A5 (±5 V) | A6 (±6 V) | Limit |
|---|---|---|---|
| Swing at 100 mA per half | 3.1 V peak | ≈ 4.1 V peak | headroom ≈ 1.9 V (§3.1) |
| SE 32 Ω | 150 mW | **240 mW** (3.92 V peak at gain 1.6, 122 mA) | swing at ±5 V; gain at ±6 V |
| SE 16 Ω | 300 mW | **320 mW** | current, ≈ 200 mA |
| SE 300 Ω | 26 mW | 26 mW (gain 1.6) | gain |
| Balanced 32 Ω | ≈ 600 mW | **≈ 640 mW (490–760 mW)** | current, 175–218 mA per leg |
| Balanced 16 Ω | ≈ 300 mW | ≈ 320 mW | current |
| Balanced 300 Ω | 64 mW at gain 1.27 | **102 mW** | gain |

**Distortion and noise (datasheet basis):**

- OPA1622 single amplifier: −116 dB at 32 Ω, 10 mW; −118.7 dB at the 150 mW clip point (SBOS727B §6.5, Table 2). The paralleled pair is not characterised (**UNVERIFIED**). TI notes that its output stage limits the extra distortion at high current (§8.2.3).
- DAC at `+1dB_EN` = 0: −115 dB typ, −109 dB max.
- Idle noise:
  - The DAC part scales with gain: 0.55 µV × 1.6 ≈ 0.9 µV A-weighted.
  - The amplifier's contribution with 1 kΩ networks is **UNVERIFIED** (est. ≤ 1 µV).
  - The two halves' uncorrelated noise averages down by √2.
  - Segment for comparison: FiiO JM21 < 1.5 µV, M21 < 1.6 µV (makers).

**Quiescent current:**

- The balanced output goes from 4 to 8 enabled halves (10.4 → 20.8 mA per rail). The SE output is unchanged (4 halves).
- An enabled package cannot drop to one half: its outputs are not high-impedance in shutdown and can be back-powered (SBOS727B §7.4.1). The balanced output therefore always pays for eight halves.
- The LT3045 / LT3094 add ≈ 4 mA in total (BOM v1.2 open question 13, **UNVERIFIED** until the ADI datasheets are read).

**Autonomy** (battery model, typical; runtimes Adafruit 328 / 105060):

| Case | Plan (A0) | Model typ (8 ch) | A5 | **A6** |
|---|---|---|---|---|
| S1 SE 32 Ω | 663 mW · 12.8 / 16.3 h | same | 694 mW · 12.2 / 15.6 h | **739 mW · 11.4 / 14.6 h** |
| S2 balanced 300 Ω | 642 mW · 13.2 / 16.8 h | 781 mW · 10.8 / 13.8 h | 812 mW · 10.4 / 13.3 h | **881 mW · 9.6 / 12.3 h** |
| B32 balanced IEM | 723 mW · 11.7 h | 861 mW · 9.8 h | 893 mW · 9.5 h | **977 mW · 8.7 h** (Adafruit 328) |

The SoC estimate (48 % of the draw) dominates the uncertainty of every row. The deltas between columns are more reliable than the absolute hours.

**Thermal per channel (A6, est.):**

- **Per package** (one leg, both halves), worst-case continuous sine into balanced 32 Ω (each leg sees 16 Ω): Pdiss ≈ 2·Vs·Vp/(π·R) − Vp²/(2R) = 0.44 W at the 200 mA limit, plus 0.06 W quiescent, so **≈ 0.5 W**.
- With θJA 47.6 °C/W (JEDEC board, SBOS727B §6.4) that is **+24 °C** at the junction. This is the same per-package figure as today's plan (0.5 W for two legs at ±5 V), because the load is now spread over twice the silicon.
- **Whole stage at the full-scale sine:** ≈ 2.0 W in the four balanced packages, plus ≈ 0.55 W in the two LDOs (1 V × 275 mA each), plus the converter losses. That is ≈ 3.5 W into the body (est.).
- Music sits about 10–20 dB below full-scale sine, so this is a bench condition. The body's internal ambient and the effective θJA in the case are **UNVERIFIED**: add a balanced 32 Ω full-scale soak to the prototype tests.

**PCB area (est.):**

- Two more VSON-10 packages (3 × 3 mm), plus about 12 more 0603 passives each (doubled networks, ballast resistors, bypass): ≈ 40–55 mm² per package with spacing, so **≈ +80–110 mm²**.
- The LT3045 (DFN-10, 3 × 3 mm) and LT3094 (DFN-12, 3 × 3 mm) package sizes come from LCSC listings. They are no larger than the TPS7A49 / TPS7A30 (HVSSOP-8).

**Availability (JLCPCB/LCSC, 2026-10-22):**

| Part | Stock |
|---|---|
| OPA1622IDRCR | 675 (Digi-Key 4,558 on 2026-10-21, BOM) |
| LT3045EDD#TRPBF | 3,148 |
| LT3094EDD#PBF | 533 (BOM line 26 names LT3094EDD#TRPBF, C670493: 1,417 in BOM v1.2) |

With six OPA1622 per board, 675 at LCSC covers only ≈ 110 boards; Western stock is the volume source.

### 4.6 B: OPA1622 half + BUF634A per leg

The BUF634A delivers ±250 mA continuous, with a current limit of ±350–550 mA (SBOS948F §7.5–7.6, §8.3.1).

| | Low-Iq mode | Wide-bandwidth mode |
|---|---|---|
| Quiescent current | 1.5 mA | 8.5 mA |
| Bandwidth | 35 MHz | 210 MHz |
| HD3 at 2 Vpp, 20 kHz, 100 Ω, open loop | **−40 dBc** | −77 dBc |
| Output headroom at ±100 / ±150 mA | 2.0 / 2.2 V typ, 2.2 / 2.5 V max | same |

- **Rails:** the buffer's headroom is larger than the OPA1622's 1.9 V. Reaching 3.3 V peak at 200 mA per leg needs ≈ ±6.5 V.
- **Low-Iq mode:** the OPA1622 loop gain at 20 kHz is ≈ 52 dB (8 MHz GBW). The 20 kHz HD3 would then be ≈ −92 dBc (est., **UNVERIFIED**), well short of the OPA1622 alone. Against the 100 % audio rule.
- **Wide-bandwidth mode:** the quality issue goes away, but each leg costs 2.6 + 8.5 = 11.1 mA against 5.2 mA for paralleled halves. Worse autonomy than A6.
- **Area and stock:** four extra packages; the 3 × 3 mm DRB has 32 units at LCSC (SOIC: 4,119).
- **Verdict:** rejected.

### 4.7 C: TPA6120A2

| Figure (SLOS431B §7.3–7.6) | Value |
|---|---|
| Output current | 700 mA per channel |
| Minimum supply | ±5 V |
| Quiescent current | **11.5 mA typ, 13 mA max per channel** at ±5 V |
| THD+N, 32 Ω, 10 mW, ±5 V | **−101 dB** |
| SNR, ±5 V, A-weighted | 116 dB |
| Minimum load | 16 Ω |

- **Quality:** −101 dB is 15 dB worse than the OPA1622 at the same point, and the 116 dB SNR is below the CS43198's 130 dB dynamic range.
- **Autonomy:** a balanced output needs two packages (46 mA per rail): ≈ 0.6 W more than A0 in the balanced cases.
- **Stock:** LCSC DWPR 2,127, RGYT 139.
- **Verdict:** rejected on quality and Iq.

### 4.8 D: other op-amps and E: dedicated headphone driver ICs

**Other op-amps** (short-circuit current; supply current per channel):

| Part | Output current | Supply current | Source |
|---|---|---|---|
| OPA1656 | ±100 mA | 3.9 mA | SBOS901C |
| OPA1688 | ±75 mA | 1.6 mA | SBOS724A |
| OPA1692 | ±50 mA | 0.65 mA | datasheet |

- None of them drives more current than the OPA1622, so none closes the gap alone. As the front end of a buffer they inherit option B's problems.
- The INA1620 has the OPA1622's output stage (+145 / −130 mA, 2.6 mA, SBOS859B) and adds nothing for power.
- ADA4807: datasheet not retrieved (**UNVERIFIED**). Not pursued, because its class is low-voltage, low-current.

**Dedicated headphone driver ICs:**

- The SGM8262 is the amplifier in both the Shanling M1 Plus and the FiiO JM21. It is the segment's own answer.
- **Not adoptable now:**
  - its datasheet could not be read (**UNVERIFIED** output current, Iq, THD+N);
  - every SGM8262 listing at LCSC shows **0 stock** (SOIC-8 and TDFN-3×3).
- That conflicts with the sourcing rule.
- It is worth a datasheet read and a Western-stock check before the schematic is frozen, as the only option that might beat A6 on Iq.

---

## 5. Recommendation: A6

### 5.1 What changes

The stage is the same OPA1622 class AB with more silicon per leg and 1 V more rail:

1. **Six OPA1622.** The 4.4 mm output takes one package per leg (L+, L−, R+, R−), both halves paralleled through 0.5–1 Ω ballast resistors with doubled-value difference-amplifier networks (§4.5). The 3.5 mm output keeps two packages with paralleled halves, as planned. EN gating per output stays.
2. **±6.0 V amplifier rails:**
   - TPS65131 pre-rails at +7.0 / −7.0 V;
   - **LT3045 / LT3094** at ±6.0 V (the BOM v1.2 proposal, now required rather than optional);
   - LDO headroom stays at 1 V.
3. **CS43198 at `+1dB_EN` = 0** (−115 dB THD+N, 1.73 Vrms), with the amplifier gain set to **≈ 1.6** (R2/R1 ≈ 1.6 kΩ / 1.0 kΩ):
   - **SE:** full scale reaches the clip point into 32 Ω.
   - **Balanced 32 Ω:** current-limited about 2 dB below full scale.
   - **Balanced 300 Ω:** reaches ≈ 100 mW.

### 5.2 What it delivers (est.)

| | A6 | Shanling M1 Plus | FiiO JM21 |
|---|---|---|---|
| SE 32 Ω | **≈ 240 mW** | 195 mW | 245 mW |
| Balanced 32 Ω | **≈ 640 mW** (490–760 mW) | 660 mW | 700 mW |
| SE 16 Ω | ≈ 320 mW | — | — |
| Balanced 300 Ω | ≈ 100 mW | — | — |

- Distortion and noise stay at the OPA1622 and CS43198 datasheet levels.
- The DAC is no longer in its −105 dB `+1dB_EN` mode.

### 5.3 Honest cost

**Autonomy, core SE session (S1):**

- Draw 663 → 739 mW (**+76 mW, −11 %**).
- Adafruit 328: 12.8 → 11.4 h, so 88 % → 79 % of the category average.
- 105060 target: 16.3 → 14.6 h, so 112 % → **101 %**: still at the average.
- The ±6 V rails and the LT LDOs are paid in every mode, IEMs included.

**Autonomy, balanced:**

- Against the board plan: 300 Ω 13.2 → 9.6 h on the Adafruit 328 (−27 %); on the 105060, 16.8 → 12.3 h (112 % of the 11 h average).
- Against the battery model's typical case (which already assumed eight channels): −11 %.
- Balanced IEMs: 8.7 h on the Adafruit 328.

**Body sizing (battery analysis §11):**

- The 85 %-of-average target at 20 mm (≈ 9.1 Wh at 0.66 W) would need ≈ 10.1 Wh at 0.74 W.
- The 20 mm body (option A there) leaves the table unless the measured SoC draw comes in low.
- The 24 mm card-ratio body with a 105060 pack (option F there) still reaches the average.

**Area:** ≈ +80–110 mm² (est.) and two more OPA1622 per board.

**Power design (BRD-049), full-scale continuous sine into balanced 32 Ω, both channels:**

| Item | Load | Rating | Use | Verdict |
|---|---|---|---|---|
| Each ±6 V rail | 2 × 2 × 200 mA / π + 20.8 mA ≈ **275 mA** | TPS7A4901 150 mA / TPS7A3001 200 mA | 183 % / 138 % | **Fail**: the LDO swap is mandatory |
| LT3045 / LT3094 | 275 mA | 500 mA (BOM v1.2, **UNVERIFIED**) | 55 % | OK, pending the datasheets |
| TPS65131 inverter, peak inductor current (SLVS493E Eq. 4) | 1.29 A at VIN 3.5 V, 1.43 A at 3.0 V | switch limit 1.8 A min | 72 % / 79 % | **At the limit of the 80 % rule.** The maximum-output-current curves (Figures 6-2, 6-4) must confirm ≈ 275 mA at ±7 V; otherwise split the pre-rails (part not evaluated here) |
| TPS65131 boost (Eq. 3) | 0.86–1.00 A | 1.8 A | 48–56 % | OK |
| Inductors DFE252012F-4R7M | ≈ 1.45 A peak | Isat **UNVERIFIED** | — | Check the Murata sheet |
| Rectifiers PMEG2010AEH | 275 mA average; reverse voltage ≈ 11.4 V | 1 A, 20 V | 28 % / 57 % | OK |
| VSYS draw of the headphone rails | ≈ 4.8 W: **1.38 A at 3.5 V, 1.61 A at 3.0 V** (est., η 0.8) | interim pack budget 1.6 A (power tree §4.7) | — | **Fails on the interim pack.** Today's plan draws ≈ 0.52 A in the same case. On the Adafruit 328 the full-scale balanced 32 Ω case needs a software output-power ceiling or the ADR 0011 pack (4.8 A budget) |

Music averages far below a continuous full-scale sine, but BRD-049 asks for margin and protection in the worst continuous case. The table above must enter power tree §4.10 before adoption.

### 5.4 Why not the cheaper A5

- A5 (±5 V) saves ≈ 45 mW in S1 (12.2 h instead of 11.4 h).
- It stays ≈ 1.1 dB under the Shanling M1 Plus single-ended (150 mW against 195 mW), and its SE 32 Ω figure is swing-limited at the ±5 V rail.
- A middle point, ±5.5 V, reaches ≈ 200 mW SE at 717 mW in S1 (11.8 h), but with no margin on an estimated headroom.
- **Proposal:** lay out for ±6 V. Trim to ±5.5 V only if the prototype's measured swing at 120 mA shows the margin.

---

## 6. Open points and verification

1. **Paralleled OPA1622 halves:** current sharing, stability with the ballast resistors and 400 pF headphone loads (SBOS727B §8.2.2), and THD+N at 32 Ω and 16 Ω. Simulate (TINA-TI), then measure on the first board.
2. **Swing against current at ±6 V** (SBOS727B Figure 38 is plotted at ±18 V): confirm ≥ 3.9 V peak at 122 mA.
3. **LT3045 / LT3094:** read the datasheets for noise, PSRR at 1.25 MHz, ground current, the soft-start law (ramp symmetry, BOM D3) and package thermals.
4. **TPS65131 at ±7 V and 275 mA per rail from VIN 3.0 V:** WEBENCH or SPICE (power tree risk 3), and the inductor saturation current.
5. **Interim-pack power ceiling:** a policy for the full-scale balanced 32 Ω case on the Adafruit 328 (BRD-050, ADR 0011).
6. **SGM8262:** datasheet and Western stock, as a possible lower-Iq alternative.
7. **Prototype tests:**
   - maximum power at 1 % and at 0.001 % THD+N into 16, 32 and 300 Ω, SE and balanced;
   - idle noise and output impedance;
   - a full-scale balanced 32 Ω soak in the closed body.
8. **Requirement text:** BRD-022 (Draft) names four OPA1622. Adopting A6 changes it to six, which is the maintainers' call.

---

## 7. Sources

- Texas Instruments:
  - OPA1622, SBOS727B, <https://www.ti.com/lit/ds/symlink/opa1622.pdf> (sha256 in BOM v1);
  - TPA6120A2, SLOS431B, <https://www.ti.com/lit/ds/symlink/tpa6120a2.pdf>;
  - BUF634A, SBOS948F, <https://www.ti.com/lit/ds/symlink/buf634a.pdf>;
  - OPA1656, SBOS901C, <https://www.ti.com/lit/ds/symlink/opa1656.pdf>;
  - OPA1688, SBOS724A, <https://www.ti.com/lit/ds/symlink/opa1688.pdf>;
  - OPA1612, <https://www.ti.com/lit/ds/symlink/opa1612.pdf>;
  - INA1620, SBOS859B, <https://www.ti.com/lit/ds/symlink/ina1620.pdf>;
  - OPA1692, <https://www.ti.com/lit/ds/symlink/opa1692.pdf>;
  - TPS65131, SLVS493E; TPS7A49, SBVS121E; TPS7A30, SBVS125D (all via the `libs/parts` sheets and BOM v1);
  - product pages for BUF634A and TPA6120A2 (status Active), read 2026-10-22.
- Cirrus Logic: CS43198, DS1156F2, Table 3-4 and §4.2.3 (cached copy, sha256 in BOM v1).
- Analog Devices: LT3045 and LT3094 (not retrieved; figures from BOM v1.2, **UNVERIFIED**).
- FiiO: <https://www.fiio.com/jm21> and <https://www.fiio.com/m21>, read 2026-10-22.
- HiBy: <https://store.hiby.com/products/hiby-r3pro-ii> and <https://store.hiby.com/products/hiby-r6-iii-2025>, read 2026-10-22.
- Shanling M1 Plus: figures provided by the maintainers (maker's, via a retailer listing). Not re-read (**UNVERIFIED**).
- Stock: JLCPCB parts API (LCSC), 2026-10-22.
- OpenDAP: [BOM v1](../specs/bom-v1.md), [power tree v0](../specs/power-tree-v0.md), [battery-life analysis](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-battery-life-analysis.md).
