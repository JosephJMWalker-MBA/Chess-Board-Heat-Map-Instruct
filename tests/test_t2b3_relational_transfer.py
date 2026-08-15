import json
import hashlib
import pytest
import chess
from typing import List, Callable, Tuple

from chessheat.experiment import ExperimentSpec, ExperimentResult, SuiteManifest, SuiteKind, ComparisonResult
from chessheat.semantics import SemanticSignatureV1, SufficientPosition

# --- 1. Frozen Representation Grammars ---

def ray_transition(board_fen: str, move_uci: str, source: chess.Square, target: chess.Square) -> bool:
    """
    Relational Schema (Corrected): Mechanically evaluates if ray from source to target 
    changes from blocked to enabled after the root move, for the specific source piece.
    """
    b = chess.Board(board_fen)
    
    # Must be blocked initially BY THE PREREGISTERED SOURCE PIECE
    if target in b.attacks(source):
        return False
        
    move = chess.Move.from_uci(move_uci)
    b.push(move)
    
    # Check if enabled afterwards
    if not b.piece_at(source):
        return False
        
    return target in b.attacks(source)

def square_native_canonical_path(board_fen: str, move_uci: str, source: chess.Square, target: chess.Square) -> bool:
    """
    Strong Square-Native Normalization Challenge (Final Adversarial):
    Uses purely discrete coordinate math. Takes only source and target.
    """
    b = chess.Board(board_fen)
    sx, sy = chess.square_file(source), chess.square_rank(source)
    tx, ty = chess.square_file(target), chess.square_rank(target)
    
    # Confirm valid rank/file/diagonal
    if sx != tx and sy != ty and abs(sx - tx) != abs(sy - ty):
        return False
        
    dx = (tx > sx) - (tx < sx)
    dy = (ty > sy) - (ty < sy)
    
    between_squares = []
    cx, cy = sx + dx, sy + dy
    while (cx, cy) != (tx, ty):
        between_squares.append(chess.square(cx, cy))
        cx += dx
        cy += dy
        
    # Determine if blocked before the move
    blocked_before = any(b.piece_at(sq) is not None for sq in between_squares)
    if not blocked_before:
        return False
        
    move = chess.Move.from_uci(move_uci)
    b.push(move)
    
    # Determine if clear afterward
    clear_after = all(b.piece_at(sq) is None for sq in between_squares)
    if not clear_after:
        return False
        
    # Require source piece remains
    if b.piece_at(source) is None:
        return False
        
    return True

# --- 2. Structural Suite Definitions ---
# Note: block/empty_path annotations are fully removed.

dev_fixtures = [
    {
        "id": "F1_dev_vertical_len3",
        "fen": "3q3k/8/8/3N4/3R4/8/8/4K3 w - - 0 1",
        "source": chess.D4,
        "target": chess.D8
    },
    {
        "id": "F2_dev_diagonal",
        "fen": "6q1/8/8/4N3/8/2B5/8/4K2k w - - 0 1",
        "source": chess.C3,
        "target": chess.G7
    }
]

test_fixtures = [
    {
        "id": "F3_test_vertical_d6",
        "fen": "3q3k/8/3N4/8/3R4/8/8/4K3 w - - 0 1",
        "source": chess.D4,
        "target": chess.D8
    },
    {
        "id": "F4_test_horizontal_f4",
        "fen": "4k3/8/8/8/2R2N1q/8/8/4K3 w - - 0 1",
        "source": chess.C4,
        "target": chess.H4
    }
]

def test_relational_compression_and_transfer():
    
    # Prove structural equivalence on Development set
    for fix in dev_fixtures:
        board = chess.Board(fix["fen"])
        assert board.is_valid()
        for move in board.legal_moves:
            uci = move.uci()
            rel_res = ray_transition(fix["fen"], uci, fix["source"], fix["target"])
            sq_res = square_native_canonical_path(fix["fen"], uci, fix["source"], fix["target"])
            assert rel_res == sq_res, f"Dev mismatch on {fix['id']} move {uci}"
            
    # Prove structural equivalence on Held-Out Test set (transfer test)
    for fix in test_fixtures:
        board = chess.Board(fix["fen"])
        assert board.is_valid()
        for move in board.legal_moves:
            uci = move.uci()
            rel_res = ray_transition(fix["fen"], uci, fix["source"], fix["target"])
            sq_res = square_native_canonical_path(fix["fen"], uci, fix["source"], fix["target"])
            assert rel_res == sq_res, f"Transfer mismatch on {fix['id']} move {uci}"

    # Complexity Metrics (Matched Levels)
    relational_schema_count = 1
    square_schema_count = 1
    bound_squares_relation_per_fixture = 2 # source, target
    bound_squares_square_per_fixture = 2   # source, target
    
    # Create strictly conformant S0/S1 identity artifacts
    signature = SemanticSignatureV1.create_canonical()
    all_fixtures = dev_fixtures + test_fixtures
    
    def get_digest(fix):
        return hashlib.sha256(json.dumps(fix, sort_keys=True).encode("utf-8")).hexdigest()
        
    fixtures_dict = {
        fix["fen"].replace(" ", "_"): get_digest(fix)
        for fix in all_fixtures
    }
    
    manifest = SuiteManifest(
        suite_id="t2b3-relational-transfer",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=fixtures_dict
    )
    
    results = []
    
    for fix in all_fixtures:
        spec = ExperimentSpec(
            semantic_signature_version=signature.version,
            semantic_signature_digest=signature.signature_hash(),
            suite_identity=manifest.suite_id,
            suite_digest=manifest.suite_digest(),
            fixture_identity=fix["fen"].replace(" ", "_"),
            fixture_digest=get_digest(fix),
            sufficient_position=SufficientPosition(
                board_arrangement_fen=fix["fen"].split()[0],
                side_to_move="w",
                castling_rights="-",
                en_passant_square=None,
                halfmove_clock=0,
                fullmove_number=1,
                history_available=False,
                variant="standard"
            ),
            candidate_policy={},
            producer_identity="structural",
            instrument_config={},
            budget_config={"type": "structural", "value": 0},
            line_source="pv",
            hypothesis_identifier="T2b-3-Relational-Compression-Transfer"
        )
        res = ExperimentResult.create(spec_digest=spec.spec_digest(), data={"phase": "STRUCTURAL", "fix_id": fix["id"]})
        results.append(res)
    
    # Final Classification
    classification = "FALSIFIED"
    
    comparison = ComparisonResult(
        hypothesis_identifier="T2b-3-Relational-Compression-Transfer",
        result_digest_a=results[0].artifact_digest, # Sample Dev artifact
        result_digest_b=results[2].artifact_digest, # Sample Test artifact
        outcome_payload=json.dumps({
            "classification": classification,
            "metrics": {
                "schema_count_relation": relational_schema_count,
                "schema_count_square": square_schema_count,
                "bound_identifiers_relation_per_fixture": bound_squares_relation_per_fixture,
                "bound_identifiers_square_per_fixture": bound_squares_square_per_fixture,
                "modifications_needed_held_out": 0
            },
            "message": "FALSIFIED: The 2-parameter square-native canonicalizer transfers equivalently at exactly matched complexity (both require 1 generic schema and exactly 2 bound squares: source and target)."
        }, sort_keys=True)
    )
    
    assert comparison.outcome["classification"] == "FALSIFIED"
    assert comparison.outcome["metrics"]["bound_identifiers_relation_per_fixture"] == 2
    assert comparison.outcome["metrics"]["bound_identifiers_square_per_fixture"] == 2
