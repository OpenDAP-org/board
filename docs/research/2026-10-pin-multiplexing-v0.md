# RK3566 pin multiplexing and pin allocation v0 for the T1 main board

- **Date:** 2026-10-22
- **Status:** Desk research. **Everything here is a proposal (v0), not a decision.** The maintainers must confirm each allocation, and the schematic must re-check every pin against the full RK3566 datasheet before layout.
- **Scope:** check the T1 signal set (board, faceplate connector, HAT connector) against the RK3566 IOMUX and IO voltage domains. Produce a first pin map, list the conflicts and how to resolve them, and count the faceplate and HAT contacts that result.
- **Inputs:** [`../requirements/README.md`](../requirements/README.md) (BRD-001 to BRD-048), [`../specs/bom-v1.md`](../specs/bom-v0.md), [`2026-10-high-speed-io-topology.md`](2026-10-high-speed-io-topology.md), `t1/docs/specs/faceplate-interface.md` (HID over I2C), `hat-standard/docs/requirements/README.md` and the HAT interconnect benchmark (pin budget §3), `opendap-os` ADR 0006 (native DSD through upstream work) and the system architecture research (finding 8: no DSD formats in the Rockchip I2S driver).
- **Method:** mainline Linux read on 2026-10-22 from `torvalds/linux` `master` (the same tree the topology report calls 7.3). The pin-function map below was generated mechanically from `rk3568-pinctrl.dtsi`. The mux-route constraints come from `pinctrl-rockchip.c`. The IO voltage domains come from the RK3568 datasheet (Table 2-3, "Die Power Domain" column). The RK3566 ball set was checked against two real RK3566 schematics (Radxa CM3 and Radxa ZERO 3W). Anything not confirmed by a primary source is marked **UNVERIFIED**.
- **Load note:** no builds were run. Only downloads, `pdftotext` and `grep`.

---

## 0. Summary

1. **The RK3566 has no parallel RGB output.** The RK3566 brief lists **142 GPIOs**. The union of GPIO names on the Radxa CM3 and ZERO 3W schematics is exactly 142. Compared with the 151 pins of `rk3568-pinctrl.dtsi`, the missing ones are **GPIO2_D0–D7 and GPIO3_A0**, which carry `LCDC_D0–D7` and **`LCDC_CLK`**. The CM3 schematic labels the remaining VOP pins only as `VOP_BT1120_*` and never as `LCDC_*`. The brief lists HDMI, eDP, LVDS, dual MIPI-DSI and EBC, but no RGB. **No pixel clock pin means no RGB at any bit depth, 16- or 18-bit included.** The RGB entry in BRD-048 is met with a **DSI-to-RGB bridge on the faceplate** (mainline drivers exist), not with SoC pins.
2. **MIPI DSI 4-lane has no conflict.** DSI0 and DSI1 use dedicated D-PHY balls. DSI0 shares its balls with LVDS0 (`MIPI_DSI_TX0_Dx/LVDS_TX0_Dx`), so the same five faceplate pairs can carry 4-lane DSI or single LVDS.
3. **I2S1 can use only one mux option at a time** (one route field, `GRF 0x0310[11:10]`), and **I2S1 M2 does not exist on the RK3566** (its MCLK, SCLK_TX and LRCK_TX are on missing balls). The proposal puts I2S1 on **M1** (VCCIO6 bank): it is the only RK3566 option with four separate SDO and four separate SDI pins. That gives PCM to the DACs, two spare SDO lines for future native DSD, and a separate RX clock domain with four SDI lines for multichannel capture from a HAT.
4. **Audio instance plan:** I2S1 TX → the two CS43198 (SoC as clock consumer, DAC as master). I2S1 RX → HAT multichannel input. I2S2 M1 → HAT stereo I2S with its own clocks. I2S3 M0 → MAX98357A speaker, independent of the DAC (BRD-012). PDM M1 → the two microphones. **Nothing is left for the IW612 PCM port.** v0 carries Bluetooth audio over HCI. A PCM option exists only if exclusive with HAT I2S-A (§3.4).
5. **I2C:** the six controllers are all used, with no address clash (§3.7). The HAT ID EEPROM gets its own controller (I2C4) behind a 1.8 V to 3.3 V isolating translator. HAT general I2C and camera CCI share I2C5.
6. **UART:** four of ten are used: UART0 for the RP2350, UART1 M0 with RTS/CTS for the IW612 Bluetooth, UART2 M0 for the debug pads, and UART4 M0 with RTS/CTS for the HAT.
7. **The 3.3 V GPIO budget is the real bottleneck,** more than the mux. Slow controls (power enables, presence, camera reset, spare faceplate and HAT lines) go to an **I2C GPIO expander with two supply rails** (TCA6416A class, mainline `gpio-pca953x`). It also translates levels.
8. **Faceplate connector:** the validated set is 31 signals + 6 power + 8 ground = **45 contacts**, which exactly fits the BOM's Hirose FH35C-45S (§4.1).
9. **HAT connector:** 12 high-speed pairs (48 contacts with ground fencing) + 46 low-speed + 16 power and analog + 8 low-speed grounds = **118 contacts**. That is inside the 120–128 pogo estimate with 2–10 spares. Adding DSI1 to the HAT would cost about 20 more contacts and break the budget (§4.2).
10. **IO voltages:** PMUIO1 3.3 V (fixed), PMUIO2 1.8 V, VCCIO1 3.3 V (HAT bank), VCCIO2 1.8 V (eMMC), VCCIO3 3.3/1.8 V (microSD UHS), VCCIO4 1.8 V (Wi-Fi/BT), VCCIO5 3.3 V (faceplate and speaker), VCCIO6 1.8 V (audio), VCCIO7 3.3 V (HAT SPI and I2C). Level shifting is needed only for HAT audio, the HAT ID bus and expander-driven HAT lines (§5).

---

## 1. RK3566 peripheral instances and pin options

### 1.1 Evidence and caveats

