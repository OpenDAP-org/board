# OpenDAP: SoC, DAC, PMIC and supervisor MCU selection

- **Date:** 2026-10-21
- **Scope:** open digital audio player (DAP), 100 % mainline Linux, with rear HATs (NAS, camera, recorder, oscilloscope, radio, powerbank).
- **Reference kernel status:** `torvalds/linux` master has `VERSION = 7` and `PATCHLEVEL = 3` ([Makefile](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Makefile)). Everything marked **7.4-rc1** is queued for the current merge window (Collabora treats it as a given), but today it is not in any release. Everything marked **sent** is on a mailing list and is **not** in mainline.
- **Convention:** **UNVERIFIED** = I found no primary source confirming it. **(secondary source)** = only press or forum coverage exists.

> **How this was verified.** The per-block status for Rockchip comes from Collabora's tables (GitLab repository, read via the API on 2026-10-21). For NXP, the presence of nodes in the mainline DT was checked by downloading the `.dtsi` files from `torvalds/linux` master. For codecs, chargers and TCPCs, the mainline `Kconfig` and source files were downloaded and their `of_match` tables (`.compatible`) were read. None of this has been tested on hardware: it is desk research and does not replace a board bring-up.

---

## 0. Executive summary

| | Decision |
|---|---|
| **Primary SoC (v1)** | **NXP i.MX 8M Plus (quad A53)**. It is the only candidate in which **all** the blocks we require (DSI, CSI + ISP with libcamera, PCIe, USB3, SAI/TDM, GPU, **NPU with Teflon**, VPU, thermal) have a mainline DT node and a mainline driver today. It also has NXP's 15-year longevity program. |
| **Alternative SoC / v2** | **Rockchip RK3576**. It offers better performance per watt, a Mali GPU with Vulkan, a 6 TOPS NPU, 3 four-lane CSI inputs and a lower price, with momentum from Collabora and Flipper One. But today mainline lacks things that are critical for a battery-powered device: **full suspend, NPU (PATCH v14 not merged), ISP (TODO), DDR DMC/devfreq and PWM**, and it only has **PCIe Gen2 x1**. |
| **On watch** | **i.MX 95**: it is the natural successor, but in mainline 7.3 **there are no display, camera or NPU nodes**, and the Neutron NPU driver is **blocked** because its userspace is a closed blob. **RK3588** is ruled out for the handheld due to power consumption and package; it only makes sense if a HAT requires PCIe3 x4. |
| **DAC** | In mainline: **Cirrus CS43131 / CS43198** (`cs43130.c`), **AKM AK4497 / AK4458** (`ak4458.c`), **TI PCM1792A** (`pcm179x`), **TI PCM5242 / PCM5142** (`pcm512x`) and **WM8741** (`wm8741.c`). **ESS Sabre (ES9038/ES9039) and ROHM BD34301 have no mainline driver.** |
| **Power** | SoC PMIC (**PCA9450** on i.MX 8M Plus, **RK806** on RK3576) plus a **TI BQ25792** charger (`bq257xx`, buck-boost with OTG for the powerbank HAT), a **BQ27Z561** (`bq27xxx`) or **MAX17055** (`max17042`) gauge, and a **FUSB302** or **RT1715 / ET7304** TCPC with TCPM. |
| **Supervisor MCU** | **STM32U0 or STM32L0/G0** as an ultra-low-power *always-on* supervisor. **RP2350 (stepping A4)** if a PIO-based SWD/JTAG probe is also wanted. Both have an Embassy HAL. |

---

## 1. SoC comparison table

### 1.1 Hardware

