#!/usr/bin/env python3
"""RK3566 BGA escape study: place the escape vias and route the escape of every used ball.

Run with KiCad's Python (pcbnew, numpy), from any directory:

    PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
    $PY hardware/studies/bga-escape/escape.py            # both stackups
    $PY hardware/studies/bga-escape/escape.py 8          # one

Inputs (read only):
- the RK3566 footprint from kicad-lib (workspace repos.tsv, ODAP_KICAD_LIB_DIR, or the submodule
  hardware/lib/opendap once it carries the part);
- the ball nets from hardware/pinout/pinout-v1.csv;
- the composed T1 rules hardware/t1-main-board/t1-main-board.kicad_dru, copied next to each study
  board as <board>.kicad_dru.

Writes bga-escape-<n>l.kicad_pcb / .kicad_pro / .kicad_dru and bga-escape-<n>l.result.json in this
folder. The method, the assumptions and the results are in docs/research/2026-10-bga-escape-study.md.

Method, in short: a grid router (0.025 mm grid, 8 directions, A* with a turn penalty) over obstacle
maps inflated by the clearances below; every geometric clearance is checked exactly again when a via
is placed, and KiCad's DRC with the composed rules is the final judge.
"""

import csv
import heapq
import json
import math
import os
import shutil
import sys

import numpy as np
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PINOUT = os.path.join(BOARD_REPO, "hardware", "pinout", "pinout-v1.csv")
DRU = os.path.join(BOARD_REPO, "hardware", "t1-main-board", "t1-main-board.kicad_dru")
FP_LIB = "Rockchip.pretty"
FP_NAME = "Rockchip_FCCSP-565L_15.5x14.4mm_P0.4mm_P0.65mm_Ball0.25mm_Pad0.25mm_NSMD"

# ---- geometry and rules (mm). Sources in the research note, section 2.
CX, CY = 11.0, 11.0          # package centre on the study board
BODY_X, BODY_Y = 15.5, 14.4  # RK3566 DS Rev 1.1 p. 21
BOARD = 22.0
ESCAPE_MARGIN = 0.3          # a route has escaped once it is this far outside the body
AREA_MARGIN = 1.0            # rule area BGA_ESCAPE: the body plus 1.0 mm (the courtyard)
W = 0.08                     # escape track: 0.08 mm (> PCBWay HDI 3 mil normal; CRAFT-43 series)
C = 0.0762                   # copper clearance: 3 mil, PCBWay HDI normal (0.065 mm is the floor)
W_PWR = 0.15                 # power and ground dog-bones and power-layer links
HOLE_CU_OUT, HOLE_CU_IN = 6 * 0.0254, 9 * 0.0254   # PCBWay HDI hole to copper, outer / inner (8 layers)
# Sensitivity runs only (research note section 5): ESCAPE_HOLE_CU_IN_MIL replaces the inner
# hole-to-copper value in the router and in a modified rule copy, written to ESCAPE_OUT.
SENS_MIL = os.environ.get("ESCAPE_HOLE_CU_IN_MIL")
if SENS_MIL:
    HOLE_CU_IN = float(SENS_MIL) * 0.0254
OUT = os.environ.get("ESCAPE_OUT", HERE)
HOLE_HOLE = 11 * 0.0254      # PCBWay HDI via hole to hole (mechanical)
MV_D, MV_H = 0.25, 0.10      # laser microvia land / drill (PCB-G-03, CRAFT-45)
TH_D, TH_H = 0.46, 0.20      # mechanical via (through or buried) pad / drill (PCB-G-04, CRAFT-45)
PAD_D = 0.25                 # BGA land (kicad-lib footprint)
EPS = 0.004                  # grid safety margin
S = 0.025                    # router grid step

STACKUPS = {
    # 1+N+1 HDI, L2 and L7 ground (task assumption; no stackup-v1 yet). Roles per layer.
    8: ["SIG", "GND", "SIG", "SIG", "PWR", "SIG", "GND", "SIG"],
    10: ["SIG", "GND", "SIG", "SIG", "PWR", "SIG", "GND", "SIG", "GND", "SIG"],
}


def mm(v):
    return int(round(v * 1e6))


