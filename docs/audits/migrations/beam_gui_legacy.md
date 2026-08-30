# BEAM-002 — Visualizador Beam legado

## Arquivo analisado

`src/radioskysims/interfaces/gui/beam_visualizer.py`

## Problemas identificados

- Utilizava o import inválido `from domain.beam import Beam`.
- Dependia da API Beam legada:
  - `beam.pattern`
  - `beam.name`
- Utilizava Matplotlib, divergindo da stack de GUI adotada:
  - Panel
  - HoloViews
  - Bokeh
- Não possuía consumidores ativos no código ou nos testes.
- Sua funcionalidade está coberta pelo `application/beam_panel.py`,
  já migrado para o modelo oficial `radioskysims.domain.beam.Beam`.

## Classificação

Decisão: `REMOVE`

Severidade anterior: P1 — Alta

## Justificativa

A adaptação do arquivo produziria uma segunda implementação concorrente da
visualização Beam. A remoção reduz duplicação e consolida a interface existente.