- **Pin functions:** [`rk3568-pinctrl.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3568-pinctrl.dtsi). It is generated from Rockchip's IOMUX tables and is the authoritative source of mainline group names. The task brief calls it `rk356x-pinctrl.dtsi`; mainline names it `rk3568-pinctrl.dtsi`, and [`rk356x-base.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk356x-base.dtsi) includes it for both SoCs.
- **Mux routing:** [`pinctrl-rockchip.c`](https://github.com/torvalds/linux/blob/master/drivers/pinctrl/pinctrl-rockchip.c), `rk3568_mux_route_data[]`. Each function that has M0/M1/M2 options has **one** GRF route field per controller (for example "I2S1 IO mux M0/M1/M2" at `0x0310` bits 11:10, "PDM IO mux" at `0x0314`). **A controller can therefore not mix pins from two options.** The route selects the input path, so in principle a pure output could appear on another option's pin, but v0 assumes one option per controller (**UNVERIFIED** detail).
- **IO domains:** RK3568 Datasheet V1.0, Table 2-3 "Function IO description" ([Radxa mirror](https://dl.radxa.com/rock3/docs/hw/datasheet/Rockchip-RK3568-Datasheet-V1.0-20201210.pdf)). Domain boundaries were read from where the merged "Die Power Domain" cells sit. They match the function groups and every RK3566 board DT's `io-domains` node. The full **RK3566** datasheet was not retrievable: the Pine64 mirror returned 503 and the Radxa and Firefly paths returned 404. RK3566 domain boundaries are therefore **UNVERIFIED** against an RK3566 document, though consistent with all RK3566 board DTs.
- **RK3566 ball set:** [RK3566 brief](https://www.rock-chips.com/uploads/pdf/2022.8.26/192/RK3566%20Brief%20Datasheet.pdf) ("GPIO x142", "I2S/TDM(8ch) x2, one for HDMI", "I2S/PCM(2ch) x2", "PDM(8ch)", "UART x10", "SPI x4", "I2C x6", "PWM x16"). Ball labels come from the [Radxa CM3 v1.31A schematic](https://dl.radxa.com/cm3/docs/hw/RADXA_CM3_V1.31A_SCH_20221010.pdf) and the [Radxa ZERO 3W v1.12 schematic](https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf).
- **I2S0 has no pins.** In mainline, `i2s0_8ch` has no `pinctrl-0`, and the pin table has no `i2s0` function. It is the internal HDMI audio path, so it is useless for the T1.
- **Not read this session:** RK3568 TRM GRF/IOMUX chapters (only the datasheet was read), and Pine64 schematics (wiki previously returned 503). The Quartz64 A/B, SOQuartz, PineNote, Anbernic RGxx3/RG353, Orange Pi 3B and Firefly ROC-PC **mainline DTs** stand in for them.

### 1.2 Balls missing on the RK3566

| Missing balls | Functions lost on the RK3566 |
|---|---|
| GPIO2_D0–D7 | `LCDC_D0–D7`, `BT656_D0–D7_M0`, `SPI0_*_M1`, `SPI2_CS0/CS1/MOSI/MISO_M1`, `I2S1_MCLK/SCLKTX/LRCKTX/SDI0–3/SDO0_M2`, `UART8_TX_M1`, `PCIE20_CLKREQn/WAKEn_M1` |
| GPIO3_A0 | `LCDC_CLK`, `BT656_CLK_M0`, `SPI2_CLK_M1`, `UART8_RX_M1`, `I2S1_SDO1_M2` |
| (no ball change) | GMAC0 functions on GPIO2_A3–C5 (the RK3566 has no GMAC0); the pins stay, with their other functions |

Consequences: **no RGB, no SPI2 M1, no I2S1 M2, no BT656 M0.** These were found by comparing pin names. The ball-map page of an RK3566 datasheet should confirm them (**UNVERIFIED** in that one sense, but strongly supported: 142 = 142).

### 1.3 IO voltage domains (RK3568 datasheet Table 2-3, applied to the RK3566)

| Domain | GPIOs | Range | Main functions in the domain |
|---|---|---|---|
| PMUIO1 | GPIO0_A0–A7 | **3.3 V fixed** (2.97–3.63 V) | REFCLK_OUT, TSADC_SHUT, PMIC_SLEEP, SDMMC0_DET/PWREN, PCIe20 CLKREQ M0, FLASH_VOL_SEL |
| PMUIO2 | GPIO0_B0–D1 | 1.8 or 3.3 V | CLK32K_IN, I2C0, I2C1, I2C2 M0, SPI0 M0, PWM0–7, UART0, UART2 M0, PCIe20 WAKE/PERST M0 |
| (PMU, no alt function) | GPIO0_D3–D6 | (RK3568 labels the domain PMUIO0) | GPIO only |
| VCCIO1 | GPIO1_A0–B3 | 1.8 or 3.3 V | I2S1 M0, PDM M0, I2C3 M0, UART3 M0, UART4 M0, PCIe20 M2 sidebands, SPDIF M0 |
| VCCIO2 | GPIO1_B4–D4 | 1.8 or 3.3 V (set by FLASH_VOL_SEL strap) | eMMC, FSPI, NAND |
| VCCIO3 | GPIO1_D5–GPIO2_A2 | 1.8 or 3.3 V | SDMMC0 (microSD), UART2/6 M1, UART5 M0, PWM8/9/10 M1 |
| VCCIO4 | GPIO2_A3–C6 | 1.8 or 3.3 V | SDMMC1, UART1 M0, I2C4 M1, I2S2 M0, SPI1 M0, SPI2 M0, UART6–9 M0, CLK32K_OUT1 |
| VCCIO5 | GPIO3_A1–C5 (GPIO2_D0–GPIO3_A0 absent) | 1.8 or 3.3 V | VOP BT1120, I2S3 M0, SDMMC2 M1, SPI1 M1, I2C3 M1, I2C5 M0, PWM8–15 M0, GMAC1 M0, PDM M2 |
| VCCIO6 | GPIO3_C6–GPIO4_C1 | 1.8 or 3.3 V | CIF, EBC, I2S1 M1, I2S2 M1, PDM M1, SDMMC2 M0, SPI3 M0, I2C2 M1, I2C4 M0, GMAC1 M1, CAM_CLKOUT0/1 |
| VCCIO7 | GPIO4_C2–C6 (C7–D1 likely, **UNVERIFIED**) | 1.8 or 3.3 V | SPI3 M1, I2S3 M1, PWM12–15 M1, SPDIF M2, I2C5 M1 (HDMI DDC pins), UART9 M1 |

Board precedent (`io-domains` nodes in mainline DTs): PMUIO2 is 3.3 V on Quartz64-A, PineNote, SOQuartz and Orange Pi 3B, and **1.8 V on Quartz64-B and Radxa ZERO 3**. VCCIO4 is 1.8 V on every board with SDIO Wi-Fi. VCCIO6 is 1.8 V on Quartz64-A (DVP camera) and 3.3 V elsewhere.

### 1.4 Peripheral instances and their pin options (RK3566)

Pins are given as `bank_pin`, for example `3_C6` = GPIO3_C6. "Usable" refers to the RK3566 ball set.

| Peripheral | Option | Pins | Domain | Usable on RK3566 | Notes |
|---|---|---|---|---|---|
| I2S1 (8ch TDM, separate TX/RX clocks) | M0 | MCLK 1_A2, SCLKTX 1_A3, LRCKTX 1_A5, SCLKRX 1_A4, LRCKRX 1_A6, SDO0 1_A7, SDI0 1_B3, SDO1/SDI3 1_B0, SDO2/SDI2 1_B1, SDO3/SDI1 1_B2 | VCCIO1 | Yes | Only 5 data pins: SDO1–3 and SDI1–3 **share** balls (`rockchip,io-multiplex`). Collides with PDM M0, UART3/4 M0, I2C3 M0. Used on Quartz64, PineNote, RGxx3 (RK817 codec) |
| I2S1 | M1 | MCLK 3_C6, SCLKTX 3_C7, LRCKTX 3_D0, SDO0 3_D1, SDI0 3_D2, SDI1 3_D3, SDI2 3_D4, SDI3 3_D5, SCLKRX 4_A6, LRCKRX 4_A7, SDO1 4_B0, SDO2 4_B1, SDO3 4_B5 | VCCIO6 | **Yes** | **Four separate SDO and four separate SDI pins.** Collides with CIF, EBC, SDMMC2 M0, SPI3 M0, I2C2 M1 (4_B5), GMAC1 M1, CAM_CLKOUT0/1 |
| I2S1 | M2 | MCLK/SCLKTX/LRCKTX/SDI0–3/SDO0/SDO1 on missing balls | VCCIO5 | **No** | Absent balls |
| I2S2 (2ch I2S/PCM) | M0 | MCLK 2_C1, SCLKTX 2_C2, LRCKTX 2_C3, SDO 2_C4, SDI 2_C5, SCLKRX 2_B7, LRCKRX 2_C0 | VCCIO4 | Yes | Collides with SPI1 M0, SPI2 M0, UART6–9 M0 RTS/CTS |
| I2S2 | M1 | MCLK 4_B6, SCLKTX 4_B7, LRCKTX 4_A4, SDO 4_B3, SDI 4_B2, SCLKRX 4_C1, LRCKRX 4_A5 | VCCIO6 | Yes | Collides with SPI3 M0, I2C4 M0, UART9 M2, UART1 M1 RTS/CTS; **not** with I2S1 M1 or PDM M1 |
| I2S3 (2ch I2S/PCM) | M0 | MCLK 3_A2, SCLK 3_A3, LRCK 3_A4, SDO 3_A5, SDI 3_A6 | VCCIO5 | Yes | Shared TX/RX clocks. Collides with SDMMC2 M1, GMAC1 M0 |
| I2S3 | M1 | MCLK 4_C2, SCLK 4_C3, LRCK 4_C4, SDO 4_C5, SDI 4_C6 | VCCIO7 | Yes | Collides with SPI3 M1, PWM12–15 M1 |
| PDM (8ch) | M0 | CLK0 1_A6, CLK1 1_A4, SDI0 1_B3, SDI1 1_B2, SDI2 1_B1, SDI3 1_B0 | VCCIO1 | Yes | Same balls as I2S1 M0 (PineNote uses it this way) |
| PDM | M1 | CLK0 3_D6, SDI0 3_D7, CLK1 4_A0, SDI1 4_A1, SDI2 4_A2, SDI3 4_A3 | VCCIO6 | Yes | No collision with I2S1 M1 or I2S2 M1 |
| PDM | M2 | CLK1 3_C4, SDI0 3_B3, SDI1 3_B4, SDI2 3_B7, SDI3 3_C0 | VCCIO5 | Partly | No CLK0 on M2 |
| SPDIF TX | M0 / M1 / M2 | 1_A4 / 3_C5 / 4_C4 | VCCIO1 / 5 / 7 | Yes | Not needed on board. M2 is a free option on a HAT GPIO pin |
| MIPI DSI0 (4 lanes) | dedicated | `MIPI_DSI_TX0_CLK±`, `D0±–D3±`, shared with `LVDS_TX0_*` | own analog rails | Yes | Faceplate |
| MIPI DSI1 (4 lanes) | dedicated | `MIPI_DSI_TX1_*` | own analog rails | Yes | Spare (HAT option, §4.2) |
| eDP 1.3 | dedicated | `EDP_TX_D0–D3±`, `AUX±` | own analog rails | Yes | Mainline RK356x eDP support **UNVERIFIED**. Not used |
| VOP BT1120 out | — | D0 3_A1 … D15 3_C3, CLK 3_A6 | VCCIO5 | Balls yes | YCbCr only. A mainline VOP2 BT1120 encoder for RK356x was not found (`rockchip_drm_vop2.c` has an RGB0 endpoint only). Not used |
| SDMMC0 | — | D0–D3 1_D5,1_D6,1_D7,2_A0; CMD 2_A1; CLK 2_A2; DET 0_A4; PWREN 0_A5 | VCCIO3 (DET/PWREN: PMUIO1) | Yes | microSD on every reference board |
| SDMMC1 | — | D0–D3 2_A3–2_A6; CMD 2_A7; CLK 2_B0; PWREN 2_B1; DET 2_B2 | VCCIO4 | Yes | SDIO Wi-Fi on Quartz64, CM3, Orange Pi 3B, SOQuartz |
| SDMMC2 | M0 | D0–D3 3_C6–3_D1, CMD 3_D2, CLK 3_D3 | VCCIO6 | Yes | Same balls as I2S1 M1 (RGxx3 uses it for Wi-Fi) |
| SDMMC2 | M1 | D0–D3 3_A1–3_A4, CMD 3_A5, CLK 3_A6 | VCCIO5 | Yes | Same balls as I2S3 M0 and SPI1 M1 CS0 |
| eMMC | — | 1_B4–1_C7 | VCCIO2 | Yes | FLASH_VOL_SEL (0_A7) high means VCCIO2 = 1.8 V (CM3 schematic note) |
| UART0 | — | RX 0_C0, TX 0_C1, RTS 0_C4, CTS 0_C7 | PMUIO2 | Yes | Always-on domain |
| UART1 | M0 / M1 | 2_B3/2_B4 + RTS 2_B5, CTS 2_B6 / 3_D7, 3_D6 + 4_B6, 4_C1 | VCCIO4 / VCCIO6 | Yes | M0 is the proven Bluetooth UART (Quartz64, CM3, OPi 3B) |
| UART2 | M0 / M1 | 0_D0/0_D1 / 1_D6/1_D5 | PMUIO2 / VCCIO3 | Yes | M0 is the BootROM/TPL/U-Boot debug console on every RK3566 board |
| UART3 | M0 / M1 | 1_A0/1_A1 + RTS 1_A2, CTS 1_A3 / 3_C0, 3_B7 | VCCIO1 / VCCIO5 | Yes | |
| UART4 | M0 / M1 | RX 1_A4, TX 1_A6, RTS 1_A5, CTS 1_A7 / 3_B1, 3_B2 | VCCIO1 / VCCIO5 | Yes | |
| UART5 | M0 / M1 | 2_A1/2_A2 (+1_D7, 2_A0) / 3_C3, 3_C2 | VCCIO3 / VCCIO5 | M0 collides with SDMMC0 | |
| UART6 | M0 / M1 | 2_A3/2_A4 / 1_D6/1_D5 | VCCIO4 / VCCIO3 | Collide with SDMMC1 / SDMMC0 | |
| UART7 | M0 / M1 / M2 | 2_A5/2_A6 / 3_C5, 3_C4 / 4_A3, 4_A2 | VCCIO4 / 5 / 6 | M2 free in v0 | |
| UART8 | M0 / M1 | 2_C6, 2_C5 / missing balls | VCCIO4 | M0 only | |
| UART9 | M0 / M1 / M2 | 2_A7/2_B0 / 4_C6, 4_C5 / 4_A5, 4_A4 | VCCIO4 / 7 / 6 | M0 collides with SDMMC1 | |
| I2C0 | — | SCL 0_B1, SDA 0_B2 | PMUIO2 | Yes | PMIC on every board |
| I2C1 | — | SCL 0_B3, SDA 0_B4 | PMUIO2 | Yes | |
| I2C2 | M0 / M1 | 0_B5/0_B6 / 4_B5/4_B4 | PMUIO2 / VCCIO6 | Yes | M1 collides with I2S1 M1 SDO3 (4_B5) |
| I2C3 | M0 / M1 | 1_A1/1_A0 / 3_B5/3_B6 | VCCIO1 / VCCIO5 | Yes | |
| I2C4 | M0 / M1 | 4_B3/4_B2 / 2_B2/2_B1 | VCCIO6 / VCCIO4 | Yes | M0 collides with I2S2 M1 |
| I2C5 | M0 / M1 | 3_B3/3_B4 / 4_C7/4_D0 | VCCIO5 / VCCIO7 | Yes | M1 = HDMI DDC balls (RGxx3 uses it as general I2C) |
| SPI0 | M0 / M1 | CLK 0_B5, MOSI 0_B6, MISO 0_C5, CS0 0_C6, CS1 0_C4 / missing | PMUIO2 | M0 only | M0 collides with I2C2 M0 |
| SPI1 | M0 / M1 | CLK 2_B5, MISO 2_B6, MOSI 2_B7, CS0 2_C0, CS1 2_C6 / MOSI 3_C1, MISO 3_C2, CLK 3_C3, CS0 3_A1 | VCCIO4 / VCCIO5 | Yes | M0 collides with UART1 M0 RTS/CTS; M1 has **one** CS |
| SPI2 | M0 / M1 | CLK 2_C1, MISO 2_C2, MOSI 2_C3, CS0 2_C4, CS1 2_C5 / CLK on a missing ball | VCCIO4 | M0 only | M0 collides with I2S2 M0 |
| SPI3 | M0 / M1 | CLK 4_B3, MOSI 4_B2, MISO 4_B0, CS0 4_A6, CS1 4_A7 / CLK 4_C2, MOSI 4_C3, MISO 4_C5, CS0 4_C6, CS1 4_D1 | VCCIO6 / VCCIO7 | Yes | M0 collides with I2S1 M1 |
| PWM0–7 | M0/M1 | 0_B7…0_C7 (PWM1/2 M1 on 0_B5/0_B6) | PMUIO2 | Yes | Share balls with UART0, SPI0 M0, I2C2 M0 |
| PWM8–15 | M0 | 3_B1, 3_B2, 3_B5, 3_B6, 3_B7, 3_C0, 3_C4, 3_C5 | VCCIO5 | Yes | |
| PWM8–15 | M1 | 1_D5, 1_D6, 2_A1, 4_C0, 4_C5, 4_C6, 4_C2, 4_C3 | VCCIO3/4/6/7 | Partly | Collide with SDMMC0, SPI3 M1, I2S3 M1 |
| PCIe 2.1 sidebands | M0 / M2 | CLKREQ 0_A5, WAKE 0_B5, PERST 0_B6 / CLKREQ 1_B0, WAKE 1_B1, PERST 1_B2 | PMUIO1+2 / VCCIO1 | Yes | M1 CLKREQ/WAKE on missing balls. Mainline uses a GPIO for PERST# |
| CAM_CLKOUT0/1 | — | 4_A7 / 4_B0 | VCCIO6 | Yes | Both collide with I2S1 M1 |
| REFCLK_OUT | — | 0_A0 | PMUIO1 | Yes | Frequency programmability **UNVERIFIED** |
| SARADC VIN0–7 | dedicated | `SARADC_VIN0..` (1.8 V analog) | SARADC_AVDD_1V8 | Yes | VIN0 is the "Recovery" key on CM3 and ZERO 3W |

---

## 2. Pin allocation table v0 (proposal)

Domains and voltages follow §5. "Board" means it stays on the main PCB, "FP" means it goes through the faceplate FPC and "HAT" means it goes through the HAT flat cable and pogo field.

### 2.1 Audio

| Function | Instance | Mux | Pins | Domain / V | Destination | Notes |
|---|---|---|---|---|---|---|
| DAC BCLK in (DAC master) | I2S1 TX | M1 | SCLKTX 3_C7 | VCCIO6 / 1.8 V | Board: CS43198 L (master) and R | SoC is clock consumer (`SND_SOC_DAIFMT_BC_FC`, supported by `rockchip_i2s_tdm.c`). Test pad |
| DAC LRCK in | I2S1 TX | M1 | LRCKTX 3_D0 | VCCIO6 / 1.8 V | Board: both DACs | Test pad |
| PCM data to both DACs | I2S1 TX | M1 | SDO0 3_D1 | VCCIO6 / 1.8 V | Board: ASP data in of DAC L and DAC R | Dual mono: DAC L takes the left slot, DAC R the right slot. Test pad |
| Future native DSD, left | I2S1 TX | M1 | SDO1 4_B0 | VCCIO6 / 1.8 V | Board: DSDA of DAC L | Reserved for the ADR 0006 driver work. The CS43198 takes DSD on dedicated DSDCLK/DSDA/DSDB pins (DS1156F2 pin table), so the DSD clock is its own net to DSDCLK. Feasibility on the I2S-TDM block and the CS43198 DSD pin names are **UNVERIFIED**. Test pad |
| Future native DSD, right | I2S1 TX | M1 | SDO2 4_B1 | VCCIO6 / 1.8 V | Board: DSDA of DAC R | As above. Test pad |
| HAT multichannel out (optional) | I2S1 TX | M1 | SDO3 4_B5 | VCCIO6 → 3.3 V translator | HAT `I2S_TDM_DOUT` | Runs on the **DAC clock**. Usable while the DAC clocks run. Buffered so the HAT stub does not load the audio nets |
| I2S1 MCLK pin | I2S1 | M1 | 3_C6 | VCCIO6 / 1.8 V | Test pad only | The DACs take MCLK straight from the oscillators. The SoC does not need it in consumer mode |
| HAT multichannel in | I2S1 RX | M1 | SCLKRX 4_A6, LRCKRX 4_A7, SDI0–3 3_D2–3_D5 | VCCIO6 → 3.3 V translator | HAT `TDM_BCLK_IN`, `TDM_FS_IN`, `DIN0–3` | Its own RX clock domain (no `trcm-sync`). 4 lines × 2 ch, or TDM on DIN0 (8 ch, driver `channels_max = 8`) |
| HAT stereo I2S (A) | I2S2 | M1 | MCLK 4_B6, SCLKTX 4_B7, LRCKTX 4_A4, SDO 4_B3, SDI 4_B2 | VCCIO6 → 3.3 V translator | HAT `I2S_MCLK`, `I2S_BCLK`, `I2S_FS`, `I2S_DOUT`, `I2S_DIN` | Its own clocks; the SoC can be provider or consumer. TDM on the "2ch" I2S2 is **UNVERIFIED** |
| Speaker amp | I2S3 | M0 | SCLK 3_A3, LRCK 3_A4, SDO 3_A5 | VCCIO5 / 3.3 V | Board: MAX98357A BCLK/LRCLK/DIN | Independent of the DAC (BRD-012). MAX98357A needs no MCLK. 3_A2 and 3_A6 are free for the faceplate |
| Speaker SD_MODE | GPIO | — | 1_D1 | VCCIO2 / 1.8 V | Board: MAX98357A SD_MODE | 1.8 V logic high is above the SD_MODE threshold (**UNVERIFIED** exact value) |
| PDM main mic (faceplate) | PDM | M1 | CLK0 3_D6, SDI0 3_D7 | VCCIO6 / 1.8 V | FP | Second channel of SDI0 is unused, or both mics share one line (L/R select) |
| PDM ambient mic (body, top right) | PDM | M1 | CLK1 4_A0, SDI1 4_A1 | VCCIO6 / 1.8 V | Board | Separate clock pin keeps the faceplate clock stub off the body mic |
| MCLK 44.1k family enable | GPIO | — | 4_B4 | VCCIO6 / 1.8 V | Board: 22.5792 MHz oscillator ST (tri-state) | One oscillator at a time; the DAC is clock master |
| MCLK 48k family enable | GPIO | — | 4_C0 | VCCIO6 / 1.8 V | Board: 24.576 MHz oscillator ST (tri-state) | |
| DAC reset | GPIO | — | 4_A2 | VCCIO6 / 1.8 V | Board: both CS43198 RESET | Free because UART7 M2 is unused |
| DAC interrupt | GPIO | — | 4_A3 | VCCIO6 / 1.8 V | Board: both CS43198 INT (open-drain, wired-OR) | |
| DAC control | I2C2 | M0 | 0_B5/0_B6 | PMUIO2 / 1.8 V | Board | CS43198 at 0x30 and 0x31 (ADR pin; range by analogy with CS43130, **UNVERIFIED**) |
| Headphone amp enable / mute | GPIO | — | 1_D0 | VCCIO2 / 1.8 V | Board: OPA1622 EN, 4.4 mm pair (the 3.5 mm pair enable is on the TCA6416A expander, BOM v1 line 93, because only the selected output's two packages are enabled) | Pull-down; the BootROM FSPI probe may toggle this ball (**UNVERIFIED**). Audio rails are off during boot |
| Headphone detect 3.5 / 4.4 mm | Expander | — | TCA6416A P-port | 3.3 V port | Board | Interrupt through the expander INT. Millisecond latency is acceptable |
| I2S/DSD capture taps (BRD-040/041) | — | — | SCLKTX, LRCKTX, SDO0, SDO1, SDO2 nets | 1.8 V | Board: test pads + RP2350 inputs | RP2350 IOVDD at 1.8 V (§5) gives a direct, buffer-free tap |

### 2.2 Storage, radio, USB, coprocessor

| Function | Instance | Mux | Pins | Domain / V | Destination | Notes |
|---|---|---|---|---|---|---|
| eMMC 8-bit HS200 | SDHCI | — | 1_B4–1_C7 | VCCIO2 / 1.8 V | Board | FLASH_VOL_SEL 0_A7 strapped high |
| microSD (UHS) | SDMMC0 | — | 1_D5–2_A2, DET 0_A4 | VCCIO3 / 3.3↔1.8 V | Board | VCCIO3 fed by a switchable RK809 LDO (`vccio_sd`, as on Quartz64). SD card power from an RK809 switch, so 0_A5 is not needed as SDMMC0_PWREN |
| Wi-Fi SDIO 3.0 | SDMMC1 | — | 2_A3–2_B0 | VCCIO4 / 1.8 V | Board: IW612 | Proven pattern |
| Bluetooth HCI | UART1 | M0 | RX 2_B3, TX 2_B4, RTS 2_B5, CTS 2_B6 | VCCIO4 / 1.8 V | Board: IW612 | Proven pattern |
| IW612 power-down, host wake | GPIO | — | PDn 2_B7, WL_HOST_WAKE 2_C0, BT_HOST_WAKE 2_C1 | VCCIO4 / 1.8 V | Board | Waking from deep suspend on a non-GPIO0 pin is **UNVERIFIED**. SDIO in-band IRQ is the fallback for Wi-Fi |
| BT wake (host → BT) | GPIO | — | 2_C4 | VCCIO4 / 1.8 V | Board | |
| 32.768 kHz to IW612 | CLK32K_OUT1 | — | 2_C6 | VCCIO4 / 1.8 V | Board | If the module needs an external sleep clock (**UNVERIFIED** for Type 2EL) |
| BT PCM (optional) | I2S2 | M0 | 2_C2–2_C5 | VCCIO4 | Board: DNP 0 Ω | **Exclusive with HAT I2S-A** (one I2S2 route field). Not populated in v0 (§3.4) |
| USB-C data | OTG0 | dedicated | `USB3_OTG0_DP/DM` | — | Board: main USB-C | Per topology report |
| FUSB302B | I2C1 + INT | — | I2C 0_B3/0_B4, INT 0_C4 | PMUIO2 / 1.8 V | Board | 0x22. INT on GPIO0 so it can wake. 1.8 V I2C/INT levels **UNVERIFIED** |
| RP2350 USB | EHCI host0 | dedicated | `USB2_HOST2_DP/DM` | — | Board | Per topology report |
| RP2350 UART | UART0 | — | RX 0_C0, TX 0_C1 | PMUIO2 / 1.8 V | Board | No flow control in v0 (0_C4/0_C7 are used elsewhere) |
| RP2350 IRQ / wake | GPIO | — | 0_C7 | PMUIO2 / 1.8 V | Board | |
| RP2350 SWD | GPIO (bit-bang) | — | SWCLK 1_D2, SWDIO 1_D3 | VCCIO2 / 1.8 V | Board | OpenOCD `linuxgpiod`. BRD-015 flashing also works over USB (PICOBOOT) |
| RP2350 RUN, BOOTSEL | GPIO, open-drain | — | RUN 2_C2, BOOTSEL 2_C3 | VCCIO4 / 1.8 V | Board | Free because BT PCM is not populated. Kept off the FSPI balls so a BootROM probe cannot reset the RP2350 |
| RP2350 I2C (optional) | I2C2 | M0 | 0_B5/0_B6 | PMUIO2 / 1.8 V | Board | Address to be assigned (avoid 0x21, 0x30–0x31, 0x6A–0x6B) |

### 2.3 Power, sensors, buttons, debug

| Function | Instance | Mux | Pins | Domain / V | Destination | Notes |
|---|---|---|---|---|---|---|
| PMIC RK809 | I2C0 | — | 0_B1/0_B2 | PMUIO2 / 1.8 V | Board | 0x20, as on every RK3566 board |
| PMIC interrupt | GPIO | — | 0_A3 | PMUIO1 / 3.3 V | Board | `pmic_int_l` on PineNote, Quartz64, Zero 3 |
| PMIC sleep | PMIC_SLEEP | — | 0_A2 | PMUIO1 / 3.3 V | Board | |
| Thermal shutdown to PMIC | TSADC_SHUT | M0 | 0_A1 | PMUIO1 / 3.3 V | Board: RK809 reset input | BRD-007/010 |
| 32 kHz from PMIC | CLK32K_IN | — | 0_B0 | PMUIO2 / 1.8 V | Board | |
| Charger, fuel gauge | I2C1 | — | 0_B3/0_B4 | PMUIO2 / 1.8 V | Board | BQ25895 0x6A, MAX17055 0x36, FUSB302B 0x22 |
| Charger INT | GPIO | — | 0_C3 | PMUIO2 | Board | Wake source |
| Fuel-gauge ALRT | Expander | — | TCA6416A | — | Board | Not latency-critical |
| IMU | I2C2 | M0 | 0_B5/0_B6 | PMUIO2 / 1.8 V | Board | LSM6DSV16X at 0x6A/0x6B. No clash, because the BQ25895 0x6A is on I2C1 |
| IMU INT1 (wake on motion, BRD-030) | GPIO | — | 0_C5 | PMUIO2 | Board | INT2 goes to the expander or is left unconnected |
| GPIO expander | I2C2 + GPIO | M0 | I2C 0_B5/0_B6, INT 1_D4 | PMUIO2 / 1.8 V host side; INT on VCCIO2 / 1.8 V; 3.3 V port side | Board | TCA6416A class at 0x21. 1_D4 is the last free FSPI ball. If the expander must wake the SoC, its INT can instead be wired-OR'd with the RP2350 IRQ on 0_C7 (**owner choice**) |
| Action button | GPIO | — | 0_C2 | PMUIO2 | Board | Wake source; `gpio-keys` (BRD-036) |
| Vol+ / Vol− | SARADC VIN0 | dedicated | `SARADC_VIN0` ladder | 1.8 V analog | Board | `adc-keys`. Rockchip convention: holding Vol+ at boot enters the U-Boot loader (recovery, BRD-017) |
| Main / power button | RK809 PWRON | — | PMIC pin | — | Board | Power key via `rk805-pwrkey`. MaskROM: see §3.10 (BRD-035) |
| Debug UART (BRD-047) | UART2 | M0 | RX 0_D0, TX 0_D1 | PMUIO2 / 1.8 V | Board: test pads (+ optional SBU through TPD8S300A) | BootROM/TPL default console. 1.8 V pads |
| Faceplate HID interrupt | GPIO | — | 0_B7 | PMUIO2 / 1.8 V pull-up | FP | Open-drain on the faceplate side. Wake source for faceplate controls |
| Faceplate ALS interrupt | GPIO | — | 0_C6 | PMUIO2 / 1.8 V pull-up | FP | VEML6030 INT is open-drain |
| Status LED | PWM9 | M0 | 3_B2 | VCCIO5 / 3.3 V | FP | Developer-controllable (`pwm-leds`) |

### 2.4 Faceplate (FP)

| Function | Instance | Mux | Pins | Domain / V | Notes |
|---|---|---|---|---|---|
| DSI 4-lane + clock | DSI0 | dedicated | `MIPI_DSI_TX0_CLK±`, `D0±–D3±` | D-PHY | Same balls carry LVDS0 if a faceplate overlay selects it (mainline RK3568 LVDS **UNVERIFIED**) |
| Touch + ALS + HID + panel I2C | I2C3 | M1 | SCL 3_B5, SDA 3_B6 | VCCIO5 / 3.3 V | GT911 0x5D/0x14, VEML6030 0x10/0x48, HID controller (address to be assigned, for example 0x2C), optional backlight driver |
| SPI / DBI | SPI1 | M1 | SCLK 3_C3, MOSI 3_C1, MISO 3_C2, CS0 3_A1 | VCCIO5 / 3.3 V | One hardware CS. DBI type C needs MOSI + SCLK + CS + D/C |
| DBI D/C | GPIO | — | 3_A2 | VCCIO5 | I2S3 MCLK pin, unused by the speaker |
| Touch INT / RST | GPIO | — | 3_B3 / 3_B4 | VCCIO5 | GT911 uses INT as an address strap during reset, so INT must be a real GPIO on the faceplate bank |
| Panel RST / TE | GPIO | — | 3_A7 / 3_B0 | VCCIO5 | TE is an input for tear-free DBI/DSI command mode |
| Backlight PWM / enable | PWM8 M0 / GPIO | — | 3_B1 / 3_A6 | VCCIO5 | 3_A6 is I2S3 SDI, unused by the speaker. `VOP_PWM_M1` (3_C4) is the alternative backlight PWM |
| Status LED | PWM9 | M0 | 3_B2 | VCCIO5 | See §2.3 |
| HID INT, ALS INT | GPIO | — | 0_B7, 0_C6 | PMUIO2 | See §2.3 |
| Main mic PDM | PDM | M1 | 3_D6, 3_D7 | VCCIO6 / 1.8 V | See §2.1 |
| Faceplate detect, 2 spare GPIO | Expander | — | TCA6416A P-port | 3.3 V | Slow lines |
| Panel / backlight / mic rails | Board load switches | — | Enables on the expander | — | `VSYS_FP`, `3V3_FP`, `1V8_FP`, `MIC_VDD` (BRD-027: privacy LED on `MIC_VDD`) |

### 2.5 HAT

| Function | Instance | Mux | Pins | Domain / V | Notes |
|---|---|---|---|---|---|
| USB 3 + USB 2, USB 2 port B, PCIe, CSI-2 4-lane | dedicated PHYs | — | Per topology report | — | 12 differential pairs |
| PCIe CLKREQ#, WAKE#, PERST# | PCIe20 M2 sidebands | M2 | 1_B0, 1_B1, 1_B2 | VCCIO1 / 3.3 V | PERST# driven as GPIO (`reset-gpios`), as on every mainline RK3566 board |
| ID EEPROM I2C (dedicated) | I2C4 | M1 | SDA 2_B1, SCL 2_B2 | VCCIO4 / 1.8 V → PCA9306-class translator → 3V3_AUX | Translator enable can isolate the bus until HAT_DET# asserts. EEPROM 0x50 |
| General I2C + camera CCI | I2C5 | M1 | SCL 4_C7, SDA 4_D0 | VCCIO7 / 3.3 V | Shared bus; the HAT designer keeps addresses distinct (§3.7) |
| SPI | SPI3 | M1 | CLK 4_C2, MOSI 4_C3, MISO 4_C5, CS0 4_C6, CS1 4_D1 | VCCIO7 / 3.3 V | `4_D1` domain **UNVERIFIED** (VCCIO7 assumed) |
| UART with flow control | UART4 | M0 | RX 1_A4, TX 1_A6, RTS 1_A5, CTS 1_A7 | VCCIO1 / 3.3 V | |
| SWD/JTAG to HAT chips | GPIO (bit-bang) | — | TCK 1_A0, TMS 1_A1, TDI 1_A2, TDO 1_A3, nRESET 1_B3 | VCCIO1 / 3.3 V | OpenOCD `linuxgpiod` or `sysfsgpio`. Speed limited (§3.9) |
| PWM-capable GPIO ×4 | PWM12–15 | M0 | 3_B7, 3_C0, 3_C4, 3_C5 | VCCIO5 / 3.3 V | 3_C5 also offers SPDIF TX M1 |
| GPIO ×4 more | GPIO / expander | — | 4_C4 (GPIO, SPDIF TX M2), 3 expander lines | 3.3 V | Expander lines are slow |
| HAT detect, HAT interrupt | GPIO | — | HAT_DET# 0_A5, HAT_INT# 0_A6 | PMUIO1 / 3.3 V | GPIO0 so both can wake the SoC |
| Camera reset / power-down | Expander | — | TCA6416A | 3.3 V | |
| Camera MCLK (optional) | REFCLK_OUT | — | 0_A0 | PMUIO1 / 3.3 V | Raspberry Pi-style camera modules carry their own oscillator. Treat as optional (§3.8) |
| HAT power: VHAT enable, eFuse fault, 3V3_AUX enable | Expander | — | TCA6416A | — | Board-side signals, not on the connector |
| HAT audio (I2S-A, multichannel in, optional DOUT on the DAC clock) | I2S2 M1, I2S1 RX/TX | M1 | See §2.1 | VCCIO6 → 3.3 V translator | 12 lines at the connector (§4.2) |

---

## 3. Conflicts found and their resolution

### 3.1 Parallel RGB (BRD-048): not possible on the RK3566

- **Finding:** `LCDC_CLK` (GPIO3_A0) and `LCDC_D0–D7` (GPIO2_D0–D7) have no balls on the RK3566 (§1.2). On the RK3566 the remaining VOP balls are labelled `VOP_BT1120_D0–D15` and `VOP_BT1120_CLK`. Mainline VOP2 has an `ROCKCHIP_VOP2_EP_RGB0` path for the RK3568, but on the RK3566 it has no clock pin.
- **"RGB limited to 18-bit" does not help.** Without a pixel clock, every RGB width is impossible.
- **Resolution (proposal):** meet the "parallel RGB" entry of BRD-048 with a **bridge on the faceplate**, fed by the same 4-lane DSI:

| Panel interface | Faceplate bridge | Mainline driver |
|---|---|---|
| Parallel RGB (DPI) | Chipone ICN6211 or Toshiba TC358762 | `drivers/gpu/drm/bridge/chipone-icn6211.c`, `tc358762.c` (presence in 7.3 **UNVERIFIED** this session) |
| LVDS | TI SN65DSI83/84, or the SoC's own LVDS0 on the same balls | `ti-sn65dsi83.c` (**UNVERIFIED** this session) |
| SPI/DBI (small panels) | none | `panel-mipi-dbi` (**UNVERIFIED** this session) |

- **Trade-off:** a bridge adds a part and a little power on RGB faceplates only. In return, the board needs no RGB pins and keeps VCCIO5 and VCCIO6 for audio and the HAT.
- **Resolution not chosen:** BT1120 output with an external YCbCr-to-RGB converter. It needs 17 pins and has no known mainline encoder.

### 3.2 DSI 4-lane: no pin conflict

DSI0 uses dedicated D-PHY balls. The only coupling is that **DSI0 and LVDS0 share the same balls**, which is useful: an LVDS faceplate reuses the same five pairs. DSI1 stays spare. The VOP2 "same source, dual display" limit from the topology report still applies to any second display.

### 3.3 SPI/DBI on the faceplate

- **Options:** SPI1 M1 (VCCIO5), SPI3 M0 (collides with I2S1 M1), SPI3 M1 (wanted by the HAT), SPI0 M0 (collides with I2C2 M0), SPI2 M0 (collides with I2S2 M0 and VCCIO4 at 1.8 V). SPI0 M1 and SPI2 M1 do not exist on the RK3566.
- **Resolution:** **SPI1 M1 for the faceplate, SPI3 M1 for the HAT.** SPI1 M1 has only **one** hardware CS. A second faceplate CS would be a GPIO CS (`cs-gpios`), which mainline supports.
- **Trade-off:** taking SPI3 M1 for the HAT removes I2S3 M1 and PWM12–15 M1, so the speaker must use I2S3 M0 and the HAT PWMs must use M0 (VCCIO5).

### 3.4 I2S/TDM instances

The needs are the dual-mono DAC (with DSD later), HAT multichannel, the speaker, Bluetooth audio and PDM. Only three external I2S controllers have pins: I2S1 (8ch), I2S2 (2ch) and I2S3 (2ch). One route field per controller rules out splitting one controller across options.

| Need | Instance | Why |
|---|---|---|
| DAC PCM (+ DSD later) | **I2S1 TX on M1** | The only option with SDO0–SDO3 on separate balls; M2 does not exist; M0 shares SDO1–3 with SDI1–3 |
| HAT multichannel in | **I2S1 RX on M1** | I2S1 has separate RX clocks (SCLKRX/LRCKRX) and four separate SDI balls on M1 |
| HAT stereo I2S with its own clocks | **I2S2 M1** | Same bank as I2S1 M1 with no ball overlap; leaves VCCIO4 for the radio |
| Speaker (BRD-012) | **I2S3 M0** | An independent clock domain. M1 would collide with HAT SPI3 M1 |
| Microphones | **PDM M1** | No overlap with I2S1 M1 or I2S2 M1. PDM M0 would collide with I2S1 M0 and UART4 M0 (the HAT UART) |
| Bluetooth audio | **None in v0** | IW612 PCM would need I2S2 M0, which is exclusive with I2S2 M1 (HAT I2S-A) |

**Bluetooth trade-off.** LE Audio carries audio over HCI ISO channels, and classic SCO can also run over HCI. v0 therefore routes Bluetooth audio over the UART. Whether `btnxpuart` supports SCO over HCI with the IW612 at useful quality is **UNVERIFIED**. If PCM is needed later, there are two choices: (a) populate the DNP 0 Ω links to I2S2 M0 and give up HAT I2S-A, or (b) wire the IW612 PCM to the RP2350 for diagnostics only.

**Native DSD (ADR 0006).** Two SDO lines are reserved (SDO1 → DSDA of DAC L, SDO2 → DSDA of DAC R), with the DSD clock on its own net to each DAC's DSDCLK pin. The CS43198 takes DSD on dedicated DSDCLK/DSDA/DSDB pins (DS1156F2 pin table; [BOM v1 cross-validation](2026-10-bom-v1-cross-validation.md) F28). Two things are **UNVERIFIED**:

1. whether the Rockchip I2S-TDM block can stream raw bits at 64 × fs per line without framing gaps;
2. whether the DAC can master the DSD clock.

The board cost of keeping the option open is two traces and two test pads.

**HAT multichannel playback.** I2S2 is "2ch" and its TDM support is **UNVERIFIED**. Wider HAT playback is possible on I2S1 SDO3 (and on SDO1/SDO2 when DSD is not in use), **but only on the DAC's clock domain**. **Trade-off:** a HAT that needs its own multichannel playback clock cannot have it while the on-board DAC plays. Capture (I2S1 RX) has no such limit.

### 3.5 SDIO versus SD, and SDMMC2

- SDMMC0 → microSD and SDMMC1 → Wi-Fi do not conflict with each other or with anything else.
- **SDMMC2 is not available** in this plan. M0 sits on the I2S1 M1 balls, and M1 sits on the I2S3 M0 + SPI1 M1 CS0 balls. That answers open question 7 of the topology report: **no SDIO on the HAT** in v0.
- **Trade-off:** HAT Wi-Fi or SD readers must use USB or PCIe. That is acceptable, and HCS-004 prefers the faster buses anyway. To restore SDMMC2 M1, the speaker would have to move to I2S3 M1 and the HAT SPI to SPI3 M0, which breaks I2S1 M1. **Not recommended.**

### 3.6 UART count

There are ten UARTs, but most options collide with SDMMC0/1 or with the chosen I2S and SPI options. The plan uses four:

| UART | Use | Domain |
|---|---|---|
| UART0 | RP2350 | PMUIO2 1.8 V |
| UART1 M0 (RTS/CTS) | IW612 Bluetooth | VCCIO4 1.8 V |
| UART2 M0 | Debug pads (BootROM, TPL, U-Boot, Linux) | PMUIO2 1.8 V |
| UART4 M0 (RTS/CTS) | HAT | VCCIO1 3.3 V |

Spares that still work: UART7 M2 (4_A2/4_A3, but those balls are the DAC reset and interrupt in v0) and UART3 M0 (1_A0–A3, but those are HAT JTAG in v0). **Trade-off:** a second HAT UART costs the bit-banged HAT JTAG, or two DAC control lines, which would then move to the expander.

### 3.7 I2C bus count and addresses

There are six controllers and seven logical needs. Resolution: **HAT general I2C and camera CCI share I2C5.**

| Bus | Mux / domain | Devices (7-bit address) | Clash check |
|---|---|---|---|
| I2C0 | PMUIO2 1.8 V | RK809 0x20 | — |
| I2C1 | PMUIO2 1.8 V | FUSB302B 0x22, MAX17055 0x36, BQ25895 0x6A | None |
| I2C2 M0 | PMUIO2 1.8 V | TCA6416A 0x21, CS43198 0x30 + 0x31, LSM6DSV16X 0x6A (or 0x6B), RP2350 (to be assigned) | None. The IMU's 0x6A would clash with the BQ25895 if both were on one bus, so they are not |
| I2C3 M1 | VCCIO5 3.3 V | GT911 0x5D (or 0x14), VEML6030 0x10 (or 0x48), HID controller (to be assigned, avoid 0x10/0x14/0x48/0x5D), optional backlight driver | The faceplate spec must reserve these addresses |
| I2C4 M1 | VCCIO4 1.8 V → translator | HAT ID EEPROM 0x50 (HAT+ style) | Dedicated bus |
| I2C5 M1 | VCCIO7 3.3 V | HAT devices + camera sensor | Responsibility of the HAT designer; the HAT standard should list the addresses already taken by OpenDAP reference HATs |

**Trade-off:** sharing CCI with general I2C saves two contacts. A HAT carrying a camera at 0x10 or 0x36 cannot also place a general device at that address. If the HAT standard insists on separate CCI pins, they can be a **bit-banged `i2c-gpio`** bus from two expander lines. A camera at 400 kHz over bit-banging is marginal (**UNVERIFIED**).

### 3.8 Camera MCLK versus I2S1 M1

`CAM_CLKOUT0` (4_A7) and `CAM_CLKOUT1` (4_B0) are I2S1 M1's LRCKRX and SDO1. **Resolution:** no SoC camera clock on the HAT. HAT camera modules carry their own oscillator, as Raspberry Pi camera boards do. `REFCLK_OUT` (0_A0) is offered as an optional clock pin. Its programmable frequencies are **UNVERIFIED**, and many sensors want 24 MHz. **Trade-off:** bare sensors without an oscillator need one on the HAT, which costs the HAT about one small part.

### 3.9 HAT SWD/JTAG from SoC GPIO (BRD-004)

No SoC peripheral speaks SWD, so a bit-banged GPIO (OpenOCD `linuxgpiod`) is the direct path. It meets BRD-004 but runs at only about 100 kHz to 1 MHz (**UNVERIFIED** figure for the RK3566). **Trade-off:** large HAT firmware flashes slowly. Under BRD-005 the RP2350 may additionally act as a fast CMSIS-DAP probe, but **not** as the only path.

### 3.10 Main / power button as the MaskROM trigger (BRD-035)

The RK3566 BootROM enters MaskROM USB download when no boot medium answers. The CM3 schematic says: "Short eMMC_D0/FLASH_D0 and GND to enter Maskrom Mode". The power button reaches the RK809 PWRON pin, not the eMMC. Two candidate circuits:

1. **Button gates eMMC_D0 (or CLK) to GND only at power-on.** For example, a small logic gate enabled while the RK809 holds the SoC in reset, or for a fixed RC window after VCCIO2 rises. Holding the power button at power-on then makes the eMMC unreadable to the BootROM. **Risk:** any leakage or glitch on an eMMC line. It needs SI review and a bench test.
2. **Button in parallel with the SARADC_VIN0 "Recovery" key.** This gives U-Boot loader mode (rockusb), not BootROM MaskROM. It works only if U-Boot is intact, which is not enough for BRD-016.

**Proposal:** circuit 1, plus SD-card boot recovery (BRD-043) as a second path. **UNVERIFIED** until it is prototyped.

### 3.11 GPIO budget (the real bottleneck)

After the peripheral muxes, the free 3.3 V GPIOs are exhausted, and so are the free wake-capable GPIO0 pins:

- PMUIO1/PMUIO2: 26 balls, all assigned.
- VCCIO1: 12 balls, all HAT.
- VCCIO5: 21 balls, all faceplate, speaker and HAT PWM.
- VCCIO7: 8 balls, all HAT.

**Resolution:** a **TCA6416A-class expander** (16 I/O, two supply rails: 1.8 V host side, 3.3 V port side, INT output, mainline `gpio-pca953x`) carries:

- the power enables: faceplate rails, mic rail, VHAT eFuse enable, 3V3_AUX, audio rails, USB host VBUS;
- the inputs: eFuse fault, fuel-gauge alert, headphone detects, faceplate detect;
- the slow faceplate and HAT spares;
- HAT camera reset and power-down.

**Trade-off:** these lines become I2C-latency (about 100 µs) and are no longer usable as PWM or fast IRQs. Power-up defaults must be chosen so the SoC boots with the expander unconfigured (BRD-019). Nothing in a data path goes through it (BRD-005/006).

### 3.12 Wake sources outside GPIO0 (BRD-009)

The wake-critical lines are on GPIO0: PMIC, charger, USB-C controller, IMU, Action button, faceplate HID, ALS, RP2350, HAT detect and HAT interrupt. The IW612 host-wake lines are on GPIO2. Whether GPIO1–4 can wake the RK3566 from the deep suspend `opendap-os` is studying is **UNVERIFIED**. If they cannot, Wi-Fi wake-on-WLAN uses the SDIO in-band interrupt, or the RP2350 relays the wake to 0_C7.

---

## 4. Validated connector signal sets

### 4.1 Faceplate connector (Hirose FH35C-45S, 0.3 mm)

What fits without taking anything from audio or the HAT:

| Group | Signals | Contacts |
|---|---|---|
| MIPI DSI0 (or LVDS0) | CLK±, D0±, D1±, D2±, D3± | 10 |
| I2C (touch, ALS, HID controls, panel) | SCL, SDA | 2 |
| SPI/DBI | SCLK, MOSI, MISO, CS, D/C | 5 |
| Touch | INT, RST | 2 |
| Panel | RST, TE | 2 |
| Backlight | PWM, EN | 2 |
| Interrupts | HID_INT, ALS_INT | 2 |
| Status LED | PWM | 1 |
| Main microphone | PDM_CLK, PDM_DATA | 2 |
| Detect + spares | FP_DET#, GPIO ×2 (expander) | 3 |
| **Signals subtotal** | | **31** |
| Power | VSYS_FP ×2 (backlight boost on the faceplate), 3V3_FP ×2, 1V8_FP ×1, MIC_VDD ×1 | 6 |
| Ground | One between DSI pairs and at the group edges (6), plus 2 power returns | 8 |
| **Total** | | **45** |

Notes:

- **The count fits the FH35C-45S exactly, with no spare.** If the maintainers wants spares, the FH26W 45-pin second source is the same count. The next size up is a 51-pin part, which is **UNVERIFIED** in that family.
- **Backlight current:** about 0.1 A from VSYS for a 3.5-inch panel over two contacts. The FH35C contact rating has not been checked (**UNVERIFIED**). Large panels may need more VSYS contacts.
- **Logic level is 3.3 V** (VCCIO5). Panels with 1.8 V IOVCC take RST/TE and DBI through a translator on the faceplate. `1V8_FP` is provided for that IOVCC.
- **PDM at 1.8 V** comes from VCCIO6. The PDM clock (about 3 MHz) crosses the FPC next to DSI. The ground guard is part of the 8 grounds.
- **Not on the connector:** parallel RGB (§3.1), a second DSI, eDP. Faceplate buttons travel over HID-over-I2C, not as raw lines (T1-023/024).
- **Status LED** stays SoC-driven (`pwm-leds`) for developers, as the brief asks. It is not a HID output.

### 4.2 HAT connector

Cross-check against the hat-standard benchmark's ~120–128 contacts:

| Group | Signals | Contacts |
|---|---|---|
| High-speed pairs | USB 3 SSTX/SSRX (2), USB 2 for the USB 3 port (1), USB 2 port B (1), PCIe TX/RX/REFCLK (3), CSI-2 CLK + 4 data (5) = **12 pairs** | 24 signal + 24 ground (about 4 per pair) = **48** |
| ID I2C (dedicated) | ID_SDA, ID_SCL | 2 |
| General I2C (+ CCI) | SDA, SCL | 2 |
| SPI | SCLK, MOSI, MISO, CS0, CS1 | 5 |
| UART | TX, RX, RTS, CTS | 4 |
| Audio | I2S-A: MCLK, BCLK, FS, DOUT, DIN (5); TDM in: BCLK_IN, FS_IN, DIN0–3 (6); DOUT on DAC clock (1) | 12 |
| SWD/JTAG | TCK/SWCLK, TMS/SWDIO, TDI, TDO/SWO, nRESET | 5 |
| GPIO | 4 PWM-capable + 4 GPIO | 8 |
| Control | PERST#, CLKREQ#, WAKE#, CAM_RST, CAM_PWDN, HAT_DET#, HAT_INT#, CAM_MCLK (optional) | 8 |
| **Low-speed subtotal** | | **46** |
| Power | VHAT ×4, VHAT return ×4, 3V3_AUX ×2 | 10 |
| Analog | Line out L/R, line in L/R, AGND ×2 | 6 |
| Low-speed grounds | | 8 |
| **Total** | | **118** |

- **118 fits inside 120–128,** leaving 2–10 spares in a 4 × 32 grid. CAM_PWDN and the optional DOUT-on-DAC-clock line are cheap to drop if more spares are wanted.
- **Differences from the benchmark:**
  - CCI is merged into general I2C (−2);
  - audio grows from 7 to 12 lines, so that the I2S1 RX multichannel input is real (+5);
  - VHAT_DIR/FAULT and HAT_PWR_EN stay on the board (eFuse side, −2);
  - CAM_PWDN is added (+1);
  - HS pairs are 12, not 13: the reserve pair goes.
- **Adding DSI1 (4-lane) to the HAT** costs 5 pairs, about 20 contacts, which makes about 138 and breaks the budget. A 2-lane DSI1 (3 pairs, about 12 contacts) gives about 130, just over. **Recommendation:** no HAT display in v0. Revisit if a display HAT is a must.
- **SDIO, Ethernet, HDMI:** none on the HAT. SDIO because of §3.5. Ethernet per the benchmark's HCS-005 justification. HDMI because its DDC balls are I2C5 M1 here and it is not in the HAT list.
- **Logic level at the pogo field: 3.3 V** for all low-speed lines (Raspberry Pi HAT-compatible thinking). Audio and ID lines are translated (§5).

---

## 5. IO voltage domain plan and level shifting

| Domain | Proposed V | Supply (proposal) | What it serves | Justification |
|---|---|---|---|---|
| PMUIO1 | 3.3 V | RK809 always-on 3.3 V (`vcc3v3_pmu`) | PMIC control, HAT_DET#/HAT_INT#, SD detect, strap | Fixed 3.3 V by the datasheet (2.97–3.63 V) |
| PMUIO2 | **1.8 V** | RK809 always-on 1.8 V (`vcca1v8_pmu`) | I2C0/1/2, UART0 (RP2350), UART2 debug, wake interrupts | Precedent: Quartz64-B and Radxa ZERO 3. Matches the CS43198 control port and an RP2350 at 1.8 V |
| VCCIO1 | 3.3 V | `vcc_3v3` | HAT UART, HAT JTAG, PCIe sidebands | HAT low-speed bank |
| VCCIO2 | 1.8 V | `vcc_1v8` | eMMC HS200, RP2350 SWD, audio GPIOs | FLASH_VOL_SEL high; the CM3 note says high means 1.8 V |
| VCCIO3 | 3.3 ↔ 1.8 V | RK809 LDO (`vccio_sd`) | microSD UHS | As on every RK3566 board |
| VCCIO4 | 1.8 V | `vcc_1v8` | Wi-Fi SDIO 3.0 (UHS requires 1.8 V), Bluetooth UART, HAT ID I2C (host side), RP2350 RUN/BOOTSEL | Every SDIO-Wi-Fi board does this |
| VCCIO5 | 3.3 V | `vcc_3v3` | Faceplate logic, speaker I2S, HAT PWM | One fixed 3.3 V faceplate logic level |
| VCCIO6 | 1.8 V | Dedicated low-noise 1.8 V (audio digital) | I2S1 (DAC), I2S2 (HAT), PDM, DAC control lines | CS43198 digital I/O is referenced to VL. 1.8 V VL is assumed (**UNVERIFIED** range). Keeping the DAC clocks free of translators avoids added jitter |
| VCCIO7 | 3.3 V | `vcc_3v3` | HAT SPI, HAT I2C, HAT GPIO | HAT low-speed bank |

### 5.1 Level shifting needed

| Path | From → to | Part class (proposal) | Notes |
|---|---|---|---|
| HAT audio (12 lines) | VCCIO6 1.8 V → HAT 3.3 V | Fixed-direction dual-supply buffers (SN74AXC4T774 / SN74AXC8T245 class) | Direction is known per line. BCLK up to 24.576 MHz is well within AXC limits. The on-board DAC nets are **not** translated; the HAT branch is buffered |
| HAT ID I2C | VCCIO4 1.8 V → 3V3_AUX | PCA9306 / TCA9406 class | The EN pin isolates the bus until the HAT is detected, which helps hot-plug (HCS-014 power-down swap) |
| HAT camera reset/power-down, HAT spare GPIO, faceplate detect and spares | — | TCA6416A port side at 3.3 V | The translation is built into the expander |
| Faceplate panels with 1.8 V IOVCC | 3.3 V → 1.8 V | On the faceplate | The faceplate's own concern; `1V8_FP` is provided |
| Debug UART | 1.8 V pads | None | Use a 1.8 V-capable USB-UART adapter. Document this in the bring-up guide |
| RP2350 | 1.8 V IOVDD | None | RP2350 datasheet: IOVDD 1.8–3.3 V, with `VOLTAGE_SELECT = 1` for 1.8 V input thresholds ([RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)). The RP2350 then taps the 1.8 V I2S/DSD nets directly (BRD-041) |
| Power ICs on I2C1 at 1.8 V | — | None expected | BQ25895, MAX17055 and FUSB302B logic thresholds at 1.8 V pull-up are **UNVERIFIED**. Check each datasheet's VIH. Fallback: PMUIO2 at 3.3 V plus translators to the RP2350 and DAC control |

---

## 6. Open questions and risks

### 6.1 Open questions for the maintainers

1. **BRD-048 wording:** accept "parallel RGB through a DSI-to-RGB bridge on the faceplate"? The RK3566 cannot drive RGB natively (§3.1).
2. **Bluetooth audio:** HCI only in v0 (no PCM)? Or keep the DNP option that is exclusive with HAT I2S-A (§3.4)?
3. **HAT audio scope:** is 2ch with its own clocks + 8ch capture + playback on the DAC clock enough for "I2S/TDM multichannel" (§3.4)?
4. **HAT logic level:** 3.3 V for all HAT low-speed lines, including translated audio, or define HAT audio at 1.8 V and drop the translators?
5. **HAT CCI:** shared with general I2C (proposal), or separate pins through bit-banging (§3.7)?
6. **Display on the HAT (DSI1):** not in v0 because of the contact budget (§4.2). Is that acceptable?
7. **GPIO expander:** accept one TCA6416A-class part for slow controls (§3.11)?
8. **MaskROM circuit** on the power button: accept the eMMC_D0 gating approach for prototyping (§3.10)?
9. **Faceplate connector:** zero spare pins at 45. Accept, or move to a larger part?

### 6.2 Risks

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| 1 | The RK3566 domain boundaries come from the RK3568 datasheet | Wrong domain for a pin means a wrong rail and possible damage | Get the RK3566 datasheet (Rockchip, or the Pine64 mirror once it is back) before the schematic. Check against Quartz64/PineNote schematics |
| 2 | One route field per controller assumed; the output-only exception not used | Lost flexibility if outputs could roam | Read the RK3568 TRM GRF `IOFUNC_SEL` chapter |
| 3 | Native DSD path is unproven (I2S-TDM raw bit streaming; CS43198 DSD pins) | ADR 0006 may need different wiring | Reserved SDO1/SDO2 + test pads. Confirm against the CS43198 datasheet and with an RK3566 bench test before layout freeze |
| 4 | CS43198 VL range (1.8 V assumed) and I2C address range | Domain plan for VCCIO6/PMUIO2 | Read the CS43198 datasheet |
| 5 | Power ICs' I2C thresholds at 1.8 V (PMUIO2) | PMUIO2 may have to be 3.3 V | Datasheet check. The fallback is in §5.1 |
| 6 | Wake from GPIO1–4 in deep suspend | IW612 host wake may not wake the SoC | SDIO in-band IRQ, or an RP2350 relay to 0_C7 |
| 7 | BootROM probes FSPI balls (1_D0–D4) at boot | Glitches on HP-amp enable, speaker SD_MODE and RP2350 SWD at power-on | Pull resistors, rails off during boot. RUN/BOOTSEL already kept off FSPI |
| 8 | FH35C-45S contact current and zero spare pins | Backlight current or a later added line does not fit | Check the contact rating; consider a larger part |
| 9 | Bit-banged JTAG/SWD speed | Slow HAT flashing | Optional RP2350 CMSIS-DAP as an accelerator (BRD-005 compliant) |
| 10 | DSI-to-RGB/LVDS bridge drivers and `panel-mipi-dbi` presence in 7.3 not rechecked this session | BRD-048 claim depends on them | Verify in `drivers/gpu/drm/bridge/` and `drivers/gpu/drm/tiny/` before closing the question |
| 11 | RP2350 at 1.8 V taps the DAC nets; if the RP2350 is unpowered, its pads may load the lines (back-powering) | Audio integrity | Keep the RP2350 powered whenever the audio rail is on, or add series resistors. Review its ESD-diode behaviour |
| 12 | `4_D1` (SPI3 CS1) and `4_C7/4_D0` (I2C5 M1) domain assumed to be VCCIO7 | HAT level | RK3566 datasheet check |

---

## 7. Sources

### SoC documentation

- Rockchip, *RK3566 Brief Datasheet*: <https://www.rock-chips.com/uploads/pdf/2022.8.26/192/RK3566%20Brief%20Datasheet.pdf>
- Rockchip, *RK3568 Datasheet V1.0*, Table 2-3 and power-domain tables (Radxa mirror): <https://dl.radxa.com/rock3/docs/hw/datasheet/Rockchip-RK3568-Datasheet-V1.0-20201210.pdf>
- Full RK3566 datasheet: **not retrieved**. Pine64 `files.pine64.org` returned 503; the Radxa and Firefly paths returned 404.
- RK3568 TRM GRF/IOMUX chapters: **not read** this session (listed at <https://dl.radxa.com/rock3/docs/hw/datasheet/>).

### Mainline Linux (`torvalds/linux` master, read 2026-10-22)

- Pin functions: <https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3568-pinctrl.dtsi>
- Mux route table (`rk3568_mux_route_data`): <https://github.com/torvalds/linux/blob/master/drivers/pinctrl/pinctrl-rockchip.c>
- SoC nodes: <https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk356x-base.dtsi>, <https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-base.dtsi>
- IO domain binding: <https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/power/rockchip-io-domain.yaml>
- I2S-TDM driver and binding: <https://github.com/torvalds/linux/blob/master/sound/soc/rockchip/rockchip_i2s_tdm.c>, <https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/sound/rockchip%2Ci2s-tdm.yaml>
- VOP2: <https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/rockchip/rockchip_drm_vop2.c>, <https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/rockchip/rockchip_vop2_reg.c>
- Board DTs (proven allocations, `io-domains` voltages):
  - [`rk3566-quartz64-a.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-quartz64-a.dts)
  - [`rk3566-quartz64-b.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-quartz64-b.dts)
  - [`rk3566-soquartz.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-soquartz.dtsi)
  - [`rk3566-pinenote.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-pinenote.dtsi)
  - [`rk3566-radxa-zero-3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-radxa-zero-3.dtsi)
  - [`rk3566-radxa-cm3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-radxa-cm3.dtsi)
  - [`rk3566-anbernic-rgxx3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-anbernic-rgxx3.dtsi)
  - [`rk3566-anbernic-rg353x.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-anbernic-rg353x.dtsi)
  - [`rk3566-orangepi-3b.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-orangepi-3b.dtsi)
  - [`rk3566-roc-pc.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-roc-pc.dts)

### Board schematics

- Radxa CM3 v1.31A (RK3566 ball labels, MaskROM note, FLASH_VOL_SEL note): <https://dl.radxa.com/cm3/docs/hw/RADXA_CM3_V1.31A_SCH_20221010.pdf>
- Radxa ZERO 3W v1.12 (RK3566 ball labels, Maskrom button, SARADC_VIN0 recovery): <https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf>
- Pine64 Quartz64 A/B, SOQuartz, PineNote; Anbernic RG353; Radxa ZERO 3E schematics: **not retrieved** this session. Their mainline DTs were used instead.

### Other parts

- Raspberry Pi *RP2350 Datasheet* (IOVDD 1.8–3.3 V, `VOLTAGE_SELECT`): <https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf>
- CS43198, IW612 (Murata Type 2EL), MAX98357A, BQ25895, MAX17055, FUSB302B, LSM6DSV16X, VEML6030, GT911, TCA6416A, PCA9306: datasheets **not re-read** this session. The addresses and levels quoted above are from the parts' usual configurations and are **UNVERIFIED** where marked.