def V(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def kicad_lib_dir():
    env = os.environ.get("ODAP_KICAD_LIB_DIR")
    cands = [env] if env else []
    ws = os.path.abspath(os.path.join(BOARD_REPO, "..", "..", "..", ".."))
    tsv = os.path.join(ws, "repos.tsv")
    if os.path.exists(tsv):
        with open(tsv) as fh:
            for line in fh:
                f = line.rstrip("\n").split("\t")
                if len(f) == 2 and f[1] == "opendap-project/kicad-lib":
                    cands.append(os.path.join(ws, f[0]))
    cands.append(os.path.join(BOARD_REPO, "hardware", "lib", "opendap"))
    for c in cands:
        if c and os.path.exists(os.path.join(c, "footprints", FP_LIB, FP_NAME + ".kicad_mod")):
            return c
    sys.exit("RK3566 footprint not found in kicad-lib (set ODAP_KICAD_LIB_DIR)")


# ------------------------------------------------------------------ obstacle model

class Layer:
    """Exact geometry per copper layer plus a rasterised map of forbidden track centres."""

    def __init__(self, idx, x0, y0, nx, ny):
        self.idx = idx
        self.x0, self.y0, self.nx, self.ny = x0, y0, nx, ny
        self.block = np.zeros((ny, nx), dtype=np.int16)
        self.circles = []   # (x, y, r, net, hole_r, mech); hole_r -1 marks a pad
        self.segs = []      # (x1, y1, x2, y2, w, net)
        self.cb = {}        # circle buckets, 0.5 mm

    def near_circles(self, x, y, reach=1.2):
        k = int(math.ceil(reach / 0.5))
        bx, by = int(math.floor(x / 0.5)), int(math.floor(y / 0.5))
        for i in range(bx - k, bx + k + 1):
            for j in range(by - k, by + k + 1):
                for c in self.cb.get((i, j), ()):
                    yield c

    def cell(self, x, y):
        return int(round((x - self.x0) / S)), int(round((y - self.y0) / S))

    def xy(self, i, j):
        return self.x0 + i * S, self.y0 + j * S

    def _stamp_circle(self, x, y, R, sign):
        i0, i1 = int((x - R - self.x0) / S) - 1, int((x + R - self.x0) / S) + 2
        j0, j1 = int((y - R - self.y0) / S) - 1, int((y + R - self.y0) / S) + 2
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, self.nx), min(j1, self.ny)
        if i0 >= i1 or j0 >= j1:
            return
        xs = self.x0 + np.arange(i0, i1) * S
        ys = self.y0 + np.arange(j0, j1) * S
        d2 = (xs[None, :] - x) ** 2 + (ys[:, None] - y) ** 2
        self.block[j0:j1, i0:i1] += sign * (d2 < R * R).astype(np.int16)

    def _stamp_seg(self, x1, y1, x2, y2, R, sign):
        i0 = int((min(x1, x2) - R - self.x0) / S) - 1
        i1 = int((max(x1, x2) + R - self.x0) / S) + 2
        j0 = int((min(y1, y2) - R - self.y0) / S) - 1
        j1 = int((max(y1, y2) + R - self.y0) / S) + 2
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, self.nx), min(j1, self.ny)
        if i0 >= i1 or j0 >= j1:
            return
        xs = self.x0 + np.arange(i0, i1) * S
        ys = self.y0 + np.arange(j0, j1) * S
        X, Y = np.meshgrid(xs, ys)
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = np.zeros_like(X) if L2 == 0 else np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0, 1)
        d2 = (X - x1 - t * dx) ** 2 + (Y - y1 - t * dy) ** 2
        self.block[j0:j1, i0:i1] += sign * (d2 < R * R).astype(np.int16)

    def circle_R(self, r, hole_r, mech, inner):
        R = r + C
        if mech:
            R = max(R, hole_r + (HOLE_CU_IN if inner else HOLE_CU_OUT))
        return R + W / 2 + EPS

    def add_circle(self, x, y, r, net, hole_r=0.0, mech=False, inner=False):
        c = (x, y, r, net, hole_r, mech)
        self.circles.append(c)
        self.cb.setdefault((int(math.floor(x / 0.5)), int(math.floor(y / 0.5))), []).append(c)
        self._stamp_circle(x, y, self.circle_R(r, hole_r, mech, inner), 1)
        return c

    def del_circle(self, c, inner):
        self.circles.remove(c)
        self.cb[(int(math.floor(c[0] / 0.5)), int(math.floor(c[1] / 0.5)))].remove(c)
        self.remove_circle_stamp(c, inner, -1)

    def remove_circle_stamp(self, c, inner, sign):
        x, y, r, net, hole_r, mech = c
        self._stamp_circle(x, y, self.circle_R(r, hole_r, mech, inner), sign)

    def add_seg(self, x1, y1, x2, y2, w, net):
        q = (x1, y1, x2, y2, w, net)
        self.segs.append(q)
        self._stamp_seg(x1, y1, x2, y2, w / 2 + C + W / 2 + EPS, 1)
        return q

    def del_seg(self, q):
        self.segs.remove(q)
        self._stamp_seg(q[0], q[1], q[2], q[3], q[4] / 2 + C + W / 2 + EPS, -1)


def seg_seg_dist(a, b):
    (x1, y1, x2, y2), (x3, y3, x4, y4) = a, b
    def ccw(ax, ay, bx, by, cx, cy):
        return (cx - ax) * (by - ay) - (bx - ax) * (cy - ay)
    d1, d2 = ccw(x3, y3, x4, y4, x1, y1), ccw(x3, y3, x4, y4, x2, y2)
    d3, d4 = ccw(x1, y1, x2, y2, x3, y3), ccw(x1, y1, x2, y2, x4, y4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(seg_point_dist(x1, y1, x2, y2, x3, y3), seg_point_dist(x1, y1, x2, y2, x4, y4),
               seg_point_dist(x3, y3, x4, y4, x1, y1), seg_point_dist(x3, y3, x4, y4, x2, y2))


def seg_point_dist(x1, y1, x2, y2, px, py):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - x1 - t * dx, py - y1 - t * dy)


# ------------------------------------------------------------------ router

DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def astar(layer, start, is_goal, h, max_expand=400000, window=None, own=()):
    """A* from a cell to any goal cell, avoiding blocked cells. Turn penalty keeps paths straight.
    own: stamps (callables) removed during the search and restored afterwards."""
    for f in own:
        f(-1)
    try:
        blk = layer.block
        si, sj = start
        if window:
            wi0, wj0, wi1, wj1 = window
        else:
            wi0, wj0, wi1, wj1 = 0, 0, layer.nx, layer.ny
        if blk[sj, si] > 0:
            return None
        best = {}
        openq = [(h(si, sj), 0.0, si, sj, -1, None)]
        came = {}
        n = 0
        while openq:
            f, g, i, j, d, parent = heapq.heappop(openq)
            key = (i, j, d)
            if key in came:
                continue
            came[key] = parent
            n += 1
            if n > max_expand:
                return None
            if is_goal(i, j):
                path = []
                k = key
                while k is not None:
                    path.append((k[0], k[1]))
                    k = came[k]
                path.reverse()
                return path
            for nd, (di, dj) in enumerate(DIRS):
                ni, nj = i + di, j + dj
                if ni < wi0 or nj < wj0 or ni >= wi1 or nj >= wj1:
                    continue
                if blk[nj, ni] > 0:
                    continue
                if di and dj and (blk[j, ni] > 0 or blk[nj, i] > 0):
                    continue
                step = 1.4142 if di and dj else 1.0
                turn = 0.0 if d < 0 or d == nd else (0.6 if (nd - d) % 8 in (1, 7) else 3.0)
                ng = g + step + turn
                nk = (ni, nj, nd)
                if nk in came or best.get(nk, 1e18) <= ng:
                    continue
                best[nk] = ng
                heapq.heappush(openq, (ng + h(ni, nj), ng, ni, nj, nd, key))
        return None
    finally:
        for f in own:
            f(1)


