# MaskROM combo: ngspice simulation

The question: does the hardware MaskROM entry (Main + Volume − held at power-on, BRD-035,
[board ADR 0009](../../docs/adr/0009-bom-v1-decisions.md), BOM v1.5 lines 35, 77, 78, 97, 98)
hold eMMC_D0 low through the RK3566 BootROM's eMMC attempt across tolerances, and leave
normal boots, resume from suspend and HS200 signal integrity alone?

Results, the timing budget and their limits are in
[`docs/research/2026-10-boost-and-maskrom-simulation.md`](../../docs/research/2026-10-boost-and-maskrom-simulation.md).

## Files

| File | What it is |
|---|---|
| `maskrom-model.inc` | Behavioural model: PWRON node (RK809 17 kΩ + 100 nF), Vol− node, RK809 power-on (PWRON_ON_TIME, 2 ms slots, RESETB), window supervisor (TPS3839 on vcc_1v8, or TPS3808 on vcca1v8_pmu), Schmitt gates SN74LVC1G57/58 at their worst thresholds, BAT54, DMG1012T switch, eMMC_D0 with its pull-up. |
| `maskrom-cold.cir` | Cold power-on with Main + Vol− (MaskROM request) and with Main only (normal boot), for the BOM design (A) and the proposed one (B), over supervisor-delay and PWRON_ON_TIME corners. |
| `maskrom-resume.cir` | Resume from suspend (vcc_1v8 off in suspend) woken with Main while Vol− is held. |
| `maskrom-levels.cir` | Gate-1 input levels: PWRON pressed through the BAT54 versus temperature and pull-up value; PWRON released versus the RK809 VCC_RTC level. |
| `maskrom-d0-si.cir` | eMMC_D0 at HS200 (200 MHz SDR) with the pull-down tap off: series resistor 100 Ω to 1 kΩ, FET output capacitance 10 and 25 pF. |

Every timing value in `maskrom-model.inc` is a parameter. Values not found in a primary
source (RK809-5 OTP slots, RESETB delay, BootROM timing, VCC_RTC level, Vol− pull-up and
filter, FET output capacitance at low VDS) are marked **UNVERIFIED** in the research note,
with the corner used for each.

## Run

Tools: ngspice 47 or later. No vendor model and no Python are needed: each file prints its
own table.

```sh
ngspice -b maskrom-cold.cir     | grep -E '^(design|0 |1 )'
ngspice -b maskrom-resume.cir   | grep -E '^SUP'
ngspice -b maskrom-levels.cir   | grep -E '^(pressed|released):'
ngspice -b maskrom-d0-si.cir    | grep -E '^(COSS|10p|25p)'
```

Each run takes under a minute.
