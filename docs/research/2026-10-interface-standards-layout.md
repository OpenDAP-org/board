# Interface standards: layout tolerance windows for the T1 board

- **Date:** 2026-10-24
- **Status:** Desk research for electronics plan task E1.11. Nothing here is a decision; section 7 proposes values for the PCB design constraints (PCB-I-01 to PCB-I-04 and PCB-I-06), which this note does not edit.
- **Scope:** the impedance, skew and AC-coupling windows of USB 2.0 high speed, USB 3.x Gen 1, PCIe Gen 2 x1, MIPI D-PHY, SD 3.0 UHS-I SDR104 and eMMC 5.1 HS200, as the RK3566 board routes them.
- **Method:** primary specifications where they are public (USB-IF publishes USB 2.0 and USB 3.2; the SD Association publishes a simplified SD physical layer). PCI-SIG, MIPI and JEDEC texts are member-only or behind registration and were not read; for them the values come from public design guides, marked **secondary**. The SoC vendor's own guides are preferred among the secondary sources, because they set the windows for the RK3566 PHYs actually on the board. Page numbers are the printed page numbers unless "PDF page" is stated.

---

## 1. Sources

| Ref | Document | Kind | Revision, date | Where |
|---|---|---|---|---|
| [U2] | *Universal Serial Bus Specification Revision 2.0* (`usb_20.pdf` in `usb_20_20250603.zip`), 650 pages | Primary | Rev. 2.0, 2000-04-27; sha256 `d39698a33486c399124af92bd02e4f978fd9a836b5cf4e52e6e4633eb1d89f61` | <https://www.usb.org/document-library/usb-20-specification> |
| [U3] | *Universal Serial Bus 3.2 Specification* (`USB 3.2 Revision 1.1.pdf` in `usb_32_202206_0.zip`), 569 pages | Primary | Rev. 1.1, June 2022; sha256 `26e025a56ce0352f4f91fcaaca67b622d8e9e030ca429804bf7da98f52e674fd` | <https://www.usb.org/document-library/usb-32-revision-11-june-2022> |
| [SD] | SD Association, *Physical Layer Simplified Specification* | Primary (simplified) | Version 9.10, 2023-12-01; sha256 `ee86b20ec02b30797f14ceaf9f760feadb321de12cceb278b917aab7a65380e3` | <https://www.sdcard.org/downloads/pls/> |
| [RK-HS] | Rockchip, *RK3568 High Speed PCB Design Guide*, RK-YH-YJ-6012, 45 pages | Secondary (SoC vendor) | V1.0.0, 2021-04-12; sha256 `ba3b7aa055b641f59688f2fd0133094b71f06bc928786d4e1444c3c63b5ff513` | parts-lib `manifest.toml` (RK3566) |
| [RK-HDG] | Rockchip, *RK3566 Hardware Design Guide*, 102 pages | Secondary (SoC vendor) | V1.1.0, 2022-02-06; sha256 `27063af9183cd9a17f71d9aa66f64eb2514427e490c3cc8f9336e11eacf1d9d1` | parts-lib `manifest.toml` (RK3566) |
| [TI] | Texas Instruments, *High-Speed Interface Layout Guidelines*, SPRAAR7J | Secondary | Rev. J, February 2023; sha256 `4a14e9b00afc174f336386cf0097f3a5e7a6a367840331fbb22070053ec36f41` | <https://www.ti.com/lit/an/spraar7j/spraar7j.pdf> |
| [QC] | Qualcomm, "PCIe layout guidelines" (80-PV086-5P), web page | Secondary | Published 2023-07-07 | <https://docs.qualcomm.com/bundle/publicresource/80-PV086-5P/topics/PCIe%20layout%20guidelines.md> |
| [MC] | Microchip, *PolarFire Family PCI Express User Guide*, §6.1 "AC-Coupling", web page | Secondary | Read 2026-10-24 | <https://onlinedocs.microchip.com/oxy/GUID-E54C85EF-C33B-4E1E-A006-276B04B0FF9B-en-US-12/GUID-048B4E4B-3A92-44F4-9746-EE23AF5FD685.html> |
| [MU] | Murata, *Type 2EL/2DL Hardware Application Note*, E2B-09-1413 | Secondary (module vendor, SDIO only) | Rev. 9.0, 2026-05-21 | parts-lib `manifest.toml` (LBES5PL2EL-923) |

