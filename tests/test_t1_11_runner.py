import os
import json
import pytest
from unittest.mock import patch, MagicMock

from chessheat.validation.t1_11_runner import run_t1_11_execution, evaluate_structural, create_execution_seal
from chessheat.engine import Score

def test_seal_rejects_id_mismatch(tmp_path):
    preflight_data = {"fixtures": [{"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"}]}
    manifest_data = [{"fixture_id": "Q2"}]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
    with pytest.raises(ValueError, match="Manifest and preflight fixture IDs do not match exactly"):
        run_t1_11_execution(str(preflight_path), str(manifest_path), str(tmp_path / "out"), "dummy")

def test_seal_rejects_fail_state(tmp_path):
    preflight_data = {"fixtures": [
        {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"},
        {"fixture_id": "Q2", "eligibility_status": "FAIL", "dimension_preflight_status": "PASS"}
    ]}
    manifest_data = [{"fixture_id": "Q1"}, {"fixture_id": "Q2"}]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
    with pytest.raises(ValueError, match="Preflight has FAIL eligibility for Q2"):
        run_t1_11_execution(str(preflight_path), str(manifest_path), str(tmp_path / "out"), "dummy")

def test_seal_rejects_unexpected_pending(tmp_path):
    preflight_data = {"fixtures": [
        {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"},
        {"fixture_id": "Q4", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"},
        {"fixture_id": "Q11", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"},
        {"fixture_id": "Q14", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"}
    ]}
    manifest_data = [{"fixture_id": "Q1"}, {"fixture_id": "Q4"}, {"fixture_id": "Q11"}, {"fixture_id": "Q14"}]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
    with pytest.raises(ValueError, match="Expected exactly Q4, Q11, Q14 to be pending engine"):
        with patch("chessheat.validation.t1_11_runner.verify_preflight_reproducibility"):
            create_execution_seal(str(manifest_path), "dummy", str(preflight_path), "dummy", str(tmp_path / "out"))

@patch("chessheat.validation.t1_11_runner.ValidationHarness")
def test_runner_execution_logic(mock_harness_class, tmp_path):
    mock_harness = MagicMock()
    mock_harness.__enter__.return_value = mock_harness
    mock_harness_class.return_value = mock_harness
    
    def mock_eval(board):
        fen = board.fen()
        print(f"MOCK EVAL CALLED WITH: {fen}")
        if "w" in fen:
            if "P7" in fen: # Q4_supp
                scores = {"e4e5": Score(type="cp", value=10, perspective="white"), "d4e5": Score(type="cp", value=5, perspective="white")}
                regrets = {"e4e5": Score(type="cp", value=0, perspective="white"), "d4e5": Score(type="cp", value=5, perspective="white")}
                return scores, regrets
            if "p7" in fen: # Q4_fals
                scores = {"e4e5": Score(type="cp", value=5, perspective="white"), "d4e5": Score(type="cp", value=10, perspective="white")}
                regrets = {"e4e5": Score(type="cp", value=5, perspective="white"), "d4e5": Score(type="cp", value=0, perspective="white")}
                return scores, regrets
            if "N7" in fen: # Q4_amb
                scores = {"e4e5": Score(type="mate", value=1, perspective="white"), "d4e5": Score(type="cp", value=5, perspective="white")}
                regrets = {"e4e5": Score(type="mate", value=0, perspective="white"), "d4e5": Score(type="cp", value=0, perspective="white")}
                return scores, regrets
            if "n7" in fen: # Q11
                scores = {"e2e4": Score(type="cp", value=10, perspective="white"), "e2e3": Score(type="mate", value=1, perspective="white")}
                regrets = {"e2e4": Score(type="cp", value=0, perspective="white"), "e2e3": Score(type="mate", value=0, perspective="white")}
                return scores, regrets
            if "B7" in fen: # Q14_supp
                scores = {"e2e4": Score(type="cp", value=10, perspective="white")}
                regrets = {"e2e4": Score(type="cp", value=0, perspective="white")}
                return scores, regrets
            if "b7" in fen: # Q14_fals
                scores = {"e2e4": Score(type="cp", value=10, perspective="white")}
                regrets = {"e2e4": Score(type="cp", value=5, perspective="white")}
                return scores, regrets
            if "R7" in fen: # Q14_amb
                scores = {"e2e4": Score(type="mate", value=1, perspective="white")}
                regrets = {"e2e4": Score(type="mate", value=0, perspective="white")}
                return scores, regrets
        elif "b" in fen:
            if "r7" in fen: # twin
                scores = {"a2a4": Score(type="cp", value=5, perspective="black")}
                regrets = {"a2a4": Score(type="cp", value=5, perspective="black")}
                print(f"EVAL FOR {fen}, TWIN")
                return scores, regrets
        print(f"EVAL FOR {fen}, FALLBACK TO EMPTY")
        return {}, {}
        
    mock_harness.evaluate_root_position.side_effect = mock_eval
    
    preflight_data = {"fixtures": [
        {"fixture_id": "Q4", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "m_11": ["e4e5"], "m_10": ["d4e5"], "m_01": ["a1a2"]},
        {"fixture_id": "Q4_fals", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "m_11": ["e4e5"], "m_10": ["d4e5"], "m_01": ["a1a2"]},
        {"fixture_id": "Q4_amb", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "m_11": ["e4e5"], "m_10": ["d4e5"], "m_01": ["a1a2"]},
        {"fixture_id": "Q11", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"},
        {"fixture_id": "Q14", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "m_11": ["e2e4"], "dimension_evidence": {"twin_partitions": {"m11": ["a2a4"]}}},
        {"fixture_id": "Q14_fals", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "m_11": ["e2e4"], "dimension_evidence": {"twin_partitions": {"m11": ["a2a4"]}}},
        {"fixture_id": "Q14_amb", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "m_11": ["e2e4"], "dimension_evidence": {"twin_partitions": {"m11": ["a2a4"]}}}
    ]}
    
    manifest_data = [
        {"fixture_id": "Q4", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppp1ppp/P7/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"},
        {"fixture_id": "Q4_fals", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppp1ppp/p7/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"},
        {"fixture_id": "Q4_amb", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppp1ppp/N7/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"},
        {"fixture_id": "Q11", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppppppp/n7/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"},
        {"fixture_id": "Q14", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppppppp/B7/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "twin_fixture": {"fen": "rnbqkbnr/pppppppp/r7/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"}},
        {"fixture_id": "Q14_fals", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppppppp/b7/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "twin_fixture": {"fen": "rnbqkbnr/pppppppp/r7/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"}},
        {"fixture_id": "Q14_amb", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppppppp/R7/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "twin_fixture": {"fen": "rnbqkbnr/pppppppp/r7/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"}}
    ]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
    
    with patch("chessheat.validation.t1_11_runner.validate_preflight_and_manifest"):
        run_t1_11_execution(str(preflight_path), str(manifest_path), str(tmp_path / "out"), "dummy")
    
    with open(tmp_path / "out" / "Q4.json") as f:
        q4 = json.load(f)
        assert q4["classification"] == "SUPPORTED" # med11 (0) < med10 (5)
        
    with open(tmp_path / "out" / "Q4_fals.json") as f:
        q4_fals = json.load(f)
        assert q4_fals["classification"] == "FALSIFIED" # med11 (5) >= med10 (0)
        
    with open(tmp_path / "out" / "Q4_amb.json") as f:
        q4_amb = json.load(f)
        assert q4_amb["classification"] == "AMBIGUOUS" # med11 is mate, no CP

    with open(tmp_path / "out" / "Q11.json") as f:
        q11 = json.load(f)
        assert q11["classification"] == "SUPPORTED"
        
    with open(tmp_path / "out" / "Q14.json") as f:
        q14 = json.load(f)
        assert q14["classification"] == "SUPPORTED" # 0 != 5
        
    with open(tmp_path / "out" / "Q14_fals.json") as f:
        q14_fals = json.load(f)
        assert q14_fals["classification"] == "FALSIFIED" # 5 == 5
        
    with open(tmp_path / "out" / "Q14_amb.json") as f:
        q14_amb = json.load(f)
        assert q14_amb["classification"] == "AMBIGUOUS" # primary has mate, twin has cp

def test_production_dry_run(tmp_path):
    # Do not mock ValidationHarness class, mock engine popen
    from chessheat.validation.t1_11_runner import run_t1_11_execution
    import chess.engine
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": "Test Engine"}
    mock_engine.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(10), chess.WHITE)}
    
    with patch("chess.engine.SimpleEngine.popen_uci") as mock_popen:
        mock_popen.return_value = mock_engine
        
        preflight_data = {"fixtures": [
            {"fixture_id": "Q11", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"}
        ]}
        manifest_data = [{"fixture_id": "Q11", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}]
        
        preflight_path = tmp_path / "pre.json"
        with open(preflight_path, "w") as f: json.dump(preflight_data, f)
        manifest_path = tmp_path / "man.json"
        with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
        with patch("chessheat.validation.t1_11_runner.validate_preflight_and_manifest"):
            run_t1_11_execution(str(preflight_path), str(manifest_path), str(tmp_path / "out"), "dummy")
        
        # Ensures lifecycle works, popen called, etc.
        assert mock_popen.called
        assert mock_engine.quit.called

def test_structural_classifications_against_real_preflight():
    preflight_path = "docs/research/t1/t1_11_structural_preflight.json"
    if not os.path.exists(preflight_path):
        pytest.skip("Real preflight not found")
        
    with open(preflight_path, "r") as f:
        preflight_data = json.load(f)
        
    for fix in preflight_data["fixtures"]:
        if fix["dimension_preflight_status"] == "PASS":
            c = evaluate_structural(fix["fixture_id"], fix)
            assert c in ["SUPPORTED", "FALSIFIED", "AMBIGUOUS"]
