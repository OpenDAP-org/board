# OpenDAP T1: production variant and population options

- **Status:** Research, for the board team. Not a decision: it changes no requirement, ADR or BOM line. Items that touch a confirmed requirement are listed for the maintainers (§6).
- **Date:** 2026-10-22. Stock figures were captured on this date (JLCPCB parts API, the BOM's channel).
- **Basis:** [BOM v1.3](../specs/bom-v1.md), [power tree v0](../specs/power-tree-v0.md), [board requirements](../requirements/README.md) (BRD-053), board ADRs 0001–0012, [T1 requirements](https://github.com/opendap-project/t1/blob/main/docs/requirements/README.md), [experience budgets](https://github.com/opendap-project/t1/blob/main/docs/specs/experience-budgets.md), the [T1 UX research](https://github.com/opendap-project/t1/tree/main/docs/research/ux), the [HAT interface v0](https://github.com/opendap-project/hat-standard/blob/main/docs/specs/interface-v0.md) and hat-standard requirements, the [system architecture research](https://github.com/opendap-project/system/blob/main/docs/research/2026-10-system-architecture.md) and the OpenDAP OS [image composition](https://github.com/opendap-project/opendap-os/blob/main/docs/research/2026-10-image-composition.md) and [lifecycle](https://github.com/opendap-project/opendap-os/blob/main/docs/research/2026-10-os-lifecycle.md) research.
- **Conventions:** **UNVERIFIED** = no primary source checked in this session. **Estimate** = reasoned, not measured.

## 1. Purpose and rules

BRD-053 (Confirmed) asks the board to support assembly variants: prototypes populate every option; production variants may leave optional parts unpopulated (DNP) or fit lower-cost equivalents on the same footprint, without a respin, and every optional part is marked with its variant in the BOM. This report lists which lines can be population options in production, what each changes for the user, and which requirements each touches, so the options can be designed in from the start.

Never a population option here: the audio chain (DACs, headphone amplifiers, their rails and LDOs, the MCLK oscillators and their supply, the precision networks, the jacks, the bit-perfect and DSD paths), any power-safety margin (BRD-049), mainline driver support (BRD-001) and availability (T1-028, T1-029). The audiophile experience stays at 100 % (T1-040).

Each line is classed as **keep**, **DNP in production** (footprint stays, part omitted, software detects absence), **same-footprint alternative**, **substitute** (needs a respin or a different design) or **remove from design**.

Priorities follow the [priority audit](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-requirement-priorities.md) of 2026-10-22: BRD-014 (RP coprocessor), BRD-031 (ambient-noise microphone) and BRD-032 (IMU) are **should** and population options; BRD-014 holds as should only while no must function depends on the coprocessor, so its wake lines move to the SoC or the TCA6416A first. BRD-056, FPT-025 and FPT-026 are should. The musts T1-049 (no pops), T1-050 (DAC volume), T1-051 (exact resume), T1-052 (first import), T1-053 (pause on unplug, BRD-052), T1-054 (USB DAC at equal quality) and T1-055 (user-replaceable battery) bound what can be cut; the speaker (BRD-012, T1-016), the ambient light sensor (FPT-014) and projected-capacitive multi-touch (FPT-021) stay must.

T1-004 (Confirmed) builds the Commercial and DIY editions from exactly the same design. This report assumes the production population applies to both editions, and that prototypes are a separate build (BRD-053); the maintainers confirm this reading (§6).

## 2. Findings

1. **Few board lines can be omitted without changing what the user gets.** Three of the four INA236 current monitors (audio, display and HAT branches) and the voltage rating of the buck-output capacitors are the clear cases. The three hardware shoulds (IMU, ambient-noise microphone, RP2354A) are population options that remove gadget features, not listening ones; the RP2354A only after its wake lines move. Everything else serves a must, or is part of the audio chain or the safety design.
2. **The VSYS INA236 is a safety part, not instrumentation.** It enforces the interim battery budget and the headphone output ceiling of ADR 0012 (power tree §4.6, §4.11), so it stays.
3. **Memory and storage are the main same-footprint options.** A 16 GB eMMC keeps the experience; a 2 GB LPDDR4X puts responsiveness and long-session budgets at risk (§4).
4. **The HAT device-side piece is the largest assembly in the product outside the board.** Whether it is fitted to every T1 or as an option is a maintainers' decision (HCS-012); the board already supports both, provided it behaves correctly with the flat cable unmated (§5).

## 3. Line-by-line classification

### 3.1 Kept by rule

Audio chain and clocks: lines 18–31, 36, 37, 107–111 (T1-049, T1-050 and T1-054 rest on them; the jack detect switches serve T1-053). Power and safety: 2–7, 9, 22–29, 39, 41–45, 47, 48, 50, 51–53, 91, 92, 104, 106, and the VSYS INA236 on line 54. Core: 1, 15, 16, 17. Connectors and protection: 11, 61–66 (board end), 71, 73–75, 84, 85. Controls and glue: 76–78, 93–95, 97, 98.

### 3.2 Candidates

| # | Line(s) | Item | Class | What changes for the user | Requirements / ADR | Technical risks | Availability, driver | Prototype |
|---|---|---|---|---|---|---|---|---|
| C1 | 54 | INA236 on the audio, display and HAT branches | **DNP in production**; shunts stay fitted | Nothing in normal use. Per-block power readings for these three branches are not available on production units; battery state and time left come from the fuel gauge; HAT and USB-C budgets come from the VSYS INA236 and the eFuse IMON (power tree §4.6) | T1-026 is met on prototypes; BRD-049 is unaffected because the VSYS monitor stays | Keep the shunt resistors fitted so every supply path, including the audio feed, stays identical to the measured prototypes. OpenDAP OS must not enforce any limit from these three | Mainline `ina2xx-adc`; omitting the parts removes the thin Western stock risk for three of four | All four fitted |
| C2 | 54 | INA236 on VSYS | **Keep** | — | BRD-049; power tree §4.6, §4.11 | — | — | Fitted |
| C3 | §5 passives | 22 µF 0805 outputs of the non-audio bucks at ≤ 3.3 V (RK809 BUCK1–5, RK860, TPS62826, TLV62569): 25 V → 10 V X5R in the same case | **Same-footprint alternative** | None | BRD-049 (effective-capacitance check) | DC-bias derating differs between ratings: confirm each converter's minimum effective capacitance (TPS62826 Table 8-3, RK809 application circuit). Excluded: the TPS62840 audio pre-buck, the 5.1 V boost, the charger PMID/SYS and VBUS nodes | Samsung CL21A226MPQNNNE: LCSC 465,870 | Fit the 10 V part on one prototype build to validate ripple and load steps |
| C4 | 10 | eMMC 32 → 16 GB (Samsung KLMAG1JETD-B041, same family and FBGA-153 11.5 × 13 land) | **Same-footprint alternative** | About half the internal capacity (§4.2). The 16 GB part lists half the sequential write speed of the 32 GB part (50 against 100 MB/s, LCSC listing parameters), which slows copies to internal storage and OTA installs | BRD-037 (Draft) | Write endurance scales with capacity (**UNVERIFIED** for these parts); writes to the data partition must stay bounded (SYS-034) | LCSC 175: thin, like the 32 GB part | 32 GB; qualify one 16 GB build |
| C5 | 10 | eMMC 8 GB | Same-footprint alternative | Too little room for cache levels and artwork at the T1-046 scale (§4.2) | BRD-037, OS-022, T1-046 | Older part generation | Samsung KLM8G1GETF-B041: LCSC 822 | **Not recommended** |
| C6 | 8 | LPDDR4X 4 → 2 GB (SK hynix H9HCNNNBKUMLXR-NEE, 16 Gbit x32, 200 balls) | Same-footprint alternative | Risk to responsiveness and long sessions (§4.1) | BRD-037 (Draft), BRD-003, T1-045, T1-046, T1-047, OS-022, SYS-033, SYS-034, experience budgets | Same rkbin DDR init; package body is 10 × 14.5 or 10 × 15 mm depending on maker, so the courtyard should take both (**UNVERIFIED** per part) | LCSC 1,400 | 4 GB. **Not recommended**; qualify one 2 GB board only as a supply fallback |
| C7 | 81 + faceplate | Second-source display Displaytech DT035CTFT-IPS-SHB-PTS behind a DSI-to-RGB bridge on the faceplate (ADR 0006), for example Chipone ICN6211 | **Substitute** (new faceplate design; the board does not change) | 16-bit RGB interface (65 k colours against the 262 k of the RGB666 DSI mode of the current panel): banding on artwork and gradients is possible. Body about 1 mm taller (display research). ST1633I projected-capacitive touch instead of GT911 (palm rejection against FPT-021 **UNVERIFIED**). Backlight about 0.75 W instead of 0.9 W at full | Faceplate ADR 0001, FPT-018, FPT-019, FPT-021 (must), FPT-026 (should), T1-031, T1-032 | ST7796 has no mainline DPI driver (new compatible to upstream). ICN6211 has a mainline bridge driver (`drivers/gpu/drm/bridge/chipone-icn6211.c`); Debian 7.2.9 does not set `DRM_CHIPONE_ICN6211` (DKMS). Bridge power **UNVERIFIED** | ICN6211: LCSC 0, so it fails T1-029 today; TC358762 not listed. Displaytech: Digi-Key 256, Mouser 159 | Current panel. Not a production option until the bridge has stock |
| C8 | 67–69, 66 (device end) | HAT device-side piece fitted to every T1 | Configuration option (§5) | Without the piece, the T1 has a plain back cover and no HAT contacts until the piece is fitted | HCS-012, HCS-020 (Confirmed), hat-standard ADR 0001, HCS-003, T1-002, T1-017 | The board must behave with the flat cable unmated (§5) | No new parts | Always fitted |
| C9 | 67 | Pogo contact count | Design change (hat-standard) | None if only ground fencing is trimmed; any signal removed is a lost HAT capability | HCS-004, HCS-005, HCS-006, HCS-022 | Ground fencing protects the 5 Gb/s pairs: trim only after the flat-cable and pogo test coupon (HAT interface §7) | — | Full grid |
| C10 | 67 | Other pogo parts | Substitute after qualification | None if the envelope holds | HCS-006 (one part type, ideally) | Stocked generic pins (for example BAT WIRELESS BWCD, 10,000 cycles, 1.5 A) are 2 mm in diameter and cannot sit on the ≈ 1.27 mm grid of the interconnect benchmark; they miss its ≥ 100,000-cycle target. Multi-contact spring strips (Mill-Max 854/855 class, 1,000,000 cycles per the benchmark) are the realistic alternative | Harwin P70-1000045R: LCSC 0, Mouser 5,759 | Harwin |
| C11 | 55 | Wi-Fi 6 / BT 5.4 module | **Keep** | — | T1-027, BRD-025, BRD-029, BRD-030, BRD-001 | Alternatives checked: AMPAK AP6275S (Wi-Fi 6, BT 5.0) loses BT 5.4 and its pre-certification is **UNVERIFIED**; AP6256 is Wi-Fi 5; Murata Type 2EA (CYW55573) has no stock and an **UNVERIFIED** mainline status; u-blox MAYA-W271 is the same IW612 and stays the second source | Murata Mouser 2,820 | Murata |
| C12 | 56, 57 | Second U.FL connector and antenna | **DNP if** the Type 2EL has a single antenna port | None | BRD-025 | Port count **UNVERIFIED** (BOM line 56); with two ports both stay | — | As the module datasheet says |
| C13 | 57 | Antenna part | Same-type alternative (cable antenna, no land) | None | BRD-025: any other antenna must be on the module grant's antenna list (type, gain) | RF retune on the final enclosure | Many stocked dual-band FPC antennas | Molex |
| C14 | 59 | IMU (LSM6DSV16X) | **DNP in production** | Wake-on-motion and orientation are not available; no listening job or experience budget depends on them | BRD-032 (should, population option) | Its INT1 wake line (0_C5) is then unused; OpenDAP OS hides motion features when the part is absent (§6). An older same-family part is not needed and would conflict with T1-027 | LSM6DSV16X: LCSC 7,649 | Fitted |
| C15 | 60 | Ambient light sensor | **Keep** | Auto-dimming | FPT-014 | — | — | Fitted |
| C16 | 32, 33 | Speaker and its amplifier | **Keep** | Playing for someone without headphones (UX research, JTBD); T1-053 only governs when it plays | BRD-012, T1-016 | — | — | Fitted |
| C17 | 34 (one of two) | Ambient-noise microphone on the body | **DNP in production** | Ambient sensing and body-side recording are not available; the main faceplate microphone stays (FPT-004, FPT-017) | BRD-031 (should, population option) | The MIC_1V8 switch and the privacy LED stay for the main microphone (BRD-027); the case keeps or plugs the sound port | IM73D122: LCSC 5,327 | Fitted |
| C18 | 12–14, two of 50 | RP2354A, its oscillator, inductor and load switches | **DNP in production, conditional** | The in-device passive capture of the DAC stream is not available (the user-run bit-perfect check of UX-014 builds on BRD-041), nor the fast CMSIS-DAP probe for HAT chips (bit-banged SWD from the SoC remains, BRD-004) or the wake relay. Playback, bit-perfect output and its indicator are unaffected | BRD-014 (should, conditional); BRD-015 and BRD-041 apply when fitted; ADR 0004 | **Precondition:** pinout v1 moves every wake line from the RP to the SoC or the TCA6416A (the RP IRQ on 0_C7, the optional expander-INT wired-OR, the Wi-Fi wake relay), so no must function depends on it. DNP is electrically clean (BRD-019); RUN, BOOTSEL and SWD nets get defined pulls | RP2354A: LCSC 7,991 | Fitted |
| C19 | 79, 105 | RGB status LED and LP5521 | **Keep** | A single colour would reduce the status code to patterns only (controls spec §2) | FPT-025 (should), FPT-016, T1-044 (must) | A single colour needs its own drive path designed in as a second option; the gain is small | — | Fitted |
| C20 | 96 | Faceplate RST/TE translators | **Keep** | — | — | Removing them means running panel IOVCC at 3.3 V, the top of its 1.65–3.3 V range: no margin | — | Fitted |
| C21 | 86–89 | Test points | **Keep** | — | BRD-040, BRD-047; production test | — | — | — |
| C22 | 36, 62, 68, 69, 72–75 | ESD | **Keep** | — | BRD-007 | Already consolidated into two part numbers; the Commercial edition pins genuine-brand parts (BOM risk 13) | — | — |
| C23 | 14 | RP2350 oscillator → crystal | Substitute (different land) | None | — | Raspberry Pi tunes the crystal circuit for IOVDD 3.3 V only (BOM D6) | — | **Not recommended** |
| C24 | 46, 47 | Battery | **Keep** | — | ADR 0011, BRD-050, T1-038, T1-055 | No ADR 0011 pack found yet; the connector and fuse follow the pack, and T1-055 rules out soldered or glued packs | — | Interim pack |
| C25 | 103 | Item-tracking BLE module | Not in the design | — | BRD-030 | — | — | — |
| C26 | 58, 90, 100, 101 | RF matching, shields, mute shunts, gauge NTC | Already DNP by default | — | T1-049 (no pops) for line 100; BRD-054 allows shields | Shields and mute shunts become production parts if prototype measurements need them (audio first) | — | Fit as needed |

## 4. Memory and storage

### 4.1 LPDDR4X

- **Base image.** The trimmed root is 683 MiB raw, 231 MiB as LZMA erofs, with the OpenDAP software estimated at 30–80 MiB more; the init set uses about 24.6 MiB PSS (image composition §1, §9.1). The base image does not set the RAM size.
- **What uses RAM in the experience.** One process per activity (Slint with a GLES context), with activities destroyed under pressure to give RAM back to the page cache for music (system architecture §5.13); the architecture's risk table already names per-activity memory on 4 GB (§10). OS-022 uses RAM as a cache level for card music. T1-046 targets 1,000,000 tracks with ≤ 100 ms search at 500,000; T1-047 asks for flat behaviour over days; BRD-003 keeps on-board AI in scope.
- **Effect of 2 GB** (estimate): fewer resident activities, so more cold starts against the 150 ms screen-on and 200 ms open-a-view budgets; a smaller page cache, so the library index and artwork fall out of cache sooner, against the 100 ms search budget; a smaller OS-022 RAM level, so the card wakes more often (T1-009). The UX research identifies lag as the most common complaint about current players.
- **Proposal:** keep 4 GB. Draw the footprint for both 10 × 14.5 and 10 × 15 mm bodies, and qualify a 2 GB part on one prototype build only as a supply fallback.

### 4.2 eMMC

- **OS:** about 1 GiB (two ≈ 300 MiB A/B root slots, two ≈ 40 MiB boot/FIT partitions; image composition §9.1). The lifecycle research's first guess of two 3 GiB roots also fits 16 GB.
- **Data partition at 16 GB:** about 14 GB for the library index, the artwork cache (UX-034), capabilities, logs, the OS-022 eMMC cache level and any music kept internally. Music lives primarily on microSD (BRD-038, BRD-051). For 1,000,000 tracks, the index and display-size artwork are estimated at a few GB (**estimate**: about 80,000 albums × 30 kB thumbnails ≈ 2.4 GB, plus the index).
- **8 GB** leaves about 6 GB of data partition: too little for the cache level and artwork at the T1-046 scale.
- **Proposal:** 16 GB and 32 GB as population options on the same land; the production default is the maintainers' call (BRD-037).

## 5. HAT device-side piece

- The device-side piece carries the pogo field (about 128 contacts), its ESD (lines 68, 69) and the device end of the flat cable (line 66). HCS-012 fixes it to the T1.
- If the maintainers allow a T1 without the piece fitted (fitted later, and fixed once fitted), the board needs nothing new, but these must hold and be tested on a prototype with the cable unmated:
  - `HAT_DET#` reads high with its pull-up, and every 3.3 V HAT signal stays isolated or defined (HAT interface §2): the AXC translators' OE, the PCA9306 EN, eFuses #A and #B off.
  - The DF40 headers on the board (line 66) stay fitted, so the piece can be added without soldering.
  - The basic back cover meets the case's sealing and ESD requirements without the piece (T1-017, BRD-007).
- If the piece stays on every T1, the open levers are the pogo contact count after the test coupon (C9) and a qualified multi-contact part (C10).

## 6. Population variants and software detection

- Two variants: **PROTO** (every option fitted, BRD-053) and **PROD** (C1, C3, C14, C17, C18 once its precondition holds, and, if the maintainers agree, C4). Mark each optional line in the BOM with its variant.
- One prototype build should carry the PROD population, to confirm that the system boots, plays and suspends with the IMU, the ambient-noise microphone, the RP2354A and three INA236 absent.
- The board-ID EEPROM (line 17) should record the population variant and the memory and eMMC sizes. OpenDAP OS then applies the matching device-tree overlay, so an absent INA236 is never probed as a fault and no capability is shown that the hardware lacks (T1-045). I2C probing is the fallback.
- DDR and eMMC capacity are detected at boot (rkbin DDR init, eMMC EXT_CSD); recording them in the EEPROM helps support.
- A qualification build fits the production alternatives (10 V capacitors, a 16 GB eMMC, a 2 GB LPDDR4X sample), so every PROD substitution is validated on hardware before it ships (T1-026).

## 7. For the maintainers

| # | Question | Proposal |
|---|---|---|
| 1 | HAT device-side piece: on every T1 (HCS-012 as written), or fitted as an option and fixed once fitted | Allow the option; the board supports both (§5) |
| 2 | eMMC capacity (BRD-037, Draft) | 16 GB production default, 32 GB as a population option |
| 3 | LPDDR4X capacity (BRD-037, Draft) | Confirm 4 GB; 2 GB only as a qualified supply fallback |
| 4 | Production population for both editions (T1-004) | Same PROD population for the Commercial and DIY editions |
| 5 | Musts and shoulds this report keeps although omitting them was examined: speaker (BRD-012, T1-016), ambient light sensor (FPT-014), RGB status LED (FPT-025) | Keep |
| 6 | Second-source display path (C7) | Only once a DSI-to-RGB bridge has stock |

## 8. Sources

- Board: BOM v1.3 lines and §5, §8, §9; power tree v0 §4.6, §4.10, §4.11; requirements BRD-001 to BRD-053; ADRs 0002, 0004, 0006, 0010, 0011, 0012; pin multiplexing v0 §2.2, §3.
- T1: requirements T1-002 to T1-048; experience budgets; controls and status LED spec; UX research (persona and journey, playback and library, candidate requirements UX-014, UX-029, UX-034, UX-075).
- Touch faceplate: requirements FPT-014, FPT-016, FPT-018 to FPT-025; ADR 0001; display selection research.
- hat-standard: requirements HCS-003 to HCS-022; ADR 0001; HAT interface v0 §2, §3, §6, §7; interconnect benchmark.
- System and OpenDAP OS: system architecture §5.13 and risk table; image composition §1, §7.1, §9.1; OS lifecycle §4.2.
- Stock: JLCPCB parts API, 2026-10-22: SK hynix H9HCNNNBKUMLXR-NEE (C21912322), Samsung KLMAG1JETD-B041 (C499919), Samsung KLM8G1GETF-B041 (C499918), Samsung CL21A226MPQNNNE (C29277), Chipone ICN6211 (C246085), AMPAK AP6275S (C2918717) and AP6256 (C5248079), Harwin P70-1000045R (C17702549), BAT WIRELESS BWCD-L3.5W2.0H1.0 (C2826547), ST LSM6DSV16XTR (C5267406).
- Debian kernel configuration: `debian/config/config` and `debian/config/arm64/config` of `linux 7.2.9-1~bpo13+1` (sources.debian.org), read 2026-10-22.