Not read: PCI Express Base Specification 2.x and CEM (PCI-SIG members), MIPI D-PHY v1.2 (MIPI members), JEDEC JESD84-B51 eMMC 5.1 (free with JEDEC registration, not done in this session), and the full SD Physical Layer Specification (the simplified version removes the UHS-I bus timing, [SD] §6.7.3, table of contents p. xi).

Unit conversions: 1 mil = 0.0254 mm; 12 mil = 0.30 mm, 20 mil = 0.51 mm, 36 mil = 0.91 mm, 120 mil = 3.05 mm, 4 in = 101.6 mm, 6 in = 152.4 mm.

## 2. USB 2.0 high speed (PCB-I-01)

| Item | Value | Source | Kind |
|---|---|---|---|
| Board transmission line, receptacle to series resistor | "must be 90 Ω ±15%" (76.5–103.5 Ω) | [U2] §7.1.6.1, p. 142 | Primary |
| Cable differential impedance | 90 Ω ±15%, 76.5–103.5 Ω | [U2] Table 7-12, p. 185; §7.1.1.1, p. 124 | Primary |
| High-speed driver output impedance, including R_S | 40.5–49.5 Ω (45 Ω ±10 %) | [U2] §7.1.1.1; Table 7-7, p. 180 | Primary |
| Cable D+/D− skew | < 100 ps | [U2] §7.1.3, p. 139; Table 7-12, p. 185 | Primary |
| PCB intra-pair skew | Not specified by [U2] | — | — |
| Impedance, RK3566 board | 90 Ω ±10 % differential | [RK-HS] Table 1, p. 13 | Secondary |
| Intra-pair skew | < 20 mil (0.51 mm) | [RK-HS] Table 1, p. 13 | Secondary |
| Length, vias | < 6 in; recommend < 4 vias, never > 6 | [RK-HS] Table 1, p. 13 | Secondary |
| Series resistor at the SoC | 2.2 Ω on OTG0 and HOST D± | [RK-HDG] Table 2-13, p. 59 | Secondary |
| Comparison | 81–99 Ω; skew within a pair ≤ 50 mil | [TI] Table A-7 (AM62x), p. 19 | Secondary |

**Value for the T1:** 90 Ω differential at the fab's ±10 % (inside the primary ±15 %). Intra-pair skew target 0.15 mm (the current constraint), hard limit 0.5 mm [RK-HS]. Where USB 2.0 leaves the board on the HAT flat cable, the cable's own skew counts against the 100 ps cable budget of [U2] §7.1.3.

## 3. USB 3.x Gen 1 (PCB-I-02)

| Item | Value | Source | Kind |
|---|---|---|---|
| Transmitter AC-coupling capacitor | 75 nF min, 265 nF max; "All Transmitters shall be AC coupled" | [U3] Table 6-18, p. 82 | Primary |
| Transmitter DC differential impedance | 72–120 Ω | [U3] Table 6-18, p. 82 | Primary |
| Receiver DC differential impedance | 72–120 Ω | [U3] Table 6-22, p. 93 | Primary |
| Receiver AC coupling, if used | 297–363 nF | [U3] Table 6-22, p. 93 | Primary |
| PCB trace impedance and intra-pair skew | Not specified in the base specification (no trace impedance found in chapters 6–7) | [U3] | — |
| Impedance, RK3566 board | 90 Ω ±10 % differential | [RK-HS] Table 2, p. 13; [RK-HDG] Table 2-13, p. 59 | Secondary |
| Intra-pair skew | < 12 mil (0.30 mm) | [RK-HS] Table 2, p. 13 | Secondary |
| AC-coupling capacitor | 100 nF ±20 %, 0201 preferred, on TX; the peripheral's TX carries its own 100 nF | [RK-HS] Table 2; [RK-HDG] Table 2-13, p. 59 | Secondary |
| Placement | "AC coupling capacitors is recommended to be placed close to the connector" | [RK-HS] §1 general rule (14), p. 12 | Secondary |
| Length, vias, spacing | < 6 in; ≤ 2 vias; pair-to-pair and to other signals ≥ 4 × trace width | [RK-HS] Table 2, p. 13 | Secondary |
| Comparison | 83.7–96.3 Ω (90 Ω ±7 %) for TI AM57xx | [TI] Table A-2, p. 16 | Secondary |

**Value for the T1:** 90 Ω ±10 % differential; intra-pair target 0.1 mm, hard limit 0.3 mm; 100 nF ±20 % X7R 0201 in series with each TX line only (inside the primary 75–265 nF window even at −20 %), placed at the board's HAT/USB-C side of the path per [RK-HS]. RX pairs carry no capacitor on the board. Capacitor placement around the HD3SS3212 mux is not covered here.

