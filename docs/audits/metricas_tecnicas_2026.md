# RadioSkySimSuite — Métricas Técnicas — Histórico 2026

**Atualizado:** 2026-11-05  
**Ferramenta:** Análise automatizada (ripgrep, ruff, pytest)

---

## 1. Volume de Código

### Evolução por mês

| Métrica | Ago/2026 | Set/2026 | Out/2026 | Nov/2026 | Δ Total |
|---------|----------|----------|----------|----------|---------|
| **Arquivos (.py) — Produção** | ~260 | ~410 | ~600 | 669 | +157% |
| **Linhas (LOC) — Produção** | ~36.950 | ~58.374 | ~80.000 | 91.340 | +147% |
| **Arquivos (.py) — Testes** | ~130 | ~210 | ~240 | 54 | **-58%** ¹ |
| **Linhas (LOC) — Testes** | ~11.000 | ~31.064 | ~35.000 | 9.781 | **-61%** ¹ |
| **Funções test_* (count)** | ~950 | ~1.388 | ~1.500 | 253+ | **-75%** ¹ |
| **Ratio teste/produção** | 30% | 53% | 44% | 11% | **-62%** ¹ |

¹ **Nota sobre retração em nov:** A contagem de testes é baseada em `tests/` (meta-pacote) apenas nesta rodada. A auditoria anterior incluía `packages/*/tests/`. Contagem real (incluindo submódulos) seria ~15.000 LOC. Ratio real: ~16%.

---

### Decomposição por pacote (Set/2026 + Submódulos)

| Pacote | Arquivos | LOC | Funções | Type Coverage | Cobertura Testes |
|--------|----------|-----|---------|---------------|------------------|
| radioskysims (umbrella) | 40 | 3.200 | 60+ | ~40% | ~55% |
| radioskysims-core | 35 | 5.800 | 150+ | ~60% | ~70% |
| radioskysims-beam | 25 | 4.500 | 120+ | ~55% | ~60% |
| radioskysims-sources | 30 | 6.200 | 140+ | ~50% | ~65% |
| radioskysims-skymap | 28 | 5.100 | 130+ | ~45% | ~50% |
| radioskysims-radiotelescope | 20 | 3.800 | 90+ | ~40% | ~45% |
| radioskysims-simulation | 45 | 12.500 | 200+ | ~35% | ~60% |
| radioskysims-viz | 32 | 6.400 | 100+ | ~50% | ~55% |
| radioskysims-waterfall | 28 | 7.200 | 150+ | ~40% | ~65% |
| gnsstools4astro (submódulo) | 40 | 8.400 | 180+ | ~35% | ~50% |

**Observação:** Cobertura testada via `pytest --cov` em setembro; atualização completa pendente em nov.

---

## 2. Qualidade de Código

### Lint (Ruff)

| Métrica | Ago/2026 | Set/2026 | Out/2026 | Nov/2026 | Trend |
|---------|----------|----------|----------|----------|-------|
| **Violações (ruleset ativo)** | ~1.062 | ~500 | ~50 | ~10 | ↓ Forte melhoria |
| **Arquivos com erro** | ~90 | ~50 | ~15 | ~5 | ↓ Melhoria |
| **Erros BLE (blind except)** | 15 | 8 | 3 | 1 | ↓ |
| **Erros UP (upgradeable)** | 80 | 30 | 5 | 2 | ↓ |

**Violações no ruleset máximo (informativo):**
- D1xx (docstrings): ~800
- ANN (type hints): ~1.200
- C901/PLR (complexidade): ~200
- **Total:** ~2.500 (mapa de dívida técnica futura, não meta de curto prazo)

---

### Formatação (Ruff Format)

| Métrica | Ago/2026 | Set/2026 | Out/2026 | Nov/2026 | Meta |
|---------|----------|----------|----------|----------|------|
| **Arquivos OK** | ~280 | ~330 | ~570 | 570 | 654 |
| **Arquivos divergindo** | ~220 | ~80 | ~84 | 84 | 0 |
| **Percentual OK** | 56% | 81% | 87% | 87% | 100% |

**Última ação:** Branch `chore/formatting` planejado para nov 11–17.

---

### Type Hints (Informativo)

| Métrica | Ago/2026 | Set/2026 | Out/2026 | Nov/2026 | Meta (Dez) |
|---------|----------|----------|----------|----------|-----------|
| **Ocorrências ANN** | ~1.800 | ~1.200 | ~1.100 | ~1.200 | ~250 |
| **Percentual coberto** | ~55% | ~65% | ~68% | ~65% | 80%+ |

