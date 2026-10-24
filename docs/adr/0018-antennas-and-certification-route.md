# ADR 0018: Antennas for the Type 2EL and their certification route

- **Status:** Accepted
- **Date:** 2026-10-24
- **Decided by:** Claude, under the maintainers' delegation (2026-10-24), following the product rules (the audiophile experience is never sacrificed; battery autonomy is a top priority, T1-009; prefer available commercial parts; limits only for safety, documented and visible, BRD-049; software adapts to the hardware through data, SYS-040) and the maintainers' regulatory strategy of 2026-10-24 (prototypes use the best-available part, products are regional variants, [RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md))

## Context

BOM line 57 fits two Molex 146187-0050 antennas, which are on Japan's list of the Murata Type 2EL certification but not on the FCC or ISED lists, and the module's FCC and ISED grants are for mobile use only, while the T1 is handheld (BRD-025; [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) C3; PCB-R-04, PCB-R-05, PCB-R-07). Task E1.13 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md).

The [antennas and RF exposure study](../research/2026-10-antennas-and-rf-exposure.md) found:

- Four external antennas are on the FCC, ISED and Japan lists: Molex 146153, Molex 219611, Unictron WT32D1-KX and Inventek W24P-U (2.4 GHz only). Only the 146153 and 219611 cover both bands and are stocked. Murata's trace antenna needs 20 mm of clearance and is out (§1).
- The Molex 146153-0050 (34.9 × 9.0 × 0.1 mm flex, U.FL, 3.2 / 4.25 dBi registered) is the best-stocked candidate: Digi-Key 15,886, Mouser 21,613, LCSC 113 (2026-10-24) (§2).
- In the 59.5 × 94.3 × 25.0 mm body the top band is 7.0 mm deep. The 146153 fits on the inside of the top wall (56.3 × 14.2 mm), 7.0 mm from the battery; the 219611 (15.4 mm tall) does not, and no second antenna fits with a provisional 5 mm keep-out to metal (§3).
- Molex's "-0050" is its 50 mm length class (43.3 mm of bare cable is drawn); the 146187-0050's cable is most likely not short of Japan's "50 mm or more" (**UNVERIFIED** until Murata confirms) (§1.3).
- SAR cannot be avoided by placement: at the T1's separations (below 5 mm) the FCC exemption threshold is 2.74 mW at 2.45 GHz and 1.44 mW at 5.5 GHz and RSS-102's 3 mW and 1 mW, against up to 100 mW (2.4 GHz) and 63 mW (5 GHz) conducted from the module under FCC (§5).

## Decision

1. **Antenna: Molex 146153-0050**, one per T1, on ANT0, mounted on the inside of the top wall with its long axis along the width and away from the microSD corner. It is the prototype antenna (Q1, by availability and fit) and the production antenna of every region Murata's certification covers (§2 below), so prototype measurements carry over to the products.
2. **Configuration: Murata's shared antenna** (Wi-Fi 2.4 / 5 GHz and Bluetooth on ANT0; 10 pF from pin 18 to pin 23). The dedicated configuration (Bluetooth on ANT1) stays open in the layout and on the prototype. It becomes the production configuration only if the coexistence gate below fails, and then with a case change that gives a second antenna its keep-out.
3. **Regional variants (Q3):**

   | Region | Antenna | Route | TX-power table |
   |---|---|---|---|
   | USA | 146153-0050 (FCC Table 20) | Class II permissive change by Murata, mobile to portable, with the T1's SAR report; Class I documentation of the tuned antenna (same type, gain ≤ 3.2 / 4.25 dBi, spurious ≤ 3 dB worse); Part 15B SDoC | Murata FCC (CER-0248 Tables 6–18), capped at the SAR-tested level |
   | Canada | 146153-0050 (ISED Table 36), HVIN LBES5PL2EL-SANT | Class 4 permissive change by Murata with the SAR report against RSS-102 Issue 6 | Murata ISED (Tables 22–34), capped likewise |
   | EU (UK expected to follow, **UNVERIFIED**) | 146153-0050 (no list) | CE self-declaration: Murata's conducted reports, radiated tests and EN 50566 SAR on the T1 | Murata EU (Tables 38–47) |
   | Japan | 146153-0050 (Table 56) | Within certification 001-P02018; no filing; SAR scope **UNVERIFIED** | Murata Japan (Tables 49–53) |
   | Other markets | — | Not covered by CER-0248; defined when the maintainers open them | — |

   If the 146153 fails in the case, the fallback is another listed antenna (219611 needs 15.4 mm of wall height) or, for the USA and Canada, a Class I change through Murata for an equivalent type at no higher gain; Japan then needs Murata to add the antenna to its certification.
