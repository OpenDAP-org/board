# ADR 0004: RP2350 coprocessor

- **Status:** Accepted
- **Date:** 2026-10-21

## Context

The board includes a Raspberry Pi RP-series microcontroller as orchestration coprocessor (BRD-014), which DAP OS must be able to flash and update (BRD-015), and the SoC must boot without its firmware (BRD-019). Research: [`dap-os` OS lifecycle](https://github.com/opendap-project/dap-os/blob/main/docs/research/2026-10-os-lifecycle.md).

## Decision

Use the **RP2350**: its boot ROM falls back to the previous firmware when a new one fails, and DAP OS can always recover it from Linux over SWD or USB BOOTSEL.
