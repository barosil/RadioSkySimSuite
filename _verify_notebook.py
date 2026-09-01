"""Verificação: executa todas as células de código do notebook em sequência."""
import json
import sys
import traceback

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

nb = json.load(open("notebooks/00_examples.ipynb", encoding="utf-8"))

ns: dict = {}
failed = 0
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    print(f"=== código {i}: {src.splitlines()[0] if src else '(vazio)'}")
    try:
        exec(compile(src, f"<cell{i}>", "exec"), ns)
        plt.close("all")
        print(f"  OK ({i})")
    except Exception as exc:
        failed += 1
        print(f"  FALHOU ({i}): {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=3)

print(f"\nRESULTADO: {failed} célula(s) com erro")
sys.exit(1 if failed else 0)
