"""Build test/t1-main-board-rules-test.kicad_pcb: one failing and one passing object per rule.

The product rules use net classes and named rule areas, so this board extends
kicad-lib's TestBoard (design-rules/tools/testboard.py, through the
submodule) with nets in those classes, rule areas, and rows of any height.

Run with KiCad's Python, from any directory:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
      hardware/rules/test/make_test_board.py
Then check it with:
  python3 hardware/lib/opendap/design-rules/tools/check_drc.py \
      hardware/rules/test/t1-main-board-rules-test.kicad_pcb
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.normpath(os.path.join(HERE, "..", "t1-main-board.kicad_dru"))
sys.path.insert(0, os.path.normpath(
    os.path.join(HERE, "..", "..", "lib", "opendap", "design-rules", "tools")))

import pcbnew  # noqa: E402
import testboard as tbm  # noqa: E402
from testboard import TEST_BOARD_IGNORED_CHECKS, TestBoard, mm, pt  # noqa: E402

NAME = "t1-main-board-rules-test"
P = "T1 "

# Net classes used by the rules, with the netclasses.toml names.
CLASSES = ("PWR_BAT", "PWR_VSYS", "PWR_VBUS", "PWR_5V1", "PWR_HAT3V3",
           "PWR_AMP", "SW_NODE", "AUDIO_ANALOG", "AUDIO_REF", "MCLK")


class ProductTestBoard(TestBoard):
    """Rows of any height, nets in named classes, named rule areas."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = tbm.TOP
        self.board_w = tbm.BOARD_W
        self._class_nets = {}

    def class_net(self, netclass):
        n = self._class_nets.get(netclass, 0) + 1
        self._class_nets[netclass] = n
        net = pcbnew.NETINFO_ITEM(self.board, f"{netclass}_{n}")
        self.board.Add(net)
        return net

    def gnd(self):
        net = self.board.FindNet("GND")
        if net is None:
            net = pcbnew.NETINFO_ITEM(self.board, "GND")
            self.board.Add(net)
        return net

    def area(self, name, x1, y1, x2, y2):
        zone = pcbnew.ZONE(self.board)
        zone.SetIsRuleArea(True)
        zone.SetZoneName(name)
        zone.SetDoNotAllowTracks(False)
        zone.SetDoNotAllowVias(False)
        zone.SetDoNotAllowPads(False)
        zone.SetDoNotAllowZoneFills(False)
        zone.SetDoNotAllowFootprints(False)
        zone.SetLayerSet(pcbnew.LSET.AllCuMask())
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            outline.Append(mm(x), mm(y))
        self.board.Add(zone)

    def add_row(self, name, height, builder):
        self._label(tbm.LABEL_X, self.y, name)
        builder(tbm.FAIL_X, self.y, True)
        builder(tbm.PASS_X, self.y, False)
        self.expected_rules[name] = self.expected_rules.get(name, 0) + 1
        self.y += height
        self.row += 1

    # fixtures ------------------------------------------------------------

    def width_row(self, name, layer, netclass=None, area=None):
        w = self.rule(name).value("track_width")
        height = max(tbm.ROW_H, w + 3.0)

        def build(x, y, fail):
            if area:
                self.area(area, x - 0.5, y - 0.5, x + 3.5, y + 0.5)
            net = self.class_net(netclass) if netclass else None
            cy = y + w / 2
            # A wide track's round ends reach w / 2 past its end points: the
            # failing one starts at the FAIL column, the passing one clears it.
            xs = x + w / 2 if fail else max(x, tbm.FAIL_X + 2 * w + 2.0)
            self._track(xs, cy, xs + 1, cy, self._v(w, fail), layer, net)
            self.board_w = max(self.board_w, xs + 1 + w / 2 + 2.0)
        self.add_row(name, height, build)

    def clearance_row(self, name, width, net_a=None, net_b=None, area=None):
        gap = self.rule(name).value("clearance")
        height = max(tbm.ROW_H, gap + 2 * width + 2.5)

        def build(x, y, fail):
            if area:
                self.area(area, x - 0.5, y - 0.5, x + 3.5, y + 2 * width + gap + 0.5)
            g = self._v(gap, fail)
            a = self.class_net(net_a) if net_a else None
            b = self.class_net(net_b) if net_b else None
            self._track(x, y, x + 3, y, width, pcbnew.F_Cu, a)
            self._track(x, y + width + g, x + 3, y + width + g, width, pcbnew.F_Cu, b)
        self.add_row(name, height, build)

    def via_diameter_row(self, name, drill, vtype=None, layers=None):
        dia = self.rule(name).value("via_diameter")

        def build(x, y, fail):
            self._via(x, y, drill, self._v(dia, fail), vtype, layers)
        self.add_row(name, tbm.ROW_H, build)

    def edge_row(self, name, width):
        gap = self.rule(name).value("edge_clearance")

        def build(x, y, fail):
            self._cutouts.append((x, y - 0.5, x + 1, y + 0.5))
            ty = y + 0.5 + self._v(gap, fail) + width / 2
            self._track(x - 1, ty, x + 2, ty, width, pcbnew.F_Cu)
        self.add_row(name, tbm.ROW_H, build)

    def foreign_track_row(self, name, area):
        def build(x, y, fail):
            self.area(area, x - 0.5, y - 0.5, x + 3.5, y + 0.5)
            net = self._net() if fail else self.class_net("AUDIO_ANALOG")
            self._track(x, y, x + 3, y, 0.2, pcbnew.F_Cu, net)
        self.add_row(name, tbm.ROW_H, build)

    # output --------------------------------------------------------------

    def save(self, out_dir, ignore_checks=()):
        # testboard.save() sizes the outline from TOP, ROW_H and BOARD_W.
        tbm.TOP, saved_rows = self.y - self.row * tbm.ROW_H, self.row
        tbm.BOARD_W = self.board_w
        pcb = super().save(out_dir, ignore_checks)
        self.row = saved_rows
        return pcb

    def _write_project(self, out_dir, ignore_checks):
        super()._write_project(out_dir, ignore_checks)
        path = os.path.join(out_dir, f"{self.name}.kicad_pro")
        with open(path, encoding="utf-8") as fh:
            project = json.load(fh)
        default = project["net_settings"]["classes"][0]
        for i, name in enumerate(CLASSES):
            cls = dict(default)
            cls["name"] = name
            cls["priority"] = i
            project["net_settings"]["classes"].append(cls)
        project["net_settings"]["netclass_patterns"] = [
            {"netclass": name, "pattern": f"{name}_*"} for name in CLASSES]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(project, fh, indent=2, sort_keys=True)
            fh.write("\n")


