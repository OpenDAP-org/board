# Power tree v0

- **Status:** Draft. Desk design only: nothing here has been built, simulated or measured. Every part is *Proposed* unless [BOM v1](bom-v1.md) says *Decided*. Updated 2026-10-22 by the [BOM v1 cross-validation](../research/2026-10-bom-v1-cross-validation.md) (battery, HAT/USB 5 V source, TPS2121 isolation, faceplate rails, IO voltages, vdd_cpu part), then by BOM v1.1 (RK809-5 feeds and ratings, TPS61089 boost, 3.1 V MCLK supply, RP2354A supplies, battery derating, TPS2121 OV1, HP-amp soft-start), then by BOM v1.2 (power margin check of every rail, converter, connector and cable, BRD-049, §4.10; vcc3v3_sys on a 3 A TPS62826; battery path sized for the full output budget, BRD-050 and proposed ADR 0011; battery fuse; 50-contact HAT power connector; RGB status LED driver; TPS61089 and TPS2121 current limits), then by BOM v1.3 ([ADR 0012](../adr/0012-headphone-output-stage.md): six OPA1622 with paralleled halves, ±6 V amplifier rails on LT3045/LT3094 from ±7 V TPS65131 pre-rails, gain 1.62 with the CS43198 at `+1dB_EN` = 0, §4.1, §4.2, §4.10.1; interim-pack output ceiling, §4.11; vcc3v3_sys inductor, §4.10), then by BOM v1.4 (HAT pogo power contacts fixed by the hat-standard HAT interface v1, §4.10; no power part changes).
- **Date:** 2026-10-22
- **Companion:** [BOM v1](bom-v1.md) (parts, stock, datasheet links and hashes).
- **Inputs:** [BOM v0](bom-v0.md), [headphone output power research](../research/2026-10-headphone-output-power.md), [board requirements](../requirements/README.md) (BRD-001 to BRD-050), board ADRs 0001–0012, [component selection](../research/2026-10-component-selection.md), [sourcing alternatives](../research/2026-10-sourcing-alternatives.md), [high-speed I/O topology](../research/2026-10-high-speed-io-topology.md), [battery selection](../research/2026-10-battery-selection.md), touch-faceplate ADR 0001 (Focus E35GH), T1 and HAT Case Standard requirements, opendap-os ADRs 0006–0008. [pin multiplexing v0](../research/2026-10-pin-multiplexing-v0.md) gives the balls; GPIO names below are logical names.
- **Method:** datasheets were downloaded and read (revision and sha256 in the BOM's Datasheets table); the RK809 rail mapping follows the Radxa ROCK 3C v1.4 schematic (PMIC marked RK809-5) and the mainline device trees of RK3566 + RK809 boards (Orange Pi 3B, ROCK 3C, ODROID-M1S), with Anbernic RG353 (RK817) and the Radxa ZERO 3W schematic v1.12 for the rest. Calculations are shown inline.
- **Conventions:** **UNVERIFIED** = no primary source found in this session. "Est." = engineering estimate, to be replaced by measurement (T1-026).

## 1. Findings that change earlier drafts

1. **The CS43198 does not accept a 45.1584 or 49.152 MHz master clock.** Its datasheet (DS1156F2, §4.6 and Table 3-13) allows an external MCLK only at the nominal internal frequencies **22.5792 MHz and 24.576 MHz** (or PLL references 9.6–26 MHz). BRD-023 (Draft) and BOM v0 lines 9–10 name 45.1584/49.152 MHz. Proposal: **22.5792 MHz and 24.576 MHz NDK NZ2520SDA**, which keeps the intent of BRD-023 (two families, DAC as clock master, no resampling). A divide-by-two flip-flop would also work but adds a part and jitter in the clock path, against BRD-042.
2. **The CS43198 also needs a battery-class supply, VP = 3.0–5.25 V** (charge-pump supply for its output stage), plus four 1.8 V rails (VA, VCP, VD, VL). VP must come up first and go down last (DS1156F2 §5.2).
3. **The MCLK input is in the 1.8 V VL domain.** No stocked audio-grade 1.8 V oscillator exists at 22.5792 MHz (the 1.8 V NSC5083A has no authorized stock), so the stocked 3.3 V NSC5083D runs on its own MCLK_3V3 LDO and reaches XTI through a passive attenuator (ADR 0010).
4. **The LM27762 cannot make ±5 V from a 1S battery.** Its positive output is an LDO from VIN, so at VSYS = 3.5 V the positive rail is at most about 3.45 V (calculation in §4.2). The proposed generator is a **TPS65131** dual boost/inverter followed by **TPS7A4901 / TPS7A3001** LDOs (v1.3: **LT3045 / LT3094**, ADR 0012).
5. **The TPS7A94 is unsuitable for a battery device here:** 15 mA typical ground current at 5.1 V out (SBVS336C, Electrical Characteristics), that is about 80 mW wasted.
6. **The RK809-5 must be used with the reference rail mapping.** Its regulators come up at OTP default voltages before Linux runs. The mapping below copies the Radxa ROCK 3C v1.4 schematic (RK809-5) and the mainline device trees of the ROCK 3C, Orange Pi 3B and ODROID-M1S, which agree: every VCC pin of the reference boards is on a free-running vcc3v3_sys (the ROCK 3C leaves the EXT_EN option on its 3.3 V buck unfitted). The T1 keeps VCC5–VCC9 on vcc3v3_sys, now always-on, and feeds VCC1–VCC4 (BUCK1–4) from VSYS as in the datasheet application circuit (Fig. 1-1). Supply-pin mapping (RK809 datasheet §2.5): VCC1–VCC4 → BUCK1–4, VCC5 → LDO1–3, VCC6 → LDO4–6, VCC7 → LDO7–9, VCC9 → BUCK5 and SWOUT1, VCC8 → SWOUT2. The RK809-5 OTP defaults are not public (**UNVERIFIED**).
7. **LPDDR4X needs a separate 0.6 V VDDQ rail.** The Radxa ZERO 3W schematic table gives VDDQ 1.10 V and VDDQL 0.60 V for LPDDR4X, with a 0 Ω option (R122) that ties VCC0V6_DDR to VCC_DDR only for plain LPDDR4.
8. **The battery path is limited to 1.6 A continuous with the interim pack** (v1.1 derating). The pack is the Adafruit 328 (ADR 0007): its sheet allows ≤ 2C discharge, but JST rates the PH contact 2 A with AWG #24 wire only, and the pack leads are 26 AWG. VSYS on battery is budgeted at 1.6 A (≈ 5.6 W at 3.5 V), and from v1.2 a 2.5 A board fuse bounds it (§4.7). The board itself is sized for the full output budget, 4.8 A from the battery (BRD-050, proposed ADR 0011); no stocked pack that carries it has been found yet.
9. **The BQ25895 cannot supply OTG while it charges.** The draft fed HAT_5V and the USB-C source from the OTG boost, so a class A/B HAT lost 5 V whenever USB-C power was plugged in. HAT_5V and USB-C VBUS out now come from a **TPS61089 boost from VSYS** (5.1 V) behind eFuses #A and #C (v1.1: the TPS61088 has no ti.com product page or datasheet any more).
10. **The T1's own 5 V must not re-enter the charger.** When the T1 sources USB-C VBUS, that VBUS is also TPS2121 IN1; when it sources HAT_5V, that net is IN2. Both OV inputs are forced high by hardware OR of the source enables (`USB_SRC_ON`, `HAT_SRC_ON`), not by software order.
11. **IO voltages follow the pin plan:** I2C0/1/2 on PMUIO2 at 1.8 V (the CS43198 control port shares the bank and is 1.8 V-only); the faceplate bank VCCIO5 at 3.3 V.
12. **MCLK at 3.1 V** (ADR 0010, supply part amended in BOM v1.1): MCLK_3V1 from VSYS through a TPS7A2031. On battery VSYS follows VBAT below VSYSMIN, so a 3.3 V LDO had 0.2 V or less of headroom; 3.1 V stays inside the NSC5083D 2.97–3.63 V supply range with ≥ 0.3 V headroom down to 3.4 V. The oscillator current below is the NZ2520SDA figure.
13. **Debian already enables the INA236 current monitor** through the IIO `ina2xx-adc` driver (`CONFIG_INA2XX_ADC=m`, compatible `ti,ina236`), while the hwmon INA2xx/INA238 drivers are off. The instrumentation uses INA236.

## 2. Power tree (text diagram)

Currents are design maxima (max) and estimated screen-off playback values (play). Arrows point from source to load.

```text
USB-C VBUS 5-12 V (PD sink, FUSB302B) --[TVS2200]--+
                                                   +--> TPS2121 IN1 (priority) --+
HAT_5V pins (powerbank HAT, class F) --[TVS0500]---+--> TPS2121 IN2 (OV2 gate) --+--> VBUS_CHG (ILM 2.0-3.0 A)
                                                                                  |
VBUS_CHG --> BQ25895 (buck charger 1.5 MHz; OTG boost NOT used)                   |
   |   TPS2121 OV1 forced by USB_SRC_ON, OV2 forced by HAT_SRC_ON (hardware OR)    |
   |                                                                              |
   +--> BAT --[fuse 2.5 A interim / 7 A full budget]--> battery connector <--> Adafruit 328 (interim), 1S 2,500 mAh, JST PH 2-pin, 26 AWG (1.6 A budget)
   |            MAX17055 gauge, 10 mohm sense, board NTC on TS
   +--> VSYS 3.0-4.4 V (VSYSMIN 3.5 V on adapter; = VBAT on battery)   on battery max 1.6 A interim, 4.8 A full budget (BATFET 6 A); on adapter ISYS <= 3.9 A; play 0.20-0.30 A (est.)
          |
          +--> TPS62826 vcc3v3_sys 3.3 V 3 A, ALWAYS ON (EN = VSYS; EXT_EN unused)   play ~0.15 A, peak 1.85 A (est.)
          |         +--> RK809 VCC5-VCC9 (LDO1-9, BUCK5, SWOUT1, SWOUT2)
          |         +--> eMMC VCC, TPS22919 RP_3V3 (RP2354A), TCA6416A VCCP, PCA9306 / AXC B side
          |         +--> TPS22919 FP_3V3 (CTP VDD, ALS, faceplate logic, privacy LED) ~80 mA
          +--> RK809-5 PMIC (VCC1-VCC4 = BUCK1-4 from VSYS; VCC5-VCC9 from vcc3v3_sys)
          |      BUCK1 vdd_logic   0.90 V  2.5 A max   play ~0.30 A (est.)          [VCC1, VSYS]
          |      BUCK2 vdd_gpu     0.90 V  2.5 A max   off with GPU idle (DT)       [VCC2, VSYS]
          |      BUCK3 vcc_ddr     1.10 V  1.5 A max   play ~0.10 A (est.)          [VCC3, VSYS]
          |         +--> TPS7A1006 vcc0v6_ddr 0.60 V 0.3 A max (LPDDR4X VDDQ), play ~0.03 A
          |      BUCK4 vdd_npu     0.90 V  1.5 A max   OFF unless NPU used          [VCC4, VSYS]
          |      BUCK5 vcc_1v8     1.80 V  2.5 A max   play ~0.10 A (est.)          [VCC9, vcc3v3_sys]
          |         +--> TPS22919 DAC_DIG_1V8  (2x VD+VL+VCP)       13 mA
          |         +--> TPS22919 FP_1V8 (panel IOVCC, faceplate translator low side) ~5 mA
          |         +--> TPS22919 MIC_1V8 (2x IM73D122 + privacy LED gate) ~2 mA
          |         +--> TPS22919 RP_IOVDD_1V8 (RP2354A IOVDD, 12 MHz XO)
          |         +--> IMU, eMMC VCCQ, IW612 VIO, LPDDR4X VDD1, SoC VCCIO 1.8 V banks
          |      LDO1 vdda0v9_image 0.9 V 400 mA (CSI D-PHY, camera HAT only)  [VCC5]
          |      LDO2 vdda_0v9      0.9 V 400 mA (USB/PCIe/DSI PHY)            [VCC5]
          |      LDO3 vdda0v9_pmu   0.9 V 100 mA (always on)                   [VCC5]
          |      LDO4 FP_VCI        2.8 V 100 mA design (panel VCI; adjustable per faceplate in DT) [VCC6]
          |      LDO5 vccio_sd      1.8/3.3 V 400 mA (microSD signalling)      [VCC6]
          |      LDO6 vcc3v3_pmu    3.3 V 400 mA (always on: PMUIO1, FUSB302B; ~3.3 V less dropout from a 3.3 V feed, as on the reference) [VCC6]
          |      LDO7 vcca_1v8      1.8 V 400 mA (PLL, PHY analog)             [VCC7]
          |      LDO8 vcca1v8_pmu   1.8 V 400 mA (always on)                   [VCC7]
          |      LDO9 vcca1v8_image 1.8 V 400 mA (CSI D-PHY, camera HAT only)  [VCC7]
          |      SWOUT1 vcc3v3_wl  (IW612 VBAT)   1.5 A switch [VCC9]  max 0.6 A (est.), off when radio off
          |      SWOUT2 vcc3v3_sd  (microSD VDD)  3 A switch   [VCC8]  max 0.2 A
          |      RTC + 32.768 kHz crystal
          +--> RK860-0 vdd_cpu 0.80-1.15 V (I2C DVS)   max 3 A (est.), play ~0.15 A (est.)
          +--> TPS22919 DAC_VP (CS43198 VP x2)           0.1 mA play, VP first/last
          +--> TPS62840 AUDIO_2V2 2.2 V 750 mA max        play 16 mA
          |         +--> TPS7A2018 DAC1_VA 1.8 V    7.8 mA
          |         +--> TPS7A2018 DAC2_VA 1.8 V    7.8 mA
          +--> TPS7A2031 MCLK_3V1 3.1 V  15 mA (one NSC5083D active, other in standby; ADR 0010, part amended in v1.1)
          +--> TPS65131 AUDIO_P7V0 +7.0 V / AUDIO_N7V0 -7.0 V (v1.3)
          |         +--> LT3045 HPA_P6V0 +6.0 V  500 mA rating, 275 mA worst continuous, idle 12.7 mA (SE) / 23.1 mA (bal)
          |         +--> LT3094 HPA_N6V0 -6.0 V  500 mA rating, 275 mA worst continuous, idle 12.9 mA (SE) / 23.3 mA (bal)
          |                  +--> 6x OPA1622, halves paralleled (selected output only: 2 packages SE, 4 balanced)
          +--> MAX98357A speaker amp (VDD = VSYS, SD_MODE shutdown)
          +--> TPS61169 backlight boost, LEDA up to 16.5 V, ILED 60 mA max (5S2P, 10 LEDs)
          +--> TLV62569 HAT_3V3 3.3 V 2 A --> TPS259470 #B (ILIM 1.0 A) --> HAT_3V3
          +--> LP5521 RGB status LED driver (VDD = VSYS, 1.5x charge pump ~4.5 V, 3 x <= 20 mA) --> faceplate RGB LED
          +--> TPS61089 boost 5.1 V, 1.6 A design, RILIM 182 kohm (EN = HAT5V_EN OR USB_SRC_ON)
          |         +--> TPS259470 #A (ILIM 1.5 A) --> HAT_5V out   (on battery: budgeted, §4.6)
          |         +--> TPS259470 #C (ILIM 1.5 A) --> USB-C VBUS source (0.5 A default on battery)
          +--> MAX17055 gauge (powered from BAT)
```

## 3. Rail table

| Rail | Source | Voltage | Max current (design) | Screen-off playback (est.) | Gated by | Loads |
|---|---|---|---|---|---|---|
| VBUS_CHG | TPS2121 OUT | 5–12 V | 2.0 A (IINLIM, and ≤ 15 W; v1.2); TPS2121 ILM 2.0–3.0 A hardware ceiling | 0 (battery) | TPS2121 priority, OV pins | BQ25895 VBUS |
| VSYS | BQ25895 SYS | 3.0–4.4 V (= VBAT less the path drop on battery) | 1.6 A on battery with the interim pack (§4.7); 4.8 A with an ADR 0011 pack (BATFET 6 A continuous); ISYS ≤ 3.9 A on adapter (v1.2) | 0.20–0.30 A | BATFET ship mode | everything below |
| vdd_cpu | RK860-0 | 0.80–1.15 V | 3 A (est.) | 0.15 A (est.) | RK860 EN + DVS | RK3566 CPU |
| vdd_logic | RK809 BUCK1 (VCC1 ← VSYS) | 0.90 V | 2.5 A | 0.30 A (est.) | off in suspend | RK3566 logic |
| vdd_gpu | RK809 BUCK2 (VCC2 ← VSYS) | 0.90 V | 2.5 A | ~0 (GPU idle) | DT regulator | GPU (and NPU if tied) |
| vcc_ddr | RK809 BUCK3 (VCC3 ← VSYS) | 1.10 V | 1.5 A | 0.10 A (est.) | on in suspend | LPDDR4X VDD2, SoC DDR VDDQ |
| vdd_npu | RK809 BUCK4 (VCC4 ← VSYS) | 0.90 V | 1.5 A | 0 | DT, off by default | NPU |
| vcc_1v8 | RK809 BUCK5 (VCC9 ← vcc3v3_sys) | 1.80 V | 2.5 A | 0.10 A (est.) | off in suspend | IO banks, eMMC VCCQ, VDD1, sub-switches |
| vcc0v6_ddr | TPS7A1006 (from vcc_ddr) | 0.60 V | 0.3 A | 0.03 A (est.) | follows vcc_ddr | LPDDR4X VDDQ, SoC VDDQL |
| vcc3v3_sys | TPS62826 (EN = VSYS; v1.2, was TLV62569) | 3.30 V | 3 A | 0.15 A (est.) | always on (EXT_EN unused, as on the ROCK 3C) | RK809 VCC5–VCC9 (LDO1–9, BUCK5, SWOUT1, SWOUT2), eMMC VCC, RP2354A, FP_3V3, expander and translators. Peak ≈ 1.85 A (est.: BUCK5 input 0.4, LDOs 0.25, SWOUT1 0.6, SWOUT2 0.2, eMMC 0.25, rest 0.15 A) = 62 % of 3 A; in regulation down to VSYS ≈ 3.39 V at that peak (100 % mode, BOM line 6). TPS62827 (4 A) is the drop-in |
| vcc3v3_wl | RK809 SWOUT1 (VCC9 ← vcc3v3_sys) | 3.30 V | 1.5 A switch (DC table) | 0 (radio off) | RK809 I2C | IW612 module VBAT (supply range **UNVERIFIED**) |
| vcc3v3_sd | RK809 SWOUT2 (VCC8 ← vcc3v3_sys) | 3.30 V | 3 A switch (DC table; the ROCK 3C labels both switches 2.1 A, so design to 1.5 A) | 0–0.1 A | RK809 I2C | microSD VDD |
| FP_VCI | RK809 LDO4 (VCC6 ← vcc3v3_sys) | 2.80 V (DT-adjustable; panel absolute maximum 3.3 V) | 100 mA design (400 mA in the DC table, 100 mA in Table 4-1) | 0 (screen off) | RK809 I2C | panel VCI |
| vcc3v3_pmu | RK809 LDO6 (VCC6) | 3.3 V less dropout | 400 mA | — | always on | PMUIO1, FUSB302B |
| vdda0v9_pmu, vcca1v8_pmu | RK809 LDO3 (VCC5), LDO8 (VCC7) | 0.9 V, 1.8 V | 100 mA, 400 mA | — | always on | SoC PMU domain, MaskROM gates |
| FP_3V3 | TPS22919 (vcc3v3_sys) | 3.30 V | 1.5 A switch | 0 (screen off) | `FP_IO_EN` | CTP VDD, ALS, faceplate logic, privacy LED (the status LED runs from the LP5521, v1.2) |
| FP_1V8 | TPS22919 (vcc_1v8) | 1.80 V | 1.5 A switch | 0 (screen off) | `FP_IO_EN` | panel IOVCC, faceplate translators |
| DAC_VP | TPS22919 (VSYS) | 3.5–4.4 V | 1.5 A switch | 0.06 mA | `DAC_VP_EN` | 2× CS43198 VP |
| DAC_DIG_1V8 | TPS22919 (vcc_1v8) | 1.80 V | 1.5 A switch | 13.2 mA | `DAC_DIG_EN` | 2× CS43198 VD, VL, VCP |
| AUDIO_2V2 | TPS62840 | 2.20 V | 0.75 A | 16 mA | `AUDIO_LN_EN` | two TPS7A2018 |
| DACx_VA | TPS7A2018 ×2 | 1.80 V | 0.3 A | 7.8 mA each | `AUDIO_LN_EN` | CS43198 VA |
| MCLK_3V1 | TPS7A2031 (from VSYS) | 3.10 V | 0.3 A | 15 mA | `AUDIO_LN_EN` | 2× NSC5083D (one in standby, ST pulled down), passive attenuator to XTI (ADR 0010) |
| RP_3V3 | TPS22919 (vcc3v3_sys) | 3.30 V | 1.5 A switch | RP2354A dependent | `RP_PWR_EN` | RP2354A VREG_VIN + VREG_AVDD, QSPI_IOVDD, USB_OTP_VDD, ADC_AVDD |
| RP_IOVDD_1V8 | TPS22919 (vcc_1v8) | 1.80 V | 1.5 A switch | RP2354A dependent | `RP_PWR_EN` | RP2354A IOVDD, 12 MHz XO (≤ 2.5 mA at 1.8 V) |
| AUDIO_P7V0 / N7V0 | TPS65131 (v1.3: ±7.0 V) | +7.0 / −7.0 V | 275 mA each worst continuous; inverter at 72–79 % of its minimum switch limit (§4.10.1) | 12.7–12.9 mA each (SE idle), 23 mA (balanced idle) | `HPA_RAIL_EN` (ENP, ENN) | LDOs below |
| HPA_P6V0 | LT3045 (v1.3, was TPS7A4901 at +5.0 V) | +6.04 V | 0.5 A (≈ 0.4 A programmed limit) | 10.4 mA (SE idle) / 20.8 mA (balanced idle) at the amplifiers | `HPA_LDO_EN` | OPA1622 V+ |
| HPA_N6V0 | LT3094 (v1.3, was TPS7A3001 at −5.0 V) | −6.04 V | 0.5 A (≈ 0.4 A programmed limit) | as HPA_P6V0 | `HPA_LDO_EN` | OPA1622 V− |
| BL_LEDA | TPS61169 | 13–16.5 V | 60 mA | 0 (screen off) | `BL_PWM` (CTRL, 1 µA off) | panel LED string |
| HAT_3V3 | TLV62569 → TPS259470 #B | 3.30 V | 1.0 A (ILIM) | 0 | `HAT3V3_EN` | HAT |
| HAT_5V (out) | TPS61089 → TPS259470 #A | 5.1 V | 1.5 A (ILIM, 1.66 A max); on battery per §4.6 budget | 0 | `HAT5V_EN` (also forces TPS2121 OV2) | HAT class A/B |
| LED_R/G/B | LP5521 current sources (VDD = VSYS) | ≤ 4.55 V (charge pump) | 25.5 mA per channel, 20 mA DT cap | 0 (LED off) | LP5521 CHIP_EN (I2C) | faceplate RGB status LED (v1.2) |
| USB-C VBUS (out) | TPS61089 → TPS259470 #C | 5.1 V | 1.5 A (ILIM); 0.5 A advertised on battery | 0 | TCPM source role → `USB_SRC_ON` (also forces OV1) | USB host mode |

## 4. Calculations

### 4.1 Headphone amplifier rails (OPA1622)

**v1.3: [ADR 0012](../adr/0012-headphone-output-stage.md)** (Accepted) replaces the v1.2 stage (four OPA1622 at ±5 V, gain 1, CS43198 at `+1dB_EN` = 1). Figures are from the [headphone output power research](../research/2026-10-headphone-output-power.md) (option A6) and are desk estimates until simulated and measured.

**Topology:**

- Six OPA1622. Every package runs both halves in parallel: one package per balanced leg (L+, L−, R+, R−) and one per single-ended channel.
- Each half is its own difference amplifier fed from the same CS43198 output pair: R1 = R3 = 1.00 kΩ, R2 = R4 = 1.62 kΩ, 100 pF across R2 and R4 (gain 1.62, pole at 982 kHz), feedback taken before a 1.0 Ω ballast resistor (BOM lines 37, 107, 108).
- CS43198 at `+1dB_EN` = 0: 1.73 Vrms full scale (4.66 Vpp minimum), −115 dB THD+N typ, −109 dB max (DS1156F2 Table 3-4).

**Limits (SBOS727B):** ≈ 100 mA peak per half at ±5 V (Table 2: 109 mA into 16 Ω, 97 mA into 32 Ω, both current-limited); swing headroom ≈ 1.9 V at ≈ 100 mA (derived from Table 2), 0.8–0.9 V at low current (§6.5). Swing against current at ±6 V is **UNVERIFIED** (Figure 38 is plotted at ±18 V).

**Expected output (est., research §4.5):**

| Output | 16 Ω | 32 Ω | 300 Ω | Limited by |
|---|---|---|---|---|
| 3.5 mm SE | ≈ 320 mW | **≈ 240 mW** (3.92 V peak, 122 mA) | 26 mW | current at 16 Ω, DAC level × gain at 32 and 300 Ω |
| 4.4 mm balanced | ≈ 320 mW | **≈ 640 mW** (490–760 mW with imperfect sharing) | 102 mW | current (175–218 mA per leg) at 16 and 32 Ω, gain at 300 Ω |

**Supply current per rail** (sine, both channels; a rail supplies one half-cycle of each leg's current, average Ipk/π per leg):

- Quiescent: 2.6 mA per enabled half (3.3 mA max; 5 µA in shutdown). SE: 4 halves = **10.4 mA**; balanced: 8 halves = **20.8 mA** per rail. A disabled package cannot drop to one half, since its outputs are not high-impedance in shutdown (SBOS727B §7.4.1).
- SE 32 Ω full scale (122 mA peak per channel): 2 × 122 / π + 10.4 = **88 mA** per rail. SE 16 Ω (200 mA): **138 mA**.
- Balanced 32 Ω full scale (≈ 200 mA peak per leg, current limit): 2 channels × 2 legs × 200 / π + 20.8 = **275 mA** per rail. This is the design case for every part from VSYS to the amplifiers (§4.10.1).

**Thermal (est.):** per package, balanced 32 Ω full-scale sine (each leg into 16 Ω): ≈ 0.44 W at the 200 mA limit plus 0.06 W quiescent = **≈ 0.5 W**, +24 °C at θJA 47.6 °C/W (SBOS727B §6.4), the same per package as the v1.2 plan. Whole stage at the full-scale sine: ≈ 2.0 W in the four balanced packages, ≈ 0.6 W in the two LDOs, plus converter losses, ≈ 3.5 W into the body: a bench condition (music sits 10–20 dB lower). A balanced 32 Ω full-scale soak in the closed body is a prototype test.

### 4.2 Rail generator choice

| Option | Positive rail at VSYS = 3.5 V | Negative rail | Parts | Verdict |
|---|---|---|---|---|
| LM27762 alone (SNVSAF7C) | LDO from VIN: ≤ 3.5 − 0.045 = 3.45 V → swing 2.45 Vpk → 1.7 Vrms per leg | −VIN via charge pump, then LDO | 1 | **Rejected:** fails 4 Vrms balanced (needs 3.83 V) |
| Boost to 5.5 V + LM27762 | 5.0 V | −5.0 V | 2 + boost passives | Possible second option; LM27762 has the best stock (LCSC 41,293), 22 µVrms noise, 250 mA |
| TPS63710 inverter + boost | — | \|VOUT\| < 0.7 × VIN → max −2.45 V at 3.5 V in | 2 | **Rejected** for the negative rail |
| TPS65131 + TPS7A4901 + TPS7A3001 (v1.2) | +6.0 → +5.0 V | −6.0 → −5.0 V | 3 | **Removed in v1.3**: the LDOs would run at 183 % / 138 % of their 150 / 200 mA ratings at 275 mA |
| **TPS65131 + LT3045 + LT3094** (v1.3, ADR 0012) | +7.0 → +6.04 V | −7.0 → −6.04 V | 3 | **Proposed**: one IC makes both pre-rails from 2.7–5.5 V, 1 µA shutdown, power-save per output (PSP/PSN); 500 mA LDOs |

TPS65131 (SLVS493E): input 2.7–5.5 V, 1.25 MHz, switch current limit 1.8 / 1.95 / 2.2 A, maximum output current given only as typical curves (Figures 6-2, 6-4). v1.3 pre-rails: VPOS = 1.213 V × (1 + 475 k / 100 k) = 6.97 V, VNEG = −1.213 V × 576 k / 100 k = −6.99 V (Eq. 1–2; BOM line 111). The need is 275 mA per rail; the margin check is in §4.10.1.

**Ripple and PSRR chain** (assume 20 mVpp switching ripple on each pre-rail, **UNVERIFIED** until the output capacitors are sized):

- Forced PWM (PSP = PSN = 0): ripple at 1.25 MHz, outside the audio band. LT3045 / LT3094 PSRR at 1 V headroom ≈ 65–75 dB / ≈ 65 dB near 1 MHz (curves G45 / G47, read from the plot) → ≤ 12 µVpp at the OPA1622 (v1.3; the TPS7A4901 gave ≥ 40 dB, ≤ 0.2 mVpp). Add a ferrite bead + 10 µF π-filter before each LDO for another 20 dB.
- Power-save (PFM bursts can land in the audio band): the v1.2 budget used the TPS7A4901's 72 dB at 120 Hz, 20 mV × 10^(−72/20) = 5 µV at the amplifier supply; the LT3045 is specified higher (117 dB at 120 Hz with CSET 4.7 µF, ≈ 110 dB at 1 kHz from curve G41; the figure with CSET 0.47 µF is not tabulated), so 5 µV stays an upper bound. The OPA1622 PSRR is 0.1 µV/V typ at DC (−140 dB); even at an assumed −100 dB in band, the residue is 0.05 nV, far below the DAC floor (0.63 µVrms, §4.3). **Conclusion: power-save mode can stay enabled during playback**, which matters for battery life. Verify by measurement.

**LDO headroom and dissipation:**

| LDO (v1.3) | In → out | Maximum dropout, full range (datasheet) | Headroom | Pd at idle (SE, 10.4 mA) | Pd at 275 mA |
|---|---|---|---|---|---|
| LT3045 (Rev. D) | +7.0 → +6.04 V | 350 mV at 300 mA | ≈ 0.96 V | ≈ 25 mW | ≈ 0.34 W (+12 °C at 34 °C/W) |
| LT3094 (Rev. B) | −7.0 → −6.04 V | 280 mV at 100 mA, 410 mV at 500 mA | ≈ 0.96 V | ≈ 27 mW | ≈ 0.33 W |

Ground currents: LT3045 2.2 mA typ at 10 µA load, 4.3 mA typ (7 mA max) at 100 mA in dropout; LT3094 2.35 mA typ, 3.8 mA typ (6.5 mA max) at 100 mA in dropout. Pd at idle counts the ground current at 7 V. The TPS65131 3 % output accuracy and the ±2 % SET current leave ≥ 0.7 V of headroom (est.), above the dropout. PSRR is specified at 2 V headroom; the 1 V curves above are the design basis.

**Ramp symmetry (v1.3, D30).** The OPA1622 wants V+ and V− to ramp symmetrically with EN held low (SBOS727B §7.4.2). The LT3045 and LT3094 share the soft-start law tSS ≈ 2.3 × RSET × CSET (LT3045 Rev. D p. 19, LT3094 Rev. B p. 22): with RSET 60.4 kΩ and CSET 0.47 µF on both, each rail ramps on the same RC curve in ≈ 65 ms. Fast start-up is disabled (PGFB tied to IN), because its SET currents differ (2 mA and 1.8 mA typ). Both EN/UV pins share the 3.3 V `HPA_LDO_EN` net, raised after the TPS65131 pre-rails settle (`HPA_RAIL_EN` first), so the LDO soft-start alone sets the ramp. The residual mismatch is the CSET tolerance: a bring-up measurement. The v1.1 TPS7A4901/TPS7A3001 sizing (CNR/SS 10 nF / 15 nF, D3) no longer applies.

**Rejected positive LDOs:** TPS7A94 (15 mA ground current, §1); TPS7A2050 (VIN absolute maximum 6.0 V, below the +7 V pre-rail of v1.3); TPS7A4901 (150 mA, removed in v1.3).

### 4.3 DAC analog rails: noise budget versus PSRR

- DAC noise floor: 130 dB A-weighted dynamic range re 2 Vrms → 2 × 10^(−130/20) = **0.63 µVrms**.
- CS43198 VA PSRR: 75 dB at 217 Hz (DS1156F2, Table 3-15; the only point given).
- TPS7A2018 output noise 7 µVrms (SBVS338H). Coupled to the output: 7 µV × 10^(−75/20) = **1.2 nV**, 54 dB below the floor. Even with PSRR falling to 40 dB at 20 kHz: 70 nV, still 19 dB below.
- **Conclusion:** an ultra-low-noise LDO (LT3042 class, 0.8 µVrms, about 2 mA Iq) buys nothing measurable on VA; the TPS7A2018 costs 6.5 µA quiescent and $0.26. One LDO per DAC keeps dual mono independent.

**DAC power (Table 3-17, PCM playback, VA = VCP = VD = VL = 1.8 V, VP = 3.6 V):** VCP 3.808 mA, VA 7.835 mA, VD 2.786 mA, VP 0.028 mA, **26.1 mW per DAC**. Standby (HP detect on) 0.58 mW; off (VP only) 11 µW.

**Efficiency of the 1.8 V analog path** (two DACs' VA = 15.7 mA at 1.8 V = 28 mW; the MCLK now runs at 3.3 V from VSYS, see the clocks row):

| Feed | Chain efficiency | Battery power |
|---|---|---|
| LDO straight from VSYS (3.8 V) | 1.8 / 3.8 = 47 % | 117 mW |
| TPS62840 2.2 V (~90 %, **UNVERIFIED** at 31 mA) + LDO (1.8 / 2.2 = 82 %) | 74 % | 75 mW |

The pre-buck saves about **42 mW**, roughly 4–6 % of screen-off playback power. TPS62840 has 60 nA Iq and 25 nA shutdown (SLVSEC6D).

### 4.4 Master clocks

- NZ2520SDA: 15 mA operating, 35 µA standby, **tri-state output in standby** (NDK catalog 1703A). Both oscillator outputs can therefore share one MCLK net to the two DACs, with exactly one enabled: no clock multiplexer in the path.
- Phase noise at 1.8 V: 22.5792 MHz −158 dBc/Hz at 1 kHz, −163 at 100 kHz; at 3.3 V −164 / −169 (NDK catalog). The 1.8 V version is about 6 dB worse close-in; it is still an audio-grade XO (the CS43198 PLL, which is bypassed here, only asks for < 50 ps reference jitter). Whether the 6 dB is audible or measurable is for the A/B measurement in the sourcing report §4.
- Power (v1.1, MCLK_3V1): 15 mA maximum at 3.1 V = 47 mW at the oscillator, 15 mA × VSYS ≈ 56 mW from the battery at 3.7 V through the LDO. The idle family costs 35 µA. The 15 mA is the catalogue maximum; the typical figure is not given.
- Phase noise is characterised at 3.3 V (−164 dBc/Hz at 1 kHz, 22.5792 MHz). The figure at 3.1 V and the 24.576 MHz figure are **UNVERIFIED** until the J-test captures (ADR 0010).

### 4.5 Backlight (Focus E35GH-I-MW800-CB)

From the Focus spec sheet (rev 1.0): 10 LEDs, edge-lit, IF 60 mA, VF 14.0 / 15.0 / 16.5 V (min/typ/max), so 5 in series × 2 parallel strings, single LEDA/LEDK pair. Panel VCI 2.5–3.3 V (2.8 V typ), IOVCC 1.65–3.3 V (1.8 V typ). CTP normal current 8 mA typ, 14.5 mA max.

TPS61169 (SNVSA40B): 2.7–5.5 V in, 1.2 MHz, 1.2 A minimum switch limit, 204 mV reference, 37.5 V OVP, 1 µA shutdown.

- Sense resistor: R = 0.204 V / 0.060 A = **3.40 Ω** (1 %, 12 mW).
- Full brightness: Pout = 16.5 V × 60 mA = 0.99 W (max VF). At VIN = 3.5 V and η = 85 %: Iin = 0.99 / (3.5 × 0.85) = 0.33 A.
- Duty cycle: D = 1 − VIN·η / VOUT = 1 − 3.5 × 0.85 / 16.5 = 0.82.
- Ripple with L = 10 µH, f = 1.2 MHz: ΔIL = VIN·D / (L·f) = 3.5 × 0.82 / (10 µH × 1.2 MHz) = 0.24 A → peak 0.33 + 0.12 = **0.45 A < 1.2 A**. A 10 µH, ≥ 0.6 A saturation inductor (Murata LQH3NPN100MJRL class) and a 60 V, 1 A Schottky (Nexperia PMEG6010CEH, BOM v1.1; the 40 V PMEG4010CEH left 1 V over the 39 V OVP maximum) suffice.
- Indoor 200 nit: about 15 mA if luminance is linear in current (**UNVERIFIED**), VF about 13.5 V (est.) → 0.20 W out, about 0.25 W from the battery. Full 800 nit outdoors: about 1.1 W.
- Dimming: PWM on CTRL scales the internal reference (analog dimming of the LED current, flicker-free), driven by the ALS through OpenDAP OS (`pwm-backlight`, Debian `=m`).
- Placement: on the main board, so the faceplate FPC carries LEDA/LEDK. 37.5 V OVP covers strings up to about 10 series LEDs, so other faceplates need no board change (BRD-048).

### 4.6 HAT power: eFuse current limits and inrush

TPS259470 (SLVSFC9C): 2.7–23 V, RON 28.3 mΩ, ILIM set by RILM (1.65 kΩ → 2.03 A, 3.32 kΩ → 1.007 A, so ILIM ≈ 3,350 Ω·A / RILM), reverse-current blocking, IMON.

| eFuse | Path | ILIM target | RILM (E96) | Conduction loss at ILIM |
|---|---|---|---|---|
| #A | TPS61089 → HAT_5V | 1.5 A | 2.21 kΩ (1.52 A) | 28.3 mΩ × 1.5² = 64 mW |
| #B | TLV62569 → HAT_3V3 | 1.0 A | 3.32 kΩ (1.007 A) | 28 mW |
| #C | TPS61089 → USB-C VBUS | 1.5 A | 2.21 kΩ | 64 mW |

- **Source:** a TPS61089 boost from VSYS feeds #A and #C (the BQ25895 OTG boost cannot run while charging, finding 9). Sizing (SLVSD38C): on adapter power only HAT_5V can be sourced (1.5 A); on battery HAT_5V and USB-C source share ≈ 0.4 A with the interim pack and the full 1.5 A with an ADR 0011 pack (below). Design output 1.6 A at 5.1 V. At VIN = 3.0 V and η = 0.88 the input current is 5.1 × 1.6 / (3.0 × 0.88) = 3.1 A; with 1.5 µH at 1 MHz and D = 1 − 3.0 × 0.88 / 5.1 = 0.48, ΔIL = 3.0 × 0.48 / (1.5 µH × 1 MHz) = 0.96 A, so the peak is 3.6 A. With TI's L − 30 % (1.05 µH) the ripple is 1.18 A and the peak 3.7 A. v1.2: the limit can sit up to 0.8 A below the calculated value (SLVSD38C §9.2.2.3), so the v1.1 RILIM of 200 kΩ (5.15 A typ) gave 4.35 A minimum and the peak sat at 85 % of it. **RILIM = 182 kΩ** sets ILIM = 1,030,000 / 182,000 = 5.66 A typ, 4.86 A minimum: the peak is 76 %. The XAL4020-152 (Isat 7.1 A typ) is above the typical limit; the maximum limit at 182 kΩ is not specified (≈ 6.5 A if the spread is symmetric, **UNVERIFIED**). If software lets both eFuses reach their 1.5 A ceilings on battery, the boost current limit bounds the fault. On adapter power only HAT_5V can be sourced (the USB-C port is then the input), so #A at 1.5 A (≈ 8.5 W from VSYS at η ≈ 0.9) fits inside the 3.5 A VSYS rating with the system load. The boost also covers the case the draft missed: a class A/B HAT keeps 5 V while the T1 charges.
- **Full output budget (v1.2, BRD-050):** the same on battery as on adapter power: 1.5 A at 5.1 V shared by HAT_5V and the USB-C source (one TPS61089, 1.6 A design), plus HAT_3V3 at 1.0 A. Serving both 5 V ports at 1.5 A together is not in the budget: it would need ≈ 7.3 A from the battery, above the BQ25895's 6 A continuous discharge rating. The battery current is derived in §4.7.
- **Battery budget with the interim pack (v1.1):** on battery the derated JST PH path caps the pack at 1.6 A ≈ 5.6 W at 3.5 V. With the base system at 1–3 W (screen off to screen on with CPU load, **est.**), about 2.6 W remains: ≈ 2.6 × 0.9 / 5.1 = 0.46 A, taken as **0.4 A** at 5.1 V for HAT_5V **plus** USB-C source together. OpenDAP OS enforces it with the VSYS INA236 and the eFuse IMON; USB-C advertises Default (0.5 A) on battery. HAT power classes A/B must be written against this number until an ADR 0011 pack is fitted (hat-standard). With such a pack, USB-C advertises 1.5 A on battery while HAT_5V is idle.
- **Hardware ceilings stay** at ILIM 1.5 / 1.0 / 1.5 A (maximum trip 1.66 / 1.15 / 1.66 A, SLVSFC9C §6.5) so a fault is still bounded if software fails.
- **HAT power connector (v1.2):** a DF40 50-contact pair (HAT_5V ×12, HAT_3V3 ×6, GND ×22), allocated by the hat-standard HAT interface v0 and unchanged in v1. At 0.3 A per contact: HAT_5V 2.0 A continuous = 0.17 A per contact (56 %), HAT_3V3 1.15 A = 0.19 A (64 %), returns 2.0 + 1.15 A = 0.14 A (48 %); the worst fault ceiling, 3.0 A from a class F HAT through the TPS2121 ILM, is 0.25 A per contact (83 %, ≤ 100 %). The v1.1 30-contact pair put HAT_3V3 at 96 % (1.15 A on 4 contacts).
- **Inrush:** with CdVdt = 1.8 nF the rising slew is 0.87 V/ms at 2.7 V and 1.09 V/ms at 12 V; take 0.92 V/ms at 5 V. A HAT with 100 µF bulk draws I = C·dV/dt = 100 µF × 920 V/s = **92 mA** for 5.4 ms; 470 µF draws 0.43 A, still under ILIM. The HAT standard should cap HAT bulk capacitance at 470 µF per rail.
- **Powerbank HAT input (class F):** HAT_5V → TPS2121 IN2. When the T1 sources HAT_5V, `HAT_SRC_ON` (the same net that enables #A) drives TPS2121 OV2 high so IN2 cannot connect; when it sources USB-C VBUS, `USB_SRC_ON` drives OV1 high. The interlock is wired, not a software ordering rule.

### 4.7 Charger, battery and input path

- BQ25895: 3.9–14 V input, 5 A charge, 1.5 MHz, 1 µH inductor and ≥ 20 µF on SYS recommended (SLUSC88C §9). PMID capacitance per the datasheet for charge-only use (OTG is not used).
- Battery-only quiescent: 32 µA typ with BATFET on and monitor off (12 µA with BATFET off, ship mode).
- Pack: Adafruit 328 (ADR 0007), spec sheet Q/WAPL785060-1011: charge ≤ 1C (2.5 A) at 0–40 °C and ≤ 4.25 V, discharge ≤ 2C. Charge current 1.2 A (Adafruit's advice), VREG 4.20 V; LiHV packs later at 4.35/4.40 V from the device tree (ADR 0008). The TS thresholds must stop charging above 40 °C (the BQ25895 default hot limit is higher, **UNVERIFIED** exact value).
- Battery current (v1.1): JST rates the PH contact 2 A AC/DC with AWG #24 wire (ePH catalog) and gives no figure for the 26 AWG leads of the Adafruit 328. Assuming the rating is set by heating of the crimp and wire, equal I²R per length scales the current by √(A26 / A24) = √(0.129 / 0.205) = 0.79, so the budget is **1.6 A continuous** (est.). The VSYS INA236 enforces it in software; a JST or Adafruit 26 AWG figure would restore 2 A. From v1.2 a 2.5 A NANO2 fuse in BAT+ (BOM line 104) bounds a sustained overload in hardware: 1.6 A is 64 % of it.
- **Full output budget on battery (v1.2, BRD-050, proposed ADR 0011).** Loads at VSYS = 3.3 V, below which OpenDAP OS sheds HAT and USB-C source load through the gauge:

  | Load | Output | Efficiency | From VSYS |
  |---|---|---|---|
  | TPS61089, HAT_5V + USB-C source | 5.1 V × 1.6 A = 8.16 W | 0.88 (curve, **UNVERIFIED**) | 9.27 W |
  | TLV62569, HAT_3V3 | 3.3 V × 1.0 A = 3.3 W | 0.90 (**UNVERIFIED**) | 3.67 W |
  | System, screen on with CPU load | — | — | 3.0 W (est.) |
  | **Total** | | | **15.9 W → 4.8 A at 3.3 V** |

  Every element of the battery chain must carry 4.8 A with margin: cell ≥ 6.0 A continuous (80 %), pack PCM trip ≥ 6.0 A, lead and connector ≥ 6.9 A per pole (70 %), board fuse 7 A (69 %, NANO2 0451007, same footprint as the interim 2.5 A part), BQ25895 BATFET 6 A continuous (80 %, SLUSC88C §7.3; OCP 9 A), VSYS shunt ≥ 1 W, gauge sense 5 mΩ ≥ 0.5 W if the MAX17055 ±51.2 mV range holds (**UNVERIFIED**). Path drop at 4.8 A: BATFET 19 mΩ max + fuse + sense + shunt + connector ≈ 50 mΩ (est.) → ≈ 0.24 V, so the cell must hold ≈ 3.55 V under load for VSYS = 3.3 V. The Adafruit 328 fails at the cell (4.8 A = 96 % of its 5 A maximum) whatever the connection, and no stocked pack meeting these figures was found on 2026-10-22 (ADR 0011).
- **Input limits (v1.2).** BQ25895 IIN is rated 3.25 A and ISYS (SW) 5 A (SLUSC88C §7.3). IINLIM ≤ 2.0 A and VBUS × IINLIM ≤ 15 W (PD 9 V at 1.65 A; 5 V at 2.0 A) keep ISYS ≤ 15 W × 0.9 / 3.5 V = 3.9 A (77 %). The TPS2121 ILM is set with RILM = 44.2 kΩ to 2.0–3.0 A (2.5 A typ, SLVSEA3F §7.5): above IINLIM, ≤ 67 % of the 4.5 A rating, and it bounds a class F HAT on the DF40 power contacts (§4.6).
- Input: PD sink at 9 V; v1.2 requests 1.65 A (15 W, see input limits above) against about 7.3 W needed for charging (1.5 A × 4.2 V charge + 1 W system). TPS2121 conduction loss at 2 A input: 56 mΩ typ → 0.22 W; 100 mΩ maximum over −40 to 125 °C (SLVSEA3F §7.5) → 0.40 W, a 29 °C rise at RθJA 72.2 °C/W (JEDEC board; check in the board thermal model).
- TPS2121 OV1 (BOM v1.1, one value): R1 = 1.02 MΩ, R2 = 100 kΩ (1 %), VTRIP = VREF × (1 + R1/R2) = 1.06 × 11.2 = 11.9 V typ; 11.1–12.6 V over VREF 1.01–1.1 V and resistor tolerance. That is above a 9 V PD contract (9.45 V at +5 %) and below the BQ25895 14 V operating maximum.
- USB-C VBUS surge: TVS2200 (22 V flat clamp, 28.4 V max at 40 A 8/20 µs). The TPS2121 (24 V absolute maximum, OV1 at 11.9 V) sits between the connector and the BQ25895 (22 V absolute maximum). A 40 A surge clamp of 28.4 V exceeds both ratings, so the TVS is sized for ESD and hot-plug ringing, not for an IEC 61000-4-5 surge (**risk**, §9).

### 4.8 LPDDR4X VDDQ (0.6 V)

- TPS7A1006 (SBVS314B): 0.6 V fixed, 300 mA, VIN from vcc_ddr (1.1 V), BIAS from vcc_1v8 (1.7–5.5 V), 70 mV maximum dropout at 300 mA (VOUT > 1.0 V; larger at 0.6 V, still inside the 0.5 V headroom).
- Dissipation at an estimated 0.2 A peak: (1.1 − 0.6) × 0.2 = 0.10 W; efficiency 0.6 / 1.1 = 55 % on a small rail, against about 35 % from vcc_1v8.
- The current figure is **UNVERIFIED**: confirm it and the regulator type against the Rockchip RK3566 hardware design guide (not retrieved this session).

### 4.9 Screen-off playback budget and runtime

| Block | Load at the rail | From the battery | Basis |
|---|---|---|---|
| SoC, LPDDR4X, eMMC, PMIC losses | — | 450–800 mW | **Est., UNVERIFIED** (no RK3566 measurement yet) |
| 2× CS43198 (VA, VCP, VD, VL, VP) | 52 mW | 65 mW | Table 3-17 + chain efficiency |
| Active MCLK oscillator | 47 mW | 56 mW | NDK catalog maximum at 3.1 V, LDO from VSYS |
| OPA1622, SE output (2 packages, 4 halves), quiescent, with the LT3045/LT3094 (v1.3) | 125 mW | 256 mW | 10.4 mA × 12 V at the amplifiers; (10.4 + 2.3) mA and (10.4 + 2.45) mA at ±7 V = 179 mW at the pre-rails; TPS65131 η ≈ 70 % (**UNVERIFIED**). v1.2 (±5 V, TPS7A pair): 180 mW |
| Headphone load, 1 mW per channel | 2 mW | 4 mW | — |
| IMU, gauge, TCPC, charger | — | 3 mW | datasheets |
| **Total** | — | **0.84–1.19 W** (v1.2: 0.76–1.11 W) | — |

- Runtime, 90 % usable energy: Adafruit 328 (9.4 Wh, the only adopted pack, ADR 0007) → **7.1–10.1 h** (v1.2: 7.6–11.1 h): above the 6 h red line, around the 8 h warning, below the 12 h ideal (T1-039). The battery model of the T1 battery-life analysis gives 12.8 → 11.4 h for its core SE session (research §5.3). The SoC estimate dominates (risk 1). Larger packs are not adopted (T1-038).
- The OPA1622 quiescent current (256 mW from the battery on the SE output) is the largest audio term. Only the selected output is enabled. The balanced output enables 8 halves: (20.8 + 2.3) mA and (20.8 + 2.45) mA at ±7 V = 324 mW at the pre-rails, **≈ 464 mW** from the battery (est.).
- Screen on at 200 nit adds about 0.25 W backlight + 0.05 W panel and touch + GPU/VOP (**UNVERIFIED**, est. 0.2 W).

### 4.10 Power margin check (BOM v1.2)

BRD-049 check of every rail, converter, connector and cable. Rule: continuous load ≤ 80 % of the rating for converters, regulators, switches and diodes (fuses ≤ 75 %), ≤ 70 % for connector contacts with all contacts loaded; the worst-case trip of the protecting limiter ≤ 100 % of the rating. Loads marked est. are estimates (T1-026). "Full" = the full output budget on battery (§4.7).

| Item | Rating (source) | Design load | Use | Worst-case ceiling | Verdict |
|---|---|---|---|---|---|
| USB-C receptacle VBUS (USB4105) | 5 A (GCT drawing) | 2.0 A in / 1.5 A out | 40 % | 3.0 A (TPS2121 ILM max) | OK |
| TPS2121 power mux | 4.5 A (SLVSEA3F §7.3) | 2.0 A (IINLIM) | 44 % | 3.0 A ILM = 67 % | OK (v1.2 sets RILM 44.2 kΩ) |
| BQ25895 input | IIN 3.25 A | 2.0 A | 62 % | ILM 3.0 A = 92 % | OK |
| BQ25895 SW output (VSYS on adapter) | ISYS 5 A | 3.9 A (15 W input cap) | 77 % | — | OK (v1.2: was up to 4.6 A = 93 % at 18 W) |
| Charger inductor XAL4020-102 | Isat 8.7 A, Irms 6.7 A (20 °C) | 3.9 A | 58 % of Irms | — | OK |
| BQ25895 BATFET (battery discharge) | 6 A continuous, 9 A ≤ 1 s, OCP 9 A (SLUSC88C §7.3) | 1.6 A interim / 4.8 A full | 27 % / 80 % | 9 A OCP | OK (full at the limit of the rule) |
| Battery fuse (NANO2) | 2.5 A interim / 7 A full | 1.6 A / 4.8 A | 64 % / 69 % | — | OK (new, v1.2) |
| Battery lead and JST PH (interim pack) | 2 A with AWG #24; 26 AWG fitted | 1.6 A | 80 % of the AWG #24 rating (derated estimate 1.6 A) | fuse 2.5 A | Accepted interim; ADR 0011 for the full budget |
| Battery cell (Adafruit 328) | 5 A (2C) | 1.6 A / 4.8 A | 32 % / 96 % | — | **Fails the full budget** (ADR 0011) |
| VSYS INA236 shunt 10 mΩ | ≥ 1 W required | 0.23 W at 4.8 A | ≤ 23 % | 0.36 W at 6 A | v1.2 requirement |
| vcc3v3_sys buck TPS62826 | 3 A; ILIM ≥ 3.7 A | 1.85 A peak (est.) | 62 % | inductor peak 2.25 A = 61 % of ILIM min | OK (v1.2; TLV62569 was 80–90 %) |
| vcc3v3_sys inductor Würth 744373240047 (v1.3, D27; was DFE252012F-R47M, 4.9 A < 5.0 A) | 6.8 A (TI Table 8-5); IR 8.7 A (ΔT 40 K), Isat 10.4 A at 10 % drop (Würth page) | 2.25 A peak | 33 % of 6.8 A | ILIM max 5.0 A = 74 % of 6.8 A | OK |
| RK860-0 vdd_cpu | **UNVERIFIED** (no public datasheet) | 3 A (est.) | — | — | Open: datasheet from Rockchip |
| RK809 BUCK1–5 | 2.5 / 2.5 / 1.5 / 1.5 / 2.5 A (RK809 DC table) | play 0.1–0.3 A; peaks **UNVERIFIED** | — | — | Open: measure on a reference board |
| RK809 LDO4 FP_VCI | 100 mA design (tables disagree, 100/400 mA) | panel VCI (spec gives no current) | — | — | Open with the panel current |
| RK809 SWOUT1 / SWOUT2 | 1.5 A / 3 A (designed to 1.5 A) | 0.6 A / 0.2 A (est.) | 40 % / 13 % | — | OK |
| TPS7A1006 vcc0v6_ddr | 0.3 A | 0.2 A (est., **UNVERIFIED**) | 67 % | — | OK pending the RK3566 guide |
| TPS22919 load switches | 1.5 A | ≤ 0.08 A | ≤ 6 % | — | OK |
| TPS62840 AUDIO_2V2 | 0.75 A | 16 mA | 2 % | — | OK |
| TPS7A2018 ×2, TPS7A2031 | 0.3 A | 7.8 / 15 mA | ≤ 5 % | — | OK |
| TPS65131 pre-rails ±7 V (v1.3) | switch limit 1.8 A min | 275 mA per rail | inverter 72–79 %, boost 48–56 % of the minimum switch limit | 2.2 A max switch limit | **Conditional**: inside the rule at its edge; simulation before layout freeze (§4.10.1, ADR 0012) |
| LT3045 HPA_P6V0 (v1.3) | 0.5 A | 0.275 A worst continuous sine | 55 % | ≈ 0.4 A programmed (≈ 0.36 A min, est.) | OK |
| LT3094 HPA_N6V0 (v1.3) | 0.5 A | 0.275 A | 55 % | ≈ 0.4 A programmed | OK |
| TPS61169 backlight | switch ≥ 1.2 A | 0.45 A peak | 38 % | — | OK |
| PMEG6010CEH rectifier | 1 A, 60 V | 0.06 A avg, 39 V OVP max | 6 % / 65 % | — | OK |
| LQH3NPN100MJRL | Isat **UNVERIFIED** (≥ 0.6 A needed) | 0.45 A peak | — | — | Open: spec sheet |
| TPS61089 boost | ILIM min 4.86 A (182 kΩ) | 3.7 A peak | 76 % | max limit **UNVERIFIED** (≈ 6.5 A) | OK (v1.2; 85 % at 200 kΩ) |
| XAL4020-152 | Isat 7.1 A, Irms 5.2 A (20 °C) | 3.7 A peak, 3.1 A rms | 60 % of Irms | ≈ 6.5 A < Isat (**UNVERIFIED**) | OK |
| TPS259470 eFuses | 5.5 A switch | 1.5 / 1.0 / 1.5 A | ≤ 27 % | 1.66 / 1.15 / 1.66 A | OK |
| TLV62569 HAT_3V3 buck | 2 A | 1.0 A | 50 % | 1.15 A = 58 % | OK |
| DFE252012F-2R2M (HAT buck) | 2.3 A (ΔT 40 °C) | 1.0 A + ripple | ≤ 50 % at 1.15 A | — | OK |
| DF40 power connector, HAT_5V | 12 × 0.3 A | 2.0 A | 56 % | 3.0 A in = 83 % | OK (v1.2: 30 → 50 contacts) |
| DF40 power connector, HAT_3V3 | 6 × 0.3 A | 1.0 A | 56 % | 1.15 A = 64 % | OK (v1.1 30-pin: 96 %) |
| DF40 power connector, GND | 22 × 0.3 A | 3.0 A | 45 % | 4.15 A = 63 % | OK |
| HAT flat cable (FPC) power conductors | sized per IPC-2152 for ≤ 10 °C rise | 2.0 / 1.0 / 3.0 A | — | 3.0 / 1.15 / 4.15 A | Requirement for the FPC drawing (widths **UNVERIFIED**) |
| HAT pogo contacts (P70, device-side piece; v1.4: hat-standard interface v1 §5, HAT_5V ×3, HAT_3V3 ×2, GND ×4) | 2.0 A per contact | 2.0 / 1.0 / 3.0 A | 33 / 25 / 38 %; 50 % each with one contact open | interface ceilings 3.6 / 1.8 / 5.4 A = 60 / 45 / 68 % (90 % with one contact open); the T1's eFuse and TPS2121 ceilings are lower | OK (v1.4) |
| Faceplate FH35C contacts | 0.2 A, 0.14 A all loaded | FP_VCI 0.1 A ×1; FP_3V3 ≈ 0.08 A ×2; BL 60 mA; LED ≤ 20 mA | ≤ 71 % of the derated figure | — | OK |
| LP5521 outputs / LED | 25.5 mA; LED IF 25 mA | 20 mA DT cap | 78 % / 80 % | — | OK (new, v1.2) |

### 4.10.1 Headphone stage margin (BOM v1.3, ADR 0012)

Worst continuous case: full-scale sine into balanced 32 Ω, both channels, 275 mA per ±7 V rail (§4.1). VIN = VSYS, 3.0 V (battery near empty) to 3.5 V. The TPS65131 equations are SLVS493E Eq. 3 and 4 (peak inductor current, IL = V × I / (VIN × 0.64)); the curve readings are typical values at 25 °C, read from Figures 6-2 and 6-4 and interpolated between the plotted output voltages.

| Item | Rating (source) | Load at VIN 3.5 V | Load at VIN 3.0 V | Use (3.5 / 3.0 V) | Verdict |
|---|---|---|---|---|---|
| TPS65131 inverter switch | 1.8 A min, 1.95 typ, 2.2 max | 1.29 A peak (Eq. 4) | 1.43 A | **72 % / 79 %** | At the edge of the 80 % rule: conditional (simulation) |
| TPS65131 inverter output, typical curve | Figure 6-4: ≈ 480 mA at 3.5 V, ≈ 340 mA at 3.0 V (−7 V, interpolated) | 275 mA | 275 mA | 57 % / 81 % | Typical only; agrees with Eq. 4 at 3.0 V |
| TPS65131 boost switch | 1.8 A min | 0.86 A (Eq. 3) | 1.00 A | 48 % / 56 % | OK |
| TPS65131 boost output, typical curve | Figure 6-2: ≈ 640 mA at 3.0 V (+7 V, between the 5 V and 10 V curves) | 275 mA | 275 mA | — / 43 % | OK |
| Inverter inductor DFE252012F-4R7M | 2.1 A (ΔL/L −30 %), 1.5 A (ΔT 40 °C) | 1.29 A peak | 1.43 A peak, ≈ 1.15 A average (η 0.8, est.) | 61 % / 68 % peak; 76 % average | OK at the design load; the 2.2 A maximum switch limit exceeds the 2.1 A rating (BOM D31) |
| Boost inductor DFE252012F-4R7M | as above | 0.86 A peak | 1.00 A peak, ≈ 0.80 A average | 48 % peak; 53 % average | OK |
| Rectifiers PMEG2010AEH | 1 A, 20 V (listing) | 275 mA average | 275 mA; reverse VIN + 7 V ≤ 11.4 V | 28 %; 57 % | OK |
| LT3045 / LT3094 | 500 mA | 275 mA | 275 mA | 55 % | OK |
| VSYS draw of the headphone rails | interim battery path 1.6 A (§4.7) | 4.8 W = **1.38 A** (η 0.8, est.) | **1.61 A** | 86 % / 100 % by itself | **Fails on the interim pack without a ceiling**: §4.11 |

- **Result:** every part except the TPS65131 inverter is inside the BRD-049 rule with margin. The inverter stays at 79 % of its minimum switch limit at VIN 3.0 V by Eq. 4, and the typical curve gives ≈ 81 % there. ADR 0012's condition holds: confirm by WEBENCH or SPICE at VIN 3.0 V, ±7 V, 275 mA per rail before layout freeze, or replace the inverter by one with more margin.
- With the interim ceiling of §4.11 in screen-off playback the rails carry ≈ 217 mA, and the inverter peak drops to 1.13 A at VIN 3.0 V (63 %).

### 4.11 Interim battery: headphone output ceiling (BOM v1.3, ADR 0012)

The Adafruit 328 path is budgeted at **1.6 A continuous** (§4.7), for every load together. At full scale into balanced 32 Ω the headphone rails alone draw 2 × 7 V × 275 mA / 0.8 ≈ 4.8 W from VSYS: 1.38 A at 3.5 V, **1.61 A at 3.0 V** (η 0.8 for the TPS65131 at this load, est.). Single-ended, full scale draws ≈ 1.5 W into 32 Ω (0.51 A at 3.0 V) and ≈ 2.4 W into 16 Ω (0.80 A).

Headroom for the headphone rails is 1.6 A × VSYS less the rest of the system. Ceiling on a continuous full-scale sine into balanced 32 Ω, per channel, from the rail model of §4.1 (Ipk per leg = (I_rail − 20.8 mA) × π / 4, P = Ipk² × 16 Ω):

| VSYS | Rest of the system (est.) | Left for the headphone rails | Ceiling, balanced 32 Ω | Below the full ≈ 640 mW |
|---|---|---|---|---|
| 3.5 V | 1.0 W (screen-off playback, §4.9 without the amplifier terms, rounded up) | 4.6 W | ≈ 580 mW | −0.4 dB |
| 3.3 V | 1.0 W | 4.3 W | ≈ 490 mW | −1.1 dB |
| **3.0 V** | **1.0 W** | **3.8 W** | **≈ 380 mW** | **−2.3 dB** |
| 3.0 V | 3.0 W (screen on with CPU load, §4.7) | 1.8 W | ≈ 65 mW | −9.8 dB |

**Requirement for OpenDAP OS (ADR 0012 condition):** while a battery path budgeted below the full output is fitted (the Adafruit 328: 1.6 A), OpenDAP OS shall limit the headphone output level so that the continuous battery current, measured by the VSYS INA236, stays at or below that budget, together with the HAT and USB-C source load of §4.6. The design figure for screen-off playback is **≈ 380 mW per channel into balanced 32 Ω at VSYS 3.0 V** (≈ −2.3 dB under the full output); single-ended output stays below the ceiling except at 16 Ω with a high system load. The full output needs an ADR 0011 pack. The system figures are estimates (T1-026); the ceiling is enforced on the measured current, not on these numbers.

- **With an ADR 0011 pack:** the full output budget of §4.7 (15.9 W from VSYS) counts the system at 3.0 W and has no separate headphone term; the full-scale balanced 32 Ω sine adds ≈ 4.8 W. OpenDAP OS must budget headphone and HAT/USB-C power together, or the budget grows: a decision for the maintainers (BOM §7 item 17).

## 5. Power-gating map

Default state is the state with no software running (pull resistors). "SoC GPIO" means a RK3566 GPIO in a 1.8 V bank unless noted; ball assignment waits for the pin-multiplexing study.

| Block | Rail(s) | Switch / enable | Control | Default | Discharge | Notes |
|---|---|---|---|---|---|---|
| DAC digital (both) | DAC_DIG_1V8 | TPS22919 | SoC GPIO `DAC_DIG_EN` | off (pull-down) | QOD in TPS22919 | Park I2S lines low before removal (back-powering) |
| DAC VP (both) | DAC_VP | TPS22919 | SoC GPIO `DAC_VP_EN` | off | QOD | VP first on, last off |
| DAC analog + clocks | AUDIO_2V2, DACx_VA, MCLK_3V1 | TPS62840 EN, TPS7A2018 EN, TPS7A2031 EN | SoC GPIO `AUDIO_LN_EN` | off | TPS7A20 smart pulldown, TPS62840 active discharge | — |
| MCLK family select | NZ2520SDA ×2 | ST pin (tri-state) | `MCLK441_EN`, `MCLK48_EN` at 3.3 V logic (TCA6416A or single-bit translator, pinout v1) | both standby (pull-down on each ST pin; an open ST enables the output) | — | Never both enabled |
| HP amp rails | AUDIO_P7V0/N7V0, HPA_P6V0/N6V0 | TPS65131 ENP/ENN; LT3045 and LT3094 EN/UV (v1.3) | `HPA_RAIL_EN` (pre-rails), then `HPA_LDO_EN` (both LDOs), 3.3 V logic (EN/UV thresholds 1.24 V and +1.26 V) | off | — | Symmetric ramp from equal RSET × CSET, ≈ 65 ms (§4.2, OPA1622 §7.4.2) |
| HP amp outputs | per package | OPA1622 EN (×6: 2 SE, 4 balanced) | SoC GPIO `HPA_SE_EN`, `HPA_BAL_EN` | low (shutdown, 5 µA/ch) | — | EN low during rail ramps; on battery the level is capped by §4.11 |
| Speaker amp | VSYS | MAX98357A SD_MODE | SoC GPIO `SPK_SD` | shutdown | — | Device shutdown, no extra switch |
| Microphones + privacy LED | MIC_1V8 | TPS22919 | SoC GPIO `MIC_EN` | off | QOD | LED gate driven by MIC_1V8 itself (BRD-027) |
| Faceplate logic | FP_VCI, FP_3V3, FP_1V8 | RK809 LDO4, TPS22919 ×2 | RK809 I2C, expander `FP_IO_EN` | off | QOD | Panel and touch reset low first |
| Backlight | BL_LEDA | TPS61169 CTRL | SoC PWM `BL_PWM` | off (1 µA) | — | ALS-driven |
| Status LED (RGB) | LED_R/G/B | LP5521 CHIP_EN bit, charge pump in power-save | I2C2 (`leds-lp5521`) | standby (1 µA, EN high, CHIP_EN = 0) | — | v1.2. EN tied to vcca1v8_pmu; works with the screen off and in suspend if the driver keeps it on |
| Wi-Fi/BT | vcc3v3_wl | RK809 SWOUT1 | RK809 I2C | off | **UNVERIFIED** | Plus module PDn |
| microSD | vcc3v3_sd, vccio_sd | RK809 SWOUT2, LDO5 | RK809 I2C | per DT | **UNVERIFIED** | UHS-I voltage switch |
| RP2354A | RP_3V3, RP_IOVDD_1V8 | TPS22919 ×2 | SoC GPIO `RP_PWR_EN` | **open question** (§8) | QOD | SoC boots without it (BRD-019). VREG_VIN and VREG_AVDD share RP_3V3, so they ramp together (DS §6.1.8); IOVDD may come up in any order |
| NPU | vdd_npu | RK809 BUCK4 | DT | off | — | Enabled only by an AI overlay |
| GPU | vdd_gpu | RK809 BUCK2 | DT + devfreq | on with display | — | — |
| Camera PHY (HAT) | LDO1, LDO9 | RK809 I2C | HAT overlay | off | — | Only with a camera HAT |
| PCIe/USB3 PHY (HAT) | SoC `PD_PIPE` | SoC power domain | HAT overlay | off | — | Topology report §1.3 |
| HAT 3.3 V | HAT_3V3 | TLV62569 EN + TPS259470 #B | SoC GPIO `HAT3V3_EN` | off | eFuse | HAT EEPROM read needs 3.3 V first |
| HAT 5 V out | HAT_5V | TPS61089 + TPS259470 #A | expander `HAT5V_EN` (= `HAT_SRC_ON`) | off | eFuse | Same net forces TPS2121 OV2 |
| HAT 5 V in (powerbank) | HAT_5V → VBUS_CHG | TPS2121 IN2 | OV2 (released when `HAT_SRC_ON` is low) | enabled | — | Dead-battery boot from a powerbank HAT |
| USB-C VBUS out | VBUS | TPS61089 + TPS259470 #C | TCPM source role → `USB_SRC_ON` | off | eFuse | Forces TPS2121 OV1; Default (0.5 A) advertisement on battery |
| Instrumentation | vcc3v3_sys | INA236 power-down mode (I2C) | OpenDAP OS | power-down | — | Shunts stay in circuit |

## 6. Sequencing

### 6.1 System power-up

1. A battery is present (or VBUS / powerbank HAT on TPS2121) → BQ25895 regulates VSYS: ≥ 3.5 V (VSYSMIN) only while an input source is present; on battery alone VSYS follows VBAT less the BATFET drop and can sit near 3.0 V.
2. Power button → RK809 PWRON. RK809-5 runs its OTP sequence. RK809-1 defaults (datasheet Table 4-1) step every 2 ms: BUCK5 (1) → BUCK1, BUCK2, LDO3 (2) → LDO1, LDO2 (3) → BUCK3 (4) → BUCK4, LDO4–6 (5). **The RK809-5 OTP table is UNVERIFIED** and must be read from Rockchip's RK3566 hardware design guide before the rail mapping is frozen.
3. vcc3v3_sys is already up: the TPS62826 (TLV62569 until v1.1) runs from VSYS with EN tied high (BOM v1.1), as the 3.3 V rail of the ROCK 3C runs free, because it feeds RK809 VCC5–VCC9 (always-on LDO3, LDO6, LDO8 and BUCK5). EXT_EN is unused. eMMC VCC is therefore up before the BootROM reads it. Off-state cost: TPS62826 quiescent current (4 µA, SLVSEF9I) plus the RK809 input leakage; ship mode (BATFET off) removes it for storage.
4. RK860-0 vdd_cpu powers up (EN tied per reference design), RESETB releases the SoC.
5. Everything behind a load switch or EN pin stays off until Linux (or U-Boot, for the display) turns it on.

### 6.2 Audio power-up (pop-free)

1. `DAC_VP_EN` (VP first, DS1156F2 §5.2).
2. `DAC_DIG_EN`, `AUDIO_LN_EN`, one `MCLKxx_EN`. Wait for the XO start-up (≤ 4 ms) and LDO settling.
3. Release the CS43198 RESET (≥ 1 ms low pulse already done), program over I2C, keep outputs muted (Popguard).
4. `HPA_RAIL_EN`: TPS65131 ENP and ENN together; once the ±7 V pre-rails settle, `HPA_LDO_EN` raises both LDO EN/UV pins together, so the ±6 V rails ramp on equal RSET × CSET soft-starts, ≈ 65 ms (§4.2, OPA1622 §7.4.2). OPA1622 EN stays low.
5. After the rails are in regulation (a fixed delay: PG is unused because fast start-up is disabled), raise the OPA1622 EN for the selected output only.
6. Unmute with the DAC's soft ramp.

### 6.3 Audio power-down

Reverse order: soft-mute → OPA1622 EN low → rails off → CS43198 RESET low → VA/VCP/VL/VD off in any order (I2S lines parked low first) → VP off last.

### 6.4 HAT

1. Presence detect → `HAT3V3_EN` (TLV62569 then eFuse #B) → read the HAT EEPROM (HCS-007).
2. Apply the overlay. Class A/B: assert `HAT5V_EN` (boost + eFuse #A; the same net forces TPS2121 OV2), within the battery budget of §4.6. Class F (powerbank): keep `HAT5V_EN` low and let TPS2121 select IN2 when USB-C is absent.
3. PCIe PERST# = SoC PERST# AND HAT power-good, released ≥ 100 ms after power-good (topology report §2.3).

### 6.5 Suspend

- Stay on: vdda0v9_pmu, vcca1v8_pmu, vcc3v3_pmu, vcc_ddr + vcc0v6_ddr (self-refresh), RK809 RTC, BQ25895, MAX17055, FUSB302B, IMU (wake on motion), vcc3v3_sys (eMMC stays powered: **open question**, could be dropped if the eMMC power-off notification is used).
- Everything in §5 goes to its default state. The OPA1622, DAC and oscillators are all off, so suspend audio cost is about 0.

## 7. References

Datasheets with revision, date and sha256 are listed once, in the [BOM v1 Datasheets table](bom-v1.md#datasheets). The ones used for calculations here:

- TI OPA1622, SBOS727B (May 2016): <https://www.ti.com/lit/ds/symlink/opa1622.pdf>
- Cirrus Logic CS43198, DS1156F2 (Dec 2022): <https://www.cirrus.com/docs/ds/cs43198-datasheet.pdf>
- Rockchip RK809 datasheet Rev 1.01 (2018-08-28): <https://rockchip.fr/RK809%20datasheet%20V1.01.pdf>
- TI TPS65131, SLVS493E (Apr 2022): <https://www.ti.com/lit/ds/symlink/tps65131.pdf>
- TI LM27762, SNVSAF7C (Oct 2025): <https://www.ti.com/lit/ds/symlink/lm27762.pdf>
- TI TPS7A49, SBVS121E (May 2015): <https://www.ti.com/lit/ds/symlink/tps7a49.pdf> (part removed in v1.3)
- TI TPS7A30, SBVS125D (Jun 2015): <https://www.ti.com/lit/ds/symlink/tps7a30.pdf> (part removed in v1.3)
- ADI LT3045, Rev. D (Nov 2022), and LT3094, Rev. B (Jan 2020), read through the LCSC mirror (BOM Datasheets table) (v1.3)
- TI TPS62826, SLVSEF9I (Mar 2024), Table 8-5 (v1.3 inductor): <https://www.ti.com/lit/ds/symlink/tps62826.pdf>
- TI TPS7A20, SBVS338H (Jul 2024): <https://www.ti.com/lit/ds/symlink/tps7a20.pdf>
- TI TPS7A94, SBVS336C (Jun 2023): <https://www.ti.com/lit/ds/symlink/tps7a94.pdf>
- TI TPS62840, SLVSEC6D (Mar 2020): <https://www.ti.com/lit/ds/symlink/tps62840.pdf>
- TI TPS61169, SNVSA40B (Jun 2024): <https://www.ti.com/lit/ds/symlink/tps61169.pdf>
- TI TPS25947, SLVSFC9C (May 2026): <https://www.ti.com/lit/ds/symlink/tps25947.pdf>
- TI TPS2121, SLVSEA3F (Aug 2020): <https://www.ti.com/lit/ds/symlink/tps2121.pdf>
- TI BQ25895, SLUSC88C (Oct 2022): <https://www.ti.com/lit/ds/symlink/bq25895.pdf>
- TI TPS7A10, SBVS314B (Oct 2018): <https://www.ti.com/lit/ds/symlink/tps7a10.pdf>
- TI TVS2200, SLVSED5C (Aug 2023): <https://www.ti.com/lit/ds/symlink/tvs2200.pdf>
- NDK NZ2520SDA catalog 1703A: <https://www.ndk.com/images/products/catalog/c_NZ2520SDA_e.pdf>
- Focus LCDs E35GH-I-MW800-CB spec rev 1.0: <https://focuslcds.com/wp-content/uploads/2025/09/E35GH-I-MW800-CB_Spec.pdf>
- Raspberry Pi, Hardware design with RP2350 (build 2026-08-20): <https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf>
- Reference designs: Radxa ZERO 3W schematic v1.12 <https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf>; mainline DTs [`rk3566-orangepi-3b.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-orangepi-3b.dtsi) (RK809 + SYR827) and [`rk3566-anbernic-rgxx3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-anbernic-rgxx3.dtsi) (RK817 + FAN53555-class vdd_cpu, handheld battery power), read 2026-10-22.
- BOM v1.1 additions: TI TPS61089, SLVSD38C (Aug 2021): <https://www.ti.com/lit/ds/symlink/tps61089.pdf>; Radxa ROCK 3C schematic v1.4 (2024-03-05, RK809-5): <https://dl.radxa.com/rock3/docs/hw/3c/v1400/radxa_rock_3c_v1400_schematic.pdf>; mainline [`rk3566-rock-3c.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-rock-3c.dts) and [`rk3566-odroid-m1s.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-odroid-m1s.dts), read 2026-10-22; JST PH catalog (ePH): <https://www.jst-mfg.com/product/pdf/eng/ePH.pdf>.
- Not retrieved this session: Rockchip RK3566 hardware design guide and reference schematic, Pine64 Quartz64/SOQuartz schematics, Cirrus CDB43198 eval board, TI BQ25895 EVM guide, onsemi FUSB302B app note, ADI MAX17055 EV kit, Murata Type 2EL hardware guide. Their content is not used above.

## 8. Open questions

1. **BRD-023 frequencies:** closed (22.5792/24.576 MHz, BRD-023 corrected).
2. **Output targets:** closed in v1.3 by ADR 0012 (segment output into low-impedance headphones; paralleled halves on every package, §4.1).
3. **MCLK:** stocked 3.3 V NSC5083D with a passive attenuator into the 1.8 V XTI input (ADR 0010); SPICE check pending.
4. **RK809-5 OTP sequence:** confirm with Rockchip (or the RK3566 hardware design guide) the OTP defaults. VCC5–VCC9 on vcc3v3_sys follows the ROCK 3C v1.4 (RK809-5) and three mainline device trees; feeding VCC1–VCC4 from VSYS follows the datasheet application circuit only.
5. **Is the NPU supply separate on the RK3566 (BUCK4) or shared with the GPU** as on RK817 handhelds? This decides whether BUCK4 is free.
6. **RP2354A power default:** on at boot (always-available orchestrator) or off until OpenDAP OS enables it (lowest standby)?
7. **Backlight driver location:** main board (proposed, keeps faceplates passive) or on each faceplate?
8. **HAT power classes and the battery (v1.2):** the board carries the full output budget (§4.6–4.7); the interim pack still leaves about 0.4 A at 5.1 V on battery. ADR 0011 (Proposed) sets the pack criteria; no stocked pack meets them yet. Accept ADR 0011 and its budget definition, and choose a fallback if no pack is found.
9. **eMMC power in suspend:** keep vcc3v3_sys on, or power the eMMC down in suspend?
10. **HP-amp +5 V LDO (v1.2):** closed in v1.3 by ADR 0012 (LT3045/LT3094 at ±6 V, 55 %).
11. **TPS65131 inverter (v1.3, ADR 0012 condition):** simulate at VIN 3.0 V, ±7 V, 275 mA per rail before layout freeze, or replace the inverter (§4.10.1).
12. **Headphone and HAT power on an ADR 0011 pack (v1.3):** budget them together, or grow the full output budget (§4.11)?

## 9. Risks

1. **SoC power is unmeasured.** The 450–800 mW SoC estimate dominates the runtime figure; a ±30 % error moves runtime by hours. *Mitigation:* measure on a Radxa ZERO 3W or Quartz64 with mainline 7.2 and the INA236 plan.
2. **RK809-5 OTP defaults unknown.** A wrong mapping can put a wrong voltage on a rail at boot. *Mitigation:* the VCC feeds and rail names copy the ROCK 3C v1.4 (RK809-5); confirm the OTP table with Rockchip.
3. **TPS65131 output current at low battery** is read from a curve, not a table, and v1.3 puts the inverter at 79 % of its minimum switch limit at VIN 3.0 V. *Mitigation:* SPICE/WEBENCH at VIN = 3.0 V, ±7 V, 275 mA per rail (ADR 0012); the interim ceiling of §4.11 lowers the load on the Adafruit 328; a converter with more margin is the fallback.
4. **OPA1622 parallel halves** (v1.3: every package) are not described by TI. *Mitigation:* simulate current sharing and stability with the 1.0 Ω ballast and 400 pF loads (TINA-TI model availability **UNVERIFIED**), then measure maximum power, THD+N and output impedance on the first board (research §6).
5. **VBUS surge coordination:** TVS2200 clamp at 40 A (28.4 V) is above the TPS2121 (24 V) and BQ25895 (22 V) absolute maxima. *Mitigation:* decide whether IEC 61000-4-5 applies to the USB-C port; if it does, add series OVP or choose a lower-clamp TVS with a 14 V standoff and accept the 20 V fault case.
6. **Self-feeding loops** through TPS2121 IN1/IN2 when the T1 sources 5 V. *Mitigation:* hardware OR of `USB_SRC_ON`/`HAT_SRC_ON` into OV1/OV2 (finding 11); verify the OV pin drive levels against SLVSEA3F.
7. **MCLK attenuator** (ADR 0010): the edge at XTI must stay within the VL input limits. *Mitigation:* SPICE with the CS43198 input capacitance before layout freeze; J-test captures on the first boards.
8. **Battery current limit** (1.6 A, JST PH derated for 26 AWG, interim pack). *Mitigation:* software power budget on the VSYS INA236 and, from v1.2, a 2.5 A fuse; screen-on + CPU peak + HAT load must be measured; a pack meeting ADR 0011 for the full budget.
9. **0.6 V LPDDR4X rail sizing** is an estimate. *Mitigation:* Rockchip guide, Radxa/Firefly LPDDR4X schematics.
10. **Thermal:** RK3566 + RK809 + RK860 + charger in a 25 mm sealed body; not modelled. *Mitigation:* thermal simulation once the board outline exists.
11. **vcc3v3_sys peak** (1.85 A est.): closed in v1.2 by the 3 A TPS62826 (62 %). *Mitigation:* re-sum from the schematic; the 4 A TPS62827 is pin- and BOM-compatible.
12. **Ratings not yet published** for the RK860-0 and the RK809 BUCK1–4 peak loads of the RK3566 (§4.10). *Mitigation:* measure on a reference board; RK860 datasheet from Rockchip.
13. **Interim-pack output ceiling** depends on OpenDAP OS (§4.11). *Mitigation:* the 2.5 A battery fuse still bounds a software failure (§4.7); the ceiling acts on the measured VSYS current.
