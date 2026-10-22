# Power tree v0

- **Status:** Draft. Desk design only: nothing here has been built, simulated or measured. Every part is *Proposed* unless [BOM v1](bom-v1.md) says *Decided*. Updated 2026-10-22 by the [BOM v1 cross-validation](../research/2026-10-bom-v1-cross-validation.md) (battery, HAT/USB 5 V source, TPS2121 isolation, faceplate rails, IO voltages, vdd_cpu part).
- **Date:** 2026-10-22
- **Companion:** [BOM v1](bom-v1.md) (parts, stock, datasheet links and hashes).
- **Inputs:** [BOM v0](bom-v0.md), [board requirements](../requirements/README.md) (BRD-001 to BRD-048), board ADRs 0001–0004, [component selection](../research/2026-10-component-selection.md), [sourcing alternatives](../research/2026-10-sourcing-alternatives.md), [high-speed I/O topology](../research/2026-10-high-speed-io-topology.md), [battery selection](../research/2026-10-battery-selection.md), touch-faceplate ADR 0001 (Focus E35GH), T1 and HAT Case Standard requirements, opendap-os ADRs 0006–0008. [pin multiplexing v0](../research/2026-10-pin-multiplexing-v0.md) gives the balls; GPIO names below are logical names.
- **Method:** datasheets were downloaded and read (revision and sha256 in the BOM's Datasheets table); the RK809 rail mapping follows mainline device trees of shipping RK3566 boards (Orange Pi 3B with RK809, Anbernic RG353 with RK817, Radxa ZERO 3W schematic v1.12). Calculations are shown inline.
- **Conventions:** **UNVERIFIED** = no primary source found in this session. "Est." = engineering estimate, to be replaced by measurement (T1-026).

## 1. Findings that change earlier drafts

1. **The CS43198 does not accept a 45.1584 or 49.152 MHz master clock.** Its datasheet (DS1156F2, §4.6 and Table 3-13) allows an external MCLK only at the nominal internal frequencies **22.5792 MHz and 24.576 MHz** (or PLL references 9.6–26 MHz). BRD-023 (Draft) and BOM v0 lines 9–10 name 45.1584/49.152 MHz. Proposal: **22.5792 MHz and 24.576 MHz NDK NZ2520SDA**, which keeps the intent of BRD-023 (two families, DAC as clock master, no resampling). A divide-by-two flip-flop would also work but adds a part and jitter in the clock path, against BRD-042.
2. **The CS43198 also needs a battery-class supply, VP = 3.0–5.25 V** (charge-pump supply for its output stage), plus four 1.8 V rails (VA, VCP, VD, VL). VP must come up first and go down last (DS1156F2 §5.2).
3. **The MCLK oscillator must run at 1.8 V**, because XTI/MCLK is in the VL (1.8 V) domain. The stocked NDK spec numbers are the 3.3 V ones (NSC5083D); the 1.8 V spec is NSC5083A, which is not listed at Digi-Key (quote needed, see BOM).
4. **The LM27762 cannot make ±5 V from a 1S battery.** Its positive output is an LDO from VIN, so at VSYS = 3.5 V the positive rail is at most about 3.45 V (calculation in §4.2). The proposed generator is a **TPS65131** dual boost/inverter followed by **TPS7A4901 / TPS7A3001** LDOs.
5. **The TPS7A94 is unsuitable for a battery device here:** 15 mA typical ground current at 5.1 V out (SBVS336C, Electrical Characteristics), that is about 80 mW wasted.
6. **The RK809-5 must be used with the reference rail mapping.** Its regulators come up at OTP default voltages before Linux runs. The mapping below copies the mainline Orange Pi 3B device tree (RK3566 + RK809), including an external 3.3 V buck that feeds the RK809 switch input, so no rail starts at a wrong voltage.
7. **LPDDR4X needs a separate 0.6 V VDDQ rail.** The Radxa ZERO 3W schematic table gives VDDQ 1.10 V and VDDQL 0.60 V for LPDDR4X, with a 0 Ω option (R122) that ties VCC0V6_DDR to VCC_DDR only for plain LPDDR4.
8. **The battery path is limited to 2.0 A continuous** (cross-validation). The pack is the Adafruit 328 (ADR 0007): its sheet allows ≤ 2C discharge, but its 2-pin JST PH lead and the board's S2B-PH header are rated 2 A per contact. VSYS on battery is therefore budgeted at 2.0 A (≈ 7 W at 3.5 V), not 3.5 A.
9. **The BQ25895 cannot supply OTG while it charges.** The draft fed HAT_5V and the USB-C source from the OTG boost, so a class A/B HAT lost 5 V whenever USB-C power was plugged in. HAT_5V and USB-C VBUS out now come from a **TPS61088 boost from VSYS** (5.1 V) behind eFuses #A and #C.
10. **The T1's own 5 V must not re-enter the charger.** When the T1 sources USB-C VBUS, that VBUS is also TPS2121 IN1; when it sources HAT_5V, that net is IN2. Both OV inputs are forced high by hardware OR of the source enables (`USB_SRC_ON`, `HAT_SRC_ON`), not by software order.
11. **IO voltages follow the pin plan:** I2C0/1/2 on PMUIO2 at 1.8 V (the CS43198 control port shares the bank and is 1.8 V-only); the faceplate bank VCCIO5 at 3.3 V.
12. **No stocked 1.8 V audio-grade MCLK oscillator exists today** (BOM lines 20–21, blocker). The MCLK_1V8 rail and its LDO stay; the oscillator current below is the NZ2520SDA figure.
13. **Debian already enables the INA236 current monitor** through the IIO `ina2xx-adc` driver (`CONFIG_INA2XX_ADC=m`, compatible `ti,ina236`), while the hwmon INA2xx/INA238 drivers are off. The instrumentation uses INA236.

## 2. Power tree (text diagram)

Currents are design maxima (max) and estimated screen-off playback values (play). Arrows point from source to load.

```text
USB-C VBUS 5-12 V (PD sink, FUSB302B) --[TVS2200]--+
                                                   +--> TPS2121 IN1 (priority) --+
HAT_5V pins (powerbank HAT, class F) --[TVS0500]---+--> TPS2121 IN2 (OV2 gate) --+--> VBUS_CHG
                                                                                  |
VBUS_CHG --> BQ25895 (buck charger 1.5 MHz; OTG boost NOT used)                   |
   |   TPS2121 OV1 forced by USB_SRC_ON, OV2 forced by HAT_SRC_ON (hardware OR)    |
   |                                                                              |
   +--> BAT  <--> Adafruit 328, 1S 2,500 mAh, JST PH 2-pin (2 A per contact)
   |            MAX17055 gauge, 10 mohm sense, board NTC on TS
   +--> VSYS 3.5-4.4 V (VSYSMIN 3.5 V)   on battery max 2.0 A; on adapter max 3.5 A; play 0.20-0.30 A (est.)
          |
          +--> RK809-5 PMIC (VCC1-8 from VSYS)
          |      BUCK1 vdd_logic   0.90 V  2.5 A max   play ~0.30 A (est.)
          |      BUCK2 vdd_gpu     0.90 V  2.5 A max   off with GPU idle (DT)
          |      BUCK3 vcc_ddr     1.10 V  1.5 A max   play ~0.10 A (est.)
          |         +--> TPS7A1006 vcc0v6_ddr 0.60 V 0.3 A max (LPDDR4X VDDQ), play ~0.03 A
          |      BUCK4 vdd_npu     0.90 V  1.5 A max   OFF unless NPU used
          |      BUCK5 vcc_1v8     1.80 V  2.5 A max   play ~0.10 A (est.)
          |         +--> TPS22919 DAC_DIG_1V8  (2x VD+VL+VCP)       13 mA
          |         +--> TPS22919 FP_1V8 (panel IOVCC, faceplate translator low side) ~5 mA
          |         +--> TPS22919 MIC_1V8 (2x IM73D122 + privacy LED gate) ~2 mA
          |         +--> TPS22919 RP_IOVDD_1V8 (RP2354A IOVDD)
          |         +--> IMU, eMMC VCCQ, IW612 VIO, LPDDR4X VDD1, SoC VCCIO 1.8 V banks
          |      LDO1 vdda0v9_image 0.9 V (CSI D-PHY, camera HAT only)
          |      LDO2 vdda_0v9      0.9 V (USB/PCIe/DSI PHY)
          |      LDO3 vdda0v9_pmu   0.9 V (always on)
          |      LDO4 FP_VCI        2.8 V (panel VCI; adjustable per faceplate in DT) [codec IO rail on OPi3B; codec unused]
          |      LDO5 vccio_sd      1.8/3.3 V (microSD signalling)
          |      LDO6 vcc3v3_pmu    3.3 V (always on: PMUIO2, FUSB302B)
          |      LDO7 vcca_1v8      1.8 V (PLL, PHY analog)
          |      LDO8 vcca1v8_pmu   1.8 V (always on)
          |      LDO9 vcca1v8_image 1.8 V (CSI D-PHY, camera HAT only)
          |      EXT_EN ----------------------------+
          |      VCC9 <-- vcc3v3_sys                |
          |      SWOUT1 vcc3v3_wl  (IW612 VBAT)     |   max 0.6 A (est.), off when radio off
          |      SWOUT2 vcc3v3_sd  (microSD VDD)    |   max 0.2 A
          |      RTC + 32.768 kHz crystal           |
          +--> TLV62569 vcc3v3_sys 3.3 V 2 A <------+ (EN = RK809 EXT_EN)  play ~0.05 A
          |         +--> eMMC VCC, RK809 VCC9, TPS22919 RP_3V3 (RP2354A), TCA6416A VCCP, PCA9306 / AXC B side
          |         +--> TPS22919 FP_3V3 (CTP VDD, ALS, faceplate logic, status/privacy LEDs) ~80 mA
          +--> RK860-0 vdd_cpu 0.80-1.15 V (I2C DVS)   max 3 A (est.), play ~0.15 A (est.)
          +--> TPS22919 DAC_VP (CS43198 VP x2)           0.1 mA play, VP first/last
          +--> TPS62840 AUDIO_2V2 2.2 V 750 mA max        play 31 mA
          |         +--> TPS7A2018 DAC1_VA 1.8 V    7.8 mA
          |         +--> TPS7A2018 DAC2_VA 1.8 V    7.8 mA
          |         +--> TPS7A2018 MCLK_1V8 1.8 V  15 mA (one NZ2520SDA active, other in standby)
          +--> TPS65131 AUDIO_P6V0 +6.0 V / AUDIO_N6V0 -6.0 V
          |         +--> TPS7A4901 +5.0 V  150 mA max, play 10-40 mA
          |         +--> TPS7A3001 -5.0 V  200 mA max, play 10-40 mA
          |                  +--> 4x OPA1622 (only the selected output's 2 packages enabled)
          +--> MAX98357A speaker amp (VDD = VSYS, SD_MODE shutdown)
          +--> TPS61169 backlight boost, LEDA up to 16.5 V, ILED 60 mA max (5S2P, 10 LEDs)
          +--> TLV62569 HAT_3V3 3.3 V 2 A --> TPS259470 #B (ILIM 1.0 A) --> HAT_3V3
          +--> TPS61088 boost 5.1 V (EN = HAT5V_EN OR USB_SRC_ON)
          |         +--> TPS259470 #A (ILIM 1.5 A) --> HAT_5V out   (on battery: budgeted, §4.6)
          |         +--> TPS259470 #C (ILIM 1.5 A) --> USB-C VBUS source (0.5 A default on battery)
          +--> MAX17055 gauge (powered from BAT)
```

## 3. Rail table

| Rail | Source | Voltage | Max current (design) | Screen-off playback (est.) | Gated by | Loads |
|---|---|---|---|---|---|---|
| VBUS_CHG | TPS2121 OUT | 5–12 V | 3.25 A input limit | 0 (battery) | TPS2121 priority, OV pins | BQ25895 VBUS |
| VSYS | BQ25895 SYS | 3.5–4.4 V | 2.0 A on battery (JST PH contact rating); 3.5 A on adapter | 0.20–0.30 A | BATFET ship mode | everything below |
| vdd_cpu | RK860-0 | 0.80–1.15 V | 3 A (est.) | 0.15 A (est.) | RK860 EN + DVS | RK3566 CPU |
| vdd_logic | RK809 BUCK1 | 0.90 V | 2.5 A | 0.30 A (est.) | off in suspend | RK3566 logic |
| vdd_gpu | RK809 BUCK2 | 0.90 V | 2.5 A | ~0 (GPU idle) | DT regulator | GPU (and NPU if tied) |
| vcc_ddr | RK809 BUCK3 | 1.10 V | 1.5 A | 0.10 A (est.) | on in suspend | LPDDR4X VDD2, SoC DDR VDDQ |
| vdd_npu | RK809 BUCK4 | 0.90 V | 1.5 A | 0 | DT, off by default | NPU |
| vcc_1v8 | RK809 BUCK5 | 1.80 V | 2.5 A | 0.10 A (est.) | off in suspend | IO banks, eMMC VCCQ, VDD1, sub-switches |
| vcc0v6_ddr | TPS7A1006 (from vcc_ddr) | 0.60 V | 0.3 A | 0.03 A (est.) | follows vcc_ddr | LPDDR4X VDDQ, SoC VDDQL |
| vcc3v3_sys | TLV62569 | 3.30 V | 2 A | 0.05 A | RK809 EXT_EN | eMMC VCC, RK809 VCC9 (SWOUT1/2), RP2354A, FP_3V3, expander and translators (peak ≈ 1.3 A est.) |
| vcc3v3_wl | RK809 SWOUT1 | 3.30 V | 3 A switch | 0 (radio off) | RK809 I2C | IW612 module VBAT (UNVERIFIED 3.3 V) |
| vcc3v3_sd | RK809 SWOUT2 | 3.30 V | 1.5 A switch | 0–0.1 A | RK809 I2C | microSD VDD |
| FP_VCI | RK809 LDO4 | 2.80 V (DT-adjustable) | RK809 LDO4 rating (**UNVERIFIED**) | 0 (screen off) | RK809 I2C | panel VCI |
| FP_3V3 | TPS22919 (vcc3v3_sys) | 3.30 V | 1.5 A switch | 0 (screen off) | `FP_IO_EN` | CTP VDD, ALS, faceplate logic, LEDs |
| FP_1V8 | TPS22919 (vcc_1v8) | 1.80 V | 1.5 A switch | 0 (screen off) | `FP_IO_EN` | panel IOVCC, faceplate translators |
| DAC_VP | TPS22919 (VSYS) | 3.5–4.4 V | 1.5 A switch | 0.06 mA | `DAC_VP_EN` | 2× CS43198 VP |
| DAC_DIG_1V8 | TPS22919 (vcc_1v8) | 1.80 V | 1.5 A switch | 13.2 mA | `DAC_DIG_EN` | 2× CS43198 VD, VL, VCP |
| AUDIO_2V2 | TPS62840 | 2.20 V | 0.75 A | 31 mA | `AUDIO_LN_EN` | three TPS7A2018 |
| DACx_VA | TPS7A2018 ×2 | 1.80 V | 0.3 A | 7.8 mA each | `AUDIO_LN_EN` | CS43198 VA |
| MCLK_1V8 | TPS7A2018 | 1.80 V | 0.3 A | 15 mA | `AUDIO_LN_EN` | 2× NZ2520SDA (one in standby) |
| AUDIO_P6V0 / N6V0 | TPS65131 | +6.0 / −6.0 V | 0.2–0.5 A each (Vin-dependent) | 12–45 mA each | `HPA_RAIL_EN` (ENP, ENN) | LDOs below |
| HPA_P5V0 | TPS7A4901 | +5.0 V | 0.15 A | 10–40 mA | `HPA_RAIL_EN` | OPA1622 V+ |
| HPA_N5V0 | TPS7A3001 | −5.0 V | 0.2 A | 10–40 mA | `HPA_RAIL_EN` | OPA1622 V− |
| BL_LEDA | TPS61169 | 13–16.5 V | 60 mA | 0 (screen off) | `BL_PWM` (CTRL, 1 µA off) | panel LED string |
| HAT_3V3 | TLV62569 → TPS259470 #B | 3.30 V | 1.0 A (ILIM) | 0 | `HAT3V3_EN` | HAT |
| HAT_5V (out) | TPS61088 → TPS259470 #A | 5.1 V | 1.5 A (ILIM); on battery per §4.6 budget | 0 | `HAT5V_EN` (also forces TPS2121 OV2) | HAT class A/B |
| USB-C VBUS (out) | TPS61088 → TPS259470 #C | 5.1 V | 1.5 A (ILIM); 0.5 A advertised on battery | 0 | TCPM source role → `USB_SRC_ON` (also forces OV1) | USB host mode |

## 4. Calculations

### 4.1 Headphone amplifier rails (OPA1622)

**Targets** (proposed, to confirm with the maintainers):

- 4.4 mm balanced: 4.0 Vrms differential, i.e. 2.0 Vrms per leg (the CS43198 full-scale 2 Vrms per output, gain 1).
- 3.5 mm single-ended: 2.0 Vrms into high-impedance loads; current-limited into 16–32 Ω.

**Voltage headroom.** OPA1622 output swing to the rail is 0.8 V with no load and 0.9 V at 600 Ω (SBOS727B, §6.5); it grows with current (Figure 38, not tabulated). Use 1.0 V at 20–100 mA as the design figure (**UNVERIFIED** from the curve).

| Case | Peak voltage per leg | Peak current | Rail needed | Margin at ±5.0 V |
|---|---|---|---|---|
| Balanced, 300 Ω, 4.0 Vrms diff | 2.0 × √2 = 2.83 V | 5.66 V / 300 Ω = 18.9 mA | ±3.83 V | 1.17 V |
| Balanced, 32 Ω, 2.0 Vrms diff (125 mW) | 1.41 V | 2.83 V / 32 Ω = 88 mA | ±2.41 V | 2.59 V (current-limited first) |
| SE, 600 Ω, 2.0 Vrms | 2.83 V | 4.7 mA | ±3.83 V | 1.17 V |
| SE, 32 Ω, 2.0 Vrms (125 mW) | 2.83 V | 88 mA | ±3.83 V | 1.17 V |
| SE, 16 Ω, 1.23 Vrms (95 mW, datasheet limit at ±5 V) | 1.74 V | 109 mA | ±2.74 V | 2.26 V |

- **Current limit, not voltage, caps low-impedance loads.** TI's own ±5 V headphone example (SBOS727B, Table 2) reaches 95 mW into 16 Ω and 150 mW into 32 Ω, both limited by output current (109 mA and 97 mA peak). Short-circuit current is +145/−130 mA.
- **Why four OPA1622:** two packages per output. 4.4 mm: one package per channel drives L+ and L− (R+ and R−). 3.5 mm: one package per channel, its two halves paralleled through small ballast resistors (about 0.5–1 Ω, inside the feedback loop) for about twice the current into 16 Ω (**UNVERIFIED**, needs simulation; the alternative is one half per channel and the other package unpopulated).
- **±5.0 V is the minimum that meets the balanced 4 Vrms target with 1 V of margin.** It is also what TI characterises.

**Supply current per rail** (sine, both channels driven; a rail supplies one half-cycle, average Ipk/π per leg):

- Quiescent: 2 active packages × 2 channels × 2.6 mA = **10.4 mA** per rail (3.3 mA max per channel, 5 µA in shutdown).
- SE 32 Ω, 2 Vrms both channels: 2 × 88 mA / π = 56 mA + 10.4 = **67 mA** per rail.
- Balanced 32 Ω, 2 Vrms diff both channels: the load current alternates between the + and − legs, so V+ supplies |i| on both half-cycles: 2 channels × 2 × 88 mA / π = 112 mA + 10.4 = **122 mA** per rail.
- Design rail rating: **150 mA** (TPS7A4901 limit), which covers the worst continuous sine case (122 mA). Music averages are far lower; the balanced output into 32 Ω at full level is the case to watch.

**Thermal** (OPA1622 DRC, θJA 47.6 °C/W): worst case per channel, symmetric ±5 V into 16 Ω, Pmax = 2·Vs²/(π²·RL) = 2 × 25 / (9.87 × 16) = 0.32 W, but the 109 mA current limit holds it near 0.25 W per channel, about 0.5 W per package → +24 °C rise. Acceptable with the exposed pad soldered to a ground pour.

### 4.2 Rail generator choice

| Option | Positive rail at VSYS = 3.5 V | Negative rail | Parts | Verdict |
|---|---|---|---|---|
| LM27762 alone (SNVSAF7C) | LDO from VIN: ≤ 3.5 − 0.045 = 3.45 V → swing 2.45 Vpk → 1.7 Vrms per leg | −VIN via charge pump, then LDO | 1 | **Rejected:** fails 4 Vrms balanced (needs 3.83 V) |
| Boost to 5.5 V + LM27762 | 5.0 V | −5.0 V | 2 + boost passives | Possible second option; LM27762 has the best stock (LCSC 41,293), 22 µVrms noise, 250 mA |
| TPS63710 inverter + boost | — | \|VOUT\| < 0.7 × VIN → max −2.45 V at 3.5 V in | 2 | **Rejected** for the negative rail |
| **TPS65131 + TPS7A4901 + TPS7A3001** | +6.0 → +5.0 V | −6.0 → −5.0 V | 3 | **Proposed**: one IC makes both pre-rails from 2.7–5.5 V, 1 µA shutdown, power-save per output (PSP/PSN) |

TPS65131 (SLVS493E): input 2.7–5.5 V, 1.25 MHz, maximum output current "200 mA to 500 mA range, depending on input-to-output voltage ratio". At VIN = 3.5 V and ±6 V the curve (Figure 6-2) has to be read from the plot; the need is ≤ 150 mA per rail (**UNVERIFIED** margin until simulated).

**Ripple and PSRR chain** (assume 20 mVpp switching ripple on each pre-rail, **UNVERIFIED** until the output capacitors are sized):

- Forced PWM (PSP = PSN = 0): ripple at 1.25 MHz, outside the audio band. TPS7A4901 PSRR ≥ 52 dB up to 400 kHz (≥ 40 dB assumed at 1.25 MHz) → ≤ 0.2 mVpp at the OPA1622. Add a ferrite bead + 10 µF π-filter before each LDO for another 20 dB.
- Power-save (PFM bursts can land in the audio band): TPS7A4901 72 dB at 120 Hz → 20 mV × 10^(−72/20) = 5 µV; the OPA1622 PSRR is 0.1 µV/V typ at DC (−140 dB); even at an assumed −100 dB in band, the residue is 0.05 nV, far below the DAC floor (0.63 µVrms, §4.3). **Conclusion: power-save mode can stay enabled during playback**, which matters for battery life. Verify by measurement.

**LDO headroom and dissipation:**

| LDO | In → out | Dropout (datasheet) | Headroom | Pd at 67 mA | Pd at 150 mA |
|---|---|---|---|---|---|
| TPS7A4901 (SBVS121E) | +6.0 → +5.0 V | 260 mV at 100 mA | 1.0 V | 67 mW | 150 mW |
| TPS7A3001 (SBVS125D) | −6.0 → −5.0 V | 216 mV at 100 mA | 1.0 V | 67 mW | 150 mW |

Ground currents: TPS7A4901 about 800 µA at 100 mA; TPS7A3001 55 µA at no load, 950 µA at 100 mA. 1 V of headroom keeps PSRR on its rated curve; reducing it to 0.5 V saves 10 mW per rail at the quiescent load.

**Rejected positive LDOs:** TPS7A94 (15 mA ground current, §1); TPS7A2050 (7 µVrms, 6.5 µA Iq, better on paper, but VIN absolute maximum is 6.0 V, so the pre-rail would have to sit at ≤ 5.5 V with no overshoot margin; kept as an option if the pre-rail is set to +5.4 V).

### 4.3 DAC analog rails: noise budget versus PSRR

- DAC noise floor: 130 dB A-weighted dynamic range re 2 Vrms → 2 × 10^(−130/20) = **0.63 µVrms**.
- CS43198 VA PSRR: 75 dB at 217 Hz (DS1156F2, Table 3-15; the only point given).
- TPS7A2018 output noise 7 µVrms (SBVS338H). Coupled to the output: 7 µV × 10^(−75/20) = **1.2 nV**, 54 dB below the floor. Even with PSRR falling to 40 dB at 20 kHz: 70 nV, still 19 dB below.
- **Conclusion:** an ultra-low-noise LDO (LT3042 class, 0.8 µVrms, about 2 mA Iq) buys nothing measurable on VA; the TPS7A2018 costs 6.5 µA quiescent and $0.26. One LDO per DAC keeps dual mono independent.

**DAC power (Table 3-17, PCM playback, VA = VCP = VD = VL = 1.8 V, VP = 3.6 V):** VCP 3.808 mA, VA 7.835 mA, VD 2.786 mA, VP 0.028 mA, **26.1 mW per DAC**. Standby (HP detect on) 0.58 mW; off (VP only) 11 µW.

**Efficiency of the 1.8 V analog path** (two DACs' VA = 15.7 mA plus MCLK 15 mA = 30.7 mA at 1.8 V = 55 mW):

| Feed | Chain efficiency | Battery power |
|---|---|---|
| LDO straight from VSYS (3.8 V) | 1.8 / 3.8 = 47 % | 117 mW |
| TPS62840 2.2 V (~90 %, **UNVERIFIED** at 31 mA) + LDO (1.8 / 2.2 = 82 %) | 74 % | 75 mW |

The pre-buck saves about **42 mW**, roughly 4–6 % of screen-off playback power. TPS62840 has 60 nA Iq and 25 nA shutdown (SLVSEC6D).

### 4.4 Master clocks

- NZ2520SDA: 15 mA operating, 35 µA standby, **tri-state output in standby** (NDK catalog 1703A). Both oscillator outputs can therefore share one MCLK net to the two DACs, with exactly one enabled: no clock multiplexer in the path.
- Phase noise at 1.8 V: 22.5792 MHz −158 dBc/Hz at 1 kHz, −163 at 100 kHz; at 3.3 V −164 / −169 (NDK catalog). The 1.8 V version is about 6 dB worse close-in; it is still an audio-grade XO (the CS43198 PLL, which is bypassed here, only asks for < 50 ps reference jitter). Whether the 6 dB is audible or measurable is for the A/B measurement in the sourcing report §4.
- Power: 15 mA × 1.8 V = 27 mW for the active oscillator (36 mW from the battery through the pre-buck). The idle family costs 35 µA.

### 4.5 Backlight (Focus E35GH-I-MW800-CB)

From the Focus spec sheet (rev 1.0): 10 LEDs, edge-lit, IF 60 mA, VF 14.0 / 15.0 / 16.5 V (min/typ/max), so 5 in series × 2 parallel strings, single LEDA/LEDK pair. Panel VCI 2.5–3.3 V (2.8 V typ), IOVCC 1.65–3.3 V (1.8 V typ). CTP normal current 8 mA typ, 14.5 mA max.

TPS61169 (SNVSA40B): 2.7–5.5 V in, 1.2 MHz, 1.2 A minimum switch limit, 204 mV reference, 37.5 V OVP, 1 µA shutdown.

- Sense resistor: R = 0.204 V / 0.060 A = **3.40 Ω** (1 %, 12 mW).
- Full brightness: Pout = 16.5 V × 60 mA = 0.99 W (max VF). At VIN = 3.5 V and η = 85 %: Iin = 0.99 / (3.5 × 0.85) = 0.33 A.
- Duty cycle: D = 1 − VIN·η / VOUT = 1 − 3.5 × 0.85 / 16.5 = 0.82.
- Ripple with L = 10 µH, f = 1.2 MHz: ΔIL = VIN·D / (L·f) = 3.5 × 0.82 / (10 µH × 1.2 MHz) = 0.24 A → peak 0.33 + 0.12 = **0.45 A < 1.2 A**. A 10 µH, ≥ 0.6 A saturation inductor (Murata LQH3NPN100MJRL class) and a 40 V, 1 A Schottky (Nexperia PMEG4010CEH) suffice.
- Indoor 200 nit: about 15 mA if luminance is linear in current (**UNVERIFIED**), VF about 13.5 V (est.) → 0.20 W out, about 0.25 W from the battery. Full 800 nit outdoors: about 1.1 W.
- Dimming: PWM on CTRL scales the internal reference (analog dimming of the LED current, flicker-free), driven by the ALS through OpenDAP OS (`pwm-backlight`, Debian `=m`).
- Placement: on the main board, so the faceplate FPC carries LEDA/LEDK. 37.5 V OVP covers strings up to about 10 series LEDs, so other faceplates need no board change (BRD-048).

### 4.6 HAT power: eFuse current limits and inrush

TPS259470 (SLVSFC9C): 2.7–23 V, RON 28.3 mΩ, ILIM set by RILM (1.65 kΩ → 2.03 A, 3.32 kΩ → 1.007 A, so ILIM ≈ 3,350 Ω·A / RILM), reverse-current blocking, IMON.

| eFuse | Path | ILIM target | RILM (E96) | Conduction loss at ILIM |
|---|---|---|---|---|
| #A | TPS61088 → HAT_5V | 1.5 A | 2.21 kΩ (1.52 A) | 28.3 mΩ × 1.5² = 64 mW |
| #B | TLV62569 → HAT_3V3 | 1.0 A | 3.32 kΩ (1.007 A) | 28 mW |
| #C | TPS61088 → USB-C VBUS | 1.5 A | 2.21 kΩ | 64 mW |

- **Source:** a TPS61088 boost from VSYS feeds #A and #C (the BQ25895 OTG boost cannot run while charging, finding 10). On adapter power only HAT_5V can be sourced (the USB-C port is then the input), so #A at 1.5 A (≈ 8.5 W from VSYS at η ≈ 0.9) fits inside the 3.5 A VSYS rating with the system load. The boost also covers the case the draft missed: a class A/B HAT keeps 5 V while the T1 charges.
- **Battery budget:** on battery the JST PH contact caps the pack at 2.0 A ≈ 7 W at 3.5 V. With the base system at 1–3 W (screen off to screen on with CPU load, **est.**), about 4 W remains: ≈ 0.7 A at 5.1 V for HAT_5V **plus** USB-C source together. OpenDAP OS enforces it with the VSYS INA236 and the eFuse IMON; USB-C advertises Default (0.5 A) on battery. HAT power classes A/B must be written against this number (hat-standard).
- **Hardware ceilings stay** at ILIM 1.5 / 1.0 / 1.5 A so a fault is still bounded if software fails.
- **Inrush:** with CdVdt = 1.8 nF the rising slew is 0.87 V/ms at 2.7 V and 1.09 V/ms at 12 V; take 0.92 V/ms at 5 V. A HAT with 100 µF bulk draws I = C·dV/dt = 100 µF × 920 V/s = **92 mA** for 5.4 ms; 470 µF draws 0.43 A, still under ILIM. The HAT standard should cap HAT bulk capacitance at 470 µF per rail.
- **Powerbank HAT input (class F):** HAT_5V → TPS2121 IN2. When the T1 sources HAT_5V, `HAT_SRC_ON` (the same net that enables #A) drives TPS2121 OV2 high so IN2 cannot connect; when it sources USB-C VBUS, `USB_SRC_ON` drives OV1 high. The interlock is wired, not a software ordering rule.

### 4.7 Charger, battery and input path

- BQ25895: 3.9–14 V input, 5 A charge, 1.5 MHz, 1 µH inductor and ≥ 20 µF on SYS recommended (SLUSC88C §9). PMID capacitance per the datasheet for charge-only use (OTG is not used).
- Battery-only quiescent: 32 µA typ with BATFET on and monitor off (12 µA with BATFET off, ship mode).
- Pack: Adafruit 328 (ADR 0007), spec sheet Q/WAPL785060-1011: charge ≤ 1C (2.5 A) at 0–40 °C and ≤ 4.25 V, discharge ≤ 2C. Charge current 1.2 A (Adafruit's advice), VREG 4.20 V; LiHV packs later at 4.35/4.40 V from the device tree (ADR 0008). The TS thresholds must stop charging above 40 °C (the BQ25895 default hot limit is higher, **UNVERIFIED** exact value).
- Battery current: 2.0 A continuous through the JST PH contact (finding 9).
- Input: PD sink at 9 V, 2 A requested by TCPM → 18 W available against about 7.3 W needed (1.5 A × 4.2 V charge + 1 W system). TPS2121 conduction loss at 2 A input: 56 mΩ × 4 = 0.22 W.
- USB-C VBUS surge: TVS2200 (22 V flat clamp, 28.4 V max at 40 A 8/20 µs). The TPS2121 (24 V absolute maximum, OV1 set at about 14.5 V) sits between the connector and the BQ25895 (22 V absolute maximum). A 40 A surge clamp of 28.4 V exceeds both ratings, so the TVS is sized for ESD and hot-plug ringing, not for an IEC 61000-4-5 surge (**risk**, §9).

### 4.8 LPDDR4X VDDQ (0.6 V)

- TPS7A1006 (SBVS314B): 0.6 V fixed, 300 mA, VIN from vcc_ddr (1.1 V), BIAS from vcc_1v8 (1.7–5.5 V), 70 mV maximum dropout at 300 mA (VOUT > 1.0 V; larger at 0.6 V, still inside the 0.5 V headroom).
- Dissipation at an estimated 0.2 A peak: (1.1 − 0.6) × 0.2 = 0.10 W; efficiency 0.6 / 1.1 = 55 % on a small rail, against about 35 % from vcc_1v8.
- The current figure is **UNVERIFIED**: confirm it and the regulator type against the Rockchip RK3566 hardware design guide (not retrieved this session).

### 4.9 Screen-off playback budget and runtime

| Block | Load at the rail | From the battery | Basis |
|---|---|---|---|
| SoC, LPDDR4X, eMMC, PMIC losses | — | 450–800 mW | **Est., UNVERIFIED** (no RK3566 measurement yet) |
| 2× CS43198 (VA, VCP, VD, VL, VP) | 52 mW | 65 mW | Table 3-17 + chain efficiency |
| Active MCLK oscillator | 27 mW | 36 mW | NDK catalog |
| OPA1622, 2 packages, quiescent | 104 mW | 180 mW | 10.4 mA × 10 V, LDO 1 V headroom, TPS65131 η ≈ 70 % (**UNVERIFIED**) |
| Headphone load, 1 mW per channel | 2 mW | 4 mW | — |
| IMU, gauge, TCPC, charger | — | 3 mW | datasheets |
| **Total** | — | **0.74–1.09 W** | — |

- Runtime, 90 % usable energy: Adafruit 328 (9.4 Wh, the only adopted pack, ADR 0007) → **7.8–11.4 h**: above the 6 h red line and mostly above the 8 h warning, below the 12 h ideal (T1-039). The SoC estimate dominates (risk 1). Larger packs are not adopted (T1-038).
- The OPA1622 quiescent current (180 mW from the battery) is the largest audio term. Enabling only the selected output's two packages already halves it; a "single package per output" build option would halve it again at the cost of 16 Ω drive.
- Screen on at 200 nit adds about 0.25 W backlight + 0.05 W panel and touch + GPU/VOP (**UNVERIFIED**, est. 0.2 W).

## 5. Power-gating map

Default state is the state with no software running (pull resistors). "SoC GPIO" means a RK3566 GPIO in a 1.8 V bank unless noted; ball assignment waits for the pin-multiplexing study.

| Block | Rail(s) | Switch / enable | Control | Default | Discharge | Notes |
|---|---|---|---|---|---|---|
| DAC digital (both) | DAC_DIG_1V8 | TPS22919 | SoC GPIO `DAC_DIG_EN` | off (pull-down) | QOD in TPS22919 | Park I2S lines low before removal (back-powering) |
| DAC VP (both) | DAC_VP | TPS22919 | SoC GPIO `DAC_VP_EN` | off | QOD | VP first on, last off |
| DAC analog + clocks | AUDIO_2V2, DACx_VA, MCLK_1V8 | TPS62840 EN, TPS7A2018 EN | SoC GPIO `AUDIO_LN_EN` | off | TPS7A20 smart pulldown, TPS62840 active discharge | — |
| MCLK family select | NZ2520SDA ×2 | ST pin (tri-state) | SoC GPIO `MCLK441_EN`, `MCLK48_EN` | both standby | — | Never both enabled |
| HP amp rails | AUDIO_P6V0/N6V0, HPA_P5V0/N5V0 | TPS65131 ENP/ENN, LDO EN | SoC GPIO `HPA_RAIL_EN` | off | — | Symmetric ramp (OPA1622 §7.4.2) |
| HP amp outputs | per package | OPA1622 EN (×4) | SoC GPIO `HPA_SE_EN`, `HPA_BAL_EN` | low (shutdown, 5 µA/ch) | — | EN low during rail ramps |
| Speaker amp | VSYS | MAX98357A SD_MODE | SoC GPIO `SPK_SD` | shutdown | — | Device shutdown, no extra switch |
| Microphones + privacy LED | MIC_1V8 | TPS22919 | SoC GPIO `MIC_EN` | off | QOD | LED gate driven by MIC_1V8 itself (BRD-027) |
| Faceplate logic | FP_VCI, FP_3V3, FP_1V8 | RK809 LDO4, TPS22919 ×2 | RK809 I2C, expander `FP_IO_EN` | off | QOD | Panel and touch reset low first |
| Backlight | BL_LEDA | TPS61169 CTRL | SoC PWM `BL_PWM` | off (1 µA) | — | ALS-driven |
| Wi-Fi/BT | vcc3v3_wl | RK809 SWOUT1 | RK809 I2C | off | **UNVERIFIED** | Plus module PDn |
| microSD | vcc3v3_sd, vccio_sd | RK809 SWOUT2, LDO5 | RK809 I2C | per DT | **UNVERIFIED** | UHS-I voltage switch |
| RP2354A | RP_3V3, RP_IOVDD_1V8 | TPS22919 ×2 | SoC GPIO `RP_PWR_EN` | **open question** (§8) | QOD | SoC boots without it (BRD-019) |
| NPU | vdd_npu | RK809 BUCK4 | DT | off | — | Enabled only by an AI overlay |
| GPU | vdd_gpu | RK809 BUCK2 | DT + devfreq | on with display | — | — |
| Camera PHY (HAT) | LDO1, LDO9 | RK809 I2C | HAT overlay | off | — | Only with a camera HAT |
| PCIe/USB3 PHY (HAT) | SoC `PD_PIPE` | SoC power domain | HAT overlay | off | — | Topology report §1.3 |
| HAT 3.3 V | HAT_3V3 | TLV62569 EN + TPS259470 #B | SoC GPIO `HAT3V3_EN` | off | eFuse | HAT EEPROM read needs 3.3 V first |
| HAT 5 V out | HAT_5V | TPS61088 + TPS259470 #A | expander `HAT5V_EN` (= `HAT_SRC_ON`) | off | eFuse | Same net forces TPS2121 OV2 |
| HAT 5 V in (powerbank) | HAT_5V → VBUS_CHG | TPS2121 IN2 | OV2 (released when `HAT_SRC_ON` is low) | enabled | — | Dead-battery boot from a powerbank HAT |
| USB-C VBUS out | VBUS | TPS61088 + TPS259470 #C | TCPM source role → `USB_SRC_ON` | off | eFuse | Forces TPS2121 OV1; Default (0.5 A) advertisement on battery |
| Instrumentation | vcc3v3_sys | INA236 power-down mode (I2C) | OpenDAP OS | power-down | — | Shunts stay in circuit |

## 6. Sequencing

### 6.1 System power-up

1. A battery is present (or VBUS / powerbank HAT on TPS2121) → BQ25895 regulates VSYS (≥ 3.5 V VSYSMIN).
2. Power button → RK809 PWRON. RK809-5 runs its OTP sequence. RK809-1 defaults (datasheet Table 4-1) step every 2 ms: BUCK5 (1) → BUCK1, BUCK2, LDO3 (2) → LDO1, LDO2 (3) → BUCK3 (4) → BUCK4, LDO4–6 (5). **The RK809-5 OTP table is UNVERIFIED** and must be read from Rockchip's RK3566 hardware design guide before the rail mapping is frozen.
3. EXT_EN enables the TLV62569 vcc3v3_sys inside the sequence, so eMMC VCC is up before the BootROM reads it.
4. RK860-0 vdd_cpu powers up (EN tied per reference design), RESETB releases the SoC.
5. Everything behind a load switch or EN pin stays off until Linux (or U-Boot, for the display) turns it on.

### 6.2 Audio power-up (pop-free)

1. `DAC_VP_EN` (VP first, DS1156F2 §5.2).
2. `DAC_DIG_EN`, `AUDIO_LN_EN`, one `MCLKxx_EN`. Wait for the XO start-up (≤ 4 ms) and LDO settling.
3. Release the CS43198 RESET (≥ 1 ms low pulse already done), program over I2C, keep outputs muted (Popguard).
4. `HPA_RAIL_EN`: TPS65131 ENP and ENN together, LDO ENs together, so the ±5 V rails ramp symmetrically (OPA1622 §7.4.2). OPA1622 EN stays low.
5. After the rails are in regulation (LDO PG or a fixed delay), raise the OPA1622 EN for the selected output only.
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
- TI TPS7A49, SBVS121E (May 2015): <https://www.ti.com/lit/ds/symlink/tps7a49.pdf>
- TI TPS7A30, SBVS125D (Jun 2015): <https://www.ti.com/lit/ds/symlink/tps7a30.pdf>
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
- Not retrieved this session: Rockchip RK3566 hardware design guide and reference schematic, Pine64 Quartz64/SOQuartz schematics, Cirrus CDB43198 eval board, TI BQ25895 EVM guide, onsemi FUSB302B app note, ADI MAX17055 EV kit, Murata Type 2EL hardware guide. Their content is not used above.

## 8. Open questions

1. **BRD-023 frequencies:** closed (22.5792/24.576 MHz, BRD-023 corrected).
2. **Output targets:** is 4 Vrms balanced / 2 Vrms single-ended the right target, and must the 3.5 mm output drive 16 Ω at full level (parallel halves) or is the low-power single-half build preferred?
3. **MCLK at 1.8 V (blocker):** no stocked audio-grade part; ADR 0009 forbids the translator option. See the cross-validation §4.
4. **RK809-5 OTP sequence and VCC9:** confirm with Rockchip (or the RK3566 hardware design guide) the OTP defaults and that VCC9 may be fed from the external vcc3v3_sys, as on the Orange Pi 3B.
5. **Is the NPU supply separate on the RK3566 (BUCK4) or shared with the GPU** as on RK817 handhelds? This decides whether BUCK4 is free.
6. **RP2354A power default:** on at boot (always-available orchestrator) or off until OpenDAP OS enables it (lowest standby)?
7. **Backlight driver location:** main board (proposed, keeps faceplates passive) or on each faceplate?
8. **HAT power classes:** on battery about 0.7 A at 5.1 V is left for HAT_5V and USB-C source together (§4.6). Accept, or require external power for heavier HATs?
9. **eMMC power in suspend:** keep vcc3v3_sys on, or power the eMMC down in suspend?

## 9. Risks

1. **SoC power is unmeasured.** The 450–800 mW SoC estimate dominates the runtime figure; a ±30 % error moves runtime by hours. *Mitigation:* measure on a Radxa ZERO 3W or Quartz64 with mainline 7.2 and the INA236 plan.
2. **RK809-5 OTP defaults unknown.** A wrong mapping can put a wrong voltage on a rail at boot. *Mitigation:* copy a shipping RK809-5 board exactly and confirm with Rockchip.
3. **TPS65131 output current at low battery** is read from a curve, not a table. *Mitigation:* SPICE/WEBENCH at VIN = 3.4 V, ±6 V, 150 mA; the LM27762 + boost option stays as a fallback.
4. **OPA1622 parallel halves** for 16 Ω drive are not validated. *Mitigation:* simulate; fall back to one half per channel.
5. **VBUS surge coordination:** TVS2200 clamp at 40 A (28.4 V) is above the TPS2121 (24 V) and BQ25895 (22 V) absolute maxima. *Mitigation:* decide whether IEC 61000-4-5 applies to the USB-C port; if it does, add series OVP or choose a lower-clamp TVS with a 14 V standoff and accept the 20 V fault case.
6. **Self-feeding loops** through TPS2121 IN1/IN2 when the T1 sources 5 V. *Mitigation:* hardware OR of `USB_SRC_ON`/`HAT_SRC_ON` into OV1/OV2 (finding 11); verify the OV pin drive levels against SLVSEA3F.
7. **MCLK at 1.8 V not stocked** (blocker). The translator fallback is ruled out by ADR 0009. *Mitigation:* cross-validation §4 options.
8. **Battery current limit** (2 A JST PH contact). *Mitigation:* software power budget on the VSYS INA236; screen-on + CPU peak + HAT load must be measured.
9. **0.6 V LPDDR4X rail sizing** is an estimate. *Mitigation:* Rockchip guide, Radxa/Firefly LPDDR4X schematics.
10. **Thermal:** RK3566 + RK809 + RK860 + charger in a 25 mm sealed body; not modelled. *Mitigation:* thermal simulation once the board outline exists.