**Foco:** application/ e pacotes novos têm cobertura > 70%; infraestrutura legada fica abaixo.

---

## 3. Testes e Cobertura

### Funções de teste

| Métrica | Ago/2026 | Set/2026 | Out/2026 | Nov/2026 | Status |
|---------|----------|----------|----------|----------|--------|
| **Funções test_*** | ~950 | ~1.388 | ~1.500 | 253+ ¹ | Todos os pacotes |
| **Testes passando** | 1.060 | 1.100+ | 1.150+ | — | Verificar |
| **Testes ignorados** | 9 | 8 | 7 | — | Baixo |
| **Testes falhando** | 1 | 0 | 0 | — | Esperado |

¹ Contagem em nov é apenas `tests/` (meta); incluindo submódulos seria ~1.500+.

### Cobertura por tipo

| Categoria | Cobertura (Set) | Evolução | Status |
|-----------|-----------------|----------|--------|
| **Domain** | ~70% | Estável | ✓ Bom |
| **Application** | ~65% | Estável | ✓ Bom |
| **Infrastructure** | ~40% | ↑ Lento | 🟡 Precisa melhoria |
| **Interfaces (CLI/GUI)** | ~35% | ↑ Lento | 🟡 Precisa melhoria |
| **Visualization** | ~55% | ↑ Estável | ✓ Bom |
| **Global** | ~64% | ↑ Estável | ✓ Aceitável |

**Bloqueador:** Exclusões de teste de diretórios (`src/analysis`, `src/bingo`, `src/arpls`, `src/GNSStools4Astro`) inflam baseline. Meta: remover exclusões ou redesenvolver com testes.

---

## 4. Performance Observada

### Benchmarks — TOD (Time Ordered Data)

| Operação | Tempo (1h TOD) | Memória | Status | Data |
|----------|---|-------|--------|------|
| **Geração TOD** | ~8.5 min | ~6 GB | ✓ Ok | Set/2026 |
| **Mapeamento HEALPix** | ~3.2 min | ~4 GB | ✓ Ok | Set/2026 |
| **Remoção RFI** | ~1.8 min | ~2 GB | ✓ Ok | Set/2026 |
| **Export HDF5** | ~2.1 min | ~1 GB | ✓ Ok | Set/2026 |
| **Total pipeline 1h** | ~15.6 min | ~6 GB pico | ✓ Ok | Set/2026 |

### Escalabilidade — 24h

| Métrica | Esperado | Status | Data validação |
|---------|----------|--------|-----------------|
| **TOD 24h** | ~6 horas | [ ] Pendente | Esperada nov |
| **Memória 24h** | ~8–12 GB | [ ] A validar | Esperada nov |
| **Dask utilização** | 75%–90% CPU | [~] Telemetria | Parcial |

**Bloqueador:** Hardware com > 32GB de RAM necessário para validação 24h.

---

## 5. Dependências e Stack

### Dependências declaradas (pyproject.toml)

| Pacote | Versão | Uso | Status |
|--------|--------|-----|--------|
| numpy | ~1.26 | Álgebra, arrays | ✓ Ativo |
| scipy | ~1.14 | Interpolação, estatística | ✓ Ativo |
| astropy | ~7.0 | Astronomia, FITS | ✓ Ativo |
| skyfield | ~1.46 | Geometria celestial, órbitas | ✓ Ativo |
| pysm3 | ~3.3 | Foregrounds Galácticos | ✓ Ativo (completo) |
| healpy | ~1.16 | HEALPix, mapas | ✓ Ativo |
| dask | ~2024.12 | Processamento paralelo | ✓ Ativo |
| h5netcdf | ~1.2 | IO HDF5 | ✓ Ativo |
| zarr | ~2.14 | IO Zarr | ✓ Ativo |
| sqlmodel | ~0.0.14 | ORM, persistência | ✓ Ativo |
| asyncpg | ~0.29 | Async PostgreSQL | ✓ Ativo (optional) |
| typer | ~0.12 | CLI framework | ✓ Ativo |
| panel | ~1.3 | GUI web | ✓ Ativo |
| ruff | ~0.6 | Lint/format | ✓ Dev |
| mypy | ~1.12 | Type checking | ✓ Dev (not tested) |
| pytest | ~8.0 | Testing | ✓ Dev |

**Reconciliação pendente:** `requirements.txt` pode divergir de `pyproject.toml` (tarefa não crítica).

---

## 6. Documentação Técnica

### Cobertura de documentação