| SoC | CPU | GPU | NPU | Node | PCIe | USB3 | CSI-2 + ISP | DSI | I2S/TDM/SAI | Package |
|---|---|---|---|---|---|---|---|---|---|---|
| **RK3576** | 4×A72 + 4×A53 + M0 | Mali-G52 MC3 | 6 TOPS INT8 (RKNN) | 8 nm (**UNVERIFIED**, press) | 2×PCIe 2.1 x1, combo with SATA; the 2nd lane is also a combo with USB3 | 1×USB 3.2 Gen1 OTG Type-C with DP alt, plus 1 USB3 host on the combo | 3×4-lane CSI-2 (1 C/D-PHY and 2 D-PHY). 16 MP ISP | 1×4-lane DSI-2 (C/D-PHY) | 5 SAI: 2 with 4T/4R lanes and 3 with 1T/1R; 8-channel PDM; ASRC | FCCSP698L, 16.1×17.2 mm, **0.6 mm pitch** |
| **RK3588 / 3588S** | 4×A76 + 4×A55 | Mali-G610 MC4 | 6 TOPS | 8 nm (**UNVERIFIED**) | PCIe 3.0 x4, bifurcable 4×1 / 2×2, plus 3 PCIe2 combos | 2×USB3 OTG (USBDP) and 1 host | 2 DCPHY and 4 D-PHY. ISP 3.x | 2×4-lane DSI | 2×8-channel I2S and 2×2-channel I2S | FCBGA1088, 23×23 mm (pitch **UNVERIFIED**, 0.65 mm is commonly cited). The 3588S is smaller and has less I/O |
| **i.MX 8M Plus** | 4×A53 at 1.8 GHz + M7 | Vivante GC7000UL (3D) and GC520L (2D) | 2.3 TOPS (VeriSilicon VIPNano-SI+) | 14 nm FinFET | 1×PCIe Gen3 x1 | 2×USB 3.0 DRD | 2×CSI-2 and **2 ISPs** (12 MP) | 1×4-lane DSI, plus LVDS and HDMI | 6 SAI ("18× I2S TDM" per NXP), 8-channel PDM, EASRC | FCBGA, 15×15 mm, **0.5 mm pitch** |
| **i.MX 95** | 6×A55 + M7 + M33 | Mali-G310 (Valhall CSF) | eIQ Neutron (2 TOPS per partners) | 16 nm FinFET | 2×PCIe Gen3 x1 | 1×USB 3.0 Type-C and 1×USB 2.0 | 2×4-lane CSI-2 with ISP (Arm Mali-C55) | 1×4-lane DSI, plus LVDS | 5 SAI in the DT ("17× I2S TDM" per NXP) | 19×19 mm with **0.7 mm pitch**, or 15×15 mm with 0.5 mm pitch |
| **i.MX 93** | 2×A55 + M33 | **No 3D GPU** | Ethos-U65 (0.5 TOPS) | 16 nm FinFET (**UNVERIFIED**) | **No PCIe** | **No USB3** (2×USB2) | 1×2-lane CSI-2 with ISI, no ISP (**UNVERIFIED**) | 1×DSI (**UNVERIFIED**) | SAI | 14×14, 11×11 or 9×9 mm (**UNVERIFIED**) |
| **MediaTek Genio 700 (MT8390)** | 2×A78 + 6×A55 | Mali-G57 MC3 | MediaTek APU | 6 nm (**UNVERIFIED**) | PCIe Gen3 (**UNVERIFIED**) | Yes | Proprietary ISP | Yes | Yes | **UNVERIFIED** |
| **TI AM67A / J722S** | 4×A53 + R5F + 2×C7x DSP | IMG BXS-4-64 | C7x/MMA (~4 TOPS) | 16 nm (**UNVERIFIED**) | 1×PCIe Gen3 x1 | 1×USB3 | 4×CSI-2. The VPAC ISP depends on TI firmware | DSI and DPI | McASP | **UNVERIFIED** |
| **Allwinner T527 / A733** | 8×A55 (T527); 2×A76 + 6×A55 (A733) | Mali-G57 (T527); IMG (A733) | Vivante 2 TOPS (T527) | 22 nm / 12 nm (**UNVERIFIED**) | PCIe on A733 | Yes | Yes | Yes | Yes | **UNVERIFIED** |

Hardware sources:

