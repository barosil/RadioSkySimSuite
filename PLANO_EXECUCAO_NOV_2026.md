# Plano de Execução — RadioSkySimSuite (Nov 5–17, 2026)

**Data de Criação:** 2026-11-05  
**Timeline:** 2 semanas intensivas (nov 5–17)  
**Estratégia:** 9 branches paralelas, agrupadas por categoria  
**Total Estimado:** ~110 horas de desenvolvimento  
**Status:** 🟢 Aprovado — Pronto para Execução

---

## 📋 Resumo Executivo

**Objetivo:** Atacar dívida técnica (TD-001/002/003), qualidade de código (lint/type-hints/CI) e UX F1 completo em paralelo.

**3 Eixos de Trabalho:**

| Eixo | Foco | Branches | Esforço | Status |
|------|------|----------|---------|--------|
| **T1** | Dívida Técnica (ports, domain puro) | 3 | 52h | 🟡 Ativo |
| **T2** | Qualidade Código (lint, mypy, CI) | 2 | 19.5h | 🟡 Ativo |
| **T3** | F1 Completo (UX entrypoints) | 4 | 35h | 🟡 Ativo |

**Saída esperada (nov 17):**
- ✅ Todas 9 branches mergidas em `dev`
- ✅ Suíte 100% verde
- ✅ 0 lint violations; 100% format; 75%+ type hints
- ✅ F1 completo (ruído, defaults, errors, formatting, progress, logging, docs)
- ✅ Pronto para release `dev → main` (opcional dez 1–5)

---

## 🎯 Os 9 Branches

### T1 — Dívida Técnica (Eliminação de Violações Arquiteturais)

#### B1: `fix/td-001-application-infrastructure-ports` [30h, 8d]

**Objetivo:** Eliminar imports diretos `application → infrastructure` via ports + dependency injection.

**Items:**
- `T1.1` — Criar `application/ports/persistence.py` (abstract repo contracts)
- `T1.2` — Criar `application/ports/external_services.py` (TAP, skyfield, providers)
- `T1.3` — Refactor `application/services/sim_orchestrator.py` (remove imports diretos)
- `T1.4` — Refactor `application/services/simulation_service.py` (mesmo padrão)
- `T1.5` — Refactor `application/radiosources_use_cases.py`
- `T1.6` — Criar `bootstrap/dependencies.py` (composition root com DI)
- `T1.7` — Documentar pattern em `DESIGN.md` (before/after com exemplo)

**Validação:**
- [ ] Testes de application 100% verde
- [ ] Bootstrap funciona (CLI ainda ativa)
- [ ] 0 new lint violations
- [ ] PR description com checklist

**Merge Criteria:**
- [ ] Testes: ✅ verde
- [ ] Lint: ✅ 0 erros novos
- [ ] CI: ✅ passa
- [ ] Merge para `dev`

---

#### B2: `fix/td-002-domain-infrastructure-boundaries` [18h, 8d]

**Objetivo:** Domínio puro — promover providers/factories de domain para application/ports.

**Items:**
- `T1.8` — Mover `domain/geometry/skyfield_provider.py` → `application/ports/external_geometry.py`
- `T1.9` — Promover factories (beam, signal, satellite) para ports + infrastructure implementations
- `T1.10` — Refactor `domain/beam/services.py` e `domain/skymap/factory.py` (remover logging direto, imports)

**Validação:**
- [ ] Domain sem imports `infrastructure`
- [ ] Testes de domain 100% verde
- [ ] Factories funcionam via DI (bootstrap injeta implementations)

**Dependência:** B1 (ports devem existir)

**Merge Criteria:**
- [ ] Domain puro (0 infrastructure imports)
- [ ] Testes: ✅ verde
- [ ] Merge para `dev`

---

#### B3: `fix/td-003-domain-application-inversion` [4h, 2d]

**Objetivo:** Remover inversão de dependência — aliases de compatibilidade para application/adapters.

**Items:**
- `T1.11` — Listar todos os aliases em `domain/satellite/repositories.py`
- `T1.12` — Mover aliases para `application/adapters/compatibility.py` (re-export central)

**Validação:**
- [ ] Domain sem imports `application`
- [ ] Re-imports via `application/adapters` funcionam

**Merge Criteria:**
- [ ] Domain sem application imports
- [ ] Compatibilidade preservada
- [ ] Merge para `dev`

---

### T2 — Qualidade de Código (Lint, Formatação, Type Hints)

#### B4: `chore/ruff-format-complete` [2.5h, 1d] ⚡ Quick Win

**Objetivo:** 100% conformidade `ruff format`.

