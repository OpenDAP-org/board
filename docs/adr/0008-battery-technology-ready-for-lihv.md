# ADR 0008: Battery technology, ready for LiHV

- **Status:** Accepted
- **Date:** 2026-10-22
- **Decided by:** Claude, under the maintainers' delegation, following the product rules

## Context

The maintainers wants the best, most modern battery technology for the project. Today the most modern chemistry sold off the shelf is lithium-ion polymer with high-voltage cathodes (LiHV, 4.40–4.45 V charge), with about 10 % more energy in the same volume; silicon-anode cells are not sold off the shelf. No stocked LiHV pack of 2,000 mAh or more fits the bay, and parts must be off the shelf (T1-038). Research: [battery selection](../research/2026-10-battery-selection.md).

## Decision

- The power design is **LiHV-ready**: the charger (BQ25895, charge voltage programmable up to 4.608 V) and the fuel gauge (MAX17055, configurable cell model) are configured per pack, the board's battery protection and thermal limits cover 4.45 V cells, and the charge voltage comes from the pack's identity in software, never hard-coded.
- The pack in use is the **most modern off-the-shelf, stocked and certified one that fits**. Today that is a standard 4.2 V lithium-ion polymer pack (Adafruit 328, [ADR 0007](0007-off-the-shelf-battery.md)); a stocked, certified LiHV pack replaces it as soon as one fits.
