# OpenDAP T1: sourcing alternatives for poorly available parts

- **Date:** 2026-10-22. All stock and price figures were captured on 2026-10-22 unless a row says otherwise.
- **Input:** the risks list and "not verified" items in [`2026-10-component-selection.md`](2026-10-component-selection.md) (§3, §5.2, §5.3, §6.4, §7, §9.2, §12).
- **Owner rules applied:**
  1. **Availability first, then validate.** Every final pick below was checked against a live stock figure.
  2. Among compatible parts, prefer the best availability and the most recent generation.
  3. Mainline Linux driver for anything that needs one. A DKMS build is acceptable when Debian does not enable a mainline module. A vendor-published GPL-2.0 driver built as DKMS is also acceptable when it looks validated.
  4. For the display, availability outranks "already enabled in Debian". OpenDAP may upstream a new panel compatible with its init sequence.
  5. The commercial edition and the DIY kit (JLCPCB/PCBWay assembly) share one design.
  6. Audio quality and battery life are the top priorities.
  7. Radios: certified or pre-certified modules first. No radio is in scope here; the Wi-Fi/BT choice stays in the component-selection report and should be re-ranked there under this rule.
- **Conventions:**
  - **UNVERIFIED** means no primary source was found in this session.
  - **(vendor claim)** means the only source is the maker's or distributor's own text.
  - Prices are USD at qty 1 unless a break is given.
  - "LCSC" stock comes from the JLCPCB parts API (`selectSmtComponentList`), which matches the LCSC product page.