def main():
    tb = ProductTestBoard(NAME, RULES, copper_layers=8)
    micro = (pcbnew.VIATYPE_MICROVIA, (pcbnew.F_Cu, pcbnew.In1_Cu))

    tb.clearance_row(P + "PCB-G-01: Copper clearance", width=0.2)
    tb.width_row(P + "PCB-G-01: Track width", pcbnew.F_Cu)
    tb.clearance_row(P + "PCB-G-02: Copper clearance in the BGA escape", width=0.1,
                     area="BGA_ESCAPE")
    tb.width_row(P + "PCB-G-02: Track width in the BGA escape", pcbnew.F_Cu,
                 area="BGA_ESCAPE")
    tb.via_diameter_row(P + "PCB-G-03: Microvia diameter", 0.1, *micro)
    tb.via_diameter_row(P + "PCB-G-04: Mechanical via diameter", 0.2)
    tb.edge_row(P + "PCB-G-05: Copper to board edge", width=0.2)

    for rule, netclass in (
            ("PCB-P-01: Battery path track width", "PWR_BAT"),
            ("PCB-P-02: VSYS track width", "PWR_VSYS"),
            ("PCB-P-03: VBUS input track width", "PWR_VBUS"),
            ("PCB-P-04: 5.1 V source track width", "PWR_5V1"),
            ("PCB-P-05: HAT 3.3 V track width", "PWR_HAT3V3")):
        tb.width_row(P + rule + " (outer)", pcbnew.F_Cu, netclass)
        tb.width_row(P + rule + " (inner)", pcbnew.In1_Cu, netclass)
    tb.width_row(P + "PCB-P-06: Amplifier rail track width", pcbnew.In2_Cu, "PWR_AMP")

    tb.clearance_row(P + "PCB-A-06: Switch node to analog audio", width=0.2,
                     net_a="SW_NODE", net_b="AUDIO_ANALOG")
    tb.foreign_track_row(P + "PCB-A-07: Foreign track in the analog audio area",
                         "AUDIO_ANALOG")
    tb.clearance_row(P + "PCB-I-09: Master clock to other nets", width=0.2,
                     net_a="MCLK")

    print(tb.save(HERE, ignore_checks=TEST_BOARD_IGNORED_CHECKS))


if __name__ == "__main__":
    main()
