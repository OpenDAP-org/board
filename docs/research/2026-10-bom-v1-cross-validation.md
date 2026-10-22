# BOM v1 cross-validation

- **Date:** 2026-10-22
- **Status:** Desk validation. Nothing here was built, simulated or measured. It is an independent, adversarial check of the [BOM v1 draft](../specs/bom-v1-draft.md) and [power tree v0](../specs/power-tree-v0.md). The fixes are applied in [BOM v1](../specs/bom-v1.md) and in the power tree.
- **Inputs read:** BOM v1 draft, power tree v0, [board requirements](../requirements/README.md), board ADRs 0001–0009, [pin multiplexing v0](2026-10-pin-multiplexing-v0.md), [high-speed I/O topology](2026-10-high-speed-io-topology.md), [battery selection](2026-10-battery-selection.md), [component selection](2026-10-component-selection.md), [sourcing alternatives](2026-10-sourcing-alternatives.md), T1 requirements (T1-001 to T1-042), the T1 battery-life analysis, touch-faceplate ADR 0001 and requirements, HAT Case Standard requirements, opendap-os ADRs 0006–0008.
- **Method:**
  - Datasheets downloaded and read in this session: Cirrus CS43198 DS1156F2 (sha256 `e2da18e0…dd351d`, same as the draft's), TI CDC6C SNAS843D (`6756ca5f…16404`), Adafruit 328 cell specification Q/WAPL785060-1011 (`826149da…8ecd3`).
  - Stock: JLCPCB parts API (= LCSC), Digi-Key search pages, FindChips (brokers excluded) on 2026-10-22.
  - Everything else is checked against the documents above and marked **UNVERIFIED** where no primary source was read in this session.
- **Limits:** the session's web-search budget was exhausted, so only direct fetches were possible. Hirose and Epson document servers returned HTTP 403 or HTML instead of PDFs. Mouser pages are only seen through FindChips. Machine load was high, so no local builds or simulations were run.

---

## 1. Summary

**Blockers found (5):**

1. **MCLK (lines 20–21):** the 1.8 V NDK NSC5083A has no authorized stock anywhere. No active, stocked, audio-grade 1.8 V oscillator at 22.5792 MHz was found. ADR 0009 forbids the 3.3 V + translator route. **Not fixable by part substitution; the maintainers decide (§4).**
2. **Battery (line 46):** the draft's primary was a quoted 105060 pack, which contradicts ADR 0007 and T1-038. **Fixed:** Adafruit 328, second source Adafruit 2011.
3. **Battery current:** VSYS was rated 3.5 A and the OTG budget 3.0 A at 5 V, but the pack's JST PH lead and the board header are rated 2 A per contact. **Fixed:** 2.0 A battery budget, software power budget for HAT and USB-C source.
4. **HAT 5 V while charging:** the BQ25895 OTG boost cannot run while the charger is active, so a class A/B HAT lost 5 V whenever USB-C power was present. **Fixed:** TPS61088 boost from VSYS behind the eFuses.
5. **Self-feeding loop:** when the T1 sources USB-C VBUS, that VBUS is TPS2121 IN1. Only IN2 had an interlock, and that one was software-ordered. **Fixed:** OV1 and OV2 are forced by hardware OR of the source enables. This one is a major rather than a true blocker, but it is listed here because it can oscillate the charger.

**Majors fixed:** IO-domain contradictions (I2C0 at 3.3 V on the same bank as the 1.8 V-only DAC I2C, faceplate at 1.8 V against the pin plan), RK860-2 → RK860-0, a faceplate connector with zero spare contacts (ADR 0006), missing expander, translator and MaskROM parts, an open HAT connector (now Hirose DF40), the 4.4 mm jack being quote-only (T1-029), under-counted ESD, and the Action switch likely failing T1-022.

---

## 2. Findings

Line numbers are the draft's. Severity: **blocker** = violates a must rule or cannot work; **major** = wrong or missing for a confirmed requirement, fixable; **minor** = clarity, second source or verification gap.

| # | Line | Issue | Severity | Evidence | Fix (applied in BOM v1 unless noted) |
|---|---|---|---|---|---|
| F1 | 20, 21 | 1.8 V MCLK oscillators NSC5083A-22.5792M / -24.576M are not stocked at any authorized distributor | blocker | [FindChips NSC5083A-22.5792M](https://www.findchips.com/search/NSC5083A-22.5792M) and [-24.576M](https://www.findchips.com/search/NSC5083A-24.576M): "No results" (2026-10-22). [Digi-Key NZ2520SDA](https://www.digikey.com/en/products/result?keywords=NZ2520SDA) lists only the 3.3 V NSC5083D (22.5792M: 2,239; 24.576M: 3,083). LCSC C2847209 / C2846938 (NZ2520SDA 22.5792/24.576 MHz): 0 | Lines marked **Blocker**; 2520 land kept; options in §4 |
| F2 | 20, 21 | Draft fallback "3.3 V part + translator" | blocker | ADR 0009 forbids it | Removed |
| F3 | 46 | Primary battery is a quoted 105060 pack; ADR 0007 says off-the-shelf stocked packs only (T1-038) | blocker | ADR 0007; T1-038 | Adafruit 328 (Decided, ADR 0007), Adafruit 2011 second source |
| F4 | 46, 47, power tree §3 | VSYS 3.5 A and OTG 3.0 A at 5 V exceed the battery path rating | blocker | Adafruit 328 sheet: discharge ≤ 2C (5 A). JST PH contact rating 2 A (JST PH catalog, **UNVERIFIED** this session; the draft links [ePH.pdf](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf)). Lead wire gauge **UNVERIFIED** | Battery budget 2.0 A; HAT_5V + USB-C source ≈ 0.7 A at 5.1 V on battery; OpenDAP OS enforces with the VSYS INA236 (power tree §4.6) |
| F5 | 39, 44 | HAT_5V and USB-C source come from the BQ25895 OTG boost, which is off while charging | blocker | BQ25895 boost (OTG) and charge modes are exclusive (SLUSC88C, **UNVERIFIED** section number) | New line 91: TPS61088 (LCSC C87357: 7,570) + XAL4020-152MEC (line 92) feeding eFuses #A/#C. OTG unused |
| F6 | 45 | T1-sourced USB-C VBUS re-enters the charger through TPS2121 IN1 | major | Power tree §2: USB-C VBUS → TPS2121 IN1; eFuse #C drives the same connector VBUS | OV1 forced by `USB_SRC_ON`, OV2 by `HAT_SRC_ON` (hardware OR) |
| F7 | §4.2 | I2C0 listed at 3.3 V, but I2C0, I2C1 and I2C2 M0 (DAC control) are all in PMUIO2, and the CS43198 VL pins tolerate only VL + 0.3 V | major | Pin plan §1.4, §5 (PMUIO2 1.8 V); DS1156F2 absolute maxima (VL domain −0.3 to VL + 0.3 V; digital interface VL ≤ 2.33 V) | PMUIO2 = 1.8 V for all three buses; 1.8 V VIH of FUSB302B, MAX17055, BQ25895 marked **UNVERIFIED** |
| F8 | §4.2, 60, 71 | Faceplate low-speed at 1.8 V in the BOM vs VCCIO5 3.3 V in the pin plan (shared with speaker I2S3 and HAT PWM) | major | Pin plan §2.4, §4.1, §5 | Faceplate bank 3.3 V; FP_3V3 rail added; panel RST/TE translated on the faceplate (line 96) |
| F9 | 3 | RK860-2 is the RK3588 big-core variant (`rockchip,rk8602`, different OTP default and registers); the RK3566 reference uses RK860-0 | major | Draft §6 (Radxa ZERO 3W uses RK860-0); LCSC RK860-0 C19188628: 4,528 vs RK860-2: 2,999 | RK860-0, `rockchip,rk8600`. OTP voltage and the 0x40 address **UNVERIFIED** (no public datasheet) |
| F10 | 71 | FH35C-45S leaves 0 spare contacts; ADR 0006 asks for ≥ ≈ 10 % | major | Pin plan §4.1 (45 = 45) | [FH35C-51S-0.3SHW(50)](https://www.findchips.com/search/FH35C-51S): Mouser 8,070, Newark 2,312. 44 used + 7 spare (§5) |
| F11 | 51, 71 | Faceplate signal set differs between BOM (board backlight: LEDA/LEDK, VCI 2.8 V, IOVCC 1.8 V) and pin plan (VSYS_FP ×2 + BL PWM/EN on the faceplate) | major | Pin plan §4.1 vs draft line 71 | Unified set in §5: board-side backlight, LEDA/LEDK, FP_3V3 ×2, FP_1V8, FP_VCI (LDO4), MIC_1V8 |
| F12 | — | Parts the pin plan relies on are missing: TCA6416A expander, PCA9306 HAT ID translator, AXC translators for 12 HAT audio lines | major | Pin plan §3.11, §5.1 | Lines 93, 94, 95 (stock in BOM) |
| F13 | 77, 78 | MaskROM entry (ADR 0009: Power + Vol− at power-on) has no circuit; Vol− sits on a shared ladder; BAT54C (common cathode) cannot isolate two separate nodes | major | ADR 0009; pin plan §3.10 (eMMC_D0 to GND forces MaskROM, Radxa CM3 note) | Lines 97–98: TPS3839G18 window + SN74LVC1G27 NOR + BAT54 + DMG1012T to eMMC_D0; Vol− on its own SARADC_VIN1 node. Timing **UNVERIFIED** |
| F14 | 66 | HAT flat-cable connector open; the FH35C-61S candidate has 0 authorized stock | major | [FindChips FH35C-61S](https://www.findchips.com/search/FH35C-61S): Mouser 0, Heilind 0, only a broker | Hirose DF40 pair (§6). 5 Gb/s rating **UNVERIFIED** |
| F15 | 31 | 4.4 mm Pentaconn primary is quote-only (T1-029) | major | Sourcing report §1.1 | G-Switch GT-3321667P-01 primary (LCSC 730); Pentaconn as quoted upgrade |
| F16 | 76 | KMR221G is a short-travel switch; T1-022 asks the Action button for deeper travel | major | Draft marks travel **UNVERIFIED**; KMR2 travel ≈ 0.2 mm from memory, **UNVERIFIED** | Line set to *Open* pending samples |
| F17 | 69, 72 | ESD under-counted: HAT low-speed 4 × 6 = 24 channels for 52 lines; faceplate DSI 2 × 4 = 8 channels for 10 lines, faceplate low-speed unprotected | major | Pin plan §4.1 (31 faceplate signals), §4.2 (46 + 6 HAT lines); BRD-007 | HAT TPD6E05U06 ×9; DSI TPD4E05U06 ×3; faceplate low-speed TPD6E05U06 ×3 (line 75) |
| F18 | 75 | LSF0204 DNP escape for a 1.8 V faceplate bank is moot once the bank is 3.3 V | minor | F8 | Line removed; faceplates translate on their side |
| F19 | 54 | INA226 second source cannot run on a 1.8 V I2C bus (VIH = 0.7 × VS, VS ≥ 2.7 V) | minor | INA226 SBOS547C electrical characteristics (draft has the PDF; not re-opened, **UNVERIFIED**) | INA238 (1.2 V I2C, DKMS) |
| F20 | 77 | Second sources EVQ-P7 and SKRP do not share the PTS815 actuation and footprint | minor | Part families (**UNVERIFIED**) | Removed; actuation tied to the case design |
| F21 | 35, 80 | Privacy LED: a red LED (Vf ≈ 2 V) cannot light from the 1.8 V mic rail | minor | Everlight 0603 red typical Vf (**UNVERIFIED**) | LED anode from FP_3V3, FET gate still MIC_1V8 (BRD-027 kept) |
| F22 | 48 | BQ25895 default hot threshold is above the pack's 40 °C charge limit | minor | Adafruit 328 sheet §8.3 (charge 0–40 °C, ≤ 4.25 V) | TS divider and JEITA set for 40 °C (**UNVERIFIED** register mapping) |
| F23 | 42 | MAX17055 TH input has no thermistor (the board NTC is on the charger TS) | minor | Draft line 48 | Optional line 101 |
| F24 | 17 | Board EEPROM has no bus or address | minor | Pin plan §3.7 | I2C2 at 0x57 |
| F25 | 29 | TPS62840 2.2 V output must be one of its VSET codes | minor | SLVSEC6D VSET table (not re-opened, **UNVERIFIED**) | Note: 2.1 V if 2.2 V is not a code (TPS7A20 dropout is small at 8 mA) |
| F26 | 18 | Two DACs per unit against LCSC 346 / Digi-Key 471 | minor (risk) | LCSC C1554755: 346 (2026-10-22) | Risk listed |
| F27 | 36 | TPD1E10B06 capacitance is voltage-dependent on a ±4 V swing | minor | SLLSEB1G | Place inside the OPA1622 feedback node |
| F28 | 87, 88 | Debug pads are 1.8 V (UART2 on PMUIO2); CS43198 DSD uses dedicated DSDCLK/DSDA/DSDB pins, not BCLK | minor | Pin plan §2.3; DS1156F2 pin table (DSDA/SDIN2, DSDB/LRCK2, DSDCLK/SCLK2) | Pads renamed; pin plan §2.1 DSD rows need the same fix (not edited here) |
| F29 | ADR 0009 | "Follow the RK809-5 configuration of Quartz64 and Radxa, which use the same PMIC": both use the RK817 | minor (doc) | Draft §6 (Radxa ZERO 3W: RK817-5); pin plan sources | Not edited (outside scope). The RK809 reference is the Orange Pi 3B |
| F30 | pin plan | Stale or conflicting rows: MCLK enables labelled 45.1584/49.152 MHz; one OPA1622 EN GPIO vs two enables in the power tree; DSD on I2S SDO1/SDO2 | major (pin plan) | Pin plan §2.1 vs DS1156F2, power tree §5 | Not edited (outside scope); flagged for pinout v1 |
| F31 | BRD-030 | No hardware for item tracking while the T1 is off | minor (should) | BRD-030 | *Open* line 103 |
| F32 | 45 | OV1 ≈ 14.5 V sits above the BQ25895 14 V operating maximum | minor | Power tree §4.7 | OV1 ≈ 13.7 V (the BQ25895 internal OVP still protects) |
| F33 | 63 | TPD8S300A thin at LCSC (60) | minor | LCSC C2649824: 60 | Mouser 2,800; risk kept |
| F34 | 39 | BQ25895 D+/D− detection can disturb USB 2 enumeration on a shared port | minor | Common BQ2589x integration issue (**UNVERIFIED** for this layout) | AUTO_DPDM off; TCPM owns the input current |
| F35 | runtime | Adafruit 328 runtime 7.8–11.4 h (power tree) and 5.7 h pessimistic (T1 analysis) | major (risk, T1-039) | Power tree §4.9; battery-life analysis §0 | No BOM fix; SoC measurement gate stays decisive |

---

## 3. Compatibility matrix checked

### 3.1 IO voltage per connection

| SoC bank (V) | Device | Device IO range | Result |
|---|---|---|---|
| VCCIO6 (1.8) | CS43198 SCLK1/LRCK1/SDIN1/DSD, RESET, INT | VL 1.66–1.94 V; VIH 0.7 × VL | OK |
| PMUIO2 (1.8) | CS43198 SDA/SCL | VL domain | OK only because PMUIO2 is 1.8 V (F7) |
| PMUIO2 (1.8) | RK809, RK860-0, BQ25895, MAX17055, FUSB302B, INA236, TCA6416A (VCCI), LSM6DSV16X, AT24C02D | RK8xx: 1.8 V on Radxa ZERO 3; INA236 1.2 V-compliant; others **UNVERIFIED** at 1.8 V | OK / check |
| VCCIO6 (1.8) | IM73D122 PDM | VDD 1.62–3.6 V on MIC_1V8 | OK |
| VCCIO4 (1.8) | IW612 SDIO 3.0 + UART | VIO 1.8 V | OK (SDR104 at 1.8 V) |
| VCCIO3 (1.8/3.3) | microSD | UHS-I switch | OK |
| VCCIO2 (1.8) | eMMC VCCQ, OPA1622 EN (on ≥ 0.82 V), MAX98357A SD_MODE (> 1.4 V = left) | — | OK; OPA1622 EN reference pin **UNVERIFIED** |
| VCCIO5 (3.3) | GT911 (VDD 2.8–3.3 V on FP_3V3), VEML6030 (2.5–3.6 V), MAX98357A I2S3 | — | OK |
| VCCIO5 (3.3) | ILI9488 panel RST/TE (IOVCC 1.65–3.3 V) | IOVCC on FP_1V8 | Translator on the faceplate (line 96) |
| VCCIO6 (1.8) ↔ HAT (3.3) | I2S2, I2S1 RX, DOUT | — | AXC translators (line 95) |
| VCCIO4 (1.8) ↔ HAT ID (3.3) | EEPROM | — | PCA9306 (line 94) |
| RP2354A IOVDD (1.8) | Taps on DAC nets | RP2350 IOVDD 1.8–3.3 V, `VOLTAGE_SELECT` | OK; unpowered-pad loading **UNVERIFIED** (pin plan risk 11) |

### 3.2 I2C address map (no conflict)

| Bus (V) | Addresses |
|---|---|
| I2C0 (1.8) | RK809 0x20, RK860-0 0x40 (**UNVERIFIED**) |
| I2C1 (1.8) | FUSB302B 0x22, MAX17055 0x36, INA236 0x40–0x43, BQ25895 0x6A |
| I2C2 (1.8) | TCA6416A 0x21, CS43198 0x30 and 0x31 (DS1156F2 Table 4-12: ADR 0 Ω and 4.99 kΩ to GND set the last two bits 00 and 01; the 0x30 base is from the mainline cs43130 binding, **UNVERIFIED** in the datasheet text), AT24C02D 0x57, LSM6DSV16X 0x6A, RP2354A (to be assigned) |
| I2C3 (3.3) | VEML6030 0x10, GT911 0x5D (or 0x14), HID controller (to be assigned) |
| I2C4 (1.8 → 3.3) | HAT EEPROM 0x50 |
| I2C5 (3.3) | HAT devices + camera CCI (HAT designer) |

### 3.3 Interfaces and protocols

| Link | Check | Result |
|---|---|---|
| SDIO 3.0 | RK3566 SDMMC1 at 1.8 V ↔ IW612 | OK |
| MIPI DSI | RK3566 DSI0 4-lane ↔ E35GH 1-lane (ILI9488) | OK; 4 lanes routed for other faceplates |
| I2S | CS43198 ASP master (BCLK/LRCK), SoC I2S1 consumer (`SND_SOC_DAIFMT_BC_FC`), both DACs on one MCLK net | OK |
| PDM | RK3566 PDM M1 two clocks ↔ IM73D122 | OK |
| USB 2 | OTG0 to USB-C; USB2 HOST2 to RP2354A | OK |
| USB 3 / PCIe Gen 2 / CSI-2 | HAT only (BRD-044/045), AC caps 100 nF on TX | OK; DF40 at 5 Gb/s **UNVERIFIED** |
| USB-PD | FUSB302B + TCPM; sink 9 V/2 A; source 5 V Default on battery | OK |

### 3.4 Rails against regulator and source ratings

| Rail | Regulator rating | Load (max) | Result |
|---|---|---|---|
| Battery path | JST PH 2 A per contact; pack ≤ 2C | Draft: 3.5 A VSYS + 3.0 A OTG | **Fail → 2.0 A budget (F4)** |
| HAT_5V + USB-C out | TPS61088 from VSYS | ≤ 1.5 + 1.5 A ILIM (hardware), ≈ 0.7 A on battery (software) | OK after fix |
| vcc3v3_sys | TLV62569 2 A | ≈ 1.3 A peak (est.) | OK |
| HPA ±5 V | TPS7A4901 150 mA / TPS7A3001 200 mA | 122 mA worst sine | OK |
| AUDIO_2V2 | TPS62840 750 mA | 31 mA | OK |
| DAC VA, MCLK | TPS7A2018 300 mA | 7.8 / 15 mA | OK |
| BL_LEDA | TPS61169 1.2 A switch | 0.45 A peak inductor | OK |
| Charge | BQ25895 5 A; pack ≤ 1C (2.5 A) | 1.2 A | OK |
| Load switches | TPS22919 1.5 A, VIN ≤ 5.5 V | DAC_VP on VSYS ≤ 4.4 V (≤ 4.6 V LiHV) | OK |

### 3.5 Clocks, connectors, ESD, thermal

| Item | Check | Result |
|---|---|---|
| CS43198 MCLK | 22.5792 / 24.576 MHz only, VL 1.8 V CMOS, phase-noise mask Fig. 4-11 | Part missing (§4) |
| SoC 24 MHz, RTC 32.768 kHz | Load capacitance vs RK3566/RK809 guide | **UNVERIFIED** (guides not retrieved) |
| Faceplate FPC | FH35C-51S (51) on board; FH12-20S / FH12-6S on the faceplate flex for the TFT/CTP tails | OK; 14 % spare |
| HAT flat cable | DF40C-100DP (board) ↔ DF40C-100DS (FPC); DF40C-30DP ↔ DF40C-30DS (power) | OK as pairs; ratings **UNVERIFIED** |
| Battery | S2B-PH-SM4-TB ↔ Adafruit JST PH 2-pin | OK; polarity check per lot |
| Pogo | P70 1.27 mm on the device-side piece vs 4 × 32 at 1.27 mm proposal | OK |
| High-speed ESD | 0.5 pF → 12 % of a 200 ps UI | OK; one ESD per line, at the pogo field only |
| Thermal | OPA1622 +24 °C at worst case; RK3566 + RK809 + RK860 + charger in a sealed body | Not modelled (risk) |

---

## 4. Audio chain integrity

### 4.1 Master clock

The CS43198 takes MCLK directly at 22.5792 or 24.576 MHz only (DS1156F2 Table 4-3), on XTI/MCLK in the VL domain (VL 1.66–1.94 V), and its datasheet performance is characterised with a **crystal** on XTI/XTO (PDN_XTAL = 0, fXTAL = 22.5792 MHz; supported crystals in Table 5-1: NDK NX2016SA, TXC 8Y, River FCX-06).

| Candidate | 1.8 V | Audio-grade evidence | Stock (2026-10-22) | Verdict |
|---|---|---|---|---|
| NDK NSC5083A (NZ2520SDA, 1.8 V) | yes | −158 dBc/Hz at 1 kHz at 1.8 V (NDK catalog, via the draft) | none at any authorized distributor | **Target, not stocked** |
| NDK NSC5083D (3.3 V) | no | −164 dBc/Hz at 1 kHz | Digi-Key 2,239 / 3,083 | Rejected by ADR 0009 (translator) |
| TI CDC6CE024576ADLXR (BAW, 1.8–3.3 V) | yes | SNAS843D: −86 dBc/Hz at 1 kHz for 100 MHz (≈ −98 dBc/Hz scaled to 24.576 MHz); 400 fs only from 12 kHz up | Digi-Key 2,998; no 22.5792 MHz | **Rejected:** ≈ 60 dB worse close-in than the NDK |
| Epson SG-210STF (quartz, 1.6–3.6 V) | yes | no phase-noise data read | 24.576 MHz ML0: Digi-Key 7,053; **22.5792 MHz: Obsolete** at Digi-Key | Half a pair only |
| Kyocera KC2520Z / KC2016Z | yes | none read | 22.5792 MHz: 0 at Mouser/TME | Rejected on stock |
| SCTF SX2M22.5792M20F30TNN (1.62–3.63 V) | yes | no phase-noise spec | LCSC C5452663: 1,374 | Bring-up only, after measurement |
| SiTime SiT8008 / Microchip DSC1001 (MEMS) | yes | MEMS close-in noise (sourcing report) | LCSC 0 | Rejected |
| Crystal on each CS43198 XTI/XTO | yes | Cirrus's own characterisation condition | crystals plentiful | One crystal per DAC gives one rate family only: fails BRD-023 |

**Options for the maintainers (one must be chosen; none is compliant today):**

1. **Recommended for T1-040:** keep the NZ2520SDA land and order NSC5083A as a non-stock catalog spec number through NDK's franchised channel. This needs an explicit exception to T1-029 ("real availability") for one part; it is a catalog part, not a custom one (T1-038), but lead time and MOQ are **UNVERIFIED**.
2. Populate a stocked 1.62–3.63 V quartz XO on the same land (SCTF SX2M for 22.5792 MHz; Epson SG-210STF for 24.576 MHz) **only after** a phase-noise measurement against DS1156F2 Fig. 4-11 and an A/B listening/measurement test against the NSC5083D at 3.3 V on a bench translator. Risk: no manufacturer phase-noise data.
3. Amend ADR 0009 to allow the stocked 3.3 V NSC5083D through a passive or active level shift, with a measured jitter penalty. Rejected by the current ADR.

### 4.2 Supplies, protection, grounds

- **DAC VA:** TPS7A2018 7 µVrms through 75 dB VA PSRR → 1.2 nV at the output, 54 dB under the 0.63 µVrms floor (power tree §4.3). OK. The TPS62840 pre-buck in power-save mode may burst in the audio band; the TPS7A20 PSRR (95 dB at 1 kHz) and VA PSRR leave it far below the floor. Keep a forced-PWM strap option.
- **±5 V into OPA1622:** TPS7A4901 15.4 µVrms and TPS7A3001 15.1 µVrms; the difference amplifier and OPA1622 PSRR reject rail noise. TPS65131 power-save is acceptable by the PSRR chain (power tree §4.2) but needs measurement. LDO headroom could drop from 1.0 V to 0.5 V to save ≈ 10 mW per rail.
- **Output protection and pop:** OPA1622 current limit +145/−130 mA bounds shorts; EN low during rail ramps and CS43198 Popguard are the pop strategy. DNP mute-shunt footprints added (line 100) as insurance. Headphone ESD placed inside the feedback node.
- **Ground strategy (notes for the schematic):** one solid ground plane, with the audio section (DACs, OPA1622, LDOs) in its own region and no digital return currents routed through it. The CS43198 GNDA/GNDCP/GNDD are tied at the DAC per DS1156F2 Fig. 2-1. The TPS65131 power loop and the TPS61088 sit away from the analog region. Jack sleeves return to the audio region, with the 4.4 mm ground and the 3.5 mm sleeve as star returns to the OPA1622 reference point. MCLK runs as a short, guarded, single-net trace from the oscillators to both XTI pins. The RP2354A taps go through series resistors placed at the tap point.

---

## 5. Faceplate connector pin budget (FH35C-51S)

| Group | Signals | Contacts |
|---|---|---|
| MIPI DSI0 (or LVDS0) | CLK±, D0±–D3± | 10 |
| I2C3 | SCL, SDA | 2 |
| SPI/DBI | SCLK, MOSI, MISO, CS, D/C | 5 |
| Touch | INT, RST | 2 |
| Panel | RST, TE | 2 |
| Interrupts | HID_INT, ALS_INT | 2 |
| Status LED | PWM | 1 |
| Main microphone | PDM_CLK, PDM_DATA | 2 |
| Detect + spares | FP_DET#, GPIO ×2 | 3 |
| **Signals** | | **29** |
| Power | FP_3V3 ×2, FP_1V8, FP_VCI, MIC_1V8, BL_LEDA, BL_LEDK | 7 |
| Ground | between DSI pairs, group edges, returns | 8 |
| **Used** | | **44** |
| **Spare** | | **7 (14 %)** |

BL_PWM and BL_EN leave the connector because the TPS61169 stays on the board. The LEDA/LEDK string voltage (≤ 16.5 V) and the FH35C contact current and voltage ratings are **UNVERIFIED**.

---

## 6. HAT flat-cable connector pick

| Criterion | Hirose DF40 (pick) | Hirose FH35C-61S | Micro-coax (I-PEX class) |
|---|---|---|---|
| Authorized stock | DF40C-100DS: [Digi-Key 169,419](https://www.digikey.com/en/products/result?keywords=DF40C-100DS-0.4V(51)); DF40C-100DP: [Mouser 10,937, Arrow 906](https://www.findchips.com/search/DF40C-100DP-0.4V(51)); DF40C-30DP: [Mouser 41,535](https://www.findchips.com/search/DF40C-30DP-0.4V(51)); DF40C-30DS: [Future 5,000](https://www.findchips.com/search/DF40C-30DS-0.4V(51)) | 0 at Mouser and Heilind | assemblies made to order |
| Pin count | 100 + 30 | 61 (two needed, no power room) | 30–50 |
| High-speed | 5 Gb/s rating **UNVERIFIED** (Hirose site HTTP 403) | **UNVERIFIED** | rated, but custom |
| T1-038 | catalog parts; the FPC is fabricated like the PCB | catalog | rejected |

Allocation: 100-pin = 12 pairs in GSSG (24 + 13 grounds = 37), 46 low-speed, 6 analog, 8 low-speed grounds = 97, 3 spare. 30-pin = HAT_5V ×8, HAT_3V3 ×4, GND ×12, 6 spare (contact current **UNVERIFIED**; at ≈ 0.3 A per contact, 8 contacts carry 2.4 A). **A 5 Gb/s test coupon (FPC + DF40 + pogo) is required before the design freezes.**

---

## 7. Requirements coverage

| Requirement | BOM line(s) | Status |
|---|---|---|
| IMU (BRD-032) | 59 | Covered |
| ALS on the faceplate (FPT-014) | 60 | Covered (3.3 V corrected) |
| Two microphones (BRD-031, FPT-017) | 34 | Covered |
| SD/TF (BRD-038) | 11, 73 | Covered |
| Certified Wi-Fi/BT (BRD-025/029) | 55–58 | Covered |
| Item tracking (BRD-030) | 103 | **Open** |
| Status LED, developer-controllable (FPT-016) | 79 | Covered (PWM9) |
| Buttons, Action deeper travel (T1-022, BRD-036) | 76, 77 | Action **Open** |
| Power gating per block (BRD-008) | 50, 91, power tree §5 | Covered (FP_3V3 added) |
| Current sensing (T1-026) | 54 | Covered |
| UART pads (BRD-047) | 87 | Covered (1.8 V) |
| I2S/DSD test pads (BRD-040) | 88 | Covered (DSD pins corrected) |
| MaskROM combo (BRD-035, ADR 0009) | 78, 97, 98, 35 | Covered, timing **UNVERIFIED** |
| Battery NTC (ADR 0007) | 48, 101 | Covered |
| LiHV-ready charger (ADR 0008) | 39, 42 | Covered (VREG to 4.608 V) |
| eFuses on HAT rails (BRD-026) | 44 | Covered |
| HAT power both directions (HCS-015) | 44, 45, 91 | Covered after F5/F6 |
| USB-C OTG + PD (BRD-018/034) | 41, 61–64 | Covered |
| Speaker independent of DAC (BRD-012) | 32 | Covered |
| 3.5 + 4.4 mm outputs (BRD-011) | 30, 31 | Covered |
| No custom parts (T1-038) | 46, 66, 102 | Covered; FPC interpretation open |
| Autonomy thresholds (T1-039) | 46 | 7.8–11.4 h estimate; measurement gate |

---

## 8. Corrected decisions

1. **MCLK:** blocker; the maintainers choose an option from §4.1. The design keeps the 2520 land, the ST tri-state sharing and the MCLK_1V8 rail.
2. **Battery:** Adafruit 328, JST PH 2-pin, board NTC, 2.0 A battery budget.
3. **HAT and USB-C source power:** TPS61088 boost from VSYS → TPS25947 eFuses; BQ25895 OTG unused; TPS2121 OV1/OV2 hardware interlock.
4. **IO domains:** PMUIO2 1.8 V (I2C0/1/2), VCCIO5 3.3 V (faceplate), VCCIO6 1.8 V (audio).
5. **vdd_cpu:** RK860-0.
6. **Faceplate connector:** Hirose FH35C-51S, 44 used, 7 spare.
7. **HAT flat cable:** Hirose DF40 100-pin + 30-pin pairs on an impedance-controlled FPC (ADR 0009 item closed, pending the 5 Gb/s coupon).
8. **MaskROM:** Power + Vol− within a 200 ms window after VCCIO2 rises pulls eMMC_D0 low (TPS3839G18 + SN74LVC1G27 + BAT54 + DMG1012T).
9. **4.4 mm jack:** stocked G-Switch primary.
10. **ESD:** one part per line at the user-touchable boundary, counts corrected.

---

## 9. Not covered, and how

- **No primary datasheet re-read** for FUSB302B, MAX17055, BQ25895 I2C thresholds, RK860-0, TPS61088, DF40, FH35C, the KMR2 travel, the Type 2EL VBAT range or the RK809 PWRON idle voltage. Each is marked **UNVERIFIED** in the BOM. They are covered by the schematic-review checklist, not by this report.
- **Mouser stock** comes only through FindChips; Digi-Key was checked for the MCLK, SG-210STF, CDC6C and DF40 rows only.
- **No simulation:** TPS65131 low-battery current, TPS61088 compensation and the MaskROM timing need bench or SPICE work.
- **Files not edited** (outside the brief): pin multiplexing v0 (F28, F30), ADR 0009 (F29), the BOM v1 draft (kept as history).

## 10. Sources

- Cirrus Logic CS43198 DS1156F2: <https://www.cirrus.com/docs/ds/cs43198-datasheet.pdf>
- TI CDC6C SNAS843D: <https://www.ti.com/lit/ds/symlink/cdc6c.pdf>
- Adafruit 328 cell specification: <https://cdn-shop.adafruit.com/datasheets/785060-2500mAh_specification_sheet.pdf>
- Digi-Key searches (2026-10-22): [NZ2520SDA](https://www.digikey.com/en/products/result?keywords=NZ2520SDA), [SG-210STF 22.5792](https://www.digikey.com/en/products/result?keywords=SG-210STF%2022.5792), [SG-210STF 24.576](https://www.digikey.com/en/products/result?keywords=SG-210STF%2024.576), [CDC6C 24.576 MHz 1.8 V](https://www.digikey.com/en/products/result?keywords=24.576MHz%20XO%201.8V%20CMOS%20low%20jitter), [DF40C-100DS](https://www.digikey.com/en/products/result?keywords=DF40C-100DS-0.4V(51)), [DF40C-100DP](https://www.digikey.com/en/products/result?keywords=DF40C-100DP-0.4V(51))
- FindChips (2026-10-22): [NSC5083A-22.5792M](https://www.findchips.com/search/NSC5083A-22.5792M), [NSC5083A-24.576M](https://www.findchips.com/search/NSC5083A-24.576M), [KC2520Z22.5792](https://www.findchips.com/search/KC2520Z22.5792), [SG-210STF 22.5792](https://www.findchips.com/search/SG-210STF%2022.5792), [FH35C-61S](https://www.findchips.com/search/FH35C-61S), [FH35C-51S](https://www.findchips.com/search/FH35C-51S), [DF40C-100DS](https://www.findchips.com/search/DF40C-100DS-0.4V(51)), [DF40C-100DP](https://www.findchips.com/search/DF40C-100DP-0.4V(51)), [DF40C-30DS](https://www.findchips.com/search/DF40C-30DS-0.4V(51)), [DF40C-30DP](https://www.findchips.com/search/DF40C-30DP-0.4V(51))
- LCSC via the JLCPCB parts API (2026-10-22): RK860-0 C19188628, RK860-2 C5156489, TCA6416ARTWR C182336, PCA9306DCUR C33196, TCA9406DCUR C840107, SN74AXC8T245PWR C882718, SN74AXC4T774PWR C1849453, SN74AXC2T45DCUR C1858360, SN74AXC1T45DCKR C2677392, SN74LVC1G27DCKR C2871289, TPS3839G18DBZR C544505, TPS61088RHLR C87357, XAL4020-152MEC C18547833, BAT54,215 C85084, NZ2520SDA C2847209 / C2846938, SX2M22.5792M20F30TNN C5452663, CS43198-CNZR C1554755, TPD8S300ARUKR C2649824, INA236AIDDFR C5443912, RV-3028-C7 C2829066
