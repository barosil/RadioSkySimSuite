# RadioSkySimSuite — Checklist de Ações (Nov–Dez 2026)

**Atualizado:** 2026-11-05  
**Responsável:** @barosil  
**Status geral:** 3 frentes ativas; timeline nov–dez

---

## 📋 Ações Imediatas — Nov 5–10

- [ ] **Revisar relatórios de auditoria** (15–30 min)
  - Ler: `november_2026_audit_report.md`
  - Ler: `frentes_status_consolidado.md`
  - Validar: conclusões vs realidade local

- [ ] **Merge branches prontas** (30 min)
  - [ ] `chore/notebooks-cwd-anchor` — Ancoragem CWD de notebooks
  - [ ] `audit/broad-linting` — Consolidação de lint
  - [ ] `audit/logging-consistency` — Logging review
  - Ação: `git checkout dev && git pull origin dev`
  - Ação: `gh pr list --state ready`; merge via `gh pr merge <id>`

- [ ] **F2a: Iniciar refactoring de logging de domain** (1–2h prep)
  - [ ] Listar todos os imports `logger` em `domain/*/services.py`
    - `grep -r "from .* import logger" packages/*/src/*/domain`
  - [ ] Criar branch: `git checkout -b feat/f2a-move-logging-from-domain`
  - [ ] Document pattern em DESIGN.md (logger via dependency injection)
  - [ ] Criar first commit com esquema; PR draft para revisão

---

## 📅 Semana Nov 11–17 — Formatação + TOD Setup + F1 Prototipo

- [ ] **F2c: Ruff Format** (2–3h)
  - [ ] Criar branch: `git checkout -b chore/ruff-format`
  - [ ] Executar: `uv run ruff format src packages`
  - [ ] Verificar: `uv run ruff format --check src packages` (deve estar OK)
  - [ ] Commit: `git add src packages && git commit -m "chore(format): ruff format src packages"`
  - [ ] PR para `dev`; merge após CI verde

- [ ] **F3a: Setup TOD 24h** (4–6h prep)
  - [ ] Verificar disponibilidade de hardware (> 32GB RAM)
  - [ ] Preparar dados de entrada (catálogos, parâmetros)
  - [ ] Script de execução: `scripts/run_tod_24h_benchmark.py` (se não existir, criar)
  - [ ] Agendamento: quando rodar? (fora de horas de pico)
  - [ ] Logging/monitoramento: Dask telemetria + output capture

- [ ] **F1b: Prototipo Progress Bars** (2–3h)
  - [ ] Revisar operações longas (> 5s):
    - Simulação TOD: `radioskysims tod export ...`
    - Mapmaking: `radioskysims skymap generate ...`
    - Downloads: `radioskysim-sources ...`
  - [ ] Adicionar `tqdm` (se não instalado: `uv add tqdm`)
  - [ ] Implementar em uma operação como prototipo (ex: TOD export)
  - [ ] Testar: `uv run radioskysims tod export --help` (deve mostrar progress)
  - [ ] Branch: `feat/f1-progress-bars-tqdm` (WIP, para revisão)

---

## 📅 Semana Nov 18–24 — Merge + F2 Logging + TOD Execução

- [ ] **Merge F2c (ruff format)** (1h)
  - [ ] Aguardar CI verde em `chore/ruff-format`
  - [ ] Merge via GitHub/CLI
  - [ ] Verificar: `dev` atualizada, 0 novos erros

- [ ] **F2a: Primeiro PR de logging refactor** (8–12h, possivelmente 2 PRs)
  - [ ] Estender trabalho prep iniciado em nov 11
  - [ ] Refactoring de 3–5 arquivos iniciais (baixo risco)
  - [ ] PR para revisão; aguardar feedback
  - [ ] Timeline: PR 1 (prototipo) → merge; PR 2+ (bulk) → iterada em nov 25+

- [ ] **F3a: Executar TOD 24h** (6h wall-clock, hands-on ~2h)
  - [ ] Iniciar simulação (timing: nov 22–23 noite/madrugada?)
  - [ ] Monitorar: recursos, erros, telemetria Dask
  - [ ] Capturar logs: `logs/tod_24h_2026_11_*.json`
  - [ ] Salvar dados intermediários se possível
  - [ ] ⚠ Se falhar: diagnóstico, report em issue, retry em backup date

- [ ] **F1b: Refine progress bars** (1–2h)
  - [ ] Integrar feedback de prototipo (nov 11–17)
  - [ ] Expandir a outras operações (mapmaking, etc.)
  - [ ] PR final para merge fim de nov

---

## 📅 Semana Nov 25–Dec 1 — Análise + Refactoring Schema + Release Prep

- [ ] **F3a: Análise resultados TOD 24h** (4–8h)
  - [ ] Se sucesso:
    - [ ] Comparar vs benchmark 1h (speedup? memória?)
    - [ ] Validar vs dados reais (se disponível)
    - [ ] Documentar no relatório: `docs/audits/tod_24h_validation_nov_2026.md`
  - [ ] Se falha:
    - [ ] Debugging (logs, reprodutibilidade)
    - [ ] Agendar retry (backup date)
    - [ ] Documento de lessons learned

- [ ] **F2b: Schema de refactoring orquestração** (6–8h)
  - [ ] Analisar `simulation/sim_orchestrator.py` + `simulation/simulation.py`
  - [ ] Criar DESIGN.md com proposta de decomposição
  - [ ] Identificar casos de uso pequenos (1–2 responsabilidades cada)
  - [ ] Estimar esforço por PR
  - [ ] PR do DESIGN.md para revisão (não código ainda)

