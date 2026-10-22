# High-speed I/O topology of the T1 main board (RK3566)

- **Date:** 2026-10-22
- **Status:** Desk research. Nothing in this report is a decision. The recommendation in section 5 is a proposal for the maintainers.
- **Scope:** which high-speed controllers and PHYs the RK3566 really has, how to turn its single USB 3 lane and single PCIe lane into the physical ports the T1 needs, and what the main USB-C, the HAT and the on-board devices end up with.
- **Inputs:** BRD-004, BRD-005, BRD-006, BRD-008, BRD-015, BRD-033, BRD-034, BRD-035, BRD-039 ([`../requirements/README.md`](../requirements/README.md)), HCS-004 and hat-standard ADR 0001 (all-pogo), ADR 0002 (HAT signals leave the board over a flat cable), ADR 0003 (RK3566), and the earlier reports [`2026-10-soc-dac-pmic.md`](2026-10-soc-dac-pmic.md) and [`2026-10-component-selection.md`](2026-10-component-selection.md).
- **Method:** mainline Linux sources read on 2026-10-22 from `torvalds/linux` `master` (top-level `Makefile` reports **7.3**), the Rockchip RK3566 brief and RK3568 datasheet, two Radxa RK3566 schematics, vendor product pages, and stock from FindChips and the JLCPCB/LCSC parts library. Anything not confirmed by a primary source is marked **UNVERIFIED**.

---

## 0. Summary

1. **The RK3566 has one SuperSpeed USB lane, one PCIe lane, one 4-lane CSI-2 input and four USB 2.0 ports.** On the RK3566, `USB3 OTG0` is **USB 2.0 only**: there is no `combphy0`, and mainline forces `maximum-speed = "high-speed"`. The only SuperSpeed controller is `USB3 HOST1`, which is host-only and uses `combphy1`. That PHY is shared with SATA1 and (Q)SGMII. PCIe 2.1 x1 uses `combphy2`, which is shared with SATA2 and (Q)SGMII.
2. **The main USB-C must use OTG0, wired directly.** The BootROM downloads over the OTG port in device mode, and OTG0 is the only dual-role controller. Because OTG0 is USB 2.0 only, the main USB-C can **never** be a USB 3 *device*. It can be a USB 3 *host* only if it borrows HOST1's lane.
3. **USB 3 (two physical ports):** the proposal is a **passive 2:1 mux** (TI HD3SS3212) on the HOST1 lane. It sends the lane to the **HAT by default** or to the **main USB-C** (host only), with a second HD3SS3212 for Type-C orientation. A hub (GL3523, USB5744, VL817) would make both ports usable at the same time. But it costs roughly 0.1 to 0.5 W while active (**UNVERIFIED**), it puts an active device in the HAT path, and BRD-006 only names multiplexers. A mux keeps the HAT's direct, full 5 Gb/s path (HCS-004) and costs under 2 mW.
4. **PCIe (two physical ports):** no on-board device needs PCIe today. Wi-Fi is SDIO, storage is eMMC and microSD, and BRD-033 says on-board PCIe is only nice to have. The proposal is to run **PCIe straight to the HAT**. Reserve an optional **PI3PCIE3212** 2:1 mux footprint, plus a REFCLK switch, for a later on-board consumer. Fan-out, such as several NVMe drives and a NIC, belongs **on the HAT** with a packet switch (PI7C9X2G404EV, ASM2806). Mainline caveat: `pcie-dw-rockchip` is **built-in with `suppress_bind_attrs`** and has **no suspend/resume hooks**. PCIe HATs are therefore cold-plug in v1, and the controller should be enabled by a HAT overlay only when a PCIe HAT is present.
5. **USB 2.0:** OTG0 goes to the main USB-C. HOST1's USB 2 pair goes with the SuperSpeed lane to the HAT. EHCI/OHCI host 0 goes to the **RP2350** (direct, BRD-004/015). EHCI/OHCI host 1 is a **second HAT USB 2 port**. No hub is needed on the SoC side.
6. **Serial console on the main USB-C (BRD-039):** two workable paths. (a) The SoC UART on the **SBU pins**: about 0 W, but it needs a special dongle, because USB 2 cables have no SBU wires. (b) A **debug hub powered from VBUS** (USB 2 hub + USB-UART bridge) in front of OTG0 when the port is a UFP. It works with any cable, shows the console from power-on, keeps MaskROM working, and costs nothing from the battery. A USB 2 switch bypasses it when the T1 is the host.

---

## 1. What the RK3566 actually has

### 1.1 Primary evidence

