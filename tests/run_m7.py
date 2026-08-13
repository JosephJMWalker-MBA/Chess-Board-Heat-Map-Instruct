import json
import chess
from chessheat.geometry import extract_geometry, compute_geometry_delta

def main():
    with open("tests/fixtures/validation_m5.json", "r") as f:
        fixtures = json.load(f)

    m7_fixtures = [f for f in fixtures if f["fixture_id"].startswith(("F3", "F4", "F6"))]

    report = {}

    for fx in m7_fixtures:
        fid = fx["fixture_id"]
        fen = fx["fen"]

        b = chess.Board(fen)
        g_before = extract_geometry(b)

        report[fid] = {"moves": {}}

        for move in b.generate_legal_moves():
            b_copy = b.copy()
            b_copy.push(move)
            g_after = extract_geometry(b_copy)

            delta = compute_geometry_delta(g_before, g_after)

            report[fid]["moves"][move.uci()] = {
                "appeared_attacks": [d.model_dump() for d in delta.appeared_attacks],
                "disappeared_attacks": [d.model_dump() for d in delta.disappeared_attacks],
                "appeared_defenses": [d.model_dump() for d in delta.appeared_defenses],
                "disappeared_defenses": [d.model_dump() for d in delta.disappeared_defenses],
                "appeared_rays": [d.model_dump() for d in delta.appeared_rays],
                "disappeared_rays": [d.model_dump() for d in delta.disappeared_rays],
                "mobility_gained": [(p.model_dump(), sq) for p, sq in delta.mobility_gained],
                "mobility_lost": [(p.model_dump(), sq) for p, sq in delta.mobility_lost],
            }

    with open("tests/fixtures/results_m7.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()
