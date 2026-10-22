# VSYS bucks: ngspice simulation

The question: do the two bucks that the 2S battery adds ([ADR 0014](../../docs/adr/0014-two-cell-battery.md),
BOM v1.5) hold their load steps, ripple, loop stability and BRD-049 current margins across
VSYS 6.0–8.8 V?

- **TPS62903** (line 91): VSYS → 5.1 V for HAT_5V and the USB-C source, 1.6 A design output.
- **TPS62136** (line 113): VSYS → 3.8 V VSYS_LV, the rail that feeds the former 1S tree, 2.0 A peak.

Results and their limits are in
[`docs/research/2026-10-boost-and-maskrom-simulation.md`](../../docs/research/2026-10-boost-and-maskrom-simulation.md).

## Files

| File | What it is |
|---|---|
| `dcs-buck-generic.lib` | Open behavioural model of a DCS-Control-class buck (constant on-time, ripple emulation, integrator, current limits, power save). Not a TI model. Calibrated against TI's TPS62136 model (`check` group). |
| `tps62903-5v1-step.cir` | TPS62903 load step 0.1 → 1.6 → 0.1 A, generic model. TI's TPS62903 models are encrypted PSpice (SLVMDN8) or SIMPLIS (SLVMDP3) and do not run in ngspice. |
| `tps62903-5v1-loop.cir` | TPS62903 loop gain at one frequency (voltage injection), generic model. |
| `tps62136-3v8-step.cir` | TPS62136 load step 0.1 → 2.0 → 0.1 A with TI's transient model. |
| `tps62136-3v8-loop.cir` | TPS62136 loop gain at one frequency with TI's transient model. |
| `generic-check-step.cir`, `generic-check-loop.cir` | The generic model with TPS62136 values, for comparison with TI's model. |
| `run.py` | Runs the corner sets and prints the tables of the research note. |
| `.spiceinit` | ngspice PSpice compatibility mode, needed by TI's model. |

## Vendor model (not in this repository)

`tps62136-3v8-*.cir` need TI's **TPS62136 PSpice Unencrypted Transient Model**,
[SLVMC09](https://www.ti.com/lit/zip/SLVMC09) (model "Final 1.1", 20MAR2017). It is TI
copyright, all rights reserved, so it is not redistributed. Unzip it and copy
`TPS62136_PSPICE_TRANS/TPS62136_TRANS.lib` to `models/` (ignored by git). The copy used on
2026-10-22: `SLVMC09.zip` sha256 `764f65e3e817b73ef0690637fb1a08ab7fa04ec5a1858b203dc7cf555a04ad99`,
`TPS62136_TRANS.lib` sha256 `252dce79505a414bd31e4bd2209334de90761d277894c759c3f88da003439a56`.

The generic netlists need no vendor file.

## Run

Tools: ngspice 47 or later, Python 3.10+ through `uv`. Run from this folder, so `.spiceinit`
applies:

```sh
ngspice -b tps62903-5v1-step.cir     # one case; edit the .param line; writes step.dat
JOBS=2 uv run run.py step903 loop903 check
JOBS=2 uv run run.py step136 loop136 # TI model, about 2-4 min per case
```

`JOBS` sets how many ngspice processes run at once (default 2; keep it low on a shared
machine). Results go to `results/` (not committed); a case already in `results/` is not
run again. A generic case takes a few seconds; a TI-model case takes 2–4 minutes.
