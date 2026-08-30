> **Documento histórico** — snapshot com ``as-of: 2026-08-05`` (comparação docs
> vs. código da época). Não deve orientar decisões correntes; veja o estado
> atual em `docs/architecture.md`.

# Relatório de Divergências — Docs vs Código (Agosto/2026)

**Data:** 2026-08-05  
**Base:** branch `dev`  
**Objetivo:** registrar diferenças entre documentação e estado real da base de código, com priorização e ação recomendada.

---

## Escopo e método

Este documento compara afirmações dos relatórios/documentos em `docs/` contra evidências diretas no código-fonte (`src/`, `tests/`) coletadas no mesmo dia.

Critérios:
- **Outdated**: quando a afirmação não corresponde mais ao código atual.
- **Parcialmente válido**: quando o diagnóstico continua útil, mas os números/artefatos específicos mudaram.

---

## Matriz de divergências

| Documento | Afirmação documentada | Evidência no código atual | Status | Impacto | Prioridade | Ação recomendada |
|---|---|---|---|---|---|---|
| `docs/architecture/dependency_injection.md` | “0 imports diretos de Infrastructure dentro de Application” | Há imports diretos em `application/services/catalog_services.py`, `application/services/sim_orchestrator.py`, `application/services/simulation_service.py` | **Outdated** | Pode induzir falsa sensação de fechamento da Sprint 2.4 | **P0** | Atualizar texto para “redução parcial” + lista de pendências residuais e plano para zerar |
| `docs/architecture/current_architecture.md` | Diagnóstico inclui `domain/satellite/main.py` como problema ativo | `src/radioskysims/domain/satellite/main.py` não existe mais | **Outdated** | Ruído de diagnóstico e dívida já removida | **P1** | Marcar item como “resolvido” e inserir data de resolução |
| `docs/architecture/technical_debt.md` | TD-004/TD-007 citam artefatos específicos ainda críticos | Não há `domain/satellite/main.py`; varredura sintática atual encontrou **0 compile errors** | **Outdated (parcial)** | Backlog perde confiabilidade se itens já resolvidos permanecem abertos | **P0** | Reclassificar TDs: `resolvido`, `em aberto`, `revalidar`; manter histórico sem apagar contexto |
| `docs/architecture/module_dependencies.md` | Cita duplicidade `infrastructure/files/*` vs `infrastructure/beams/loaders/*` | Não existe `src/radioskysims/infrastructure/files/**/*.py`; somente `infrastructure/beams/loaders/*` | **Outdated** | Pode direcionar refactor para caminho inexistente | **P1** | Revisar seção de duplicidade para refletir estrutura atual real |
| `docs/code_quality.md` | Snapshot de lint/testes (ex.: 797 issues; 843 testes) | Atual: `ruff` reporta **811**; `pytest --collect-only -q --ignore=data/DB` coletou **860** | **Outdated (métricas)** | Decisões de qualidade com números vencidos | **P0** | Atualizar métricas e adicionar “as-of date” obrigatória em cada bloco quantitativo |
| `docs/_archive/reports_2026-01/SUMARIO_EXECUTIVO.md` | Scorecards e roadmap fechados em snapshot antigo | Parte continua útil conceitualmente, mas números/estado divergiram | **Parcialmente válido** | Bom para visão estratégica; fraco para status operacional | **P2** | Inserir banner “relatório histórico” + link para snapshot atual |
| `docs/_archive/reports_2026-01/ANALISE_RADIOSKYSIM.md` | Recomendações e percentuais de cobertura/estado em janela antiga | Base atual mudou (módulos, testes, lint, acoplamentos residuais) | **Parcialmente válido** | Pode ser lido como status atual sem ser | **P2** | Incluir seção “diferenças para 2026-08” e status de validade temporal |

---

## Evidências objetivas coletadas no código (2026-08-05)

### Arquitetura e acoplamento

- `application -> infrastructure` ainda presente (exemplos):
  - `src/radioskysims/application/services/catalog_services.py:35`
  - `src/radioskysims/application/services/sim_orchestrator.py:28,262,266,436`
  - `src/radioskysims/application/services/simulation_service.py:87`
- `domain -> application` ainda presente (exemplos):
  - `src/radioskysims/domain/geometry/interface.py:18`
  - `src/radioskysims/domain/geometry/skyfield_provider.py:7`
  - `src/radioskysims/domain/simulation/simulation.py:1045`

### Estado técnico

- Sintaxe/compilação (AST parse em `src/radioskysims`): **0 erros**.
- Testes coletáveis: **860** (com `--ignore=data/DB`).
- Lint (`ruff check src tests scripts --statistics`): **811 erros**.

### Estrutura de módulos (amostra)

- `src/radioskysims/domain/satellite/main.py`: **ausente**.
- `src/radioskysims/infrastructure/files/**/*.py`: **ausente**.
- `src/radioskysims/infrastructure/beams/loaders/*.py`: **presente**.

---

## Priorização de atualização documental

### Lote 1 (imediato)

1. `docs/architecture/dependency_injection.md`
2. `docs/architecture/technical_debt.md`
3. `docs/code_quality.md`

### Lote 2 (curto prazo)

4. `docs/architecture/current_architecture.md`
5. `docs/architecture/module_dependencies.md`

### Lote 3 (higiene editorial)

6. `docs/_archive/reports_2026-01/SUMARIO_EXECUTIVO.md`
7. `docs/_archive/reports_2026-01/ANALISE_RADIOSKYSIM.md`

---

## Proposta de padrão para evitar novo descompasso

Adicionar em todo relatório técnico:

- campo obrigatório `As of: YYYY-MM-DD`;
- seção `Validade do snapshot` (ex.: 30 dias);
- seção `Como reproduzir métricas` com comandos;
- tags de status por item: `ativo`, `resolvido`, `revalidar`.

---

## Conclusão

A documentação do projeto está rica, mas parte dela já mistura **histórico** com **estado atual**. A correção recomendada não é apagar histórico, e sim explicitar validade temporal e status de cada diagnóstico. Assim, o time preserva aprendizado e evita decisões com base em snapshot vencido.
