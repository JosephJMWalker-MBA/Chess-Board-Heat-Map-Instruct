import ast
import os

def test_t3b8_acquisition_executor_contract():
    script_path = "scripts/execute_t3b8_matched_acquisition.py"
    
    with open(script_path, "r", encoding="utf-8") as f:
        source = f.read()
        
    tree = ast.parse(source)
    
    analyse_calls = 0
    analysis_calls = 0
    play_calls = 0
    clear_hash_calls = 0
    experiment_result_create_calls = 0
    configure_calls = 0
    get_file_sha_engine_path_calls = 0
    
    strings = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "analyse":
                    analyse_calls += 1
                    
                    has_nodes_100000 = False
                    has_info_score = False
                    has_game_token = False
                    has_multipv_none = False
                    has_root_moves_none = False
                    
                    for kw in node.keywords:
                        if kw.arg == "info" and isinstance(kw.value, ast.Attribute) and kw.value.attr == "INFO_SCORE":
                            has_info_score = True
                        if kw.arg == "game" and isinstance(kw.value, ast.Name) and kw.value.id == "game_token":
                            has_game_token = True
                        if kw.arg == "multipv" and isinstance(kw.value, ast.Constant) and kw.value.value is None:
                            has_multipv_none = True
                        if kw.arg == "root_moves" and isinstance(kw.value, ast.Constant) and kw.value.value is None:
                            has_root_moves_none = True
                            
                    for arg in node.args:
                        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == "Limit":
                            for kw in arg.keywords:
                                if kw.arg == "nodes" and isinstance(kw.value, ast.Constant) and kw.value.value == 100000:
                                    has_nodes_100000 = True
                                    
                    assert has_nodes_100000, "Limit(nodes=100000) missing in analyse call"
                    assert has_info_score, "info=chess.engine.INFO_SCORE missing in analyse call"
                    assert has_game_token, "game=game_token missing in analyse call"
                    assert has_multipv_none, "multipv=None missing in analyse call"
                    assert has_root_moves_none, "root_moves=None missing in analyse call"
                    
                elif node.func.attr == "analysis":
                    analysis_calls += 1
                elif node.func.attr == "play":
                    play_calls += 1
                elif node.func.attr == "clear_hash":
                    clear_hash_calls += 1
                elif node.func.attr == "configure":
                    configure_calls += 1
                elif node.func.attr == "create":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "ExperimentResult":
                        experiment_result_create_calls += 1
            elif isinstance(node.func, ast.Name) and node.func.id == "get_file_sha":
                if len(node.args) == 1 and isinstance(node.args[0], ast.Name) and node.args[0].id == "engine_path":
                    get_file_sha_engine_path_calls += 1
                        
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.add(node.value)
            
        elif isinstance(node, ast.Name):
            assert node.id != "mate_score", "mate_score identifier found"
            bad_identifiers = {
                "G_j", "T_j", "D_j", "S_j", "S_match", "L", "E", "Q", "Q_suite", "H_.75",
                "evaluable", "classification", "supported", "weak_support", "falsified"
            }
            assert node.id not in bad_identifiers, f"Forbidden T3b-6 identifier {node.id} found"

    assert analyse_calls == 1, f"Expected 1 analyse call, found {analyse_calls}"
    assert analysis_calls == 0, f"Expected 0 analysis calls, found {analysis_calls}"
    assert play_calls == 0, f"Expected 0 play calls, found {play_calls}"
    assert clear_hash_calls == 0, f"Expected 0 clear_hash calls, found {clear_hash_calls}"
    assert configure_calls == 1, f"Expected 1 configure call, found {configure_calls}"
    assert get_file_sha_engine_path_calls >= 2, f"Expected at least 2 get_file_sha(engine_path) calls, found {get_file_sha_engine_path_calls}"
    assert experiment_result_create_calls >= 1, "Expected ExperimentResult.create to be called"
    
    expected_strings = [
        "40949ceeaa5ff1cd1c8a083df45f0dbe0f252d3f1637a692dbf96ae98156ad13",
        "6ce6b91d3839998f2b9f24c3c6368cbb30cf799c1e8ddaeb9a9a3dcfc54e957b",
        "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7",
        "ENGINE_BINARY_IDENTITY_CHANGED_AFTER_SPAWN",
        "REQUIRED_ENGINE_OPTIONS_MISSING",
        "tests/fixtures/t3b8/t3b8_acquisition_started.json",
        "tests/fixtures/t3b8/t3b8_raw_acquisition.json"
    ]
    for s in expected_strings:
        assert s in strings, f"Expected string literal {s} not found in source"
        
    started_path = "tests/fixtures/t3b8/t3b8_acquisition_started.json"
    raw_path = "tests/fixtures/t3b8/t3b8_raw_acquisition.json"
    
    # Verify the executor script itself contains logic to check if paths exist
    has_path_exists_check = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "exists" and isinstance(node.func.value, ast.Attribute):
                    if node.func.value.attr == "path" and isinstance(node.func.value.value, ast.Name):
                        if node.func.value.value.id == "os":
                            has_path_exists_check = True
                            
    assert has_path_exists_check, "Executor must contain os.path.exists checks to fail closed on existing outputs"

if __name__ == "__main__":
    test_t3b8_acquisition_executor_contract()
    print("Test passed.")
