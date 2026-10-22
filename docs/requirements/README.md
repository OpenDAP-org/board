# Board requirements

Electrical and system requirements for the OpenDAP T1 main board.

| ID | Requirement | Priority | Status |
|---|---|---|---|
| BRD-001 | Every component shall work with mainline Linux drivers. OpenDAP OS builds no custom kernel; a board device tree and overlays are acceptable. | must | Confirmed |
| BRD-002 | The SoC shall meet the project requirements without raising the product price significantly. | must | Confirmed |
| BRD-003 | The board shall be a general-purpose Linux platform, not a DAP-only design, able to serve the HAT ecosystem and on-board AI uses. | must | Confirmed |
| BRD-004 | The SoC shall reach every chip on the board and on attached HATs directly, for debugging, flashing and operation. | must | Confirmed |
| BRD-005 | Helper microcontrollers may assist and orchestrate, but shall never sit in a data path or limit capabilities. | must | Confirmed |
| BRD-006 | High-speed buses shall go directly from the SoC to the HAT interface. Multiplexers are allowed. | must | Confirmed |
| BRD-007 | The board shall include protection and safety mechanisms. | must | Confirmed |
| BRD-008 | The board shall power down specific hardware blocks when they are not in use. | must | Confirmed |
| BRD-009 | The board shall support a low-power mode. | must | Confirmed |
| BRD-010 | The board shall monitor CPU and temperature. | must | Confirmed |
| BRD-011 | The board shall provide a 3.5 mm and a 4.4 mm headphone output. | must | Confirmed |
| BRD-012 | The integrated mono speaker shall be driven independently of the DAC. | must | Confirmed |
| BRD-013 | The board repository shall own the specification of the flat cable from the board to the device-side piece of the HAT case. | must | Confirmed |
| BRD-014 | The board shall include a Raspberry Pi RP-series microcontroller as an orchestration coprocessor. The exact part is not fixed yet. | must | Confirmed |
| BRD-015 | OpenDAP OS shall be able to flash and update the RP coprocessor. | must | Confirmed |
| BRD-016 | The board shall provide a MaskROM button for recovery flashing. | must | Confirmed |
| BRD-017 | The board shall provide a recovery key. | must | Confirmed |
| BRD-018 | The board shall provide USB-C OTG, so it can be flashed over USB. | must | Confirmed |
| BRD-019 | The SoC shall boot without the RP coprocessor firmware. | must | Confirmed |
| BRD-020 | The PMIC shall be the Rockchip RK809, the companion PMIC of the RK3566. | must | Draft |
| BRD-021 | Memory: 4 GB LPDDR4X and 32 GB eMMC. | should | Withdrawn |
| BRD-022 | The audio stage shall use two Cirrus Logic CS43198 DACs in dual mono, followed by six OPA1622 headphone amplifiers (both halves of one package in parallel on each balanced leg), sized to meet the mid-range segment's output into low-impedance headphones (ADR 0012). | must | Draft |
| BRD-023 | The audio stage shall have two master clocks, 22.5792 MHz and 24.576 MHz (44.1 kHz and 48 kHz families) at the CS43198's 1.8 V clock input, with the DAC as clock master, so every sample rate plays bit-perfect without resampling. | must | Confirmed |
| BRD-024 | The 3.5 mm output shall be single-ended and the 4.4 mm output balanced (Pentaconn). | must | Draft |
| BRD-025 | Every radio (Wi-Fi, Bluetooth and any other) shall prioritize certified or pre-certified modules. | must | Confirmed |
| BRD-026 | Each HAT power rail shall be protected by an eFuse. | must | Draft |
| BRD-027 | The microphone privacy LED shall be wired to the microphone power, so it cannot be lit independently of the microphone. | must | Draft |
| BRD-028 | The first intention is a single PCB carrying the SoC, the DAC chipset and the rest of the electronics (no system-on-module). Not final. | should | Confirmed |
| BRD-029 | The T1 shall have Wi-Fi and Bluetooth. | must | Confirmed |
| BRD-030 | The T1 should support item tracking over Bluetooth, in the style of an AirTag. | should | Confirmed |
| BRD-031 | An ambient-noise microphone shall sit at the top right of the device, in addition to the main microphone on the faceplate. | must | Confirmed |
| BRD-032 | The board shall include an IMU. | must | Confirmed |
| BRD-033 | PCIe on the board PCB is nice to have, not required. | should | Confirmed |
| BRD-034 | The main USB-C port shall support as much as possible: OTG, flashing, debugging, working with the device, file transfer, charging, and acting as a host when needed. | must | Confirmed |
| BRD-035 | The main / power button shall also be the boot-mode (MaskROM) button. | must | Confirmed |
| BRD-036 | Every button of the T1 should be accessible to developers; at least the Action button shall be. | must | Confirmed |
| BRD-037 | Memory: most likely 4 GB of RAM and 32 GB of storage. | should | Draft |
| BRD-038 | The T1 shall have an SD/TF card slot; the more storage, the better. | must | Confirmed |
| BRD-039 | The early serial console shall follow the same path as the main USB-C port. | must | Confirmed |
| BRD-040 | The board shall expose test pads on the I2S/DSD lines to the DAC, so the digital audio stream can be captured passively. | must | Confirmed |
| BRD-041 | The RP2350 shall be able to capture those lines passively (for example with PIO) and stream them to a host, without being in the data path. | should | Draft |
| BRD-042 | No unusual switches or tricks in the high-speed paths. | must | Confirmed |
| BRD-043 | Recovery flashing shall also work by booting from the SD/TF card, which then flashes the internal storage, besides MaskROM over the main USB-C. | must | Confirmed |
| BRD-044 | The single USB 3 lane shall go to the HAT only; the main USB-C carries USB 2.0 (OTG0: MaskROM, gadget, host) and USB-PD. | must | Confirmed |
| BRD-045 | PCIe shall go straight to the HAT. | must | Confirmed |
| BRD-046 | Ideally everything goes through the main USB-C, including the serial console from as early in boot as possible: U-Boot and Linux expose a USB serial (CDC-ACM) console on it. | should | Confirmed |
| BRD-047 | UART test pads shall exist for bring-up of the earliest boot stages (BootROM, TPL/SPL), which cannot use USB. | must | Confirmed |
| BRD-048 | The board shall route enough dedicated signals to the faceplate for almost any display and touch connection standard, so that a change of display or touch part needs no board redesign. | must | Confirmed |
| BRD-049 | Power safety comes first: every rail, converter, connector and cable shall run with margin below its rating and shall be protected. A safer power design is preferred over a smaller or cheaper one. | must | Confirmed |
| BRD-050 | The battery path shall carry enough current for the full HAT and USB-C output budget on battery, with a more robust battery connection if the off-the-shelf lead or connector cannot. | must | Confirmed |
| BRD-051 | The microSD/TF slot shall run in the fastest mode the SoC supports, for performance: UHS-I SDR104 on the RK3566 (SD 3.0), with 1.8 V signalling. | must | Confirmed |
| BRD-052 | Both headphone jacks shall detect plug insertion and removal, so playback can pause when headphones are unplugged and never move to the speaker unasked. | must | Confirmed |
| BRD-053 | The board shall support assembly variants: prototypes populate every option to validate the full functionality, and production variants may leave optional parts unpopulated (DNP) or fit lower-cost equivalents on the same footprint, without a board respin. Every optional part is marked as such in the BOM, with its variant. | must | Confirmed |

