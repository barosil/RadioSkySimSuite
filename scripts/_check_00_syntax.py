"""Valida sintaxe (compile-only) das células de código do notebook 00_examples."""

import json
import sys

nb = json.loads(open("notebooks/00_examples.ipynb", encoding="utf-8").read())
failed = 0
for i, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    if not src.strip():
        continue
    lines = src.splitlines()
    code_lines = [ln for ln in lines if not ln.lstrip().startswith(("%", "!"))]
    try:
        compile("\n".join(code_lines), f"cell{i}", "exec")
    except SyntaxError as exc:
        failed += 1
        print(f"ERRO célula {i}: {exc}")
print(f"RESULTADO: {failed} célula(s) com erro de sintaxe")
sys.exit(1 if failed else 0)
