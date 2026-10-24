# Antennas and RF exposure for the Murata Type 2EL in the T1 (2026-10)

- **Date:** 2026-10-24
- **Task:** E1.13 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md). Decided in [ADR 0018](../adr/0018-antennas-and-certification-route.md).
- **Question:** which antennas from Murata's certification lists serve the T1, which of them fit the top band with a keep-out, what route each regulatory market needs (listed antenna or permissive change), and what the handheld T1 needs for RF exposure (SAR), given Murata's transmit powers.
- **Regulatory strategy (maintainers, 2026-10-24; [RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md) "regional"):** prototypes ([RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) Q1) use the most accessible, best-available part; certification lists do not constrain them, only the RF copy rules and a layout that keeps every certified option open. Products (Q3) are regional variants, each with the antenna and transmit-power table of its market.
- **Inputs:**
  - Murata *Type 2EL Radio Law Certification Application Note* CER-0248 Rev. 6.0 (2025-03-04, sha256 `f37a1725…69ed`), cited "CER-0248"; Murata *Type 2EL/2DL Hardware Application Note* E2B-09-1413 Rev. 9.0 (2026-05-21, sha256 `aade44c5…76ea`), cited "E2B-09-1413". Both re-read for this study; the hashes match `parts-lib/manifest.toml`.
  - parts-lib sheets [LBES5PL2EL-923](https://github.com/opendap-project/parts-lib/blob/main/Murata/LBES5PL2EL-923.md), [146187-0050](https://github.com/opendap-project/parts-lib/blob/main/Molex/146187-0050.md), and the new [146153-0050](https://github.com/opendap-project/parts-lib/blob/main/Molex/146153-0050.md) and [W24P-U](https://github.com/opendap-project/parts-lib/blob/main/Inventek/W24P-U.md).
  - [PCB design constraints](../specs/pcb-design-constraints.md) PCB-R-01 to PCB-R-07; [battery selection](2026-10-battery-selection.md) §2.2–2.3; [ADR 0016](../adr/0016-front-side-height-under-the-display.md) (body 59.5 × 94.3 × 25.0 mm, height zones); [t1 ADR 0003](https://github.com/opendap-project/t1/blob/main/docs/adr/0003-tentative-body-size.md).
  - [Design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.2–2.3 and the [compliance regimes catalog](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/research/2026-10-compliance-regimes.md) §2.1, §2.5.
  - 47 CFR 1.1307 (CFR 2025 edition, govinfo XML, read 2026-10-24); ISED RSS-102 Issue 6 (2023-12-15, ISED web page read 2026-10-24).
- **Conventions:** **UNVERIFIED** means no primary source was read in this session. "(vendor claim)" means the only source is the maker's or a distributor's own text. Stock is from distributor pages on 2026-10-24; Mouser, Newark, TME, Arrow and RS figures come through the [FindChips](https://www.findchips.com/) aggregator, LCSC from the JLCPCB parts API, Digi-Key from its search page. Prices are USD at quantity 1.

## 0. Summary

1. **Four external antennas appear on all three lists** (FCC Table 20, ISED Table 36, Japan Table 56): Molex 146153, Molex 219611, Unictron WT32D1-KX and Inventek W24P-U (2.4 GHz only). Murata's own trace antenna is on all three too, but needs a 40 × 40 mm board and 20 mm clearance to metal, which the T1 cannot give. Japan's list adds twelve more, among them the Molex 146187 of BOM line 57.
2. **The Molex 146153-0050 is the antenna.** It is a 34.9 × 9.0 × 0.1 mm flexible balanced dipole with a U.FL plug, registered at 3.2 dBi (2.4 GHz) and 4.25 dBi (5 GHz) in all three markets, and the best-stocked of the candidates (Digi-Key 15,886, Mouser 21,613, LCSC 113). It is therefore both the prototype antenna and the production antenna of every Murata-covered region, so prototype measurements carry over.
3. **It does not lie flat in the 7.0 mm top band; it fits on the inside of the top wall.** The wall face behind the board is about 56.3 × 14.2 mm, the 146153 needs 34.9 × 9.0 mm, and the battery pocket is 7.0 mm away. A second antenna does not fit there with a keep-out (§3). The T1 therefore uses Murata's **shared-antenna configuration** (Wi-Fi, Bluetooth on ANT0), and the layout keeps the dedicated configuration open.
4. **Molex's "-0050" is the 50 mm length class.** The 146187-0050's 43.3 mm cable is drawn from the antenna to the plug; Molex's 146153-1050 and 219611-0050 drawings use the same convention for their "50 mm" variants, and Murata registers "146153 (50 mm cable)". The earlier finding that the 146187-0050 is "shorter than the 50 mm registered in Japan" is most likely a reading of the nomenclature, not a real shortfall (**UNVERIFIED** until Murata confirms how its "cable length" is measured). It no longer matters for the decision: the 146187 is not on the FCC or ISED lists.
5. **Routes.** USA: listed antenna, Class II permissive change by Murata (mobile to portable, with the T1's SAR report). Canada: listed antenna, Class 4 permissive change by Murata. EU: no antenna list; CE self-declaration with Murata's conducted reports, radiated tests on the T1 and EN 50566 SAR. Japan: listed antenna, no filing. Murata's certification covers no other market.
6. **SAR is needed in the USA, Canada and the EU; no placement avoids it.** At the T1's separations (below 5 mm) the FCC exemption threshold is 2.74 mW at 2.45 GHz and 1.44 mW at 5.5 GHz, RSS-102's is 3 mW and 1 mW; the module transmits up to 100 mW (FCC 2.4 GHz) and 63 mW (FCC 5 GHz) conducted. Even 25 mm of separation would only raise the FCC threshold to 58.6 mW and 40.7 mW.

## 1. The certification lists

### 1.1 Lists side by side

Peak gain in dBi at 2.4 GHz / 5 GHz as registered (CER-0248 Tables 20, 36, 56; E2B-09-1413 Tables 3, 4).

| Antenna | Type, connector | FCC (T20) | ISED (T36) | Japan (T56) | Cable registered (E2B-09-1413) | Notes |
|---|---|---|---|---|---|---|
| Molex 146153 | Dipole, u.FL | 3.2 / 4.25 | 3.2 / 4.25, "50 mm cable" | 3.2 / 4.25 | 50 mm or more | — |
| Molex 219611 | Dipole, u.FL | 2.67 / 3.67 | 2.67 / 3.67, "50 millimeter" | 2.67 / 3.67 | 40 mm or more | Wi-Fi 6E part |
| Unictron WT32D1-KX | Dipole, MHF I | 3.0 / 4.0 | 3.0 / 4.0 | 3.0 / 4.0 | 119 mm or more | No distributor listing found |
| Inventek W24P-U | Dipole, u.FL | 3.2 / — | 3.2 / — | 3.2 / — | 90 mm or more | 2.4 GHz only |
| Murata Type2EL_Antenna | Monopole, PCB trace | 3.6 / 4.6 | 3.6 / 4.6 | 3.6 / 4.6 | — | ANT0 only; Gerber copy |
| Molex 206994 | Monopole, u.FL | — | — | 3.6 / 3.6 | 100 mm or more | Japan only |
| Molex 146187 | Dipole, u.FL | — | — | 3.2 / 4.25 | 50 mm or more | Japan only; BOM line 57 today |
| Unictron AA258 | Dipole, MHF I | — | — | 0.9 / 3.8 | 100 mm or more | Japan only |
| Antenova SRF2W012 | Dipole, MHF I | — | — | 3.0 / 4.0 | 100 mm or more | Japan only |
| Laird EMF2471A3S; KAVX 1001932FT, 1001932PT | Dipole, MHF I | — | — | 2.4 / 4.4; 2.5 / 4.4; 2.03 / 4.45 | 100 mm (or more) | Japan only |
| Unictron TA-38B-A-W01, TA-6B-A-WE01; Taoglas GW.48.A151, GW.40.2153, GW.52.A153 | Dipole, RSMA | — | — | 1.82–3.15 / 3.07–4.59 | — | External whips; Japan only |

- In the dedicated configuration, ANT1 (Bluetooth and 802.15.4) may use the four external antennas 146153, 219611, WT32D1-KX and W24P-U; the trace antenna is for ANT0 only (CER-0248 §2.1.6.1, §2.2.4.1).
- ISED certifies both configurations: HVIN LBES5PL2EL-SANT and LBES5PL2EL-DANT, IC: 772C-LBES5PL2EL (CER-0248 p. 34). FCC ID: VPYLBES5PL2EL (CER-0248 p. 27). Japan: certification 001-P02018 (CER-0248 §2.4.7).
- **The largest overlap is the four external antennas.** Of them, only the 146153 and 219611 cover both bands and are stocked.

### 1.2 The trace antenna is out

Murata's Type2EL_Antenna needs a board of at least 40 × 40 mm around it and at least 20 mm from the antenna to metal or ground on every side (E2B-09-1413 §3.5.5, Table 7), and the antenna plus its feed line copied from Murata's Gerber (CER-0248 §2.1.5.1). The T1's top band is 7.0 mm deep and the board fills the body. It is not a candidate.

### 1.3 What the cable length means

| Part | Molex length class | Cable drawn | Source |
|---|---|---|---|
| 146153-1050 (MHF4L plug) | 50 mm | L1 = 43.3 mm | Drawing 1461531050 rev. B1, item table |
| 219611-0050 | 50 mm | L1 = 43 mm, L2 = 50 mm | Drawing 2196110100 rev. A1, item table |
| 146187-0050 | 50 mm | L = 43.3 mm | Drawing 1461870050 rev. D |
| 146153-0050 | "50MM" (Digi-Key description), "50.00mm cable length" (vendor claim) | Not drawn here (drawing not obtained) | — |

Molex names its variants by a nominal length (−0050, −0100 … −0300) and draws the bare cable shorter by about 6.7 mm, the antenna-end solder joint and the plug. Murata's ISED table registers "146153 (50 mm cable)" and "219611 (50 millimeter …)", that is the −0050 class. Reading E2B-09-1413's "50 mm or more" as the Molex length class, the 146187-0050 complies. **UNVERIFIED** until Murata says which length it measures (§6, question 3).

## 2. Candidates for the T1

| Antenna | Size (mm) | Gain registered (dBi) | Cable (−0050 class) | Plug | Availability (2026-10-24) |
|---|---|---|---|---|---|
| **Molex 146153-0050** | **34.9 × 9.0 × 0.10** flex (1461531050 drawing; same flex) | 3.2 / 4.25 (FCC, ISED, JP) | 50 mm class | U.FL / MHF1 (Digi-Key) | Digi-Key 15,886 @ $2.27; Mouser 21,613 (FindChips range $1.34–2.27); Newark 6,592; TME 1,068; LCSC C916292 113 @ $2.49 |
| Molex 219611-0050 | 35.4 × 15.4 × 0.23 flex | 2.67 / 3.67 (FCC, ISED, JP) | L1 43 / L2 50 mm | MHF-1, 2.5 mm high | Mouser 4,593; Arrow 497; TME 600; Digi-Key listed @ $10.11, stock not shown; LCSC C6991332 0 |
| Inventek W24P-U | 30 × 5.0 PCB, 0.5 mm high (Digi-Key; the spec prints ".05") | 3.2 / — (FCC, ISED, JP) | 90 mm | U.FL | Digi-Key 8,353 @ $1.48; Mouser 2,491; LCSC C6604641 0 |
| Molex 146187-0050 | 40.95 × 9.00 × 0.70 rigid PCB | 3.2 / 4.25 (JP only) | L 43.3 mm (50 mm class) | U.FL, 2.5 mm high | Mouser 3,831 @ $1.78; TME 3,488 @ $1.55; Newark 631; Digi-Key listed @ $2.80, stock not shown; LCSC C6390118 12 @ $1.92 |
| Unictron WT32D1-KX | **UNVERIFIED** | 3.0 / 4.0 | 119 mm or more | MHF I | No listing on FindChips or LCSC |

Gain of the 146153 by cable length: Murata registers 3.2 / 4.25 dBi. Distributors print other figures for the same series (Digi-Key "3.2/4.75 dBi" for the −0050; RS 4.25 dBi for the 50 mm and 3.5–4.0 dBi for longer cables) (vendor claims). The 5 GHz figure that bounds the certification is Murata's 4.25 dBi; Molex's product specification PS-146153-100-001, which would settle the per-length gain, was not obtained (Molex's site refused automated fetches). The tuned antenna in the T1 must measure at or below the registered gain (§4.1).

## 3. Fit in the T1

### 3.1 The space

| Quantity | Value | Basis |
|---|---|---|
| Body | 59.5 × 94.3 × 25.0 mm | ADR 0016 item 2 |
| Inner cavity width | 59.5 − 2 × 1.6 = 56.3 mm | Walls 1.6 mm (battery selection §2.3) |
| Top band (y) | **7.0 mm** at the 25 mm body: the HAT device-side piece sits over the bottom band | Battery selection §2.3, §2.5; pocket 63.8 mm long (ADR 0016) |
| Top band usable width | ≈ 54 mm: cavity less two screw bosses and the 0.8 mm rib | Battery selection §2.3 |
| Back-side height in the bands (z) | 14.2 mm | PCB-Z-02 (ADR 0016 item 4) |
| Top-wall inner face behind the board | ≈ 56.3 × 14.2 mm | Arithmetic from the two lines above |
| Nearest metal to the top band | Battery pouch and the metal pocket floor (ADR 0016 item 3), 7.0 mm from the top wall; microSD shell (placement open, ADR 0016); HAT metal is at the bottom | — |

**Keep-out to metal.** Neither Molex's application specification (AS-146153-100-001, not obtained) nor Inventek's specification states a clearance. This study sets a **provisional ≥ 5 mm** from the radiating element to any metal (battery, pocket floor, microSD shell, screw inserts, display frame), the upper end of the "~3–5 mm" of the battery selection §2.3, to be confirmed or changed by return-loss and efficiency measurements in the prototype case (**UNVERIFIED**).

### 3.2 Arrangements

| Arrangement | Fits? | Keep-out to battery | Verdict |
|---|---|---|---|
| 146153 flat in the top band | **No**: 9.0 mm wide against a 7.0 mm band | — | Out |
| **146153 on the inside of the top wall**, long axis along x, centred away from the microSD corner | **Yes**: 34.9 × 9.0 on 56.3 × 14.2, 2.6 mm free above and below, ≥ 10 mm free at each end | 7.0 mm (the band) | **Chosen for ANT0** |
| 219611 on the top wall | **No**: 15.4 mm tall against 14.2 mm | — | Out (fallback only with a deeper back) |
| 146187 on the top wall | Yes: 40.95 × 9.00 | 7.0 mm | Fits, Japan only, 0.7 mm rigid |
| Two antennas on the top wall end to end (146153 + W24P-U) | **No**: 34.9 + 30 = 64.9 mm against 56.3 mm | — | Out |
| Two antennas stacked on the top wall (9.0 + 5.0 mm) | 14.0 mm in 14.2 mm: no gap between them | 7.0 mm | Out: no isolation |
| W24P-U flat in the top band | Yes: 5.0 mm in 7.0 mm | ≈ 1–2 mm | Below the keep-out; a Q1 experiment only |
| Second antenna on a side wall, long axis along y | 2.5 mm side margin + 0.4 mm clearance to the pack | ≈ 2.9 mm | Below the keep-out |

**Result:** one antenna fits the T1 with its keep-out: the 146153-0050 on the top wall. A second one does not, unless the case grows or the battery shrinks, which the product rules do not allow for this (battery autonomy is a top priority, T1-009).

### 3.3 Shared or dedicated configuration

Murata certifies both (§1.1). In the shared configuration ANT0 carries Wi-Fi 2.4 GHz, Wi-Fi 5 GHz, Bluetooth and 802.15.4, with pin 18 tied to pin 23 through 10 pF (E2B-54-1953 §4.3.3; E2B-09-1413 Figure 9). In the dedicated configuration ANT1 carries Bluetooth and 802.15.4 to a second antenna (E2B-09-1413 Figure 10) and Linux loads `WlanCalData_ext_dANT.conf` (E2B-09-1413 §4.4).

| Criterion | Shared (one antenna) | Dedicated (two antennas) |
|---|---|---|
| Fits with the keep-out | Yes | No (§3.2) |
| Simultaneous transmission from two radiators (SAR sum) | Not from two antennas; Wi-Fi and Bluetooth share ANT0 by the module's coexistence (whether any mode transmits both at the same instant is **UNVERIFIED**) | Yes: sum of ratios or SPLSR (§5.4) |
| Bluetooth audio while Wi-Fi is busy | Time-shared airtime; dropouts at the highest codec rate are the risk to measure | Better isolation, less airtime contention |
| Cost | One antenna | Two antennas |

The audio experience decides between them by measurement, not by assumption: the prototype carries the dedicated option (second U.FL and positions fitted) so both can be compared (V-row in ADR 0018).

## 4. Certification routes per market

### 4.1 USA (FCC)

- **Antenna:** 146153 is listed (Table 20); no Class I change is needed for the antenna itself.
- **Matching:** tuning the matching network on the final enclosure is allowed, but Murata asks to check the three points of a Class I change: same antenna type, gain no higher than listed, spurious emissions no more than 3 dB worse than the certification report (CER-0248 §2.1.5.1, §2.1.3.12). The T1 must document these with a gain measurement and a spurious scan.
- **RF exposure:** the grant is for mobile use (≥ 20 cm). Portable use needs a SAR test of the T1 and a **Class II permissive change** filed by Murata, "from a Mobile equipment to a Portable equipment", except when only Bluetooth is used (CER-0248 §2.1.3.6, §2.1.3.8).
- **What Murata needs from OpenDAP for the Class II filing** (outward contact, later): the SAR test report of the T1 at the maximum tune-up powers it ships (body-worn and extremity positions, every surface and edge near the antenna, simultaneous-transmission analysis); the antenna's type and gain documents; the internal photos and antenna placement; the TX-power table the T1 ships; the user-manual RF exposure text. The test lab procedure follows the FCC KDBs for portable devices and 802.11 SAR (447498, 248227) with IEC/IEEE 62209-1528 (KDB numbers as in the compliance catalog, **UNVERIFIED** editions).
- **Unlisted antenna (if ever):** equivalent type with lower gain, Class I permissive change approved by Murata, evaluated against FCC KDB 178919 (E2B-09-1413 §3.5.1, p. 14).
- **Host obligations unchanged:** "Contains FCC ID: VPYLBES5PL2EL", Part 15B SDoC of the T1 with the module installed (CER-0248 §2.1.3.8, §2.1.3.10).

### 4.2 Canada (ISED)

- **Antenna:** 146153 is listed (Table 36).
- **RF exposure:** portable use needs a SAR test and a **Class 4 permissive change** using the SAR report, through Murata (CER-0248 p. 35).
- **What it needs:** the same SAR report, evaluated against RSS-102 Issue 6 (§5.3), plus the HVIN of the configuration used (SANT for shared).

### 4.3 EU (RED)

- **No antenna list.** Murata supplies conducted test reports (EN 300 328 v2.2.2, EN 301 893 v2.1.1, EN 300 440 v2.1.1) and EN 62311; only their antenna-terminated conducted sections may enter the T1's technical file. Radiated data is acquired on the T1, and the CE declaration is OpenDAP's (CER-0248 §2.3).
- **Antenna:** the same 146153-0050, so one part serves every region. EIRP at Murata's EU tables with 3.2 / 4.25 dBi: 2.4 GHz Wi-Fi 16 dBm (14 ± 2, Table 38) → 19.2 dBm EIRP; 5 GHz 17 dBm (15 ± 2, Table 42) → 21.25 dBm; Bluetooth 6 dBm (3 ± 3, Table 41) → 9.2 dBm (arithmetic; the limits of each harmonised standard are checked by the test lab).
- **RF exposure:** EN 62479 low-power exclusion (20 mW, **UNVERIFIED** value) covers Bluetooth at the EU table (6 dBm = 4 mW) but not Wi-Fi (40–50 mW): EN 50566 with SAR per EN IEC/IEEE 62209-1528 applies.
- **UK:** expected to follow the EU variant under the UK's own regulations (**UNVERIFIED**; not studied).

### 4.4 Japan (MIC)

- **Antenna:** 146153 is listed (Table 56), within certification 001-P02018. No filing. An unlisted antenna can only be added to Murata's certification by Murata (E2B-09-1413 §3.5.1, p. 14); there is no host-side permissive change.
- **RF exposure:** whether Japan's SAR rules apply to a 2.4 / 5 GHz WLAN device of the T1's class is **UNVERIFIED** (question to Murata or a Japanese certification body).
- **Power:** Murata's Japan tables are typical values: Wi-Fi 2.4 GHz 15–16 dBm, 5 GHz 12–14 dBm, Bluetooth LE 5 dBm, BR 12 dBm high-power option (Tables 49–53).

### 4.5 Other markets

CER-0248 covers FCC, ISED, EU and Japan only. Korea (KC), Australia and New Zealand, China and others need their own module certification or Murata's; a regional variant for them is not defined until the maintainers open those markets.

## 5. RF exposure

### 5.1 The T1's transmit powers

Maximum conducted power = Murata's "maximum tune-up" setting plus its tolerance (CER-0248). EIRP with the 146153 (3.2 / 4.25 dBi); ERP = EIRP − 2.15 dB.

| Radio, region | Highest setting | Max conducted | ERP | EIRP | Reference |
|---|---|---|---|---|---|
| Wi-Fi 2.4 GHz, FCC/ISED | 802.11b ch 3–9, 18.0 ± 2.0 dBm | 20 dBm = 100 mW | 127 mW | 209 mW | Tables 6, 22 |
| Wi-Fi 5 GHz, FCC/ISED | 802.11a, 16.0 ± 2.0 dBm | 18 dBm = 63 mW | 102 mW | 168 mW | Tables 10, 26 |
| Bluetooth BR / LE, FCC/ISED | 13.0 ± 3.0 dBm | 16 dBm = 40 mW | 51 mW | 83 mW | Tables 9, 25 |
| 802.15.4, FCC/ISED | 15.0 ± 3.0 dBm | 18 dBm = 63 mW | — | — | Table 9; **not used**: the T1 does not wire the module's SPI (BOM line 55) |
| Wi-Fi 2.4 GHz, EU | 14.0 ± 2.0 dBm | 16 dBm = 40 mW | 51 mW | 83 mW | Table 38 |
| Wi-Fi 5 GHz, EU (36–140) | 802.11a 15.0 ± 2.0 dBm | 17 dBm = 50 mW | 81 mW | 133 mW | Table 42 |
| Bluetooth, EU | 3.0 ± 3.0 dBm | 6 dBm = 4 mW | 5 mW | 8 mW | Table 41 |

Measured on Murata's evaluation board: 802.11b 18 dBm at 150 + 235 mA, Bluetooth 13 dBm (E2B-09-1413 Tables 18, 20).

### 5.2 FCC (47 CFR 2.1093, 1.1307(b)(3))

The T1 is a portable device. A single source is exempt if its available maximum time-averaged power is ≤ 1 mW, or if the larger of that power and its ERP is ≤ P_th, for 0.5–40 cm and 0.3–6 GHz (1.1307(b)(3)(i)(A), (B), CFR 2025 text). P_th itself is printed as an image in the CFR; the formula used here, P_th = ERP_20cm × (d / 20 cm)^x with x = −log10(60 / (ERP_20cm × √f)), ERP_20cm = 3060 mW at 1.5–6 GHz, is transcribed from the compliance catalog (**UNVERIFIED** against the image). Below 0.5 cm the 0.5 cm value is used.

| Separation d | 2.45 GHz | 5.2 GHz | 5.5 GHz | 5.8 GHz |
|---|---|---|---|---|
| ≤ 0.5 cm | **2.74 mW** | 1.50 mW | **1.44 mW** | 1.38 mW |
| 1.0 cm | 10.3 mW | 6.3 mW | 6.1 mW | 5.9 mW |
| 1.5 cm | 22.2 mW | 14.5 mW | 14.1 mW | 13.7 mW |
| 2.0 cm | 38.3 mW | 26.3 mW | 25.6 mW | 24.9 mW |
| 2.5 cm | 58.6 mW | 41.7 mW | 40.7 mW | 39.7 mW |

(Arithmetic.)

- **The T1's separations are all below 0.5 cm.** The 146153 on the top wall is about 1.6 mm (wall) from the top face, and about 2.6 + 1.5 + 0.4 ≈ 4.5 mm from the back face (§3.1). A T1 in a pocket during playback is a body-worn case; in the hand, an extremity case.
- **Wi-Fi 2.4 GHz at 127 mW ERP is 46× the 2.74 mW threshold; Wi-Fi 5 GHz at 102 mW is 71× the 1.44 mW threshold.** No placement inside a 25 mm body reaches exemption; SAR is measured. Limits: 1.6 W/kg over 1 g (body), 4 W/kg over 10 g (extremities) (2.1093(d), as in the catalog).
- **Bluetooth alone** (51 mW ERP) is also above the threshold at any separation under about 2 cm. Murata's exception "except to use only Bluetooth" (CER-0248 §2.1.3.6) is Murata's statement about its grant; its basis is **UNVERIFIED** and the T1 uses Wi-Fi anyway.

### 5.3 Canada (RSS-102 Issue 6)

Exemption from SAR evaluation applies at or below Table 11's output power, adjusted for tune-up tolerance, taking the larger of the source-based time-averaged EIRP and conducted power (RSS-102 Issue 6 §6.3, ISED page read 2026-10-24):

| Frequency | ≤ 5 mm | 10 mm | 15 mm | 20 mm | 25 mm |
|---|---|---|---|---|---|
| 2450 MHz | **3 mW** | 7 mW | 16 mW | 32 mW | 56 mW |
| 5800 MHz | **1 mW** | 5 mW | 13 mW | 23 mW | 32 mW |

The T1's 209 mW (2.4 GHz) and 168 mW (5 GHz) EIRP are far above; SAR is evaluated. Limits: 1.6 W/kg over 1 g head, neck and trunk; 4 W/kg over 10 g limbs. Simultaneous transmission may be exempted from testing by the SPLSR method (§8.2.4).

### 5.4 EU (EN 62479, EN 50566)

Above the EN 62479 low-power level for Wi-Fi (§4.3), so EN 50566:2017 applies, with SAR measured per EN IEC/IEEE 62209-1528:2021 against Council Recommendation 1999/519/EC: 2 W/kg over 10 g for head and trunk, 4 W/kg for limbs (catalog §2.5).

### 5.5 Simultaneous transmission

- **Shared configuration (chosen):** one radiator; Wi-Fi and Bluetooth airtime are shared by the IW612's coexistence. The test lab confirms whether any operating mode puts both on the air at the same instant (**UNVERIFIED**).
- **Dedicated configuration (kept open):** FCC exemption for multiple sources is the sum of fractional contributions ≤ 1 (1.1307(b)(3)(ii)(B)); above that, SAR sum or peak-separation analysis in the test; RSS-102 uses SPLSR (≤ 0.02 head and trunk, ≤ 0.013 limbs).

## 6. What the layout and the software must guarantee

### 6.1 Layout (every regional choice without a respin)

1. **Both antenna paths routed as Murata's copy:** ANT0 (pin 15) and ANT1 (pin 23) each to a U.FL through Murata's matching positions in 0603, RF trace copied from Murata's U.FL layout, 230–240 µm to its ground, 7–25 mm long, ≥ 0.8 mm copper keep-out under each U.FL (PCB-R-02, PCB-R-03).
2. **Both configuration positions:** the 10 pF from pin 18 to pin 23 (shared) and the dedicated-configuration 0 Ω and termination positions of E2B-09-1413 Figure 10, so the configuration is an assembly option, not a layout change.
3. **U.FL positions in the top band, near the top wall**, so the 146153-0050 (50 mm class) reaches from its wall position to the ANT0 U.FL, and the Japan-only 146187-0050 (same cable class) or a 90 mm W24P-U can be fitted without moving them.
4. **Antenna keep-out in the case (input to E4.6):** a 146153 mounting area on the inside of the top wall (34.9 × 9.0 mm plus margin, within the 14.2 mm back-side height), ≥ 5 mm (provisional) from any metal; no metal screw inserts, microSD shell or HAT metal in that zone; the polymer wall carries no metallic paint or coating there (CASE-020).
5. **No HAT metal near the top wall:** HATs keep the T1's antenna keep-out (P-T1-p, design for compliance §2.11); the HAT device-side piece stays over the bottom band at the 25 mm body.
6. **Away from fast I/O:** PCB-R-06 unchanged.

### 6.2 Software (Blackbird OS)

1. **Regional TX-power tables as data:** each regional variant ships its market's certified table (Murata's `txpower_{US,CA,EU,JP}.bin`, `rutxpower_*`, Bluetooth TX scripts) selected by variant data, never hard-coded (SYS-040). How these tables reach the mainline `nxpwifi` driver is **UNVERIFIED** (LBES5PL2EL-923 sheet, Linux driver): the T1 needs a loader or an equivalent cap through cfg80211 before Q2.
2. **Time-averaged power never above the SAR-tested level:** SAR is assessed at the maximum time-averaged power the software allows; the shipped cap equals the tested one. This is a safety and legal limit in the sense of BRD-049: documented and visible to the user (for example in the radio settings), never silent.
3. **Configuration match:** the calibration file follows the fitted configuration (default for shared, `WlanCalData_ext_dANT.conf` for dedicated).
4. **802.15.4 off:** the radio is not wired (no SPI); the driver configuration never enables it, so it adds no exposure.
5. **Regulatory domain:** the variant's country code is applied at boot; DFS client behaviour as certified (CER-0248 footnotes: no DFS master).

## 7. Open points

1. Molex 146153-0050 sales drawing, product specification (gain per cable length, efficiency) and application specification (clearance, adhesive surfaces): not obtained; Molex refused automated fetches. Needed before Q2.
2. Keep-out distance: the provisional 5 mm is a design target until measured in the prototype case.
3. Murata (outward contact, later): the Class II / Class 4 procedure for a portable host, what Murata needs in the SAR report, how it measures "cable length", whether the shared configuration ever transmits Wi-Fi and Bluetooth at the same instant, and Japan's SAR scope.
4. The 47 CFR 1.1307 P_th formula image and the EN 62479 20 mW value: confirm against the primary texts (catalog open items).

## Sources

- Murata CER-0248 Rev. 6.0 and E2B-09-1413 Rev. 9.0: URLs and hashes in `parts-lib/manifest.toml` (LBES5PL2EL-923).
- Molex drawings from the LCSC datasheet mirror: 1461531050 rev. B1 (146153 flex, MHF4L variant), sha256 `4bb15eb60149c8948841a603aa14e5b46fc2d3eff0d85ce457dd8ce2793d674f`; 2196110100 rev. A1 (219611 series), sha256 `207fd73b2212b4729ad69ff5ea91e635712a97bd8836a9bd20dbf321acd03c8f`; 1461870050 rev. D (parts-lib sheet).
- Inventek *W24P-U* specification DOC-DS-20075-1.0 (2013-10-01), <https://www.inventeksys.com/wp-content/uploads/W24P-U_2.4Ghz_-Antenna_Specification.pdf>, sha256 `68cde1cc9ebc00631efe68414a5c1dce6e3f248c57385f4c0f66edbb11dfecbc`.
- Availability: Digi-Key search pages (`/en/products/result?keywords=…`), FindChips (`/search/<MPN>`), JLCPCB parts API, all 2026-10-24.
- 47 CFR 1.1307, CFR 2025 edition: <https://www.govinfo.gov/content/pkg/CFR-2025-title47-vol1/xml/CFR-2025-title47-vol1-sec1-1307.xml>.
- ISED RSS-102 Issue 6: <https://ised-isde.canada.ca/site/spectrum-management-telecommunications/en/devices-and-equipment/radio-equipment-standards/radio-standards-specifications-rss/rss-102-radio-frequency-rf-exposure-compliance-radiocommunication-apparatus-all-frequency-bands>.
