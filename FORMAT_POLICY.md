# Política de Formatação de Código — RadioSkySimSuite

**Versão:** 1.0  
**Data:** 2026-11-05  
**Status:** ✅ Ativa

## Resumo

Todo código Python do projeto deve estar em conformidade com **`ruff format`**. Esta política garante:
- Consistência de estilo em todo o workspace (meta-repo + 9 pacotes)
- História de git limpa (sem commits de "limpeza de formatação")
- CI automático impedindo merge de código não-formatado

## Padrão: Ruff Format

- **Ferramenta:** `ruff >= 0.6.0`
- **Comando:** `ruff format src packages/*/src`
- **Check:** `ruff format --check src packages/*/src` (CI)
- **Cobertura:** Código de produção + testes

### Configuração (pyproject.toml)

```toml
[tool.ruff.format]
quote-style = "double"          # Use aspas duplas
indent-width = 4                # Indentação de 4 espaços
line-length = 88                # PEP 8 standard
```

## Fluxo de Trabalho

### Local (Antes de Commitar)

```bash
# Formatação automática
uv run ruff format src packages/*/src

# Verificação (para CI)
uv run ruff format --check src packages/*/src
```

### CI (GitHub Actions)

Pull requests são verificados automaticamente via:
```yaml
- name: Check ruff format
  run: ruff format --check src packages/*/src --exit-zero-code
```

**Bloqueador:** Merge será rejeitado se `--check` falhar.

## Antes e Depois

### Exemplo 1: Aspas e Strings

**Antes:**
```python
def foo():
    s = 'hello world'
    return s
```

**Depois:**
```python
def foo():
    s = "hello world"
    return s
```

### Exemplo 2: Linhas Longas

**Antes:**
```python
result = some_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9)
```

**Depois:**
```python
result = some_function(
    arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9
)
```

### Exemplo 3: Método com Docstring

**Antes:**
```python
def calculate(x, y):
    """Calcula x + y."""
    return x+y
```

**Depois:**
```python
def calculate(x, y):
    """Calcula x + y."""
    return x + y
```

## Exceções

**Nenhuma.** O `ruff format` é obrigatório para:
- ✅ Código de produção (`src/`)
- ✅ Testes (`tests/`)
- ✅ Scripts de exemplo (`scripts/`)
- ✅ Notebooks (via `jupytext` ou conversão manual)

Exceto:
- ❌ Arquivos gerados automaticamente (com comentário `# auto-generated`)
- ❌ Código vendorizado dentro de `# begin vendor` / `# end vendor`

## Importância

Esta política foi estabelecida durante a **Fase 4 — Consolidação (Nov 2026)**:
- Reduz violações de lint de 1.062 (ago) → ~10 (nov)
- Garante consistência visual entre 669 arquivos
- Evita conflitos de merge causados por reformatação
- Libera recursos para revisão de lógica (não estilo)

## Referência

- **Branch:** `chore/ruff-format-complete` (B4)
- **Critério de Sucesso:** 100% conformidade, 0 violações
- **Timeline:** Nov 5–6, 2026
- **Plano:** [`PLANO_EXECUCAO_NOV_2026.md`](./PLANO_EXECUCAO_NOV_2026.md) — seção T2

---

**Mantido por:** @barosil (RadioSkySimSuite)  
**Última atualização:** 2026-11-05
