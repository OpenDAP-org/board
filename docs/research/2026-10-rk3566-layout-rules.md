# RK3566 layout rules from Rockchip's documents

- **Date:** 2026-10-24
- **Status:** Desk research, task E1.11 (part 1) of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md). Nothing here is a decision. It transcribes, with page cites, what Rockchip's documents say about the constraints in [`../specs/pcb-design-constraints.md`](../specs/pcb-design-constraints.md), and says for each **UNVERIFIED** value there what the source now gives. The constraints spec itself is not edited here.
- **Scope:** PCB-I-01 to PCB-I-09, PCB-S-01 to PCB-S-06, PCB-G-02 and PCB-G-03 (BGA escape), PCB-P-10 (decoupling). Plus the question of whether the RK3566's 0.4 mm-pitch balls can be escaped without via-in-pad.
- **Sources:** all are listed in the parts-lib `manifest.toml` with URL, revision, date and sha256, and are fetched into the local cache by `parts-sync.py`. None is redistributable, so none is committed. Spec sheet: [parts-lib `Rockchip/RK3566.md`](https://github.com/opendap-project/parts-lib/blob/main/Rockchip/RK3566.md).

| Short | Document | Revision, date | Pages |
|---|---|---|---|
| DS | Rockchip *RK3566 Datasheet* | Rev 1.1, 2021-03-05 | 59 |
| HDG | Rockchip *RK3566 Hardware Design Guide* | V1.1.0, 2022-02-06 | 102 |
| HSPCB | Rockchip *RK3568 High Speed PCB Design Guide* (RK-YH-YJ-6012) | V1.0.0, 2021-04-12 | 45 |
| TPL | Rockchip RK3568 LPDDR4X core-board template design notes, `RK3568_Template_LP4XD200P132SD6_43x28_1600MHz` (Chinese) | V10, 2021-02-01 | 6 |
| EVB | Rockchip *RK3566 EVB2 User Guide* | V1.1, 2021-02-02 | 42 |

HDG names an *RK3566 High Speed PCB Design Guide* (HDG p. 4) that was not found online. HSPCB is the RK3568 edition. The RK3566 shares the RK3568's interface blocks (DDR controller, multi-PHY, USB, MIPI), but it uses a different package. Every HSPCB value below is therefore **UNVERIFIED for the RK3566 package**, and it is the closest primary source. HSPCB states that "trace length should include package length and via length" (p. 6). The RK3566 package pin-length table was not found. Units: Rockchip writes mil; 1 mil = 0.0254 mm, and the conversions are arithmetic.

## 0. Summary

1. **Rockchip's LPDDR4X impedance is 50 Ω single-ended and 100 Ω differential (±10 %), not 40/80 Ω** (HSPCB p. 45, Table 34). Matching is loose: DQ to DQS within a byte under 600 mil (15.2 mm); CA to CLK under 500 mil (12.7 mm); DQS and CLK P/N under 12 mil (0.30 mm); DQS to CLK under 1200 mil (30.5 mm).
2. **Rockchip strongly steers LPDDR4X layout to its own templates.** A customer-made layout must be simulated (HSPCB p. 23; HDG p. 26). LPDDR4/4X DQ and CA order may not be swapped (HDG p. 22). Rockchip's RK3568 LPDDR4X template is a **6-layer** board with **0.2/0.4 mm through vias**, LPDDR4X on one side, 43 × 28 mm, rated for 1600 MHz (TPL items 5, 6, 7, and 5.2).
3. **The package is two grids.** 343 core balls sit on 0.65 mm. 222 balls form a two-row perimeter ring on 0.4 mm: the inner ring is fully populated, the outer ring has about every third ball missing (DS pp. 21–30). Ball Ø 0.25 mm nominal. **Rockchip publishes no land pattern and no via size for the RK3566.**
4. **Via-in-pad is not required by any Rockchip document, and by arithmetic it is not needed** (§3). Laser microvias placed as dog-bones in the 0.825–0.875 mm channel between the ring and the core escape every inner-ring ball. Through vias of 0.2/0.4 mm do not fit there for adjacent 0.4 mm balls, so a through-via-only escape of the ring is unproven. The constraints' statement that the 0.4 mm field needs via-in-pad microvias (§0 item 3, PCB-S-02) is not supported. The T1 needs microvias, not necessarily in the pad. An escape study in KiCad (E4) settles it.
5. **No reference-board stackup is published** for the Radxa ZERO 3W/3E, ROCK 3C, Quartz64, SOQuartz or Orange Pi 3B: their schematics carry none. Rockchip's own evidence points to 4–6 layers: thermal test board 4 layers; the RK3568 LPDDR4X template 6 layers; the RK3566 EVB2 PCB name likely means 6 layers. The T1's 8–10-layer HDI assumption is therefore **not forced by the SoC**. It rests on the T1's own density, its double-sided z budget and the audio partition, and it stays an assumption until the escape study (§4).

## 1. Signal classes (PCB-I)

HSPCB general rules for all high-speed pairs (pp. 7–12):

- Serpentines placed close to the point of mismatch (p. 7).
- Continuous ground reference with no splits (p. 8). The ground plane is voided under SMT pads, ESD parts, common-mode chokes and AC capacitors (pp. 8–11).
- Stitching ground vias at every layer change, symmetric for pairs, within 30 mil (0.76 mm) of the signal via (p. 8).
- Same-layer ground copper at least 3 × trace width away (p. 9).
- Simulate any via stub over 12 mil (0.30 mm) (p. 10).
- Differential pairs at least 40 mil (1.02 mm) from a reference-plane edge (p. 11).
- 10° zig-zag against fibre weave for ≥ 5 GT/s runs of 4 inches or more (p. 11).
- No traces under or near crystals, oscillators, switching regulators, mounting holes or magnetics. No test points on high-speed pairs. 135° bends (p. 12).
- AC coupling capacitors close to the connector (p. 12).

| ID | Spec value marked UNVERIFIED | What Rockchip says | Source |
|---|---|---|---|
| PCB-I-01 `USB2_90D` | Intra-pair skew ≤ 0.15 mm | 90 Ω ±10 % differential; intra-pair skew < 20 mil (0.51 mm); length < 6 in (152 mm); fewer than 4 vias recommended, never more than 6. 2.2 Ω series resistor on each D± line at the SoC. The spec's 0.15 mm is tighter than Rockchip's; the USB 2.0 text itself is still not retrieved | HSPCB p. 13, Table 1; HDG p. 59, Table 2-13 |
| PCB-I-02 `USB3_90D` | Intra-pair ≤ 0.1 mm; AC caps near the source | 90 Ω ±10 %; intra-pair < 12 mil (0.30 mm); < 6 in; AC caps 100 nF ±20 %, 0201 preferred; pair-to-pair and pair-to-other spacing ≥ 4 × trace width; ≤ 2 vias. HDG: 100 nF in series on SSTX; SSRX direct or 0 Ω, because the far end's TX carries its own capacitor. HSPCB p. 12 puts AC caps "close to the connector"; the spec's "near the source" differs, and both are allowed by USB 3 (**UNVERIFIED** until the USB 3 text is in the docs) | HSPCB p. 13, Table 2; HDG p. 59 |
| PCB-I-03 `PCIE_85D` | 85–100 Ω allowed; intra-pair ≤ 0.1 mm | Data 85 Ω ±10 %; **REFCLK 100 Ω ±10 %**, so REFCLK needs its own net class; intra-pair < 12 mil (0.30 mm); REFCLK P/N < 12 mil; TX and RX < 6 in; AC caps 100 nF ±20 % 0201, at the sending end or at the mainboard connector (RX caps on the device side); pair-to-pair ≥ 4 × W; to other signals ≥ 5 × W recommended, ≥ 4 × W minimum; ≤ 2 vias | HSPCB p. 15, Table 5; HDG p. 89, Table 2-37 |
| PCB-I-04 `MIPI_100D` | Intra-pair ≤ 0.1 mm; lane-to-clock ≤ 1 mm | 100 Ω ±10 %; intra-pair < 12 mil (0.30 mm); data to clock < 36 mil (0.91 mm); < 6 in; at most 4 vias; pair-to-pair and to other signals ≥ 3 × W. The spec's 1 mm lane-to-clock is looser than Rockchip's 0.91 mm. DSI and CSI analog supplies (0.9 V, 1.8 V) go through ferrite beads, with decoupling at the pins | HSPCB pp. 18–19, Table 10; HDG pp. 78, 84–85 |
| PCB-I-05 `DDR_*` | 40 Ω SE / 80 Ω diff; byte-lane and CA matching | **50 Ω ±10 % SE, 100 Ω ±10 % differential.** DQ–DQS and DM–DQS within a byte < 600 mil (15.2 mm), kept as short as possible (DQ need not match DQS); CA to CLK < 500 mil (12.7 mm); DQS_P–DQS_N < 12 mil (0.30 mm); CLK_P–CLK_N < 12 mil; DQS to CLK < 1200 mil (30.5 mm). Spacing: byte to byte, DQ to DQ and CA to CA ≥ 2 × W; DQ to DQS and CLK to others ≥ 3 × W recommended (≥ 2 × W minimum). Further DDR rules in §1.1 | HSPCB p. 45, Table 34 (LPDDR4X; Table 33, p. 44, LPDDR4, has the same values) |
| PCB-I-06 `EMMC_SD_50` | CLK to data ≤ 2 mm | eMMC: 50 Ω ±10 %; data to clock < 120 mil (3.05 mm); < 4 in; spacing within the bus ≥ 2 × W, to others 3 × W recommended (≥ 2 × W); ≤ 4 vias recommended. SDMMC: 50 Ω; data to clock < 120 mil; < 4 in above 50 Mb/s; ≥ 2 × W; ≤ 4 vias. Series 22 Ω on eMMC CLK (at the SoC) and on SDMMC0 DATA, CMD and CLK; SD ESD < 1 pF for SDR104. The spec's 2 mm is tighter than Rockchip's 3.05 mm | HSPCB pp. 19–20, Tables 12, 13; HDG pp. 26, 52 |
| PCB-I-07 `RF_50` | Murata guide | Not in Rockchip's documents. The SDIO bus to the radio: 50 Ω ±10 %; < 4 in; CLK to data and CMD within 120 mil; CLK series resistor near the SoC; CLK guarded with ground and ground vias at ≤ 300 mil (7.6 mm); solid ground reference | HDG p. 54; HSPCB p. 19, Table 11 |
| PCB-I-08 `I2S_DSD` | Bus matching ≤ 5 mm | No impedance or length rule for I2S in HSPCB or HDG. HDG asks for 22 Ω in series on MCLK, SCLK and LRCK at the source, and SDO/SDI connected directly. The 5 mm matching stays a T1 value (**UNVERIFIED**, from the CS43198 timing budget) | HDG pp. 70–71, Tables 2-20, 2-21 |
| PCB-I-09 `MCLK` | — | Not a Rockchip signal in the T1 (the DACs take MCLK from the oscillators). Nearest rule: no traces under or near crystals and oscillators. For the SoC's 24 MHz crystal: 2 × 18 pF C0G matched to the crystal's CL, 22 Ω series in XOUT24M, 1 MΩ across. The reset line is guarded with ground and vias at ≤ 300 mil | HSPCB p. 12 item 11; HDG pp. 16–18 |

### 1.1 Further DDR rules (HSPCB pp. 23–30; HDG pp. 21–26; TPL)

- **Templates first.** Rockchip strongly requires its demo PCB at up to 3200 Mb/s. A customer-made layout must be simulated by the customer (HSPCB p. 23). Most official RK3566 templates reach 1056 MHz; for a custom layout, "consult RK for more detailed layout restrictions" (HDG p. 26). The rate the T1 can reach is **UNVERIFIED** until its own layout is simulated (E4.4).
- **No swaps.** LPDDR4/LPDDR4X DQ and CA order cannot be swapped and follow the reference schematic (HDG p. 22).
- **Vias:**
  - Enough vias on the CPU-side GND balls (HSPCB p. 23, Fig. 14).
  - Stitching GND vias within 25 mil (0.64 mm) of every layer change that references GND (p. 23).
  - One via per DRAM power pad and one per DRAM GND pad (pp. 24–25).
  - At least 6 vias on VCC_DDR at the DC-DC output (p. 25).
  - One via per capacitor pad (p. 26).
  - For LPDDR4X, at least 8 vias on the CPU-side VCC_DDR balls and at least 6 on VCC0V6_DDR (p. 30).
- **Return path:**
  - No slits in the reference plane (p. 26).
  - Where a layer change swaps the reference between GND and power, add a 100 nF stitching capacitor for every 3–4 signal vias (p. 26).
  - Traces at least 6 mil (0.15 mm) from any via hole or pad; remove unused via pads (p. 27).
  - Signals at least 12 mil (0.30 mm) from a reference-plane edge (p. 28).
- **The RK3568 LPDDR4X template** (TPL items 1–7 and 5.1–5.6; RK3568 FCBGA, not the RK3566 package):
  - Layout: 6 layers; LPDDR4X on one side and other parts on both; 43 × 28 mm; LPDDR4/LPDDR4X up to 8 GB; simulated stable at 1600 MHz.
  - Planes: power and ground planes unbroken. Rockchip reports random crashes and reboots from split planes.
  - Vias: layer-change vias spread evenly, at least 0.7 mm apart, 0.2 mm hole and 0.4 mm pad.
  - Copper: pour line width 4 mil.
  - Guarding: DDR data and address lines are guarded with ground every two signals, with 0.1 mm from the ground copper to the signal.

## 2. Stackup and build (PCB-S)

| ID | What Rockchip's documents say | Source |
|---|---|---|
| PCB-S-01 thickness | Nothing required. The thermal test board is 1.6 mm, 4 layers (JESD51-2 simulation, not a design rule). The template notes give no thickness | DS p. 59; HDG p. 90, Table 3-2 |
| PCB-S-02 build | No document requires HDI, blind or buried vias, or via-in-pad. The RK3568 LPDDR4X template uses 0.2/0.4 mm vias on 6 layers. On a 4-layer board, add a GND trace with vias along a signal that changes layer | TPL items 5, 5.2; HSPCB p. 27 item 11 |
| PCB-S-03 layer count | Rockchip writes for 4-layer and thicker boards: "If the PCB exceeds 4 layers, try to route all clock signals in the inner layers". RK3568 LPDDR4X template: 6 layers. RK3566 EVB2 PCB file `RK_EVB2_RK3566_LP4X200P132SD6_V10_20200916lxf.PCB`: its suffix matches the RK3568 template's `LP4XD200P132SD6`, which the template notes describe as 6 layers. That the EVB2 is 6 layers is an inference from the naming, **UNVERIFIED** | HDG p. 96; TPL item 5; EVB p. 15 |
| PCB-S-04 reference planes | Every high-speed route over continuous GND with no split. Stitching vias at layer changes (< 30 mil general, < 25 mil DDR). SDIO and RGMII over a complete ground plane. Clocks on inner layers above 4 layers. Power-plane copper pulled back from the ground-plane edge by a multiple of H (the power-to-ground dielectric thickness); the factor in the source is cut off. GND balls of the SoC joined in a "#" pattern of 10 mil traces on top, with one via per GND ball (at worst one per 1.5 balls) into an adjacent ground plane | HSPCB pp. 8, 23, 26; HDG pp. 54, 93, 96 |
| PCB-S-05 dielectric | Not specified. Simulate via stubs over 12 mil | HSPCB p. 10 |
| PCB-S-06 material | Not specified. Fibre-weave zig-zag (10°) for ≥ 5 GT/s runs of 4 inches or more; PCIe 3.0 (not on the RK3566) to be simulated | HSPCB pp. 11, 16 |

**Reference boards (target 3 of the task).** The Radxa ZERO 3W v1.12, ROCK 3C v1.4 and CM3 v1.31A schematics, and the Pine64 Quartz64 Model A v2.0 and SOQuartz v1.1 schematics, were searched for "layer", "stack", "HDI", "blind", "laser" and "impedance". None states a stackup. Radxa and Pine64 do not publish board files for these boards. Vendor pages, secondary and **UNVERIFIED**:

- An RK3566 core board from a Chinese PCBA house: "6L, 1.6 mm, 1 oz, min hole 0.2 mm, 5/5 mil" (<https://chenghepcba.com/pcba/48.html>, read 2026-10-24). It does not say whether the 5 mil applies under the SoC.
- ArmDesigner CM3566 SOM: 8 layers, 47 × 40 mm (<https://www.armdesigner.com/CM3566_SOM/>, read 2026-10-24).

So the public evidence is: Rockchip's own boards are 4–6 layers with through vias. Third-party RK3566 modules are 6 or 8 layers. **No source shows how the RK3566 0.4 mm ring is escaped.**

## 3. BGA escape (PCB-G-02, PCB-G-03) and the via-in-pad question

**Geometry (DS pp. 21–22; ball counts from the DS pin list, pp. 23–30):**

| Item | Value |
|---|---|
| Body | 15.500 × 14.400 mm |
| Ball Ø (b) | 0.200 / 0.250 / 0.300 mm (min / nom / max) |
| Ball position tolerance | Ø0.15 mm to C-A-B, Ø0.05 mm to C |
| Core | 343 balls, 0.65 mm grid, 18 rows × 20 columns (`1A1`–`1V20`), partly depopulated |
| Ring | 222 balls, 0.4 mm grid, 38 columns × 35 rows (`A1`–`AR38`), two rows per side |
| Inner ring (row B, row AP, columns 2, 37) | Fully populated |
| Outer ring | Row A 24/38, row AR 25/38, column 1 20/35, column 38 23/35 |
| Ring outer to inner row | 0.400 mm |
| Inner ring to first core row (centres) | 0.825 mm in x, 0.875 mm in y (arithmetic: 1.575 − 0.350 − 0.400 and 1.675 − 0.400 − 0.400) |

**What sits in the ring:** most DDR byte-lane balls, eMMC data, USB 2/3, PCIe, eDP, the MIPI DSI/CSI and HDMI pairs, XIN/XOUT24M, nPOR, the I2C0/1 PMIC bus, and part of I2S1_M1, I2S3_M0 and PDM_M1 (DS pp. 23–30). The ring carries the critical nets, not only spare GPIO.

**Rockchip's guidance:** none on pads, vias or escape for the RK3566 (DS, HDG and HSPCB searched). The only via size in a Rockchip document is the RK3568 template's 0.2/0.4 mm (TPL item 5.2).

**Arithmetic escape check.** It assumes a 0.25 mm copper land per ball (= nominal ball Ø; NSMD or SMD is still a choice), the PCBWay HDI 0.065 mm rule (PCB-G-02) and a 0.25 mm microvia land (PCB-G-03). It is not a substitute for the escape study.

| Case | Count | How it escapes | Fits? |
|---|---|---|---|
| Outer-ring balls (row A, row AR, columns 1 and 38) | 88 | Outward on L1 | Yes |
| Inner-ring balls behind an outer-ring gap | 14 / 12 / 15 / 11 per side (row B / row AP / column 2 / column 37) | Outward on L1 through the gap. Neighbours 0.8 mm apart leave 0.55 mm of copper gap: one 0.075 mm trace with 0.24 mm each side, or two traces at the HDI minimum | Yes |
| Inner-ring balls behind an outer-ring ball | 20 / 22 / 16 / 20 per side (77 of 78 are signals) | Need a via. Runs of 2–3 adjacent balls at 0.4 mm occur | See next rows |
| — with laser microvias (0.10 mm drill, 0.25 mm land), dog-bone into the channel | — | Via line at mid-channel (0.41–0.44 mm from both rows). Via to ring ball 0.41 − 0.125 − 0.125 = 0.16 mm; via to via at 0.4 mm pitch 0.15 mm; both above 0.065 mm | **Yes, without via-in-pad** |
| — with 0.2/0.4 mm through vias in the channel | — | Two adjacent vias at 0.4 mm pitch touch (0.4 mm pads), so they must be staggered. The second via then lands within about 0.15 mm (centre) of the core row: 0.425 + 0.3 = 0.725 mm into a 0.825–0.875 mm channel | **No** in general; only where a core ball is missing opposite |
| Core field, 0.65 mm | 343 | Diagonal dog-bone to a 0.2/0.4 mm through via: centre 0.46 mm from each ball, copper gap 0.46 − 0.2 − 0.125 = 0.135 mm. One 0.1 mm trace between balls (0.4 mm copper gap) | Yes, with through vias |

**Answer to the via-in-pad question.** Rockchip's documents do not answer it, and neither do the reference boards, which publish no layout or stackup. By the package drawing and the arithmetic above:

- Via-in-pad is not needed to escape the 0.4 mm ring. Dog-bone laser microvias in the 0.825–0.875 mm channel fit at every inner-ring position.
- Through vias alone do not fit for adjacent inner-ring balls.
- The plain answer for the T1 is: **microvias yes (at least L1–L2), via-in-pad no**, pending the KiCad escape study. Rockchip's 6-layer through-via practice comes from the RK3568 template with a different package, so it is no counterexample.
- Two inputs change the margins: the channel also has to carry the core outer rows' own fan-out, and the PCBWay microvia land and land-to-land space are still to be confirmed (E3.6).

## 4. Decoupling (PCB-P-10)

The spec has "RK3566 guide **UNVERIFIED**". HDG now gives:

- **Placement.**
  - The DDR capacitors "should be placed under the U1000 package" (HDG p. 40, Fig. 2-26).
  - The large capacitors of VDD_CPU, VDD_LOGIC, VDD_GPU, VDD_NPU and VCC_DDR go on the back under the SoC, to keep ripple below 60 mV under heavy load (pp. 36–39).
  - PLL and USB/MIPI PHY capacitors close to their pins (pp. 35, 58, 78). A 100 nF capacitor close to each GPIO supply pin (p. 41).
  - Rockchip asks that no capacitor of the reference schematic be removed (pp. 35–39).
- **Vias and pads.**
  - One via per capacitor pad (HSPCB p. 26).
  - Capacitor ground pads under the SoC connected solid, not through thermal reliefs (HDG p. 93).
- **Values per domain** (HDG pp. 35–40). Near the SoC; source-side capacitors in the spec sheet:

| Domain | Near the SoC |
|---|---|
| VDD_CPU | 2 × 4.7 µF 0402, 22 µF 0603 |
| VDD_LOGIC | 100 nF 0201, 3 × 4.7 µF 0402, 22 µF 0603 |
| VDD_GPU | 100 nF 0201, 4.7 µF 0402, 22 µF 0603 |
| VDD_NPU | 100 nF 0201, 22 µF 0603 |
| VCC_DDR (DDR_VDDQ, 1.1 V) | 3 × 100 nF 0201, 4.7 µF 0402, 10 µF 0603 |
| VCC0V6_DDR (DDR_VDDQL, 0.6 V) | 3 × 100 nF 0201, 2 × 4.7 µF 0402 |
| SYSPLL / PMUPLL 0.9 V and 1.8 V | 1 µF 0402 + 100 nF 0201 each |

  The PLL supplies are best fed from a separate LDO (p. 35).

The spec's "smallest capacitor closest to its pin, same side" differs from Rockchip for the SoC: Rockchip puts the SoC's decoupling **on the opposite side, under the package**. This needs back-side placement under the SoC, which the PCB-Z height zones must allow.

## 5. Still not found

- The *RK3566 High Speed PCB Design Guide*, the RK3566 DDR templates, the RK3566 package pin-length table, and the *RK3566 Schematic and PCB Review Checklist* (HDG p. 4).
- A land pattern or recommended pad for FCCSP565L.
- The *RK356X Power Consumption Test Report*.
- The RK3566 EVB2 layer count and stackup, stated rather than inferred.
- The stackup of any RK3566 reference board.
- IBIS models.
