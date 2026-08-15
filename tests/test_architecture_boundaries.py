import ast
import os
from pathlib import Path

def get_imports(file_path: Path):
    """Parse a python file and return a set of its import modules."""
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=str(file_path))
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            prefix = "." * node.level
            full_name = f"{prefix}{module_name}" if module_name else prefix
            imports.add(full_name)
            for alias in node.names:
                if full_name == ".":
                    imports.add(f".{alias.name}")
                else:
                    imports.add(f"{full_name}.{alias.name}")
    return imports

def test_objective_code_does_not_depend_on_human_layers():
    """
    Ensure that objective measurement code (models, recurrence, consequence)
    does not import or depend on human-navigation or explanation layers (e.g. ui, explanation).
    """
    base_dir = Path(__file__).parent.parent / "src" / "chessheat"
    
    # We will check models, recurrence, consequence, attribution, branch, delta
    core_modules = ["models.py", "recurrence.py", "consequence.py", "attribution.py", "branch.py", "delta.py"]
    
    forbidden_prefixes = (
        "chessheat.ui", "chessheat.explanation", "chessheat.visualization",
        ".ui", ".explanation", ".visualization",
        "..ui", "..explanation", "..visualization"
    )
    
    for module_name in core_modules:
        file_path = base_dir / module_name
        if not file_path.exists():
            continue
            
        imports = get_imports(file_path)
        for imp in imports:
            for forbidden in forbidden_prefixes:
                assert not imp.startswith(forbidden), (
                    f"Architecture Violation: Objective module '{module_name}' "
                    f"must not import from human/explanation layer '{imp}'"
                )