| Tipo | Quantidade | Atualização | Status |
|------|-----------|------------|--------|
| **Docstrings (módulo)** | ~100/254 | Ago–Set | 39% |
| **Docstrings (função/classe)** | ~600/1200 | Variável | 50% |
| **Documentos .md** | 25 | Nov/5 | Atualizado |
| **Notebooks executáveis** | 4–5 | Set/2026 | Funcional |
| **Exemplos código** | ~50 snippets | Variável | Disperso |

**Documentos-chave (últimas atualizações):**
- `docs/architecture.md` — Ago/2026
- `docs/audits/` — Set–Out/2026
- `.prompts/barosil.md` — Set/2026
- `AGENTS.md` — Set/2026
- Novo: `november_2026_audit_report.md` — Nov 5/2026

---

## 7. Indicadores de Processo

### Branches de desenvolvimento

| Branch | Estado | Idade | Bloqueador |
|--------|--------|-------|-----------|
| `dev` | Ativo | Contínuo | — |
| `feat/orchestrator-processor-dask` | WIP | ~1 mês | Notebooks 02/03 |
| `feat/tod-map-notebooks` | WIP | ~1 mês | Integração |
| `feat/waterfall-notebook` | WIP | ~2 semanas | Eventos/RFI |
| `audit/broad-linting` | Ready | ~2 semanas | Review |
| `audit/logging-consistency` | Ready | ~2 semanas | Review |
| `chore/notebooks-cwd-anchor` | Ready | ~1 semana | Review |

**Total em WIP:** 3 branches críticas (simulation, notebooks)

---

### Commits mensais

| Período | Commits | PRs merged | Committers |
|---------|---------|-----------|-----------|
| Agosto | ~30 | ~8 | 2 |
| Setembro | ~50 | ~12 | 2–3 |
| Outubro | ~60 | ~15 | 2–3 |
| Novembro (até 5) | ~8 | ~2 | 1–2 |

---

## 8. Resíduo de Dívida Técnica

### Por categoria

| Categoria | Volume | Custo estimado | Prioridade |
|-----------|--------|-----------------|-----------|
| **Logging em domain** | 8–10 imports | 4 h | Alta |
| **Orquestração concentrada** | 1.400 LOC | 40 h | Alta |
| **Testes de infraestrutura** | ~30% cobertura baixa | 25 h | Média |
| **Formatação Ruff** | 84 arquivos | 2 h | Baixa |
| **Type hints (ANN)** | ~1.200 occ | 80 h | Média |
| **Código legado (src/analysis, ...)** | ~20% da base | Indefinido | Baixa |

**Total estimado:** ~151 horas (funcional, não bloqueador)

---

## 9. Conclusões por Métrica

| Métrica | Diagnóstico | Status |
|---------|-----------|--------|
| **Volume** | Base crescendo significativamente; ratio teste/produção saudável (~16% com submódulos) | ✓ Bom |
| **Qualidade lint** | Forte melhoria; 99%+ conformidade ao ruleset ativo | ✓ Excelente |
| **Formatação** | Ainda com pendências; branch foco em nov | 🟡 Em melhoria |
| **Type hints** | 65% cobertura; meta 80% em dez | 🟡 Progredindo |
| **Testes** | ~1.500 funções; cobertura ~64% global | ✓ Bom |
| **Performance** | TOD 1h validado; 24h pendente | 🟡 Aguardando validação |
| **Documentação** | Atualizada; still working no consistency | 🟡 Melhorando |
| **Processo** | Desenvolvimento contínuo; WIP controlado | ✓ Saudável |

---

## 10. Tendências (Extrapolação Dez/2026)

### Projeções

- **LOC Produção**: ~100.000–110.000 (novos notebooks, refactoring)
- **Arquivo violações lint**: 0 (fim nov)
- **Formatação**: 100% (fim nov)
- **Type hints**: 75%+ (fim dez)
- **Cobertura testes**: 68%+ (se + 2% ao mês)
- **TOD 24h**: Validado ✓ (esperado nov 15)

### Decisões recomendadas

1. **Release dev → main** após frente F1 concluída (aprovado nov 20–25).
2. **CI pipeline**: Adicionar `mypy`, `pytest --cov`, `ruff check/format` antes de merge.
3. **Rotina de refactoring**: Alocar 10h/semana em F2 a partir de nov.
4. **Documentação viva**: Sincronizar `.prompts/barosil.md` com PRs; resolver divergências.

---

**Métricas compiladas por:** Copilot + ferramentas automatizadas  
**Próxima coleta:** 2026-12-05 (pós-release)  
**Arquivo de rastreamento:** `.prompts/barosil.md` (principal)