**Items:**
- `T2.1` — Executar `uv run ruff format src packages` (84 arquivos)
- `T2.2` — Review automatizado (nenhuma lógica alterada)
- `T2.3` — Adicionar CI check `ruff format --check` (falhar se diverge)

**Validação:**
- [ ] 100% conformidade (0 divergências)
- [ ] Testes ainda passam
- [ ] CI verde

**Merge Criteria:**
- [ ] Formato OK
- [ ] CI com ruff format check
- [ ] Merge para `dev`

---

#### B5: `chore/type-hints-coverage-expansion` [17h, 5d]

**Objetivo:** Elevar type hints de 65% para 75%+ (application + critical infrastructure).

**Items:**
- `T2.4` — Audit: listar 50–100 funções críticas sem hints
- `T2.5` — Type hints em `application/services/` (8–10 arquivos)
- `T2.6` — Type hints em `application/use_cases/` (5–7 arquivos)
- `T2.7` — Type hints em `infrastructure/{persistence,io}` (key modules)
- `T2.8` — Adicionar `mypy application/ --strict` em CI

**Validação:**
- [ ] mypy verde em application/
- [ ] Type coverage 75%+
- [ ] CI verde

**Dependência:** B4 (linting deve estar limpo)

**Merge Criteria:**
- [ ] Type hints 75%+
- [ ] mypy --strict application OK
- [ ] CI com mypy check
- [ ] Merge para `dev`

---

### T3 — F1 Completo (UX Entrypoints)

#### B6: `fix/f1-startup-noise-and-defaults` [3h, 1d]

**Objetivo:** Remover ruído no startup, corrigir defaults quebrados.

**Items:**
- `T3.1` — Validar: asyncpg warning ausente (já feito?)
- `T3.2` — Fix: `--telescope default` quebrado → settings ou fallback
- `T3.3` — Documentar: `--constellations` help + README (default=no satellites)

**Validação:**
- [ ] `uv run radioskysims --help` sem warnings
- [ ] `uv run radioskysims tod export` sem args funciona
- [ ] Help text claro

**Merge Criteria:**
- [ ] Startup limpo
- [ ] Defaults funcionam
- [ ] Merge para `dev`

---

#### B7: `fix/f1-silent-failures-and-consistency` [9h, 3d]

**Objetivo:** Eliminar fallbacks silenciosos, standardizar tratamento de erro e documentar unidades.

**Items:**
- `T3.4` — F1.M1: `radioskysim-sources radio list` erro claro quando banco falha (não fallback silencioso)
- `T3.5` — F1.R4: Standardizar exit codes em 3 CLIs via base error handler (2–4 expected, 1 unexpected)
- `T3.6` — F1.M2: Help text com unidades em todas flags; README com table

**Validação:**
- [ ] Erro claro (não fallback)
- [ ] Exit codes consistentes
- [ ] Help text com unidades

**Merge Criteria:**
- [ ] Sem fallbacks silenciosos
- [ ] Exit codes padronizados
- [ ] Merge para `dev`

---

#### B8: `feat/f1-output-formatting-and-progress` [16h, 4d]

**Objetivo:** Formatação visual (cores, tables) e progress bars + logging estruturado.

**Items:**
- `T3.7` — F1.M3: Cores em 3 CLIs (vermelho=erro, amarelo=aviso, verde=sucesso) via `rich`
- `T3.8` — F1.R5: Progress bars em operações > 5s (`tqdm`) — TOD, mapmaking, downloads
- `T3.9` — F1.M4: Logging JSON → stderr, output humano → stdout
- `T3.10` — F1.M5: Help text em todas flags (completar generate/survey)

**Validação:**
- [ ] Cores/tables visíveis (manual test)
- [ ] Progress bar funciona
- [ ] Logging separado
- [ ] Help text completo

**Dependência:** B7 (error handling base)

**Merge Criteria:**
- [ ] CLI visual OK
- [ ] Progress funciona
- [ ] Logging separado
- [ ] Merge para `dev`

---

#### B9: `docs/f1-getting-started-and-reference` [7h, 2d]

**Objetivo:** Documentação de uso clara e acessível.

**Items:**
- `T3.11` — F1.L1: README "Getting Started" com 3–5 exemplos (copy-paste ready)
- `T3.12` — F1.L2: Docstring de CLI commands (typer help strings claras)
- `T3.13` — F1.L3: Guia troubleshooting (FAQ com erros comuns + soluções)

**Validação:**
- [ ] Exemplos funcionam (testar copy-paste)
- [ ] Docstrings claras
- [ ] FAQ útil

**Merge Criteria:**
- [ ] README OK
- [ ] Docstrings OK
- [ ] Troubleshooting útil
- [ ] Merge para `dev`

---

## 📅 Timeline Detalhada — Nov 5–17