## 4. PCIe Gen 2 x1 (PCB-I-03)

| Item | Value | Source | Kind |
|---|---|---|---|
| Data pair impedance, RK3566 PHY | 85 Ω ±10 % differential | [RK-HS] Table 5, p. 15; [RK-HDG] Table 2-37, p. 89 | Secondary |
| REFCLK impedance | 100 Ω ±10 % differential | [RK-HS] Table 5, p. 15; [RK-HDG] Table 2-37, p. 89 | Secondary |
| Intra-pair skew (data); REFCLK+ to REFCLK− | < 12 mil (0.30 mm); < 12 mil | [RK-HS] Table 5, p. 15 | Secondary |
| Inter-pair skew | < 6 in (TX/RX pairs need not match) | [RK-HS] Table 5, p. 15 | Secondary |
| AC-coupling capacitor | 100 nF ±20 %, 0201, on TX near the transmitter; the RX capacitor sits on the far side | [RK-HS] Table 5; [RK-HDG] Table 2-37, p. 89 | Secondary |
| AC-coupling window | 75–200 nF | [MC] §6.1 | Secondary |
| AC-coupling window, Gen 2 | 75–265 nF (Gen 3: 176–265 nF) | [QC] | Secondary |
| Impedance range, Gen 2 | 70–100 Ω differential, including manufacturing variation; intra-lane match 5 ps (0.7 mm) | [QC] | Secondary |
| Length, vias, spacing | < 6 in; ≤ 2 vias; ≥ 4 × width between pairs, ≥ 5 × width recommended to other signals | [RK-HS] Table 5, p. 15 | Secondary |
| Comparison | 90–110 Ω (100 Ω ±10 %) for TI AM57xx | [TI] Table A-2, p. 16 | Secondary |

85 Ω or 100 Ω: both appear in the secondary sources; the choice follows the PHY on the board, and Rockchip specifies 85 Ω for the RK3566 data pairs. The primary window (PCI Express Base 2.x) was not read: **UNVERIFIED**.

**Value for the T1:** data pairs 85 Ω ±10 %; REFCLK 100 Ω ±10 % (a separate net class: the current PCB-I-03 lists `PCIE_REFCLK±` under the 85 Ω class); intra-pair target 0.1 mm, hard limit 0.3 mm on data and REFCLK; 100 nF ±20 % X7R 0201 on the board's TX pair near the SoC side; none on RX.

## 5. MIPI D-PHY (PCB-I-04)

| Item | Value | Source | Kind |
|---|---|---|---|
| Impedance, RK3566 DSI and CSI | 100 Ω ±10 % differential | [RK-HS] Table 10, p. 18; [RK-HDG] DSI table p. 78, CSI table p. 85 | Secondary |
| Intra-pair skew | < 12 mil (0.30 mm) | [RK-HS] Table 10, p. 18 | Secondary |
| Data-to-clock mismatch | < 36 mil (0.91 mm) | [RK-HS] Table 10, p. 18 | Secondary |
| Length, vias, spacing | < 6 in; 4 vias; ≥ 3 × trace width | [RK-HS] Table 10, p. 18 | Secondary |
| Comparison: impedance | 85–115 Ω; pairs "must be loosely coupled" because the lanes also signal single-ended in low-power mode | [TI] Table A-7 (AM62x CSI), p. 19, note 2 | Secondary |
| Comparison: lane skew | 40 ps, "defined by MIPI spec as 0.1 × UI" at 2.5 Gb/s | [TI] Table A-7, p. 19, note 3 | Secondary, quoting MIPI |
| Comparison: intra-pair skew | set by the D-PHY mode-conversion S-parameters; "general estimate is UI/50" (8 ps at 2.5 Gb/s) | [TI] Table A-7, p. 19, note 1 | Secondary, quoting MIPI |

The D-PHY v1.2 text was not read; its receiver and channel impedance windows are **UNVERIFIED**.

**Value for the T1:** 100 Ω ±10 % differential; intra-pair target 0.1 mm, hard limit 0.3 mm; lane-to-clock hard limit 0.9 mm on the board (tighter than the current 1 mm). Where DSI or CSI-2 continues on a flat cable to the faceplate or a HAT, the board's share of the lane-to-clock budget has to leave room for the cable: the 0.1 UI figure [TI] applies to the whole link.

## 6. SD 3.0 UHS-I SDR104 and eMMC 5.1 HS200 (PCB-I-06)