- **Rockchip RK3566 Brief Datasheet** (block diagram): "PCIe2.1/SATA3.0", "USB3.0 HOST/SATA3.0", "USB2.0 HOST x2", "USB2.0 OTG", "I2S/TDM(8ch) x2, one for HDMI", "I2S/PCM(2ch) x2", "PDM(8ch)", "SPDIF(8ch)", "SDIO 3.0", "Ethernet GMAC x1", "eMMC 5.1", "SD3.0/MMC4.51", "Dual MIPI-DSI_TX", "eDP1.3", "Single LVDS", "E-Ink Interface", "8M ISP", "MIPI-CSI_RX 4 Lane", and the application diagram shows "4 Lanes or 2+2 Lanes" ([rock-chips.com](https://www.rock-chips.com/uploads/pdf/2022.8.26/192/RK3566%20Brief%20Datasheet.pdf)).
- **RK3568 Datasheet V1.0** (the full datasheet; the RK3566 is the reduced variant). Multi-PHY0 is "USB3.0 OTG / SATA0". Multi-PHY1 is "USB3.0 Host / SATA1 / QSGMII/SGMII". Multi-PHY2 is "PCIe2.1 / SATA2 / QSGMII/SGMII". The xHCI host supports "1 USB2.0 port and 1 Super-Speed port". PCIe2.1 is "Root Complex", 2.5 and 5.0 Gb/s, "one lane". MIPI CSI RX is "Up to 4 data lanes, 2.5Gbps maximum data rate per lane", with either "One interface with 1 clock lane and 4 data lanes" or "Two interface, each with 1 clock lane and 2 data lanes". The BootROM supports "system code download by … USB OTG interface (Device mode)" ([Radxa mirror](https://dl.radxa.com/rock3/docs/hw/datasheet/Rockchip-RK3568-Datasheet-V1.0-20201210.pdf)). A full RK3566 datasheet was **not retrievable** from the Pine64 or Radxa mirrors this session. Where the RK3566 brief is silent, RK3568 figures apply to the RK3566 only if the block is the same. That holds for the CSI D-PHY, combphy1/2, the PCIe 2.1 controller and the BootROM, but it is formally **UNVERIFIED** for the RK3566.
- **Mainline device tree** (`torvalds/linux` master, 7.3):
  - [`rk356x-base.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk356x-base.dtsi) has the nodes common to both SoCs.
  - [`rk3566-base.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-base.dtsi) has the RK3566 overrides.
  - [`rk3568.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3568.dtsi) has the RK3568-only nodes.

The decisive lines are these.

```dts
/* rk3566-base.dtsi: OTG0 has no SuperSpeed PHY on the RK3566 */
&usb_host0_xhci {
 phys = <&usb2phy0_otg>;
 phy-names = "usb2-phy";
 extcon = <&usb2phy0>;
 maximum-speed = "high-speed";
};

/* rk3568.dtsi only: OTG0 gets combphy0 on the RK3568 */
&usb_host0_xhci {
 phys = <&usb2phy0_otg>, <&combphy0 PHY_TYPE_USB3>;
 phy-names = "usb2-phy", "usb3-phy";
};
```

`combphy0`, `sata0`, `pcie30phy`, `pcie3x1`, `pcie3x2`, `gmac0` and `can0..2` exist **only** in `rk3568.dtsi`. The RK3566 inherits `combphy1`, `combphy2`, `sata1`, `sata2`, `pcie2x1`, `usb_host0/1_xhci`, `usb_host0/1_ehci/ohci`, `usb2phy0/1`, `csi_dphy`, `vicap`, `dsi0/1`, `dsi_dphy0/1`, `sdhci`, `sdmmc0/1/2`, `gmac1`, `i2s0..3`, `pdm` and `spdif` from the base.

### 1.2 RK3566 compared with RK3568

| Block | RK3568 | **RK3566** | Mainline node (RK3566) |
|---|---|---|---|
| USB3 OTG0 (DWC3 DRD) | USB 3.0 + 2.0 via `combphy0` | **USB 2.0 only** (no `combphy0`) | `usb_host0_xhci`, `phys = <&usb2phy0_otg>`, `maximum-speed = "high-speed"` |
| USB3 HOST1 (DWC3 xHCI, host-only) | USB 3.0 via `combphy1` | **USB 3.0 via `combphy1`**: the **only SuperSpeed port** | `usb_host1_xhci`, `dr_mode = "host"`, `phys = <&usb2phy0_host>, <&combphy1 PHY_TYPE_USB3>` |
| USB 2.0 EHCI/OHCI hosts | 2 | **2** | `usb_host0_ehci/ohci` on `usb2phy1_otg`; `usb_host1_ehci/ohci` on `usb2phy1_host` |
| combphy0 | USB3 OTG0 / SATA0 | **absent** | none |
| combphy1 | USB3 HOST1 / SATA1 / (Q)SGMII | **same** | `combphy1` (`rockchip,rk3568-naneng-combphy`) |
| combphy2 | PCIe 2.1 / SATA2 / (Q)SGMII | **same** | `combphy2` |
| PCIe 2.1 x1 (DWC, RC) | yes | **yes**, Gen2 x1, `max-link-speed = <2>` | `pcie2x1` (`rockchip,rk3568-pcie`), `phys = <&combphy2 PHY_TYPE_PCIE>` |
| PCIe 3.0 x2 (+ x1 bifurcation) | yes | **absent** | none |
| SATA | 3 controllers | **2** (SATA1 on combphy1, SATA2 on combphy2) | `sata1`, `sata2` |
| GMAC | 2 | **1** (`gmac1`, RGMII, 10/100/1000) | `gmac1` |
| MIPI CSI-2 RX | 1× D-PHY, 4 lanes or 2×2, 2.5 Gb/s/lane | same (brief: "4 Lanes or 2+2 Lanes") | `csi_dphy` and `vicap` (no ISP node in master) |
| MIPI DSI TX | 2 | 2 (brief: "Dual MIPI-DSI_TX") | `dsi0`, `dsi1`, `dsi_dphy0/1` |
| eMMC / SD / SDIO | `sdhci` + 3× `sdmmc` | same | `sdhci`, `sdmmc0`, `sdmmc1`, `sdmmc2` (all in base) |
| I2S / PDM / SPDIF | 2× 8-ch TDM, 2× 2-ch, PDM 8-ch, SPDIF | same (brief: one 8-ch I2S "for HDMI") | `i2s0_8ch`, `i2s1_8ch`, `i2s2_2ch`, `i2s3_2ch`, `pdm`, `spdif` |

### 1.3 The combo PHYs in detail

The mainline driver [`phy-rockchip-naneng-combphy.c`](https://github.com/torvalds/linux/blob/master/drivers/phy/rockchip/phy-rockchip-naneng-combphy.c) has `rk3568_combphy_cfg()` with cases `PHY_TYPE_PCIE`, `PHY_TYPE_USB3`, `PHY_TYPE_SATA`, `PHY_TYPE_SGMII` and `PHY_TYPE_QSGMII`. The mode is chosen by the **consumer phandle** in the DT, so it is fixed per boot by the device tree or an overlay.

| PHY | Can carry | Mutually exclusive | Notes |
|---|---|---|---|
| `combphy1` | **USB 3 SuperSpeed for HOST1**, SATA1, SGMII/QSGMII | Yes. Only one function at a time. | Ball names `USB3_HOST1_SSTX/SSRX` / `SATA1_*` / `QSGMII_*_M0`. Quartz64 A DT: "usb3 controller is muxed with sata1". |
| `combphy2` | **PCIe 2.1 x1**, SATA2, SGMII/QSGMII | Yes | Ball names `PCIE20_TX/RX` / `SATA2_*` / `QSGMII_*_M1`, plus the `PCIE20_REFCLKP/N` pair. |

- **Reference clock.** The binding ([`phy-rockchip-naneng-combphy.yaml`](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/phy/phy-rockchip-naneng-combphy.yaml)) states: "By default the internal clock is selected. The PCIe PHY provides a 100MHz differential clock output (optional with SSC) for system applications". `rockchip,ext-refclk` selects an external clock instead, and `rockchip,enable-ssc` enables spread spectrum for U3, SATA and PCIe. **The SoC can source the 100 MHz PCIe REFCLK itself**, and the Radxa Zero 3W schematic routes `PCIE20_REFCLKp/n` to SoC balls.
- **(Q)SGMII on the RK3566 is not usable in practice.** The RK3568 datasheet says QSGMII supports "only two GMII controller", and the RK3566 has a single GMAC. Mainline `rk356x-base.dtsi` has no XPCS node (**UNVERIFIED** that SGMII through `gmac1` works).
- **The power domain is shared.** `RK3568_PD_PIPE` carries QoS for `pcie2x1`, `sata1`, `sata2`, `usb3_0` and `usb3_1` (`rk3566-base.dtsi`). Any enabled consumer keeps the whole PIPE domain powered.

### 1.4 USB 2.0 ports and PHYs

The RK3566 has two Innosilicon USB 2.0 PHYs (`rockchip,rk3568-usb2phy`), each with an `otg-port` and a `host-port`. That gives **four USB 2.0 ports**:

| PHY port | Controller (mainline) | Role | Board precedent |
|---|---|---|---|
| `usb2phy0_otg` | `usb_host0_xhci` (OTG0, DWC3) | **DRD** (host, device, OTG). The BootROM download port. | PineNote: OTG0 behind a `wusb3801` Type-C controller, `dr_mode = "otg"` |
| `usb2phy0_host` | `usb_host1_xhci` (HOST1) | Host. The USB 2 half of the SuperSpeed port. | Quartz64 A/B, Radxa Zero 3, CM3-IO |
| `usb2phy1_otg` | `usb_host0_ehci/ohci` | Host only (EHCI/OHCI, despite the port name) | Quartz64 A, CM3-IO |
| `usb2phy1_host` | `usb_host1_ehci/ohci` | Host only | Quartz64 A, RG353 |

Observation: the Anbernic RGxx3 DT (`rk3566-anbernic-rgxx3.dtsi`) overrides HOST1 to `phys = <&usb2phy1_host>, <&combphy1 PHY_TYPE_USB3>`. Whether HOST1's UTMI can actually be re-paired to `usb2phy1`, or whether this override only affects PHY power handling, is **UNVERIFIED**. This design does not depend on it.

### 1.5 PCIe 2.1 x1 controller

- Compatible `rockchip,rk3568-pcie` (RC) / `rockchip,rk3568-pcie-ep` (EP). Driver [`pcie-dw-rockchip.c`](https://github.com/torvalds/linux/blob/master/drivers/pci/controller/dwc/pcie-dw-rockchip.c), binding [`rockchip-dw-pcie.yaml`](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/pci/rockchip-dw-pcie.yaml). The node uses `num-lanes = <1>` and `max-link-speed = <2>`.
- `reset-gpios` (PERST#) and `vpcie3v3-supply` are honoured. `supports-clkreq` enables **L1 substates** only "if CLKREQ# is properly connected". Otherwise the driver pulls CLKREQ# low, and L1 substates stay off.
- **No suspend/resume callbacks** exist in the driver (no `pm_ops` in master). This is consistent with the earlier finding that RK356x PCIe system suspend is only a patch series (see [`2026-10-soc-dac-pmic.md`](2026-10-soc-dac-pmic.md)).
- **No unbind/rebind and no native hot-plug.** The driver is `builtin_platform_driver()` with `.suppress_bind_attrs = true`. The RC system IRQ handles "hot reset or link-down reset" through `pci_host_handle_link_down()`, but the RC path has **no link-up → rescan** handler (only the EP path handles `PCIE_RDLH_LINK_UP_CHGED`).
- The pinmux offers `PCIE20_CLKREQn_M0/M2`, `PCIE20_PERSTn_M0/M1/M2` and `PCIE20_WAKEn_M0/M2` (net names in the [Radxa Zero 3W schematic](https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf) and the [Radxa CM3 schematic](https://dl.radxa.com/cm3/docs/hw/RADXA_CM3_V1.31A_SCH_20221010.pdf)). Every mainline RK3566 board that enables PCIe uses a GPIO for `reset-gpios` (Quartz64 A/B, Firefly ROC-PC: `gpio1 RK_PB2`; Orange Pi 3B: `gpio0 RK_PB6`).

### 1.6 Camera, display, storage, audio, Ethernet

- **MIPI CSI-2 RX:** one D-PHY with 4 data lanes at up to 2.5 Gb/s per lane (RK3568 datasheet), or two interfaces of 2 data lanes each. Mainline master has `csi_dphy` and `vicap` with a single MIPI port. There is **no ISP node**. The earlier report expects VICAP and CSI in 7.4. Whether the 2×2 split mode works in mainline is **UNVERIFIED**. For the HAT, treat the CSI-2 input as **one 4-lane port**.
- **DSI:** two DSI hosts and two D-PHYs. The brief describes the VOP as "Same Source, Dual Display". What that means for a second, independent DSI panel on a HAT is **UNVERIFIED**.
- **Storage and SDIO:** `sdhci` (eMMC 5.1, 8-bit), `sdmmc0` (microSD on all reference boards), `sdmmc1` (4-bit, SDIO Wi-Fi on Quartz64 and CM3) and `sdmmc2` (in the base DT; the RG353 uses `cap-sdio-irq` on it). That is **three SD/SDIO hosts plus eMMC**.
- **I2S/TDM:** `i2s1_8ch` is the multi-lane TDM block (Quartz64, PineNote and ROC-PC use it for codecs). `i2s0_8ch` is tied to HDMI. `i2s2_2ch`, `i2s3_2ch`, `pdm` (8-channel) and `spdif` are also present.
- **Gigabit MAC:** one `gmac1` (RGMII). It is single-ended at 125 MHz DDR, so it is a poor fit for a pogo interface. HAT Ethernet is better served by a USB 3 or PCIe NIC on the HAT, as the hat-standard benchmark already proposes.

### 1.7 MaskROM

The BootROM falls back to "USB OTG interface (Device mode)" (RK3568 datasheet), which is OTG0 on `usb2phy0_otg`. Reference boards confirm this. The Radxa Zero 3W has a "Maskrom" button and its USB 2.0 Type-C on `USB_OTG0_DP/DM`, while its separate USB 3.0 Type-C is wired to `USB3_HOST1_*`.

**Consequence:** the main USB-C's D+/D− must reach `usb2phy0_otg` with **no SoC-controlled element in the way at reset**. At reset, Linux is not running and GPIOs are at their default state. Any switch on this path must default to the OTG0 position in hardware.

---

## 2. Two physical ports from one lane: options

### 2.1 Building blocks

| Approach | What it does | Simultaneous? | HAT bandwidth (HCS-004) | Power | Linux |
|---|---|---|---|---|---|
| **Passive 2:1 mux** | Analog switch. The lane goes to port A *or* port B. | No | Full line rate. The path is passive, with a little insertion loss. | Microwatts to about 2 mW | GPIO select. No data-path driver. |
| **USB 3 hub** | Packet repeater with 1 upstream and N downstream ports | Yes | Full line rate per port, but the ports share 5 Gb/s upstream and the hub adds latency | Hundreds of mW while active (**UNVERIFIED**); suspend states exist | Class driver, no special driver. `onboard_usb_dev` can manage its reset and regulator. |
| **PCIe packet switch** | Transparent PCI-to-PCI bridges | Yes | Full line rate per port, shared upstream | 0.3 W in L0, 35 mW in L1.1 (PI7C9X2G404EV) | Transparent. Standard PCI bridge enumeration. |

**BRD-006 caveat.** The requirement text reads "High-speed buses shall go directly from the SoC to the HAT interface. **Multiplexers are allowed.**" The brief for this report also allows switches and hubs, but the confirmed requirement does not. A hub or packet switch **in the HAT path** therefore needs an explicit amendment to BRD-006. A hub or switch **on a HAT** does not, because it is HAT hardware.

### 2.2 USB 3: HOST1's single SuperSpeed lane

The candidate ports for the lane are the **HAT** and the **main USB-C**. The main USB-C can only use it as a **host**, because HOST1 is host-only.

#### Option U1: lane to the HAT only (no extra parts)

- HOST1 SuperSpeed and HOST1's USB 2 pair go straight to the HAT pogo field.
- The main USB-C is USB 2.0 only (OTG0).
- Zero added power and the best signal integrity.
- Fails the maintainers' "two physical ports" intent for USB.

#### Option U2: 2:1 mux, HAT by default and main USB-C as an alternative (proposed)

```text
                       +-------------- HAT pogo: SSTX/SSRX (USB3 port A)
HOST1 SS (combphy1) ---[MUX-A 2:1]
                       +--[MUX-B 2:1 orientation]-- USB-C SSTX1/SSRX1 | SSTX2/SSRX2
HOST1 HS (usb2phy0_host) ------------------------- HAT pogo: D+/D- (USB3 port A, USB 2 half)
OTG0 HS (usb2phy0_otg) --------------------------- USB-C D+/D- (always)
```

- **MUX-A** is a TI **HD3SS3212** (2 differential channels, 2:1, 10 Gb/s, "<2 mW" active, "<20 µW" with OEn off, VQFN-20 4.5 × 2.5 mm, Active; [ti.com](https://www.ti.com/product/HD3SS3212)). The HAT position is the default (SEL pull-down). This also allows SATA1 on the HAT through the same lane, because the switch is passive.
- **MUX-B** is a second **HD3SS3212** that selects the Type-C orientation. The Radxa Zero 3W does the same with a WCH **CH482D** next to an Etek ET7301B CC controller on its USB 3 Type-C port (schematic sheet 17). That is a cheaper precedent, but CH482D is at 0 stock at JLCPCB.
- **Orientation control.** The FUSB302B with TCPM (already chosen for PD) reports the orientation to the Type-C class. Mainline drives a GPIO select from orientation in [`gpio-sbu-mux.c`](https://github.com/torvalds/linux/blob/master/drivers/usb/typec/mux/gpio-sbu-mux.c) (`select-gpios`, `enable-gpios`). Its DT binding is written for SBU switches, so using it for an HD3SS3212 on SuperSpeed lanes needs a **one-line binding addition upstream**, or a similar small driver (**UNVERIFIED** that maintainers accept it).
  - **Alternative:** a TI **HD3SS3220** (DRP controller with a built-in 2:1 SuperSpeed mux, automatic orientation, mainline [`hd3ss3220.c`](https://github.com/torvalds/linux/blob/master/drivers/usb/typec/hd3ss3220.c) with role switch). It removes MUX-B and the GPIO, but it **has no USB PD**. Charging would be capped at Type-C current (5 V 3 A), and it cannot share the CC pins with a FUSB302B. It is only worth it if PD is dropped.
  - For a Type-C crossbar there is also Diodes `pi3usb30532` (I2C, mainline `TYPEC_MUX_PI3USB30532`). It is overkill without DisplayPort alt mode.
- **USB 2 half in "C-port USB 3 host" mode.** The C-port D+/D− stay on **OTG0** (in host role when the port is a DFP), and the SuperSpeed lanes come from **HOST1**. A USB 3 peripheral then links SuperSpeed on HOST1. If SuperSpeed training fails, it falls back to USB 2 on OTG0. A USB 3 hub plugged in would show its USB 2 part on OTG0 and its SuperSpeed part on HOST1. Linux tolerates this split: they appear as two independent root ports without peer-port pairing. Pairing the USB 2 half of the USB-C with a different controller than its SuperSpeed half is **UNVERIFIED** for compliance and robustness and **must be bench-tested**. Fallback: a USB 2 2:1 switch (TI **TS3USB221A** or Diodes **PI3USB102**) that moves HOST1-HS to the C-port together with MUX-A. In that case the HAT's USB 2 half moves to EHCI host 1 for that time.
- **Selection policy (DAP OS).** The HAT wins when its EEPROM declares USB 3 use. Otherwise the C-port wins when a USB 3 device is attached as DFP. Switching MUX-A looks like an unplug/replug to xHCI, which is harmless. The select line is a plain GPIO (`gpio-line-names`, libgpiod) or a `gpio-mux` mux-controller.
- **HCS-004:** met. When selected, the HAT path is passive and dedicated, with no shared bandwidth and no added latency.

#### Option U3: USB 3 hub on HOST1 (both ports usable at once)

```text
HOST1 (SS + HS) --> [USB 3 hub] --DS1--> HAT USB3 port
                                --DS2--> USB-C SS (+ orientation mux; HS still OTG0 or USB 2 mux)
                                --DS3/4-> spare / internal
```

- Candidates, all needing **no driver** (USB hub class). [`onboard_usb_dev`](https://github.com/torvalds/linux/blob/master/drivers/usb/misc/onboard_usb_dev.h) adds reset and regulator handling for `usb424,5744` (USB5744), `usb2109,817/2817` (VL817) and `usb5e3,610/620`. The last two are the Genesys IDs that GL3523 is believed to enumerate with (**UNVERIFIED**).
  - **Genesys GL3523** (USB 3.2 Gen1, 4 downstream ports configurable to 2/3/4, built-in 5 V→3.3 V/1.2 V regulators, multiple TT; [genesyslogic.com.tw](https://www.genesyslogic.com.tw/en/product_view.php?show=67)). **Best availability**: GL3523-OTY30 is LCSC C390630, **12,453** in the JLCPCB library.
  - **Microchip USB5744** (4-port Gen1, SMBus configuration): LCSC C633619 **111**; Newark 834.
  - **VIA VL817** (2- or 4-port Gen1, QFN-76/56, integrated DC-DC and LDO, BC1.2, SPI firmware; [via-labs.com](https://www.via-labs.com/product_show.php?id=83)): **0** in the JLCPCB library and broker stock only. The newer **VL818** has a built-in Type-C mux and CC logic for 2 DFP ports ([via-labs.com](https://www.via-labs.com/product_show.php?id=138)). It is attractive for a C-port, but its CC logic is DFP-only, so it cannot own the T1's DRP/PD C-port.
  - USB 3.2 Gen2 hubs (VL822, USB7206) are pointless behind a 5 Gb/s root port and draw more power.
- **Cost:** about $1.3 to $4 per hub plus a crystal, flash (GL3523 and VL817 use SPI firmware) and power switching. Active power of a few hundred mW (**UNVERIFIED**; none of the vendor pages give a figure).
- **HCS-004:** a HAT alone on the hub still reaches about 5 Gb/s line rate, but the bandwidth is shared and an active device sits in the path. **BRD-006 does not cover this** (see 2.1).
- **When it would make sense:** only if the product needs USB 3 on the C-port **and** a USB 3 HAT working at the same time. Nothing in the requirements asks for that today.

**USB 3 verdict:** U2 (mux) is the best fit. It gives two physical ports, keeps the HAT's direct full-rate path, costs about 2 mW, and needs only GPIO control.

### 2.3 PCIe: the single Gen2 x1 lane (`pcie2x1` on `combphy2`)

| Option | Parts | On-board device + HAT | REFCLK, PERST#, CLKREQ# | Power | Verdict |
|---|---|---|---|---|---|
| **P1: direct to the HAT** | none | HAT only | SoC `PCIE20_REFCLK` out to the HAT; PERST# GPIO; CLKREQ# and WAKE# to the HAT | 0 | **Proposed for v1** |
| **P2: 2:1 lane mux** | **Diodes PI3PCIE3212** for TX/RX (8 Gb/s, "0.2mA typ.", QFN-20 2.5 × 4.5 mm, Active; [diodes.com](https://www.diodes.com/part/view/PI3PCIE3212)), plus a second PI3PCIE3212 or an HD3SS3212 channel for REFCLK, or a 2-output HCSL buffer with OE# | Either one, never both | REFCLK must follow the lane. PERST# to both sides, or gated per side. CLKREQ# is wired-OR. | ~1 mW | Reserve as a DNP footprint until an on-board consumer exists |
| **P3: on-board packet switch** | **Diodes PI7C9X2G404EV** (4-port Gen2, "0.3W typical in L0", "0.035W typical in L1.1 D3Hot", integrated 100 MHz clock buffer per downstream port, L1.1, Active; [diodes.com](https://www.diodes.com/part/view/PI7C9X2G404EV)) or **PI7C9X2G304EV** (3-port, "300 mW typical in L0", aQFN-136 10 × 10 mm; [diodes.com](https://www.diodes.com/part/view/PI7C9X2G304EV)) | Both at once | The switch generates the downstream REFCLKs. Each downstream port needs its own PERST#. | 35 to 300 mW | Not proposed on the board. This is the "via the HAT" building block. |

- **Legacy parts to avoid:** PI7C9X2G304SL is marked **NRND** by Diodes ([diodes.com](https://www.diodes.com/part/view/PI7C9X2G304SL)). **ASMedia ASM1182e** no longer appears in ASMedia's current PCIe switch list, which shows only ASM2806/2806A/2806I, ASM2812/2812I and ASM2824. JLCPCB shows C2833072 at 0. Its status is **UNVERIFIED**, so treat it as legacy.
- **Forward-looking HAT switch:** **ASMedia ASM2806** ("1-, 2- lane" upstream, "4 lane PCIe 3.1 … up to 4 PCIe ports", L1 substates; [asmedia.com.tw](https://www.asmedia.com.tw/product/012Yq70sX2zI9xN5/7c5YQ79xz8urEGr1.html)). A HAT built with it stays Gen3-ready for a future SoC. Its power is **UNVERIFIED**, and JLCPCB shows 0 stock.
- **"Via the board or via the HAT".** The SoC lane only needs to reach one physical connector. A HAT that needs several PCIe devices (the NAS HAT: NVMe + NIC) carries its own switch and is still reached **directly** by the SoC: the switch is a transparent bridge, and every endpoint is enumerated and driven by the SoC (BRD-004).
- **Hot-plug over pogo.** The driver cannot be rebound, has no RC link-up rescan, and has no PM ops (section 1.5). The v1 rule should therefore be: **PCIe HATs are detected at boot.** U-Boot reads the HAT EEPROM and applies an overlay that enables `combphy2` and `pcie2x1`. Hardware should still allow a later hot-attach:
  - PERST# to the HAT = SoC PERST# **AND** HAT-power-good, delayed by at least 100 ms. This keeps the endpoint in reset across a live attach.
  - The HAT rail sits behind its eFuse (BRD-026).
  - After a live attach, `echo 1 > /sys/bus/pci/rescan` may find the device if the LTSSM trained by itself (**UNVERIFIED**; bench-test it).
- **Battery.** With `pcie2x1` disabled in the DT unless a PCIe HAT is present, `PD_PIPE` can stay off when HOST1 is also idle. With it enabled, nothing in mainline suspends the link (**UNVERIFIED** idle cost, likely tens of mW). Wire CLKREQ# and set `supports-clkreq` so that L1 substates work.

### 2.4 Does sharing respect "theoretical maximum" (HCS-004)?

- **Mux:** yes. The selected port gets the full, dedicated Gen1 or Gen2 line rate. The only cost is passive insertion loss: PI3PCIE3212 lists −1.7 dB at 4 GHz, which is well above the 2.5 GHz Nyquist of 5 Gb/s. Add this loss to the stage-1 flat cable budget of ADR 0002.
- **Hub or switch:** the per-port line rate is the same, but bandwidth is shared and latency is added. A HAT that runs alone still reaches the line rate. Report it as "full rate, shared" under HCS-005 (justify every compromise).
- **Inherent SoC limits** apply whatever the topology. USB 3.2 Gen1 5 Gb/s is about 400 MB/s in practice (**UNVERIFIED**). PCIe Gen2 x1 is 5 GT/s with 8b/10b, so 500 MB/s raw and about 400 MB/s usable (earlier report). CSI-2 is 4 × 2.5 Gb/s.

---

## 3. On-board consumers and the resulting port map

### 3.1 Which on-board hardware should use which bus

| On-board device | Bus | High-speed lane needed? | Assignment |
|---|---|---|---|
| Wi-Fi/BT (NXP IW612, Murata Type 2EL) | SDIO 3.0 + UART | No | `sdmmc1` + a UART |
| eMMC 5.1 | eMMC | No | `sdhci` (8-bit) |
| microSD (BRD-038) | SD 3.0 | No | `sdmmc0` |
| RP2350 coprocessor | USB 2.0 Full-Speed (12 Mb/s) + SWD/UART/BOOTSEL | No | **EHCI/OHCI host 0** (`usb2phy1_otg`), **direct**. BRD-015 flashing uses UF2/PICOBOOT over this link. Note: Full-Speed USB cannot carry the high-rate passive I2S/DSD capture of BRD-041 (for example 192 kHz × 32 bit × 2 ≈ 12.3 Mb/s is already at the limit). That capture path needs another transport. |
| DAC (2× CS43198) | I2S/TDM | No | `i2s1_8ch` |
| Microphones | PDM | No | `pdm` |
| Display + touch | DSI + I2C | No | `dsi0` |
| Any USB audio, USB camera or USB storage on the board | — | — | **None proposed.** Every on-board function already has a native SoC bus. |
| **On-board PCIe device** | PCIe | Optional (BRD-033) | **None proposed for v1.** If one is added later (for example M.2 2230 NVMe), use the P2 mux. |
| **On-board USB 3 device** | USB 3 | — | **None.** HOST1's lane is shared only between the HAT and the main USB-C. |

**Result:** no USB 2 hub is needed on the SoC side. The four USB 2 ports cover OTG0, the HAT USB 3 port's USB 2 half, the RP2350 and a second HAT USB 2 port, each with a direct SoC path.

### 3.2 Complete port map (proposed)

| Physical port | Signals | SoC source | Notes |
|---|---|---|---|
| **Main USB-C**: data | USB 2.0 D+/D− | **OTG0** (`usb2phy0_otg`), DWC3 DRD, via the debug-hub switch in section 4.2 | MaskROM (rockusb), gadget (CDC-NCM + CDC-ACM + mass storage), OTG host at 480 Mb/s |
| **Main USB-C**: SuperSpeed | SSTX/SSRX ×2 (orientation) | **HOST1** via MUX-A (alternate) + MUX-B | Host only. Unavailable while the HAT owns USB 3. |
| **Main USB-C**: CC/PD | CC1/CC2 | FUSB302B (TCPM) + charger | PD sink for charging. Source for OTG and the powerbank role. Role switch to OTG0. |
| **Main USB-C**: SBU | SBU1/SBU2 | Optional: UART2 (debug), through TPD8S300A | Option (a) of section 4.2 |
| **HAT**: USB 3 port A | SSTX/SSRX + D+/D− | **HOST1** (MUX-A default) + `usb2phy0_host` | Or SATA1 through an overlay (same lane) |
| **HAT**: USB 2 port B | D+/D− | **EHCI/OHCI host 1** (`usb2phy1_host`) | Always available, including while USB 3 is on the C-port |
| **HAT**: PCIe | TX/RX, REFCLK, PERST# (gated), CLKREQ#, WAKE# | **`pcie2x1`** on `combphy2` | Or SATA2 through an overlay. Gen2 x1. Cold-plug in v1. |
| **HAT**: camera | CSI-2 clock + 4 data lanes | `csi_dphy` → VICAP | Full 4 lanes. Any on-board camera would force a 2+2 split, against HCS-004. |
| **Internal**: RP2350 | D+/D− | **EHCI/OHCI host 0** (`usb2phy1_otg`) | Direct (BRD-004) |
| **Internal**: Wi-Fi/BT | SDIO + UART | `sdmmc1` | — |
| **Internal**: eMMC, microSD | — | `sdhci`, `sdmmc0` | — |
| **Spare** | SDIO | `sdmmc2` | Candidate for a HAT SDIO line. Pin conflicts are **UNVERIFIED**. |

Lane count for the HAT pogo field: 2 pairs (USB 3) + 2 pairs (USB 2 ×2) + 3 pairs (PCIe TX/RX/REFCLK) + 5 pairs (CSI-2) = **12 differential pairs**, plus sidebands (PERST#, CLKREQ#, WAKE#, PRESENT#, I2C for the EEPROM). This is input for the hat-standard pinout.

---

## 4. The main USB-C in detail (BRD-034, BRD-035, BRD-039)

### 4.1 Functions and how each is met

| Function | Path | Works when the SoC is… |
|---|---|---|
| Flashing in MaskROM (rockusb) | D+/D− → OTG0 in device mode | in BootROM (BRD-035 button) |
| Gadget: file transfer, network, console after boot | OTG0 device (configfs NCM + ACM + mass storage) | running Linux |
| Host (keyboard, USB stick, DAC) | OTG0 host at 480 Mb/s; SuperSpeed through MUX-A when free | running Linux |
| Charging (PD sink) | CC → FUSB302B → TCPM → charger | any state. FUSB302B dead-battery behaviour is **UNVERIFIED**. |
| Early serial console (BRD-039) | see 4.2 | from power-on |

### 4.2 Early serial console: two options

**(a) UART on SBU.** Wire UART2 TX/RX to SBU1/SBU2 through the TPD8S300A already selected for CC/SBU over-voltage protection, with Ioff buffers or level shifting.

- Advantages: about 0 W and very few parts.
- Disadvantages: needs an OpenDAP debug dongle. USB 2.0 C-to-C and C-to-A cables carry no SBU wires, so a stock cable never shows the console.

**(b) Debug hub powered from VBUS (proposed).**

```text
                    +-- (UFP: VBUS from a PC/charger) --> [USB 2 hub, VBUS-powered]
USB-C D+/D- --[SW]--+                                        |-- DS1 --> OTG0 (device)
                    |                                        |-- DS2 --> USB-UART bridge --[Ioff buffer]--> UART2
                    +-- (DFP: the T1 is host) -----------------------------> OTG0 (host)
```

- **SW** is a USB 2 SPDT switch, Diodes **PI3USB102** or TI **TS3USB221A**. Its select is derived in hardware from "the T1 is **not** sourcing VBUS", so that at reset and in MaskROM the switch sits in the UFP→hub position. Linux only moves it, through the OTG VBUS enable, when the T1 becomes the host.
- **Hub:** a fixed-function USB 2 hub with multiple TT, for example **WCH CH334** (LCSC C4154405 CH334R, **17,256**) or **Microchip USB2422** (2-port, C622611, 743). It sits on the **PC's** side of OTG0, so **T1 Linux never needs a driver for it**.
- **Bridge:** **Silicon Labs CP2102N** (C964632, **31,407**; Mouser 38,371) or **WCH CH343P** (C2846043, 9,309). The FTDI FT230X/FT231X are at **0** at Mouser and should be avoided.
- **Power:** taken from external VBUS only, through a load switch that is **off while the T1 sources VBUS**. That gives **zero battery drain**.
- **MaskROM:** rockusb works through a hub (it is an ordinary USB device). A PC sees the BootROM and the console at the same time, even when the SoC is bricked.
- **Requirement fit:** BRD-005 forbids helper *microcontrollers* in a data path. A hub and a USB-UART bridge are fixed-function parts, but hub silicon often runs internal firmware. **Open question for the maintainers.**

### 4.3 Why not a hub directly on OTG0

A hub with OTG0 as its upstream port would make OTG0 a permanent host. That breaks device mode, gadget mode and MaskROM, which violates BRD-018 and BRD-034/035. Any hub on the C-port must sit on the **external host's** side, as in 4.2(b), and must be bypassed when the T1 is the host.

---

## 5. Recommendation (proposal)

### 5.1 Block diagram

```text
                                   RK3566
 +--------------------------------------------------------------------------------+
 | OTG0 (DWC3 DRD, USB2 only) usb2phy0_otg ---------------------------+           |
 | HOST1 (xHCI) HS usb2phy0_host ----------------------------------+  |           |
 | HOST1 SS combphy1 [USB3|SATA1] ------------------------------+  |  |           |
 | PCIe2.1 x1 combphy2 [PCIe|SATA2] + REFCLK out ------------+  |  |  |           |
 | EHCI/OHCI0 usb2phy1_otg --------------------------------+ |  |  |  |           |
 | EHCI/OHCI1 usb2phy1_host -----------------------------+ | |  |  |  |           |
 | CSI-2 D-PHY 4 lanes ------------------------------+   | | |  |  |  |           |
 | sdmmc1 SDIO --> IW612   sdhci --> eMMC   sdmmc0 --> microSD   i2s1 --> DACs    |
 +---------------------------------------------------|---|-|-|--|--|--|-----------+
                                                     |   | | |  |  |  |
          HAT pogo (via flat cable, ADR 0002) <------+   | | |  |  |  |  CSI 4L
          HAT USB2 port B <------------------------------+ | |  |  |  |
          RP2350 USB (internal) <--------------------------+ |  |  |  |
          HAT PCIe (TX/RX/REFCLK, PERST# AND PG) <-----------+  |  |  |
                                                                |  |  |
                         +---------[MUX-A HD3SS3212]------------+  |  |
                         | default: HAT USB3 port A SS             |  |
                         | alt: [MUX-B HD3SS3212 orient.]--> USB-C SS1/SS2
          HAT USB3 port A HS <-------------------------------------+  |
                                                                      |
          USB-C D+/D- <--[SW PI3USB102]--+-- UFP: [USB2 hub (VBUS)]--DS1--> OTG0
                                          |                         `-DS2--> CP2102N --> UART2
                                          `-- DFP: ---------------------------> OTG0
          USB-C CC  <--> FUSB302B (TCPM, role switch -> OTG0, orientation -> MUX-B)
          USB-C SBU <--> TPD8S300A (optional UART on SBU)
```

### 5.2 Parts

Stock was checked on 2026-10-22. "JLC/LCSC" is the JLCPCB parts library (LCSC codes). Mouser and Newark figures come from FindChips. Win Source is a **broker** and is not listed. Digi-Key was not retrievable this session, except where the earlier report already had it.

| Function | Part | Key spec (source) | JLC/LCSC | Mouser / Digi-Key | Mainline Linux |
|---|---|---|---|---|---|
| USB 3 lane: HAT/C select (MUX-A) | **TI HD3SS3212RKSR** (industrial: HD3SS3212IRKSR) | 2:1, 10 Gb/s, <2 mW active, <20 µW off ([TI](https://www.ti.com/product/HD3SS3212)) | C129320: 338; C544517 (I): 2,513 | Mouser 1,566 @ $2.12; Digi-Key 73 @ $2.21 (earlier report) | GPIO select (no driver in the data path) |
| C-port orientation (MUX-B) | **TI HD3SS3212** (2nd) | same | same | same | TCPM orientation → `gpio-sbu-mux`-style GPIO (binding addition **UNVERIFIED**) |
| Alternative to FUSB302B + MUX-B (no PD) | TI HD3SS3220RNHR | DRP + 2:1 SuperSpeed mux, auto orientation, 200 µA ([TI](https://www.ti.com/product/HD3SS3220)) | C165155: 1,807 | — | `hd3ss3220.c` |
| TCPC (already selected) | onsemi FUSB302BMPX | PD with TCPM | C132291: 1,648 (earlier report) | Mouser 5,563 @ $1.10 | `fusb302.c` |
| C-port USB 2 switch (SW) | **Diodes PI3USB102GZLEX** / TI TS3USB221ARSER | USB 2.0 SPDT | C155356: 7,422 / C128396: **81,223** | Mouser 82,703 (PI3USB102JXUCEX) / 38,032 | none needed |
| Debug hub (USB 2, VBUS-powered) | **WCH CH334R** / Microchip USB2422T-I/MJ | 4-port MTT / 2-port | C4154405: **17,256** / C622610: 705 | Newark 6,476 (USB2422) | none on the T1 (the PC side drives it) |
| Debug USB-UART bridge | **SiLabs CP2102N-A02-GQFN20R** / WCH CH343P | fixed-function bridge | C969913: 10,171 / C2846043: 9,309 | Mouser 38,371 | PC side: `cp210x` / `cdc_acm`. macOS driver status **UNVERIFIED**. |
| CC/SBU protection (already selected) | TI TPD8S300ARUKR | 20 V CC/SBU OVP + ESD | C2649824: 60 (earlier report) | Mouser 2,800 @ $1.27 | — |
| PCIe lane mux (**DNP** option) | **Diodes PI3PCIE3212ZBEX** | 2:1, 8 Gb/s, 0.2 mA ([Diodes](https://www.diodes.com/part/view/PI3PCIE3212)) | C154729: 256 | Newark 3,199 | GPIO select |
| USB 3 hub (U3 only, not proposed) | Genesys GL3523-OTY30 | 4-port Gen1 ([Genesys](https://www.genesyslogic.com.tw/en/product_view.php?show=67)) | C390630: **12,453** | — | hub class; `onboard_usb_dev` for reset/regulator |
| USB 3 hub (alternative) | Microchip USB5744 | 4-port Gen1, SMBus | C633619: 111 | Newark 834 | hub class + `onboard_usb_dev` (`usb424,5744`) |
| USB 3 hub (alternative) | VIA VL817-Q7 | 4-port Gen1 ([VIA](https://www.via-labs.com/product_show.php?id=83)) | 0 | brokers only | hub class + `onboard_usb_dev` (`usb2109,817`) |
| PCIe switch (**HAT side**) | Diodes PI7C9X2G404EV | 4-port Gen2, 0.3 W L0, 35 mW L1.1 ([Diodes](https://www.diodes.com/part/view/PI7C9X2G404EV)) | C5245932: 0 | Mouser 301 @ $16.22 | transparent |
| PCIe switch (**HAT side**, stocked fallback) | Diodes PI7C9X2G404SLBFDEX | 4-port Gen2 (older SL family; lifecycle **UNVERIFIED**) | C500767: 2,741 | Mouser 919 @ $14.94 | transparent |
| PCIe switch (**HAT side**, Gen3-ready) | ASMedia ASM2806 | Gen3, up to 4 downstream ports, L1 substates ([ASMedia](https://www.asmedia.com.tw/product/012Yq70sX2zI9xN5/7c5YQ79xz8urEGr1.html)) | C20616048: 0 | not found | transparent |
| USB 3 receptacle (if the C-port gets SuperSpeed) | Amphenol 12401610E4#2A | 24-pin USB 3.1 Type-C | C5119948: 6,644 (earlier report) | Digi-Key 80,288 (earlier report) | — |

Sourcing flags:

- MUX-A and MUX-B: LCSC stock of the commercial HD3SS3212 is thin (338). The industrial **HD3SS3212IRKSR** (2,513) is the better JLC pick.
- PCIe switches: none is well stocked at LCSC. This supports keeping switches on HATs, where volume and timing differ.

### 5.3 Power budget and gating (BRD-008, BRD-009)

| Block | Active | Idle / gated | Gating method |
|---|---|---|---|
| MUX-A, MUX-B (HD3SS3212) | < 2 mW each | < 20 µW (OEn) | GPIO OEn. Disable MUX-B whenever the C-port is not a USB 3 host. |
| SW (PI3USB102 / TS3USB221A) | µA range (**UNVERIFIED**) | — | always on (3.3 V always-on rail) |
| Debug hub + bridge | tens of mW (**UNVERIFIED**) | **0 from the battery** | powered only from external VBUS, off while the T1 sources VBUS |
| `PD_PIPE` (combphy1/2, HOST1, PCIe) | **UNVERIFIED** | off when no consumer is bound | Leave `pcie2x1` and `combphy2` disabled unless a PCIe HAT overlay is applied. HOST1 uses DWC3 runtime PM. |
| PI3PCIE3212 (if fitted) | ~0.7 mW | — | GPIO |
| (Not proposed) USB 3 hub | ~0.1 to 0.5 W (**UNVERIFIED**) | regulator off | load switch + `onboard_usb_dev` regulator/reset (it powers off in system suspend; at runtime it relies on U3/selective suspend) |
| (HAT side) PCIe switch | 0.3 W L0 | 35 mW L1.1 | needs CLKREQ# and `supports-clkreq` |

### 5.4 Linux support summary

- **Muxes:** no driver in the data path. Select lines are GPIOs, controlled by DAP OS (libgpiod) or modelled as a `gpio-mux` mux-controller. C-port orientation comes from TCPM through a Type-C `orientation-switch`.
- **Hubs:** the USB hub class is driverless. `onboard_usb_dev` is optional, for power and reset.
- **PCIe switches:** standard PCI-to-PCI bridges, nothing special.
- **Combo PHY mode:** set by the DT or an overlay (`PHY_TYPE_USB3`, `PHY_TYPE_SATA` or `PHY_TYPE_PCIE`). The HAT EEPROM drives which overlay U-Boot applies.
- **Debian:** `USB_DWC3`, `TYPEC_FUSB302` and `TYPEC_TCPM` are already modules (earlier report). Confirm that `TYPEC_MUX_GPIO_SBU`, `PCIE_ROCKCHIP_DW_HOST` (built-in) and `PHY_ROCKCHIP_NANENG_COMBPHY` are enabled in Debian arm64 (**UNVERIFIED**). If not, add them to the existing Debian wishlist bug.

---

## 6. Risks

1. **Mixed USB 2 and SuperSpeed controllers on the C-port** (OTG0 HS + HOST1 SS) in USB 3 host mode: **UNVERIFIED**. Bench-test it early with a USB 3 SSD, a USB 3 hub and a device that falls back to USB 2. The fallback is a USB 2 switch that moves HOST1-HS together with MUX-A.
2. **PCIe hot-plug:** the mainline driver cannot rebind and has no RC link-up rescan. v1 PCIe HATs are cold-plug. Hot-attach needs the PERST#-gating hardware plus a manual rescan (**UNVERIFIED**).
3. **PCIe suspend:** no PM ops in `pcie-dw-rockchip.c`. System suspend with a PCIe HAT attached is unsupported until upstream lands it.
4. **Signal integrity:** each mux adds insertion loss on top of the ADR 0002 flat cable and the pogo contact. On the C-port, SuperSpeed crosses two muxes. Whether a redriver is allowed under BRD-006 is still the open question from the hat-standard benchmark. Note that the component-selection report assumed the 5 Gb/s lanes stay on the main PCB to the pogo field, which ADR 0002 has superseded.
5. **Debug-hub back-powering:** the bridge's UART lines must not power the SoC IO when only VBUS is present (use Ioff buffers). The hub load switch must stay off while the T1 sources VBUS.
6. **Thin stock:** HD3SS3212 commercial grade (LCSC 338), PCIe switches (LCSC 0 for EV parts), VL817 (0). GL3523 and the HD3SS3212 industrial grade are the safer picks.
7. **`gpio-sbu-mux` binding scope:** using it for a SuperSpeed mux may need an upstream binding change (**UNVERIFIED**). The alternative is a separate GPIO-orientation driver.
8. **RP2350 Full-Speed USB:** 12 Mb/s caps any streaming use (BRD-041). This is not a topology problem, but it constrains that requirement.

---

## 7. Open questions for the maintainers

1. **USB 3 on the main USB-C:** is the C-port USB 3 host mode wanted (MUX-A + MUX-B + 24-pin receptacle), or should HOST1 go to the HAT only (Option U1)?
2. **BRD-006 wording:** should "hubs and packet switches" be allowed in the HAT path, or only multiplexers? This report assumes multiplexers only on the board.
3. **On-board PCIe consumer:** is there any (for example M.2 2230 NVMe)? If not, fit no PCIe mux in v1 and keep only a DNP footprint.
4. **Serial console:** SBU UART with a dongle (a), or the VBUS-powered debug hub (b)? Under BRD-005, do fixed-function hub or bridge chips count as "helper microcontrollers"?
5. **PD versus HD3SS3220:** keep FUSB302B PD (faster charging, powerbank role) or accept 5 V 3 A and use the single-chip HD3SS3220?
6. **Second camera:** is any on-board camera planned? It would force CSI 2+2 and halve the HAT's camera lanes (HCS-004).
7. **`sdmmc2` and SATA on the HAT:** should the HAT standard expose SDIO (`sdmmc2`) and declare lane A/B as "USB3|SATA1" and "PCIe|SATA2" through overlays?

---

## 8. Sources

### SoC documentation

- Rockchip, *RK3566 Brief Datasheet*: <https://www.rock-chips.com/uploads/pdf/2022.8.26/192/RK3566%20Brief%20Datasheet.pdf>
- Rockchip, *RK3568 Datasheet V1.0* (Radxa mirror): <https://dl.radxa.com/rock3/docs/hw/datasheet/Rockchip-RK3568-Datasheet-V1.0-20201210.pdf>
- RK3568 TRM Part 1/2 (Radxa mirror, listed but not read this session): <https://dl.radxa.com/rock3/docs/hw/datasheet/>

### Mainline Linux (torvalds/linux master, 7.3, read 2026-10-22)

- `rk356x-base.dtsi`: <https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk356x-base.dtsi>
- `rk3566-base.dtsi`: <https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-base.dtsi>
- `rk3568.dtsi`: <https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3568.dtsi>
- Board DTs: [`rk3566-quartz64-a.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-quartz64-a.dts), [`rk3566-quartz64-b.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-quartz64-b.dts), [`rk3566-radxa-zero-3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-radxa-zero-3.dtsi), [`rk3566-radxa-cm3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-radxa-cm3.dtsi), [`rk3566-radxa-cm3-io.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-radxa-cm3-io.dts), [`rk3566-anbernic-rgxx3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-anbernic-rgxx3.dtsi), [`rk3566-pinenote.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-pinenote.dtsi), [`rk3566-roc-pc.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-roc-pc.dts) (Firefly), [`rk3566-orangepi-3b.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-orangepi-3b.dtsi)
- Combo PHY driver and binding: <https://github.com/torvalds/linux/blob/master/drivers/phy/rockchip/phy-rockchip-naneng-combphy.c>, <https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/phy/phy-rockchip-naneng-combphy.yaml>
- PCIe driver and bindings: <https://github.com/torvalds/linux/blob/master/drivers/pci/controller/dwc/pcie-dw-rockchip.c>, <https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/pci/rockchip-dw-pcie.yaml>, <https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml>
- On-board USB hub support: <https://github.com/torvalds/linux/blob/master/drivers/usb/misc/onboard_usb_dev.h>, <https://github.com/torvalds/linux/blob/master/drivers/usb/misc/onboard_usb_dev.c>
- Type-C: <https://github.com/torvalds/linux/blob/master/drivers/usb/typec/mux/Makefile>, <https://github.com/torvalds/linux/blob/master/drivers/usb/typec/mux/gpio-sbu-mux.c>, <https://github.com/torvalds/linux/blob/master/drivers/usb/typec/hd3ss3220.c>

### Board schematics

- Radxa ZERO 3W v1.12 schematic (USB 3 Type-C with CH482D + ET7301B, OTG0 USB 2 Type-C, Maskrom button, `PCIE20_REFCLK` balls): <https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf>
- Radxa CM3 v1.31A schematic (`PCIE20_*` sidebands, SATA nets): <https://dl.radxa.com/cm3/docs/hw/RADXA_CM3_V1.31A_SCH_20221010.pdf>
- Pine64 Quartz64 and PineNote schematics: **not retrieved** (wiki.pine64.org returned HTTP 503). Their mainline DTs were used instead.

### Vendor product pages

- TI HD3SS3212: <https://www.ti.com/product/HD3SS3212>
- TI HD3SS3220: <https://www.ti.com/product/HD3SS3220>
- Diodes PI3PCIE3212: <https://www.diodes.com/part/view/PI3PCIE3212>
- Diodes PI7C9X2G304SL (NRND): <https://www.diodes.com/part/view/PI7C9X2G304SL>
- Diodes PI7C9X2G304EV: <https://www.diodes.com/part/view/PI7C9X2G304EV>
- Diodes PI7C9X2G404EV: <https://www.diodes.com/part/view/PI7C9X2G404EV>
- VIA Labs VL817: <https://www.via-labs.com/product_show.php?id=83>
- VIA Labs VL818: <https://www.via-labs.com/product_show.php?id=138>
- VIA Labs product list: <https://www.via-labs.com/product.php>
- Genesys GL3523: <https://www.genesyslogic.com.tw/en/product_view.php?show=67>
- ASMedia ASM2806: <https://www.asmedia.com.tw/product/012Yq70sX2zI9xN5/7c5YQ79xz8urEGr1.html>
- Microchip USB5744: <https://www.microchip.com/en-us/product/usb5744> (HTTP 403 this session; specs not read)

### Stock

- FindChips (Mouser, Newark, TME rows), for example: <https://www.findchips.com/search/HD3SS3212RKSR>
- JLCPCB parts library (LCSC codes): <https://jlcpcb.com/parts>. LCSC product pages follow the form `https://www.lcsc.com/product-detail/<code>.html`.