## Open questions

- Exact DAC part.

## Context

- BRD-053 (maintainers, 2026-10-22): prototypes may exceed the production cost limits to validate everything; production simply omits parts. Value engineering therefore targets the production variant, and optional parts are designed in as population options from the start.
- BRD-051: UHS-II (SD 4.0) needs a second row of contacts and SoC support the RK3566 does not have (RK3568 datasheet Rev 1.0, p. 8: SD 3.0, 4-bit). The board already provides the switchable 1.8/3.3 V VCCIO3 and 1.8 V-rated ESD for SDR104 (BOM lines 11, 73).
- The main board is likely to benefit from HDI, and the flat cables (FPC) possibly from an equivalent level. Not decided.
- BRD-020 to BRD-027: Adopted from the earlier experiments on 2026-10-21 as **Draft**: consistent with the decisions already taken and with the product philosophy, pending the maintainers' confirmation. Part availability still has to be checked against the sourcing rule (T1-010).
- Experiment parts worth evaluating: charger BQ25895 (or BQ25792 from the desk research, which can also source power to a powerbank HAT), fuel gauge BQ27Z561, power-path TPS2121, USB-PD FUSB302B, HAT eFuse TPS25947, radio module Murata Type 2EL (NXP IW612; its mainline driver status must be verified), coprocessor variant RP2354B (RP2350 with in-package flash).
- The experiments split the electronics into a compute module (8-layer HDI), an audio module and a base board. Not adopted: the first intention is a single PCB (see the last requirement).
- Withdrawn on 2026-10-21 after the [experiment review](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-experiment-review.md): BRD-021.
- BRD-016 (MaskROM button) is met by the main / power button (BRD-035).
- Pending: deep suspend on the RK3566 (see `opendap-os`).
- Topology research: [`../research/2026-10-high-speed-io-topology.md`](../research/2026-10-high-speed-io-topology.md). Its USB 3 switch to the main USB-C and its debug USB hub were set aside by the "no unusual switches or tricks" rule. Early serial console: USB serial (CDC-ACM) on the main USB-C from U-Boot onward, plus UART test pads for the earliest stages.
- Candidate signal set for the faceplate connector, to validate against the RK3566 pin multiplexing (some display interfaces share pins with audio and other peripherals): MIPI DSI 4-lane, parallel RGB, SPI/DBI, I2C and interrupt/reset lines for touch, PWM backlight control and enable, and the usual panel supply rails.
- BRD-023 corrected on 2026-10-22: the CS43198 datasheet only accepts a 22.5792 or 24.576 MHz external master clock at 1.8 V; the earlier 45.1584 / 49.152 MHz figures came from the experiments and were wrong.