> **How this was gathered, and its limits.**
>
> - **Distributors:** Digi-Key search and product pages were fetched directly. Mouser, Newark, TME, Arrow-group and broker stock came from the [FindChips](https://www.findchips.com/) aggregator, with the link pattern `https://www.findchips.com/search/<MPN>`. FindChips also lists brokers (Win Source, Vyrian, IBS, Quest, Bristol); those are named as brokers and are **not** treated as authorized stock.
> - **Kernel:** driver sources were read from `torvalds/linux` master and the `v7.2`/`v7.3` tags. Debian status was read from `linux-config-7.2_7.2.9-1~bpo13+1_arm64.deb` (trixie-backports) and `linux-config-7.3_7.3~rc7-1~exp1_arm64.deb` (experimental), both from `deb.debian.org/debian/pool/main/l/linux/`.
> - **Not covered:**
>   - The session's web-search budget ran out early, and a search-engine bot challenge was not bypassed. Marketplace listings (Alibaba, AliExpress, Taobao, Made-in-China) and makers without a fetchable catalog (Grepow, EEMB, PKCELL, Varta, Renata, Ansmann, Kycon, Hosiden) could not be searched. Those rows are **UNVERIFIED**.
>   - Mouser pages time out when fetched directly, so Mouser figures come only from FindChips.
>   - PCBWay has no public parts catalog.
>   - Nothing here has been tested on hardware.

---

## 0. Summary of recommended picks

| # | Item | Recommendation | Driver path | Availability (2026-10-22) |
|---|---|---|---|---|
| 1a | 4.4 mm balanced jack | **Genuine Pentaconn through NDICS's Hong Kong/Shenzhen offices** (commercial). Lay out a dual footprint so the LCSC-stocked **G-Switch GT-3321667P-01** can be fitted for the DIY kit and as a fallback | n/a | Pentaconn: quote only. G-Switch: LCSC 730 @ $7.30 |
| 1b | 3.5 mm jack | **Same Sky SJ2-35954D-SMT-TR** (TRRS, gold, two switches) | `simple-audio-card` jack detection on a GPIO | Mouser 4,528; Digi-Key 850 cut tape plus reel |
| 2 | Display | **Focus LCDs E35GH-I-MW800-CB** (3.5" 320×480 IPS, 1-lane MIPI DSI, ILI9488, GT911, 800 nit) for fit, **or Newhaven NHD-3.5-640480EF-MSXP-CTP** (640×480, 810 nit) if the body can grow to ≈66 mm | ILI9488: exact mainline compatible since 7.3, Debian off → DKMS. Newhaven: ST7703-class, so a new compatible in a Debian-enabled driver | Focus: Digi-Key 9 + Focus direct 9 (thin). Newhaven: Digi-Key 189, Mouser 128, TME 9 |
| 3 | Battery | **Jauch LP705176JS+PCM** (3,000 mAh) as a factory variant with 10 kΩ NTC and a JST-PH lead; **Adafruit 328** (2,500 mAh) as the stocked second source and DIY-kit pack | n/a (gauge and charger elsewhere) | Jauch: Digi-Key 199 @ $21.59. Adafruit 328: Digi-Key 1,834 @ $14.95 |
| 4 | Audio MCLK | **NDK NZ2520SDA**: `NSC5083D-45.158M` and `NSC5083D-49.152M` (3.3 V). Use `NSC5083A` (1.8 V) if the clock rail is 1.8 V | n/a | Digi-Key 2,801 / 3,404 @ $2.94 |
| 5 | IP-rated USB-C | USB 2 + PD: **GCT USB4730-GF-A-KIT** (IP67, gasket included). USB 3 + mid-mount: **Same Sky UJ31-CH-3-MSMT-TR-67** | n/a | GCT: Digi-Key 15,083 @ $1.86. Same Sky: Digi-Key 13,661 @ $3.82 |
| 6 | Microphones | **Keep Infineon IM73D122**. Same-footprint second source: **Infineon IM72D128** | `rockchip_pdm` + `dmic` (Debian on) | IM73D122: Mouser 15,038, Newark 20,502, LCSC 5,352. IM72D128: Mouser 48,099 |
| 7 | LPDDR4X 4 GB / eMMC 32 GB | **Samsung K4UBE3D4AB-MGCL** and **Samsung KLMBG2JETD-B041** from LCSC. Second sources: SK hynix H9HCNNNCPMMLXR-NEE and FORESEE FEMDNN032G-C9A55 | rkbin `rk3566_ddr_1056MHz` **v1.26 or newer** | LCSC 236 @ $82.09 and 270 @ $40.33 |
| 8 | Charger | **Keep TI BQ25895** for v1. Newer-generation powerbank-HAT upgrade: **TI BQ25798** (best stock of the buck-boost parts) | BQ25895: mainline + Debian on. BQ25798: needs a new compatible in `bq257xx` + DKMS | BQ25895: LCSC 5,954, Mouser 3,608. BQ25798: Mouser 9,488, LCSC 5,148 |

---

## 1. Headphone jacks

### 1.1 4.4 mm balanced (JEITA RC-8141C, 5-pole)

**Authorized Pentaconn channel.**

- Pentaconn is made by **NIPPON DICS CO., LTD. (NDICS)**, Tokyo. Sources: [ndics.com Pentaconn page](https://www.ndics.com/brands/pentaconn/), [company page](https://www.ndics.com/en/).
- NDICS has its own sales offices close to Shenzhen assembly:
  - NDICS Hong Kong Limited, +852 2735-9339;
  - an NDICS Shenzhen representative office, +86 755-2775-4558;
  - NDICS Malaysia;
  - a dedicated Pentaconn line in Japan, +81 3-5793-3398.
- **This is the authorized OEM channel. Ask the Hong Kong or Shenzhen office for the PCB jack catalog, MOQ, lead time and drawings.**
- The retail [Pentaconn Online Shop](https://pentaconn.shop/) sells plugs, cables and earphones only. It lists **no PCB-mount jack**.
- NDICS publishes these jack features (vendor claim):
  - two contact points per pole on all five poles;
  - a non-magnetic hard-alloy underplate under the gold;
  - equal path length from each contact to its solder tail;
  - a detect switch on an independent circuit that opens only after all five poles have made contact.
- NDICS also warns publicly that **counterfeit "Pentaconn"/RC-8141C jacks with out-of-spec dimensions** are on the market. That argues against buying unbranded 4.4 mm jacks from marketplaces for the commercial edition.
- Not known: MPN, MOQ, mating-cycle rating and price (**UNVERIFIED**, no catalog online).

**Catalog distributors.** Digi-Key returned no results for "4.4mm balanced jack" or "pentaconn". FindChips and the JLC API show no Pentaconn listing.

**4.4 mm jacks that are actually listed (JLC/LCSC API, 2026-10-22):**

| MPN | Maker | Mounting | Stock / price | Notes |
|---|---|---|---|---|
| **GT-3321667P-01** ([LCSC C2762984](https://www.lcsc.com/product-detail/C2762984.html)) | G-Switch | **PCB through-hole, right-angle**; 20.5 × 8.3 × 6.5 mm (L × W × H); TRRRS; gold over phosphor bronze; 30 V / 0.5 A | **730 @ $7.30** | Only PCB-mount 4.4 mm jack with real stock found. JLC extended part. Detect pin, mating cycles and JEITA dimensional compliance: **UNVERIFIED** (the datasheet link on LCSC did not render) |
| KH-PJ-44002-12DBAP-A (C42396781) | Shenzhen Kinghelm | PCB right-angle, plug-in; 21 × 5.45 × 5 mm | 0 @ $7.11 | Lowest body (5 mm) but no stock |
| PJ-619 / PJ-619G (C707213 / C707212) | Korean Hroparts | **Wire-solder panel jack**, not PCB | 25 / 54 | Not suitable for SMT/THT assembly |

**Makers named in the brief, not verified.** Kycon, Same Sky/CUI, Switchcraft, Hosiden and Foxconn 4.4 mm PCB jacks are **UNVERIFIED**. None appears at Digi-Key or FindChips under a 4.4 mm description, and no web search was available to find their MPNs. The OEMs of FiiO, Shanling and HiBy players are not published (**UNVERIFIED**).

**Layout guidance** (engineering judgement, to be confirmed against the chosen drawing):

1. Pick the 4.4 mm part first and freeze its footprint. **No pair of 4.4 mm jacks has been shown to share a footprint.** Put the G-Switch footprint on the same board edge, overlapping the Pentaconn footprint, only if the drawings allow it. Otherwise give the kit its own BOM variant on a separate footprint, which breaks "one design".
2. 4.4 mm pole order, tip to sleeve, is L+, L−, R+, R−, GND. Route each ± pair as a tightly coupled pair from the OPA1622 outputs. Return the sleeve (GND) pole to the analog ground at the output stage, not through the shield.
3. Tie the metal shell or shield pegs, if present, to chassis ground through a 0 Ω / 1 nF option.
4. Use the detect switch for plug detection and to mute before the output is connected.
5. Through-hole pegs survive plug side-loads better than SMT-only jacks. A through-hole jack in an otherwise SMT board needs a selective or hand solder step, which JLCPCB and PCBWay both offer.

### 1.2 3.5 mm low-profile jack with detection

| MPN | Description | Stock / price | Source |
|---|---|---|---|
| **Same Sky SJ2-35954D-SMT-TR** | 3.5 mm TRRS, 4 conductors / 6 contacts, **two internal switches**, SMT right-angle, **gold** contacts, 12 V / 1 A | **Mouser 4,528 @ $1.55**; Digi-Key 850 cut tape + ≥1,000 on reel @ $1.55 ($0.807 @ 10k), Active; LCSC C4992270: 71 @ $2.44 | [Digi-Key](https://www.digikey.com/en/products/result?keywords=SJ2-35954D-SMT-TR), [FindChips](https://www.findchips.com/search/SJ2-35954D-SMT-TR) |
| Same Sky SJ2-35894D-SMT-TR (the earlier pick) | TRRS with tip/ring switches, silver | Mouser 436, Newark 71, LCSC C4991838: 10 | [FindChips](https://www.findchips.com/search/SJ2-35894D-SMT-TR) |
| Same Sky SJ-43514-SMT-TR | 3.5 mm 4-conductor SMT, no detect switch (UNVERIFIED) | Mouser 13,517, TME 500 | [FindChips](https://www.findchips.com/search/SJ-43514-SMT-TR) |
| XUNPU PJ-327A (LCSC C49284723) | 3.5 mm TRRS SMD, silver, 6 mm height class | LCSC 3,470 @ $0.22 | JLC API |
| SHOU HAN PJ-327A 5JJ (LCSC C668605) | 3.5 mm SMD | LCSC 12,726 @ $0.11 | JLC API |

**Pick:** SJ2-35954D-SMT-TR. It is the best-stocked part with detect switches, and its gold contacts suit an audio output. The PJ-327A clones are JLC-stocked and cheap, but they have silver/tin contacts and no published cycle rating. Use one only as an emergency kit substitute, after checking its footprint.

---

## 2. Display (faceplate)

### 2.1 Fit constraint: a 4:3 3.5" panel does not fit a 54 mm body

- A 3.5" 4:3 panel's active area is about **71.1 × 53.3 mm** (from the diagonal alone). With bezel and FPC bend, the module is wider than **54 mm** in either orientation.
- That includes the RG353V-V2 panel, whose mainline driver states 70 × 57 mm.
- Inside an 85.6 × 54 mm body, the realistic options are therefore:
  - a **3.5" tall-aspect panel** (2:3, 3:5 or 9:16, about 49 × 73 mm active), or
  - a **≤3.0" 4:3 panel**.
- The maintainers' widened brief (3.0–4.0", IPS or better, touch, power, outdoor readability, stock) is scored against that.

### 2.2 Driver landscape for small panels (mainline master; Debian 7.2 bpo and 7.3 exp)

| Mainline driver | Small-panel compatibles | Debian 7.2 / 7.3 | Path |
|---|---|---|---|
| `panel-sitronix-st7703` | `anbernic,rg353v-panel-v2`, `gameforce,chi-panel` (640×480 3.5"), `powkiddy,rgb30-panel`, `powkiddy,rgb10max3-panel`, `ayaneo,pocket-ds-lower-panel` | **on / on** | New compatible + init table, then upstream |
| `panel-ilitek-ili9488` (**new in v7.3**, absent in v7.2) | `focuslcds,e35gh-i-mw800cb` (3.5" 320×480, 1 lane, 48 × 73 mm) | n/a / **off** | DKMS until Debian enables `DRM_PANEL_ILITEK_ILI9488` |
| `panel-sitronix-st7701` | `anbernic,rg-arc-panel`, `anbernic,rg28xx-panel` (2.8"), `densitron,dmt028vghmcmi-1a`, `winstar,wf40eswaa6mnn0`, `techstar,ts8550b` | off / off | DKMS |
| `panel-ilitek-ili9806e-dsi` | `ortustech,com35h3p70ulc` (3.5" 480×800), `densitron,dmt028vghmcmi-1d` | off / off | DKMS |
| `panel-newvision-nv3051d` | RG353P/M/V v1, RG351V, RK2023 (640×480 3.5") | off / off | DKMS |
| `panel-newvision-nv3052c` | `leadtek,ltk035c5444t`, `fascontek,fs035vg158`, `anbernic,rg35xx-plus-panel` (3.5" 640×480, SPI + DPI) | off / off | DKMS; costs ≈24 DPI pins |
| `panel-jadard-jd9365da-h3` | `waveshare,3.4-dsi-touch-c`, `waveshare,4.0-dsi-touch-c` (round/square, too large for 54 mm) | off / off | DKMS |
| `panel-sitronix-st7789v` | 240×320 and 240×280 only | on / on | Rejected: resolution too low |
| Touch: `goodix` (GT911), `edt-ft5x06` (FT5426, FT6236 and others) | — | **on / on** | Works as is |

**OLED/AMOLED.**

- Digi-Key's small AMOLED MIPI modules (American Bright AB-J240-A800R with RM690B0, AB-J143-A450C with CO5300) all show **0 stock**.
- Mainline has no driver for those DDICs. The Raydium drivers cover only `rm67191`, `rm67200`, `rm68200`, `rm692e5` and `rm69380`.
- **Rejected for now:** no stock and no driver. An AMOLED's power advantage for dark UIs is real, but it cannot be validated against stock today.

**Vendor drivers.**

- [waveshareteam/Waveshare-DSI-LCD](https://github.com/waveshareteam/Waveshare-DSI-LCD) ships prebuilt `.ko` files only, with no license file, for Raspberry Pi kernels 5.10–6.6.51, and has no 3.5" entry. It does not qualify as a validated GPL-2.0 vendor driver.
- Newhaven publishes example code on [GitHub](https://github.com/newhavendisplay). Whether it contains this panel's init table is **UNVERIFIED**.

### 2.3 Purchasable candidates, ranked by fit, then availability, then driver path

| Rank | Module | Panel | Controller / driver path | Touch | Brightness / angle / power | Stock / price |
|---|---|---|---|---|---|---|
| 1 (best fit) | **Focus LCDs E35GH-I-MW800-CB** | 3.5" **320×480** IPS, **1-lane MIPI DSI**; outline **54.46 × 82.94 mm**, active 48.96 × 73.44 mm | **ILI9488**. Exact mainline compatible `focuslcds,e35gh-i-mw800cb` (v7.3), so **zero new kernel code**. Debian off → DKMS build of `panel-ilitek-ili9488.c` for 7.2, plus a config request | **GT911** (Debian on) | **800 nit** (sunlight-readable, vendor claim), IPS; power **UNVERIFIED** | [Digi-Key 9 @ $56.55, Active](https://www.digikey.com/en/products/detail/focus-lcds/E35GH-I-MW800-CB/2632-E35GH-I-MW800-CB-ND); [Focus LCDs direct 9 @ $45.24, "Recommended for New Designs"](https://focuslcds.com/product/e35gh-i-mw800-cb/). Production MOQ by quote |
| 2 (best stock) | **Newhaven NHD-3.5-640480EF-MSXP-CTP** | 3.5" **640×480** IPS, MIPI DSI 1–4 lanes, 40-pin 0.5 mm FPC; **4:3, so it will not fit a 54 mm body** | **FL7703NI** (ST7703 command set). New compatible + init table in `panel-sitronix-st7703` (Debian **on**); DKMS copy until upstream | **FT5426G** (`focaltech,ft5426`, Debian on), separate 6-pin cable | **810 nit typ.**, 85° all sides, 800:1; logic 3.0 V / 38–75 mA; backlight 19.2 V × 40 mA ≈ 0.77 W at full brightness; 30,000 h backlight life | [Digi-Key 189 @ $44.85, Active](https://www.digikey.com/en/products/detail/newhaven-display-intl/NHD-3-5-640480EF-MSXP-CTP/21705285); [Mouser 69 + 59 @ $49.63, TME 9 @ $63](https://www.findchips.com/search/NHD-3.5-640480EF-MSXP-CTP) |
| 3 | Waveshare 3.5inch DSI LCD (H) | 3.5" **480×800** IPS, DSI, 5:3 | Controller **not published (UNVERIFIED)**. It runs on the Pi with no init sequence, so it probably needs only a timings entry (new `panel-simple` DSI entry upstream, or DKMS) | GT911 | 270 nit, 170°, 3.3 V / 180 mA; **no brightness control** | [Waveshare $37.99](https://www.waveshare.com/3.5inch-dsi-lcd-h.htm); stock not shown; no longevity policy |
| 4 | Waveshare 3.5inch DSI LCD (E) | 3.5" 640×480 IPS, 4:3 (does not fit) | Same as (H) | GT911 | 180 nit, 150 mA, no brightness control | [Waveshare $32.99](https://www.waveshare.com/3.5inch-dsi-lcd-e.htm) |
| — | Ortustech COM35H3P70ULC | 3.5" 480×800, mainline `ili9806e-dsi` compatible | DKMS | — | — | **Not found** at FindChips distributors (UNVERIFIED availability) |
| — | Riverdi RVT35 / Focus E35RG / Winstar WF35 RGB parts | 3.5" 320×240 or RGB-parallel | `panel-simple` DPI | some CTP | — | TME 17 @ $34.20 (Riverdi); RS 210 @ $31.68 (Focus E35RG). Lower resolution, and 4:3 does not fit |
| — | RG353V-V2 spare panel | 3.5" 640×480 ST7703 | Mainline + Debian on | none | — | Marketplace spare with no datasheet or lifecycle (**UNVERIFIED**). Prototype or repair use only |

**Custom modules (production).**

- Shenzhen module houses such as Wisecoco, KD/Kingtech and BuyDisplay/East Rising sell 3.5" MIPI modules on ST7701S, ST7703 or ILI9488, with GT911 or FT6336 CTP options, and offer OCA lamination.
- Typical industry figures are an **MOQ of 1–5k with NRE of $1–5k** for a new touch FPC or cover lens. These are **UNVERIFIED** (buydisplay.com returned 403 and no marketplace search was possible).
- Such a house can match an init sequence if it is given the target driver's table. Ask for the panel datasheet and init code as deliverables, not just a sample.

### 2.4 Display trade-offs

- **Fit and resolution.**
  - The ILI9488 module is the only stocked part with an exact mainline match that fits the card's short side. At 320×480 (≈165 ppi) it is coarse but adequate for a DAP UI.
  - The Newhaven part has twice the pixels but forces a ≈66 mm body.
  - The Waveshare (H) fits and has 480×800, but it is dim, has no dimming, and has no documented controller.
- **Battery.**
  - A high-nit backlight is the largest display load. Both the Focus and Newhaven modules need a PWM-dimmable boost LED driver. Run them at ≈150–250 nit indoors and use the full 800 nit only outdoors via the ALS.
  - Waveshare's lack of brightness control rules it out for battery reasons.
- **Lifecycle.**
  - Focus LCDs marks the E35GH as "Recommended for New Designs" and Newhaven is "Active" at Digi-Key.
  - Neither longevity statement was fetched (**UNVERIFIED**).
  - Waveshare publishes no lifecycle policy.

---

## 3. Battery

Fit assumption: the 54 mm outer width leaves about 50–51 mm inside, so a 51–52 mm pack is borderline.

| MPN | Maker | Capacity | T × W × L (mm) | PCM / NTC / connector | Certification | Stock / price |
|---|---|---|---|---|---|---|
| **LP705176JS+PCM+2 WIRES 70MM** | Jauch | 3,000 min / 3,150 typ mAh | 7.2 × 51.0 × 76.0 bare cell; 7.8 × 51.8 × 78.0 with PCM (Digi-Key) | PCM yes / **no NTC** / bare 70 mm wires | Brochure says "UL listed". IEC 62133-2 and UN 38.3 for this MPN: **UNVERIFIED** (ask Jauch) | [Digi-Key 199 @ $21.59 ($13.94 @ 360)](https://www.digikey.com/en/products/result?keywords=LP705176JS); factory lead time 28 weeks |
| **Adafruit 328** | Adafruit (OEM not named) | 2,500 mAh | 7.3 × 50 × 60 (Adafruit); 8.0 × 50 × 65 (Digi-Key) | PCM yes / no NTC / **JST-PH 2-pin** | Adafruit says UN 38.3 documentation is available; IEC 62133-2 not seen | [Digi-Key 1,834 @ $14.95](https://www.digikey.com/en/products/detail/adafruit-industries-llc/328/5054542); [Adafruit](https://www.adafruit.com/product/328) $11.96 @ 100 |
| USE-104060-3K-PCBJST | US Electronics (cell by Shenzhen Hysincere) | 3,000 mAh | 10.0 × 40.5 × 62.0 | PCM (cut-off 4.28 V) / no NTC / JST-PH | No IEC 62133 or UN 38.3 claim in the datasheet | [Digi-Key marketplace 1,249 @ $14.95](https://www.digikey.com/en/products/result?keywords=USE-104060-3K-PCBJST). Needs 10 mm of z-height |
| SparkFun PRT-13855 | SparkFun | 2,000 mAh | 5.6 × 49.2 × 68.8 | PCM / no NTC / JST-PH | MSDS only | [SparkFun $19.41](https://www.sparkfun.com/products/13855) |
| Jauch LP675365JU+PCM | Jauch | 2,800 mAh | 7.5 × **54** × 68 | PCM | — | Digi-Key 693 @ $17.93. **Too wide** |
| Jauch LP685077JU+PCM | Jauch | 3,500 mAh | — | PCM | — | Out of stock; 120 due 2027-03-22 |
| Jauch LP854165J | Jauch | 2,500 mAh | 8.5 × 41.5 × 64.5 | cell | — | Ideal size but not at Digi-Key; quote only |
| JLC/LCSC | — | — | — | — | — | **No LiPo ≥2,000 mAh listed.** The largest is a KAMCY 803450 1,500 mAh (C55805827, 19 pcs) |

- **Grepow, EEMB, PKCELL, LiPol Battery Co., Varta, Renata and Ansmann: UNVERIFIED.** lipolbattery.com returned 403, and the others could not be searched.
- High-voltage (4.4/4.45 V) and silicon-anode cells: **UNVERIFIED**.
- Jauch does sell NTC + Molex variants of its packs: Digi-Key lists `LP503030JU+PCM+2IC+NTC+MOL. 78172-3`. That makes a 10 kΩ NTC + connector variant of the LP705176JS plausible as a factory order, but its MOQ and price are **UNVERIFIED**.

**Design consequences.**

1. Design one battery bay of about **52 × 80 × 8–8.5 mm** with a **JST-PH 2.0 mm 2-pin** socket. All stocked candidates end in JST-PH or in bare wires that can take a PH plug. A connectorised pack also supports EU 2023/1542 user replacement (from Feb 2027).
2. **No stocked pack has an NTC.** Place a 10 kΩ NTC on the board, pressed against the cell and wired to the charger's TS pin, so that any of these packs is safe. Keep "NTC inside the pack" as a requirement for the custom production order only.
3. Get the IEC 62133-2 and UN 38.3 reports from the pack makers before committing.

---

## 4. Audio master clocks (45.1584 MHz and 49.152 MHz)

**Key finding:** NDK's audio-dedicated **NZ2520SDA** is stocked at Digi-Key under its **specification number** `NSC5083x`, not under "NZ2520SDA". That is why the earlier search missed it.

| MPN | Series / type | Phase noise (datasheet) | Stock / price | Notes |
|---|---|---|---|---|
| **NDK NSC5083D-45.158M** | NZ2520SDA, ultra-low phase-noise CMOS XO, 2.5 × 2.0 × 0.9 mm, 3.3 V, ±50 ppm, 15 mA, standby 35 µA | Typical at 3.3 V: −164 dBc/Hz at 1 kHz and −169 dBc/Hz at 100 kHz (22.5792 MHz data). The 45.1584 MHz value is not tabulated | **[Digi-Key 2,801 @ $2.94, Active](https://www.digikey.com/en/products/detail/ndk-america-inc/NSC5083D-45-158M/13982372)**; LCSC C17523715: 0 @ $2.16 | Digi-Key labels the frequency "45.158 MHz". **Confirm 45.1584 MHz on the NDK spec sheet before ordering.** |
| **NDK NSC5083D-49.152M** | same | At 49.152 MHz, 3.3 V: **−158 dBc/Hz at 1 kHz, −172 dBc/Hz at 100 kHz; 43 fs RMS jitter (12 kHz–20 MHz)** | **[Digi-Key 3,404 @ $2.94, Active](https://www.digikey.com/en/products/result?keywords=NZ2520SDA)**; LCSC C17466132: 36 @ $5.76 | Best-documented audio XO that is actually stocked |
| NDK NSC5083A-… | NZ2520SDA at **1.8 V** | Slightly worse close-in noise at 1.8 V (−152 dBc/Hz at 1 kHz for 49.152 MHz) | Not checked | Spec numbers A/B/C/D = 1.8 / 2.5 / 3.0 / 3.3 V ([NDK catalog PDF](https://www.ndk.com/images/products/catalog/c_NZ2520SDA_e.pdf)) |
| NDK NZ2520SDA, DIY channel | same | — | [DIYINHK](https://www.diyinhk.com/shop/audio-kits/128-ndk-nz2520sda-33v-49152mhz-451584mhz-24576mhz-225792mhz-ultra-low-phase-noise-oscillator.html) $8.10, "in stock", limit 5 per frequency | Not an authorized distributor. Only useful for hand-built kits |
| Crystek CCHD-957-25-45.1584 | Audio-grade HCMOS XO, 14 × 9 mm class | — | Mouser 265 @ $26.08 | Large and costly |
| Crystek CCHD-957-25-49.152 | same | — | [Digi-Key 45 @ $34.98](https://www.digikey.com/en/products/detail/crystek-corporation/CCHD-957-25-49-152/2742158) | The earlier report's "not checked" is now resolved |
| Crystek CCHD-575 (45.1584 / 49.152) | 5 × 7.5 mm low-noise XO | — | No stock at any FindChips distributor for these frequencies; LCSC placeholders 0 | Rejected on availability |
| Renesas XLH736045.158400I / XLH736049.152000I | 7050 HCMOS XO | Not checked | Mouser 981 @ $2.16 / 95 @ $2.32; LCSC 6 / 6 | Stocked Western alternative; phase noise **UNVERIFIED** |
| SCTF SX3M45.1584M20F30TNN / SX3M49.152M20F30TNN | 3225 CMOS XO | No phase-noise spec | LCSC 3,616 @ $0.34 / 2,367 @ $0.51 | Low-cost reference for the A/B measurement |
| SiTime / Microchip DSC1001 (MEMS) | MEMS | Worse close-in phase noise | Microchip DSC1001DI2-049.1520: LCSC 37 | Rejected for the DAC master clock |
| Kyocera, Abracon, Epson, KDS | — | — | **UNVERIFIED** (not searched) | — |

**Recommendation (clocks).**

- **NDK NSC5083D-45.158M + NSC5083D-49.152M** on a 2520 footprint. They are the newest audio-dedicated generation (NZ2520SDA supersedes NZ2520SD), stocked in thousands at Digi-Key, about 1/10 the cost of the Crystek, and small enough to sit right at the CS43198 MCLK pins.
- The standby pin lets the unused family clock be **disabled (35 µA)**, which helps battery life.
- Keep a 3225 pad overlap only if the SCTF A/B measurement is still wanted.

---

## 5. Waterproof / IP-rated USB-C receptacle

| MPN | Type | Mounting | IP rating | Stock / price | Notes |
|---|---|---|---|---|---|
| **GCT USB4730-GF-A-KIT** | **USB 2.0** Type-C, 24 positions (16 + 8 dummy), 5 A / 48 V, 20,000 cycles | SMT right-angle with through-hole shell stakes; top-mount, 4.66 mm profile | **IP67** (IP6X/IPX7 test reports; needs the USBTJ-04 gasket, which the "KIT" includes) | **[Digi-Key 15,083 @ $1.86, Active](https://www.digikey.com/en/products/detail/gct/USB4730-GF-A-KIT/21838842)** | Best stocked IP67 USB 2 + PD part. Not mid-mount ([GCT page](https://gct.co/connector/usb4730)) |
| GCT USB4730-GF-A | same, without gasket | same | IP67 with gasket | [Digi-Key 4,370 @ $1.76](https://www.digikey.com/en/products/detail/gct/USB4730-GF-A/21838841) | Order the gasket separately |
| **Same Sky UJ31-CH-3-MSMT-TR-67** | **USB 3.2 Gen 2** Type-C, 24 positions, 10,000 cycles | **Mid-mount**, horizontal | **IP67** | **[Digi-Key 13,661 @ $3.82 ($2.40 @ 700), Active](https://www.digikey.com/en/products/result?keywords=UJ31-CH-3-MSMT-TR-67)** | Only stocked IP67 **mid-mount** part found. Carries USB 2 + CC as well, so it serves USB 2 + PD too |
| Same Sky UJ31-CH-G-SMT-TR-67 | USB 3.2 Gen 2 | Horizontal SMT | IP67 | Digi-Key 14,877 @ $3.75 | |
| Amphenol LTW UC-00PFFH-QF7001 | USB 3.2 Gen 2, 24 positions | Mid-mount | IP67 | Digi-Key 2,936 @ $5.90 | Second source for the mid-mount USB 3 case |
| GCT USB4715-GF-A-KIT | **Power only** (6 pins) | Mid-mount | IP67 | Digi-Key 5,936 @ $1.81 | Rejected: no data lines |
| GCT USB4725-03-C-KIT | USB 3.2 Gen 2 | Vertical | IP67 | Digi-Key 3,874 @ $2.41 | Wrong orientation |
| JAE DX07 / Amphenol 124 waterproof variants | — | — | — | **UNVERIFIED** (not found by these searches) | |

**Recommendation (USB-C).**

- If the board edge allows a top-mount part, use **GCT USB4730-GF-A-KIT** (USB 2.0 + PD, IP67, cheapest, best stock).
- If the mechanics need **mid-mount**, or the USB 3 lane may ever reach the port, use **Same Sky UJ31-CH-3-MSMT-TR-67**, with **Amphenol LTW UC-00PFFH-QF7001** as the mid-mount second source. Their footprints differ.
- Either way, a receptacle's IP67 rating only holds with the specified gasket compressed against the housing. The enclosure design owns the final IP rating.

---

## 6. Microphones (PDM)

Stock from [FindChips](https://www.findchips.com/search/IM73D122V01XTMA1) and the JLC API on 2026-10-22, except the Digi-Key figures from 2026-10-21.

| MPN | SNR / AOP | Footprint | Mouser | Newark / TME | LCSC | Digi-Key | Notes |
|---|---|---|---|---|---|---|---|
| **Infineon IM73D122V01XTMA1** | 73 dB / 122 dBSPL | LLGA-5, 4 × 3 × 1.2 mm | **15,038 @ $2.79** | **Newark 20,502 @ $1.90** | C5563886: 5,352 @ $2.88 | 36,572 @ $2.72 | **Not an availability risk.** Keep |
| **Infineon IM72D128V01XTMA1** | 72 dB / 128 dBSPL | Same 4 × 3 LLGA-5 (pin-for-pin, UNVERIFIED against both drawings) | **48,099 @ $2.88** | Newark 6,455 @ $1.84 | C5119248: 0 | — | Best second source: same family, same footprint class, higher AOP |
| Infineon IM69D130V01XTSA1 | 69 dB | 4 × 3 | 28,079 @ $2.66 | — | C42464166: 0 | 66,648 | Older generation |
| Knowles/Syntiant SPH0641LU4H-1 | 64.3 dB | 3.5 × 2.65 | 3,198 @ $3.22 (as -1-8) | — | C2879853: 587 @ $2.08 | 2,979 | Lower SNR, different footprint |
| TDK MMICT5838-00-012 (T5838) | 68 dB, low power, acoustic activity detect | 3.5 × 2.65 | 0 | Newark 8; **TME 4,418 @ $1.63** | C7230692: 1,381 @ $3.36 | 182 | Good always-on ambient mic; thin at Western distributors |
| ST MP23DB01HPTR | 64 dB | RHLGA-5, 3.5 × 2.65 | 0 (FindChips) | Newark 771 @ $3.97; TME 94 | C3171836: 67 @ $1.72 | — | Weakest stock of the four |

**Recommendation (mics).** Keep **IM73D122** (the best SNR, stocked at four authorized channels). Name **IM72D128** as the same-family second source on the same footprint class, once both drawings are checked pin-for-pin. Drop the MP23DB01HP. Both go through the Debian-enabled `rockchip_pdm` + `dmic` path, so no driver work is needed.

---

## 7. LPDDR4X 4 GB and eMMC 32 GB

### 7.1 LPDDR4X 4 GB (32 Gb, x32, 200-ball)

| MPN | Source | Stock / price | Notes |
|---|---|---|---|
| **Samsung K4UBE3D4AB-MGCL** | [LCSC C5827966](https://www.lcsc.com/product-detail/C5827966.html) | **236 @ $82.09** | Best available |
| SK hynix H9HCNNNCPMMLXR-NEE | [LCSC C19192462](https://www.lcsc.com/product-detail/C19192462.html) | 47 @ $79.85 | Second source, low quantity |
| Micron MT53E1G32D2FW-046 WT:A / WT:C | Digi-Key | 0 in stock (list $19.00 for WT:A; $224.32 for WT:C) | Lead-time order only. Brokers Vyrian (5,281) and Win Source (3,830 @ $100) are **not** authorized |
| Micron …-046 AUT:B | LCSC C5128897 | 3 @ $367 | Automotive; not worth it |
| CXMT CXDB5CCAM-MK / -ML | LCSC C39047067 / C20598559 | 0 / 0 | Nothing to buy |
| Nanya NT6AN1024F32AV-J2 | LCSC C53337622 | 0 @ $63.64 | — |
| Longsys FORESEE LPDDR4X | LCSC | Not listed | — |

**Traps.**

- **SK hynix H9HCNNNBKUMLXR-NEE** (LCSC 1,400 @ $65.61) is only **16 Gb (2 GB)**.
- **Samsung K4FBE3D4HM-MGCJ** and **Micron MT53D1024M32D4DT-046** are plain **LPDDR4** (1.1 V VDDQ). They are not drop-in replacements on an LPDDR4X (0.6 V VDDQ) layout.

### 7.2 eMMC 5.1, 32 GB, 153-ball

| MPN | Source | Stock / price | Notes |
|---|---|---|---|
| **Samsung KLMBG2JETD-B041** | [LCSC C5821038](https://www.lcsc.com/product-detail/C5821038.html) / [C2803245](https://www.lcsc.com/product-detail/C2803245.html) | **270 @ $40.33** / 490 @ $45.04 | Best available |
| **Longsys FORESEE FEMDNN032G-C9A55** | LCSC C42395192 | 148 @ $79.36 | Second source |
| FORESEE FEMDRW032G-88A19 (−40 to 85 °C) | LCSC C719926 | 136 @ $66.67 | Industrial-temperature option |
| MK MKEML032GN1E-C / MKEMF032GT1E-C | LCSC C54952141 / C22374386 | 95 @ $41.75 / 204 @ $51.60 | No Rockchip validation evidence |
| Kioxia THGAMVG8T13BAIL | LCSC C19185995 | 0 | Broker only |
| Micron MTFC32GAPALBH-IT | LCSC 0; all MTFC32GAP variants **Obsolete/Discontinued** at Digi-Key | — | Avoid in a new design |
| SanDisk SDINBDG4-32G-XI1, Biwin, YMTC YMEC | LCSC | 0 / not listed | — |

### 7.3 rkbin compatibility

- [`rockchip-linux/rkbin`](https://github.com/rockchip-linux/rkbin/tree/master/bin/rk35) ships `rk3566_ddr_1056MHz_v1.26.bin`.
- The [RK3566 release notes](https://github.com/rockchip-linux/rkbin/blob/master/doc/release/RK3566_EN.md) record these changes:
  - byte-mode LPDDR4/4X support (v1.19 Ultra);
  - Vref training "to improve compatibility" (v1.20);
  - a fix for LP4X low-frequency stability, plus printing the DRAM maker ID at boot (v1.22);
  - a fix for LP4/4X CA-training timeouts (v1.24);
  - single-channel LP4/4X support and a "tdqs2dq DRAM compatibility" fix (v1.26, 2026-05).
- **Use v1.26 or newer.**
- No rkbin note blocks CXMT or Micron by name.
- **Rockchip's DDR/eMMC support list was not found (UNVERIFIED).** Ask the Rockchip agent or a reseller (Firefly, Radxa) for `Rockchip_Support_List_DDR_Ver2.xx`.
- The Radxa ZERO 3W v1.12 schematic labels its eMMC **Samsung KLM8G1GEAC-B031**, from the same KLM family as the pick.

**Market.** TrendForce (2026-09-30) projects conventional DRAM contract prices **+10–15 % QoQ in 4Q26**. Buy early.

**Recommendation (memory).**

- **K4UBE3D4AB-MGCL + KLMBG2JETD-B041** from LCSC. Put the SK hynix and FORESEE parts on the BOM as alternates; their footprints are compatible.
- About 230 kits exhaust the current LPDDR4X stock. Beyond that, the commercial edition needs a franchise lead-time order (Micron through Digi-Key/Mouser) or a Samsung/SK hynix agent such as WPG.
- Do not buy broker stock.

---

## 8. Charger with reverse (OTG) boost

### 8.1 Driver map (mainline master, v7.2 / v7.3 tags; Debian 7.2 bpo and 7.3 exp)

| Part | Mainline driver | First in | OTG/boost in driver | Debian 7.2 / 7.3 |
|---|---|---|---|---|
| **TI BQ25895** (also bq25890/2/6) | `bq25890_charger.c` | long-standing | yes (`ti,boost-voltage`, `ti,boost-max-current`) | **on / on** |
| TI BQ25792 | `mfd/bq257xx.c` + `bq257xx_charger.c` + regulator | 7.2 | yes (regulator) | off / off |
| TI **BQ25798** | **Not listed.** `bq257xx` matches only `ti,bq25703a` and `ti,bq25792` | — | — | — |
| TI BQ25630 | `bq25630_charger.c` (Axis, 2026) | **7.3** | **No regulator in the driver** (the OTG registers are only defined) | off (7.3) |
| SGMicro SGM41542 | `sgm41542_charger.c` | **7.3** | yes (`otg-vbus` regulator) | off (7.3) |
| Richtek RT9471 | `rt9471.c` | long-standing | yes (`usb-otg-vbus-regulator`) | off / off |
| Richtek RT9467 | `rt9467-charger.c` | long-standing | yes | off / off |
| TI BQ24296/7 | `bq24190_charger.c` | long-standing | yes | off / off |
| TI BQ25620/22 | not in `bq256xx_charger.c` (which lists bq25600/1/11d/18/19) | — | — | — |

### 8.2 Stock (JLC API + FindChips + TI, 2026-10-22)

| Part | LCSC | Mouser | Others | Key specs |
|---|---|---|---|---|
| **BQ25895RTWR** | [C80200](https://www.lcsc.com/product-detail/C80200.html): **5,954 @ $2.13** | **3,608 @ $3.36** (+79 second listing) | Digi-Key 0 (Active, 2026-10-21); TME 0 @ $3.34; Win Source (broker) 55,555 | 3.9–14 V input, 5 A charge, **OTG 4.5–5.5 V up to 3.1 A**; TI status ACTIVE ([TI](https://www.ti.com/product/BQ25895)) |
| BQ25890RTWR | C130451: 6,921 @ $2.23 | 493 @ $3.52 | — | Same driver, same footprint |
| **BQ25798RQMR** | [C2876593](https://www.lcsc.com/product-detail/C2876593.html): **5,148 @ $2.82** | **9,488 @ $5.27** (+8,630) | Maritex 6,084 @ $4.09 | 1–4S buck-boost, 3.6–24 V, 5 A, **OTG 2.8–22 V up to 3.32 A**, MPPT, backup mode, QFN-29 4×4; ACTIVE ([TI](https://www.ti.com/product/BQ25798)) |
| BQ25792RQMR | C2862876: 7,582 @ $2.10 | not in stock | Maritex 5,093 @ $3.01 | Same pinout class as the BQ25798 |
| RT9471DGQW(2) | C17442001: 1,457 @ $1.05 | RT9471GQW(2): 158 @ $2.56 | — | 3 A, 13.5 V |
| SGM41542YTQF24G/TR | C5153796: **0** | — | — | Rejected: no stock |
| BQ25630YBGR | C53283867: **0**; DSBGA | EVM only | — | Rejected: no stock, no OTG in the driver |

### 8.3 Recommendation (charger)

- **v1: keep BQ25895.** It is still the only Debian-enabled charger with OTG boost and multi-channel stock (LCSC 5,954, Mouser 3,608). Its 3.1 A OTG at 5 V covers a light powerbank-HAT role.
- **Newer generation for the powerbank HAT path: BQ25798**, not the BQ25792.
  - Mouser has 9,488 BQ25798 against no BQ25792.
  - It adds MPPT and backup-mode switchover, and has the same 2.8–22 V / 3.32 A bidirectional OTG.
  - **Driver cost:** a `ti,bq25798` compatible must be added to `bq257xx`. Register compatibility with the BQ25792 is **UNVERIFIED**; check the device-ID and register map in the datasheets.
  - Ship it as DKMS, then upstream it. Debian also needs `MFD_BQ257XX`, `CHARGER_BQ257XX` and `REGULATOR_BQ257XX` (already in the component-selection §10 request).
- No vendor-published Linux driver was evaluated for these chargers (**not checked**). The mainline drivers already cover them.
- **Rejected:** SGM41542 and BQ25630 (no stock, 7.3-only, BQ25630 has no OTG control), RT9471 (Debian off and thin Western stock, with no advantage over the BQ25895).

---

## 9. Recommended picks

| Item | Recommendation | Second source / kit path |
|---|---|---|
| 4.4 mm jack | **Recommendation: genuine Pentaconn via NDICS Hong Kong/Shenzhen** (quote MPN, MOQ, drawing now) | **G-Switch GT-3321667P-01** (LCSC 730) on an overlapping footprint if the drawings allow; otherwise a kit BOM variant |
| 3.5 mm jack | **Recommendation: Same Sky SJ2-35954D-SMT-TR** | SJ2-35894D-SMT-TR (same family); PJ-327A clones as an emergency kit part |
| Display | **Recommendation: Focus LCDs E35GH-I-MW800-CB** (fits the card width, exact mainline compatible, 800 nit, GT911). Before committing, order from Digi-Key + Focus direct and get a production quote, because stock is thin | **Newhaven NHD-3.5-640480EF-MSXP-CTP** (best stock, 640×480, ST7703-class), if the body can grow to ≈66 mm. Production: a custom ILI9488/ST7703 module from a Shenzhen house with OCA-laminated GT911 |
| Battery | **Recommendation: Jauch LP705176JS+PCM** (3,000 mAh) ordered as an NTC + JST-PH variant with IEC 62133-2 / UN 38.3 reports | **Adafruit 328** (2,500 mAh, Digi-Key 1,834) for the second source and the DIY kit; board-side NTC for both |
| MCLK | **Recommendation: NDK NSC5083D-45.158M + NSC5083D-49.152M** (NZ2520SDA) | Crystek CCHD-957 (Mouser/Digi-Key) for reference measurements; SCTF SX3M as the low-cost A/B part |
| IP-rated USB-C | **Recommendation: GCT USB4730-GF-A-KIT** (USB 2 + PD, IP67) | **Same Sky UJ31-CH-3-MSMT-TR-67** if mid-mount or USB 3 is required; Amphenol LTW UC-00PFFH-QF7001 as its mid-mount second source |
| Microphones | **Recommendation: Infineon IM73D122** (no availability problem) | **Infineon IM72D128** (same footprint class); TDK T5838 for an always-on ambient mic |
| LPDDR4X / eMMC | **Recommendation: Samsung K4UBE3D4AB-MGCL + KLMBG2JETD-B041** (LCSC) | SK hynix H9HCNNNCPMMLXR-NEE; FORESEE FEMDNN032G-C9A55; rkbin v1.26+ |
| Charger | **Recommendation: TI BQ25895** for v1 | **TI BQ25798** as the newer powerbank-HAT upgrade (new `bq257xx` compatible + DKMS) |

---

## 10. Remaining risks

1. **4.4 mm jack is still single-source in practice.** Neither the Pentaconn MPN, MOQ nor drawing is public. The only stocked alternative (G-Switch, 730 at LCSC) has an unverified datasheet, detect pin and cycle rating. Counterfeit RC-8141C jacks are circulating (NDICS warning). *Mitigation:* contact NDICS Hong Kong/Shenzhen this month; mechanically sample the G-Switch part; keep the 3.5 mm output.
2. **Display availability is thin for the best-fitting part.** The Focus E35GH has 9 + 9 units, and its driver is 7.3-only and Debian-off. The well-stocked Newhaven part does not fit a 54 mm body. *Mitigation:* decide the body height now; buy evaluation units of both; request Focus production lead time and a longevity statement; start the DKMS package for `panel-ilitek-ili9488` and add `DRM_PANEL_ILITEK_ILI9488` to the Debian config request.
3. **No battery pack combines stock, an NTC, a connector and a downloadable IEC 62133-2 report.** *Mitigation:* a board-side NTC; cert reports from Jauch/Adafruit; quotes from Grepow/EEMB once search is available.
4. **Memory.** About 236 LPDDR4X and 270–490 eMMC at LCSC cover a few hundred kits only, at rising prices (+10–15 % QoQ forecast). The Rockchip AVL is not verified. *Mitigation:* agent quotes (Samsung/SK hynix/WPG), buffer stock, validation of two DRAM parts with rkbin v1.26.
5. **BQ25798 driver gap.** It is not yet a mainline compatible, and register compatibility with the BQ25792 is unverified. *Mitigation:* stay on BQ25895 for v1; prototype the BQ25798 on the HAT.
6. **NDK frequency labelling.** Digi-Key shows "45.158 MHz". Confirm 45.1584 MHz on the NDK spec sheet or with the distributor before ordering.
7. **IP67 depends on the enclosure.** The receptacle ratings assume the gasket and the housing design.
8. **Coverage gaps from this session.** No marketplace (Alibaba/AliExpress/Taobao) or broad web search was possible. Kycon, Hosiden, Foxconn, Grepow, EEMB, Kyocera, Abracon and Epson were not checked, and PCBWay was not checked. All stock is a 2026-10-22 snapshot.

---

## Sources

- Prior report: [`2026-10-component-selection.md`](2026-10-component-selection.md).
- Kernel:
  - [torvalds/linux](https://github.com/torvalds/linux) master and tags v7.2/v7.3;
  - display drivers `drivers/gpu/drm/panel/panel-{sitronix-st7703,ilitek-ili9488,sitronix-st7701,ilitek-ili9806e-dsi,newvision-nv3051d,newvision-nv3052c,jadard-jd9365da-h3,sitronix-st7789v}.c`;
  - charger drivers `drivers/power/supply/{bq25890_charger,bq257xx_charger,bq25630_charger,sgm41542_charger,bq256xx_charger,rt9471,rt9467-charger,bq24190_charger}.c` and `drivers/mfd/bq257xx.c`.
- Debian: `linux-config-7.2_7.2.9-1~bpo13+1_arm64.deb` and `linux-config-7.3_7.3~rc7-1~exp1_arm64.deb` from [deb.debian.org pool](http://deb.debian.org/debian/pool/main/l/linux/).
- Distributors:
  - Digi-Key product and search pages, linked inline;
  - [FindChips](https://www.findchips.com/) for Mouser, Newark, TME and brokers;
  - JLCPCB parts API / [LCSC](https://www.lcsc.com/) product pages.
- Makers:
  - [NDICS / Pentaconn](https://www.ndics.com/brands/pentaconn/), [Pentaconn Online Shop](https://pentaconn.shop/);
  - [NDK NZ2520SDA](https://www.ndk.com/en/products/lineup/crystal-oscillator/NZ2520SDA.html) and [catalog PDF](https://www.ndk.com/images/products/catalog/c_NZ2520SDA_e.pdf);
  - [TI BQ25895](https://www.ti.com/product/BQ25895), [TI BQ25798](https://www.ti.com/product/BQ25798);
  - [GCT USB4730](https://gct.co/connector/usb4730);
  - [Focus LCDs E35GH-I-MW800-CB](https://focuslcds.com/product/e35gh-i-mw800-cb/);
  - [Waveshare 3.5inch DSI LCD (H)](https://www.waveshare.com/3.5inch-dsi-lcd-h.htm);
  - [Adafruit 328](https://www.adafruit.com/product/328), [SparkFun PRT-13855](https://www.sparkfun.com/products/13855);
  - [Jauch LiPo catalogue (via Digi-Key)](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5883/LP504783J.pdf);
  - [rockchip-linux/rkbin](https://github.com/rockchip-linux/rkbin).
- Market: [TrendForce press center](https://www.trendforce.com/presscenter/news?page=2) (2026-09-30 DRAM outlook).
