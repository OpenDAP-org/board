# ADR 0010: Audio master clock source

- **Status:** Accepted (revised 2026-10-22 after the maintainers' review: no dependence on parts whose supply is not known)
- **Date:** 2026-10-22
- **Decided by:** Claude, under the maintainers' delegation, following the product rules

## Context

The CS43198 takes an external MCLK only at 22.5792 or 24.576 MHz, on its 1.8 V VL domain (BRD-023). The BOM v1 cross-validation ([report §4.1](../research/2026-10-bom-v1-cross-validation.md)) found:

- NDK NSC5083A (1.8 V) has no stock at any authorized distributor. The project does not depend on parts it may not get.
- No other stocked, audio-grade 1.8 V oscillator exists at 22.5792 MHz: the TI CDC6C is about 60 dB worse close to the carrier; the Epson SG-210STF at 22.5792 MHz is obsolete; Kyocera has no stock; MEMS parts are rejected; stocked general-purpose XOs publish no phase-noise data.
- The 3.3 V NDK NSC5083D is stocked (Digi-Key 2,239 / 3,083 on 2026-10-22) and has the best phase noise of every candidate (−164 dBc/Hz at 1 kHz, against −158 dBc/Hz for the 1.8 V NSC5083A).

ADR 0009 excluded "a 3.3 V oscillator behind a level translator" because an active translator adds jitter. A passive attenuator adds no active stage.

## Decision

- **Oscillators:** NDK NSC5083D-22.5792M and NSC5083D-24.576M (NZ2520SDA, 3.3 V), one per rate family, the DAC as clock master (BRD-023).
- **Supply:** a dedicated low-noise LDO, MCLK_3V3 (TI TPS7A2033), only for the two oscillators.
- **Level adaptation:** a passive, series-terminated resistive attenuator from each oscillator output into the shared MCLK net at the CS43198 XTI/MCLK input (VL 1.8 V). No active translator in the clock path. The values are set in the schematic so the edge at XTI stays inside the VL input limits and does not slow down materially; this is checked by SPICE with the CS43198 input capacitance before layout freeze.
- **Tri-state:** each oscillator's ST pin is driven at 3.3 V logic (from the TCA6416A expander, or a single-bit translator if the expander port is not at 3.3 V; fixed in pinout v1). One oscillator runs at a time.
- **Second source:** a stocked 3.3 V audio-grade XO in a compatible package, to be qualified (Crystek CCHD-957 class; stock **UNVERIFIED**).
- This revision supersedes the "no 3.3 V oscillator" line of ADR 0009.

## Consequences

- BOM v1 lines 20–21 are *Decided* with authorized stock. No part on the clock path depends on a quote.
- The power tree replaces MCLK_1V8 with MCLK_3V3. Its TPS7A2033 runs from VSYS, whose minimum is 3.5 V (VSYSMIN), which leaves enough headroom at 15 mA.
- The SoC GPIOs that drove the oscillator enables at 1.8 V (pin plan 4_B4, 4_C0) are freed or reassigned in pinout v1.
- Verification: SPICE for the attenuator edge, then the J-test and THD+N captures of the verification toolkit on the first boards.
