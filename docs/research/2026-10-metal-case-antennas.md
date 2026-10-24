# Antennas in an anodised-aluminium T1 (2026-10)

- **Date:** 2026-10-24
- **Requirement:** BRD-061 (should, confirmed by the maintainers on 2026-10-24). Recorded against [ADR 0018](../adr/0018-antennas-and-certification-route.md) in its note of 2026-10-24.
- **Question:** which antenna strategies keep Wi-Fi 2.4 / 5 GHz and Bluetooth working when the case core is anodised aluminium (case requirement CASE-022, a later material option), what each strategy needs from the board, and what each one means for certification under the regional-variant strategy of [RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md) §4.
- **Maintainers' constraints (2026-10-24):**
  1. Every radiator, feed and tuning part lives in the main body (board and case core), **never in the faceplate**: the faceplate is a separate, interchangeable module, and any faceplate must work with any radio configuration.
  2. The preferred antenna zone is the core's frame (top wall or side walls) and the board's own edge. The **back cover is a last resort**: HATs mount on the back and a HAT case replaces the basic back cover (CASE-006), so a HAT, possibly metal, would cover or detune an antenna there. HATs keep the antenna keep-out.
- **Inputs:** [ADR 0018](../adr/0018-antennas-and-certification-route.md) and its study [antennas and RF exposure](2026-10-antennas-and-rf-exposure.md) (cited "AR §n"); [LBES5PL2EL-923](https://github.com/opendap-project/parts-lib/blob/main/Murata/LBES5PL2EL-923.md) with Murata CER-0248 Rev. 6.0 and E2B-09-1413 Rev. 9.0 (hashes in `parts-lib/manifest.toml`; both re-read for this note); [PCB design constraints](../specs/pcb-design-constraints.md) PCB-R-01 to R-07; case requirements CASE-006, CASE-020 to CASE-022, CASE-025, CASE-028 and case ADR 0001 (core, basic back cover, HAT case), read only.
- **Scope:** the electronics only. The case geometry (where cuts, caps or contact spots go, wall thickness) belongs to the case repository; this note states what the board must hold and what the case would have to provide (§7).
- **Conventions:** **UNVERIFIED** means no primary source was read in this session. "(vendor claim)" means the only source is the maker's own text. "Arithmetic" marks a value computed here.

## 0. Summary

1. **A closed aluminium core silences the antenna of ADR 0018.** The Molex 146153-0050 sits on the inside of the top wall; a metal top wall puts a conductor between it and the user. Anodising does not help: the anodic layer is an insulating oxide of 2–25 µm on a metal whose skin depth at 2.45 GHz is about 1.7 µm (§1).
2. **Two strategies fit the T1 and the maintainers' constraints:**
   - **S1, non-metallic top end cap.** The top wall (and a strip of the sides and back around it) is polymer, glass or ceramic, the rest of the core aluminium. The 146153-0050 and the board stay as they are; only the matching is retuned. Same listed antenna, same regional routes as ADR 0018. This is the lowest-risk path and the **preferred** one.
   - **S2, the frame is the antenna.** A split band or a dielectric-filled slot in the top wall or the upper side walls, fed from the board through a spring contact and grounded at defined points. The case becomes the antenna; the board feeds it through a second branch with its own matching and ESD positions. A new antenna type for Murata's certification: a permissive change in every region (§5).
3. **Excluded:** antenna in the faceplate (maintainers' constraint 1); antenna in or behind the back cover except as a flagged last resort (constraint 2); external or on-metal antennas mounted outside the body (not on Murata's lists, and against a closed handheld body); Murata's trace antenna (20 mm clearance, AR §1.2).
4. **What the board now holds (PCB-R-08 to PCB-R-13):** the main-body rule; a case-antenna feed pad on the ANT0 path selected against the U.FL by assembly variant, without a stub; a pi matching network, a DC-block, a shunt-inductor position and a ≤ 0.2 pF ESD position at that pad; case-ground contact pads at the top corners and upper side edges with their own ESD return; the variant field that ties the fitted antenna path to its calibration and TX-power table. The polymer production variant leaves all of it unpopulated.
5. **Certification:** S1 keeps ADR 0018's routes (listed antenna, Class I documentation of the retuned match). S2 is a new antenna type: FCC Class II permissive change through Murata, ISED permissive change through Murata (class **UNVERIFIED**), Japan only if Murata adds the antenna to certification 001-P02018, EU radiated tests and SAR on the metal variant. Each metal-case regional variant is verified and certified on its own (RFC 0011 rule 9).

## 1. What anodised aluminium does to RF

| Quantity | Value | Source |
|---|---|---|
| Anodic layer (MIL-A-8625 Type II, sulfuric) | 0.0001–0.001 in, about 2.5–25 µm, aluminium oxide, electrically insulating | MIL-A-8625 Type II as quoted by finishers (secondary; the specification text was not retrieved, **UNVERIFIED**) |
| Skin depth of aluminium at 2.45 GHz | ≈ 1.7 µm (arithmetic: δ = √(ρ / (π f µ0)), ρ = 2.65 × 10⁻⁸ Ω·m) | Arithmetic; resistivity textbook value |
| Skin depth at 5.5 GHz | ≈ 1.1 µm (arithmetic) | Arithmetic |
| Case wall | 1.6 mm (assumption carried from the battery selection §2.3, **UNVERIFIED** until the case sets it) | AR §3.1 |

- A 1.6 mm aluminium wall is about a thousand skin depths: a closed metal box passes nothing at these frequencies. The oxide is a thin dielectric on top of the conductor; it changes contact resistance (contacts need un-anodised spots), not RF transparency.
- "An antenna cannot radiate through metal": at least one face of the enclosure near the antenna must be free of metal (Antenova, *4 ways to increase wireless antenna performance in metal devices*, vendor guidance). Antenova lists four routes: a window, a hybrid enclosure that uses the metal as antenna, an external antenna, an on-metal multilayer antenna outside the enclosure.
- A metal body close to an antenna also detunes it. A 2.45 GHz printed IFA near a metal plate needs a minimum "clearance distance" for efficiency and bandwidth, and a reconfigurable matching network reduced that distance by 40 % (Casado et al., *2.45 GHz printed IFA on metallic environments: clearance distance and retuning considerations*, EuCAP 2012, abstract). This is why the board keeps matching positions at every antenna feed, not only the U.FL.
- A floating metal part near an antenna resonates and detunes it unpredictably, and a metal case touched by the user takes ESD. The metal core is therefore bonded to board ground at defined points (the frame-antenna patents of §3 ground the frame at defined points and put an ESD element at the feed; for the T1 **UNVERIFIED** until measured).

## 2. The body and the zones

| Zone | Allowed | Reason |
|---|---|---|
| Top wall of the core (inner face about 56.3 × 14.2 mm, AR §3.1) | **Preferred** | ADR 0018's antenna position; farthest from the battery pocket and the HAT |
| Upper side walls of the core (top band, left and right) | Preferred | Same frame; a split band or slot can turn the top corners |
| Board's own top edge | Preferred (feeds, ground contacts, a board-edge antenna if one is ever used) | The board is part of the main body |
| Back cover | **Last resort only**, flagged | A HAT case replaces the basic back cover (CASE-006); a HAT, possibly metal, covers or detunes an antenna there |
| Faceplate | **Never** | Separate, interchangeable module; any faceplate must work with any radio configuration |

## 3. Strategies

### S1. Non-metallic top end cap (window) with the listed antenna

- **What:** the core is aluminium except the top end: the top wall, and the strips of the side walls and back next to it, are a non-metallic cap (polymer, glass or ceramic) bonded or screwed to the aluminium. The Molex 146153-0050 stays on the inside of that cap, as in ADR 0018.
- **Practice:** this is Antenova's "window" route above: a gap, slit or window in the enclosure next to the antenna, which Antenova notes must be much larger than engineers usually expect (no figure given). Metal-bodied phones with non-metallic end caps follow it (**UNVERIFIED**: no primary teardown read in this session).
- **Size of the non-metal region (arithmetic, with ADR 0018's provisional 5 mm keep-out):** the radiator is 34.9 × 9.0 mm; with 5 mm on every side the metal-free region is 44.9 × 19.0 mm. The inner face of the top wall is 14.2 mm tall and the 146153 leaves 2.6 mm above and below (AR §3.2), so the keep-out cannot be met within the top wall alone: the non-metal cap must take the whole top wall and wrap onto the back. A back-cover surface 2.6 mm from the radiator's edge is within 5 mm of it over √(5² − 2.6²) ≈ 4.3 mm inward from the top wall's inner face, so the back strip of the cap reaches ≈ 1.6 + 4.3 ≈ 5.9 mm from the outer top face at a 1.6 mm wall (arithmetic). On the other long side the radiator faces the board's top edge, whose copper keep-out is the board's own (PCB-R-07). The ≥ 10 mm free at each end of the 146153 (AR §3.2) is met inside the top wall if the cap covers its full width.
- **Board needs:** nothing new. The ANT0 U.FL path of PCB-R-02 and R-03 with Murata's matching positions retunes the antenna in the new surroundings.
- **Certification:** the antenna is the listed 146153; ADR 0018's routes stand. The retuned match is documented as a Class I item (same type, gain ≤ 3.2 / 4.25 dBi, spurious ≤ 3 dB worse; CER-0248 §2.1.3.12). SAR is measured on the metal variant, because the metal body changes the field near the user.
- **Risks:** the cap's look and joint belong to the case design; the aluminium side walls still end within millimetres of the radiator ends if the cap is narrow, so the cap width is set by measurement on the prototype.

### S2. The frame is the antenna (split band or slot)

- **What:** the aluminium frame itself radiates.
  - **Split band (frame IFA or loop):** one or two cuts in the top or upper side walls separate a frame segment; the board feeds it at one point and grounds it at others. A split on the metal frame with ground points on both sides of it forms two resonance loops (frame-antenna patents returned by a USPTO search, read only in summary, **UNVERIFIED**).
  - **Slot:** a dielectric-filled slot cut in the metal wall, fed across its width. Apple's *Electronic device with housing slots for antennas* (US 10,965,008 B2, 2021-03-30) describes dielectric-filled slots in a metal housing, widths from 0.1–0.7 mm to under 5 mm, fed by terminals on the housing on both sides of the slot, with capacitors and inductors bridging the slot, and lists 2.4 GHz Bluetooth and 2.4 / 5 GHz Wi-Fi among the bands. Apple's earlier *Microslot antennas for electronic devices* (US 8,373,610 B2) forms dielectric-filled microslots in a conductive housing that acts as ground plane.
- **Lengths (arithmetic):** free-space wavelength 122.4 mm at 2.45 GHz and 54.5 mm at 5.5 GHz. A closed half-wave slot at 2.45 GHz is 61.2 mm, longer than the 59.5 mm top wall: it has to turn a corner into a side wall, or be loaded by its dielectric fill (with εr ≈ 3 for a PC fill, **UNVERIFIED**, the factor √((εr + 1) / 2) ≈ 1.41 gives ≈ 43 mm). An open-ended quarter-wave slot at 2.45 GHz, ≈ 30.6 mm, fits the top wall. The 5 GHz band needs a second resonance or a higher mode, set by the antenna design (**UNVERIFIED** until designed and measured).
- **Published result for a metal-rimmed wearable:** a dual-band metal-bezel smartwatch antenna (metal ring, a capacitor, the system ground with its feeding network) measured −5 dB efficiency in the Wi-Fi / Bluetooth 2.4 GHz band on the wrist (*Design of dual-band antenna for metal-bezel smartwatches with circular polarization in GPS band and low wrist effect*, IEEE Trans. Antennas Propag., vol. 71, no. 6, pp. 4651–4662, June 2023; abstract read). This sets the expectation that a metal frame can carry 2.4 GHz with moderate efficiency, not a T1 figure.
- **Board needs (§4):** a feed contact from the module's ANT0 path to the frame (spring contact on a board pad), a matching network at that pad with enough range to retune the frame on the prototype, a DC-block and a DC path to ground for ESD, a low-capacitance ESD diode, and several ground contacts to the frame at the top corners and side edges.
- **Certification (§5):** a new antenna type; a permissive change in every region, and the gain must be measured and kept at or below Murata's listed gain so the certified TX-power tables still hold.
- **Risks:** custom design and tooling; hand effect (the user holds the frame); the cut positions are case design and interact with the industrial design. It is the strategy with the most work and the most reward if the maintainers want a fully metal top.

### Other strategies considered

| Strategy | Verdict | Reason |
|---|---|---|
| LDS antenna on a polymer carrier (laser-activated plastic, electroless plating) | Variant of S1 | Only works behind a non-metal region; it is a custom antenna (not listed), so it costs S2's certification without S2's metal top. Kept as an option if the 146153 does not fit a narrow cap. Process: LPKF laser direct structuring (Apple patent US 9,954,273, *antennas with laser-activated plastic and foam carriers*); traces down to 0.2 mm (Taoglas, vendor claim) |
| Board-edge chip antenna or antenna booster (for example Ignion's mXTEND range) | Variant of S1 | Radiates through the board edge and needs a non-metal region too; not on Murata's lists; Ignion's application notes were not retrieved (**UNVERIFIED**). Fed from the same case-antenna branch as S2 if ever used |
| On-metal or external antenna outside the enclosure (Antenova REFLECTOR, Molex on-metal Wi-Fi antennas, vendor claims) | Out | Outside a closed handheld body; not on Murata's lists |
| Murata trace antenna | Out | 40 × 40 mm board and 20 mm clearance (AR §1.2) |
| Antenna in the faceplate | **Out** | Maintainers' constraint 1: the faceplate is a separate, interchangeable module |
| Antenna in or behind the back cover (window in the back cover) | **Last resort** | Maintainers' constraint 2: a HAT case replaces the back cover (CASE-006); a HAT, possibly metal, covers or detunes it. Used only if S1 and S2 both fail, and then with the HAT keep-out extended over it |

## 4. What the board holds

Both strategies use the module's ANT0 (pin 15) in Murata's shared configuration (ADR 0018 item 2); the dedicated ANT1 option of PCB-R-02 stays as it is.

1. **Feed selection without a stub.** At the end of Murata's copied line (PCB-R-03), the ANT0 path continues either to the U.FL (polymer case, S1) or to the case-antenna branch (S2). The selection is a single series position whose footprint shares one pad between the two directions (or two series positions on a shared pad), so the unused direction is an open at the pad, not a stub of trace. Murata's copied line from pin 15 to that point stays unchanged. Whether Murata accepts the shared junction as "a copy of its U.FL layout" for the Class I documentation of S1 is **UNVERIFIED** (outward question, §8).
2. **Case-antenna branch:** a 50 Ω line from the junction to a gold (ENIG) spring-contact pad at the board's top edge, near the top wall; along it, in this order from the junction: a series DC-block capacitor position; a pi matching network of three 0603 positions (series element and two shunts to ground), the same size Murata uses (E2B-09-1413 Figures 9–10); at the pad, a shunt-inductor position to ground (a DC path that takes ESD to ground and doubles as a tuning element) and a low-capacitance ESD diode position. Tuning range: the values are set by the prototype measurement; the positions accept capacitors and inductors of the 0603 RF range so the frame can be matched in either direction (**UNVERIFIED** until the frame is designed).
3. **ESD part class:** the diode must add no more than about 0.2 pF at 2.5–6 GHz. Example: Infineon ESD904-B1-W0201, 0.1 pF at 2.5 GHz and 0.09 pF at 5 GHz, 0.1 dB insertion loss at 2.5 GHz, IEC 61000-4-2 ±9 kV contact / ±10 kV air, 5.5 V, 0201 (Infineon datasheet, document reference IFX-vxu1699602170948, sha256 `e00f647e…c799`). The part is chosen in the BOM; this note fixes the class, not the part. A diode at an antenna that the user can touch is required by the product's ESD rule (BRD-007, PCB-E-01), because the metal frame is an external contact surface.
4. **Case-ground contacts:** spring-contact pads to ground at both top corners and on the left and right board edges in the top band, so a split band, a slot or a window frame can be grounded on either side of the feed; plus the four mounting bosses on a plated GND ring (PCB-H-03). Each pad reaches the ground plane through its own vias at the pad, and its ESD current returns locally, never through the audio reference region (PCB-E-04, PCB-E-05).
5. **Keep-outs:** around the feed pad and the top-wall zone, the provisional ≥ 5 mm keep-out to metal parts of ADR 0018 item 5 applies to the case antenna's radiating part as well; the microSD shell and other metal parts stay out of it.
6. **Assembly variants (BRD-053):** every position of the branch carries its variant: *polymer* (U.FL and 146153 fitted, branch DNP), *metal with end cap* (same as polymer, matching retuned), *metal frame* (branch fitted, U.FL DNP). Production in the polymer case leaves the branch unpopulated; the cost of the empty footprints is copper only.
7. **Software:** the variant data names the fitted antenna path, and Blackbird OS selects the matching calibration file and the regional TX-power table capped at the SAR-tested level of that variant (ADR 0018 item 6; SYS-040; BRD-049).

## 5. Certification per strategy

What CER-0248 says:

- **FCC:** a changed antenna needs documentation "equivalent to a Class I change": the same type as the original antenna, gain the same or lower, spurious no more than 3 dB worse (CER-0248 §2.1.3.12, p. 28). Portable use already needs a Class II permissive change with the SAR report (§2.1.3.6).
- **US and Canada:** "user can use any equivalent type of antenna with less antenna gain than antenna gain of recommended antennas for US/CA and EU under approval of Class I Permissive Change by Murata"; an unlisted vendor is evaluated against FCC KDB 178919 (E2B-09-1413 §3.5.1, p. 14).
- **ISED:** "Antenna types not included in this list that have a gain greater than the maximum gain indicated for any type listed are strictly prohibited" (CER-0248 p. 34).
- **Japan:** "JP is required to add an antenna in the Certified antenna list if user use an antenna that is not in the certified antenna list" (E2B-09-1413 §3.5.1).
- **FCC permissive-change policy:** equivalent antennas (same type, equal or lower gain, similar in-band and out-of-band characteristics) are a Class I change; a new antenna type or a higher gain needs a Class II change (KDB 178919 D01 §II, as summarised by module makers' guides; the KDB text was not retrieved, **UNVERIFIED**).

| Region | S1 (listed 146153 behind a non-metal cap) | S2 (frame or slot antenna) |
|---|---|---|
| USA | As ADR 0018: Class II (mobile to portable) with SAR of the metal variant; Class I documentation of the retuned match | New type: Class II permissive change through Murata, folded into the portable Class II filing the T1 needs anyway; gain measured, kept ≤ 3.2 / 4.25 dBi; spurious scan |
| Canada | As ADR 0018: Class 4 with SAR | Permissive change through Murata for a new type at no higher gain (class **UNVERIFIED**; the Class 4 for SAR is needed anyway) |
| EU | Radiated tests and EN 50566 SAR on the metal variant | Same, with the frame antenna's radiated data; no antenna list |
| Japan | Listed antenna, no filing | Murata must add the antenna to certification 001-P02018; no host-side route |

Each metal-case variant is a regional variant of its own (RFC 0011 §4 and rule 9): its own SAR report, its own TX-power cap, its own filings. Prototypes (Q1) are not constrained by the lists: a metal-core prototype can be machined and anodised through PCBWay (CASE-028) to measure S1 and S2 before any filing.

## 6. Recommendation

- **S1 first.** It keeps the antenna, the board, the regional routes and the measurements of the polymer T1; the metal-case variant then differs only in the case cap, the retuned match and its own SAR.
- **S2 as the option the board keeps open.** The branch, contacts and ESD positions cost only copper in the polymer production board and let a metal-frame case be developed later without a respin.
- **Back cover only if both fail**, with the HAT keep-out extended over it; **never the faceplate**.

## 7. Input to the case (E4.6)

One line for the case's interface input list:

- **Metal (anodised-aluminium) core, CASE-022:** either a non-metallic top end cap (polymer, glass or ceramic) over the whole top wall, wrapping onto the side walls and the back far enough to keep the 146153-0050's radiator ≥ 5 mm (provisional) from metal (S1, preferred), or a frame antenna in the top or upper side walls (dielectric-filled cuts or slots) whose feed and ground points meet the board's feed and ground contact pads (PCB-R-10, PCB-R-11) through spring contacts on un-anodised (masked or laser-ablated) spots (S2); in both cases the metal core is bonded to board ground at the mounting bosses, nothing radiates from the faceplate, and the back cover carries no antenna except as a flagged last resort.

## 8. Open points

1. Antenna-vendor primary sources not obtained in this session: Molex application specification for the 146153 (clearance), Ignion and Taoglas metal-enclosure application notes (automated fetches refused or timed out). Needed before the S2 design starts.
2. FCC KDB 178919 D01 text, and ISED's classification of an antenna-type change for a portable host: confirm with Murata or a test lab.
3. Murata (outward contact, later): whether the shared junction after its copied line keeps S1 within the Class I documentation; whether a frame antenna can join the Class II / Class 4 filings and Japan's certification.
4. The cap width (S1) and the frame cuts (S2) are set by return-loss, efficiency and SAR measurements on a metal-core prototype (Q1 experiment), not by this note.

## Sources

- Murata CER-0248 Rev. 6.0 (§2.1.3.5, §2.1.3.6, §2.1.3.12, p. 34) and E2B-09-1413 Rev. 9.0 (§3.5.1): URLs and hashes in `parts-lib/manifest.toml`.
- Antenova, *4 ways to increase wireless antenna performance in metal devices*, <https://www.antenova.com/4-ways-to-increase-wireless-antenna-performance-in-metal-devices>, read 2026-10-24.
- F. Casado et al., *2.45 GHz printed IFA on metallic environments: clearance distance and retuning considerations*, EuCAP 2012, <https://dsp.tecnalia.com/items/ef101aad-3eed-40d8-8fbf-c935baf44212> (abstract).
- *Design of dual-band antenna for metal-bezel smartwatches with circular polarization in GPS band and low wrist effect*, IEEE Trans. Antennas Propag. 71(6):4651–4662, 2023, <https://pure.bit.edu.cn/en/publications/design-of-dual-band-antenna-for-metal-bezel-smartwatches-with-cir/> (abstract).
- Apple Inc., US 10,965,008 B2, *Electronic device with housing slots for antennas*, <https://patents.google.com/patent/US10965008>; US 8,373,610 B2, *Microslot antennas for electronic devices*, <https://patents.google.com/patent/US8373610>; US 9,954,273, *Electronic device antennas with laser-activated plastic and foam carriers* (USPTO).
- Taoglas, *LDS antenna technology*, <https://www.taoglas.com/lds-antenna-technology/> (vendor claim).
- Infineon, ESD904-B1-W0201 datasheet, <https://www.infineon.com/assets/row/public/documents/24/49/infineon-esd904-b1-w0201-datasheet-en.pdf>, sha256 `e00f647e537e4a784a36f9868f11f82a8371911db181a27bdc52fd999092c799`.
- FCC permissive-change policy as summarised by Silex Technology, <https://www.silextechnology.com/unwired/permissive_change_policy> (secondary).
- MIL-A-8625 Type II thickness as quoted by finishers (secondary), for example <https://www.mpofcinci.com/blog/mil-a-8625f/>.
