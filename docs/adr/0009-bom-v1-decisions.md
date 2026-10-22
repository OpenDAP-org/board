# ADR 0009: BOM v1 decisions

- **Status:** Accepted
- **Date:** 2026-10-22
- **Decided by:** Claude, under the maintainers' delegation, following the product rules

## Context

The complete BOM v1 and power tree ([`../specs/bom-v1-draft.md`](../specs/bom-v1-draft.md), [`../specs/power-tree-v0.md`](../specs/power-tree-v0.md)) found errors in v0 and left choices open. The audiophile experience is never sacrificed (T1-040).

## Decision

- **Audio master clocks:** 22.5792 MHz and 24.576 MHz at 1.8 V, as the CS43198 requires (BRD-023 corrected). The parts must be low-jitter and in stock at 1.8 V; a 3.3 V oscillator behind a level translator is not acceptable, because it would degrade jitter.
- **Headphone amplifier rails:** ±5 V from a TPS65131 followed by low-noise TPS7A4901 / TPS7A3001 regulators, the minimum for 4 Vrms balanced output with 1 V of headroom.
- **MaskROM entry:** holding **Power + Volume −** at power-on forces MaskROM (BRD-035); the power button alone never does, so normal boots are not affected.
- **PMIC configuration:** follow the RK809-5 configuration of the reference designs (Quartz64, Radxa), which use the same PMIC.
- **HAT flat-cable connector:** chosen during the BOM cross-validation (high-speed rated, in stock).
