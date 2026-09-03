#!/usr/bin/env python3
"""
Script para verificar documentação e type hints nos arquivos Python do projeto.

Verifica:
- Presença de docstrings de módulo
- Type hints em funções e métodos
- Documentação de classes
"""

import ast
from pathlib import Path


class DocChecker(ast.NodeVisitor):
    """Verificador de documentação e type hints."""

    def __init__(self, filename: str):
        self.filename = filename
        self.issues: list[str] = []
        self.has_module_docstring = False

    def visit_Module(self, node: ast.Module) -> None:
        """Verifica docstring do módulo."""
        if ast.get_docstring(node):
            self.has_module_docstring = True
        else:
            self.issues.append("❌ Módulo sem docstring")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Verifica funções e métodos."""
        # Pula métodos privados e dunder
        if node.name.startswith("_") and not node.name.startswith("__"):
            self.generic_visit(node)
            return

        # Verifica docstring
        if not ast.get_docstring(node):
            self.issues.append(f"⚠️  Função '{node.name}' sem docstring (linha {node.lineno})")

        # Verifica type hints no retorno
        if node.name != "__init__" and not node.returns:
            self.issues.append(
                f"⚠️  Função '{node.name}' sem type hint de retorno (linha {node.lineno})"
            )

        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Verifica classes."""
        if not ast.get_docstring(node):
            self.issues.append(f"⚠️  Classe '{node.name}' sem docstring (linha {node.lineno})")
        self.generic_visit(node)


def check_file(filepath: Path) -> tuple[bool, list[str]]:
    """
    Verifica um arquivo Python.

    Returns:
        tuple: (tem_problemas, lista_de_issues)
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            return False, []

        tree = ast.parse(content, filename=str(filepath))
        checker = DocChecker(str(filepath))
        checker.visit(tree)

        return len(checker.issues) > 0, checker.issues

    except SyntaxError as e:
        return True, [f"❌ Erro de sintaxe: {e}"]
    except Exception as e:
        return True, [f"❌ Erro ao processar: {e}"]


def iter_roots() -> list[Path]:
    """Retorna as raízes de código a varrer (meta-pacote + packages)."""
    project_root = Path(__file__).parent.parent
    roots: list[Path] = []

    meta_src = project_root / "src" / "radioskysims"
    if meta_src.exists():
        roots.append(meta_src)

    packages_src = project_root / "packages"
    if packages_src.exists():
        for pkg in sorted(packages_src.iterdir()):
            pkg_src = pkg / "src"
            if pkg_src.exists() and pkg_src.is_dir():
                roots.append(pkg_src)

    return roots


def main() -> None:
    """Executa verificação em todos os arquivos Python do projeto.

    Varre o meta-pacote (``src/radioskysims``) e, a partir do E14, também
    todos os pacotes do workspace (``packages/*/src``).
    """
    roots = iter_roots()

    if not roots:
        print("❌ Nenhuma raiz de código encontrada (src/radioskysims ou packages/*/src).")
        return

    py_files: list[tuple[Path, Path]] = []  # (arquivo, rel_path)
    for root in roots:
        for py_file in sorted(root.rglob("*.py")):
            py_files.append((py_file, py_file.relative_to(root)))

    print(f"📋 Verificando {len(py_files)} arquivos Python ({len(roots)} raízes)...\n")

    files_with_issues = 0
    total_issues = 0

    for py_file, rel_path in sorted(py_files, key=lambda item: str(item[1])):
        has_issues, issues = check_file(py_file)

        if has_issues:
            files_with_issues += 1
            total_issues += len(issues)
            print(f"\n📄 {rel_path}")
            for issue in issues:
                print(f"   {issue}")

    print(f"\n{'=' * 60}")
    print(f"✅ Arquivos verificados: {len(py_files)}")
    print(f"⚠️  Arquivos com problemas: {files_with_issues}")
    print(f"📊 Total de issues: {total_issues}")
    print(f"{'=' * 60}\n")

    if files_with_issues == 0:
        print("🎉 Todos os arquivos estão bem documentados!")
    else:
        print("💡 Execute novamente após correções para verificar progresso.")


if __name__ == "__main__":
    main()
