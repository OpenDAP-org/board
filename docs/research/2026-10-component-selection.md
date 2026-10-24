# OpenDAP T1: component selection for the main board and touch faceplate

- **Date:** 2026-10-21. Stock and price data were captured 2026-10-21/22.
- **Updated 2026-10-24:** the charger, gauge and battery picks here (BQ25895, MAX17055, Adafruit 328) are superseded by [ADR 0014](../adr/0014-two-cell-battery.md) (BQ25798, BQ28Z610-R1, quoted 2S pack), and the 1.27 mm P70 pogo field by hat-standard [ADR 0004](https://github.com/opendap-project/hat-standard/blob/main/docs/adr/0004-pogo-part-and-field-geometry.md) (2.54 mm, Mill-Max 0965 second source). [BOM v1](../specs/bom-v1.md) holds the current parts. Kept as history.
- **Scope:** every board-level part around the decided core. The core is the RK3566 SoC, RK809 PMIC (draft), 2× CS43198 + 4× OPA1622 (draft), 45.1584/49.152 MHz master clocks (draft), RP2350 coprocessor, pre-certified Wi-Fi/BT module, pogo-pin HAT bus, single PCB, and Debian trixie with the **trixie-backports 7.2.x** kernel.
- **Owner directives applied:**
  1. Prefer commercial, multi-distributor, second-sourced, active-lifecycle parts.
  2. Mainline drivers only, ideally enabled in Debian's own arm64 config.
  3. Audio quality and battery life first.
  4. One design shared by the commercial edition and the DIY kit (JLCPCB/PCBWay assembly).
  5. Added mid-task: **prefer the newest generation of each part** when it stays compatible. Every category below has a "newest generation" line that says so explicitly.
- **Conventions:**
  - **UNVERIFIED** means I found no primary source for the claim.
  - **(vendor claim)** means the only source is the manufacturer's marketing or distributor text.
  - "Debian: **on**" or "**off**" refers to the *final* built config described in "How this was verified" below.

> **How this was verified.**
>
> **Debian config.** I extracted the authoritative config from the binary package `linux-config-7.2_7.2.9-1~bpo13+1_arm64.deb` (file `config.arm64_none_arm64.xz`, header "Linux/arm64 7.2.9 Kernel Configuration"), downloaded from `deb.debian.org/debian/pool/main/l/linux/`. This is what `linux-image-arm64` in trixie-backports actually ships, not the partial `debian/config` fragments. I cross-checked the fragments on the [salsa `debian/7.2/trixie-backports` branch](https://salsa.debian.org/kernel-team/linux/-/tree/debian/7.2/trixie-backports/debian/config), whose head is 7.2.11-1~bpo13+1, built 2026-10-18.
>
> **Mainline drivers.** I downloaded the files from `torvalds/linux` master (Makefile says 7.3.0) and read their `of_match` tables. For `v7.2` vs `v7.3` questions I used the tags.
>
> **Stock and price.**
>
> - **LCSC/JLCPCB:** the JLCPCB parts API (`selectSmtComponentList`). Its stock equals the LCSC product page; I spot-checked C1554755, where both show 346. Links use the form `https://www.lcsc.com/product-detail/<C-code>.html`.
> - **Digi-Key:** product pages fetched directly, with quantity, "Part Status" and the qty-1 price read from the page data. Links are given.
> - **Mouser and others:** the [FindChips](https://www.findchips.com/search/) aggregator, with the link pattern `https://www.findchips.com/search/<MPN>`. Mouser blocks direct fetching.
> - **PCBWay:** has no public parts catalog, so it is **not** covered. PCBWay sources parts on demand, and anything stocked at Digi-Key, Mouser or LCSC can be supplied.
>
> **Limits.** Prices are qty-1 USD unless a break is given. Stock changes daily. "JLC library: extended" means the part can be placed by JLCPCB with the extended-part fee. None of the parts below is in JLC's "basic" library. Nothing here has been tested on hardware.

---

## 0. Executive summary

### 0.1 Five findings that change the plan

1. **Debian's arm64 kernel does not enable the DAC driver.** `# CONFIG_SND_SOC_CS43130 is not set`; the CS43198 uses `sound/soc/codecs/cs43130.c`. OpenDAP therefore needs a Debian kernel-config change no matter what else is chosen.
   - Debian enables almost no hi-fi DAC codecs. The only one it turns on is `PCM5102A`. AK4458, PCM179x, WM8741 and PCM512x are all off.
   - **Recommendation:** batch every gap listed in §10 into **one** Debian wishlist bug ("please enable as modules on arm64"). Ship a DKMS build of the in-tree module until the bug lands.
2. **Debian also disables the I²C fuel-gauge drivers.** `BATTERY_BQ27XXX_I2C` is off, even though its Kconfig default is `y`, and `BATTERY_MAX17042` (the MAX17055 driver) is off. With the stock kernel today, the only working gauges are the **RK817's coulomb counter** (`CHARGER_RK817=m`) and **CellWise CW2015** (`BATTERY_CW2015=m`).
3. **Debian disables the IW612 drivers, and Wi-Fi support is too new for 7.2.** IW612 Wi-Fi (`nxpwifi`) exists in mainline **7.3** (`drivers/net/wireless/nxp/nxpwifi`), not in 7.2. Its Bluetooth driver `BT_NXPUART` exists but is **off** in Debian 7.2. The Murata Type 2EL is still the newest-generation option that meets "mainline + SDIO". It needs a 7.3+ backport kernel **and** a config request.
4. **The RK3566 has one USB 3 lane and one PCIe lane, and both are needed by the HAT.** Mainline `rk3566-base.dtsi` limits `usb_host0_xhci` (the OTG controller) to the USB 2 PHY. USB 3 exists only on `usb_host1_xhci` through `combphy1`, as host only, and PCIe 2 x1 is on `combphy2`.
   - So the **USB-C port is USB 2.0 OTG**, and a USB 3 receptacle only makes sense if the single USB 3 host lane is switched between the C port and the HAT.
   - This also rules out a PCIe Wi-Fi 6E/7 module, because the only lane belongs to the HAT.
5. **The candidate panels split on Debian support.**
   - **Disabled in Debian:** the panels in the best-known RK3566 handhelds: RG353P/M/V (v1) and Powkiddy RK2023, which use **NewVision NV3051D** (`DRM_PANEL_NEWVISION_NV3051D` is off), and RG-ARC and the 4" Winstar, which use **ST7701** (off).
   - **Enabled in Debian:** the 3.5" 640×480 **Sitronix ST7703** panels (Anbernic RG353V-V2/RG353PS/RG353VS and Gameforce Chi; `DRM_PANEL_SITRONIX_ST7703=m`). Goodix (`TOUCHSCREEN_GOODIX=m`) and FocalTech FT5x06/FT6x36 (`TOUCHSCREEN_EDT_FT5X06=m`) are on. The Hynitron CST340 used by the RG353P is off.

### 0.2 Recommended picks

| Area | Recommendation | Debian 7.2 status |
|---|---|---|
| Display | 3.5" 640×480 IPS MIPI-DSI on **ST7703**, with a GT911 or FT6336 CTP laminated by the module maker | on (panel and touch) |
| Charger / power path | **TI BQ25895** now; BQ25792 is the newest-generation upgrade but is supply-constrained and Debian-off | on (BQ25895) |
| USB-PD TCPC | **onsemi FUSB302B**; second source **Richtek RT1715** (or Etek ET7304) on `tcpci_rt1711h` | on (both) |
| Fuel gauge | **TI BQ27Z561** or **MAX17055** after the Debian config fix; **RK817** gauge as the stock-Debian fallback | off (needs request) |
| Battery | 1S Li-ion pouch, 104050 (≈2500 mAh) or 805060 (≈3000 mAh) class, with PCM, 10 kΩ NTC and a locking connector; IEC 62133-2 + UN 38.3 | n/a (distributor stock **not verified**) |
| Wi-Fi / BT | **Murata Type 2EL** (IW612, Wi-Fi 6 + BT 5.3/5.4 LE Audio, (vendor claim)); second source **u-blox MAYA-W271** (same IW612). Fallback for stock Debian today: **Murata Type 1MW** (CYW43455, Wi-Fi 5/BT 5.0) | 2EL off (needs 7.3 + request); 1MW on |
| Audio | CS43198-CNZR + OPA1622IDRCR confirmed active and stocked. Clocks: Crystek CCHD-957 (audio-grade, expensive, large) or a low-cost LCSC XO pending jitter measurement. Speaker amp **MAX98357A**; mics **Infineon IM73D122** (PDM) | DAC off (needs request); amp/PDM on |
| IMU / ALS | **ST LSM6DSV16X** and **Vishay VEML7700/VEML6030** | on |
| Memory | LPDDR4X 4 GB (Samsung K4UBE3D4AB-MGCL) + eMMC 5.1 32 GB (Samsung KLMBG2JETD-B041). **Memory is the BOM's biggest cost and availability risk** | n/a |
| HAT pogo | Harwin **P70** SMT 1.27 mm spring probes (2 A each) on a GSG pattern, with **parallel pins for power** | n/a |
| USB-C | USB 2.0 16-pin **GCT USB4105-GF-A**, or 24-pin **Amphenol 12401610E4#2A** if the USB 3 host lane is ever routed to the port | n/a |

---

## 1. Display for the touch faceplate (3.5" IPS, fixed)

### 1.1 What the RK3566 and Debian accept

- **RK3566 outputs:** DSI0 and DSI1 (4-lane DSI with the Innosilicon D-PHY), RGB/DPI parallel through VOP2, LVDS (shared with the DSI PHY) and HDMI. In Debian: `ROCKCHIP_DW_MIPI_DSI=y` and `PHY_ROCKCHIP_INNO_DSIDPHY=m`.
- **Debian arm64 enables only these DRM panel drivers:**
  - `SITRONIX_ST7703`, `SITRONIX_ST7789V`, `SIMPLE`, `EDP`, `LVDS`;
  - `ILITEK_ILI9882T`, `HIMAX_HX83102`;
  - `BOE_TV101WUM_NL6`, `BOE_TH101MB31UIG002_28A`;
  - `FEIYANG_FY07024DI26A30D`, `INNOLUX_P079ZCA`, `KINGDISPLAY_KD097D04`;
  - `RASPBERRYPI_TOUCHSCREEN`, `SAMSUNG_ATNA33XC20`.

  Everything else is off, including `NEWVISION_NV3051D`, `SITRONIX_ST7701`, `ELIDA_KD35T133`, `HIMAX_HX8394` and `ILITEK_ILI9881C`.

### 1.2 Mainline 3.5" panels used by RK3566 and RK3326 handhelds

| Panel (DT compatible) | Controller and driver | Resolution and active area | Used in | Debian |
|---|---|---|---|---|
| `anbernic,rg353v-panel-v2` | ST7703, `drivers/gpu/drm/panel/panel-sitronix-st7703.c` | 640×480, 71×53 mm (≈3.5") | RG353V-V2, RG353PS, RG353VS (`rk3566-anbernic-rg353ps.dts`) | **on** |
| `gameforce,chi-panel` | ST7703, same driver | 640×480, 70×57 mm | GameForce Chi (RK3326) | **on** |
| `anbernic,rg353p-panel`, `anbernic,rg351v-panel` | NV3051D, `panel-newvision-nv3051d.c` | 640×480, 70×57 mm | RG353P/M/V v1, RG351V | **off** |
| `powkiddy,rk2023-panel` | NV3051D | 640×480, 70×57 mm | Powkiddy RK2023 | **off** |
| `anbernic,rg-arc-panel`, `winstar,wf40eswaa6mnn0` | ST7701, `panel-sitronix-st7701.c` | 480×640, 4" | RG-ARC; Winstar 4" | **off** |
| `powkiddy,rgb30-panel` | ST7703 | 720×720, 76×76 mm (4") | RGB30, RGB20SX | **on**, but 4", which the maintainers has ruled out |

### 1.3 Touch controllers

| Controller | Linux driver | Debian | Notes |
|---|---|---|---|
| Goodix GT911 | `drivers/input/touchscreen/goodix.c` (`goodix,gt911`, `gt9110`, `gt912`, `gt917s`, `gt928`, and others) | **on** | |
| FocalTech FT6236 / FT6336 / FT5426 | `edt-ft5x06.c` (`focaltech,ft6236` and others) | **on** | |
| Hynitron CST340 (RG353P) | `hynitron_cstxxx.c` | **off** | |

- These controllers are bonded to the CTP's FPC, so the bare-chip stock below matters less than the CTP supplier.
- **GT911:** not stocked at LCSC (C2837272: 0) and not found at Digi-Key.

### 1.4 Panel availability

- **No catalog distributor carries a bare 3.5" MIPI panel with a Debian-enabled driver.** Digi-Key, Mouser and LCSC have no ST7703 3.5" part.
- The RG353V-V2 and Gameforce panels are sold as handheld **spare parts** on AliExpress-class marketplaces (**UNVERIFIED**: I could not search the web in this session). Their OEM part numbers are unpublished, and they have **no touch layer**, because the RG353V-V2, PS and VS have no touchscreen.
- A Debian-enabled driver also covers future panels. Any ST7703 panel with a different init sequence only needs a new compatible plus its init table in `panel-sitronix-st7703.c`. Because the module is already `=m`, it reaches Debian with the next backport kernel without another config request.
- The fallback is **RGB/DPI through `panel-simple`** (`DRM_PANEL_SIMPLE=m`). It costs about 24 extra pins plus often an SPI init. Many 3.5" 640×480 DPI IPS modules exist, but each needs a `panel-simple` entry upstream.

### 1.5 Newest generation

- In-cell touch (TDDI) 3.5" panels exist, such as the Synaptics/FocalTech TDDI parts in phones. The mainline TDDI panel driver (`DRM_PANEL_SYNAPTICS_TDDI`) is **off** in Debian, and no 3.5" TDDI panel has a mainline entry.
- **Not compatible today.** The ST7703 plus discrete CTP is the newest option that meets the constraints.

### 1.6 Recommendation (display)

1. **Commission a 3.5" 640×480 IPS MIPI-DSI module built on the Sitronix ST7703**, with a **GT911 or FT6336U** CTP that the module maker laminates (OCA). The DT compatibles are already Debian-enabled.
2. Ask the module house to **match the RG353V-V2 timing and init sequence** (`rg353v2_desc` in `panel-sitronix-st7703.c`). Ideally a part-for-part match lets it bind to `anbernic,rg353v-panel-v2` with no kernel change. Otherwise, upstream a new compatible.
3. **Second source:** a second module house for the same ST7703 + GT911 spec. The driver IC, rather than the module, is the common factor.
4. **DIY kit:** the same module. If the custom module has a MOQ, the kit can start with an RG353V-V2 spare plus an add-on CTP, but that is a stop-gap.

---

## 2. Battery charger, power path, USB-PD, fuel gauge and HAT eFuse

### 2.1 Charger and power path

| MPN | Key specs | Mainline driver | Debian | LCSC | Digi-Key | Mouser | Lifecycle / second source / package |
|---|---|---|---|---|---|---|---|
| **TI BQ25895RTWR** | 1S switch-mode charger, 3.9–14 V input, 5 A charge, power-path, **OTG boost 4.5–5.5 V** (current per datasheet, **UNVERIFIED** here), 7-ch ADC | `drivers/power/supply/bq25890_charger.c` (`ti,bq25890/2/5/6`) | **on** (`CHARGER_BQ25890=m`) | [C80200](https://www.lcsc.com/product-detail/C80200.html): 5,954 @ $2.13 | [qty 0, Active, $3.35](https://www.digikey.com/en/products/detail/texas-instruments/BQ25895RTWR/5214018) | 3,608 @ $3.36 ([FindChips](https://www.findchips.com/search/BQ25895RTWR)) | Active. Pin-compatible Southchip SC89890H (C19629486) exists but has **0 stock**. QFN-24 4×4, easy |
| **TI BQ25792RQMR** (newer generation) | 1–4S **buck-boost**, 3.6–24 V input, 5 A, dual-input mux, **OTG 2.8–22 V** (bidirectional HAT power) | `drivers/mfd/bq257xx.c` + `power/supply/bq257xx_charger.c` + `regulator/bq257xx-regulator.c`; BQ25792 support **in v7.2** (Flipper's Alexey Charkov) | **off** (`MFD_BQ257XX` not set) | [C2862876](https://www.lcsc.com/product-detail/C2862876.html): 7,587 @ $2.10 | [**"no longer carried by DigiKey"**](https://www.digikey.com/en/products/detail/texas-instruments/BQ25792RQMR/13577777) | **34** @ $7.36 | Active at TI. Single source. QFN-29 4×4, moderate |
| **Rockchip RK817-5** (replaces RK809) | PMIC with integrated switch charger + coulomb-counter gauge + boost + codec | `mfd/rk8xx-*`, `power/supply/rk817_charger.c`; used by mainline RG353 and RK2023 | **on** (`CHARGER_RK817=m`, `MFD_RK8XX_I2C=y`) | [C5179490](https://www.lcsc.com/product-detail/C5179490.html): **70** @ $2.89 | not listed | not listed | Rockchip agent channel only. QFN-68 7×7, 0.35 mm pitch, hard |
| Rockchip RK809-5 (current draft) | PMIC, **no charger, no gauge** | `rk8xx`, `rk808-regulator` | **on** | [C2939628](https://www.lcsc.com/product-detail/C2939628.html): 1,226 @ $2.47 | not listed | not listed | Rockchip channel |
| SGMicro SGM41513 | Cheap 1S charger | **No mainline driver** found | — | C5153778: 2,575 @ $1.26 | — | — | Rejected: no driver |

**Newest generation.** TI's newest buck-boost chargers are BQ25792/BQ25798. The BQ25792 *is* mainline (7.2), but it fails "enabled in Debian" and "highly available": Digi-Key has dropped it and Mouser has 34. The BQ25895 is older (2015 class) but Debian-enabled and stocked everywhere. The RK817 is the only option with a charger *and* gauge enabled in stock Debian, but it is single-channel (Rockchip agents) and 70 pcs at LCSC.

**Recommendation (charger).**

- **v1: BQ25895** (Debian on, multi-distributor).
- Keep the **BQ25792** footprint as a planned upgrade for bidirectional HAT power once Debian enables `MFD_BQ257XX` and stock recovers.
- If the PMIC is still open, evaluate **RK817 instead of RK809**. That gives charger and gauge in stock Debian and a proven RK3566 handheld reference, at the cost of Rockchip-channel sourcing and 5 V-class input (**UNVERIFIED**: check the RK817 VBUS maximum before relying on 9 V PD).
- None of these chargers can source 5 A into the HAT. The 3–5 A HAT rail needs its own boost or buck stage behind the eFuse (§2.4).

### 2.2 USB-PD controller (TCPC)

| MPN | Specs | Driver | Debian | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|---|---|
| **onsemi FUSB302BMPX** | Type-C port controller with BMC PD PHY. PD revision is handled by Linux TCPM (PD 3.x incl. PPS sink) | `drivers/usb/typec/tcpm/fusb302.c` | **on** (`TYPEC_FUSB302=m`, `TYPEC_TCPM=m`) | [C132291](https://www.lcsc.com/product-detail/C132291.html): 1,648 @ $0.84 | [5,545 @ $1.18, Active](https://www.digikey.com/en/products/detail/onsemi/FUSB302BMPX/6138869) | 5,563 @ $1.10 | Also at Arrow, Verical and Newark. WQFN-14 2.5×2.5 |
| **Richtek RT1715WSC** | TCPCI-standard TCPC | `tcpci_rt1711h.c` (`richtek,rt1715`) | **on** (`TYPEC_RT1711H=m`) | not found | [540 @ $1.19](https://www.digikey.com/en/products/detail/richtek-usa-inc/RT1715WSC/6834142) | 3,239 @ $1.19 | WLCSP, harder for the DIY kit |
| Etek ET7304 | RT1715-compatible TCPCI | `tcpci_rt1711h.c` (`etekmicro,et7304`) | **on** | only JLC placeholder entries (0 stock) | — | — | **UNVERIFIED** availability |
| Hynetek HUSB311 | TCPCI | `tcpci` generic (**UNVERIFIED** compatible) | `TYPEC_TCPCI=m` | C7471922: **0** | — | — | Rejected |

**Newest generation.** USB-PD 3.2 adds EPR (28–48 V) and AVS. The device sinks at most 14 V (BQ25895) or 20 V (BQ25792), so SPR PD 3.x is enough. Every TCPC here is a PHY, and the PD revision is a TCPM software feature, so a "newer TCPC" brings nothing.

**Recommendation (TCPC).** **FUSB302B**, with the RT1715 as the driver-level second source on a different footprint.

### 2.3 Fuel gauge

| MPN | Specs | Driver | Debian | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|---|---|
| **TI BQ27Z561YPHR** | Impedance Track, 1S, WCSP-15 | `bq27xxx_battery_i2c.c` (`bq27z561`) | **off** (`BATTERY_BQ27XXX_I2C` not set, though Kconfig default is `y`) | not found under this MPN | [1,997 @ $2.64, Active](https://www.digikey.com/en/products/detail/texas-instruments/BQ27Z561YPHR/9597827) | 2,871 @ $2.24 | WCSP: JLC can place it; hard by hand |
| **ADI/Maxim MAX17055EWL+T** | ModelGauge m5, 1S, WLP-9 | `max17042_battery.c` | **off** (`BATTERY_MAX17042` not set) | [C2682627](https://www.lcsc.com/product-detail/C2682627.html): 5,840 @ $1.52 | [5,988 @ $4.66, Active](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX17055EWL-T/7392108) | 10,332 @ $4.55 | Best multi-distributor stock |
| CellWise CW2015CHBD | Voltage-based gauge, TDFN-8 | `cw2015_battery.c` | **on** | [C881838](https://www.lcsc.com/product-detail/C881838.html): 1,955 @ $0.79 | not listed | not listed | LCSC only; single source; less accurate |
| RK817 internal | Coulomb counter | `rk817_charger.c` | **on** | see §2.1 | — | — | Only if the PMIC becomes RK817 |

**Newest generation.** The BQ27Z561 and MAX17055 are the newest gauges that the mainline drivers list. Newer TI gauges such as the BQ27Z746 are not in `bq27xxx_battery_i2c.c`'s ID table (checked 2026-10-21).

**Recommendation (gauge).** **MAX17055**, for stock at all three distributors. Its WLP-9 package can be placed by JLC but is hard to solder by hand. Add `BATTERY_MAX17042` to the Debian request in §10. The BQ27Z561 is the alternative if the same request flips `BATTERY_BQ27XXX_I2C`. If stock Debian *today* is a hard gate, use CW2015 or RK817 and accept single-channel sourcing.

### 2.4 eFuse and power mux for the HAT rails

No Linux driver is needed for these. Fault and IMON signals go to GPIO/ADC (`ROCKCHIP_SARADC=m`) or to the RP2350.

| MPN | Specs | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|
| **TI TPS259470ARPWR** (TPS25947 family) | 2.7–23 V, 5.5 A eFuse, reverse-current blocking, IMON, 2×2 QFN | [C3662799](https://www.lcsc.com/product-detail/C3662799.html): 3,766 @ $1.29 | [76,492 @ $2.06, Active](https://www.digikey.com/en/products/detail/texas-instruments/TPS259470ARPWR/14123984) | 17,695 @ $1.97 | Family variants 470A/472A/474L are all stocked. Good for **both directions** with two devices back-to-back |
| **TI TPS2121RUXR** | 2.7–22 V, 4.5 A **power mux** (USB-C vs HAT input) | [C485916](https://www.lcsc.com/product-detail/C485916.html): 25,557 @ $0.92 | [16,584 @ $2.44](https://www.digikey.com/en/products/detail/texas-instruments/TPS2121RUXR/9859001) | 18,252 @ $2.44 | |

**Recommendation (HAT power).** Use **two TPS259470A** in a bidirectional (back-to-back) arrangement on the HAT power pins. Use **TPS2121** when the HAT can be a *source* (powerbank HAT) alongside USB-C. The 5 V/5 A HAT output itself needs a dedicated boost converter, which is out of scope here and should be flagged for the power-tree document.

---

## 3. Battery

### 3.1 Distributor data

**Not verified.** Catalog searches at Digi-Key, Mouser (via FindChips) and LCSC returned no LiPo pouch cells for the size codes 103450, 104050, 654060 or 805060 in this session. Pouch cells are mostly sold direct by cell makers and their agents. Treat every MPN below as **UNVERIFIED** until it is quoted.

### 3.2 Envelope

- A credit-card footprint is 85.6 × 54 mm, at 15–19 mm total thickness.
- After the PCB, faceplate and shells, roughly **8–10 mm** of z-height is realistic for the cell.

| Size code (t × w × l, mm) | Typical 1S capacity | Fits 54 mm width? | Comment |
|---|---|---|---|
| 103450 (10×34×50) | 1800–2000 mAh | yes | At the ≥2000 mAh limit |
| 104050 (10×40×50) | ~2500 mAh | yes | Good balance |
| 654060 (6.5×40×60) | ~2000 mAh | yes | Thin |
| **805060** (8×50×60) | ~3000 mAh | yes (50 mm) | Best energy in the envelope if z-height allows |

### 3.3 Requirements for any cell or pack

- **Certifications:** IEC 62133-2:2017 report, **UN 38.3** test summary (required for shipping), MSDS. UL 2054/UL 1642 is useful for the US market.
- **Pack contents:** a protection PCM (OV/UV/OC/short), a **10 kΩ NTC** wired to the charger's TS pin, and a **locking wire-to-board connector**. Use Molex Pico-Lock or JST GH class, with exact series chosen at layout. Do not solder the cell.
- **Reputable makers with distribution channels** (**UNVERIFIED** current catalog MPNs): Jauch (sells LiPo packs through Digi-Key/Mouser in other sizes), Varta (LPP series), Grepow, EEMB. The Adafruit/SparkFun 2000 mAh packs are prototyping-only and lack the certification paperwork a commercial product needs.

### 3.4 EU user-replaceability

Regulation (EU) 2023/1542, Art. 11, as I recall it; this needs a legal check:

- From **18 February 2027**, portable batteries in appliances placed on the EU market must be **removable and replaceable by the end user** using commercially available tools. If special tools are needed, they must be supplied free.
- Batteries must not be glued in, unless an exemption applies (e.g. devices used in wet conditions, which an IP-rated DAP *might* argue, **UNVERIFIED**).
- Practical design consequences:
  1. Battery behind a screwed or latched door.
  2. Connectorised pack, not soldered tabs.
  3. Pack sold as a spare part.
  4. A standard size code, so third-party replacements exist.

### 3.5 Newest generation

- Silicon-anode or high-voltage (4.45 V) LiPo cells give 10–15 % more energy in the same volume.
- They are **compatible**: BQ25895 and MAX17055 both support a 4.4 V+ charge voltage by register or model (**UNVERIFIED** for 4.45 V on each part). They are, however, rarely stocked in standard size codes.

**Recommendation (battery).** A **805060 or 104050 1S Li-ion polymer pack, 4.2 V (or 4.35/4.4 V HV if quoted with certificates)**, with PCM + NTC + locking connector and an IEC 62133-2 / UN 38.3 report. Qualify **two** cell makers with the same size code and pinout. The battery bay should be designed for user replacement from day one.

---

## 4. Wi-Fi and Bluetooth module

### 4.1 Interface limits

- **SDIO:** RK3566 SDMMC1 is SDIO 3.0, 4-bit SDR104, ≈ 50 MB/s practical.
- **PCIe:** the only Gen2 x1 lane goes to the HAT.
- **USB:** only USB 2.0 hosts are free.
- So **SDIO is the only sensible bus**. PCIe Wi-Fi 6E/7 is excluded by the HAT, and USB Wi-Fi is bus-limited and idles at higher power.

### 4.2 Candidates

| Module (MPN) | Chipset, standard | Linux drivers | Debian 7.2 | Certification | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|---|---|---|
| **Murata Type 2EL, LBES5PL2EL-923** | NXP IW612: Wi-Fi 6 (11ax) 1×1 dual-band + **BT 5.3** (Mouser text) + 802.15.4 | Wi-Fi: `drivers/net/wireless/nxp/nxpwifi` (`NXPWIFI_SDIO`, "IW61x"), **mainline 7.3** (not in v7.2). BT: `drivers/bluetooth/btnxpuart.c` (IW612 chip ID 0x7601). Firmware `nxp/sd_w61x_v1.bin.se` is in linux-firmware and in Debian **firmware-misc-nonfree** (trixie-backports) | **off**: nxpwifi absent in 7.2; `BT_NXPUART` not set | Murata modules are radio-certified (FCC/IC/CE modular) (vendor claim) | [C23572665](https://www.lcsc.com/product-detail/C23572665.html): **0** @ $14.27 | [938 @ $20.30, Active](https://www.digikey.com/en/products/detail/murata-electronics/LBES5PL2EL-923/21689817) | 2,820 @ $20.71 |
| **u-blox MAYA-W271-00B** | NXP IW612 (same silicon); "802.11ax + BT + 802.15.4, 2 antenna pins" | same | same | u-blox lists global certifications (vendor claim) | [C19942033](https://www.lcsc.com/product-detail/C19942033.html): **0** | [398 @ $15.12, Active](https://www.digikey.com/en/products/detail/u-blox/MAYA-W271-00B/18688830) | 415 @ $14.05 |
| **Murata Type 1MW, LBEE5HY1MW-230** | Infineon CYW43455: Wi-Fi 5 (11ac) 1×1 + **BT 5.0** | `brcmfmac` (SDIO) + `hci_uart` BCM. Firmware `brcmfmac43455-sdio.bin` + NVRAM (incl. `pine64,quartz64-b`, an RK3566 board) in Debian **firmware-brcm80211**; `BCM4345C0.hcd` packaged | **on** (`BRCMFMAC_SDIO=y`, `BT_HCIUART_BCM=y`) | "Radio certified" (Newark text) | [C2151969](https://www.lcsc.com/product-detail/C2151969.html): 2 @ $20.06 | [271 @ $17.45, Active](https://www.digikey.com/en/products/detail/murata-electronics/LBEE5HY1MW-230/10129245) | **0** @ $16.42 |
| AMPAK AP6256 | BCM43456 class, Wi-Fi 5 + BT 5.0 | `brcmfmac` | **on** | **No modular certificate found** (**UNVERIFIED**) | [C5248079](https://www.lcsc.com/product-detail/C5248079.html): 4,173 @ $8.28 | not listed | not listed |
| Realtek RTL8723DS / RTL8821CS modules | Wi-Fi 4 / Wi-Fi 5 + BT | `rtw88` SDIO (`RTW88_8723DS`/`8821CS`) + `btrtl` | **on** | No certified module at any catalog distributor; Digi-Key's only RTL8821CS hit (Advantech EWM-W157M201E) is **Obsolete** | placeholders only | — | — |
| MediaTek MT7921S (SDIO) | Wi-Fi 6 2×2 + BT 5.2 | `mt76/mt7921` (`MT7921S`) + `btmtksdio` | **on** | **No module found** at any distributor | — | — | — |

### 4.3 Newest generation

| Generation | Example | Mainline | RK3566-compatible | Verdict |
|---|---|---|---|---|
| Wi-Fi 7 + BT 5.4 | MediaTek MT7925 | `mt7925e`/`mt7925u` (Debian **on**) | PCIe is taken by the HAT; USB 2 caps throughput at ~300 Mb/s, raises idle power, and no certified USB module was found | Rejected (interface) |
| Wi-Fi 7 | Qualcomm WCN785x | `ath12k` (PCIe, Debian **on**) | PCIe taken by the HAT | Rejected (interface) |
| Wi-Fi 6E + BT 5.3 | Infineon CYW55573 (Murata Type 2EA) | No CYW5557x SDIO support found in `brcmfmac` (**UNVERIFIED**) | — | Rejected (driver) |
| **Wi-Fi 6 + BT 5.3/5.4 LE Audio** | **NXP IW612** | **Yes (7.3)** | SDIO + UART | **Recommended** |

LE Audio and Auracast depend on the controller (ISO channels) plus BlueZ. The IW612 advertises LE Audio (vendor claim). The CYW43455 is BT 5.0 and has **no LE Audio**.

**Recommendation (Wi-Fi/BT).**

1. Design for the **Murata Type 2EL**, with the **u-blox MAYA-W271** as the second source on the *same chipset and driver*.
   - It needs (a) a 7.3+ trixie-backports kernel, and (b) Debian enabling `NXPWIFI_SDIO` and `BT_NXPUART` (both in §10).
   - Firmware is already packaged.
2. If the board must boot with Wi-Fi on stock Debian before that lands, populate a **Type 1MW** on a shared SDIO/UART routing for early prototypes only. The footprints differ (Type 1MW LGA vs Type 2EL LGA), so this costs a separate board spin or a dual-footprint layout.
3. Bluetooth tracking (LE) works on both modules.

---

## 5. Audio

### 5.1 DAC and output stage

| MPN | Specs | Driver | Debian | LCSC | Digi-Key | Mouser | Lifecycle |
|---|---|---|---|---|---|---|---|
| **Cirrus CS43198-CNZR** | 32-bit, 130 dB, pseudo-differential, QFN-40 5×5, 1.8 V | `sound/soc/codecs/cs43130.c` (`cirrus,cs43198`) | **off** (`SND_SOC_CS43130` not set) | [C1554755](https://www.lcsc.com/product-detail/C1554755.html): 346 @ $5.38 | [471 @ $18.19, Active](https://www.digikey.com/en/products/detail/cirrus-logic-inc/CS43198-CNZR/7430362) | 1,274 @ $18.19 (+450 of CS43198-CNZ tray) | Active, single source. The LCSC price is ~⅓ of the Digi-Key/Mouser price, so check authenticity and channel. The WLCSP variant CS43198-CWZR (C1554757) has 0 stock |
| **TI OPA1622IDRCR** | Audio op-amp/HP driver, VSON-10 3×3 | none needed | — | [C2876559](https://www.lcsc.com/product-detail/C2876559.html): 666 @ $3.03 | [4,558 @ $7.43, Active](https://www.digikey.com/en/products/detail/texas-instruments/OPA1622IDRCR/5804204) | 1,952 @ $7.43 (+365 IDRCT) | Active, single source |

**Newest generation.** Newer flagship DACs (ESS ES9039 family, AKM AK4499EX, ROHM BD34301) have **no mainline driver** (see the SoC/DAC research doc). The CS43198 remains the newest high-end DAC with a mainline codec driver.

**Recommendation.** Keep **CS43198 + OPA1622**. Add `SND_SOC_CS43130` to the Debian request; this is mandatory. Buy the CS43198 from an authorized channel (Digi-Key/Mouser) for the commercial build.

### 5.2 Master clocks: 45.1584 MHz and 49.152 MHz

| MPN | Type | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|
| **Crystek CCHD-957-25-45.1584** | Audio-grade low-phase-noise HCMOS XO, 3.3 V, 25 ppm | none | [47 @ $33.00, Active](https://www.digikey.com/en/products/detail/crystek-corporation/CCHD-957-25-45-1584/2742157) | 265 @ $26.08 | Large package (9×14 mm class, **UNVERIFIED**); costly |
| **Crystek CCHD-957-25-49.152** | same | none | not checked | **0** @ $34.23 | Out of stock at Mouser |
| SCTF SX3M45.1584M20F30TNN | 3225 CMOS XO, 1.62–3.63 V, ±20 ppm | [C2901589](https://www.lcsc.com/product-detail/C2901589.html): 3,616 @ $0.34 | — | — | **No jitter or phase-noise spec in the listing** |
| SCTF SX3M49.152M20F30TNN | same | [C2901591](https://www.lcsc.com/product-detail/C2901591.html): 2,367 @ $0.51 | — | — | same |
| JYJE 3TO445158CWBD / 3TO449152CWBD | 3225 CMOS XO | C2924632: 4,960 / C2924633: 106 | — | — | same |
| NDK NZ2520SDA (audio-dedicated series) | 2520 low-noise XO | not found | not found | not found | FindChips returned nothing; distributor availability **UNVERIFIED** |

**Newest generation.** Modern ultra-low-jitter XOs are offered as audio-dedicated series (NDK NZ2520SDA, Crystek CCHD-575). They are not stocked for these frequencies at the channels checked here. MEMS oscillators (SiTime) are available but have worse close-in phase noise, which is not appropriate for a DAC master clock.

**Recommendation (clocks).**

1. Lay out a **dual footprint** (3225 and 7050 pads) for each clock.
2. Prototype with the **Crystek CCHD-957** (the 45.1584 MHz part is in stock; source the 49.152 MHz from Digi-Key or on order).
3. **Measure** phase noise and THD+N against a low-cost LCSC XO (SCTF SX3M). Pick the production part from the measurement, not the datasheet.
4. Request NDK NZ2520SDA samples and quotes through NDK's agent.

### 5.3 Jacks

| MPN | Type | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|
| **Same Sky (ex-CUI) SJ-43514-SMT-TR** | 3.5 mm, 4-conductor, R/A SMT | not checked | [10,933 @ $1.52, Active](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/SJ-43514-SMT-TR/669724) | 13,517 |
| **Same Sky SJ2-35894D-SMT-TR** | 3.5 mm, 4-conductor with tip/ring switches (plug detect) | not checked | [2,955 @ $1.53, Active](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/SJ2-35894D-SMT-TR/6619567) | 436 |
| **4.4 mm Pentaconn** (Nippon DICS) | 5-pole balanced | **not found** | **not found** | **not found** |

The 4.4 mm Pentaconn receptacle is **not stocked by any catalog distributor checked**. FindChips, LCSC and the JLC API returned no 4.4 mm jacks. It must be bought from Nippon DICS or its agents, and AliExpress clones exist. The MPN and MOQ are **UNVERIFIED**, so this is a single-source part and a schedule risk.

**Recommendation (jacks).** **SJ2-35894D-SMT-TR** for 3.5 mm, so detect works through `extcon`/`jack` GPIO. Open a Nippon DICS quote now for the genuine Pentaconn 4.4 mm (mid-mount, with detect pin).

### 5.4 Speaker amplifier (integrated speaker)

| MPN | Specs | Driver | Debian | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|---|---|
| **ADI/Maxim MAX98357AETE+T** | I²S class-D mono, 3.2 W, filterless, TQFN-16 3×3 | `sound/soc/codecs/max98357a.c` | **on** | [C910544](https://www.lcsc.com/product-detail/C910544.html): 23,202 @ $1.32 | [38,518 @ $4.08, Active](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX98357AETE-T/4936122) | 23,563 @ $4.08 |
| ADI/Maxim MAX98360AENL+T (newer) | Same function, lower power, WLP-9 1.4×1.4 | same driver (`maxim,max98360a`) | **on** | C4990962: 24 | [78 @ $3.52](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX98360AENL-T/12460957) | 366 |
| TI TAS2562YFPR | Smart amp with I/V sense | `tas2562.c` | **on** | C2879588: **0** | [non-stock at Digi-Key ("Available To Order")](https://www.digikey.com/en/products/detail/texas-instruments/TAS2562YFPR/10820212) | not listed |
| TI TAS2781 / Cirrus CS35L56 (newest smart amps) | DSP smart amps | `tas2781-i2c`, `cs35l56` | **on** | — | — | — |
| Nuvoton NAU8315YG | Class-D mono | `nau8315.c` | **on** | C4991453: 0 | — | 0 |

The newest smart amps (TAS2781, CS35L56) are Debian-enabled but need speaker-specific DSP tuning firmware. That is not open and not trivial for a DIY kit.

**Recommendation (amp).** **MAX98357A** (stock everywhere, QFN, simplest driver). The MAX98360A is the newer same-driver part, but its stock is thin and WLP is harder for the kit.

**Speaker.** **Same Sky CMS-151125-078S-67**: 15×11×2.5 mm, 8 Ω, 0.7 W, IP67, spring contacts. [Digi-Key 719 @ $3.04, Active](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMS-151125-078S-67/9561100); Mouser 890. Alternatives are PUI AS01508MR-6-R (Mouser 1,657) and Same Sky CMS-15113-078SP.

---

## 6. Coprocessor, IMU, ambient light and microphones

### 6.1 RP2350 family

| MPN | LCSC | Digi-Key | Mouser |
|---|---|---|---|
| RP2350A (QFN-60 7×7) | [C42411118](https://www.lcsc.com/product-detail/C42411118.html): 6,002 @ $1.29 | Listed under Raspberry Pi "SC" codes (e.g. `SC1511-A4` for RP2354A); stock **not retrieved** | not found via FindChips |
| RP2350B (QFN-80 10×10) | [C42415655](https://www.lcsc.com/product-detail/C42415655.html): 3,922 @ $1.28 | as above | — |
| **RP2354A** (RP2350A + 2 MB stacked flash) | [C41378174](https://www.lcsc.com/product-detail/C41378174.html): 8,081 @ $1.26 | as above | — |
| RP2354B | [C39843328](https://www.lcsc.com/product-detail/C39843328.html): **3** @ $1.52 | — | — |

- **Newest generation:** RP2350 is Raspberry Pi's newest MCU. The RP2354 (in-package flash) removes the QSPI flash chip.
- **Recommendation:** **RP2354A** (in stock, fewer parts, no external flash to source). Use the RP2350B/RP2354B only if the GPIO count demands it, and note that RP2354B stock is near zero.

### 6.2 IMU

| MPN | Generation | Driver | Debian | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|---|---|
| **ST LSM6DSV16XTR** | 2022, newest ST 6-axis with sensor fusion and Qvar | `st_lsm6dsx` (`st,lsm6dsv16x`) | **on** (`IIO_ST_LSM6DSX`, I²C + SPI) | [C5267406](https://www.lcsc.com/product-detail/C5267406.html): 7,764 @ $3.36 | [0, Active, $5.75](https://www.digikey.com/en/products/detail/stmicroelectronics/LSM6DSV16XTR/16841485) | 4,510 @ $5.75 |
| ST LSM6DSOXTR | Previous generation | same | **on** | [C481766](https://www.lcsc.com/product-detail/C481766.html): 11,043 @ $3.86 | [0, Active](https://www.digikey.com/en/products/detail/stmicroelectronics/LSM6DSOXTR/9841882) | 4,557 |
| ST LSM6DSO32XTR | — | same | **on** | — | [1,533 @ $5.73](https://www.digikey.com/en/products/detail/stmicroelectronics/LSM6DSO32XTR/14291421) | — |
| TDK ICM-42688-P | — | `inv_icm42600` (`invensense,icm42688`) | **on** | [C1850418](https://www.lcsc.com/product-detail/C1850418.html): 786 @ **$20.86**; Tokmas clone ICM-42688-P(TOKMAS) C54308212: 2,978 | [0, Active](https://www.digikey.com/en/products/detail/tdk-invensense/ICM-42688-P/10824934) | 0 |
| Bosch BMI270 | — | `drivers/iio/imu/bmi270` | **off** (`BMI270_I2C` not set) | [C2836813](https://www.lcsc.com/product-detail/C2836813.html): 28,442 @ $2.76 | not retrieved | 74,790 @ $4.23 |
| TDK ICM-45686 (newest TDK) | — | `inv_icm45600` | **off** | not checked | — | — |

**Recommendation (IMU).** **LSM6DSV16X**: the newest generation that is Debian-enabled, with stock at LCSC and Mouser. The LSM6DSOX is its pin-compatible LGA-14 2.5×3 fallback on the same driver.

### 6.3 Ambient light sensor (one per faceplate)

| MPN | Driver | Debian | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|---|
| **Vishay VEML7700-TT** | `veml6030.c` (`vishay,veml7700`) | **on** | [C1850416](https://www.lcsc.com/product-detail/C1850416.html): 7,161 @ $1.20 | [6,226 @ $1.53](https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/VEML7700-TT/6210690) | 86,433 |
| **Vishay VEML6030** (2×2 mm, smaller) | `veml6030.c` | **on** | [C132182](https://www.lcsc.com/product-detail/C132182.html): 10,967 @ $0.72 | [9,408 @ $1.59](https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/VEML6030/6007711) | 10,103 |
| Lite-On LTR-303ALS-01 | `ltr501.c` (`liteon,ltr303`) | **on** | [C364577](https://www.lcsc.com/product-detail/C364577.html): 14,671 @ $0.55 | [18,484 @ $0.78](https://www.digikey.com/en/products/detail/liteon/LTR-303ALS-01/4847335) | 29,622 |
| TI OPT3001DNPR | `opt3001.c` | **on** | [C90462](https://www.lcsc.com/product-detail/C90462.html): 3,084 @ $2.17 | not retrieved | **0** |
| Vishay VCNL4040M3OE (ALS + proximity) | `vcnl4000.c` | **on** | [C142526](https://www.lcsc.com/product-detail/C142526.html): 11,767 @ $1.61 | — | 21,986 |
| TI OPT4001 / OPT4060, Vishay VEML3235 (newest generation) | `opt4001.c`, `opt4060.c`, `veml3235.c` | **off** | — | — | — |

**Recommendation (ALS).** **VEML6030** (2×2 mm, Debian on, stock at all three). The **LTR-303ALS-01** on the same footprint class is a second source with a different driver, which is also on. The newest TI and Vishay parts would need a Debian config request for no functional gain here.

### 6.4 MEMS microphones and how the RK3566 takes PDM

- **Path:** the RK3566 has an 8-channel **PDM controller** (`pdm@fe440000`, `rockchip,rk3568-pdm` in `sound/soc/rockchip/rockchip_pdm.c`). Pair it with the generic `dmic` codec. Debian: **on** (`SND_SOC_ROCKCHIP_PDM=m`, `SND_SOC_DMIC=m`).
- **Wiring:** two mics share one PDM data line (L/R select) and one clock. PDM avoids burning an I²S port, since I²S1 8ch goes to the DACs.
- **I²S mics are worse here:** the I²S MEMS codec driver (`SND_SOC_ICS43432`) is **off** in Debian, and the ICS-43434 is now **Obsolete** at Digi-Key.

| MPN | Type | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|
| **Infineon IM73D122V01XTMA1** | PDM, 73 dB SNR, 122 dB AOP; newest Infineon XENSIV | [C5563886](https://www.lcsc.com/product-detail/C5563886.html): 5,352 @ $2.88 | [36,572 @ $2.72, Active](https://www.digikey.com/en/products/detail/infineon-technologies/IM73D122V01XTMA1/16999563) | 15,038 | Best SNR in the list |
| Infineon IM69D130V01XTSA1 | PDM, 69 dB SNR | C42464166: 0 | [66,648 @ $2.62](https://www.digikey.com/en/products/detail/infineon-technologies/IM69D130V01XTSA1/8030732) | 28,079 | Previous generation |
| TDK T5838 (MMICT5838-00-012) | PDM, low power, acoustic activity detect | [C7230692](https://www.lcsc.com/product-detail/C7230692.html): 1,381 @ $3.36 | [182 @ $2.67](https://www.digikey.com/en/products/detail/tdk-invensense/MMICT5838-00-012/16903860) | 0 | Good for an always-listening ambient mic |
| Knowles/Syntiant SPH0641LU4H-1 | PDM | [C2879853](https://www.lcsc.com/product-detail/C2879853.html): 587 @ $2.08 | [2,979 @ $3.68](https://www.digikey.com/en/products/detail/syntiant/SPH0641LU4H-1/5332438) | 3,198 | |
| TDK ICS-43434 | I²S | C5656610: 2,248 | [**Obsolete**](https://www.digikey.com/en/products/detail/tdk-invensense/ICS-43434/6140298) | — | Rejected |

**Recommendation (mics).** **IM73D122** for both the faceplate (main) and body (ambient-noise) mics, on one PDM data line using L/R. The SPH0641LU4H-1 is the PDM second source on a different footprint.

---

## 7. Memory and storage

### 7.1 Constraints

- The RK3566 supports **LPDDR4/LPDDR4X** (no LPDDR5) and **eMMC 5.1** (no UFS). These are therefore the newest generations the SoC can use.
- The rkbin DDR init blob for the RK356x handles LPDDR4/4X generically. Rockchip's per-part "memory support list" was **not verified** in this session.

### 7.2 Candidates

**Availability warning.** Catalog-distributor DRAM pricing is extreme in Oct 2026. Micron 4 GB LPDDR4X is listed at **$386–$468 each** at Mouser and Newark, and LCSC's Samsung and SK hynix parts sit at **~$80** with tens to hundreds of units. Treat memory as a broker/agent-quoted item and budget for it.

| MPN | Type | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|
| **Samsung K4UBE3D4AB-MGCL** | LPDDR4X 32 Gb (4 GB), x32, 200-FBGA | [C5827966](https://www.lcsc.com/product-detail/C5827966.html): 236 @ $82.09 | not listed | not listed | Common on RK356x boards (**UNVERIFIED** against the AVL) |
| SK hynix H9HCNNNCPMMLXR-NEE | LPDDR4X 4 GB, 200-FBGA | [C19192462](https://www.lcsc.com/product-detail/C19192462.html): 47 @ $79.85 | — | — | Second source, same ballout class (verify) |
| Micron MT53E1G32D2FW-046 (WT/IT/AAT) | LPDDR4X 4 GB | WT:B C20453120: 0 | — | AAT:C 1,210 @ **$441.60** | Automotive grade only in stock |
| CXMT CXDB5CCAM-MK | LPDDR4X 4 GB | C39047067: **0** @ $89.97 | — | — | Chinese source, used by many RK boards |
| **Samsung KLMBG2JETD-B041** | eMMC 5.1, 32 GB, FBGA-153 | [C2803245](https://www.lcsc.com/product-detail/C2803245.html): 490 @ $45.04; [C5821038](https://www.lcsc.com/product-detail/C5821038.html): 270 @ $40.33 | not listed | not listed | |
| Kioxia THGAMVG8T13BAIL | eMMC 32 GB | C19185995: **0** @ $51.61 | — | — | |
| Micron MTFC32GAPALBH-IT | eMMC 32 GB | C485825: **0** @ $22.89 | — | brokers only | |
| SanDisk SDINBDG4-32G-XI1 | eMMC 32 GB | C2830399: **0** | — | — | |

**Recommendation (memory).**

- **K4UBE3D4AB-MGCL + KLMBG2JETD-B041.** Both are standard 200-ball LPDDR4X and 153-ball eMMC footprints, so the SK hynix and Micron parts are drop-in second sources after the DDR blob is validated.
- Buy the first lot now through LCSC or an agent.
- **For the DIY kit, JLC must have these in stock at order time.** That is the weakest link of the "one design for both editions" goal.

### 7.3 microSD sockets (push-push, low profile)

| MPN | Type | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|
| **Hirose DM3AT-SF-PEJM5** | microSD **push-push**, SMT, R/A | [C114218](https://www.lcsc.com/product-detail/C114218.html): 15,961 @ $1.39 | [77,167 @ $3.55, Active](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DM3AT-SF-PEJM5/2533565) | Newark 3,209; TME 3,939 |
| Molex 104031-0811 | microSD, SMT (push type **UNVERIFIED**) | [C585350](https://www.lcsc.com/product-detail/C585350.html): 3,086 @ $0.83 | [38,441 @ $2.21](https://www.digikey.com/en/products/detail/molex/1040310811/2370379) | 62,492 |
| Molex 503182-1852 | microSD push-push, low profile | C587953: 0 | — | Newark/RS 0. Poor availability |

**Recommendation (SD socket).** **Hirose DM3AT-SF-PEJM5** (push-push, stocked everywhere, JLC-placeable).

---

## 8. HAT pogo interface and internal flat-cable connectors

### 8.1 Spring pins

**No catalog distributor stocks a ready-made 120–128-contact, 4-row, 1.27 mm pogo block.** The realistic options are:

- (a) **discrete SMT spring probes** placed by pick-and-place on a 1.27 mm grid, mating flat ENIG pads on the HAT (maintainers' choice); or
- (b) a custom block from a pogo specialist (CFE, Yokowo, Preci-Dip custom).

Option (a) keeps it multi-source and assembly-friendly.

| MPN | Type | Rating | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|---|
| **Harwin P70-1000045R** | SMT spring probe, "P70 1.27 mm" (Mouser text), tape & reel | 2 A (Newark) | C17702549: **0** @ $1.37 | [5,006 @ $1.04, Active](https://www.digikey.com/en/products/detail/harwin-inc/P70-1000045R/6211189) | 5,759 @ $1.04 | **Best fit**: SMT and 1.27 mm. Also TME, Newark, Verical |
| Harwin P70-2000045R | Same family, other height | — | C20607207: 89 @ $1.90 | — | 6,616 @ $1.08 | Height option |
| Mill-Max 0906-0-15-20-76-14-11-0 | Through-hole micro spring pin, 0.508 mm mounting hole | 2 A | — | [43,902 @ $0.81](https://www.digikey.com/en/products/detail/mill-max-manufacturing-corp/0906-0-15-20-76-14-11-0/1147048) | (Arrow, RS, Verical) | TH means a second process; 100k–1M cycles (Mill-Max page) |
| Mill-Max 0908-0-15-20-75-14-11-0 | Through-hole spring pin | 2 A | C21067326: 0 | [34,782 @ $1.13](https://www.digikey.com/en/products/detail/mill-max-manufacturing-corp/0908-0-15-20-75-14-11-0/1991674) | 103,654 | |
| Mill-Max 0965-0-15-20-80-14-11-0 | **SMT** spring pin | — | C5209815: 0 | — | 305,846 @ $0.61 | Newark lists it as 2.54 mm class, so likely too wide for 1.27 mm (**UNVERIFIED**) |
| Mill-Max 0985-0-15-20-71-14-11-0 | Through-hole spring pin | 2 A (Newark) | — | [103,121 @ $1.04](https://www.digikey.com/en/products/detail/mill-max-manufacturing-corp/0985-0-15-20-71-14-11-0/3635123) | 118,336 | |

**Electrical design notes** (engineering judgement, not measured):

- **Power:** 2 A per pin with derating means **3–5 A needs 4–6 pins per rail per direction**, plus as many ground returns. Budget **~16–20 contacts for power and ground** in a 128-contact layout.
- **High speed:** PCIe Gen2 (5 GT/s) and USB 3 (5 Gb/s) across spring pins need a **G-S-S-G** pattern per differential pair, minimal stub, and characterisation.
  - Inductance per pin (~1 nH class for short probes, **UNVERIFIED**) is tolerable at 2.5 GHz Nyquist if the path is short.
  - Plan a TDR/eye test of a coupon before freezing the pinout.
  - A redriver (e.g. a TI DS80PCI-class or USB 3 redriver) may be needed on the HAT side.
- **CSI-2 4-lane:** D-PHY ≤1.5 Gb/s per lane is easier, but still use a GSG pattern.
- **Mating cycles:** Mill-Max states 100k–1M cycles at mid-stroke. Harwin's P70 cycle rating was **not retrieved**.

**Recommendation (pogo).** **Harwin P70 SMT probes** on the main board, at 1.27 mm pitch in 4 rows with a GSG pattern for the 5 Gb/s pairs and paralleled power pins, mating ENIG/hard-gold pads on the HAT. Keep the **Mill-Max 0906** as the through-hole second source. Before committing, build a 1-row test coupon to measure insertion loss and contact resistance.

### 8.2 FPC/FFC and board-to-board connectors (main board to side pieces and faceplate)

| MPN | Pitch, positions | LCSC | Digi-Key | Mouser | Notes |
|---|---|---|---|---|---|
| **Hirose FH35C-45S-0.3SHW(50)** | 0.3 mm FPC, 45 pos, back-flip, dual-side contact, 0.9 mm high | [C424664](https://www.lcsc.com/product-detail/C424664.html): 3,599 @ $0.35 | [2,711 @ $3.73, Active](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FH35C-45S-0-3SHW-50/4515399) | 3,337 | **Display / faceplate (MIPI DSI) candidate**. The dual-row contact allows interleaved grounds |
| **Hirose FH26W-45S-0.3SHW(60)** | 0.3 mm FPC, 45 pos | [C424655](https://www.lcsc.com/product-detail/C424655.html): 9,241 @ $0.35 | [7,124 @ $2.89](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FH26W-45S-0-3SHW-60/5132505) | 17,969 | Best stocked 0.3 mm |
| **Molex 505110-4091** | 0.5 mm FPC, 40 pos | [C588009](https://www.lcsc.com/product-detail/C588009.html): 15,918 @ $0.41 | [23,619 @ $2.25](https://www.digikey.com/en/products/detail/molex/5051104091/5254662) | 14,986 | Easy for the DIY kit |
| Hirose BM28B0.6-40DS/2-0.35V(51) + BM28B0.6-40DP/2-0.35V(51) | 0.35 mm board-to-board, 40 pos | C6132031: 474 @ $0.34; C5953962: 696 @ $0.27 | not found | not found | For rigid-flex or stacked sub-boards |
| I-PEX 20455-040E-12 (CABLINE-VS, micro-coax) | 0.5 mm, 40 pos | only a clone (Lian Xin C53327329: 2,742) | not found | not found | For 5 Gb/s over cable. Genuine I-PEX availability **UNVERIFIED** |

**Recommendation (internal connectors).**

- **FH35C** for the faceplate (DSI + touch + ALS + mic).
- **FH26W** for low-speed side pieces.
- **Do not route PCIe or USB 3 through an FPC.** Keep the 5 Gb/s lanes on the main PCB straight to the pogo field, because the pogo block sits on the main board.

---

## 9. USB-C receptacle, ESD and redriver

### 9.1 Interface reality

The device's USB-C carries **USB 2.0 OTG + PD + debug UART**. The UART can go over SBU with a mux, or over USB CDC from the RP2350. The single USB 3 host lane (`combphy1`) should go to the HAT.

### 9.2 Candidates

| MPN | Type | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|
| **GCT USB4105-GF-A** | USB 2.0 Type-C, 16-pin, SMT (with TH shell pegs) | C3020560: **0** (variants -060: 1,133; -120: 2,893) | [91,262 @ $0.80, Active](https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198441) | 422,342 |
| GCT USB4085-GF-A | USB 2.0 Type-C, through-hole, top mount | [C7095263](https://www.lcsc.com/product-detail/C7095263.html): 3,506 @ $1.41 | [84,200 @ $0.91](https://www.digikey.com/en/products/detail/gct/USB4085-GF-A/9859662) | 133,248 |
| **Amphenol 12401610E4#2A** | **USB 3.1** Type-C, 24-pin, SMD R/A (Arrow: automotive) | [C5119948](https://www.lcsc.com/product-detail/C5119948.html): 6,644 @ $1.35 | [80,288 @ $1.43, Active](https://www.digikey.com/en/products/detail/amphenol-cs-commercial-products/12401610E4-2A/5775519) | 10,547 |
| JAE DX07S024JJ2R1300 | **USB 3.2** Type-C, 24-pin, top mount | [C2977282](https://www.lcsc.com/product-detail/C2977282.html): 2,947 @ $0.68 | [41,707 @ $2.72](https://www.digikey.com/en/products/detail/jae-electronics/DX07S024JJ2R1300/5246067) | 8,684 |
| Würth 632723300011 | USB 3.1 Type-C, 24-pin | [C2830802](https://www.lcsc.com/product-detail/C2830802.html): 270 @ $6.45 | [23,754 @ $4.37](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/632723300011/5806670) | 38,882 |
| Amphenol 12402012E212A | USB 2.0 Type-C, 24-pin R/A | [C5150972](https://www.lcsc.com/product-detail/C5150972.html): 12,815 @ $0.74 | not checked | Newark 14,558 |
| Molex 217175-0001 | 6-pin **power-only** Type-C | — | — | 10,496. **Rejected**: no data lines |

- **Waterproof:** no IPx7 Type-C receptacle was verified in stock this session. Mid-mount waterproof variants exist in JAE DX07 and Amphenol 124 series catalogs (**UNVERIFIED** MPNs). If IP rating is a requirement, quote these separately.
- **Mid-mount:** none of the verified parts is explicitly listed as mid-mount; check against z-height.

### 9.3 ESD and switching

| MPN | Function | LCSC | Digi-Key | Mouser |
|---|---|---|---|---|
| **TI TPD4E05U06DQAR** | 4-ch low-cap ESD for D+/D− and SS pairs, USON-10 | [C138714](https://www.lcsc.com/product-detail/C138714.html): 211,901 @ $0.083. Pin-compatible second sources at LCSC: Tech Public C2827646, MSKSEMI C2836386, BORN C920310 | Digi-Key lists a **Goodwork-branded** TPD4E05U06DQAR, [27,000](https://www.digikey.com/en/products/detail/goodwork/TPD4E05U06DQAR/29515395), so check the brand | TI 0 at Mouser; Newark 35,363 |
| TI TPD8S300ARUKR | CC/SBU overvoltage (20 V short) + ESD | C2649824: 60 | not retrieved | 2,800 @ $1.27 |
| TI HD3SS3212RKSR | 2:1 10 Gb/s mux (USB 3 orientation or C-port/HAT switch). Linux control via `gpio-sbu-mux`/`gpio-mux` (generic) | [C129320](https://www.lcsc.com/product-detail/C129320.html): 338 @ $1.57 | [73 @ $2.21](https://www.digikey.com/en/products/detail/texas-instruments/HD3SS3212RKSR/5278905) | 1,566 |

- **Redriver:** not needed for a USB 2 port.
- For the HAT USB 3/PCIe lanes through pogo pins, plan a footprint for a redriver on the HAT side. Debian enables `TYPEC_MUX_PTN36502` and `NB7VPQ904M` for Type-C redrivers, but they are not needed on the device side.

**Recommendation (USB-C).** **GCT USB4105-GF-A + TPD4E05U06 + TPD8S300A** (CC/SBU protection, which matters with PD up to 14–20 V). Only if product management wants USB 3 on the C port, switch the single USB 3 host lane between the HAT and the C port with an HD3SS3212 and a USB 3 receptacle (12401610E4#2A). Note that this cannot be simultaneous with HAT USB 3.

---

## 10. Debian kernel-config requests (one bug, all gaps)

All of these are in mainline and currently off in `linux-config-7.2` (arm64). File them as one wishlist bug against `src:linux` in Debian, asking to enable them as modules on arm64.

| Symbol | Needed for | Mainline since |
|---|---|---|
| `CONFIG_SND_SOC_CS43130` | CS43198 DAC (**mandatory**) | long-standing |
| `CONFIG_BATTERY_MAX17042` and/or `CONFIG_BATTERY_BQ27XXX_I2C` | MAX17055 / BQ27Z561 gauge | long-standing |
| `CONFIG_BT_NXPUART` | IW612 Bluetooth | 6.x |
| `CONFIG_NXPWIFI_SDIO` | IW612 Wi-Fi | **7.3** (needs a 7.3+ backport) |
| `CONFIG_MFD_BQ257XX`, `CONFIG_CHARGER_BQ257XX`, `CONFIG_REGULATOR_BQ257XX` | BQ25792 (upgrade path) | 7.2 for BQ25792 |
| optional: `CONFIG_BMI270_I2C`, `CONFIG_INV_ICM45600_I2C`, `CONFIG_OPT4001`, `CONFIG_DRM_PANEL_NEWVISION_NV3051D`, `CONFIG_DRM_PANEL_SITRONIX_ST7701`, `CONFIG_TOUCHSCREEN_HYNITRON_CSTXXX` | Only if those alternates are chosen | — |

Until Debian ships these, publish a DKMS package that builds the in-tree modules against Debian's `linux-headers` and `linux-kbuild` for 7.2. This keeps "stock Debian kernel" true.

---

## 11. Summary BOM: recommended parts

| # | Function | Recommended MPN | Mfr | Debian 7.2 | LCSC (stock @ qty-1) | Digi-Key | Mouser | Second source |
|---|---|---|---|---|---|---|---|---|
| 1 | Display | 3.5" 640×480 IPS MIPI-DSI, ST7703 (custom module, RG353V-V2-compatible) | module house | on | n/a | n/a | n/a | second module house, same IC |
| 2 | Touch | GT911 (on CTP) / FT6336U | Goodix / FocalTech | on | — | — | — | each other |
| 3 | Charger | BQ25895RTWR | TI | on | C80200: 5,954 @ $2.13 | 0, Active, $3.35 | 3,608 @ $3.36 | SC89890H (Southchip, 0 stock) |
| 4 | TCPC | FUSB302BMPX | onsemi | on | C132291: 1,648 @ $0.84 | 5,545 @ $1.18 | 5,563 @ $1.10 | RT1715WSC (driver-level) |
| 5 | Gauge | MAX17055EWL+T | ADI | off → request | C2682627: 5,840 @ $1.52 | 5,988 @ $4.66 | 10,332 @ $4.55 | BQ27Z561 (request) |
| 6 | HAT eFuse | TPS259470ARPWR ×2 | TI | n/a | C3662799: 3,766 @ $1.29 | 76,492 @ $2.06 | 17,695 @ $1.97 | TPS259472A/474L |
| 7 | Power mux | TPS2121RUXR | TI | n/a | C485916: 25,557 @ $0.92 | 16,584 @ $2.44 | 18,252 @ $2.44 | — |
| 8 | Battery | 805060 / 104050 1S LiPo pack, PCM + NTC + locking connector | cell maker (quote) | n/a | not verified | not verified | not verified | second cell maker |
| 9 | Wi-Fi/BT | LBES5PL2EL-923 (Type 2EL) | Murata | off → 7.3 + request | C23572665: 0 | 938 @ $20.30 | 2,820 @ $20.71 | MAYA-W271-00B (u-blox, same IW612) |
| 10 | DAC ×2 | CS43198-CNZR | Cirrus | off → request | C1554755: 346 @ $5.38 | 471 @ $18.19 | 1,274 @ $18.19 | none |
| 11 | HP amp ×4 | OPA1622IDRCR | TI | n/a | C2876559: 666 @ $3.03 | 4,558 @ $7.43 | 1,952 @ $7.43 | none |
| 12 | MCLK 44.1k family | CCHD-957-25-45.1584 (proto) → measured production part | Crystek | n/a | SCTF C2901589 (alt) | 47 @ $33.00 | 265 @ $26.08 | NDK NZ2520SDA (quote) |
| 13 | MCLK 48k family | CCHD-957-25-49.152 (proto) | Crystek | n/a | SCTF C2901591 (alt) | not checked | 0 @ $34.23 | as above |
| 14 | 3.5 mm jack | SJ2-35894D-SMT-TR | Same Sky | n/a | not checked | 2,955 @ $1.53 | 436 | SJ-43514-SMT-TR |
| 15 | 4.4 mm jack | Pentaconn 4.4 mm (MPN by quote) | Nippon DICS | n/a | not found | not found | not found | none (**risk**) |
| 16 | Speaker amp | MAX98357AETE+T | ADI | on | C910544: 23,202 @ $1.32 | 38,518 @ $4.08 | 23,563 @ $4.08 | MAX98360A (same driver) |
| 17 | Speaker | CMS-151125-078S-67 | Same Sky | n/a | — | 719 @ $3.04 | 890 | PUI AS01508MR-6-R |
| 18 | Coprocessor | RP2354A | Raspberry Pi | n/a | C41378174: 8,081 @ $1.26 | not retrieved | not found | RP2350A + QSPI flash |
| 19 | IMU | LSM6DSV16XTR | ST | on | C5267406: 7,764 @ $3.36 | 0, Active | 4,510 @ $5.75 | LSM6DSOXTR (same driver/footprint) |
| 20 | ALS ×2 | VEML6030 | Vishay | on | C132182: 10,967 @ $0.72 | 9,408 @ $1.59 | 10,103 | LTR-303ALS-01 |
| 21 | Mics ×2 | IM73D122V01XTMA1 | Infineon | on (PDM + DMIC) | C5563886: 5,352 @ $2.88 | 36,572 @ $2.72 | 15,038 | SPH0641LU4H-1 |
| 22 | LPDDR4X 4 GB | K4UBE3D4AB-MGCL | Samsung | n/a | C5827966: 236 @ $82.09 | — | — | H9HCNNNCPMMLXR-NEE (SK hynix) |
| 23 | eMMC 32 GB | KLMBG2JETD-B041 | Samsung | n/a | C2803245: 490 @ $45.04 | — | — | MTFC32GAPALBH-IT, THGAMVG8T13BAIL (both 0 now) |
| 24 | microSD | DM3AT-SF-PEJM5 | Hirose | n/a | C114218: 15,961 @ $1.39 | 77,167 @ $3.55 | (Newark 3,209) | Molex 104031-0811 |
| 25 | HAT pogo ×~128 | P70-1000045R | Harwin | n/a | C17702549: 0 | 5,006 @ $1.04 | 5,759 @ $1.04 | Mill-Max 0906 (TH) |
| 26 | Faceplate FPC | FH35C-45S-0.3SHW(50) | Hirose | n/a | C424664: 3,599 @ $0.35 | 2,711 @ $3.73 | 3,337 | FH26W-45S-0.3SHW(60) |
| 27 | USB-C | USB4105-GF-A | GCT | n/a | 0 (variants in stock) | 91,262 @ $0.80 | 422,342 | 12402012E212A (Amphenol) |
| 28 | USB ESD | TPD4E05U06DQAR | TI | n/a | C138714: 211,901 @ $0.083 | (Goodwork brand) 27,000 | 0 (TI) | Tech Public / MSKSEMI / BORN |
| 29 | CC/SBU protection | TPD8S300ARUKR | TI | n/a | C2649824: 60 | not retrieved | 2,800 @ $1.27 | — |

All LCSC/JLC parts above are in JLC's **extended** library (assembly fee per unique part). The PMIC (RK809/RK817) is decided elsewhere and is listed in §2.1.

---

## 12. Risks

1. **DAC driver off in Debian** (`SND_SOC_CS43130`). Without the config change, OpenDAP has no main audio path on the stock kernel. *Mitigation:* the Debian bug in §10 plus a DKMS module in the interim.
2. **Wi-Fi 6 needs kernel 7.3+ and two Debian config changes.** If trixie-backports stays on 7.2 or Debian declines, there is no Wi-Fi or BT. *Mitigation:* early prototypes with Type 1MW; follow trixie-backports 7.3; upstream-first relationship with the Debian kernel team.
3. **Memory price and availability.** Catalog LPDDR4X is broker-priced ($80 at LCSC; $386–$468 at Mouser/Newark), and eMMC 32 GB is ~$40–45 with only one stocked brand. It threatens the BOM target and the DIY kit, because JLC must have stock at order time. *Mitigation:* agent quotes (Samsung/SK hynix/CXMT), buffer stock, and validate two DRAM parts on the DDR blob.
4. **4.4 mm Pentaconn jack is single-source and not at any distributor.** *Mitigation:* quote Nippon DICS early, consider a qualified licensed alternative, and keep the 3.5 mm jack as a second output.
5. **No catalog-stocked display with a Debian-enabled driver.** The panel is a custom or marketplace item, its init sequence may differ, and touch must be added. *Mitigation:* insist on an ST7703 controller, request the init table, and budget an upstream patch.
6. **Battery sourcing and EU Art. 11.** No cell was verified at distributors, and user replaceability from 18 Feb 2027 constrains the mechanics. *Mitigation:* two qualified cell makers with certificates; a connectorised, door-accessible pack.
7. **Charger choice.** BQ25792 (bidirectional, newest) was dropped by Digi-Key, Mouser has 34, and Debian has it off. BQ25895 cannot supply 3–5 A to the HAT. *Mitigation:* a separate HAT power stage behind TPS25947 eFuses, and the BQ25792 as a later upgrade.
8. **Pogo interface signal integrity and cost.** 5 Gb/s over spring pins is unproven for this geometry, about 128 × $1 is a large BOM line, and the probes have a single SMT source at 1.27 mm (Harwin). *Mitigation:* a test coupon (TDR, eye diagram), a GSG pinout, HAT-side redriver pads, and volume quotes from Harwin/Mill-Max/CFE.
9. **Single lane of USB 3 and PCIe on the RK3566.** HAT and C-port features compete. *Mitigation:* fix the policy now (HAT owns both); the USB-C port is USB 2.
10. **Price spread and authenticity on LCSC** (CS43198 at $5.38 vs $18.19 authorized; TPD4E05U06 "brand" clones at Digi-Key). *Mitigation:* the commercial edition buys Cirrus/TI parts from authorized channels; the kit BOM pins exact LCSC C-codes.
11. **Thin stock on some recommended parts.** TI TPD8S300A at LCSC: 60; RP2354B: 3; LSM6DSV16X at Digi-Key: 0. *Mitigation:* the second sources listed per item.
12. **Data freshness.** All stock figures are a snapshot from 2026-10-21/22. PCBWay was not checked.

---

## Sources

- Debian config: `linux-config-7.2_7.2.9-1~bpo13+1_arm64.deb` from `http://deb.debian.org/debian/pool/main/l/linux/`; [salsa kernel-team/linux, branch debian/7.2/trixie-backports](https://salsa.debian.org/kernel-team/linux/-/tree/debian/7.2/trixie-backports); [packages.debian.org contents search](https://packages.debian.org/) for `sd_w61x_v1.bin.se` (firmware-misc-nonfree) and `brcmfmac43455-sdio*` (firmware-brcm80211).
- Mainline sources (master and tags v7.2/v7.3) from [torvalds/linux](https://github.com/torvalds/linux):
  - `drivers/gpu/drm/panel/panel-sitronix-st7703.c`, `panel-newvision-nv3051d.c`, `panel-sitronix-st7701.c`, `panel-himax-hx8394.c`;
  - `sound/soc/codecs/cs43130.c`, `max98357a.c`, `tas2562.c`, `nau8315.c`;
  - `drivers/power/supply/bq25890_charger.c`, `bq257xx_charger.c`, `bq27xxx_battery_i2c.c`, `rk817_charger.c`, `cw2015_battery.c`;
  - `drivers/mfd/bq257xx.c`;
  - `drivers/net/wireless/nxp/nxpwifi/` and `drivers/net/wireless/marvell/mwifiex/sdio.c`;
  - `drivers/bluetooth/btnxpuart.c`;
  - `drivers/usb/typec/tcpm/tcpci_rt1711h.c`;
  - `drivers/iio/...` (`st_lsm6dsx`, `inv_icm42600`, `veml6030`, `ltr501`, `vcnl4000`, `opt3001`);
  - `sound/soc/rockchip/rockchip_pdm.c`;
  - `arch/arm64/boot/dts/rockchip/rk3566-base.dtsi`, `rk356x-base.dtsi`, `rk3566-anbernic-*.dts*`, `rk3566-powkiddy-*.dts*`.
- [linux-firmware (GitLab mirror)](https://gitlab.com/kernel-firmware/linux-firmware): `nxp/sd_w61x_v1.bin.se`, `nxp/uartspi_n61x_v1.bin.se`.
- Stock and price: JLCPCB parts API / [LCSC product pages](https://www.lcsc.com/); Digi-Key product pages (linked inline); Mouser, Newark, Arrow, TME and Verical via [FindChips](https://www.findchips.com/).
- Spring pins: [Mill-Max 0906](https://www.mill-max.com/products/pin/0906), [0965](https://www.mill-max.com/products/pin/0965), [0985](https://www.mill-max.com/products/pin/0985) product pages; [Harwin P70-1000045R](https://www.harwin.com/products/P70-1000045R/).
- Prior project research: `docs/research/2026-10-soc-dac-pmic.md`.