### Semana 1: Nov 5–10 (Ramp-up)

**Segunda (5):**
- Criar 3 branches: B1, B4, B6 (30 min)
- B1: T1.1, T1.2 (4h prep)
- B4: T2.1, T2.2 (1h, pode completar hoje)
- B6: T3.1 audit + T3.2 fix (1.5h)

**Terça (6):**
- B4 : T2.3 (CI setup, 1h) → **Ready to Merge**
- B1: T1.3, T1.4 (refactoring, 6h)
- B6: T3.3 docs (1h)
- Criar B2 (prep inicial)

**Quarta (7):**
- B4 **MERGE** (quick win ✅)
- B1: T1.5, T1.6 (7h continua)
- B7: T3.4 iniciado (2h)
- B2: T1.8 iniciado (2h)

**Quinta (8):**
- B1: T1.7 DESIGN.md + wrap-up
- B6: Review + PR
- B7: T3.5 (error handler design, 2h)
- B2: T1.8, T1.9 (4h)

**Sexta (9):**
- B6 **MERGE** (2h após review)
- B1 **MERGE** (após review + testes)
- B7: T3.5 error handler impl (4h)
- B5: T2.4 audit iniciado (1h)
- Criar B3, B8, B9

**Sábado (10):**
- B2: T1.9 continua (4h)
- B7: T3.6 docs unidades (2h)
- B5: T2.5 application/services hints (3h)
- B3: Iniciado (1h)

---

### Semana 2: Nov 11–17 (Consolidação)

**Segunda (11):**
- B2: T1.10 + wrap-up (3h) → **Ready**
- B5: T2.6 application/use_cases (4h)
- B8: T3.7 rich setup (2h)
- B3: T1.11, T1.12 (2h)

**Terça (12):**
- B2 **MERGE** (após review)
- B5: T2.7 infrastructure hints (4h)
- B8: T3.8 tqdm integration (4h)
- B9: T3.11 README começar (1h)

**Quarta (13):**
- B3 **MERGE** (quick one)
- B5: T2.8 mypy CI setup (1h) → **Ready**
- B7 **MERGE** (após review final)
- B8: T3.9 logging config (3h)
- B9: T3.12 docstrings (2h)

**Quinta (14):**
- B5 **MERGE** (após tests verde)
- B8: T3.10 help text completo (2h) → **Ready**
- B9: T3.13 troubleshooting FAQ (2h)

**Sexta (15):**
- B8 **MERGE** (após review)
- B9: Review + finalize → **Ready**
- Dev branch review: todos os commits, testes, documentação

**Sábado–Domingo (16–17):**
- B9 **MERGE**
- Final validation: CI verde, manual tests, docs updated
- `.prompts/barosil.md` atualizado com snapshot pós-execução

---

## 🔀 Sequência de Merge

**Ordem (respeitar dependências):**

1. `chore/ruff-format-complete` (B4) — independente, quick win
2. `fix/f1-startup-noise-and-defaults` (B6) — independente
3. `fix/td-001-application-infrastructure-ports` (B1) — **bloqueador para B2**
4. `fix/f1-silent-failures-and-consistency` (B7) — independente
5. `fix/td-002-domain-infrastructure-boundaries` (B2) — depende B1
6. `feat/f1-output-formatting-and-progress` (B8) — depende B7
7. `chore/type-hints-coverage-expansion` (B5) — depende B4 (linting limpo)
8. `fix/td-003-domain-application-inversion` (B3) — independente
9. `docs/f1-getting-started-and-reference` (B9) — independente

**Cada merge:**
- [ ] Testes locais 100% verde: `uv run pytest tests/ --cov`
- [ ] Lint OK: `ruff check && ruff format --check`
- [ ] CI verde (se auto-merge)
- [ ] Squash or rebase (manter história limpa)
- [ ] Delete branch remoto

---

## 🎯 Critérios de Sucesso Finais (DoD)

### Global
- [ ] **Todas 9 branches** mergidas em `dev`
- [ ] **Testes:** 100% verde (`pytest tests/ -q` = 0 falhas)
- [ ] **Lint:** 0 violações (ruleset ativo)
- [ ] **Formatação:** 100% conformidade (ruff format)
- [ ] **Type hints:** 75%+ cobertura (up from 65%)
- [ ] **CI:** Todos checks verdes (ruff, mypy, pytest)
- [ ] **CLI:** End-to-end funcional (manual test)
- [ ] **Documentação:** README, DESIGN.md, troubleshooting atualizados

