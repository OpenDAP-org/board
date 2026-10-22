# ADR 0010: Audio master clock source

- **Status:** Accepted
- **Date:** 2026-10-22
- **Decided by:** Claude, under the maintainers' delegation, following the product rules

## Context

The CS43198 takes an external MCLK only at 22.5792 or 24.576 MHz, on its 1.8 V VL domain (BRD-023, ADR 0009). The BOM v1 cross-validation ([report §4.1](../research/2026-10-bom-v1-cross-validation.md)) found no active, stocked, audio-grade 1.8 V oscillator at 22.5792 MHz:

- NDK NSC5083A (NZ2520SDA, 1.8 V, −158 dBc/Hz at 1 kHz) is a catalog part with no stock at authorized distributors.
- TI CDC6C (BAW) is about 60 dB worse close to the carrier.
- Epson SG-210STF at 22.5792 MHz is obsolete; Kyocera KC2520Z has no stock; MEMS parts are rejected for close-in noise.
- Stocked general-purpose quartz XOs (SCTF SX2M) publish no phase-noise data, and the project has no phase-noise instrument to qualify them.
- A 3.3 V oscillator behind a translator is excluded by ADR 0009.

The audiophile experience is never sacrificed (T1-040); availability (T1-029) is balanced against everything else.

## Decision

- **Production part:** NDK NSC5083A-22.5792M and NSC5083A-24.576M on the NZ2520SDA land, at 1.8 V, ordered as catalog spec numbers through NDK's franchised channel.
- This is a scoped exception to T1-029 for these two lines only. It is a catalog part, not a custom one, so T1-038 holds.
- **Bring-up boards** may populate the stocked SCTF SX2M22.5792M20F30TNN and Epson SG-210STF 24.5760ML0 on the same land, for function only. Audio measurements are never taken with them.
- If NDK cannot quote the volume and lead time, this decision is reopened before the layout freezes. The 3.3 V + translator route stays excluded.

## Consequences

- BOM v1 lines 20–21 move from *Blocker* to *Decided*, with lead time and MOQ as a tracked risk until NDK quotes them.
- The board keeps the 2520 land, the tri-state sharing of one MCLK net and the dedicated MCLK_1V8 LDO.
- The pin plan's MCLK enables drive the oscillators' ST pins at 1.8 V.