4. **The layout holds every option (no respin):** both ANT0 and ANT1 paths as Murata's copy, with U.FL, 0603 matching positions, the 10 pF shared link and the dedicated-configuration positions; U.FLs in the top band near the top wall; ≥ 0.8 mm keep-out under each U.FL (study §6.1).
5. **Keep-out:** the radiating element stays ≥ 5 mm (provisional, **UNVERIFIED**) from any metal: battery, metal pocket floor, microSD shell, screw inserts, display frame and HAT metal. The case keeps that zone free and uncoated. The figure is confirmed or changed by measurement on the prototype.
6. **Software guarantees (Blackbird OS):** the variant's certified TX-power table is selected from variant data; the time-averaged power never exceeds the SAR-tested level, as a documented and visible safety and legal limit (BRD-049); the calibration file follows the fitted configuration; 802.15.4 stays off (not wired).
7. **RF exposure is a Q2–Q3 item per regional variant:** SAR pre-assessment at Q2 (V5-06), formal SAR at Q3 for the USA, Canada and the EU; the Murata filings are outward contacts for later.

## Consequences

- **BOM line changes** (bom-v1.md is owned by another session; to be applied there):
  - Line 57: Molex 146187-0050 × 2 → **Molex 146153-0050 × 1** (Wi-Fi/Bluetooth antenna, 2.4/5 GHz flexible dipole, U.FL, 50 mm class); availability Digi-Key 15,886 @ $2.27, Mouser 21,613, Newark 6,592, TME 1,068, LCSC C916292 113 @ $2.49 (2026-10-24); alternates Molex 219611-0050 (listed in all three, needs 15.4 mm of wall) and, Japan only, Molex 146187-0050. Notes: top-wall mount, shared configuration; a second antenna only under the dedicated option (prototype experiment: Inventek W24P-U, 2.4 GHz, listed in all three).
  - Line 56: Hirose U.FL-R-SMT-1(10) quantity stays **2** (ANT0 fitted; ANT1 footprint kept, fitted on the prototype for the dedicated-configuration experiment, DNP in production unless decision 2 changes); the note "number of RF pins on Type 2EL **UNVERIFIED**" becomes "ANT0 pin 15, ANT1 pin 23 (E2B-54-1953 Table 3)".
  - Line 58: matching positions in **0603** as in Murata's reference (E2B-09-1413 Figures 9–10), not 0402, plus the 10 pF pin 18–pin 23 link (fitted for shared) and the dedicated-configuration positions (DNP).
- **Constraints to update in the PCB design constraints** (main session): PCB-R-04 names the 146153-0050 and the regional routes of this ADR; PCB-R-07 takes the 5 mm provisional keep-out and the top-wall position instead of "Molex 146187 data".
- **Verification rows to add** (electronics integration and verification, prototype level): antenna return loss and efficiency in the prototype case, gain at or below 3.2 / 4.25 dBi after tuning, spurious no more than 3 dB worse than Murata's report; isolation and coexistence of the dedicated option; and the **coexistence gate**: Bluetooth audio at the highest codec rate the T1 offers, with Wi-Fi streaming at the same time, over a long session, without dropouts. If shared fails it, decision 2 switches to dedicated with a case change before Q2.
- **Case input (E4.6):** the top-wall antenna area and its metal-free zone; HATs keep the antenna keep-out (hat-standard).
- **Software input (system):** a TX-power table loader or equivalent cap for mainline `nxpwifi` is needed before Q2; how Murata's tables reach the mainline driver is **UNVERIFIED**.
- **parts-lib:** new sheets for Molex 146153-0050 and Inventek W24P-U; the 146187-0050 sheet gets a note on Molex's length classes.
- **Outward contacts for later (not made):** Murata for the Class II (FCC) and Class 4 (ISED) permissive changes, what the SAR report must contain, how "cable length" is measured, and Japan's SAR scope.