### T1 (Dívida Técnica)
- [ ] **TD-001:** Application→infrastructure via ports + DI (0 direct imports)
- [ ] **TD-002:** Domain puro (0 infrastructure imports; providers/factories em ports)
- [ ] **TD-003:** Domain sem application imports (aliases em application/adapters)
- [ ] **Bootstrap:** DI funcional; todas as dependências injetadas
- [ ] **Nenhuma regressão:** CLIs, notebooks, testes funcionam

### T2 (Qualidade Código)
- [ ] **Formatação:** `ruff format --check src packages` = 0 divergências
- [ ] **Type hints:** Cobertura 75%+ (audit de functions críticas)
- [ ] **mypy:** Verde em `application/` com `--strict`
- [ ] **CI:** Checks adicionados (.github/workflows)

### T3 (F1 — UX)
- [ ] **Startup:** Limpo (0 asyncpg, 0 pydantic warnings)
- [ ] **Defaults:** `--telescope` e `--constellations` funcionam sem args
- [ ] **Error handling:** Standardizado (exit codes 2–4 expected, 1 unexpected; mensagens claras)
- [ ] **Formatação visual:** Cores em 3 CLIs; tabelas claras
- [ ] **Progress bars:** Visíveis em operações > 5s
- [ ] **Logging:** JSON → stderr; output humano → stdout (separado)
- [ ] **Help text:** Completo em todas flags + unidades
- [ ] **Documentação:** README (3+ exemplos), CLI docstrings, troubleshooting FAQ
- [ ] **Manual test:** Copy-paste dos exemplos funciona

---

## 🛠️ Como Trabalhar com Este Plano

### Para Cada Branch

**1. Criar:**
```bash
git checkout dev
git pull origin dev
git checkout -b <branch-name>
```

**2. Desenvolver:**
- Small commits (~200–500 LOC cada; lógica agrupada)
- Mesma estrutura em todos os pacotes (packages/radioskysims-*/src/*/...)
- Incluir testes + docstrings

**3. Testar:**
```bash
uv run pytest <scope> --cov
uv run ruff check src packages
uv run ruff format --check src packages
```

**4. PR:**
- Criar draft PR no GitHub com descrição detalhada
- Checklist dos items (T1.1, T1.2, etc)
- Mensagem de commit: `fix(arch): <item> — <descrição> (#<issue>)`

**5. Review:**
- Self-review (código, testes, docs)
- Peer review (1+ reviewer se possível)

**6. Merge:**
```bash
git checkout dev
git pull origin dev
git merge --squash <branch-name>
git commit -m "fix/feat: <titulo>\n\n- Item 1\n- Item 2\n\nCo-authored-by: Copilot..."
git push origin dev
git branch -d <branch-name>
git push origin --delete <branch-name>
```

### Daily Tracking

Use `docs/audits/CHECKLIST_NOV_DEC_2026.md` para rastrear:
- Progresso por dia
- Bloqueadores encontrados
- Reajustes de timeline

Atualizar `.prompts/barosil.md` com snapshot semanal.

---

## ⚠️ Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Refactoring T1 quebra testes | Média | Alto | Testes antes de push; rollback se needed |
| Merge conflicts em dev | Baixa | Médio | Merge sequence planejada; rebase se needed |
| Esforço subestimado | Média | Médio | Daily check-in; priorizar high-value items |
| Type hints mypy muito rigoroso | Baixa | Baixo | Usar `# type: ignore` com documento; adaptar se needed |
| Logging refactor afeta performance | Muito Baixa | Médio | Benchmarks antes/depois (T3.9) |

---

## 📞 Próximas Ações Imediatas

1. ✅ Salvar este plano no repositório (commit em dev)
2. ⏳ Setup: `uv sync`, verificar testes baseline
3. ⏳ Criar 9 branches (nov 5 afternoon)
4. ⏳ Iniciar B1, B4, B6 em paralelo (nov 5 evening)
5. ⏳ Daily check-in: progresso vs timeline, riscos

---

## 📚 Referências

**Documentação de contexto:**
- `docs/audits/november_2026_audit_report.md` — Auditoria completa
- `docs/audits/frentes_status_consolidado.md` — Status F1/F2/F3
- `docs/architecture/technical_debt.md` — Dívida técnica detalhada
- `notebooks/ux_entrypoints_audit.md` — Auditoria UX (contexto T3)
- `.prompts/barosil.md` — Documento-mestre de trabalho

**Rastreamento:**
- `docs/audits/CHECKLIST_NOV_DEC_2026.md` — Checklist semanal
- `.prompts/barosil.md` — Snapshot e plano-mestre (atualizar semanal)

---

**Plano finalizado:** 2026-11-05  
**Status:** 🟢 Pronto para Execução  
**Timeline:** Nov 5–17 (2 semanas intensivas)  
**Merge Target:** `dev` branch  
**Próxima Revisão:** Nov 18 (pós-conclusão)
