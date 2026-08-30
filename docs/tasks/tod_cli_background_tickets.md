# Tickets: CLI export TODs + Background runner + Notebook helpers

Este arquivo contém um breakdown de tickets pequenos, estimativas e critérios de aceitação para implementação do MVP das features "CLI export TODs" e "simulações non-blocking em notebooks".

## Epic: TOD export CLI + Job Runner (MVP)

- Estimated total: 80h (aprox. 10 dias úteis)

### TICKET 1 — `TOD-001` : Schema de settings e validador
- Estimativa: 4h
- Descrição: Definir schema mínimo para `settings.toml` usado nas execuções TOD; implementar validação leve (já existe utilitário `load_settings` e `validate_settings`). Incluir exemplos em `config/examples`.
- Critério de aceitação: Arquivo `config/examples/tod_settings_example.toml` presente; função `validate_settings(settings)` valida cenários mínimos e falha com mensagem clara.

### TICKET 2 — `TOD-002` : Módulo Job model + SQLite schema
- Estimativa: 8h
- Descrição: Implementar modelo simples de jobs com SQLite (tabela `jobs`) e API mínima para criar/atualizar/consultar jobs. Pode usar SQLAlchemy leve ou acesso direto via sqlite3.
- Critério de aceitação: Script de migração/initialização cria tabela `jobs`; testes unit validam lifecycle: create → update status → read.

### TICKET 3 — `TOD-003` : Runner foreground (CLI) — stub funcional
- Estimativa: 12h
- Descrição: Implementar comando CLI `radioskysims tod export --config PATH` que: carrega settings, executa uma run curta (simulação pequena) em foreground usando o pipeline existente (TODSimulator), mostra progresso em TTY (tqdm) e grava output em `output.outdir`.
- Critério de aceitação: Executar comando gera um NetCDF pequeno, exibe progresso e retorna exit code 0.

### TICKET 4 — `TOD-004` : Background runner MVP (subprocess)
- Estimativa: 16h
- Descrição: Implementar `--background` no CLI que cria um job no DB, spawna um subprocesso worker que executa o run, atualiza DB com status e grava log/progress file. Retorna job id imediatamente.
- Critério de aceitação: `radioskysims tod export --background` retorna job id; `jobs status <id>` mostra RUNNING → SUCCESS e output_path no DB.

### TICKET 5 — `TOD-005` : CLI jobs management (list/status/cancel)
- Estimativa: 8h
- Descrição: Criar comandos auxiliares: `radioskysims tod jobs list`, `radioskysims tod jobs status <id>`, `radioskysims tod jobs cancel <id>`.
- Critério de aceitação: Comandos retornam informações corretas e `cancel` sinaliza processo e grava CANCELLED.

### TICKET 6 — `TOD-006` : Progress persistence (file JSON) e monitor
- Estimativa: 6h
- Descrição: Padronizar formato de progresso (JSON: {percent, step, eta}) atualizado pelo worker; monitor no CLI lê o arquivo para exibir progresso no TTY e widget no notebook.
- Critério de aceitação: Worker escreve progresso e CLI/Notebook exibem corretamente, incluindo ETA aproximada.

### TICKET 7 — `TOD-007` : Notebook API (JobHandle) e widget
- Estimativa: 12h
- Descrição: Implementar função `run_simulation(settings_or_path, background=False, progress_callback=None)` que retorna `JobHandle` quando background; implementar widget básico (ipywidgets/Panel) para mostrar progresso e botão cancelar/foreground.
- Critério de aceitação: Notebook de exemplo inicia job em background, exibe widget com progresso e permite cancelar.

### TICKET 8 — `TOD-008` : Tests & CI integration
- Estimativa: 6h
- Descrição: Adicionar testes unitários e integração curta que executa um TOD pequeno; integrar no CI (pipeline de PR) execução dos testes rápidos.
- Critério de aceitação: Pipeline de CI executa testes e passa para as novas rotas; cobertura básica para parsing e job lifecycle.

### TICKET 9 — `TOD-009` : Docs Quickstart MyST + example notebook
- Estimativa: 4h
- Descrição: Adicionar página Quickstart em MyST que mostra como usar a CLI e o notebook example atualizado; incluir exemplos de config e screenshots do widget.
- Critério de aceitação: Página Quickstart renderiza e valida exemplos locais.

### TICKET 10 — `TOD-010` : Cleanup e checklist de release
- Estimativa: 4h
- Descrição: Revisar docs, remover documentos históricos listados, atualizar `CHANGELOG` e preparar notas de release.
- Critério de aceitação: PR de release com changelog e guideline de migração.

---

Cada ticket deve ser implementado em branch `feat/tod-<ticket>` e submetido via PR com testes e documentação mínima.