| Item | Value | Source | Kind |
|---|---|---|---|
| SDR104 bus | 4 data lines, 1.8 V signalling, up to 208 MHz | [SD] §2, p. 3 | Primary |
| SDR104 bus timing and load | Removed from the simplified specification | [SD] §6.7.3 (table of contents) | Primary (not public) |
| eMMC 5.1 HS200 | JESD84-B51 not read | — | **UNVERIFIED** |
| Impedance (SDIO, SDMMC, eMMC) | 50 Ω ±10 % single-ended | [RK-HS] Tables 11–13, pp. 19–20; [RK-HDG] p. 54 (SDIO) | Secondary |
| Data-to-clock mismatch | < 120 mil (3.05 mm) | [RK-HS] Tables 11–13, pp. 19–20 | Secondary |
| Maximum length | < 4 in above 50 Mb/s (SDIO, SDMMC); < 4 in (eMMC) | [RK-HS] Tables 11–13 | Secondary |
| Spacing, vias | ≥ 2 × trace width within the bus; eMMC to other signals 3 × recommended, 2 × minimum; ≤ 4 vias | [RK-HS] Tables 11–13 | Secondary |
| Series resistors at the SoC | 22 Ω on SDMMC0 CLK, CMD, DATA; 22 Ω on SDIO_CLK; 22 Ω on eMMC_CLK | [RK-HDG] pp. 52, 54, 26 | Secondary |
| Wi-Fi SDIO (Murata 2EL) | "isometric zero delay routing with 50Ω impedance"; damping resistors on SD_CLK, SD_CMD, SD_DAT0–3 | [MU] §3.2, p. 14; Figure 5, p. 10 | Secondary (module vendor) |

**Value for the T1:** 50 Ω ±10 % single-ended; CLK-to-data target 2 mm (the current constraint), hard limit 3.0 mm; total length ≤ 100 mm; series resistors at the source as in [RK-HDG].

## 7. Values proposed for the constraints

| ID | Class | Impedance | Skew and length | AC coupling | Basis |
|---|---|---|---|---|---|
| PCB-I-01 | `USB2_90D` | 90 Ω ±10 % diff. | Intra-pair target 0.15 mm, limit 0.5 mm; ≤ 150 mm | — | [U2] §7.1.6.1 (±15 %, primary); [RK-HS] Table 1 |
| PCB-I-02 | `USB3_90D` | 90 Ω ±10 % diff. | Intra-pair target 0.1 mm, limit 0.3 mm; ≤ 150 mm; ≤ 2 vias | 100 nF ±20 % 0201 on TX only | [U3] Table 6-18 (75–265 nF, primary); [RK-HS] Table 2 |
| PCB-I-03 | `PCIE_85D` | 85 Ω ±10 % diff. (data) | Intra-pair target 0.1 mm, limit 0.3 mm; ≤ 150 mm; ≤ 2 vias | 100 nF ±20 % 0201 on TX only | [RK-HS] Table 5; [RK-HDG] Table 2-37; [MC], [QC] (secondary only) |
| PCB-I-03b (new) | `PCIE_REFCLK_100D` | 100 Ω ±10 % diff. | REFCLK+ to REFCLK− ≤ 0.3 mm | — | [RK-HS] Table 5; [RK-HDG] Table 2-37 |
| PCB-I-04 | `MIPI_100D` | 100 Ω ±10 % diff., loosely coupled | Intra-pair target 0.1 mm, limit 0.3 mm; lane-to-clock limit 0.9 mm; ≤ 150 mm | — | [RK-HS] Table 10; [TI] Table A-7 |
| PCB-I-06 | `EMMC_SD_50` | 50 Ω ±10 % SE | CLK-to-data target 2 mm, limit 3.0 mm; ≤ 100 mm | — | [RK-HS] Tables 11–13; [MU] §3.2 |

## 8. Still open

- PCI Express Base 2.x and CEM windows (impedance, C_TX): member-only; only secondary values here.
- MIPI D-PHY v1.2 impedance and skew: member-only; only secondary values here.
- eMMC 5.1 (JESD84-B51) and the full SD physical layer timing for SDR104: not read.
- The 85 Ω / 90 Ω / 100 Ω pairs share the board with the fab's ±10 % tolerance: the achieved values need the PCBWay stackup and coupons (E3.6).
- The skew and AC-coupling budget through the HAT flat cable, the faceplate cable and the HD3SS3212 / PI3PCIE3212 muxes.
