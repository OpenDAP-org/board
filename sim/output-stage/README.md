# Headphone output stage: ngspice simulation

The question: does the ADR 0012 output stage hold its BRD-049 margins? The study checks
the TPS65131 ±7 V pre-rails under the worst-case output load, current sharing between
the paralleled OPA1622 halves, and the LT3045 / LT3094 headroom; then the replacement
−7 V converter (LMR33630C inverting buck-boost) and the paired-LDO current limits. Results and their limits
are in [`docs/research/2026-10-output-stage-simulation.md`](../../docs/research/2026-10-output-stage-simulation.md).

## Files

| File | What it is |
|---|---|
| `tps65131-switch-model.cir` | Switch-level TPS65131 model (subcircuits) built from SLVS493E parameters. Not a TI model: TI publishes none. |
| `tps65131-dc-load.cir` | Both pre-rails at one DC load point; prints the peak switch current and % of the 1.8 A minimum limit. |
| `tps65131-audio-load.cir` | Both pre-rails under a full-wave rectified sine load (full-scale sine, both channels). |
| `lmr33630-ibb.cir` | −7 V pre-rail from VSYS with an LMR33630C as an inverting buck-boost (follow-up, research note §5), TI transient model. |
| `opa1622-model-check.cir` | TI OPA1622 model against SBOS727B Table 2 (±5 V, 16 and 32 Ω). |
| `opa1622-paralleled-halves.cir` | One balanced channel: two legs, each two paralleled halves with 1.0 Ω ballast, worst-case offset and resistor spread. |
| `sweep.py` | Runs the TPS65131 sweeps of the research note into `results/*.csv` (standard library only). |
| `.spiceinit` | Sets ngspice's PSpice compatibility mode, needed by the TI OPA1622 and LMR33630C models. |

## Vendor models (not in this repository)

Two netlists need TI models, which are TI copyright with all rights reserved, so they
are not redistributed here. Put them in `models/` (ignored by git):

| Netlist | Model | File to place in `models/` | Copy used on 2026-10-22 (sha256 of the zip) |
|---|---|---|---|
| `opa1622-*.cir` | [SBOM958](https://www.ti.com/lit/zip/SBOM958), OPA1622 PSpice model, Rev. D | `OPA1622.LIB` | `1bafa50b657ea2ece0c1d3e1ab7684556093d824a7d749aaaf07a933b81e49b8` |
| `lmr33630-ibb.cir` | [SNVMBG5](https://www.ti.com/lit/zip/SNVMBG5), LMR33630C unencrypted inverting and non-inverting transient model, Rev. A | `LMR33630C_TRANS.lib` | `bf3d8f3b2d33a7e957147972194555b7883da88efde2ba4275be0a23c69bc2b7` |

No vendor model is needed for the TPS65131 netlists. TI lists no TPS65131 transient
model, and the LT3045 / LT3094 figures come from their datasheets (LTspice models are
not used).

## Run

Tools: ngspice 47 or later with XSPICE code models (the Homebrew build has them), and
Python 3.10+ through `uv`. Run from this folder, so `.spiceinit` and the relative
includes resolve:

```sh
ngspice -b tps65131-dc-load.cir          # one point (edit the .param lines)
ngspice -b tps65131-audio-load.cir
ngspice -b opa1622-model-check.cir
ngspice -b opa1622-paralleled-halves.cir
ngspice -b lmr33630-ibb.cir              # 15-25 min for 5 ms
uv run sweep.py margin                   # also: ceiling, calibration
```

`JOBS=n` sets how many ngspice runs `sweep.py` starts at once (default 2). A DC point
takes about 4 s; the margin sweep is 84 points.
