# BOM v1 (draft)

- **Status:** Superseded by [BOM v1](bom-v1.md). Kept as history.
- **Date:** 2026-10-22
- **Scope:** the T1 main board and the touch faceplate, by subsystem, including the support parts around the main ICs (regulators, switches, protection, clocks, magnetics, connectors, test access).
- **Companion:** [power tree v0](power-tree-v0.md) holds the rails, currents, gating map, sequencing and the calculations behind the power, audio, backlight and HAT picks.
- **Sources:** [BOM v0](bom-v0.md), [component selection](../research/2026-10-component-selection.md), [sourcing alternatives](../research/2026-10-sourcing-alternatives.md), [high-speed I/O topology](../research/2026-10-high-speed-io-topology.md), [battery selection](../research/2026-10-battery-selection.md), touch-faceplate ADR 0001, board ADRs 0001–0004, opendap-os ADRs 0006–0008. `2026-10-pin-multiplexing-v0.md` does not exist yet.
- **Owner rules applied:** availability first and validated; newest compatible generation; mainline Linux drivers (DKMS or validated vendor drivers acceptable); no unusual switches or tricks (BRD-042); helper MCUs never in a data path (BRD-005); audio quality and battery life first; every block power-gated when unused (BRD-008); every bus and interface protected (BRD-007); the SoC reaches every chip directly (BRD-004).

## Conventions