def simplify(path):
    if len(path) < 3:
        return path
    out = [path[0]]
    for a, b, c in zip(path, path[1:], path[2:]):
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            out.append(b)
    out.append(path[-1])
    return out


# ------------------------------------------------------------------ study

class Study:

    def __init__(self, nlayers):
        self.n = nlayers
        self.roles = STACKUPS[nlayers]
        self.board = pcbnew.BOARD()
        self.board.SetCopperLayerCount(nlayers)
        self.cu = [pcbnew.F_Cu] + [getattr(pcbnew, "In%d_Cu" % i) for i in range(1, nlayers - 1)] + [pcbnew.B_Cu]
        for k, (lid, role) in enumerate(zip(self.cu, self.roles)):
            self.board.SetLayerName(lid, "L%d_%s" % (k + 1, role))
        hx, hy = BODY_X / 2 + ESCAPE_MARGIN + 0.3, BODY_Y / 2 + ESCAPE_MARGIN + 0.3
        self.x0, self.y0 = -round(hx / S) * S, -round(hy / S) * S
        nx, ny = int(round(2 * -self.x0 / S)) + 1, int(round(2 * -self.y0 / S)) + 1
        self.L = [Layer(k, self.x0, self.y0, nx, ny) for k in range(nlayers)]
        self.nets = {}
        self.rec = None
        self.result = {"layers": nlayers, "roles": self.roles, "escaped": {}, "failed": [],
                       "vias": {}, "via_in_pad": [], "power_links_failed": []}

    # ---- board items (package frame: origin at the package centre)
    def net(self, name):
        if name not in self.nets:
            ni = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(ni)
            self.nets[name] = ni
        return self.nets[name]

    def track(self, pts, li, w, net):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.board)
            t.SetStart(V(CX + x1, CY + y1))
            t.SetEnd(V(CX + x2, CY + y2))
            t.SetWidth(mm(w))
            t.SetLayer(self.cu[li])
            t.SetNet(self.net(net))
            self.board.Add(t)
            q = self.L[li].add_seg(x1, y1, x2, y2, w, net)
            if self.rec is not None:
                self.rec.append(("s", t, li, q))

    def via(self, x, y, kind, net):
        """kind: 'th' through, 'mvs' microvia L1-L2 stacked on a buried L2-L(n-1), 'mvg' microvia
        L1-L2 only (ground), 'mvb' microvia L(n-1)-Ln."""
        def add(vtype, a, b, d, h):
            v = pcbnew.PCB_VIA(self.board)
            v.SetViaType(vtype)
            v.SetPosition(V(CX + x, CY + y))
            v.SetLayerPair(self.cu[a], self.cu[b])
            v.SetWidth(mm(d))
            v.SetDrill(mm(h))
            v.SetNet(self.net(net))
            self.board.Add(v)
            if self.rec is not None:
                self.rec.append(("b", v))

        def circ(k, *a):
            c = self.L[k].add_circle(x, y, *a)
            if self.rec is not None:
                self.rec.append(("c", k, c, 0 < k < self.n - 1))
        if self.rec is not None:
            self.rec.append(("v", kind))
        if kind == "th":
            add(pcbnew.VIATYPE_THROUGH, 0, self.n - 1, TH_D, TH_H)
            for k in range(self.n):
                circ(k, TH_D / 2, net, TH_H / 2, True, 0 < k < self.n - 1)
        elif kind == "mvs":
            add(pcbnew.VIATYPE_MICROVIA, 0, 1, MV_D, MV_H)
            add(pcbnew.VIATYPE_BURIED, 1, self.n - 2, TH_D, TH_H)
            circ(0, MV_D / 2, net, MV_H / 2)
            for k in range(1, self.n - 1):
                circ(k, TH_D / 2, net, TH_H / 2, True, True)
        elif kind == "mvg":
            add(pcbnew.VIATYPE_MICROVIA, 0, 1, MV_D, MV_H)
            circ(0, MV_D / 2, net, MV_H / 2)
            circ(1, MV_D / 2, net, MV_H / 2)
        self.result["vias"][kind] = self.result["vias"].get(kind, 0) + 1

    def undo(self, rec):
        for e in reversed(rec):
            if e[0] == "s":
                self.board.Remove(e[1])
                self.L[e[2]].del_seg(e[3])
            elif e[0] == "b":
                self.board.Remove(e[1])
            elif e[0] == "c":
                self.L[e[1]].del_circle(e[2], e[3])
            elif e[0] == "v":
                self.result["vias"][e[1]] -= 1

    # ---- exact clearance check of a via site
    def via_fits(self, x, y, kind, net):
        layers = {"th": range(self.n), "mvs": range(self.n - 1), "mvg": (0, 1)}[kind]
        for k in layers:
            if kind == "th" or (kind == "mvs" and k >= 1):
                r, hole, mech = TH_D / 2, TH_H / 2, True
            else:
                r, hole, mech = MV_D / 2, MV_H / 2, False
            inner = 0 < k < self.n - 1
            hcu = HOLE_CU_IN if inner else HOLE_CU_OUT
            for (cx, cy, cr, cnet, chole, cmech) in self.L[k].near_circles(x, y):
                if abs(cx - x) > 1.2 or abs(cy - y) > 1.2:
                    continue
                d = math.hypot(cx - x, cy - y)
                if cnet == net:
                    if d < 1e-6 and k > 0:
                        return False  # no stacking on own items except the L1 pad (via in pad)
                    if mech and cmech and d < hole + chole + HOLE_HOLE:
                        return False  # hole to hole applies whatever the net
                    continue
                # KiCad applies the hole-to-copper rule when either item is a pad or a
                # mechanical via (PCBWay HDI rule condition, observed with KiCad 10.0.7)
                cpad = chole < 0
                need = r + cr + C
                if (mech or cmech or cpad) and hole > 0:
                    need = max(need, hole + hcu + cr)
                if (mech or cmech) and chole > 0:
                    need = max(need, chole + hcu + r)
                if mech and cmech:
                    need = max(need, hole + chole + HOLE_HOLE)
                if d < need:
                    return False
            for (x1, y1, x2, y2, w, snet) in self.L[k].segs:
                if snet == net:
                    continue
                d = seg_point_dist(x1, y1, x2, y2, x, y)
                need = r + w / 2 + C
                if mech:
                    need = max(need, hole + hcu + w / 2)
                if d < need:
                    return False
        return True

    def dogbone_fits(self, x1, y1, x2, y2, w, net):
        for (cx, cy, cr, cnet, chole, cmech) in self.L[0].near_circles((x1 + x2) / 2, (y1 + y2) / 2,
                                                                       math.hypot(x2 - x1, y2 - y1) / 2 + 0.8):
            if cnet == net:
                continue
            if seg_point_dist(x1, y1, x2, y2, cx, cy) < cr + C + w / 2:
                return False
            if cmech and seg_point_dist(x1, y1, x2, y2, cx, cy) < chole + HOLE_CU_OUT + w / 2:
                return False
        for (a, b, c, d, sw, snet) in self.L[0].segs:
            if snet == net:
                continue
            if seg_seg_dist((a, b, c, d), (x1, y1, x2, y2)) < sw / 2 + C + w / 2:
                return False
        return True

    # ---- goals
    def outside(self, x, y):
        return abs(x) >= BODY_X / 2 + ESCAPE_MARGIN or abs(y) >= BODY_Y / 2 + ESCAPE_MARGIN

    def h_out(self, i, j):
        x, y = self.L[0].xy(i, j)
        return max(0.0, min(BODY_X / 2 + ESCAPE_MARGIN - abs(x), BODY_Y / 2 + ESCAPE_MARGIN - abs(y))) / S

    def route_out(self, li, x, y, net, own_circle=None, window_box=None, max_expand=300000):
        lay = self.L[li]
        inner = 0 < li < self.n - 1
        own = []
        if own_circle is not None:
            c = own_circle
            own.append(lambda s, c=c: lay.remove_circle_stamp(c, inner, s))
        start = lay.cell(x, y)
        win = None
        if window_box:
            a, b = lay.cell(window_box[0], window_box[1])
            c2, d2 = lay.cell(window_box[2], window_box[3])
            win = (max(0, min(a, c2)), max(0, min(b, d2)), min(lay.nx, max(a, c2) + 1), min(lay.ny, max(b, d2) + 1))
        path = astar(lay, start, lambda i, j: self.outside(*lay.xy(i, j)), self.h_out, max_expand, win, own)
        if not path:
            return None
        return [lay.xy(i, j) for i, j in simplify(path)]

    # ------------------------------------------------------------------ run
    def run(self, lib_dir):
        # board outline and the BGA_ESCAPE rule area
        r = pcbnew.PCB_SHAPE(self.board)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetStart(V(0, 0))
        r.SetEnd(V(BOARD, BOARD))
        r.SetLayer(pcbnew.Edge_Cuts)
        r.SetWidth(mm(0.05))
        self.board.Add(r)
        z = pcbnew.ZONE(self.board)
        z.SetIsRuleArea(True)
        z.SetZoneName("BGA_ESCAPE")
        z.SetLayerSet(pcbnew.LSET.AllCuMask())
        for f in ("SetDoNotAllowTracks", "SetDoNotAllowVias", "SetDoNotAllowPads",
                  "SetDoNotAllowZoneFills", "SetDoNotAllowFootprints"):
            getattr(z, f)(False)
        o = z.Outline()
        o.NewOutline()
        ax, ay = BODY_X / 2 + AREA_MARGIN, BODY_Y / 2 + AREA_MARGIN
        for x, y in ((-ax, -ay), (ax, -ay), (ax, ay), (-ax, ay)):
            o.Append(mm(CX + x), mm(CY + y))
        self.board.Add(z)

        # footprint and nets
        fp = pcbnew.FootprintLoad(os.path.join(lib_dir, "footprints", FP_LIB), FP_NAME)
        fp.SetReference("U1")
        fp.SetPosition(V(CX, CY))
        fp.SetFPIDAsString("Rockchip:" + FP_NAME)
        self.board.Add(fp)
        with open(PINOUT, newline="") as fh:
            rows = {r["ball"]: r for r in csv.DictReader(fh)}
        balls = {}
        seen = {}
        for pad in sorted(fp.Pads(), key=lambda p: p.GetNumber()):
            b = pad.GetNumber()
            row = rows[b]
            p = pad.GetPosition()
            x, y = pcbnew.ToMM(p.x) - CX, pcbnew.ToMM(p.y) - CY
            net = row["net"]
            kind = "nc" if net in ("NC", "") else ("gnd" if row["function"] == "ground" else
                                                     ("pwr" if row["function"] == "power" else "sig"))
            if kind == "sig":
                # a signal net on two balls (joined outside the package on the real board) gets
                # one net per ball here, so each escape is checked on its own
                if net in seen:
                    net = "%s_%s" % (net, b)
                seen[net] = b
            if kind != "nc":
                pad.SetNet(self.net(net))
            balls[b] = dict(x=x, y=y, net=net, kind=kind, ring=not b.startswith("1"))
            self.L[0].add_circle(x, y, PAD_D / 2, net if kind != "nc" else "~" + b, -1.0)
        self.balls = balls

        sig = [b for b, v in balls.items() if v["kind"] == "sig"]
        self.result["used_signal_balls"] = len(sig)
        self.result["power_balls"] = sum(v["kind"] == "pwr" for v in balls.values())
        self.result["ground_balls"] = sum(v["kind"] == "gnd" for v in balls.values())

        def edge_dist(v):
            return min(BODY_X / 2 - abs(v["x"]), BODY_Y / 2 - abs(v["y"]))

        # 1. ring signals on L1: outward, outer row first, then inner balls through the gaps
        escaped = {}
        for b in sorted([b for b in sig if balls[b]["ring"]], key=lambda b: edge_dist(balls[b])):
            v = balls[b]
            x, y = v["x"], v["y"]
            box = self.out_window(x, y, 1.0)
            own = (x, y, PAD_D / 2, v["net"], -1.0, False)
            path = self.route_out(0, x, y, v["net"], own, box, 60000)
            if path:
                self.track(path, 0, W, v["net"])
                escaped[b] = 1
        self.result["escaped"]["L1"] = len(escaped)

        # 2. vias: signals (ring in the channel, core at the interstitials or in the channel),
        # then power (through), then ground (microvia to L2)
        gnd = [b for b, v in balls.items() if v["kind"] == "gnd"]
        for b in sorted([b for b in gnd if balls[b]["ring"]], key=lambda b: edge_dist(balls[b])):
            if not self.place_via(b, "gnd"):
                self.result["failed"].append(b)
        # 3. vias for every signal that did not escape on L1 (ring: in the channel; core: at
        # the interstitials, outer core rows also in the channel), outer balls first
        need_via = [b for b in sig if b not in escaped]
        need_via.sort(key=lambda b: (not balls[b]["ring"], edge_dist(balls[b])))
        pwr = [b for b, v in balls.items() if v["kind"] == "pwr"]
        core_pg = [b for b in pwr + gnd if not balls[b]["ring"]]
        sites = {}
        pwr_sites = {}
        self.ballrec = {}
        later = []
        for b in need_via + sorted(core_pg, key=lambda b: edge_dist(balls[b])):
            role = balls[b]["kind"]
            if role != "sig":
                later.append(b)   # core power and ground: after the signals are routed
                continue
            self.rec = []
            s = self.place_via(b, role)
            self.ballrec[b], self.rec = self.rec, None
            if s and role == "sig":
                sites[b] = s
            elif s and role == "pwr":
                pwr_sites[b] = s
            elif not s:
                later.append(b) if role != "sig" else self.result["failed"].append(b)
        # 4. inner and bottom layers: route every signal via out, layer by layer (L3 first),
        # vias nearest the package edge first
        order = [k for k, r in enumerate(self.roles) if r == "SIG" and k > 0]
        todo = sorted(sites, key=lambda b: self.site_edge(sites[b]))
        for li in order:
            done = []
            for b in todo:
                x, y, kind = sites[b]
                if kind == "mvs" and li == self.n - 1:
                    continue  # the stacked microvia does not reach the bottom layer
                net = balls[b]["net"]
                own = next(c for c in self.L[li].circles if c[3] == net and
                           abs(c[0] - x) < 1e-6 and abs(c[1] - y) < 1e-6)
                path = self.route_out(li, x, y, net, own, self.out_window(x, y, 3.0), 250000)
                if not path:
                    path = self.route_out(li, x, y, net, own, None, 500000)
                if path:
                    self.rec = self.ballrec[b]
                    self.track(path, li, W, net)
                    self.rec = None
                    done.append(b)
            self.result["escaped"]["L%d" % (li + 1)] = len(done)
            todo = [b for b in todo if b not in done]
            print("  L%d: %d routed, %d left" % (li + 1, len(done), len(todo)), flush=True)
        # rip-up and retry: a signal boxed in on every layer moves its via (routed dog-bone on
        # L1 to any site within 1.3 mm) to the first site from which it escapes
        moved = {}
        for b in list(todo):
            li = self.retry(b, order)
            if li is None:
                li = self.retry_with_neighbour(b, order, sites)
            if li is not None:
                moved[b] = "L%d" % (li + 1)
                self.result["escaped"]["L%d" % (li + 1)] += 1
                todo.remove(b)
        self.result["moved_vias"] = moved
        self.result["unrouted"] = sorted(todo)
        self.result["failed"] += sorted(todo)

        # 4. core power (through vias) and ground (microvias to L2), placed around the routed
        # signals; a ball whose four interstitial sites are taken gets a routed dog-bone
        for b in later:
            role = balls[b]["kind"]
            s = self.place_via(b, role)
            if not s:
                s = self.repair_supply(b, order, sites)
            if s and role == "pwr":
                pwr_sites[b] = s
            elif not s:
                self.result["failed"].append(b)

        # 5. power nets joined on the power layer (stand-in for the split plane)
        self.link_power(pwr_sites)
        return self.result

    def broad_sites(self, x, y, rad, step=0.05):
        pts = []
        k = int(rad / step)
        for i in range(-k, k + 1):
            for j in range(-k, k + 1):
                d = math.hypot(i * step, j * step)
                if 0.3 <= d <= rad:
                    pts.append((d, round((x + i * step) / S) * S, round((y + j * step) / S) * S))
        pts.sort()
        return [(px, py) for _, px, py in pts]

    def dogbone_to(self, x, y, px, py, w, net, limit=6000):
        """Straight dog-bone if it fits, else a routed one on L1; adds the track. True on success."""
        if self.dogbone_fits(x, y, px, py, w, net):
            self.track([(x, y), (px, py)], 0, w, net)
            return True
        lay = self.L[0]
        goal = lay.cell(px, py)
        own = (x, y, PAD_D / 2, net, -1.0, False)
        stamp = [lambda sg, c=own: lay.remove_circle_stamp(c, False, sg)]
        path = astar(lay, lay.cell(x, y), lambda i, j: (i, j) == goal,
                     lambda i, j: max(abs(i - goal[0]), abs(j - goal[1])), limit, None, stamp)
        if not path:
            return False
        pts = [lay.xy(i, j) for i, j in simplify(path)]
        pts[0], pts[-1] = (x, y), (px, py)
        self.track(pts, 0, w, net)
        return True

    def route_ball(self, b, px, py, kind, order):
        net = self.balls[b]["net"]
        for li in order:
            if kind == "mvs" and li == self.n - 1:
                continue
            own = next(c for c in self.L[li].circles if c[3] == net and
                       abs(c[0] - px) < 1e-6 and abs(c[1] - py) < 1e-6)
            path = self.route_out(li, px, py, net, own, None, 300000)
            if path:
                self.track(path, li, W, net)
                return li
        return None

    def retry_with_neighbour(self, b, order, sites):
        """Rip up one neighbouring signal (via, dog-bone and escape), place and route the boxed
        ball first, then put the neighbour back through its own retry. Kept only if both escape."""
        v = self.balls[b]
        near = sorted((math.hypot(sites[n][0] - v["x"], sites[n][1] - v["y"]), n) for n in sites
                      if n != b and n in self.ballrec and math.hypot(sites[n][0] - v["x"], sites[n][1] - v["y"]) < 1.4)
        for _, n in near:
            saved_n = self.ballrec[n]
            saved_b = self.ballrec.get(b, [])
            n_layer = next((e[2] for e in saved_n if e[0] == "s" and e[2] > 0), None)
            self.undo(saved_n)
            self.ballrec[n] = []
            li = self.retry(b, order)
            if li is not None:
                ln = self.retry(n, order)
                if ln is not None:
                    self.result["escaped"]["L%d" % (ln + 1)] += 1
                    if n_layer is not None:
                        self.result["escaped"]["L%d" % (n_layer + 1)] -= 1
                    return li
                # restore both as they were
                self.undo(self.ballrec[b])
                self.replay(saved_b)
                self.ballrec[b] = saved_b
            self.replay(saved_n)
            self.ballrec[n] = saved_n
        return None

    def repair_supply(self, b, order, sites):
        """A power or ground ball with no legal via site: move one neighbouring signal's via
        (and its escape) elsewhere, take the freed site, keep it only if the signal escapes."""
        v = self.balls[b]
        near = []
        for n in sites:
            if n not in self.ballrec:
                continue
            d = math.hypot(sites[n][0] - v["x"], sites[n][1] - v["y"])
            for e in self.ballrec[n]:
                if e[0] == "s":
                    q = e[3]
                    d = min(d, seg_point_dist(q[0], q[1], q[2], q[3], v["x"], v["y"]))
            if d < 0.6:
                near.append((d, n))
        near.sort()
        for _, n in near:
            saved_n = self.ballrec[n]
            n_layer = next((e[2] for e in saved_n if e[0] == "s" and e[2] > 0), None)
            self.undo(saved_n)
            self.ballrec[n] = []
            self.rec = []
            s = self.place_via(b, v["kind"])
            rec_b, self.rec = self.rec, None
            if s:
                ln = self.retry(n, order)
                if ln is not None:
                    if n_layer is not None:
                        self.result["escaped"]["L%d" % (n_layer + 1)] -= 1
                    self.result["escaped"]["L%d" % (ln + 1)] += 1
                    self.result.setdefault("moved_for_supply", {})[n] = b
                    return s
            self.undo(rec_b)
            self.replay(saved_n)
            self.ballrec[n] = saved_n
        return None

    def replay(self, rec):
        """Re-add the items of an undone record (tracks and vias)."""
        new = []
        for e in rec:
            if e[0] == "s":
                t = e[1]
                self.board.Add(t)
                q = self.L[e[2]].add_seg(*e[3])
                new.append(("s", t, e[2], q))
            elif e[0] == "b":
                self.board.Add(e[1])
                new.append(e)
            elif e[0] == "c":
                c = e[2]
                self.L[e[1]].add_circle(c[0], c[1], c[2], c[3], c[4], c[5], e[3])
                new.append(e)
            elif e[0] == "v":
                self.result["vias"][e[1]] += 1
                new.append(e)
        rec[:] = new

    def retry(self, b, order):
        v = self.balls[b]
        x, y, net = v["x"], v["y"], v["net"]
        old = self.ballrec.get(b, [])
        self.undo(old)
        for px, py in self.broad_sites(x, y, 1.3):
            kind = "mvs" if (v["ring"] or abs(px) > 6.175 + 0.1 or abs(py) > 5.525 + 0.1) else "th"
            if not self.via_fits(px, py, kind, net):
                continue
            self.rec = []
            ok = self.dogbone_to(x, y, px, py, W, net)
            if ok:
                self.via(px, py, kind, net)
                li = self.route_ball(b, px, py, kind, order)
                if li is not None:
                    self.ballrec[b], self.rec = self.rec, None
                    return li
            self.undo(self.rec)
            self.rec = None
        # nothing better: put the original items back
        self.replay(old)
        self.ballrec[b] = old
        return None

    def site_edge(self, s):
        return min(BODY_X / 2 - abs(s[0]), BODY_Y / 2 - abs(s[1]))

    def out_window(self, x, y, lateral):
        """Box from the point to the nearest body side, extended past the escape line."""
        ex, ey = BODY_X / 2 + ESCAPE_MARGIN + 0.2, BODY_Y / 2 + ESCAPE_MARGIN + 0.2
        dx, dy = ex - abs(x), ey - abs(y)
        if dx < dy:
            sx = 1 if x > 0 else -1
            return (min(x - sx * 0.3, sx * ex), y - lateral, max(x - sx * 0.3, sx * ex), y + lateral)
        sy = 1 if y > 0 else -1
        return (x - lateral, min(y - sy * 0.3, sy * ey), x + lateral, max(y - sy * 0.3, sy * ey))

    def candidates(self, b, kind):
        """Via sites around a ball, best first: dog-bone positions on 0.025 mm steps."""
        v = self.balls[b]
        x, y = v["x"], v["y"]
        out = []
        if v["ring"]:
            # into the channel between the ring and the core, then sideways along it
            ix, iy = -np.sign(x) if abs(abs(x) - 7.0) < 1e-6 else 0, -np.sign(y) if abs(abs(y) - 6.4) < 1e-6 else 0
            if abs(abs(x) - 7.4) < 1e-6:
                ix = -np.sign(x)
            if abs(abs(y) - 6.8) < 1e-6:
                iy = -np.sign(y)
            if ix and iy:  # corner balls: outward diagonal first
                cand = [(x - ix * d, y - iy * d) for d in (0.3, 0.35, 0.4)]
                cand += [(x + ix * d, y + iy * d) for d in (0.3, 0.35, 0.4)]
            else:
                cand = []
                depth = (0.825 if ix else 0.875) / 2
                base = abs(abs(x) - 7.4) < 1e-6 or abs(abs(y) - 6.8) < 1e-6  # outer row: farther
                for dd in np.arange(-0.10, 0.11, 0.025):
                    for lat in np.arange(0, 1.61, 0.025):
                        for sgn in ((1,) if lat == 0 else (1, -1)):
                            d = depth + dd + (0.4 if base else 0.0)
                            if ix:
                                cand.append((x + ix * d, y + sgn * lat))
                            else:
                                cand.append((x + sgn * lat, y + iy * d))
                cand.sort(key=lambda p: math.hypot(p[0] - x, p[1] - y))
            if kind == "gnd":
                # ground: also outward: into the gap of the outer row, or outside the body
                ox = np.sign(x) if abs(abs(x) - 7.4) < 1e-6 or abs(abs(x) - 7.0) < 1e-6 else 0
                oy = np.sign(y) if abs(abs(y) - 6.8) < 1e-6 or abs(abs(y) - 6.4) < 1e-6 else 0
                out = []
                for d in (0.4, 0.6, 0.7, 0.8, 1.0, 1.1, 1.2):
                    if ox:
                        out.append((x + ox * d, y))
                    if oy:
                        out.append((x, y + oy * d))
                cand = out + cand
            return [(round(px / S) * S, round(py / S) * S) for px, py in cand]
        # core: the four interstitial sites, then (outer core rows) the channel
        h = 0.325
        cand = [(x + sx * h, y + sy * h) for sx in (1, -1) for sy in (1, -1)]
        # quadrant fan-out: the diagonal pointing away from the package centre first, which
        # gives every ball of a full quadrant its own site
        qx, qy = (1 if x > 1e-6 else -1), (1 if y > 1e-6 else -1)
        cand.sort(key=lambda p: ((np.sign(p[0] - x) != qx) + (np.sign(p[1] - y) != qy),
                                 min(BODY_X / 2 - abs(p[0]), BODY_Y / 2 - abs(p[1]))))
        if kind == "sig":
            extra = []
            for d in np.arange(0.35, 0.56, 0.025):
                for lat in np.arange(-0.5, 0.51, 0.025):
                    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        px, py = x + sx * d + sy * 0 + (lat if sy else 0), y + sy * d + (lat if sx else 0)
                        if abs(px) > 6.175 + 0.2 or abs(py) > 5.525 + 0.2:
                            extra.append((px, py))
            extra.sort(key=lambda p: math.hypot(p[0] - x, p[1] - y))
            cand = extra + cand if min(BODY_X / 2 - abs(x), BODY_Y / 2 - abs(y)) < 1.7 else cand + extra
        return [(round(px / S) * S, round(py / S) * S) for px, py in cand]

    def place_via(self, b, role):
        v = self.balls[b]
        x, y, net = v["x"], v["y"], v["net"]
        w = W if role == "sig" else W_PWR
        for px, py in self.candidates(b, role):
            if role == "gnd":
                kind = "mvg"
            elif role == "pwr":
                kind = "th"
            else:
                kind = "mvs" if (v["ring"] or abs(px) > 6.175 + 0.1 or abs(py) > 5.525 + 0.1) else "th"
            if not self.via_fits(px, py, kind, net):
                continue
            straight = self.dogbone_fits(x, y, px, py, w, net)
            if straight:
                self.track([(x, y), (px, py)], 0, w, net)
                self.via(px, py, kind, net)
                return (px, py, kind)
            if role == "sig":
                # a routed dog-bone on L1 to the site
                lay = self.L[0]
                goal = lay.cell(px, py)
                own = (x, y, PAD_D / 2, net, -1.0, False)
                stamp = [lambda s, c=own: lay.remove_circle_stamp(c, False, s)]
                path = astar(lay, lay.cell(x, y), lambda i, j: (i, j) == goal,
                             lambda i, j: max(abs(i - goal[0]), abs(j - goal[1])), 4000, None, stamp)
                if path and len(path) < 120:
                    pts = [lay.xy(i, j) for i, j in simplify(path)]
                    pts[0], pts[-1] = (x, y), (px, py)
                    self.track(pts, 0, w, net)
                    self.via(px, py, kind, net)
                    return (px, py, kind)
        if role == "gnd":
            # ground: join a neighbouring ground ball or ground via on L1 (Rockchip's "#" pattern
            # of ground traces on top, HSPCB p. 26), nearest first
            near = sorted((math.hypot(c[0] - x, c[1] - y), c) for c in self.L[0].circles
                          if c[3] == net and 1e-6 < math.hypot(c[0] - x, c[1] - y) < 0.95)
            for wd in (W_PWR, W):
                for _, c in near:
                    if self.dogbone_fits(x, y, c[0], c[1], wd, net):
                        self.track([(x, y), (c[0], c[1])], 0, wd, net)
                        self.result.setdefault("ground_joined_on_L1", []).append(b)
                        return (c[0], c[1], "shared")
        if role in ("gnd", "pwr"):
            kind = "mvg" if role == "gnd" else "th"
            for px, py in self.broad_sites(x, y, 1.4):
                if not self.via_fits(px, py, kind, net):
                    continue
                if self.dogbone_to(x, y, px, py, W, net, 8000):
                    self.via(px, py, kind, net)
                    self.result.setdefault("routed_dogbones", []).append(b)
                    return (px, py, kind)
        # last resort: microvia in the pad (counted; the study reports it)
        kind = "mvg" if role == "gnd" else ("th" if role == "pwr" else "mvs")
        if self.via_fits(x, y, kind, net):
            self.via(x, y, kind, net)
            self.result["via_in_pad"].append(b)
            return (x, y, kind)
        return None

    def link_power(self, pwr_sites):
        li = self.roles.index("PWR")
        lay = self.L[li]
        bynet = {}
        for b, s in pwr_sites.items():
            bynet.setdefault(self.balls[b]["net"], []).append(s)
        for net, ss in sorted(bynet.items()):
            tree = [ss[0]]
            for s in sorted(ss[1:], key=lambda s: min(math.hypot(s[0] - t[0], s[1] - t[1]) for t in tree)):
                goal_cells = set()
                for t in tree:
                    gi, gj = lay.cell(t[0], t[1])
                    goal_cells.add((gi, gj))
                own = [c for c in lay.circles if c[3] == net]
                stamps = [lambda sg, c=c: lay.remove_circle_stamp(c, True, sg) for c in own]
                segs_own = [sg for sg in lay.segs if sg[5] == net]
                stamps += [lambda sg, q=q: lay._stamp_seg(q[0], q[1], q[2], q[3], q[4] / 2 + C + W / 2 + EPS, sg)
                           for q in segs_own]
                gl = [(t, lay.cell(t[0], t[1])) for t in tree]
                path = astar(lay, lay.cell(s[0], s[1]), lambda i, j: (i, j) in goal_cells,
                             lambda i, j: min(max(abs(i - c[0]), abs(j - c[1])) for _, c in gl),
                             200000, None, stamps)
                if path:
                    pts = [lay.xy(i, j) for i, j in simplify(path)]
                    self.track(pts, li, W, net)
                    tree.append(s)
                else:
                    self.result["power_links_failed"].append([net, s[0], s[1]])

    def fill_ground(self):
        for k, role in enumerate(self.roles):
            if role != "GND":
                continue
            z = pcbnew.ZONE(self.board)
            z.SetLayer(self.cu[k])
            z.SetNet(self.net("GND"))
            z.SetLocalClearance(mm(C))
            z.SetMinThickness(mm(0.065))   # PCB-W-01 in BGA_ESCAPE
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            o = z.Outline()
            o.NewOutline()
            for x, y in ((0.5, 0.5), (BOARD - 0.5, 0.5), (BOARD - 0.5, BOARD - 0.5), (0.5, BOARD - 0.5)):
                o.Append(mm(x), mm(y))
            self.board.Add(z)
        pcbnew.ZONE_FILLER(self.board).Fill(self.board.Zones())

    def save(self):
        name = "bga-escape-%dl" % self.n
        ds = self.board.GetDesignSettings()
        ds.m_SolderMaskExpansion = 0
        ds.m_SolderMaskMinWidth = mm(3 * 0.0254)   # PCBWay advanced green web [P2]
        pcbnew.SaveBoard(os.path.join(OUT, name + ".kicad_pcb"), self.board)
        if SENS_MIL:
            with open(DRU) as fh:
                text = fh.read()
            rule = text.index('(rule "PCBWay HDI: Hole to copper (inner)"')
            end = text.index("(constraint hole_clearance (min 9mil))", rule)
            text = text[:end] + "(constraint hole_clearance (min %smil))" % SENS_MIL + \
                text[end + len("(constraint hole_clearance (min 9mil))"):]
            with open(os.path.join(OUT, name + ".kicad_dru"), "w") as fh:
                fh.write(text)
        else:
            shutil.copyfile(DRU, os.path.join(OUT, name + ".kicad_dru"))
        zero = {k: 0.0 for k in (
            "min_clearance", "min_connection", "min_copper_edge_clearance", "min_groove_width",
            "min_hole_clearance", "min_hole_to_hole", "min_microvia_diameter", "min_microvia_drill",
            "min_silk_clearance", "min_text_height", "min_text_thickness", "min_through_hole_diameter",
            "min_track_width", "min_via_annular_width", "min_via_diameter")}
        project = {
            "board": {"design_settings": {"rules": zero}},
            "meta": {"filename": name + ".kicad_pro", "version": 3},
            "net_settings": {"classes": [{
                "name": "Default", "priority": 2147483647, "clearance": C, "track_width": W,
                "via_diameter": TH_D, "via_drill": TH_H, "microvia_diameter": MV_D, "microvia_drill": MV_H,
                "diff_pair_gap": 0.1, "diff_pair_width": 0.1, "diff_pair_via_gap": 0.1}],
                "meta": {"version": 4}},
        }
        with open(os.path.join(OUT, name + ".kicad_pro"), "w") as fh:
            json.dump(project, fh, indent=2, sort_keys=True)
            fh.write("\n")
        with open(os.path.join(OUT, name + ".result.json"), "w") as fh:
            json.dump(self.result, fh, indent=1, sort_keys=True)
            fh.write("\n")
        return name


def main(argv):
    pcbnew.KIID.SeedGenerator(1)
    lib = kicad_lib_dir()
    for n in [int(a) for a in argv] or sorted(STACKUPS):
        print("%d layers" % n, flush=True)
        st = Study(n)
        res = st.run(lib)
        st.fill_ground()
        name = st.save()
        print("  %s: escaped %s; failed %d; via-in-pad %d; power links failed %d" % (
            name, res["escaped"], len(res["failed"]), len(res["via_in_pad"]), len(res["power_links_failed"])),
            flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