- [ ] **F3b: Auditoria de Satélites — Prep** (2–3h)
  - [ ] Listar componentes:
    - [ ] Propagação TLE (skyfield integration)
    - [ ] Contribuição em rádio (S-band, gain)
    - [ ] Validação integrada
  - [ ] Criar issue/branch: `audit/f3b-satellites-audit`
  - [ ] Esquema de validação (vs dados NORAD? vs literatura?)

- [ ] **Release Prep** (2–3h)
  - [ ] Draft changelog: F1/F2/F3 resumo
  - [ ] Verificar `dev` contra `main` (diffs)
  - [ ] Listar breaking changes (se houver)
  - [ ] Revisar AGENTS.md / docs contemporâneos (estão sync?)

---

## 📅 Dezembro — Iteração Refactoring + Release

- [ ] **F2b: Refactoring orquestração (Iteração 1)** (20–30h, spread across)
  - [ ] PR 1: Extrair `case_1_data_generation` (6–8h)
  - [ ] PR 2: Extrair `case_2_mapping` (6–8h)
  - [ ] PR 3: Refine logging integration (3–4h)
  - [ ] Cada PR aguarda revisão + merge

- [ ] **F3b: Auditoria satélites (Iteração 1)** (10–15h)
  - [ ] Validação de propagação TLE
  - [ ] Validação de contribuição em rádio
  - [ ] Documento: `docs/audits/satellites_audit_dec_2026.md`

- [ ] **CI: Adicionar mypy + pytest --cov** (4–6h)
  - [ ] Configurar mypy em `.github/workflows/` (não verificado em nov)
  - [ ] Adicionar `pytest --cov` em CI
  - [ ] Baseline de falhas esperadas; iterar para 0

- [ ] **Release `dev → main`** (2–3h)
  - [ ] Final PR review (todos os compromissos de nov estão em `dev`?)
  - [ ] Merge `dev → main`
  - [ ] Tag release: `v<version>` (consultar versioning scheme)
  - [ ] Draft release notes no GitHub
  - [ ] Announcement (se aplicável)

---

## 🎯 Definições de Pronto (DoD) — Checkpoints

### Checkpoint 1: Nov 17 (Formatação + TOD Setup OK)
- [x] Docs auditorias atualizadas ✓ (11/5)
- [ ] F2c (ruff format) merged
- [ ] F3a (TOD 24h) em andamento
- [ ] F1b (progress bars) prototipado

### Checkpoint 2: Nov 24 (Merge + Execução)
- [ ] F2c (ruff format) merged ✓
- [ ] F2a (logging refactor PR1) em revisão
- [ ] F3a (TOD 24h) finalizado (sucesso ou fail/retry claro)
- [ ] F1b (progress bars) mergeable

### Checkpoint 3: Dez 1 (Análise + Schema)
- [ ] F3a (TOD 24h) analisado; documento escrito
- [ ] F2b (refactoring orquestração) schema aprovado
- [ ] F3b (satélites) audit iniciada
- [ ] Release prep checklist iniciada

### Checkpoint 4: Dez 5–10 (Release)
- [ ] F2b (orquestração refactoring) PR 1–3 merged
- [ ] F3b (satélites) documento concluído
- [ ] `dev → main` merged
- [ ] Versão tagged + release notes publicado

---

## 📞 Comunicação e Escalação

### Status meetings (recomendado: semanal)
- **Usar:** `AUDIT_SUMMARY_NOV2026.txt` para visão rápida
- **Detalhe técnico:** referências em `november_2026_audit_report.md`
- **Timeline:** `frentes_status_consolidado.md` seção 4

### Bloqueadores conhecidos
- [ ] TOD 24h depende de hardware disponível (> 32GB RAM)
- [ ] F2b refactoring afeta testes (pode demandar atualização suite)
- [ ] Release depende de aprovação executiva (se aplicável)

### Contatos
- Repo: `barosil/RadioSkySimSuite`
- Issues: GitHub issues (etiqueta: `audit`, `f1`, `f2`, `f3`)
- Branch: `dev` (principal)

---

## 📊 Métricas de Sucesso

**Nov 10:**
- [ ] 3 branches merged (notebooks-cwd, broad-linting, logging-consistency)
- [ ] F2a iniciado (1 commit no mínimo)

**Nov 24:**
- [ ] Formatação 100% (570/654 → 654/654 OK)
- [ ] F3a TOD 24h resultado claro (sucesso ou fail+retry agendado)
- [ ] F1b prototipo funcional

**Dez 5:**
- [ ] F2b PR 1 merged
- [ ] F3b documento + PR
- [ ] Release `dev → main` done

**Dez 10:**
- [ ] Todos os checkpoints ✅
- [ ] Novo relatório de auditoria (dez 2026) iniciado

---

## 📝 Template de Atualização Semanal

Copie este template ao atualizar status em `.prompts/barosil.md`:

```markdown
## Snapshot — YYYY-MM-DD (Semanal)

**Dev branch:** [commit hash] — [descrição]
**Status geral:** F1 [x%], F2 [y%], F3 [z%]

### Concluído esta semana
- [ ] Item 1
- [ ] Item 2

### Em andamento
- [ ] Item A
- [ ] Item B

### Próximas prioridades
1. Ação 1
2. Ação 2

### Bloqueadores (se houver)
- Bloqueador 1 — esperado até DATA
```

---

**Autor:** Copilot (análise + planejamento)  
**Última revisão:** 2026-11-05  
**Próxima revisão:** 2026-11-08 (pós-primeiro checkpoint)  
**Link para documento-mestre:** `.prompts/barosil.md`
