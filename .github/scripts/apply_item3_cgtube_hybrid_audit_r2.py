#!/usr/bin/env python3
"""Apply the bounded item3 C-G-TUBE hybrid audit-r2 source revision.

This script is control-plane material on main.  It modifies exactly four files
in a checkout fixed at 3a025346da89818273dc22616e6c7995478f25bb.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_SHA = "3a025346da89818273dc22616e6c7995478f25bb"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected exactly one source block, found {text.count(old)}")
    return text.replace(old, new, 1)


def patch_pilot(root: Path) -> None:
    path = root / "c_g_tube_pilot.py"
    text = path.read_text()
    old = '''            cross_lo, cross_hi, _ = identity_gprime(
                kern, a, b, lam,
                partitions=CONFIG["center_refined_t_partition_count"],
                tol=CONFIG["center_tol"],
                depth=CONFIG["center_int_depth"],
                limit=CONFIG["center_int_limit"],
                keep_pieces=False)
            payload.update({
                "crosscheck_method": cross_method,
                "cross_partition_count":
                    CONFIG["center_refined_t_partition_count"],
                "cross_depth_limit": CONFIG["center_int_depth"],
                "cross_evaluation_limit": CONFIG["center_int_limit"],
                "Gprime_cross_ball": [str(cross_lo), str(cross_hi)],
                "cross_negative": bool(cross_hi < 0),
            })
'''
    new = '''            cross_lo, cross_hi, cross_pieces = identity_gprime(
                kern, a, b, lam,
                partitions=CONFIG["center_refined_t_partition_count"],
                tol=CONFIG["center_tol"],
                depth=CONFIG["center_int_depth"],
                limit=CONFIG["center_int_limit"],
                keep_pieces=True)
            payload.update({
                "crosscheck_method": cross_method,
                "cross_partition_count":
                    CONFIG["center_refined_t_partition_count"],
                "cross_depth_limit": CONFIG["center_int_depth"],
                "cross_evaluation_limit": CONFIG["center_int_limit"],
                "cross_identity_pieces": cross_pieces,
                "Gprime_cross_ball": [str(cross_lo), str(cross_hi)],
                "cross_negative": bool(cross_hi < 0),
            })
'''
    text = replace_once(text, old, new, "pilot refined identity")
    old = '''                "weighted_ball": [str(arb(weighted.lower())),
                                  str(arb(weighted.upper()))],
'''
    new = '''                # Diagnostic only.  The checker reconstructs this term
                # independently from t_a, t_b and Frr_ball.
                "weighted_ball": [str(arb(weighted.lower())),
                                  str(arb(weighted.upper()))],
'''
    text = replace_once(text, old, new, "pilot weighted_ball annotation")
    path.write_text(text)


def patch_checker(root: Path) -> None:
    path = root / "c_g_tube_checker.py"
    text = path.read_text()
    text = replace_once(
        text,
        '    "neg_spot_sign_flip": 1,\n',
        '    "neg_spot_sign_flip": 1,\n'
        '    "neg_center_spot_balls_tamper": 1,\n'
        '    "neg_center_spot_piece_missing": 1,\n'
        '    "neg_center_spot_piece_sign_flip": 1,\n',
        "checker control registry",
    )
    old = '''def identity_record_negative(rec: dict) -> bool:
    n = rec.get("partition_count")
    if not isinstance(n, int) or n != CONFIG["center_t_partition_count"]:
        die(f"CENTER IDENTITY PARTITION MISMATCH at {rec.get('a')}..{rec.get('b')}", 1)
    pieces = rec.get("identity_pieces")
    if not isinstance(pieces, list) or len(pieces) != n:
        die("CENTER IDENTITY PIECE COUNT MISMATCH", 1)
    dt = qa(Fr(1, n))
    total_lo, total_hi = arb(0), arb(0)
    for i, piece in enumerate(pieces):
        ta, tb = Fr(piece["t_a"]), Fr(piece["t_b"])
        if ta != Fr(i, n) or tb != Fr(i + 1, n):
            die("CENTER IDENTITY t-PARTITION MISMATCH", 1)
        fball = piece.get("Frr_ball")
        if not isinstance(fball, list) or len(fball) != 2:
            die("CENTER IDENTITY Frr BALL MISSING", 1)
        flo, fhi = endpoint_lo(fball[0]), endpoint_hi(fball[1])
        if bool(flo > fhi):
            die("CENTER IDENTITY Frr BALL REVERSED", 1)
        plo, phi = weighted_product_bounds(ta, tb, flo, fhi)
        total_lo = arb((total_lo + plo * dt).lower())
        total_hi = arb((total_hi + phi * dt).upper())
    stored = rec.get("G_prime_ball")
    if not isinstance(stored, list) or len(stored) != 2:
        die("CENTER IDENTITY SUMMARY BALL MISSING", 1)
    stored_lo, stored_hi = endpoint_lo(stored[0]), endpoint_hi(stored[1])
    if bool(stored_hi < total_lo) or bool(total_hi < stored_lo):
        die("CENTER IDENTITY SUMMARY DISJOINT FROM RECONSTRUCTION", 1)
    negative = bool(total_hi < 0)
    if negative != bool(rec.get("negative")):
        die("CENTER IDENTITY NEGATIVITY MISMATCH", 1)
    return negative
'''
    new = '''def identity_piece_bounds(pieces, n: int, label: str) -> tuple[arb, arb]:
    if not isinstance(pieces, list) or len(pieces) != n:
        die(f"{label} PIECE COUNT MISMATCH", 1)
    dt = qa(Fr(1, n))
    total_lo, total_hi = arb(0), arb(0)
    for i, piece in enumerate(pieces):
        if not isinstance(piece, dict):
            die(f"{label} PIECE IS NOT AN OBJECT", 1)
        try:
            ta, tb = Fr(piece["t_a"]), Fr(piece["t_b"])
        except (KeyError, TypeError, ValueError) as exc:
            die(f"{label} MALFORMED t-PARTITION: {exc}", 1)
        if ta != Fr(i, n) or tb != Fr(i + 1, n):
            die(f"{label} t-PARTITION MISMATCH", 1)
        fball = piece.get("Frr_ball")
        if not isinstance(fball, list) or len(fball) != 2:
            die(f"{label} Frr BALL MISSING", 1)
        flo, fhi = endpoint_lo(fball[0]), endpoint_hi(fball[1])
        if bool(flo > fhi):
            die(f"{label} Frr BALL REVERSED", 1)
        plo, phi = weighted_product_bounds(ta, tb, flo, fhi)
        total_lo = arb((total_lo + plo * dt).lower())
        total_hi = arb((total_hi + phi * dt).upper())
    return total_lo, total_hi


def require_summary_intersects(stored, total_lo: arb, total_hi: arb,
                               label: str) -> None:
    if not isinstance(stored, list) or len(stored) != 2:
        die(f"{label} SUMMARY BALL MISSING", 1)
    stored_lo, stored_hi = endpoint_lo(stored[0]), endpoint_hi(stored[1])
    if bool(stored_lo > stored_hi):
        die(f"{label} SUMMARY BALL REVERSED", 1)
    if bool(stored_hi < total_lo) or bool(total_hi < stored_lo):
        die(f"{label} SUMMARY DISJOINT FROM RECONSTRUCTION", 1)


def identity_record_bounds(rec: dict) -> tuple[bool, arb, arb]:
    n = rec.get("partition_count")
    if not isinstance(n, int) or n != CONFIG["center_t_partition_count"]:
        die(f"CENTER IDENTITY PARTITION MISMATCH at {rec.get('a')}..{rec.get('b')}", 1)
    total_lo, total_hi = identity_piece_bounds(
        rec.get("identity_pieces"), n, "CENTER IDENTITY")
    require_summary_intersects(
        rec.get("G_prime_ball"), total_lo, total_hi, "CENTER IDENTITY")
    negative = bool(total_hi < 0)
    if negative != bool(rec.get("negative")):
        die("CENTER IDENTITY NEGATIVITY MISMATCH", 1)
    return negative, total_lo, total_hi


def identity_record_negative(rec: dict) -> bool:
    return identity_record_bounds(rec)[0]
'''
    text = replace_once(text, old, new, "checker identity reconstruction")
    text = replace_once(
        text,
        '''    cells_ok = True
    unresolved_count = 0
    for i in range(n_cells):
''',
        '''    cells_ok = True
    unresolved_count = 0
    center_identity_hulls: dict[int, tuple[arb, arb]] = {}
    for i in range(n_cells):
''',
        "checker center hull initialization",
    )
    old = '''        leaves = []
        for sub in rec.get("sub", []):
            if cell_record_negative(sub, i):
                leaves.append((Fr(sub["a"]), Fr(sub["b"])))
        tiled = exact_tile(leaves, a_exp, b_exp)
'''
    new = '''        leaves = []
        center_bounds = []
        for sub in rec.get("sub", []):
            if i < CONFIG["center_identity_cell_count"]:
                if sub.get("method") != "center_identity":
                    die(f"NON-IDENTITY RECORD IN CENTER CELL {i}", 1)
                negative, bound_lo, bound_hi = identity_record_bounds(sub)
            else:
                negative = cell_record_negative(sub, i)
                bound_lo = bound_hi = None
            if negative:
                leaves.append((Fr(sub["a"]), Fr(sub["b"])))
                if bound_lo is not None:
                    center_bounds.append((bound_lo, bound_hi))
        tiled = exact_tile(leaves, a_exp, b_exp)
        if tiled and i < CONFIG["center_identity_cell_count"]:
            if not center_bounds:
                die(f"CENTER CELL {i} HAS NO RECONSTRUCTED LEAF BOUNDS", 1)
            hull_lo, hull_hi = center_bounds[0]
            for bound_lo, bound_hi in center_bounds[1:]:
                if bool(bound_lo < hull_lo):
                    hull_lo = bound_lo
                if bool(bound_hi > hull_hi):
                    hull_hi = bound_hi
            center_identity_hulls[i] = (
                arb(hull_lo.lower()), arb(hull_hi.upper()))
'''
    text = replace_once(text, old, new, "checker center cell hull")
    old = '''        id_lo = endpoint_lo(rec["Gprime_identity_ball"][0])
        id_hi = endpoint_hi(rec["Gprime_identity_ball"][1])
        identity_negative = bool(id_hi < 0)
        method = rec.get("crosscheck_method")

        if i < CONFIG["center_identity_cell_count"]:
            meta_ok = meta_ok and method == "identity_refined"
            meta_ok = meta_ok and (
                rec.get("cross_partition_count") == CONFIG["center_refined_t_partition_count"] and
                rec.get("cross_depth_limit") == CONFIG["center_int_depth"] and
                rec.get("cross_evaluation_limit") == CONFIG["center_int_limit"]
            )
            cross_ball = rec.get("Gprime_cross_ball")
            if not isinstance(cross_ball, list) or len(cross_ball) != 2:
                die("REFINED IDENTITY SPOT BALL MISSING", 1)
            cross_lo, cross_hi = endpoint_lo(cross_ball[0]), endpoint_hi(cross_ball[1])
            tiling_complete = None
            terminal_unresolved = None
        elif i in adaptive_indices:
'''
    new = '''        stored_identity = rec.get("Gprime_identity_ball")
        if not isinstance(stored_identity, list) or len(stored_identity) != 2:
            die("SPOT IDENTITY BALL MISSING", 1)
        method = rec.get("crosscheck_method")

        if i < CONFIG["center_identity_cell_count"]:
            meta_ok = meta_ok and method == "identity_refined"
            meta_ok = meta_ok and (
                rec.get("cross_partition_count") == CONFIG["center_refined_t_partition_count"] and
                rec.get("cross_depth_limit") == CONFIG["center_int_depth"] and
                rec.get("cross_evaluation_limit") == CONFIG["center_int_limit"]
            )
            if i not in center_identity_hulls:
                die(f"CENTER SPOT {i} HAS NO CERTIFIED CELL RECONSTRUCTION", 1)
            id_lo, id_hi = center_identity_hulls[i]
            require_summary_intersects(
                stored_identity, id_lo, id_hi,
                "CENTER SPOT CELL-LINKED IDENTITY")
            n_refined = CONFIG["center_refined_t_partition_count"]
            cross_lo, cross_hi = identity_piece_bounds(
                rec.get("cross_identity_pieces"), n_refined,
                "REFINED IDENTITY SPOT")
            require_summary_intersects(
                rec.get("Gprime_cross_ball"), cross_lo, cross_hi,
                "REFINED IDENTITY SPOT")
            tiling_complete = True
            terminal_unresolved = 0
        else:
            id_lo = endpoint_lo(stored_identity[0])
            id_hi = endpoint_hi(stored_identity[1])

        identity_negative = bool(id_hi < 0)

        if i < CONFIG["center_identity_cell_count"]:
            pass
        elif i in adaptive_indices:
'''
    text = replace_once(text, old, new, "checker center spot verification")
    text = replace_once(
        text,
        '            "Gprime_identity_ball": rec["Gprime_identity_ball"],\n',
        '            "Gprime_identity_ball_stored": rec["Gprime_identity_ball"],\n'
        '            "Gprime_identity_ball_reconstructed": [str(id_lo), str(id_hi)],\n',
        "checker spot output",
    )
    path.write_text(text)


def patch_controls(root: Path) -> None:
    path = root / "run_controls.py"
    text = path.read_text()
    text = replace_once(
        text,
        '    "neg_spot_sign_flip": 1,\n',
        '    "neg_spot_sign_flip": 1,\n'
        '    "neg_center_spot_balls_tamper": 1,\n'
        '    "neg_center_spot_piece_missing": 1,\n'
        '    "neg_center_spot_piece_sign_flip": 1,\n',
        "controls registry",
    )
    old = '''def center_identity_leaf(a: Fr, b: Fr, *, positive: bool = False) -> dict:
    n = CONFIG["center_t_partition_count"]
    fball = ["0.008", "0.012"] if positive else ["-0.012", "-0.008"]
    summary = ["0.003", "0.007"] if positive else ["-0.007", "-0.003"]
    pieces = [
        {"t_a": str(Fr(i, n)), "t_b": str(Fr(i + 1, n)),
         "Frr_ball": fball}
        for i in range(n)
    ]
'''
    new = '''def identity_pieces(n: int, *, positive: bool = False) -> list[dict]:
    fball = ["0.008", "0.012"] if positive else ["-0.012", "-0.008"]
    return [
        {"t_a": str(Fr(i, n)), "t_b": str(Fr(i + 1, n)),
         "Frr_ball": fball}
        for i in range(n)
    ]


def center_identity_leaf(a: Fr, b: Fr, *, positive: bool = False) -> dict:
    n = CONFIG["center_t_partition_count"]
    summary = ["0.003", "0.007"] if positive else ["-0.007", "-0.003"]
    pieces = identity_pieces(n, positive=positive)
'''
    text = replace_once(text, old, new, "controls identity helper")
    text = replace_once(
        text,
        '''          missing_spot_leaf: bool = False,
          flip_spot_leaf: bool = False) -> None:
''',
        '''          missing_spot_leaf: bool = False,
          flip_spot_leaf: bool = False,
          center_spot_balls_tamper: bool = False,
          center_spot_piece_missing: bool = False,
          center_spot_piece_sign_flip: bool = False) -> None:
''',
        "controls synth signature",
    )
    old = '''        if index < center_count:
            base.update({
                "crosscheck_method": "identity_refined",
                "cross_partition_count":
                    CONFIG["center_refined_t_partition_count"],
                "cross_depth_limit": CONFIG["center_int_depth"],
                "cross_evaluation_limit": CONFIG["center_int_limit"],
                "Gprime_cross_ball": ["-0.011", "-0.009"],
                "cross_negative": True,
            })
'''
    new = '''        if index < center_count:
            refined_n = CONFIG["center_refined_t_partition_count"]
            refined_pieces = identity_pieces(
                refined_n, positive=center_spot_piece_sign_flip)
            if center_spot_piece_missing:
                refined_pieces = refined_pieces[:-1]
            identity_ball = (["-0.002", "-0.001"]
                             if center_spot_balls_tamper
                             else ["-0.007", "-0.003"])
            cross_ball = (["-0.002", "-0.001"]
                          if center_spot_balls_tamper
                          else ["-0.007", "-0.003"])
            base["Gprime_identity_ball"] = identity_ball
            base.update({
                "crosscheck_method": "identity_refined",
                "cross_partition_count": refined_n,
                "cross_depth_limit": CONFIG["center_int_depth"],
                "cross_evaluation_limit": CONFIG["center_int_limit"],
                "cross_identity_pieces": refined_pieces,
                "Gprime_cross_ball": cross_ball,
                "cross_negative": not center_spot_piece_sign_flip,
            })
'''
    text = replace_once(text, old, new, "controls center spot")
    text = replace_once(
        text,
        '        "neg_spot_sign_flip": {"flip_spot_leaf": True},\n',
        '        "neg_spot_sign_flip": {"flip_spot_leaf": True},\n'
        '        "neg_center_spot_balls_tamper": {"center_spot_balls_tamper": True},\n'
        '        "neg_center_spot_piece_missing": {"center_spot_piece_missing": True},\n'
        '        "neg_center_spot_piece_sign_flip": {"center_spot_piece_sign_flip": True},\n',
        "controls specs",
    )
    path.write_text(text)


def patch_readme(root: Path) -> None:
    (root / "README.md").write_text('''# item3_center_connection/c_g_tube — Actions clean-room hybrid pilot（ソースのみ）

役割: 単一 λ スライス（λ=118/25, r∈[1/64,11/256]）の一意根 pilot。
項目3全体の証明書ではない。左端8セルを中心恒等式、残り48セルを
Taylor 包含で処理する二領域 hybrid C-G-TUBE である。

このディレクトリはソース・設定・対照・checker・workflow のみを含む。
計算結果（JSON/JSONL/certificate/checkpoint/manifest 実体）は同梱しない。
全成果物は Actions 内で endpoint → 56 hybrid cells
（8 center-identity + 48 outer-Taylor）→ spot crosschecks
[0: refined identity pieces, 18: adaptive Taylor, 37/55: Taylor]
→ controls → checker/finalize → manifest の順にゼロから再生成される。

checker の trust boundary は原始 Arb 評価ボールである。Taylor 不等式、
中心恒等式の区間 Riemann 和、被覆、鎖 SHA、型・phase・件数、spot 交差は
保存された原始ボールから独立再構成する。spot 0 の base identity は
cells 鎖の同一セル再構成値に結合し、refined identity は256分割の
Frr_ball ピースから再構成する。identity_pieces 内の weighted_ball は
診断表示専用であり、checker は t_a, t_b, Frr_ball から再計算する。

状態遷移: UNVERIFIED_DELIVERY →（SHA照合）VERIFIED_DELIVERY →
SOURCE_CANDIDATE →（独立静的監査 PASS）AUDITED_SOURCE →
（固定SHAの Actions全再生成 PASS と成果物照合）CERTIFIED_SINGLE_SLICE。

依存: vendor 核2本を config.json にファイル別パスと SHA でピン留めする。
F 核は CERTIFICATES/prolate/item2_circle/vendor/、Frr 核は
CERTIFICATES/prolate/item3_center_connection/vendor/。不一致・欠落は exit 2。
較正の根拠は PR #15 の schema-v2 較正記録（セル幅 1/2048）を参照する。
''')


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_item3_cgtube_hybrid_audit_r2.py CHECKOUT_ROOT")
    checkout = Path(sys.argv[1]).resolve()
    root = checkout / "CERTIFICATES/prolate/item3_center_connection/c_g_tube"
    patch_pilot(root)
    patch_checker(root)
    patch_controls(root)
    patch_readme(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
