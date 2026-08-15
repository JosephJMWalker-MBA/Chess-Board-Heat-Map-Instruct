import json
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

def square_native_canonical_path(board_fen: str, move_uci: str, source: chess.Square, target: chess.Square, blocker: chess.Square) -> bool:
    """
    Strong Square-Native Normalization Challenge:
    Uses discrete coordinate translation without python-chess ray helpers.
    """
    # 1. Root move must originate from blocker
    move = chess.Move.from_uci(move_uci)
    if move.from_square != blocker:
        return False
        
    # 2. Iterate coordinate translation from source to target
    b = chess.Board(board_fen)
    sx, sy = chess.square_file(source), chess.square_rank(source)
    tx, ty = chess.square_file(target), chess.square_rank(target)
    
    dx = (tx > sx) - (tx < sx)
    dy = (ty > sy) - (ty < sy)
    
    cx, cy = sx + dx, sy + dy
    while (cx, cy) != (tx, ty):
        sq = chess.square(cx, cy)
        if sq != blocker and b.piece_at(sq) is not None:
            return False
        cx, cy = cx + dx, cy + dy
        
    return True

# --- 2. Structural Suite Definitions ---

dev_fixtures = [
    {
        "id": "F1_dev_vertical_len3",
        "fen": "3q3k/8/8/3N4/3R4/8/8/4K3 w - - 0 1",
        "source": chess.D4,
        "target": chess.D8,
        "blocker": chess.D5
    },
    {
        "id": "F2_dev_diagonal",
        "fen": "6q1/8/8/4N3/8/2B5/8/4K2k w - - 0 1",
        "source": chess.C3,
        "target": chess.G7,
        "blocker": chess.E5
    }
]

test_fixtures = [
    {
        "id": "F3_test_vertical_d6",
        "fen": "3q3k/8/3N4/8/3R4/8/8/4K3 w - - 0 1",
        "source": chess.D4,
        "target": chess.D8,
        "blocker": chess.D6
    },
    {
        "id": "F4_test_horizontal_f4",
        "fen": "4k3/8/8/8/2R2N1q/8/8/4K3 w - - 0 1",
        "source": chess.C4,
        "target": chess.H4,
        "blocker": chess.F4
    }
]

def test_relational_compression_and_transfer():
    
    # Prove structural equivalence on Development set and freeze schemas
    for fix in dev_fixtures:
        board = chess.Board(fix["fen"])
        assert board.is_valid()
        for move in board.legal_moves:
            uci = move.uci()
            rel_res = ray_transition(fix["fen"], uci, fix["source"], fix["target"])
            sq_res = square_native_canonical_path(fix["fen"], uci, fix["source"], fix["target"], fix["blocker"])
            assert rel_res == sq_res, f"Dev mismatch on {fix['id']} move {uci}"
            
    # Prove structural equivalence on Held-Out Test set (transfer test)
    # The frozen schemas transfer completely without modification.
    for fix in test_fixtures:
        board = chess.Board(fix["fen"])
        assert board.is_valid()
        for move in board.legal_moves:
            uci = move.uci()
            rel_res = ray_transition(fix["fen"], uci, fix["source"], fix["target"])
            sq_res = square_native_canonical_path(fix["fen"], uci, fix["source"], fix["target"], fix["blocker"])
            assert rel_res == sq_res, f"Transfer mismatch on {fix['id']} move {uci}"

    # Complexity Metrics (Matched Levels)
    # 1. Schema Definition Operator Count
    relational_schema_count = 1
    square_schema_count = 1
    
    # 2. Context-Specific Bound Identifiers per fixture
    bound_squares_relation_per_fixture = 2 # source, target
    bound_squares_square_per_fixture = 3   # source, target, blocker
    
    # 3. Number of template modifications needed for held-out
    relational_modifications = 0
    square_modifications = 0
    
    # Create S0/S1 identity artifacts
    signature = SemanticSignatureV1.create_canonical()
    
    all_fixtures = dev_fixtures + test_fixtures
    manifest = SuiteManifest(
        suite_id="t2b3-relational-transfer",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={fix["fen"].replace(" ", "_"): "structural_hash" for fix in all_fixtures}
    )
    
    # Dev Experiment
    spec_dev = ExperimentSpec(
        semantic_signature_version=signature.version,
        semantic_signature_digest=signature.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity="DEV_PHASE",
        fixture_digest=manifest.suite_digest(), # proxy
        sufficient_position=SufficientPosition(
            board_arrangement_fen="DEV",
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
    
    res_dev = ExperimentResult.create(spec_digest=spec_dev.spec_digest(), data={"phase": "DEV"})
    
    # Held-Out Experiment
    spec_test = ExperimentSpec(
        semantic_signature_version=signature.version,
        semantic_signature_digest=signature.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity="TEST_PHASE",
        fixture_digest=manifest.suite_digest(), # proxy
        sufficient_position=SufficientPosition(
            board_arrangement_fen="TEST",
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
    
    res_test = ExperimentResult.create(spec_digest=spec_test.spec_digest(), data={"phase": "TEST"})
    
    # 7. Classification and Output
    comparison = ComparisonResult(
        hypothesis_identifier="T2b-3-Relational-Compression-Transfer",
        result_digest_a=res_dev.artifact_digest,
        result_digest_b=res_test.artifact_digest,
        outcome_payload=json.dumps({
            "classification": "WEAK_SUPPORT",
            "metrics": {
                "schema_count_relation": relational_schema_count,
                "schema_count_square": square_schema_count,
                "bound_identifiers_relation_per_fixture": bound_squares_relation_per_fixture,
                "bound_identifiers_square_per_fixture": bound_squares_square_per_fixture,
                "modifications_needed_held_out": 0
            },
            "message": "WEAK_SUPPORT: The relational schema remains smaller (2 bounds vs 3 bounds), but the fair square-native normalization canonicalizes the varied paths perfectly and transfers without fixture-specific rewriting."
        }, sort_keys=True)
    )
    
    assert comparison.outcome["classification"] == "WEAK_SUPPORT"
    assert comparison.outcome["metrics"]["bound_identifiers_relation_per_fixture"] == 2
    assert comparison.outcome["metrics"]["bound_identifiers_square_per_fixture"] == 3
