# T1 main board project

The folder of the T1 main board's KiCad project. The schematic and the layout are not started; today it holds the project's rule composition and its craft check configuration, so both are in place when the project is created here.

| File | What it is |
|---|---|
| `t1-main-board.dru.toml` | The rule sources, in composition order: the PCBWay HDI fab rules and the OpenDAP craft rules (kicad-lib, submodule `../lib/opendap`), then the T1 product rules ([`../rules/`](../rules/)) |
| `t1-main-board.kicad_dru` | The composed rules KiCad reads. Generated, never edited by hand |
| `t1-main-board.craft.toml` | The craft check's target level (Q1 for prototype 1) and the mirrored blocks of CRAFT-34. The block references are placeholders until the schematic numbers its parts |

The constraints behind the product rules are in the [PCB design constraints](../../docs/specs/pcb-design-constraints.md); the method every OpenDAP board follows is toolkit-hardware's [PCB design constraints method](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/specs/pcb-design-constraints-method.md) (§8, rule composition).

## Commands

From the repository root, with toolkit-hardware's `odapkit` on the path:

```sh
odapkit dru compose hardware/t1-main-board/t1-main-board.dru.toml   # after any source changes
odapkit dru check                                                   # also the kicad-dru-composed pre-commit hook
odapkit craft check hardware/t1-main-board/t1-main-board.kicad_pcb  # once the layout exists
```

A source changes when the product rules are edited or when the kicad-lib submodule moves; the pre-commit hook then fails until the composition is regenerated.