- RK3576: [Rockchip Brief Datasheet](https://macrogroup.ru/upload/iblock/5ae/pcppugofyszbwkpynnc1pn5ceaxyd0sg/RK3576-Brief-Datasheet.pdf). It is an official PDF hosted by a distributor; the package, the 4T/4R SAIs, the PCIe/SATA/USB3 combos and the CSIs come from it.
- RK3588: [RK3588J datasheet at LCSC](https://datasheet.lcsc.com/lcsc/2403201054_Rockchip-RK3588J_C22364189.pdf) and [FET3588 SoM sheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5731/FET3588-C%20SoM.pdf) (secondary source) for PCIe bifurcation.
- i.MX 95: [NXP product page](https://nxp.com/products/iMX95).
- i.MX 8M Plus: [NXP product page](https://www.nxp.com/products/i.MX8MPLUS).
- The Genio, TI and Allwinner rows are indicative only: they are ruled out before the detail is needed.

### 1.2 Mainline status per block

Legend: ✅ in a mainline release (version given), 🟡 queued for 7.4-rc1 or partial, 🟠 sent to the list, not merged, ❌ nobody is working on it or it is blocked.

| Block | RK3576 | RK3588 | i.MX 8M Plus | i.MX 95 | i.MX 93 |
|---|---|---|---|---|---|
| CPU, clk, pinctrl, pmdomain | ✅ 6.12–6.13 | ✅ 5.19–6.4 | ✅ (mature since 5.x) | ✅ (SCMI) | ✅ |
| cpufreq | ✅ 6.13 (OPP in the DT) | ✅ 6.11 | ✅ | ✅ (via SCMI, details **UNVERIFIED**) | ✅ |
| Thermal | ✅ 6.17 (TSADC) | ✅ 6.4 | ✅ TMU (`fsl,imx8mp-tmu` in the DT) | ✅ SCMI thermal zones in the DT | ✅ |
| DDR devfreq (DMC) | ❌ (DFI 🟠) | ❌ DMC TODO | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** |
| PCIe | ✅ PCIe2 6.16 (DT) | ✅ PCIe3 and PCIe2 6.6–6.7 | ✅ `fsl,imx8mp-pcie` | ✅ `fsl,imx95-pcie` ×2 | n/a |
| PCIe in system suspend | 🟠 PATCH v6 | 🟠 PATCH v6 | **UNVERIFIED** | **UNVERIFIED** | n/a |
| USB3 | ✅ USB3 DRD (DT 6.14); Type-C orientation pending | ✅ 6.7–6.10 | ✅ `fsl,imx8mp-dwc3` ×2 | ✅ `nxp,imx95-dwc3` | n/a |
| DSI | ✅ 6.18 (controller and PHY) | ✅ 6.16 | ✅ `fsl,imx8mp-mipi-dsim` and LCDIF | ❌ **no DPU/DSI node in the 7.3 DT** | (not evaluated) |
| CSI-2 (receive) | 🟡 VICAP and CSI 7.4-rc1 (CSI driver 7.2, D-PHY 7.4) | ✅ VICAP and CSI 7.2 (DCPHY 🟠) | ✅ `fsl,imx8mp-mipi-csi2` ×2 and ISI | ❌ no node in the 7.3 DT | ✅ (not evaluated in detail) |
| ISP + libcamera | ❌ ISP TODO; only libcamera's GPU softISP remains | 🟠 rkisp2 PATCH v3 (Ideas on Board) | ✅ `fsl,imx8mp-isp` ×2 (rkisp1) and rkisp1 IPA in libcamera | 🟡 the Mali-C55 driver exists in mainline, but there is no i.MX 95 node in the 7.3 DT | n/a |
| Audio (SAI/I2S/TDM) | ✅ SAI 6.16 (`rockchip_sai.c`, TDM, slave mode) | ✅ I2S 6.2 and SAI | ✅ `fsl,imx8mp-sai` ×6, MICFIL, EASRC | ✅ `fsl,imx95-sai` ×5, MICFIL | ✅ |
| GPU (kernel and Mesa) | ✅ Panfrost, DT 6.13 (G52: conformant GLES 3.1, Vulkan 1.3) | ✅ Panthor 6.10 (G610: conformant GLES 3.1 and Vulkan 1.4) | ✅ etnaviv (`vivante,gc` in the DT) | ✅ Panthor, `arm,mali-valhall-csf` node in the DT | ❌ no GPU |
| NPU | 🟠 rocket with RK3576 support, PATCH v14 (2026-09) | ✅ rocket 6.18 with Teflon in Mesa | ✅ etnaviv (kernel 6.9) and Teflon (Mesa 24.1) | ❌ `accel/neutron` blocked by a userspace blob | ✅ `accel/ethosu` (6.19) and Gallium Ethos in Mesa |
| VPU decode | ✅ H.264/H.265 7.0 (VP9 and AV1 in development) | ✅ H.264/H.265 7.0, AV1 6.7, VP8/MPEG2 6.12 | ✅ Hantro G1/G2 in the DT | 🟡 JPEG; VPU with `vpu-csr` node (**UNVERIFIED**) | n/a |
| VPU encode | ❌ | 🟡 JPEG only (H.264 WIP) | **UNVERIFIED** (VC8000E) | **UNVERIFIED** | n/a |
| Suspend-to-RAM | 🟠 **partial**: upstream TF-A supports it, but full-system suspend aborts with brcmfmac and PCIe PM is missing | 🟠 **partial**: "full system suspend fails in a later step" | ✅ widely used (**UNVERIFIED** with a primary citation) | **UNVERIFIED** | **UNVERIFIED** |
| PWM | 🟠 PATCH v5 | ✅ 6.3 | ✅ | ✅ `fsl,imx7ulp-pwm` | ✅ |

Sources for table 1.2:

- RK3576: [Collabora mainline status table](https://gitlab.collabora.com/hardware-enablement/rockchip-3588/notes-for-rockchip-3576/-/blob/main/mainline-status.md) (read on 2026-10-21) and the [NPU PATCH v14](https://lore.kernel.org/linux-rockchip/20260924102135.92217-1-gahing@gahingwoo.com/).
- RK3588: [Collabora mainline status table](https://gitlab.collabora.com/hardware-enablement/rockchip-3588/notes-for-rockchip-3588/-/blob/main/mainline-status.md), the [rkisp2 v3 series](https://lore.kernel.org/linux-media/20260827-rkisp2-v3-0-e91ff0a604d6@ideasonboard.com/) and the [PCIe system PM v6](https://lore.kernel.org/linux-rockchip/20260908-rockchip-pcie-system-suspend-v6-0-fbabcca9921b@collabora.com/).
- Suspend on Rockchip: [Sebastian Reichel's cover letter, 2026-03-16](https://lkml.iu.edu/2603.2/01733.html) and the [TF-A Rockchip platform documentation](https://git.org.ru/Djam/arm-trusted-firmware/src/commit/04b2fb42b171e3fbf2ef823558ac5b0119663dc7/docs/plat/rockchip.rst) (mirror: "suspend/resume system" for RK3576).
- Rocket: [kernel documentation](https://kernel.org/doc/html/v7.2-rc2/_sources/accel/rocket/index.rst.txt) and [Phoronix, merged in 6.18](https://www.phoronix.com/news/Rockchip-NPU-Linux-Mesa).
- Mesa: [Panfrost](https://docs.mesa3d.org/drivers/panfrost.html) and [Teflon](https://docs.mesa3d.org/teflon.html).
- i.MX 8M Plus: [`imx8mp.dtsi` in mainline](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/arm64/boot/dts/freescale/imx8mp.dtsi), [ISP binding in rkisp1](https://lkml.iu.edu/hypermail/linux/kernel/2402.2/00331.html), [libcamera with i.MX8MP](https://lists.libcamera.org/pipermail/libcamera-devel/2024-February/040500.html), [etnaviv NPU on i.MX8MP](https://www.phoronix.com/news/Etnaviv-NPU-Performing-iMX8MP) and [YOLOX on etnaviv (Aug. 2026)](https://www.opensourceforu.com/2026/08/etnaviv-adds-support-for-yolox/) (secondary sources).
- i.MX 95: [`imx95.dtsi` in mainline](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/arm64/boot/dts/freescale/imx95.dtsi), [Mali-C55 driver documentation](https://docs.kernel.org/7.1/_sources/admin-guide/media/mali-c55.rst.txt), [Mali-C55 on i.MX95 according to libcamera](https://libcamera.org/entries/2024-01-31.html), [`accel/neutron` documentation](https://lkml.iu.edu/2603.0/11340.html), [Phoronix on the Neutron block (2026-03-26)](https://www.phoronix.com/news/NXP-Neutron-NPU-User-Blob) and [Panthor on i.MX95 (NXP community)](https://community.nxp.com/t5/i-MX-Graphics/Panthor-driver-on-iMX95/m-p/2300523).
- i.MX 93: [`imx93.dtsi` in mainline](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/arm64/boot/dts/freescale/imx93.dtsi) (contains `fsl,imx93-npu`), [Ethos-U driver v3](https://lkml.iu.edu/hypermail/linux/kernel/2509.3/07231.html), [Mesa Ethos](https://www.phoronix.com/news/Arm-Ethos-Gallium-Merged) and [Linaro](https://www.linaro.org/blog/direct-kernel-access-to-ethos-u65-npu-on-i-mx9-benchmarks-using-latest-kernel-and-mesa-support/). The 6.19 version comes from [a mirror of the v6.19.12 branch](https://git.radix-linux.su/kernel/linux.git/atom/drivers/accel/ethosu?h=v6.19.12) (secondary source).

### 1.3 Other candidates, briefly

- **MediaTek Genio 510/700/1200**: Collabora has the Mali GPU, DSI, audio and Type-C in mainline since 6.14–6.16 ([Collabora, 2025-03](https://www.collabora.com/news-and-blog/news-and-events/mediatek-genio-update-kernel-debian-13-images-and-kernelci.html)), and HDMI since 6.19/7.0 ([Collabora](https://collabora.com/news-and-blog/news-and-events/mediatek-genio-upstream-update-from-hdmi-20-to-booting-uboot-trusted-firmware-a.html)). **There is no ISP or APU (NPU) in mainline (UNVERIFIED that nobody is working on it).** It is ruled out by the camera and NPU requirement.
- **TI AM67A / J722S / AM62P**: the `powervr` driver is being extended to the BXS-4 ([Phoronix](https://www.phoronix.com/news/IMG-AM62P-AM67A-J722S)), and there is a DT for the J722S PCIe and USB ([LKML](https://lkml.iu.edu/hypermail/linux/kernel/2406.1/04663.html)). But the NPU (C7x/MMA) and the ISP (VPAC) depend on TI firmware and the TI SDK, **with no mainline accel driver**. TI's longevity is excellent, but it is ruled out because of the NPU and the ISP.
- **Allwinner T527 / A733**: the T527 boots with 6.18 in community images, and the A733 is in "early stages" with patches pulled from the lists ([CNX](https://www.cnx-software.com/?p=153490), [Armbian](https://newreleases.io/project/github/armbian/build/release/v26.11.0-trunk.54)) (secondary sources). It is ruled out for a product in 2026–2027.

### 1.4 Power, price, longevity and PCB design

| SoC | Typical power | Price (1k units) | Longevity | PCB / chip-down |
|---|---|---|---|---|
| RK3576 | Idle board with the screen off at about 1–2 W (**UNVERIFIED**). With no reliable suspend today, standby battery life is the big risk | ~20–30 USD (**UNVERIFIED**) | Rockchip does not publish a formal program. There are SoMs with "7–10 years" or "10+ years" ([Geniatech](https://www.geniatech.com/product/xpi-3576/), secondary source). The industrial RK3576J variant helps | 0.6 mm pitch with 32-bit LPDDR4x/5. Chip-down is viable in KiCad, but probably with 1-level HDI or 8 layers (**UNVERIFIED**). There are many SoMs (ArmSoM, Radxa, MYIR, Forlinx) |
| RK3588 | 2–4 W idle and more than 10 W under load (**UNVERIFIED**) | ~45–60 USD (**UNVERIFIED**) | Same; the RK3588J exists | 23×23 mm FCBGA with 1088 balls. Too large and hot for a thin handheld |
| **i.MX 8M Plus** | The lowest among the capable ones: A53 at 14 nm, SoC idle well below 1 W (**UNVERIFIED**; NXP publishes a power consumption note) | ~25–45 USD (**UNVERIFIED**) | **15 years** for the i.MX 8M family ([NXP Product Longevity](https://nxp.com/products/product-information/product-longevity); [Purism forum](https://forums.puri.sm/t/nxp-will-manufacture-its-i-mx-8m-processors-till-jan-2033/12937), secondary source). Launched in 2021, which gives roughly 2035–2036 | 0.5 mm pitch on 15×15 mm: **requires HDI** with microvias. Chip-down is possible, but expensive for the DIY kit. There are many SoMs (Toradex Verdin, Variscite, Olimex with open hardware in KiCad, **UNVERIFIED**) |
| i.MX 95 | Moderate: 6 A55 at 16 nm (**UNVERIFIED**) | ~40–60+ USD (**UNVERIFIED**) | 10 years, or **15 years** in industrial, automotive or medical variants ([NXP](https://nxp.com/products/iMX95)) | **0.7 mm pitch on 19×19 mm**: the friendliest of the recent ones for standard PCBs (probably without HDI, **UNVERIFIED**) |
| i.MX 93 | Very low | ~10–20 USD (**UNVERIFIED**) | 15 years (**UNVERIFIED**) | Easy, but does not meet the GPU or PCIe requirements |

---

## 2. Recommendation

### 2.1 Primary: NXP i.MX 8M Plus (quad version, industrial or consumer grade)

Why:

1. **It is the only one that meets all the hard constraints in mainline today**, checked against the 7.3 `.dtsi`:
   - DSI (`samsung-dsim`) and LCDIF.
   - CSI-2 ×2, **ISP ×2 (rkisp1) with IPA in libcamera**.
   - PCIe Gen3 x1.
   - 2 USB3 DRD.
   - 6 SAI with TDM, plus MICFIL and EASRC.
   - etnaviv GPU.
   - **NPU with etnaviv and Teflon, already in Mesa**.
   - Hantro VPU and TMU.
   There are no out-of-tree patches.
2. **Battery**: A53 at 14 nm with mature power domains (`blk-ctrl`), and suspend in use in real products.
3. **Longevity**: 15 years, suitable for the commercial SKU.
4. **Audio**: the SAIs have several data lanes and fractional audio PLLs. Slave mode with local 22.5792 and 24.576 MHz oscillators is supported, which is standard DAP practice.
5. **Open ecosystem**: MNT Reform, Pocket Reform and Librem 5 (the latter on i.MX 8M Quad) demonstrate viability in open hardware (**UNVERIFIED**, the details of each product).

How the I/O is allocated on the i.MX 8M Plus:

| Resource | Use |
|---|---|
| PCIe Gen3 x1 | **To the HAT connector**. The NAS HAT carries a PCIe switch (for example ASM1182e or PI7C9X2G304, transparent to the kernel) with NVMe and a NIC (RTL8125 with `r8169`, or i226 with `igc`) |
| USB3 #1 | On-board USB-C (with PD) |
| USB3 #2 | **To the HAT connector** for an oscilloscope, radio or FPGA with a USB3 bridge |
| CSI #1 (4 lanes) | **To the camera HAT** |
| CSI #2 | Free, or on-board camera |
| 4-lane DSI | On-board display |
| SAI with multi-lane TDM | **To the recording HAT**: 8 or more channels, for example AK5558 (8 channels) or 2× TLV320ADC6140 in TDM |
| Dedicated SAI | On-board DAC |
| uSDHC | On-board SDIO Wi-Fi (for example NXP IW61x with `nxpwifi`, already in mainline) |
| Second uSDHC | SDIO to the HAT |
| eMMC | Internal storage |
| ECSPI, I2C, UART, GPIO | To the HAT |

Limitations to accept:

- The CPU is modest: the Slint UI must use the GL or software renderer, and resolutions around 720p are the sensible target.
- The etnaviv GPU has no conformant Vulkan (**UNVERIFIED**, the exact GLES level).
- The NPU is 2.3 TOPS.
- There is only **one** PCIe lane.
- The 0.5 mm pitch forces HDI.

### 2.2 Alternative / v2: Rockchip RK3576

It should be chosen as **primary** only if both of the following hold:

- (a) the mass production schedule is later than mid-2027, and
- (b) decision gates are accepted under which, if something is not merged, work stops.

Advantages:

- Clearly superior A72 CPU.
- G52 GPU with conformant GLES 3.1 and Vulkan 1.3.
- 6 TOPS NPU.
- 3 four-lane CSIs.
- HEVC and AV1 decoding.
- 5 SAIs, two of them with 4 TX/RX lanes (8 channels of I2S or TDM).
- Lower price.
- **Flipper One** (a handheld with RK3576 and Collabora) is pushing exactly our blocks: suspend, Type-C and DP ([Collabora and Flipper, 2026-05-21](https://collabora.com/news-and-blog/news-and-events/collabora-flipper-opening-up-the-rk3576.html); [CNX](https://www.cnx-software.com/2026/05/21/flipper-one-a-rockchip-rk3576-powered-portable-arm-linux-computer-and-networking-multi-tool/)).

**Mandatory gates** before freezing the schematic with RK3576. Each one must be in a mainline release:

1. Full suspend-to-RAM with PCIe, USB and Wi-Fi active and stable resume. Today: 🟠.
2. RK3576 NPU in `accel/rocket`. Today: PATCH v14.
3. PWM, needed for the backlight. Today: 🟠 PATCH v5.
4. VICAP and CSI, expected in 7.4.
5. Type-C orientation on USBDP. Today: "needs more work".

In addition, the ISP is still **TODO**: the camera would have to use **libcamera's GPU softISP**. libcamera 0.7 (January 2026) added GPU acceleration with OpenGL ([announcement](https://lists.libcamera.org/pipermail/libcamera-devel/2026-January/057034.html)). This is acceptable for a prototype, not for a "GoPro-like" device.

I/O allocation on the RK3576:

- combphy0 (PCIe2 x1) goes to the HAT.
- combphy1 goes to the HAT as a USB3 host or as a second PCIe x1.
- The USB3 OTG with DP alt goes to the on-board USB-C.
- Wi-Fi goes over SDIO.

Caution: PCIe Gen2 x1 gives about 400 MB/s of usable bandwidth, far below what a NAS with NVMe needs.

### 2.3 Why not the others

- **i.MX 95**: it would be the ideal choice in 2027–2028. It has 0.7 mm pitch, 2×PCIe Gen3, Mali-C55 with libcamera, Panthor and 15 years in industrial grade. But today the **mainline DT has no display, camera or NPU**, and the Neutron is **blocked** ([Phoronix](https://www.phoronix.com/news/NXP-Neutron-NPU-User-Blob)). It is worth reviewing every quarter.
- **RK3588**: power consumption, area and missing DMC. It is only useful if a HAT genuinely needs PCIe3 x4.
- **i.MX 93**: it has no GPU, PCIe or USB3. It could serve as a "co-processor" on a HAT, never as the main SoC.

### 2.4 Remaining risks and gaps with the primary

1. **UI performance**: Slint on etnaviv. It must be measured early on an EVK at the planned display resolution.
2. **Single PCIe lane**: the NAS and radio HATs share the lane via a switch, or the radio goes over USB3. This must be defined in the connector specification.
3. **HDI and 0.5 mm pitch**: this raises the cost of the DIY kit. Mitigation: a main board with an **in-house open SoM in KiCad** (HDI, manufacturable at PCBWay), or a commercial SoM with a stable pinout. See the open questions.
4. **Video encoder** for the camera HAT: the mainline status of the VC8000E on i.MX8MP is **UNVERIFIED**. It may force recording in MJPEG or encoding on the CPU.
5. **NPU**: 2.3 TOPS with Teflon, for TFLite INT8 only. Large audio or voice models do not fit.
6. **Suspend**: must be validated with the codec, the TCPC and the gauge as wake sources (GPIO IRQ from the SNVS block or from the MCU).

---

## 3. DAC shortlist with a mainline ASoC driver

All verified in `torvalds/linux` master (7.3) through their `Kconfig` and their `of_match` table.

| Chip | Vendor | Mainline driver (`sound/soc/codecs/`) | Verified compatibles | Output | DAP use |
|---|---|---|---|---|---|
| **CS43131** | Cirrus | `cs43130.c` (`SND_SOC_CS43130`) | `cirrus,cs43130`, `cirrus,cs43131`, `cirrus,cs4399`, `cirrus,cs43198` | 32 bit / 384 kHz DAC with an **integrated** ground-centered **headphone amplifier**, 130 dB DR, 30 mW into 32 Ω ([Mouser](https://www.mouser.ca/cirrus-cs431xx-high-performance-dacs)) | **3.5 mm SE without an external amplifier**. The driver handles load detection and Class-H. For **4.4 mm balanced**, 2× CS43131 (one per channel) is a pattern used in commercial DAPs (**UNVERIFIED** the driver's mono mode) |
| **CS43198** | Cirrus | `cs43130.c` | `cirrus,cs43198` | 2 Vrms **pseudo-differential** line output, 130 dB | Two units plus a differential amplifier give **4.4 mm balanced** |
| **AK4497** | AKM | `ak4458.c` (`SND_SOC_AK4458`) | `asahi-kasei,ak4497`, `asahi-kasei,ak4458` | AK4497: high-end stereo with **differential voltage** output and DSD | A natural fit for a **balanced** amplifier. Availability after the AKM fire (2020): **UNVERIFIED** |
| AK4458 | AKM | `ak4458.c` | (same) | 8 channels, 768 kHz, DSD, TDM | Useful for a multichannel DAC or for 4 differential channels |
| AK4375 | AKM | `ak4375.c` | `asahi-kasei,ak4375` | Low-power DAC with headphone amplifier | Budget option for SE |
| **PCM5242 / PCM5142** | TI | `pcm512x.c` and `pcm512x-i2c.c` | `ti,pcm5242`, `ti,pcm5142`, `ti,pcm5122`… | PCM5242 with **differential output**, internal PLL and miniDSP | Very well tested (Raspberry Pi), mid-range. The differential PCM5242 works for balanced |
| PCM1792A | TI | `pcm179x.c` | `ti,pcm1792a` | Current output, 132 dB | High-end classic, but needs I/V with op-amps: more power and more area |
| WM8741 | Cirrus (Wolfson) | `wm8741.c` | `wlf,wm8741` | Differential | Old; doubtful longevity (**UNVERIFIED**) |
| TAD5212 | TI | `pcm6240.c` | `ti,tad5212` (and the PCM6xx0/TAA/TAD family) | DAC with headphone driver | Modern and low-power; performance below the above (**UNVERIFIED**) |

### No mainline driver (confirmed by absence from `Kconfig`)

- **ESS ES9038Q2M, ES9039Q2M, ES9219 and ES9280.** The only `ES9xxx` in mainline is **Everest**'s `ES9356`, which is SoundWire.
- **ROHM BD34301EKV.** From ROHM only the `bd28623` amplifier exists.

Using ESS would mean **writing and upstreaming** a regmap driver. It is feasible (they are about 1000 lines), but it contradicts "nothing out of tree" until it is merged.

### Headphone amplifiers (analog, no driver beyond enable or volume)

- **OPA1622**: low power and very low THD. It is the reference in DAPs.
- **INA1620**.
- **TPA6120A2**: lots of current, but power-hungry.
- **OPA1612 with BUF634A** for discrete balanced.
- **TPA6130A2** has a mainline driver (`tpa6130a2.c`, volume control over I2C).

GPIO enable is modeled with `simple-audio-amplifier` (`SND_SOC_SIMPLE_AMPLIFIER`, in mainline). Switching between 3.5 and 4.4 mm can be done with `SND_SOC_SIMPLE_MUX`.

### Concrete proposals

| Tier | Composition |
|---|---|
| **A (power / quality balance)** | 2× **CS43131**. 3.5 mm SE directly from one chip and 4.4 mm balanced with both chips in mono mode (validate mono mode in the driver) |
| **B (high end)** | **AK4497** with 2× OPA1622 bridged for 4.4 mm balanced, and differential-to-SE summing for 3.5 mm |
| **C (simple and robust)** | **PCM5242** with OPA1622 |

**Clock:** two low-jitter 22.5792 and 24.576 MHz oscillators switched by GPIO, with the codec or the SoC in slave mode. `rockchip_sai.c` supports `SND_SOC_DAIFMT_BC_FC` and TDM; the i.MX SAIs do as well.

**ADCs for the recording HAT**, all in mainline:

- **AK5558 / AK5552** (`ak5558.c`): 8 channels.
- **TLV320ADC3140, 5140 and 6140** (`tlv320adcx140.c`): 4 channels, daisy-chainable in TDM.
- **PCM1862 to PCM1865** (`pcm186x`).
- **PCM3168A** (`pcm3168a.c`): 8 DACs and 6 ADCs in TDM.
- **CS42448 / CS42888** (`cs42xx8`).

---

## 4. PMIC, charger, fuel gauge and USB-PD (mainline)

| Function | For i.MX 8M Plus | For RK3576 | For i.MX 95 | Mainline driver |
|---|---|---|---|---|
| SoC PMIC | **NXP PCA9450C** | **Rockchip RK806** (over SPI or I2C; in the DT of RK3576 boards since 6.13) | **NXP PF0900** and **PF5300/5301/5302** | `pca9450-regulator` (`REGULATOR_PCA9450`); `rk8xx-i2c` and `rk8xx-spi` with `rk808-regulator` (compatible `rockchip,rk806`); `REGULATOR_PF0900` and `REGULATOR_PF530X` |
| Charger | **TI BQ25792**: 1 to 4 cell buck-boost, 3.6 to 24 V USB-C input, **OTG / reverse** | same | same | `bq257xx` (MFD `bq257xx.c` with `ti,bq25792` and `ti,bq25703a`, plus `bq257xx_charger.c` and `bq257xx-regulator.c` for VBUS in OTG; **UNVERIFIED** that the regulator covers the BQ25792) |
| Charger (alternative) | TI BQ25895 / BQ25896 (1 cell, 5 V OTG) | same | same | `bq25890_charger.c` (`ti,bq25890/2/5/6`) |
| Charger (alternative) | TI BQ2560x / BQ2561x, SGM41542, RT9467 | | | `bq256xx_charger`, `sgm41542`, `rt9467` |
| Fuel gauge | **TI BQ27Z561** (pack gauge with Impedance Track) or BQ27441 | same | same | `bq27xxx_battery_i2c.c` (`ti,bq27z561`, `ti,bq28z610`, `ti,bq27441`…) |
| Fuel gauge (alternative) | **MAX17055** (ModelGauge m5) or MAX17201 | | | `max17042_battery.c` (`maxim,max17055`); `max1720x_battery.c` (`maxim,max17201`) |
| TCPC / PD | **onsemi FUSB302B** | same; Collabora's RK3588 boards use it since 6.18 | same | `fusb302.c` with TCPM |
| TCPC (alternative) | **Richtek RT1715 / RT1711H**, **Etek ET7304**, **Hynetek HUSB311** (merged in 7.1 according to Collabora), NXP PTN5110 (generic TCPCI) | | | `tcpci_rt1711h.c` (`richtek,rt1711h`, `richtek,rt1715`, `etekmicro,et7304`); `tcpci.c` (`nxp,ptn5110`) |
| USB3 mux / retimer | HD3SS3220, or the mux integrated in USBDP (Rockchip) | | | `hd3ss3220.c`; Rockchip `phy-rockchip-usbdp` |

Sources:

- The mainline `Kconfig` files: [`drivers/power/supply/Kconfig`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/power/supply/Kconfig), [`drivers/regulator/Kconfig`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/regulator/Kconfig) and [`drivers/usb/typec/tcpm/Kconfig`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/usb/typec/tcpm/Kconfig).
- The `of_match` tables of [`bq257xx.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/mfd/bq257xx.c), [`bq27xxx_battery_i2c.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/power/supply/bq27xxx_battery_i2c.c), [`max17042_battery.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/power/supply/max17042_battery.c), [`tcpci_rt1711h.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/usb/typec/tcpm/tcpci_rt1711h.c) and [`rk8xx-i2c.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/mfd/rk8xx-i2c.c).
- The [Collabora RK3588 table](https://gitlab.collabora.com/hardware-enablement/rockchip-3588/notes-for-rockchip-3588/-/blob/main/mainline-status.md) for FUSB302 and HUSB311.

**The powerbank HAT (bidirectional)** is built as follows:

- The on-board BQ25792 supports input (charging from the HAT) and OTG output (powering the HAT).
- A VBAT/VSYS rail protected by an *ideal diode* or eFuse (for example TPS25947 or LTC4412) runs through the connector. It has no driver; the supervisor MCU controls it.
- Role negotiation (who charges whom) is decided by the MCU over I2C with the HAT and is exposed to Linux as a `power_supply` through the HAT's gauge. **UNVERIFIED** that a generic driver exists: a simple `power_supply` in the DT, or a small driver, will probably be needed.

### Per-block gating

- i.MX 8M Plus: `imx8mp-blk-ctrl` and GPC pmdomains, in mainline.
- RK3576: pmdomain in 6.12.
- External HAT rails: `regulator-fixed` with GPIO, or load switches with *enable* driven by the MCU.

---

## 5. Supervisor MCU (power, HAT ID, wake)

Role: always on. It handles the PMIC power-up sequence, the power button, reading the HAT EEPROM or ID, controlling the connector's load switches, waking the SoC via GPIO and the watchdog. **It is never in the high-speed data path.**

| MCU | Standby power | Embassy | Notes |
|---|---|---|---|
| **STM32U0** (U031/U073) | Ultra-low: ST's lowest (**UNVERIFIED** exact figure, on the order of hundreds of nA in standby) | `embassy-stm32` covers "all STM32 microcontroller families" ([Embassy](https://github.com/embassy-rs/embassy)) | **Recommended as a pure supervisor.** Cheap, small QFN and easy to solder in the kit |
| STM32L0 / STM32G0 | Very low / low | same | Very long-lived, high-stock alternatives |
| STM32U5 / STM32U3 | Low | same | If USB FS, more RAM or TrustZone is needed |
| **RP2350 (stepping A4)** | Higher than STM32U0 in dormant (**UNVERIFIED** figure) | `embassy-rp` supports "RP2040 and RP23xx" ([Embassy](https://github.com/embassy-rs/embassy)) | The **A4 fixes erratum E9**, a leakage issue on input GPIOs ([Raspberry Pi](https://www.raspberrypi.com/news/rp2350-a4/)). The PIO is ideal for an **SWD/JTAG probe** (debugprobe / CMSIS-DAP firmware). Dual-core and cheap |
| nRF54L / nRF52 | Very low | `embassy-nrf` | Only if BLE is wanted on the supervisor; not needed today |

### SWD/JTAG to the chips on the HATs (FPGAs and MCUs)

- **Option A**, with no MCU in the path: SoC GPIOs with OpenOCD (`linuxgpiod`) or `probe-rs`. Slow, but adequate.
- **Option B**: RP2350 as a CMSIS-DAP probe over USB2 to the SoC. It is not a high-speed data bus, so it does not violate the rule.
- Recommendation: an **STM32U0** supervisor and, if FPGAs need frequent programming, an **optional RP2350** as a probe, or JTAG wired directly to the SoC.

---

## 6. Open questions we need to decide

1. **Schedule.** When is the schematic frozen and when does mass production start? If it is before mid-2027, the choice is i.MX 8M Plus. If it is later, the door reopens for the RK3576 (and the i.MX 95) under the criteria in §2.2.
2. **Chip-down or SoM?** Do we build an **in-house open SoM in KiCad** (SoC, DDR, PMIC and eMMC on HDI) with a 4–6 layer carrier board without HDI? That way the DIY kit buys the assembled SoM and solders the carrier board. Or chip-down on a single HDI board for both SKUs?
3. **PCIe width on the connector**: x1 (i.MX8MP / RK3576) or x2–x4. Do we require a PCIe switch on the NAS HAT, or do we define the NAS as "1 NVMe plus USB3 Ethernet"?
4. **HAT connector electrical specification**: differential pairs (PCIe, USB3, 4-lane CSI), maximum impedance and length, pin count and specific connector (for example high-speed Samtec or Hirose). This is critical for signal integrity of PCIe Gen3 and CSI at 2.5 Gbps.
5. **DAC**: dual CS43131 (lower power, no external amplifier) or AK4497 with OPA1622 (higher perceived quality, more power and area). Do we want ESS at the cost of writing and upstreaming a driver?
6. **Display**: size and resolution, and **which DSI panel already has a mainline `drm/panel` driver** (ILI9881C, HX8394, JD9365DA, ST7701… controllers). Touch with Goodix or FocalTech (`goodix`, `edt-ft5x06`) is in mainline.
7. **Wi-Fi/BT**: NXP IW61x with `nxpwifi` in mainline (over SDIO, same NXP longevity), Realtek RTL8822CS with `rtw88` SDIO, or Infineon CYW with `brcmfmac`. Caution: on RK3576, `brcmfmac` currently breaks suspend ([LKML](https://lkml.iu.edu/2603.2/01733.html)). All of them need firmware in `linux-firmware`.
8. **Power targets**: how many days of standby and how many hours of playback with the screen off? That decides whether SoC suspend is essential, or whether a "deep idle" with the MCU cutting rails is enough as plan B.
9. **Camera**: is hardware H.264/H.265 encoding needed for the GoPro-like HAT? On i.MX8MP the mainline encoder is **UNVERIFIED**; on RK3576 it does not exist today.
10. **On-board AI**: which specific models (audio source separation, voice, vision)? Are 2.3 TOPS INT8 with TFLite and Teflon enough, or are the RK3576's 6 TOPS needed?
11. **HAT identification**: an EEPROM in the style of Raspberry Pi HAT+ with a DT overlay loaded by the bootloader (U-Boot) or Linux, or a descriptor read by the MCU? And the overlay format we will upstream.
12. **Licensing and firmware**: the DDR training blob (Rockchip, "the last binary blob") and NXP's DDR, HDMI and SCU firmware. Is this acceptable for "open hardware"? It must be documented.

---

### Appendix A. What could not be verified and how to close it

- **Actual power consumption** (idle and suspend) of each SoC: measure on an EVK. For i.MX 8M Plus, NXP's power consumption note. For RK3576, an ArmSoM Sige5 or a Radxa ROCK 4D with mainline 7.4.
- **Suspend on i.MX 8M Plus with mainline**: a primary citation is missing. It must be verified on an EVK with `rtcwake -m mem` and the planned set of wake sources.
- **VC8000E encoder (i.MX8MP) in mainline**: not verified.
- **RK3588 pitch and HDI requirement for the RK3576 / i.MX 95**: the vendors' *hardware design guides* still need to be consulted.
- **Availability of the AK4497 / AK4458** and **CS43131 mono mode in `cs43130.c`**: check with the distributor and read the driver.
- **Prices**: all indicative. Quotes must be requested from distributors (Avnet, Arrow, WPI) and from Rockchip.
