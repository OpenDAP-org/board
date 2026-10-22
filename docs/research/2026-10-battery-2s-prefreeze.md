# 2S battery: checks before the board freezes (ADR 0014)

- **Date:** 2026-10-22. All stock and price figures were captured on 2026-10-22.
- **Question:** do the open items of [ADR 0014](../adr/0014-two-cell-battery.md) "Consequences" hold: (1) is the TI BQ25798 supported by the mainline `bq257xx` driver written for the BQ25792, and what patch does it need; (2) does the Debian kernel enable the `bq257xx` and `bq27xxx` drivers on arm64, and does `bq27xxx` drive the BQ28Z610; (3) is there now a stocked, protected 2S pack for the pocket, and which pack makers publicly quote custom 2S packs?
- **Inputs:**
  - [ADR 0014](../adr/0014-two-cell-battery.md) and the [2S study](2026-10-battery-2s.md) §2, §3 and §7;
  - [battery for the full output budget](2026-10-battery-high-current.md) (pack search method) and [component selection](2026-10-component-selection.md) §2.1;
  - battery pocket 10.9 × 50.5 × 63.8 mm ([t1 ADR 0003](https://github.com/opendap-project/t1/blob/main/docs/adr/0003-tentative-body-size.md), via the 2S study).
- **Conventions:**
  - **UNVERIFIED** means no primary source was read in this session.
  - **Est.** marks an engineering estimate.
  - Dimensions are T × W × L in mm. Prices are USD at qty 1.
  - Register addresses are hexadecimal; "REG0F[0]" is bit 0 of register 0x0F.
  - Nothing here edits an ADR, the BOM or the power tree.

> **How this was gathered, and its limits.**
>
> - **Read directly:** mainline Linux (`torvalds/linux` master, `Makefile` 7.3) and linux-next (tag `next-20261022`) sources: `drivers/mfd/bq257xx.c`, `drivers/power/supply/bq257xx_charger.c`, `drivers/regulator/bq257xx-regulator.c`, `include/linux/mfd/bq257xx.h`, `Documentation/devicetree/bindings/mfd/ti,bq25703a.yaml`, `drivers/power/supply/bq27xxx_battery.c` and `bq27xxx_battery_i2c.c`, the `Kconfig` files of `drivers/mfd` and `drivers/power/supply`, and the git.kernel.org commit logs of these files; the kernel patchwork API (patchwork.kernel.org) for "bq25798", "bq25792" and "bq257xx"; TI BQ25798 datasheet SLUSDV2C (June 2026, sha256 `163e4568…f1e222`); TI BQ28Z610-R1 Technical Reference Manual SLUUC81 (sha256 `5663b323…927bd9`); the Debian kernel configuration on salsa.debian.org, branch `debian/latest` at commit `ab4d926d` (2026-10-22, `linux 7.3-1~exp1`); Digi-Key keyword listings; FindChips; the pages of Varta, Jauch, EEMB, Grepow, PKCELL, Renata, Ultralife, Epec, Inventus Power, Cadex and Large Power linked in §4.
> - **Not covered:** the **BQ25792 datasheet could not be read**: ti.com returns 404 for its datasheet and product page (the BQ25798 and BQ25895 pages return 200 from the same client), and no mirror was reached. The BQ25792 side of §1 therefore rests on the mainline register header and on the upstream commit that documents the BQ25798 (§1.1). lore.kernel.org answered with a bot challenge, so the mailing-list check used patchwork.kernel.org, which indexes the same lists. Web search was not available (session budget used up): only pages reachable by direct URL were read. Mouser returned an empty page, Farnell and RS returned HTTP 403, Arrow did not answer, and Digi-Key rate-limited (HTTP 429) after four keyword listings. Nothing in §1 was built or run.
> - **Not measured:** nothing here was tested on hardware.

---

## 0. Summary

1. **BQ25798 on mainline: no driver change is needed, and the binding is already upstream in linux-next.** (§1)
   - The BQ25798 is register-compatible with the BQ25792 for everything the `bq257xx` MFD and charger drivers touch: same I2C address (0x6B), same addresses, field positions, step sizes and offsets for all 16 registers the drivers read or write. The BQ25798 adds MPPT (REG15) and backup mode (REG0F[0], REG10[7:6], REG16[0], VBUS_STAT = 0xC), which the driver never enables; its init write to REG0F leaves backup mode off.
   - The driver never reads the part-ID register (REG48); it trusts the compatible. REG48 reads PN = 011b on the BQ25798; the BQ25792 value is **UNVERIFIED** (datasheet withdrawn).
   - **Upstream already took the BQ25798**: commit `c3746b35b050` "dt-bindings: mfd: ti,bq25703a: Expand to include BQ25798" (Alexey Charkov, 2026-09-17; acked by Rob Herring, applied by Lee Jones) is in linux-next. It documents `compatible = "ti,bq25798", "ti,bq25792"`, a fallback with no driver ID. Its commit message states that **TI has unpublished the BQ25792** and calls the BQ25798 its pin- and register-compatible replacement, which matches the 404s above. It is not yet in master.
   - **The patch master needs** is that binding change only (§1.4; draft kept outside the repository, not sent). OpenDAP has nothing to send for the ID: ADR 0014's "send the ID upstream" is already done by others.
   - **Gaps that matter to the T1** (same on the BQ25792): the `bq257xx-regulator` child still uses the BQ25703A OTG register descriptor for every chip (BQ25792 regulator support is at v8 on the list, not in linux-next), so the T1 device tree must not describe the charger's OTG output, which ADR 0014 does not use anyway; and the charger init sets `SFET_PRESENT`, clears `EN_EXTILIM` (the ILIM_HIZ pin limit) and disables the watchdog unconditionally (§1.3).
2. **Debian (`debian/latest`, 7.3-1~exp1):** `MFD_BQ257XX` and `CHARGER_BQ257XX` are **not set** (not named in either file, Kconfig has no default). `BATTERY_BQ27XXX=m`, but `BATTERY_BQ27XXX_I2C` is **explicitly "is not set"** in `debian/config/config` and `arm64/config` does not override it: **the BQ28Z610 has no I2C driver in Debian's arm64 kernel**, resolving the 2S study's **UNVERIFIED**. Both the charger and the gauge front end need DKMS (OS-023) until Debian enables them. (§2)
3. **`bq27xxx` drives the BQ28Z610:** it binds `ti,bq28z610` (I2C id `bq28z610`), uses a BQ27Z561-style register table and flag layout, and every standard command it reads matches the BQ28Z610-R1 TRM (§2.2). It writes no data memory for this chip, so the gauge configuration (cell count, chemistry, protection thresholds) is a production programming step, not a driver task.
4. **Pack search: still no stocked pack fits.** The only new stocked protected 2S pack is the **Varta CellPac LITE 2S/LIC 18650-26** (3.0 A continuous, IEC 62133, Sager 1,127 @ $23.49), at 18.5 × 37.2 × 70 mm: too thick and too long (§3). ADR 0014 item 2 (quoted pack) stands.
5. **Custom 2S pack makers with a public offer:** Grepow, EEMB, Jauch, Varta (CellPac PLUS), Renata, Ultralife, Epec, Inventus Power, Cadex, Large Power and PKCELL (§4). **None publishes a minimum order quantity**; Renata states custom work for "larger-volume projects", and Epec publishes certification sample counts (17 for UN 38.3, 50 for UL/IEC). Two independent quotes (ADR 0014 item 2) need direct requests.

---

## 1. BQ25798 against the mainline `bq257xx` driver

### 1.1 Upstream state

| Item | master (7.3) | linux-next (next-20261022) | Source |
|---|---|---|---|
| `bq257xx` MFD: `ti,bq25703a`, `ti,bq25792` | Yes | Yes | `drivers/mfd/bq257xx.c` |
| BQ25792 MFD support | Yes (`9adbe53e32cd`) | Yes | commit log |
| BQ25792 self-modifying registers marked volatile (REG05–06, 0F, 11, 13, 2E) | **No** | Yes (`56d974f3ad07`, Cc stable) | commit log |
| BQ25792 charger support | Yes (`13cf94703737`) | Yes, plus `.init` callback conversion (`455e49c6700c`) | commit log |
| BQ25792 OTG regulator support | **No** | **No** ("regulator: bq257xx: Add support for BQ25792" v8, 2026-07-27, linux-pm patchwork) | patchwork |
| Binding `ti,bq25798` with `ti,bq25792` fallback | **No** | **Yes** (`c3746b35b050`, 2026-09-17) | commit log; patchwork shows v1 on 2026-09-14 and v2 on 2026-09-17 |
| Any other BQ25798 patch (driver ID, MPPT, backup mode) | — | — | none on patchwork for "bq25798" besides the binding |

### 1.2 Register comparison

The BQ25792 column is the mainline header (`include/linux/mfd/bq257xx.h`, written for the BQ25792) and the upstream commit message; the BQ25798 column is SLUSDV2C §7.5. Only registers and fields the drivers use are listed.

| Reg | Field(s) used by the driver | BQ25792 (header) | BQ25798 (SLUSDV2C) | Driver access | Difference |
|---|---|---|---|---|---|
| 00 | VSYSMIN[5:0] | 2.5–16 V, 250 mV, offset 2.5 V | Same; 2S POR 7.0 V | read, write (= battery `voltage-min-design`) | None |
| 01 | VREG[10:0], 16-bit | 3.0–18.8 V, 10 mV | Same; 2S POR 8.4 V | read, write | None |
| 03 | ICHG[8:0], 16-bit | 50 mA–5 A, 10 mA | Same | read, write | None |
| 06 | IINDPM[8:0], 16-bit | 100 mA–3.3 A, 10 mA, default 3 A | Same, POR 3,000 mA | read, write | None |
| 0A | CELL[7:6], TRECHG[5:4], VRECHG[3:0] | 1–4S; 64–2048 ms; 50–800 mV, 50 mV | Same | write (2S chosen when VREG < 10 V) | None |
| 0F | EN_AUTO_IBATDIS, EN_CHG, EN_ICO, EN_TERM | bits 7, 5, 4, 1; bit 0 not defined | Same; **bit 0 = EN_BACKUP** | write 0xB2 | BQ25798 only: the write clears EN_BACKUP (backup off, its POR value) |
| 10 | VAC_OVP[5:4], WD_RST, WATCHDOG[2:0] | bits 7:6 not defined | Same; **bits 7:6 = VBUS_BACKUP** | write 0x00 | BQ25798 only: VBUS_BACKUP set to 40 % of VINDPM; no effect while backup is off. VAC_OVP 26 V, watchdog off |
| 14 | SFET_PRESENT, EN_IBAT, IBAT_REG[4:3], EN_IINDPM | bit 6 reserved | Same | write 0xB4 | None (see §1.3) |
| 15 | — | "REG15 reserved" | **MPPT control** | in the writeable range, never written | BQ25798 only; POR EN_MPPT = 0 |
| 16 | — | bit 0 not defined | **bit 0 = BKUP_ACFET1_ON** | not accessed | BQ25798 only |
| 1B | PG_STAT (bit 3) | Same | Same | read | None |
| 1C | CHG_STAT[7:5] | Same | Same; VBUS_STAT[4:1] adds 0xC "Backup Mode" | read (CHG_STAT only) | None for the driver |
| 20 | VBAT/VAC2/VAC1 OVP, IBAT/CONV OCP | Same | Same | read | None |
| 2E, 2F, 30 | ADC_EN; per-channel disables | Same | Same | write | None |
| 33 | IBAT_ADC, 16-bit two's complement, 1 mA | Same | Same | read | None |
| 3B | VBAT_ADC, 16-bit, 1 mV | Same | Same | read | None |
| 48 | PN[5:3], DEV_REV[2:0] | masks only, no value | PN = 011b, DEV_REV = 001b | **never read** | Value for BQ25792 **UNVERIFIED** |

The commit message of `c3746b35` places one backup bit at "reg 0x0f[1]" and backup status at "0x1c[7:5]"; SLUSDV2C shows EN_BACKUP at REG0F[0] (bit 1 is EN_TERM) and the backup state in VBUS_STAT (REG1C[4:1]). Neither affects the driver.

**Reading:** a BQ25798 behaves under the mainline driver exactly as a BQ25792 does. Its extra features stay at their POR state (MPPT off) or are forced off (backup).

### 1.3 Driver behaviour that matters to the T1 (applies to both chips)

| Behaviour (source) | Effect on the T1 | What the T1 does |
|---|---|---|
| The MFD always registers a `bq257xx-regulator` child, and the regulator driver uses the BQ25703A OTG descriptor (enable REG 0x34 bit 12, voltage REG 0x06) for every chip (`bq257xx-regulator.c`, master and next) | On a BQ2579x those addresses are the IBAT ADC and **IINDPM**; a consumer that set the OTG voltage would write IINDPM | ADR 0014 does not use the charger OTG. The device tree omits the `regulators` node, and the DKMS package does not ship the regulator module until BQ25792 regulator support lands (§1.1). With no node, the regulator has no constraints and is not driven (code reading, **not tested**) |
| `hw_init` writes REG14 with `SFET_PRESENT = 1` and `EN_EXTILIM = 0` | The charger assumes a ship FET; the ILIM_HIZ pin resistor no longer limits input current once the driver loads | The schematic either fits the ship FET or accepts SFET_PRESENT = 1 without one (effect not described in SLUSDV2C, **UNVERIFIED**). The input limit comes from the DT `input-current-limit-microamp` (required by the binding) |
| `hw_init` writes REG10 = 0: watchdog disabled ("TODO: make it work instead") | Settings persist if Linux hangs; no watchdog fallback to POR defaults | A safety review item for BRD-049; the PROG-pin defaults and pack PCM still bound the hardware |
| `voltage-min-design-microvolt` of the battery node is written as VSYSMIN | VSYS floor equals the battery's minimum design voltage | Set it to 6.0 V for the ADR 0014 VSYS range |
| `constant-charge-voltage-max-microvolt` < 10 V selects 2S | 8.4 V (or LiHV up to 8.8 V, ADR 0008) selects 2S correctly | — |
| Interrupt requested on both edges | — | Wire INT to a GPIO with edge interrupts |

### 1.4 Draft patch

A unified diff against master, `Documentation/devicetree/bindings/mfd/ti,bq25703a.yaml`, 10 insertions and 4 deletions: the compatible becomes `oneOf` an enum (`ti,bq25703a`, `ti,bq25792`) or the pair `ti,bq25798` + `ti,bq25792`, and the BQ25792 limits apply when the compatible **contains** `ti,bq25792`. It is identical to linux-next `c3746b35b050` and was checked to apply cleanly to master (`git apply --check`). **It was not sent** and should not be: upstream already carries it. No C change is needed. The draft and an illustrative charger and gauge device-tree fragment are kept in the session scratch area, not in this repository.

For OpenDAP OS (OS-023, [opendap-os ADR 0007](https://github.com/opendap-project/opendap-os/blob/main/docs/adr/0007-kernel-modules-through-dkms.md)), the DKMS package for the charger is the mainline `bq257xx` MFD and charger built from source, carrying `56d974f3ad07` (volatile registers) until it reaches the Debian kernel. The device tree uses `compatible = "ti,bq25798", "ti,bq25792"`.

---

## 2. Debian kernel configuration and the BQ28Z610

### 2.1 Configuration values

Branch `debian/latest`, commit `ab4d926d` (2026-10-22), changelog `linux (7.3-1~exp1) UNRELEASED`. The arm64 flavour uses `debian/config/config` plus `debian/config/arm64/config`.

| Option | `config` | `arm64/config` | Effective on arm64 | Kconfig default |
|---|---|---|---|---|
| `CONFIG_MFD_BQ257XX` | not named | not named | **not set** | none (off) |
| `CONFIG_CHARGER_BQ257XX` | not named | not named | **not set** (depends on `MFD_BQ257XX`) | none (off) |
| `CONFIG_BATTERY_BQ27XXX` | `=m` (line 4501) | `=m` (line 2098) | **m** | — |
| `CONFIG_BATTERY_BQ27XXX_I2C` | `# ... is not set` (line 4502) | not named | **not set** | `default y` |
| `CONFIG_BATTERY_BQ27XXX_HDQ` | `=m` | not named | m | — |
| `CONFIG_CHARGER_BQ25890` (reference) | not set | `=m` | m | — |

**Reading:** Debian builds the `bq27xxx` core but not its I2C front end, so the BQ28Z610 gets no driver on arm64. The front end is a separate module (`bq27xxx_battery_i2c.o`) that uses symbols the core exports (`bq27xxx_battery_setup`, `_teardown`, `_update`), so DKMS can build it alone against Debian's headers. The `bq257xx` MFD and charger are off and must come from DKMS as a pair. Asking Debian to enable `BATTERY_BQ27XXX_I2C` and `MFD_BQ257XX` / `CHARGER_BQ257XX` as modules on arm64 would end both DKMS needs; that request has not been made.

### 2.2 `bq27xxx` and the BQ28Z610

| Check | Driver | BQ28Z610-R1 TRM (SLUUC81) | Match |
|---|---|---|---|
| Binding | `ti,bq28z610` (OF table), `bq28z610` (I2C id) | 7-bit address 0x55 | — |
| Chip data | `BQ28Z610`: own register table, options `BQ27Z561_O_BITS`, no data-memory table | — | — |
| Temperature | 0x06 | 0x06/07 Temperature(), 0.1 K | Yes |
| Voltage | 0x08 | 0x08/09 Voltage(), mV | Yes |
| Flags | 0x0A; FDC bit 4, FC bit 5, discharging bit 6 | 0x0A/0B BatteryStatus(): FD bit 4, FC bit 5, DSG bit 6 | Yes |
| Average current | 0x14 | 0x14/15 AverageCurrent(), mA | Yes |
| Time to empty / full | 0x16 / 0x18 | AverageTimeToEmpty() / AverageTimeToFull(), min | Yes |
| Remaining / full charge capacity | 0x10 / 0x12 | RemainingCapacity() / FullChargeCapacity(), mAh | Yes |
| Average power | 0x22 | 0x22/23 AveragePower(), mW | Yes |
| Cycle count, SoC, design capacity | 0x2A, 0x2C, 0x3C | CycleCount(), RelativeStateOfCharge(), DesignCapacity() | Yes |

The driver exposes status, presence, voltage, current, capacity and level, temperature, time to empty and full, charge now and full, design capacity, cycle count, average power, health and manufacturer. It does not expose per-cell voltages or balancing state, and writes no data memory for this chip: cell count, chemistry and protection thresholds are programmed into the gauge in production (TI's flow in SLUUC81), not by Linux.

---

## 3. Stocked 2S packs, second search

Criteria from ADR 0014 item 2: protected (PCM), continuous rating ≥ 3.0 A, fits 10.9 × 50.5 × 63.8 mm, in authorized stock.

| Pack | Capacity / energy | T × W × L | Continuous | PCM / certifications | Stock / price | Fails |
|---|---|---|---|---|---|---|
| **Varta CellPac LITE 2S/LIC 18650-26** (56653 502 012), new | 2,600 mAh / 18.9–19.0 Wh (7.3 V) | **18.5** × 37.2 × **70** | **3.0 A** | Varta states UL 2054 and IEC 62133 for the range | Sager **1,127** @ $23.49 (FindChips) | Thickness, length (cylindrical 18650) |
| Jauch LI18650JLS HB 2S1P+PCM+PTC | 3,350 mAh (7.2 V) | **20** × 38 × 69 | Not read | PCM + PTC | Digi-Key 312 @ $18.21 | Thickness, length |
| Jauch LI18650JP2S1P+PCM | 3,250 mAh (7.2 V) | **20** × 38 × 69 | Not read | PCM | Digi-Key 1,439 @ $25.68, **obsolete** | Thickness, length, lifecycle |
| SparkFun PRT-11855 | 1,000 mAh / 7.4 Wh | **18** × 35 × 70 | 25C (vendor) | **None** | Digi-Key 38 @ $17.04 | No PCM, thickness |
| GlobTek BL1800P0639602S1PPLB | 1,800 mAh | **14** × 43.5 × 60 | Not stated | Not read | Digi-Key **0** | Stock, thickness |
| GlobTek BL1200F7034452S1PQAN | 1,200 mAh | **15** × 35 × 46 | Not stated | Not read | Digi-Key **0** | Stock, thickness |

The Digi-Key rows are unchanged from the [2S study](2026-10-battery-2s.md) §2.1. Catalogs that list no 2S pack: Jauch lithium-polymer range (3.7 V only), EEMB rechargeable and custom pack categories (example packs at 3.7 V and 14.8 V only), Renata lithium polymer (cells of 35–2,800 mAh). Ultralife's standard packs are military and industrial ranges (not read in detail). Mouser, Farnell, RS and Arrow were not reached (header).

**Reading:** the only stocked, protected 2S packs with a published rating of at least 3.0 A are 2S 18650 assemblies, 18.5–20 mm thick. A flat 2S pack of two pouch cells is still not stocked anywhere that was reached. ADR 0014 item 2 (quoted pack, two independent makers) stands.

---

## 4. Makers that publicly offer custom 2S packs

"Published MOQ" is what the page says about minimum order; "not published" means the page read gives none.

| Maker | Page | Custom offer (as published) | Published MOQ | Notes |
|---|---|---|---|---|
| Grepow | [custom battery](https://www.grepow.com/custom-battery.html) | Cell, structure and BMS customization, "1~24S Battery BMS Customization" | Not published | Also makes LiPo cells |
| EEMB | [custom request](https://www.eemb.com/custom) | Request form with cells in series and parallel, PCM/BMS, enclosure, UL / CE / IEC 62133 / UN 38.3 | Not published (form asks prototype and production quantities) | <DesignMyBattery@eemb.com> |
| Jauch | [custom battery request](https://www.jauch.com/en-INT/products/battery_technology/custom_battery_request) | Form with gauge/BMS, thermistor, enclosure, UL2054, UL1642, UN38.3, IEC 62133-2:2017; in-house UN 38.3 laboratory | Not published; its LiPo page states "custom sizes are available at relatively low production volumes" (cells) | Germany, Eastern Europe, China |
| Varta | [CellPac PLUS](https://www.varta-ag.com/en/industry/product-solutions/power-pack-solutions/cellpac-plus) | Custom lithium packs from consultation to production and certification | Not published | Also CellPac BLOX (semi-standard) |
| Renata | [lithium polymer](https://www.renata.com/en/products/lithium-polymer-batteries/) | "individualized solutions and modifications for larger-volume projects" | Not published ("larger-volume") | Cells up to 2,800 mAh, 4.2–4.35 V |
| Ultralife | [custom solutions](https://ultralifecorporation.com/battery-energy/custom-solutions/) | Concept to production, qualification and certification support | Not published | — |
| Epec | [custom lithium packs](https://www.epectec.com/batteries/custom-lithium-battery-packs.html), [lead times](https://www.epectec.com/batteries/battery-pack-standard-lead-times-and-prototypes.html) | Custom Li-ion packs; prototypes 4–6 weeks; UN 38.3 6–8 weeks (17 samples); UL/IEC 6–8 weeks (50 samples) | Not published | United States and Asia |
| Inventus Power | [custom battery packs](https://inventuspower.com/custom-battery-packs/) | Custom battery solutions | Not published | — |
| Cadex | [OEM batteries](https://www.cadex.com/custom-solutions/oem-batteries) | Custom Li-ion packs | Not published | — |
| Large Power | [custom solutions](https://www.large.net/custom-lithium-ion-battery-solutions/) | 7.4 V Li-ion packs to specification; UN 38.3, IEC 62133; prototypes 15–20 days (standard) or 25–45 days | Not published; FAQ: "we do not offer off-the-shelf inventory" | — |
| PKCELL | [home](https://www.pkcell.net/) | "PCM/BMS protection integration" and custom lithium configurations | Not published | Pouch packs not named explicitly |

GlobTek (2S packs in the Digi-Key listings) may also build to specification; its custom offer was not read (**UNVERIFIED**).

**Reading:** at least eleven makers publicly offer custom multi-cell packs with protection and the certifications ADR 0014 asks for, on three continents, so the two independent quotes of item 2 are reachable. None publishes a minimum order quantity; quantities and prices need a request against one specification (ADR 0014 item 2).

---

## 5. Consequences for ADR 0014

- **"Confirm the BQ25798 register map against the mainline BQ25792 support":** confirmed for every register the driver uses (§1.2); the only unread item is the BQ25792 REG48 value, which the driver does not use.
- **"Send the ID upstream":** already done upstream by another contributor (`c3746b35b050`, linux-next). OpenDAP OS uses the fallback compatible and ships `bq257xx` through DKMS until Debian enables it.
- **"Confirm Debian's `BATTERY_BQ27XXX_I2C` on arm64":** it is **off**. The BQ28Z610 front end also needs DKMS (or a Debian config change).
- **Pack:** no stocked pack fits; request quotes from at least two makers in §4.
- **New board-level items:** decide whether to fit the BQ25798 ship FET (the driver sets SFET_PRESENT); do not route the charger OTG in the device tree; review the disabled watchdog under BRD-049.

---

## 6. Sources

- Linux: [drivers/mfd/bq257xx.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/mfd/bq257xx.c), [drivers/power/supply/bq257xx_charger.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/power/supply/bq257xx_charger.c), [drivers/regulator/bq257xx-regulator.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/regulator/bq257xx-regulator.c), [include/linux/mfd/bq257xx.h](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/linux/mfd/bq257xx.h), [ti,bq25703a.yaml](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Documentation/devicetree/bindings/mfd/ti,bq25703a.yaml), [bq27xxx_battery.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/power/supply/bq27xxx_battery.c), [bq27xxx_battery_i2c.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/power/supply/bq27xxx_battery_i2c.c); linux-next commits [c3746b35b050](https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=c3746b35b0503a90d744347bee22c9a9c04b7fd4) and [56d974f3ad07](https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=56d974f3ad074a60bf877d131eab8b1df5b4f069); [patchwork search "bq25798"](https://patchwork.kernel.org/api/patches/?q=bq25798) and ["bq25792"](https://patchwork.kernel.org/api/patches/?q=bq25792).
- Debian: [debian/config/config](https://salsa.debian.org/kernel-team/linux/-/blob/debian/latest/debian/config/config), [debian/config/arm64/config](https://salsa.debian.org/kernel-team/linux/-/blob/debian/latest/debian/config/arm64/config).
- TI: [BQ25798 datasheet SLUSDV2C](https://www.ti.com/lit/ds/symlink/bq25798.pdf), [BQ25798 product page](https://www.ti.com/product/BQ25798), [BQ28Z610-R1 TRM SLUUC81](https://www.ti.com/lit/ug/sluuc81/sluuc81.pdf); [BQ25792 product page](https://www.ti.com/product/BQ25792) (404 on 2026-10-22).
- Stock: [FindChips 56653502012](https://www.findchips.com/search/56653502012); [Digi-Key rechargeable batteries](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91) (keywords "7.4V", "7.4 V", "2S1P", "7.2V").
- Packs and makers: [Varta CellPac LITE](https://www.varta-ag.com/en/industry/product-solutions/power-pack-solutions/cellpac-lite), [Jauch lithium polymer](https://www.jauch.com/en-INT/products/battery_technology/getPrm/batteries/Lithium%20Polymer%20Batteries/), [EEMB rechargeable packs](https://www.eemb.com/categories-64) and the maker pages in §4.
