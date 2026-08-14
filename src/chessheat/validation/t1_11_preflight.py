import json
import chess
import chess.pgn
import io
from chessheat.validation.harness import ValidationHarness, extract_all_signatures
from chessheat.temporal import build_temporal_ledger_from_pgn

def get_sig_from_fen(fen, sig_str, san=None):
    b = chess.Board(fen)
    if san:
        b.push_san(san)
    sigs = extract_all_signatures(b)
    for sig in sigs:
        if str(sig) == sig_str:
            return sig
    return None

def make_pgn(fen, history):
    b = chess.Board(fen)
    game = chess.pgn.Game()
    game.setup(b)
    node = game
    for san in history:
        move = b.parse_san(san)
        node = node.add_variation(move)
        b.push(move)
    return str(game)

def run_preflight():
    with open("docs/research/t1/t1_11_manifest.json", "r") as f:
        manifest = json.load(f)

    preflight_results = []
    
    for item in manifest:
        q_id = item["fixture_id"]
        fen = item["pre_move_fen"]
        played_move_san = item["played_move_san"]
        reqs = item["required_evidence_families"]
        
        pred_sig = get_sig_from_fen(fen, item["predecessor_signature"])
        succ_sig = get_sig_from_fen(fen, item["successor_signature"], played_move_san)
        
        result = {
            "fixture_id": q_id,
            "hypothesis": item["human_hypothesis"],
            "pre_move_fen": fen,
            "played_move_san": played_move_san,
            "e_str": item["predecessor_signature"],
            "f_str": item["successor_signature"],
            "required_evidence_families": reqs,
            "eligibility_status": "PASS",
            "dimension_preflight_status": "PASS",
            "error_msg": None,
            "m_11": [], "m_10": [], "m_01": [], "m_00": [],
            "dimension_evidence": {}
        }
        
        if pred_sig is None and item["predecessor_signature"] is not None:
            result["eligibility_status"] = "FAIL"
            result["dimension_preflight_status"] = "FAIL"
            result["error_msg"] = "Could not resolve predecessor signature"
            preflight_results.append(result)
            continue
            
        if succ_sig is None:
            result["eligibility_status"] = "FAIL"
            result["dimension_preflight_status"] = "FAIL"
            result["error_msg"] = "Could not resolve successor signature"
            preflight_results.append(result)
            continue
            
        try:
            m11, m10, m01, m00 = ValidationHarness.preflight_fixture(
                fen, played_move_san, pred_sig, succ_sig
            )
            result["m_11"] = m11
            result["m_10"] = m10
            result["m_01"] = m01
            result["m_00"] = m00
            
            n11, n10, n01, n00 = len(m11), len(m10), len(m01), len(m00)
            
            if q_id == "Q4":
                if n01 == 0:
                    result["dimension_preflight_status"] = "FAIL"
                else:
                    result["dimension_preflight_status"] = "PRECONDITIONS_PASS_PENDING_ENGINE"
            elif q_id == "Q5":
                pgn = make_pgn("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2", item["history"])
                ledger = build_temporal_ledger_from_pgn(pgn)
                evt = None
                for k, v in ledger.events.items():
                    if str(k) == item["successor_signature"]:
                        evt = v
                        break
                if evt:
                    intervals = evt.active_intervals
                    duration = sum((end if end is not None else ledger.total_plies) - start for start, end in intervals)
                    result["dimension_evidence"] = {
                        "intervals": [f"{s}-{e if e else 'ongoing'}" for s, e in intervals],
                        "computed_duration": duration,
                        "right_censored": evt.is_right_censored
                    }
                else:
                    result["dimension_preflight_status"] = "FAIL"
            elif q_id == "Q6":
                if not (n01 + n00 == 0 and (n11 + n10) > 1):
                    result["dimension_preflight_status"] = "FAIL"
            elif q_id == "Q7":
                b = chess.Board(fen)
                sig_e = get_sig_from_fen(fen, item["predecessor_signature"])
                sig_f = get_sig_from_fen(fen, item["successor_signature"], played_move_san)
                c_m11, c_m10, c_m01, c_m00 = ValidationHarness.preflight_fixture(fen, played_move_san, sig_e, sig_f)
                result["dimension_evidence"] = {
                    "constituent_pairs": [{"e": item["predecessor_signature"], "f": item["successor_signature"]}],
                    "bundle_equality": {
                        "m11": c_m11, "m10": c_m10, "m01": c_m01, "m00": c_m00
                    }
                }
            elif q_id in ["Q8", "Q9"]:
                pred_sqs = [pred_sig.attacker.square, pred_sig.target_square]
                succ_sqs = [succ_sig.attacker.square, succ_sig.target_square]
                shared = list(set(pred_sqs).intersection(set(succ_sqs)))
                result["dimension_evidence"] = {
                    "implicated_squares_e": pred_sqs,
                    "implicated_squares_f": succ_sqs,
                    "intersection": shared
                }
                if q_id == "Q8" and len(shared) == 0: result["dimension_preflight_status"] = "FAIL"
                if q_id == "Q9" and len(shared) > 0: result["dimension_preflight_status"] = "FAIL"
            elif q_id == "Q10":
                pgn = make_pgn("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", item["history"])
                ledger = build_temporal_ledger_from_pgn(pgn)
                evt = None
                for k, v in ledger.events.items():
                    if str(k) == item["successor_signature"]:
                        evt = v
                        break
                if evt:
                    intervals = evt.active_intervals
                    result["dimension_evidence"] = {
                        "intervals": [f"{s}-{e if e else 'ongoing'}" for s, e in intervals],
                        "reappearance_boolean": len(intervals) > 1
                    }
                else:
                    result["dimension_preflight_status"] = "FAIL"
            elif q_id == "Q11":
                result["dimension_preflight_status"] = "PRECONDITIONS_PASS_PENDING_ENGINE"
            elif q_id == "Q13":
                fen_base = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                pgn_a = make_pgn(fen_base, item["twin_history"]["moves_a"])
                pgn_b = make_pgn(fen_base, item["twin_history"]["moves_b"])
                b_a = chess.Board(fen_base)
                for m in item["twin_history"]["moves_a"]: b_a.push_san(m)
                b_b = chess.Board(fen_base)
                for m in item["twin_history"]["moves_b"]: b_b.push_san(m)
                
                la = build_temporal_ledger_from_pgn(pgn_a)
                lb = build_temporal_ledger_from_pgn(pgn_b)
                
                evt_a = None
                for k, v in la.events.items():
                    if str(k) == item["successor_signature"]:
                        evt_a = v
                        break
                evt_b = None
                for k, v in lb.events.items():
                    if str(k) == item["successor_signature"]:
                        evt_b = v
                        break
                        
                result["dimension_evidence"] = {
                    "fen_a": b_a.fen(),
                    "fen_b": b_b.fen(),
                    "lifecycle_differences": f"History A: {len(evt_a.active_intervals) if evt_a else 0} intervals. History B: {len(evt_b.active_intervals) if evt_b else 0} intervals."
                }
                if b_a.fen() != b_b.fen():
                    result["dimension_preflight_status"] = "FAIL"
            elif q_id == "Q14":
                twin = item["twin_fixture"]
                pred_twin = get_sig_from_fen(twin["fen"], twin["e_str_part"])
                succ_twin = get_sig_from_fen(twin["fen"], twin["f_str_part"], twin["played_move_san"])
                tm11, tm10, tm01, tm00 = ValidationHarness.preflight_fixture(twin["fen"], twin["played_move_san"], pred_twin, succ_twin)
                
                def reflect_san(san):
                    import re
                    # very naive mapping for this specific fixture
                    for c1, c2 in [('a','h'), ('b','g'), ('c','f'), ('d','e')]:
                        if c1 in san: return san.replace(c1, c2)
                        if c2 in san: return san.replace(c2, c1)
                    return san
                
                result["dimension_evidence"] = {
                    "mapped_partitions": {
                        "m11": tm11, "m10": tm10, "m01": tm01, "m00": tm00
                    },
                    "mapping": "X-axis reflection"
                }
                if len(m11) != len(tm11) or len(m10) != len(tm10):
                    result["dimension_preflight_status"] = "FAIL"
                else:
                    result["dimension_preflight_status"] = "PRECONDITIONS_PASS_PENDING_ENGINE"
            elif q_id == "Q15":
                b1 = chess.Board(fen)
                b1.turn = chess.BLACK
                b1.clear_stack()
                
                sigs_w = extract_all_signatures(chess.Board(fen))
                sigs_b = extract_all_signatures(b1)
                
                tuple_str = item["successor_signature"]
                found_w = any(str(s) == tuple_str for s in sigs_w)
                found_b = any(str(s) == tuple_str for s in sigs_b)
                
                result["dimension_evidence"] = {
                    "fen_white_to_move": fen,
                    "fen_black_to_move": b1.fen(),
                    "tuple_present_when_white_to_move": found_w,
                    "tuple_present_when_black_to_move": found_b
                }
                if not (found_b and not found_w):
                    result["dimension_preflight_status"] = "FAIL"
                
        except Exception as e:
            result["eligibility_status"] = "FAIL"
            result["dimension_preflight_status"] = "FAIL"
            result["error_msg"] = str(e)
            
        preflight_results.append(result)
        
    with open("docs/research/t1/t1_11_structural_preflight.json", "w") as f:
        json.dump({
            "corpus_status": "FROZEN PENDING T1.11.2 EXECUTION SEAL",
            "fixtures": preflight_results
        }, f, indent=2)

if __name__ == "__main__":
    run_preflight()