- **Driver path:** *mainline + Debian* (module enabled in Debian's trixie-backports `linux-config-7.2_7.2.9-1~bpo13+1` arm64 config, re-checked 2026-10-22), *DKMS* (mainline driver Debian does not enable; opendap-os ADR 0007), *none* (no driver needed).
- **Availability:** stock and qty-1 price captured **2026-10-22**. LCSC figures come from the JLCPCB parts API; Mouser, Newark, Arrow, Verical and TME figures from [FindChips](https://www.findchips.com/) (brokers excluded); Digi-Key figures from Digi-Key pages. Figures dated 2026-10-21 are carried over from the component-selection report.
- **UNVERIFIED** = no primary source found in this session.
- Datasheets (URL, revision, date, sha256) are in the [Datasheets](#datasheets) table at the end. No PDF is stored in the repository.

## 1. What changed from v0

1. **Master clocks: 45.1584/49.152 MHz → 22.5792/24.576 MHz, 1.8 V.** The CS43198 accepts an external MCLK only at 22.5792 or 24.576 MHz (DS1156F2 §4.6), and its MCLK input is in the 1.8 V VL domain. Lines 9–10 of v0 are replaced; BRD-023 (Draft) needs the same change. See power tree §1.
2. **Battery line replaced** by the battery-selection proposal (105060-class pack; Adafruit 328 for prototypes). The v0 Jauch LP705176JS fits no envelope.
3. **HAT pogo pins move to the device-side piece** (board ADR 0002, flat cable). The board now carries the flat-cable connector instead; the pogo line is kept for traceability.
4. **eFuses ×2 → ×3:** a third TPS259470 limits and protects the USB-C VBUS source path (OTG host).
5. **New support parts** around every main IC: vdd_cpu buck, LPDDR4X 0.6 V LDO, external 3.3 V buck, audio rails (TPS65131, TPS7A4901, TPS7A3001, TPS62840, TPS7A2018), load switches, backlight driver, current monitors, ESD/TVS, crystals, inductors, connectors, buttons and test access.

## 2. Bill of materials

### 2.1 Core

| # | Subsystem | Function | Part (MPN) | Qty | Status | Driver path | Availability (best source, stock, date) | Second source | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Core | SoC | Rockchip RK3566 | 1 | Decided (ADR 0003) | mainline + Debian | LCSC C2943786: 637 @ $14.60 (2026-10-22); not at Western catalog distributors | Upgrades: RK3576, i.MX 8M Plus | v0 #1 |
| 2 | Core | PMIC | Rockchip RK809-5 | 1 | Proposed | mainline + Debian (`rk8xx`, `rk808-regulator`, `rtc-rk808`, `clk-rk808`) | LCSC C2939628: 1,226 @ $2.47; RK809-5A C20417421: 631 (2026-10-22) | RK817-5 (LCSC 70) | v0 #2. Rail map copied from mainline Orange Pi 3B DT; codec and class-D unused (RK817 codec driver is Debian `=m`, an option for the speaker) |
| 3 | Core | vdd_cpu buck (I2C DVS) | Rockchip RK860-2 | 1 | Proposed | mainline + Debian (`fan53555`, `rockchip,rk8602`, `REGULATOR_FAN53555=m`) | LCSC C5156489: 2,999 @ $0.86 (2026-10-22) | Silergy SYR827PKC (same driver, LCSC 852); TI TPS62869 (`tps6286x`, Debian `=m`, Mouser 5,027; different footprint) | Radxa ZERO 3W uses RK860-0, Orange Pi 3B SYR827, RG353 a FAN53555-class part |
| 4 | Core | vdd_cpu inductor | Murata DFE252012F-R47M (0.47 µH) | 1 | Proposed | none | LCSC C703140: 1,283; Arrow 4,460 (2026-10-22) | TDK TFM252012ALMAR47MTAA, Changjiang FPA252012D-R47MT0 (LCSC 2,671) | Value and saturation current to confirm against the RK860 datasheet (**UNVERIFIED**) |
| 5 | Core | PMIC buck inductors (BUCK1–5) | Murata DFE252012F-R47M (0.47 µH) | 5 | Proposed | none | as line 4 | as line 4 | RK809 datasheet application circuit: 0.47 µH, 4 A (BUCK1, 2, 5) and 3 A (BUCK3, 4). Murata saturation rating against 4 A **UNVERIFIED** |
| 6 | Core | 3.3 V system buck (vcc3v3_sys, feeds RK809 VCC9 and eMMC) | TI TLV62569DBVR (2 A) | 1 | Proposed | none | LCSC C141836: 417,227 @ $0.07; Mouser 34,039 (2026-10-22) | TI TPS62A01 (1 A, LCSC 48,310) | EN from RK809 EXT_EN; 2.2 µH inductor (line 7) |
| 7 | Core | 3.3 V buck inductor | Murata DFE252012F-2R2M (2.2 µH) | 2 | Proposed | none | LCSC C576403: 15,523 (2026-10-22) | TDK TFM252012ALMA2R2MTAA (LCSC 6,666) | Lines 6 and 38 |
| 8 | Core | LPDDR4X 4 GB | Samsung K4UBE3D4AB-MGCL | 1 | Proposed | none (rkbin DDR blob ≥ v1.26) | LCSC C5827966: 236 @ $82.09 (2026-10-22) | SK hynix H9HCNNNCPMMLXR-NEE. **Risk:** broker prices, low stock | v0 #3 |
| 9 | Core | LPDDR4X VDDQ 0.6 V LDO | TI TPS7A1006PDSER | 1 | Proposed | none | LCSC C2863706: 1,030 @ $0.48; Mouser 5,135 (DSE) / 11,485 (PDQNR) (2026-10-22) | TI TPS7A1006PDQNR (X2SON) | VIN = vcc_ddr 1.1 V, BIAS = vcc_1v8. Need from Radxa ZERO 3W v1.12 DDR table (LPDDR4X VDDQL 0.60 V); current **UNVERIFIED** |
| 10 | Core | eMMC 32 GB | Samsung KLMBG2JETD-B041 | 1 | Proposed | none | LCSC C5821038: 270 @ $40.33; C2803245: 490 @ $45.04 (2026-10-22) | Micron, Kioxia, Longsys FORESEE. **Risk:** one stocked brand | v0 #4 |
| 11 | Core | microSD socket | Hirose DM3AT-SF-PEJM5 | 1 | Proposed | none | LCSC C114218: 15,961 @ $1.39; Digi-Key 77,167 (2026-10-21) | Molex 104031-0811 | v0 #5. VDD from RK809 SWOUT2, signalling from LDO5 (1.8/3.3 V) |
| 12 | Core | Coprocessor | Raspberry Pi RP2354A (RP2350 with flash) | 1 | Decided family (ADR 0004); part Proposed | none (flashed from OpenDAP OS) | LCSC C41378174: 8,021 @ $1.26 (2026-10-22) | RP2350A + QSPI flash | v0 #6. IOVDD at 1.8 V so it can tap the 1.8 V I2S lines without translators (RP2350 datasheet §"IOVDD") |
| 13 | Core | RP2350 core-regulator inductor | Abracon AOTA-B201610S3R3-101-T (3.3 µH) | 1 | Proposed | none | LCSC C42411119: 634; Newark 17,400; Verical 87,000 (2026-10-22) | none (Raspberry Pi requires this polarity-marked part) | Hardware design with RP2350, §"Core voltage regulator" |
| 14 | Core | RP2350 12 MHz crystal | Abracon ABM8-272-T3 | 1 | Proposed | none | LCSC C20625731: 4,605; Mouser 11,140 (2026-10-22) | none recommended by Raspberry Pi | Same crystal as Pico 2; 10 pF load |
| 15 | Core | SoC 24 MHz crystal | YXC X322524MOB4SI (3225, 24 MHz) | 1 | Proposed | none | LCSC C70590: 45,538 @ $0.09 (2026-10-22) | YXC XL2EL89COI-111YLC-24M (LCSC 14,700) | Load capacitance per the RK3566 hardware design guide (**UNVERIFIED**, guide not retrieved) |
| 16 | Core | RTC 32.768 kHz crystal (RK809) | Seiko SC-32S 32.768 kHz 20 ppm, 7 pF | 1 | Proposed | none | LCSC C97604: 133,710 @ $0.19 (2026-10-22) | SC-32S 12.5 pF (LCSC 103,834); Epson FC-135 (LCSC 0) | Load capacitance to match the RK809 oscillator (**UNVERIFIED**) |
| 17 | Core | Board-ID / calibration EEPROM (2 kbit) | Microchip AT24C02D-STUM-T | 1 | Proposed | mainline + Debian (`at24`, `EEPROM_AT24=m`) | Mouser 23,696; LCSC C79996: 8,212 (2026-10-22) | ST M24C02-RMN6TP (SO-8, LCSC 188,302) | Board revision, serial, headphone-output trim; not used for faceplate ID (T1-020) |

### 2.2 Audio

| # | Subsystem | Function | Part (MPN) | Qty | Status | Driver path | Availability (best source, stock, date) | Second source | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 18 | Audio | DAC ×2 (dual mono) | Cirrus Logic CS43198-CNZR | 2 | Decided family (ADR 0001); part Proposed | DKMS (`SND_SOC_CS43130` off in Debian) | LCSC C1554755: 346 @ $5.38 (2026-10-22); Digi-Key 471 @ $18.19 (2026-10-21) | None. DSD128 cap in the driver (opendap-os ADR 0006) | v0 #7. Rails: VA, VCP, VD, VL 1.8 V; VP 3.0–5.25 V; 26.1 mW each in playback |
| 19 | Audio | Headphone amp ×4 | TI OPA1622IDRCR | 4 | Proposed | none | LCSC C2876559: 666 @ $3.03 (2026-10-22); Digi-Key 4,558 (2026-10-21) | None | v0 #8. 2 packages for 4.4 mm (L±, R±), 2 for 3.5 mm (halves paralleled for 16 Ω, **UNVERIFIED**). EN per output for gating |
| 20 | Audio | MCLK 44.1 kHz family (1.8 V) | NDK NSC5083A-22.5792M (NZ2520SDA) | 1 | Proposed | none | NSC5083A not listed at Digi-Key (quote, **UNVERIFIED**); 3.3 V NSC5083D-22.5792M: Digi-Key 2,239 @ $2.30 (2026-10-22) | Crystek CCHD-957 for reference measurements | Replaces v0 #9 (45.1584 MHz). Tri-state standby lets both XOs share one MCLK net |
| 21 | Audio | MCLK 48 kHz family (1.8 V) | NDK NSC5083A-24.576M (NZ2520SDA) | 1 | Proposed | none | as line 20; 3.3 V NSC5083D-24.576M: Digi-Key 3,083 @ $2.94 (2026-10-22) | Crystek CCHD-957 | Replaces v0 #10 (49.152 MHz) |
| 22 | Audio | HP-amp pre-rails ±6 V | TI TPS65131RGER | 1 | Proposed | none | LCSC C87663: 2,826 @ $2.88; Mouser 2,182; Arrow 2,175 (2026-10-22) | No pin-compatible part; fallback topology: 5.5 V boost + TI LM27762 (LCSC 41,293) | 1 µA shutdown, PSP/PSN power-save; power tree §4.2 |
| 23 | Audio | TPS65131 inductors | Murata DFE252012F-4R7M (4.7 µH) | 2 | Proposed | none | LCSC C668313: 5,859 (2026-10-22) | TDK VLS/TFM 4.7 µH 2520 | Datasheet example uses 4.7 µH |
| 24 | Audio | TPS65131 rectifiers | Nexperia PMEG2010AEH (20 V, 1 A) | 2 | Proposed | none | LCSC C110921: 12,253 (2026-10-22) | onsemi MBRM120LT1G (datasheet example, LCSC 15,827) | — |
| 25 | Audio | +5.0 V HP-amp LDO | TI TPS7A4901DGNR | 1 | Proposed | none | LCSC C16430: 9,656 @ $1.45 (2026-10-22) | ADI LT3045 (LCSC 3,180, 2.2 mA Iq); TI TPS7A2050 (if pre-rail ≤ 5.5 V) | 15.4 µVrms, 72 dB at 120 Hz, 150 mA |
| 26 | Audio | −5.0 V HP-amp LDO | TI TPS7A3001DGNR | 1 | Proposed | none | LCSC C33835: 8,391 @ $2.02 (2026-10-22); DRBR C2865863: 3,261 | ADI LT3094 (LCSC 1,422); ADI ADP7182 (LCSC 4,911) | 15.1 µVrms, 200 mA, 55 µA Iq |
| 27 | Audio | Audio 2.2 V pre-buck | TI TPS62840DLCR | 1 | Proposed | none | LCSC C2071859: 6,365; YBGR C2071139: 3,798 (2026-10-22) | TI TPS62A01 (LCSC 48,310) | 60 nA Iq; saves ~42 mW vs. LDOs from VSYS (power tree §4.3) |
| 28 | Audio | TPS62840 inductor | Murata DFE201610E-2R2M (2.2 µH) | 1 | Proposed | none | LCSC C337891: 855 (2026-10-22) | DFE201610E-1R0M (LCSC 21,995) if the datasheet allows 1 µH | — |
| 29 | Audio | 1.8 V low-noise LDOs (DAC1 VA, DAC2 VA, MCLK) | TI TPS7A2018PDBVR | 3 | Proposed | none | LCSC C963430: 13,236 @ $0.26; Mouser 3,163 (2026-10-22) | TPS7A2018PDQNR (X2SON); TI LP5907-1.8 (LCSC 29,195) | 7 µVrms, 95 dB PSRR at 1 kHz, 6.5 µA Iq; noise budget in power tree §4.3 |
| 30 | Audio | 3.5 mm jack | Same Sky SJ2-35954D-SMT-TR | 1 | Proposed | none | Mouser 4,528 (2026-10-22, sourcing report); LCSC C4992270: 71 | SJ2-35894D-SMT-TR | v0 #11. Detect switches to SoC GPIO (`simple-audio-card` jack) |
| 31 | Audio | 4.4 mm balanced jack | Pentaconn 4.4 mm (Nippon DICS, by quote) | 1 | Proposed | none | Quote only (NDICS Hong Kong/Shenzhen) | **Risk:** single source, at no distributor. G-Switch GT-3321667P-01 (LCSC) unverified | v0 #12. G-Switch: LCSC C2762984: 730 @ $7.30 (2026-10-22) |
| 32 | Audio | Speaker amp | ADI MAX98357AETE+T | 1 | Proposed | mainline + Debian | LCSC C910544: 18,910 @ $1.32 (2026-10-22) | MAX98360A (same driver) | v0 #13. VDD = VSYS; gated by SD_MODE. Limit gain: speaker is 0.7 W |
| 33 | Audio | Speaker | Same Sky CMS-151125-078S-67 | 1 | Proposed | none | Digi-Key 719 (2026-10-21); LCSC C3310572: 0 | PUI AS01508MR-6-R | v0 #14. Spring contacts on gold pads; no connector |
| 34 | Audio | Microphones ×2 (main on faceplate, ambient-noise on the body) | Infineon IM73D122V01XTMA1 (PDM) | 2 | Proposed | mainline + Debian | LCSC C5563886: 5,352 @ $2.88 (2026-10-22); Mouser 15,038 | Infineon IM72D128 | v0 #15. VDD 1.62–3.6 V on gated MIC_1V8 |
| 35 | Audio | Mic power switch + privacy-LED gate | Diodes DMG1012T-7 (N-MOSFET, VGS(th) ≤ 1.0 V) | 1 | Proposed | none | LCSC C20512: 125,636; Newark 1,042,692 (2026-10-22) | Nexperia/onsemi logic-level SOT-523 FET | Gate = MIC_1V8, so the LED cannot light without mic power (BRD-027) |
| 36 | Audio | Headphone output ESD (L±, R± on 4.4 mm; L, R on 3.5 mm; 2 detect lines) | TI TPD1E10B06DPYR (bidirectional, 12 pF, ±5.5 V) | 8 | Proposed | none | LCSC C48260: 303,333 @ $0.04; Newark 61,842 (2026-10-22) | Tech Public TPD1E10B06 (LCSC 19,651); onsemi ESD9B5.0ST5G (LCSC 237,799) | Bidirectional because outputs swing ±4 V. 12 pF is negligible at 20 kHz |
| 37 | Audio | HP-amp precision resistors (difference amps, feedback, ballast) | Panasonic ERA-3AEB series (0603, 0.1 %, thin film) | ~40 | Proposed | none | LCSC (e.g. C2074417: 4,200) (2026-10-22) | Susumu RG1608, Yageo RT0603 | Values from the OPA1622 difference-amplifier example; C0G 470 pF caps listed in §5 |

### 2.3 Power

| # | Subsystem | Function | Part (MPN) | Qty | Status | Driver path | Availability (best source, stock, date) | Second source | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 38 | Power | HAT 3.3 V buck | TI TLV62569DBVR | 1 | Proposed | none | as line 6 | TI TPS62A01 | Feeds eFuse #B |
| 39 | Power | Charger / power path | TI BQ25895RTWR | 1 | Proposed | mainline + Debian | LCSC C80200: 5,942 @ $2.13; Mouser 3,608 (2026-10-22) | Newer: BQ25798 (needs a mainline entry + DKMS) | v0 #16. OTG 4.5–5.5 V up to 3.1 A for HAT and USB-C source |
| 40 | Power | Charger inductor (1 µH, Isat ≥ 5 A) | Coilcraft XAL4020-102MEC | 1 | Proposed | none | LCSC C4555951: 7,677 @ $4.32 (2026-10-22) | Würth 74438357010 (LCSC 0); Murata 1239AS-H-1R0M (LCSC 12,604, lower current) | Datasheet §9: 1 µH and ≥ 20 µF on SYS |
| 41 | Power | USB-PD controller | onsemi FUSB302BMPX | 1 | Proposed | mainline + Debian | LCSC C132291: 1,635 @ $0.84 (2026-10-22); Digi-Key 5,545 (2026-10-21) | Richtek RT1715 | v0 #17. VDD from vcc3v3_pmu (always on) |
| 42 | Power | Fuel gauge | ADI MAX17055EWL+T | 1 | Proposed | DKMS (`BATTERY_MAX17042` off) | LCSC C2682627: 5,840 @ $1.52 (2026-10-22); Mouser 10,332 (2026-10-21) | TI BQ27Z561 | v0 #18 |
| 43 | Power | Gauge sense resistor 10 mΩ 1 % | Yageo RL0603FR-070R01L | 1 | Proposed | none | LCSC C728437: 69,111 (2026-10-22) | Vishay WSL0603R0100FEA (LCSC 0) | MAX17055 typical 10 mΩ (**UNVERIFIED**, datasheet not downloaded) |
| 44 | Power | eFuse ×3 (HAT 5 V out, HAT 3.3 V out, USB-C VBUS out) | TI TPS259470ARPWR | 3 | Proposed | none | LCSC C3662799: 3,761 @ $1.29 (2026-10-22); Digi-Key 76,492 (2026-10-21) | TPS259472A / TPS259474L | v0 #19 (was ×2). ILIM 1.5 / 1.0 / 1.5 A; IMON to SoC SARADC (power tree §4.6) |
| 45 | Power | Power mux (USB-C IN1 priority, powerbank HAT IN2) | TI TPS2121RUXR | 1 | Proposed | none | LCSC C485916: 25,546 @ $0.92; Mouser 18,252 (2026-10-22) | — | v0 #20. OV1 ≈ 14.5 V; OV2 driven by `HAT_SRC_DIS` |
| 46 | Power | Battery | 1S LiPo pack, 105060 size class (max 10.3 × 50.5 × 62.5 mm with PCM), ≥ 3,000 mAh, PCM + 10 kΩ NTC + latching connector, IEC 62133-2 + UN 38.3 (quote: Jauch / EEMB / Grepow). Prototypes and DIY kit: Adafruit 328 | 1 | Proposed | none (charge voltage and gauge model per pack in DT) | Adafruit 328: Digi-Key 1,834 @ $14.95 (2026-10-22); 105060 pack: quote, **UNVERIFIED** | USE-104060-3K-PCBJST (no certificates yet), Adafruit 2011 | Replaces v0 #21 per the battery-selection report §9 |
| 47 | Power | Battery connector (2-pin, stocked packs) | JST S2B-PH-SM4-TB(LF)(SN) | 1 | Proposed | none | LCSC C295747: 29,219 (2026-10-22) | JST S3B-PH-SM4-TB (3-pin, NTC packs; LCSC 60,710, Mouser 68,446) | Commercial NTC pack would use the 3-pin part: one footprint each, **open question** |
| 48 | Power | Board-side battery NTC 10 kΩ | Murata NCP15XH103F03RC | 1 | Proposed | none | LCSC C77131: 273,958; Arrow 280,000 (2026-10-22) | — | Pressed against the pocket floor, to BQ25895 TS; B = 3380 K (charger TS divider set for it) |
| 49 | Power | vdd_npu, vdd_gpu, vdd_logic, vcc_ddr, vcc_1v8, LDO1–9, RTC | (inside RK809-5, line 2) | — | Proposed | — | — | — | Rail map in power tree §3 |
| 50 | Power | Load switches (DAC_VP, DAC_DIG_1V8, FP_IOVCC_1V8, MIC_1V8, RP_3V3, RP_IOVDD_1V8) | TI TPS22919DCKR | 6 | Proposed | none | LCSC C2149796: 42,715 @ $0.12; Mouser 21,679 (2026-10-22) | TI TPS22916CYFPR (LCSC 2,674); Vishay SiP32431DR3 (LCSC 5,617; pinout **UNVERIFIED**) | 1.5 A, 90 mΩ, QOD, 2 nA off. 2 more DNP footprints as fallback for RK809 SWOUT1/2 |
| 51 | Power | Backlight LED driver | TI TPS61169DCKR | 1 | Proposed | mainline + Debian (`pwm-backlight` on CTRL, `BACKLIGHT_PWM=m`) | LCSC C71045: 26,243 @ $0.32; Newark 3,734 (2026-10-22) | TI TPS61160DRVR (26 V OVP, LCSC 9,749) | RSET 3.40 Ω for 60 mA (power tree §4.5) |
| 52 | Power | Backlight inductor 10 µH | Murata LQH3NPN100MJRL | 1 | Proposed | none | LCSC C668449: 9,393; Mouser 6,136 (2026-10-22) | Murata LQH3NPN100MMEL (LCSC 4,745) | Peak 0.45 A at full brightness |
| 53 | Power | Backlight rectifier 40 V 1 A | Nexperia PMEG4010CEH | 1 | Proposed | none | LCSC C193342: 2,419; Newark 900 (2026-10-22) | onsemi NSR0340HT1G (LCSC 15,962) | — |
| 54 | Power | Current monitors (VSYS, audio block, display block, HAT) | TI INA236AIDDFR | 4 | Proposed | mainline + Debian (IIO `ina2xx-adc`, `ti,ina236`, `INA2XX_ADC=m`) | LCSC C5443912: 1,938 @ $2.16; Mouser 111 (2026-10-22) | TI INA226AIDGSR (same driver, LCSC 33,329); TI INA238 (hwmon, DKMS) | 1.2 V-compliant I2C; shunts 10 / 100 / 100 / 20 mΩ (§5). For T1-026 instrumentation |

### 2.4 Connectivity and sensors

| # | Subsystem | Function | Part (MPN) | Qty | Status | Driver path | Availability (best source, stock, date) | Second source | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 55 | Connectivity | Wi-Fi 6 + BT 5.4 (pre-certified) | Murata LBES5PL2EL-923 (Type 2EL, NXP IW612) | 1 | Proposed | DKMS (`nxpwifi` arrives in 7.3; `BT_NXPUART` off) | Digi-Key 938 @ $20.30 (2026-10-21); Mouser 2,820; LCSC C23572665: 0 (2026-10-22) | u-blox MAYA-W271-00B (same chip) | v0 #22. VBAT on RK809 SWOUT1 (3.3 V, **UNVERIFIED** supply range), VIO 1.8 V, SDIO on `sdmmc1` |
| 56 | Connectivity | Antenna connector | Hirose U.FL-R-SMT-1(10) | 2 | Proposed | none | LCSC C88373: 9,801; Mouser 160,436 (2026-10-22) | Hirose U.FL-R-SMT-1(80) (LCSC 123,360) | One per module antenna pin; number of RF pins on Type 2EL **UNVERIFIED** |
| 57 | Connectivity | Antenna (2.4/5 GHz FPC) | Molex 146187-0050 | 2 | Proposed | none | TME 3,488; Verical 3,488 (2026-10-22) | Taoglas / Kyocera AVX dual-band FPC (**UNVERIFIED**) | Placement depends on case (metal or polymer) |
| 58 | Connectivity | RF matching network | 0402 C0G / inductors, π-network, DNP by default | 3 per antenna | Proposed | none | jellybean | — | Tuned on the final enclosure |
| 59 | Sensors | IMU | ST LSM6DSV16XTR | 1 | Proposed | mainline + Debian | LCSC C5267406: 7,746 @ $3.36 (2026-10-22); Mouser 4,510 (2026-10-21) | LSM6DSOXTR (same driver and footprint) | v0 #23. On vcc_1v8, always on for wake-on-motion |
| 60 | Sensors | Ambient light sensor (on the faceplate) | Vishay VEML6030 | 1 | Proposed | mainline + Debian | LCSC C132182: 10,967 @ $0.72 (2026-10-22) | LTR-303ALS-01 | v0 #24. VDD 2.5–3.6 V from vcc_fp_2v8; I2C H-level 1.7–3.6 V, so 1.8 V I2C works |

### 2.5 Connectors, protection and interfaces

| # | Subsystem | Function | Part (MPN) | Qty | Status | Driver path | Availability (best source, stock, date) | Second source | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 61 | Interfaces | Main USB-C (USB 2.0 OTG + PD) | GCT USB4105-GF-A | 1 | Proposed | none | Digi-Key 91,262 (2026-10-21); LCSC variants -120: 2,890, -060: 1,133 (2026-10-22) | Amphenol 12402012E212A. IP67 option for the Commercial edition: GCT USB4730-GF-A | v0 #25 |
| 62 | Protection | USB ESD (D+/D−) | TI TPD4E05U06DQAR | 1 | Proposed | none | LCSC C138714: 211,256 @ $0.08; Newark 35,363 (2026-10-22) | Tech Public, MSKSEMI | v0 #26. 0.42–0.5 pF |
| 63 | Protection | CC/SBU protection | TI TPD8S300ARUKR | 1 | Proposed | none | LCSC C2649824: 60; Mouser 2,800 (2026-10-21) | TI TPD4S311A (LCSC 7) | v0 #27. **Low LCSC stock**. Dead-battery Rd included |
| 64 | Protection | USB-C VBUS TVS (22 V flat clamp) | TI TVS2200DRVR | 1 | Proposed | none | Mouser 5,672; LCSC C523793: 504 (TI) / C55616459: 2,360 (Maxinmicro) (2026-10-22) | Littelfuse/MDD SMBJ24A (LCSC 58,577; softer clamp) | Clamp coordination is a risk (power tree §4.7) |
| 65 | Protection | HAT 5 V and 3.3 V rail TVS (5 V flat clamp) | TI TVS0500DRVR | 2 | Proposed | none | Mouser 70,452; LCSC C609571: 3,693 (2026-10-22) | MDD SMF5.0A (LCSC 551,604) | At the HAT flat-cable connector |
| 66 | Interfaces | HAT flat-cable connector (board side) | Open. Candidate Hirose FH35C-61S-0.3SHW(50) | 1–2 | Open | none | FH35C-61S (99) packaging: LCSC 200; (50): 0 (2026-10-22) | I-PEX CABLINE micro-coax (**UNVERIFIED**) | ADR 0002, BRD-013. Needs ~12 diff pairs + grounds + sidebands + power: likely > 61 pins or two connectors. SI of 5 Gb/s over FPC to be proven |
| 67 | Interfaces | HAT pogo pins (~128) | Harwin P70-1000045R | ~128 | Proposed | none | Digi-Key 5,006 (2026-10-21); LCSC C17702549: 0 (2026-10-22) | Mill-Max 0906 (through-hole) | v0 #28. Moves to the device-side piece (ADR 0002, hat-standard scope); kept here for traceability |
| 68 | Protection | HAT high-speed ESD (USB 3 SS ×2 pairs, PCIe TX/RX/REFCLK ×3 pairs, CSI-2 ×5 pairs, USB 2 ×2 pairs) | TI TPD4E05U06DQAR | 6 | Proposed | none | as line 62 | TI TPD1E04U04DPYR per line (0.5 pF; Mouser 7,608, LCSC 10,280) | 0.42–0.5 pF meets the 5 Gb/s budget (§4). Place at the user-touchable pogo field (device-side piece); board footprints at the flat cable as fallback |
| 69 | Protection | HAT low-speed ESD (I2C, GPIO, PRESENT#, PERST#, CLKREQ#, WAKE#, UART) | TI TPD6E05U06RVZR | 4 | Proposed | none | LCSC C962978: 880; Arrow 1,857 (2026-10-22) | TPD4E05U06 ×6 | 6 channels per part |
| 70 | Interfaces | HAT high-speed AC-coupling caps (USB 3 SSTX, PCIe TX) | 100 nF X7R 0201 | 4 | Proposed | none | jellybean | — | 75–265 nF window (USB 3), 75–200 nF (PCIe Gen2) |
| 71 | Interfaces | Faceplate FPC connector | Hirose FH35C-45S-0.3SHW(50) | 1 | Proposed | none | LCSC C424664: 3,599 @ $0.35 (2026-10-22) | Hirose FH26W-45S-0.3SHW(60) | v0 #29. Carries DSI, I2C (touch, ALS), INT/RST, BL LEDA/LEDK, PWM, mic PDM, LEDs, VCI 2.8 V, IOVCC 1.8 V, 3.3 V |
| 72 | Protection | Faceplate DSI and low-speed ESD | TI TPD4E05U06DQAR | 2 | Proposed | none | as line 62 | Tech Public / BORN clones | DSI clock + up to 4 lanes; faceplate is service-replaceable |
| 73 | Protection | microSD ESD (CLK, CMD, D0–D3) | TI TPD6E05U06RVZR | 1 | Proposed | none | as line 69 | TPD4E05U06 ×2 | UHS-I at 1.8 V: ≤ 0.5 pF keeps SDR104 edges |
| 74 | Protection | Button ESD (Power, Action, Vol+, Vol−) | TI TPD1E10B06DPYR | 4 | Proposed | none | as line 36 | onsemi ESD9B5.0ST5G | — |
| 75 | Interfaces | Level translation (DNP option) | TI LSF0204DYZPR | 0 (DNP ×2) | Proposed | none | Verical 162,210; LCSC (PWR) 9,360 (2026-10-22) | TI TXB0104 (push-pull only) | Not needed in the baseline (§4.2): footprints for a 1.8 V faceplate bank meeting a 3.3 V-only faceplate |

### 2.6 Mechanical and miscellaneous

| # | Subsystem | Function | Part (MPN) | Qty | Status | Driver path | Availability (best source, stock, date) | Second source | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 76 | Controls | Action button (deeper travel, clear click) | C&K KMR221GLFS | 1 | Proposed | mainline + Debian (`gpio-keys`) | LCSC C72443: 4,368 @ $0.65 (2026-10-22) | Alps SKHHLQA010 (LCSC 2,416) | T1-022. Feel to be sampled with the case plunger; travel and click spec **UNVERIFIED** |
| 77 | Controls | Power (also MaskROM), Vol+, Vol− | C&K PTS815SJM250SMTRLFS | 3 | Proposed | mainline + Debian (`gpio-keys`; Vol keys may use `adc-keys`, `KEYBOARD_ADC=m`) | Mouser 165,929; LCSC C2689510: 32,314 (2026-10-22) | Panasonic EVQ-P7A01P (LCSC 7,880); Alps SKRPACE010 (LCSC 67,869) | Power → RK809 PWRON. MaskROM/recovery wiring is an open question (§8) |
| 78 | Controls | MaskROM steering diode (if Power doubles as MaskROM) | Nexperia BAT54C,215 | 1 | Proposed | none | LCSC C37704: 188,997 (2026-10-22) | onsemi BAT54CLT1G (LCSC 234,967) | Isolates PWRON from SARADC_VIN0; validity of the scheme is **UNVERIFIED** |
| 79 | Faceplate | Status LED (developer-controllable) | Everlight 19-217/GHC-YR1S2/6T (green, 0603) | 1 | Proposed | mainline + Debian (`leds-pwm` / `leds-gpio`) | LCSC C2986059: 822,393 (2026-10-22) | XINGLIGHT XL-1608UGC-04 (LCSC 2,253,540) | FPT-003, FPT-016 |
| 80 | Faceplate | Microphone privacy LED | Everlight 19-217/R6C-AL1M2VY/6T (red, 0603) | 1 | Proposed | none (hardware-tied to mic power) | LCSC C2986060: 3,786,700 (2026-10-22) | Kento KT-0603R | BRD-027; switched by line 35 |
| 81 | Faceplate | Display | Focus LCDs E35GH-I-MW800-CB (3.5" 320×480 IPS, MIPI DSI) | 1 | Decided (faceplate-touch ADR 0001) | DKMS (mainline compatible, off in Debian) | Digi-Key 9 @ $56.55; Focus LCDs 9 @ $45.24 (2026-10-22, display research) | Displaytech DT035CTFT-IPS-SHB-PTS. Production volume by quote | v0 #30. Spec rev 1.0: VCI 2.5–3.3 V, IOVCC 1.65–3.3 V, backlight 10 LEDs 60 mA, VF 14–16.5 V |
| 82 | Faceplate | Touch controller | Goodix GT911 (on the display module) | 1 | Decided with the display | mainline + Debian | on the module | Best available touch technology (FPT-021) | v0 #31 |
| 83 | Faceplate | Cover glass (lens) | Custom, optically bonded | 1 | Open | none | quote | — | v0 #32. FPT-022 |
| 84 | Faceplate | Display FPC mating connector (on the faceplate flex) | Hirose FH12-20S-0.5SH(55) | 1 | Proposed | none | LCSC C596730: 3,496; Mouser 14,597 (2026-10-22) | — | Named by the Focus spec for the TFT tail |
| 85 | Faceplate | Touch FPC mating connector | Hirose FH12-6S-0.5SH(55) | 1 | Proposed | none | LCSC C202118: 1,831; Mouser 15,235 (2026-10-22) | — | Named by the Focus spec for the CTP tail |
| 86 | Misc | Test points (rails, I2C, PG, enables) | bare pads, Ø 0.8–1.0 mm | ~40 | Proposed | none | — | — | One per rail in the power tree + every enable and PG |
| 87 | Misc | Early-boot UART pads (TX, RX, GND) | bare pads | 3 | Proposed | none | — | — | BRD-047; 1.8 V or 3.3 V per the UART2 bank |
| 88 | Misc | I2S/DSD test pads (MCLK, SCLK, LRCK, SDO0, SDO1, DSD lines, GND) | bare pads | ~8 | Proposed | none | — | — | BRD-040; RP2354A taps the same nets passively (BRD-041) |
| 89 | Misc | RP2354A SWD pads | bare pads | 3 | Proposed | none | — | — | OpenDAP OS can also flash over USB (BRD-015) |
| 90 | Misc | Shielding cans (SoC + DDR + PMIC; audio stage) | Open (Würth / Laird two-piece frame + cover) | 2 | Open | none | **UNVERIFIED** | — | DNP footprints first; fit only if EMC or audio measurements require |

## 3. Debian driver status of the new lines

All checked against `config.arm64_none_arm64` from `linux-config-7.2_7.2.9-1~bpo13+1` on 2026-10-22.

| Symbol | Status | Lines |
|---|---|---|
| `REGULATOR_FAN53555` | `=m` | 3 |
| `MFD_RK8XX_I2C`, `RTC_DRV_RK808`, `COMMON_CLK_RK808` | `=y` | 2 |
| `REGULATOR_RK808` | `=m` | 2 |
| `CHARGER_BQ25890`, `TYPEC_FUSB302` | `=m` | 39, 41 |
| `BATTERY_MAX17042`, `SND_SOC_CS43130`, `BT_NXPUART` | not set (DKMS) | 42, 18, 55 |
| `INA2XX_ADC` | `=m` | 54 |
| `SENSORS_INA2XX`, `SENSORS_INA238`, `SENSORS_INA3221` | not set | (alternatives only) |
| `BACKLIGHT_PWM`, `LEDS_PWM`, `LEDS_GPIO` | `=m` | 51, 79 |
| `EEPROM_AT24` | `=m` | 17 |
| `KEYBOARD_GPIO`, `KEYBOARD_ADC`, `ROCKCHIP_SARADC` | `=m` | 76, 77 |
| `SND_SOC_MAX98357A`, `SND_SOC_ROCKCHIP_PDM`, `SND_SOC_DMIC`, `SND_SOC_ROCKCHIP_I2S_TDM`, `SND_SIMPLE_CARD`, `SND_AUDIO_GRAPH_CARD` | `=m` | 18, 32, 34 |
| `SND_SOC_RK817` (RK809 codec, unused option) | `=m` | 2 |
| `REGULATOR_TPS6286X` (second-source vdd_cpu) | `=m` | 3 |
| `PHY_ROCKCHIP_NANENG_COMBO_PHY`, `TYPEC_MUX_GPIO_SBU`, `USB_ONBOARD_DEV` | `=m` | HAT topology |
| `PCIE_ROCKCHIP_DW_HOST` | `=y` | HAT topology |

## 4. Protection, level shifting and clocks

### 4.1 ESD capacitance budget for high-speed lines

A shunt capacitance C on a line of characteristic impedance Z0 sees the two line halves in parallel, so its time constant is τ = (Z0/2)·C, and it adds a 10–90 % edge of about 2.2·τ.

| Interface | Z0 single-ended | Unit interval | C per line | 2.2·τ | Share of UI | Verdict |
|---|---|---|---|---|---|---|
| USB 3 Gen 1, PCIe Gen 2 (5 Gb/s) | 45 Ω (90 Ω diff) | 200 ps | 0.5 pF (TPD4E05U06 typ) | 25 ps | 12 % | OK |
| same | 45 Ω | 200 ps | 1.0 pF | 50 ps | 25 % | Marginal; avoid |
| CSI-2 D-PHY (2.5 Gb/s per lane max) | 50 Ω | 400 ps | 0.8 pF (TPD4E1U06) | 44 ps | 11 % | OK; TPD4E05U06 used anyway for one part number |
| USB 2.0 HS (480 Mb/s) | 45 Ω | 2.08 ns | 0.5 pF | 25 ps | 1 % | OK |
| MIPI DSI to the faceplate (1 lane, ≤ 500 Mb/s) | 50 Ω | ≥ 2 ns | 0.5 pF | 28 ps | 1.4 % | OK |
| Headphone outputs (audio) | — | — | 12 pF (TPD1E10B06) | — | — | 12 pF against a 1 Ω output impedance is a 13 GHz pole: irrelevant |

The add-on connectors (flat cable, pogo contact) and the passive 2:1 muxes of the topology report add their own loss and capacitance; the ESD part is the smallest term at 0.5 pF.

### 4.2 IO domains and level shifting

The RK3566 IO banks are each 1.8 V or 3.3 V, so the baseline needs **no level translator**: each bank is set to its peripheral's voltage.

| Bank / bus | Voltage | Devices | Why no translator |
|---|---|---|---|
| I2S1 (DACs), PDM (mics), I2C to DACs | 1.8 V | CS43198 VL, IM73D122 (VDD 1.8 V), RP2354A taps | CS43198 VL is 1.8 V only; RP2354A IOVDD at 1.8 V |
| SDIO `sdmmc1`, BT UART | 1.8 V | IW612 VIO | — |
| `sdmmc0` | 1.8/3.3 V switched by LDO5 | microSD | UHS-I voltage switch in the SoC bank |
| eMMC | 1.8 V VCCQ | KLMBG2JETD | — |
| DSI + faceplate low-speed (touch I2C, INT, RST, PWM) | 1.8 V | ILI9488 IOVCC, GT911 VDDIO, VEML6030 (H-level ≥ 1.7 V) | Other faceplates translate on their side; LSF0204 DNP footprints (line 75) as an escape |
| I2C0 (PMUIO2) | 3.3 V | RK809, RK860-2, BQ25895, FUSB302B, MAX17055, INA236 | Same domain as the Orange Pi 3B reference |
| HAT low-speed bank (I2C EEPROM, GPIO) | 3.3 V | HAT | Raspberry Pi HAT+ convention (HCS-017) |
| UART2 debug pads | bank voltage | — | Test pads only |

### 4.3 Clocks

| Clock | Part | Supply | Gating |
|---|---|---|---|
| SoC 24 MHz | YXC X322524MOB4SI crystal (line 15) | SoC oscillator | SoC |
| RTC 32.768 kHz | Seiko SC-32S crystal on RK809 (line 16) | RK809 | always on |
| DAC MCLK 22.5792 MHz | NDK NSC5083A-22.5792M (line 20) | MCLK_1V8 | ST pin, 35 µA standby, output tri-stated |
| DAC MCLK 24.576 MHz | NDK NSC5083A-24.576M (line 21) | MCLK_1V8 | as above; the two outputs share one net, one enabled at a time |
| RP2350 12 MHz | Abracon ABM8-272-T3 (line 14) | RP2354A | with RP2354A power |
| PCIe 100 MHz REFCLK | SoC combphy2 internal output | — | HAT overlay |

## 5. Passives and magnetics (estimate)

Counts are scaled from the Radxa ZERO 3W v1.12 schematic (RK3566 + RK817 + LPDDR4 + eMMC + Wi-Fi + 2× USB-C + HDMI: **214 C, 117 R, 16 L, 6 ferrite beads**), plus each datasheet's application circuit for the T1-specific blocks. Values follow the cited application circuits; final counts come from the schematic.

| Subsystem | Capacitors | Resistors | Inductors | Ferrite beads | Key values |
|---|---|---|---|---|---|
| SoC, RK809, RK860, LPDDR4X, eMMC | ~150 | ~40 | 7 | 4 | 100 nF ×~90 (one per supply ball group), 1 µF ×~30, 22 µF ×~25 (buck outputs: 33 µF/22 µF per RK809 app circuit), 4.7 µF ×~12; vcc_ddr 2×22 µF + 1 µF + 10×100 nF (Radxa) |
| Charger, PD, gauge, eFuses, mux, TVS | ~30 | ~30 | 1 | 0 | BQ25895: PMID 60 µF (3.1 A OTG), SYS ≥ 20 µF, BAT 10 µF; eFuse RILM 2.21 kΩ/3.32 kΩ, CdVdt 1.8 nF; gauge 10 mΩ |
| Audio (2 DACs, 4 OPA1622, rails, clocks) | ~90 | ~60 | 3 | 4 | CS43198: FILT± 15 µF, flying caps 2.2 µF ×4 per DAC (DS1156F2 Fig. 2-1); OPA1622 difference amps 0.1 % thin film, 470 pF C0G (TI example); TPS65131 4.7 µH ×2, 10 µF X7R ×6; LDO outputs 10 µF; XO bypass 10 nF (NDK) |
| Wi-Fi/BT + antennas | ~10 | ~4 | 2 | 1 | 0402 matching (DNP) |
| RP2354A | ~15 | ~10 | 1 | 0 | 3.3 µH Abracon, 4.7 µF/100 nF per guide, 12 MHz load caps, 1 kΩ series on XOUT |
| Display, backlight, faceplate FPC | ~12 | ~10 | 1 | 1 | RSET 3.40 Ω, COUT 1 µF 50 V, CIN 4.7 µF |
| HAT path (bucks, eFuses, AC caps, sideband) | ~25 | ~20 | 1 | 1 | AC caps 100 nF 0201 ×4, PERST#/PG RC delay ≥ 100 ms |
| Sensors, mics, speaker amp, current monitors | ~12 | ~12 | 0 | 0 | INA236 shunts: 10 mΩ (VSYS, 8 A full scale at 80 mV), 100 mΩ (audio, display: 0.8 A FS), 20 mΩ (HAT, 4 A FS) |
| Buttons, LEDs, pull-ups, straps | ~10 | ~25 | 0 | 0 | I2C pull-ups 2.2 kΩ (1.8 V) / 4.7 kΩ (3.3 V); LED 1 kΩ |
| **Total** | **~354** | **~211** | **16** | **11** | **≈ 590 passives** |

## 6. Benchmark notes (reference designs)

| Design | What it confirms for the T1 | Source status |
|---|---|---|
| Anbernic RG353 family (mainline `rk3566-anbernic-rgxx3.dtsi`) | Battery-direct VCC_SYS into the PMIC, FAN53555-class vdd_cpu, 3.3 V from a PMIC buck, PWM backlight, adc-keys | Read 2026-10-22 |
| Orange Pi 3B (mainline `rk3566-orangepi-3b.dtsi`) | RK809 rail mapping (BUCK1–5, LDO1–9, SWITCH1/2), SYR827 vdd_cpu, VCC9 from an external 3.3 V rail | Read 2026-10-22 |
| Radxa ZERO 3W v1.12 schematic | RK817-5 + RK860-0, TPD4E05U06 on USB, LPDDR4/4X VDDQ table and VCC0V6_DDR option, passive counts | Read 2026-10-22 |
| TI OPA1622 datasheet application (±5 V difference amplifier) | Rail choice and output-power limits used in power tree §4.1 | Read |
| Pine64 Quartz64 / SOQuartz, Rockchip RK3566 reference schematic, Cirrus CDB43198, TI BQ25895 EVM, MAX17055 EV kit, Murata 2EL guide | — | **Not retrieved** this session |
| Commercial DAPs (FiiO, Shanling, HiBy, iBasso) | No teardown or schematic was fetched. Public marketing states dual CS43198 in some iBasso players (**UNVERIFIED**) | **Not verified** |

## 7. Open questions

1. **BRD-023:** change the master clocks to 22.5792/24.576 MHz (CS43198 constraint)?
2. **1.8 V NZ2520SDA (NSC5083A):** order by NDK quote, or use the stocked 3.3 V parts plus a translator?
3. **3.5 mm output topology:** parallel halves for 16 Ω drive (4 packages) or one half per channel (3 packages, lower power)?
4. **MaskROM on the power button (BRD-035):** the power button is held while the SoC boots, so a direct tie to SARADC_VIN0 could force MaskROM on every power-on. Accept a "hold > N s" behaviour, a Power + Vol− combination, or a recessed MaskROM pad?
5. **Battery connector:** 2-pin JST PH (stocked packs, board NTC) or 3-pin with pack NTC (commercial)? One design should pick one footprint.
6. **HAT flat cable:** connector family and pin count for 12 differential pairs plus power; is 5 Gb/s over FPC acceptable before a test coupon?
7. **HAT ESD location:** at the pogo field on the device-side piece (preferred) or on the board?
8. **Shielding cans:** fit by default, or only after EMC and audio measurements?
9. **RTC across battery swaps:** accept that the RK809 RTC loses time when the user-replaceable battery is removed, or add a backup RTC (Micro Crystal RV-3028-C7: Arrow 10, GLYN 1,000; Debian driver off, so DKMS)?
10. **Backlight driver** on the board (proposed) or on each faceplate?

## 8. Risks

1. **Memory price and availability** (lines 8, 10): LPDDR4X 236 and eMMC 270–490 at LCSC.
2. **4.4 mm jack single source** (line 31).
3. **Display stock is retail samples** (line 81); production by quote.
4. **Battery certificates not verified** (line 46).
5. **DKMS drivers** until Debian enables them (lines 18, 42, 55, 81).
6. **MCLK at 1.8 V not in distributor stock** (lines 20, 21).
7. **Thin stock:** TPD8S300A (LCSC 60), INA236 at Mouser (111), TPS7A3001 at Western distributors (0 at Mouser/TME), TPS62840DLC at Mouser (131), Murata 2EL at LCSC (0), RV-3028 (option).
8. **RK809-5 OTP defaults and VCC9 feed** are not confirmed (line 2); a wrong map is a hardware respin.
9. **TPS65131 current at low battery** read from a curve (line 22).
10. **VBUS surge clamp above downstream absolute maxima** (line 64).
11. **HAT flat-cable connector undefined** (line 66), and 5 Gb/s signal integrity over FPC plus pogo is unproven.
12. **Clone parts on LCSC** (TPD4E05U06, TVS2200, TPS7A2050 clones): the commercial edition must pin genuine-brand C-codes.
13. **Stock is a 2026-10-22 snapshot**; Digi-Key was only partly re-checked; PCBWay has no public catalog.

## Datasheets

Every MPN in this BOM. "sha256" is the hash of the PDF downloaded on 2026-10-22 from the URL shown (kept outside the repository). Where a download failed (HTTP 403, timeout or no public datasheet), the cell says "not downloaded". Revision and date come from the document itself when downloaded, otherwise **UNVERIFIED**. URLs on "not downloaded" rows were not fetched in this session (except where a failure reason is given): they follow the maker's usual document path and are **UNVERIFIED** until the follow-up spec-sheet task opens them.

| MPN | Manufacturer | Datasheet URL | Revision | Date | sha256 or "not downloaded" |
|---|---|---|---|---|---|
| RK3566 | Rockchip | <https://www.rock-chips.com/uploads/pdf/2022.8.26/192/RK3566%20Brief%20Datasheet.pdf> | Brief datasheet | 2022 | 1f97b585f023ee6e4183800650af09bf89abf7ec53bcee974674c371932bf697 |
| RK3566 (full, RK3568 family) | Rockchip | <https://dl.radxa.com/rock3/docs/hw/datasheet/Rockchip-RK3568-Datasheet-V1.0-20201210.pdf> | V1.0 | 2020-12-10 | not downloaded |
| RK809-5 | Rockchip | <https://rockchip.fr/RK809%20datasheet%20V1.01.pdf> | Rev 1.01 | 2018-08-28 | 3f9b42ed70ec5eac76ce0e7aceed6e31743a35f4773a14489a052ec75908062f |
| RK860-2 | Rockchip | no public datasheet found | UNVERIFIED | UNVERIFIED | not downloaded |
| SYR827PKC | Silergy | <https://www.silergy.com> (product page; PDF not located) | UNVERIFIED | UNVERIFIED | not downloaded |
| TPS62869 | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps62869.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| DFE252012F-R47M | Murata | <https://www.murata.com/en-us/products/productdetail?partno=DFE252012F-R47M%3DP2> | UNVERIFIED | UNVERIFIED | not downloaded |
| DFE252012F-2R2M | Murata | <https://www.murata.com/en-us/products/productdetail?partno=DFE252012F-2R2M%3DP2> | UNVERIFIED | UNVERIFIED | not downloaded |
| DFE252012F-4R7M | Murata | <https://www.murata.com/en-us/products/productdetail?partno=DFE252012F-4R7M%3DP2> | UNVERIFIED | UNVERIFIED | not downloaded |
| DFE201610E-2R2M | Murata | <https://www.murata.com/en-us/products/productdetail?partno=DFE201610E-2R2M%3DP2> | UNVERIFIED | UNVERIFIED | not downloaded |
| TLV62569DBVR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tlv62569.pdf> | SLVSDG1C | 2017-10 | 1ba6f55dfe678d06d563acd6632f1f950a497d812270806021097b55cd81d3c4 |
| TPS62A01 | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps62a01.pdf> | SLUSEG9E | 2024-06 | cad0b23ab86368916991fc9bb2840df5f9b8013320eb8b62b28ae517e53f6518 |
| K4UBE3D4AB-MGCL | Samsung | no public datasheet (NDA) | UNVERIFIED | UNVERIFIED | not downloaded |
| H9HCNNNCPMMLXR-NEE | SK hynix | no public datasheet (NDA) | UNVERIFIED | UNVERIFIED | not downloaded |
| TPS7A1006PDSER | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps7a10.pdf> | SBVS314B | 2018-10 | c2c2c5ff934b44df9fdbbff6e66f5d6397ffd5b78f6d918c91f3ffcb4dd355f9 |
| KLMBG2JETD-B041 | Samsung | no public datasheet (NDA) | UNVERIFIED | UNVERIFIED | not downloaded |
| DM3AT-SF-PEJM5 | Hirose | <https://www.hirose.com/en/product/series/DM3> (series page) | UNVERIFIED | UNVERIFIED | not downloaded |
| RP2354A | Raspberry Pi | <https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf> | Release 8, build 80d627281ed5 | 2026-10-01 | a638d6780da919162660691bfa02c6dcf7c2a0b6e9f18e2d7519c80b664a2e39 |
| RP2354A (hardware design guide) | Raspberry Pi | <https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf> | build 06a7f75e58a1 | 2026-08-20 | cef88bc7d87e67b4262ee15f2b94b03566667143f4e8daf6931828bef6408059 |
| AOTA-B201610S3R3-101-T | Abracon | <https://abracon.com/Magnetics/power/AOTA-B201610.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| ABM8-272-T3 | Abracon | <https://abracon.com/Resonators/ABM8-272.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| X322524MOB4SI | YXC | <https://www.lcsc.com/product-detail/C70590.html> (LCSC page) | UNVERIFIED | UNVERIFIED | not downloaded |
| SC-32S | Seiko Instruments | <https://www.lcsc.com/product-detail/C97604.html> (LCSC page) | UNVERIFIED | UNVERIFIED | not downloaded |
| AT24C02D-STUM-T | Microchip | <https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT24C01D-AT24C02D-I2C-Compatible-Two-Wire-Serial-EEPROM-1-Kbit-2-Kbit-DS20006064.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| CS43198-CNZR | Cirrus Logic | <https://www.cirrus.com/docs/ds/cs43198-datasheet.pdf> | DS1156F2 | 2022-12 | e2da18e07a5683ee9eb134154a31ac7f8a197587c01c250c42286ea604dd351d |
| OPA1622IDRCR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/opa1622.pdf> | SBOS727B | 2016-05 | 505556d18113e86aed84f20c1dbcfc6b4ad66ccdc5202998bd883f7a7eac9824 |
| NSC5083A-22.5792M, NSC5083A-24.576M (NZ2520SDA) | NDK | <https://www.ndk.com/images/products/catalog/c_NZ2520SDA_e.pdf> | catalog 1703A | 2017-03 (code) | b818c72bf170e8dac004fcc7e0c5639eb8ffbe22d624f2e851aef9fde8f87825 |
| TPS65131RGER | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps65131.pdf> | SLVS493E | 2022-04 | e8360b9509047317416cfd9163a09d8cdf5c8accbd4e702ad6a43292ef48e0ed |
| LM27762 | Texas Instruments | <https://www.ti.com/lit/ds/symlink/lm27762.pdf> | SNVSAF7C | 2025-10 | 465db259d11b3b2fe202661b21e1e664065ff8873056a984aa9f967a9fbdc6e0 |
| PMEG2010AEH | Nexperia | <https://assets.nexperia.com/documents/data-sheet/PMEG2010AEH.pdf> | UNVERIFIED | UNVERIFIED | not downloaded (HTTP 403 from this host) |
| MBRM120LT1G | onsemi | <https://www.onsemi.com/pdf/datasheet/mbrm120lt1-d.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| TPS7A4901DGNR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps7a49.pdf> | SBVS121E | 2015-05 | f69e957b22bcc2db72149f57c96501aedeb4ed214f016c98f562d71411474182 |
| TPS7A2050 (option) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps7a20.pdf> | SBVS338H | 2024-07 | b6c487d79ebed6dd43bf220b07fc5b3ecb9ee55d87e6daa2312acda6546046c0 |
| TPS7A3001DGNR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps7a30.pdf> | SBVS125D | 2015-06 | b60d6fd8d7220e9f8a4dcfeaa7438a5e5e419ef589e1ea85e9d04781f2203ae5 |
| TPS7A94 (rejected) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps7a94.pdf> | SBVS336C | 2023-06 | bf9c611825fdcd2b8d0887b64721e5c2cb43be68913385e8538869d62120e4bf |
| LT3045, LT3094, LT3042 (alternatives) | Analog Devices | <https://www.analog.com/media/en/technical-documentation/data-sheets/lt3045.pdf>, <https://www.analog.com/media/en/technical-documentation/data-sheets/lt3094.pdf> | UNVERIFIED | UNVERIFIED | not downloaded (timeout) |
| ADP7182 (alternative) | Analog Devices | <https://www.analog.com/media/en/technical-documentation/data-sheets/adp7182.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| TPS62840DLCR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps62840.pdf> | SLVSEC6D | 2020-03 | b715ae80beb8f08b5c4a417537c5f52e01ad0a52f3791c240146b72fec5f3214 |
| TPS7A2018PDBVR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps7a20.pdf> | SBVS338H | 2024-07 | b6c487d79ebed6dd43bf220b07fc5b3ecb9ee55d87e6daa2312acda6546046c0 |
| LP5907 (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/lp5907.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| SJ2-35954D-SMT-TR | Same Sky | <https://www.sameskydevices.com/product/resource/sj2-3595xd-smt.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| Pentaconn 4.4 mm jack | Nippon DICS | <https://www.ndics.com/brands/pentaconn/> (no public drawing) | UNVERIFIED | UNVERIFIED | not downloaded |
| GT-3321667P-01 | G-Switch | <https://www.lcsc.com/product-detail/C2762984.html> (LCSC page) | UNVERIFIED | UNVERIFIED | not downloaded |
| MAX98357AETE+T | Analog Devices | <https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf> | UNVERIFIED | UNVERIFIED | not downloaded (timeout) |
| CMS-151125-078S-67 | Same Sky | <https://www.sameskydevices.com/product/resource/cms-151125-078s-67.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| IM73D122V01XTMA1 | Infineon | <https://www.infineon.com/assets/row/public/documents/24/49/infineon-im73d122-datasheet-en.pdf> | v1.00 | 2022-08-12 | 1a597dbd8ff794b98d09a8b214eb1f9e864f36ae4a05d4eaf0d9c3ba6211ce36 |
| DMG1012T-7 | Diodes Inc. | <https://www.diodes.com/assets/Datasheets/ds31783.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| TPD1E10B06DPYR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf> | SLLSEB1G | 2024-08 | 77fb9c454aee5b14a220d256b7ee9fa9751572840478f80437393aeed2582f8d |
| ERA-3AEB series | Panasonic | <https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/AOA0000C331.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| BQ25895RTWR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/bq25895.pdf> | SLUSC88C | 2022-10 | 2667a8d185cbf9138aed63f47616d35c0d0d29da877702b32b301caa55f8d404 |
| XAL4020-102MEC | Coilcraft | <https://www.coilcraft.com/getmedia/6adcb47d-8b55-416c-976e-1e22e0d2848c/xal4000.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| FUSB302BMPX | onsemi | <https://www.onsemi.com/pdf/datasheet/fusb302b-d.pdf> | UNVERIFIED | UNVERIFIED | not downloaded (HTTP 403) |
| MAX17055EWL+T | Analog Devices | <https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17055.pdf> | UNVERIFIED | UNVERIFIED | not downloaded (timeout) |
| RL0603FR-070R01L | Yageo | <https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RL_Group_51_RoHS_L_12.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| TPS259470ARPWR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps25947.pdf> | SLVSFC9C | 2026-05 | 8f96de389903091650d4f462dcfad3210071c3ae7093623a7978f34baf8a65b4 |
| TPS2121RUXR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps2121.pdf> | SLVSEA3F | 2020-08 | b2f5950f596dc2c4ca33e4ebac27fd35e4dcc68ea63e173466123e1118e91a06 |
| Adafruit 328 (battery) | Adafruit | <https://cdn-shop.adafruit.com/datasheets/785060-2500mAh_specification_sheet.pdf> | Q/WAPL785060-1011 | 2010 | not downloaded |
| 105060-class pack | Jauch / EEMB / Grepow | by quote | UNVERIFIED | UNVERIFIED | not downloaded |
| S2B-PH-SM4-TB(LF)(SN), S3B-PH-SM4-TB(LF)(SN) | JST | <https://www.jst-mfg.com/product/pdf/eng/ePH.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| NCP15XH103F03RC | Murata | <https://www.murata.com/en-us/products/productdetail?partno=NCP15XH103F03RC> | UNVERIFIED | UNVERIFIED | not downloaded |
| TPS22919DCKR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps22919.pdf> | SLVSEN5B | 2019-05 | 743c59b01fb0891d2d0f1faba779161cd2d2b6c18edf68e6d5b3279016240c84 |
| TPS22916CYFPR (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps22916.pdf> | SLVSDO5F | 2021-12 | a4d81b70556d5564aaee9baf455b7651375a94c629448f3f7e7ced2f5c41b33f |
| SiP32431DR3 (alternative) | Vishay | <https://www.vishay.com/docs/66597/sip32431.pdf> | S20-0532-Rev. G | 2020-07-06 | b65cb9eb72321cc173cef97ffa71be590916dbacb63e4237bd89eab7d178ed59 |
| TPS61169DCKR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps61169.pdf> | SNVSA40B | 2024-06 | 7d0b8ace2459a9fd22fe7145086cbad4ccb3bb43219247459313fcba75230151 |
| TPS61160DRVR (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tps61160.pdf> | SLVS791E | 2016-07 | 61b6bd7f86e32f06067896335a65e61f43e822470302c4676a4d6042fdfb3b3b |
| LQH3NPN100MJRL | Murata | <https://www.murata.com/en-us/products/productdetail?partno=LQH3NPN100MJRL> | UNVERIFIED | UNVERIFIED | not downloaded |
| PMEG4010CEH | Nexperia | <https://assets.nexperia.com/documents/data-sheet/PMEG4010CEH.pdf> | UNVERIFIED | UNVERIFIED | not downloaded (HTTP 403 from this host) |
| INA236AIDDFR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/ina236.pdf> | SBOSA81D | 2023-08 | 47e4c0976d958a27621450eb4732ba2f1b3b3e7f5606b3f7370ad8ba456ec45d |
| INA226AIDGSR (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/ina226.pdf> | SBOS547C | 2026-08 | c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d |
| INA238 (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/ina238.pdf> | SLYS025B | 2025-05 | 66d47e5eec628369772c7a545c32420c2a0e31225efce08f9fd82aa37640f61d |
| LBES5PL2EL-923 | Murata | <https://www.murata.com/en-us/products/productdetail?partno=LBES5PL2EL-923> | UNVERIFIED | UNVERIFIED | not downloaded (datasheet link 404) |
| U.FL-R-SMT-1(10) | Hirose | <https://www.hirose.com/en/product/series/U.FL> (series page) | UNVERIFIED | UNVERIFIED | not downloaded |
| 146187-0050 | Molex | <https://www.molex.com/en-us/products/part-detail/1461870050> | UNVERIFIED | UNVERIFIED | not downloaded |
| LSM6DSV16XTR | STMicroelectronics | <https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf> | UNVERIFIED | UNVERIFIED | not downloaded (timeout) |
| VEML6030 | Vishay | <https://www.vishay.com/docs/84366/veml6030.pdf> | Rev. 1.8 | 2024-11-28 | 46bc766f22f7e933afba4c3d1e84ca836b6f3e013d1c9b73402fbb3447471b56 |
| USB4105-GF-A | GCT | <https://gct.co/files/drawings/usb4105.pdf> | drawing (revision field not parsed) | UNVERIFIED | fb331fbabee8392ed2937ed757c1610cb0f174b84625147c0b580a18eea8c0e5 |
| TPD4E05U06DQAR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf> | SLVSBO7O | 2024-08 | c167cf1e72a5473a4d2c59b6a3c0251498701da05b7785919b9ceaae3b3e02c6 |
| TPD6E05U06RVZR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tpd6e05u06.pdf> (same document as TPD4E05U06) | SLVSBO7O | 2024-08 | c167cf1e72a5473a4d2c59b6a3c0251498701da05b7785919b9ceaae3b3e02c6 |
| TPD1E04U04DPYR (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tpd1e04u04.pdf> | SLVSDG4B | 2016-08 | f48a05822f3f04931d733d809c20d723bc03d3bf3f9b6ae44dab5da22c595d11 |
| TPD4E1U06 (reference for CSI budget) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tpd4e1u06.pdf> | SLVSBQ9E | 2026-10 | 24b66f58ea59d1894a27ffe0883a0b7f6277af8f0ec407d17b517a8e9353b159 |
| TPD8S300ARUKR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tpd8s300a.pdf> | SLVSEL9 | 2018-06 | 2c1d5b68b19430efcd8127f6e425186c88fbf0bbdc268df1d053ec45af8f88f1 |
| TPD4S311A (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tpd4s311.pdf> | SLVSF72C | 2021-02 | 3f206dd65f48b10e3c1c3d4ea9df9566fb7417bb480b2c5abd018f3188229e49 |
| TVS2200DRVR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tvs2200.pdf> | SLVSED5C | 2023-08 | 84c986c9cc4f323fdb0c6840bff455438802dd6df9af5fd89c73b8bce4dced9e |
| TVS0500DRVR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/tvs0500.pdf> | SLVSED2C | 2019-11 | ac7a4dc56da905c36f143d2dc76760d526b9e143bfedaacfacf6c8f5c9541fc7 |
| FH35C-61S-0.3SHW(50) (candidate) | Hirose | <https://www.hirose.com/en/product/series/FH35C> (series page) | UNVERIFIED | UNVERIFIED | not downloaded |
| P70-1000045R | Harwin | <https://www.harwin.com/products/P70-1000045R/> | UNVERIFIED | UNVERIFIED | not downloaded |
| FH35C-45S-0.3SHW(50) | Hirose | <https://www.hirose.com/en/product/series/FH35C> (series page) | UNVERIFIED | UNVERIFIED | not downloaded |
| LSF0204DYZPR | Texas Instruments | <https://www.ti.com/lit/ds/symlink/lsf0204.pdf> | SLVSCP5H | 2021-04 | 06c40a136b3d0513f3e8812295a66eadaaa0da68ccc777d8406736895ad33c6b |
| TXB0104 (alternative) | Texas Instruments | <https://www.ti.com/lit/ds/symlink/txb0104.pdf> | SCES650K | 2025-03 | 9a852f7bcc4104df0676d7ee3e4918429c3db2cbd79a5338aca0a1d34471e400 |
| KMR221GLFS | C&K | <https://www.ckswitches.com/media/1479/kmr2.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| PTS815SJM250SMTRLFS | C&K | <https://www.ckswitches.com/media/2768/pts815.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| SKHHLQA010 (alternative) | Alps Alpine | <https://tech.alpsalpine.com/e/products/detail/SKHHLQA010/> | UNVERIFIED | UNVERIFIED | not downloaded |
| BAT54C,215 | Nexperia | <https://assets.nexperia.com/documents/data-sheet/BAT54_SER.pdf> | UNVERIFIED | UNVERIFIED | not downloaded |
| 19-217/GHC-YR1S2/6T | Everlight | <https://www.lcsc.com/product-detail/C2986059.html> (LCSC page) | UNVERIFIED | UNVERIFIED | not downloaded |
| 19-217/R6C-AL1M2VY/6T | Everlight | <https://www.lcsc.com/product-detail/C2986060.html> (LCSC page) | UNVERIFIED | UNVERIFIED | not downloaded |
| E35GH-I-MW800-CB | Focus LCDs | <https://focuslcds.com/wp-content/uploads/2025/09/E35GH-I-MW800-CB_Spec.pdf> | Rev 1.0 | UNVERIFIED | 2912a2ebd90ead827494d9b20842f6da3a1ceb43b620b62f27978a82a52c91df |
| GT911 | Goodix | programming guide copy obtained in session; source URL not recorded (Goodix publishes no public datasheet) | Rev.00 (preliminary) | 2014-08-04 | 60c6c2284b482a7acdcd2747c47a9a7d25283235ccda8c688c10e2fd3216a98b |
| FH12-20S-0.5SH(55), FH12-6S-0.5SH(55) | Hirose | <https://www.hirose.com/en/product/series/FH12> (series page) | UNVERIFIED | UNVERIFIED | not downloaded |
| Radxa ZERO 3W schematic (reference) | Radxa | <https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf> | v1.12 | UNVERIFIED | 50f0ca8af531c2c91813fb050bdaf339d37123f7d035d59ca65785df829d28bc |
