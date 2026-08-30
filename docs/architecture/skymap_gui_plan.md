# Planejamento da interface gráfica de SkyMap (Hexagonal + DDD)

## 1. Objetivo da GUI

Definir uma camada de apresentação web para o bounded context **SkyMap** usando **Panel + HoloViews + Bokeh**, permitindo ao usuário:

- gerar mapas sintéticos;
- carregar surveys (HiPS/FITS) e reprojetar para HEALPix;
- executar análises estatísticas e espectrais;

sem expor detalhes de infraestrutura (providers, persistência, bibliotecas científicas concretas).

---

## 2. Escopo do MVP

O MVP cobre três fluxos funcionais principais:

1. **Generate**: geração de mapa sintético por frequência, NSide e componentes físicos.
2. **Survey**: carga de survey e padronização para HEALPix.
3. **Analyze**: leitura de FITS e cálculo de estatísticas + espectro angular.

Fora do escopo inicial:

- edição avançada de mapas;
- pipelines distribuídos complexos;
- comparação multi-mapa com cache persistente sofisticado;
- autenticação/autorização de usuários.

---

## 3. Casos de uso reutilizados (application/skymap)

A GUI **não cria regra científica nova**. Ela reutiliza casos de uso existentes no `application/skymap`, especialmente os equivalentes a:

- geração de mapa sintético;
- ingestão/carga de survey;
- análise estatística de pixels;
- cálculo de espectro angular;
- leitura/escrita de artefatos necessários ao fluxo SkyMap.

> Observação: a GUI deve consumir os **DTOs e contratos já existentes**, sem alterar assinaturas, sem duplicar algoritmos e sem mover lógica de domínio para a camada de interface.

---

## 4. Fluxos do MVP

### 4.1 Fluxo Generate

1. Usuário define frequência, NSide e componentes.
2. Controller valida entrada básica (formato/faixa mínima).
3. Controller monta DTO de entrada.
4. Chamada do caso de uso de geração em `application/skymap`.
5. Presenter transforma saída em:
   - metadados;
   - visualização do mapa;
   - histogramas;
   - mensagens de status.
6. Estado da GUI é atualizado.

### 4.2 Fluxo Survey

1. Usuário seleciona survey/catálogo e parâmetros de frame/unidade/resolução.
2. Controller valida entradas.
3. Controller chama caso de uso de carregamento/reprojeção.
4. Presenter converte saída em dados exibíveis.
5. Estado registra origem (`survey`) e parâmetros utilizados.

### 4.3 Fluxo Analyze

1. Usuário informa arquivo FITS e parâmetros de análise (ex.: `lmax`, Stokes).
2. Controller valida arquivo e parâmetros.
3. Chama caso de uso de análise.
4. Presenter prepara:
   - resumo estatístico;
   - gráfico do espectro angular;
   - tabela dos primeiros coeficientes Cℓ.
5. Estado persiste resultado da análise e mensagens.

---

## 5. Componentes visuais

- **Shell da aplicação** (Panel `Template`).
- **Aba Generate**:
  - frequência (GHz), NSide, componentes, frame/unidade.
- **Aba Survey**:
  - seleção de survey, parâmetros de reprojeção, área/campo de visão.
- **Aba Analyze**:
  - upload/caminho FITS, `lmax`, Stokes, opções de saída.
- **Painel de resultados**:
  - metadados, histogramas, mapa renderizado, espectro angular, tabela Cℓ.
- **Feedback do usuário**:
  - mensagens de sucesso/erro e indicador de processamento.

---

## 6. Estado da interface (`state.py`)

Estado mínimo (imutabilidade parcial e atualização controlada):

- `current_map` (referência ao mapa corrente/objeto de saída);
- `map_origin` (`generated`, `survey`, `fits`);
- `input_params` (últimos parâmetros válidos);
- `analysis_result` (estatísticas + espectro);
- `messages` (info/warn/error);
- `is_processing` (spinner/bloqueio de ações).

Recomendação: estado tipado com dataclasses ou outro mecanismo leve.
Pydantic poderá ser adotado caso já seja uma dependência oficial do projeto.

---

## 7. Controllers e Presenters

### Controllers (`controller.py`)

Responsabilidades:

- validar entrada de formulário (sem regra científica);
- construir DTOs para use cases;
- chamar serviços/casos de uso de `application/skymap`;
- capturar exceções de aplicação;
- acionar atualização de estado.

### Presenters (`presenters.py`)

Responsabilidades:

- converter DTOs de saída em ViewModel para widgets/gráficos;
- formatar métricas e metadados para exibição;
- normalizar mensagens de erro para usuário final;
- desacoplar detalhes do formato interno do domínio.

---

## 8. Composition Root (`bootstrap/skymap_gui.py`)

Toda montagem concreta deve ocorrer em:

`src/radioskysims/bootstrap/skymap_gui.py`

Responsabilidades:

- instanciar adapters concretos de infraestrutura;
- ligar portas aos adapters;
- criar instâncias dos casos de uso;
- injetar dependências na camada `interfaces/gui/skymap`;
- expor função de inicialização da aplicação Panel.

A GUI (`interfaces/gui`) recebe apenas dependências prontas (injeção), sem conhecimento de construção concreta.

---

## 9. Estrutura de diretórios proposta

```text
src/radioskysims/interfaces/gui/skymap/
    __init__.py
    app.py
    controller.py
    presenters.py
    state.py
    views.py
    widgets.py
```

Papéis:

- `app.py`: ponto de entrada da GUI Panel (layout global + roteamento de abas);
- `widgets.py`: fábricas de widgets e bindings;
- `views.py`: composição visual e atualização reativa;
- `state.py`: estado da UI;
- `controller.py`: coordenação de eventos e casos de uso;
- `presenters.py`: transformação de DTO -> ViewModel.

---

## 10. Regras de dependência (obrigatórias)

Arquitetura alvo:

**Panel GUI**  
`-> interfaces/gui/skymap`  
`-> application/skymap`  
`-> domain/skymap`  
`-> ports`  
`<- infrastructure/skymap`

Restrições:

- `interfaces/gui/skymap` **não pode**:
  - construir adapters concretos;
  - importar diretamente PySM3;
  - importar providers Healpy/HiPS;
  - importar `reproject`;
  - acessar persistência diretamente.
- Infraestrutura concreta só no `bootstrap/skymap_gui.py`.
- Nenhum algoritmo científico duplicado na GUI.

---

## 11. Tratamento de erros

Princípios:

- erro para usuário final deve ser legível e sem traceback;
- traceback detalhado apenas em logs de desenvolvimento;
- padronização de mensagens por presenter/controller.

Cenários mínimos:

- arquivo inexistente;
- FITS inválido;
- NSide inválido;
- frequência inválida;
- componentes vazios;
- survey sem pixels válidos;
- dependência opcional indisponível.

---

## 12. Estratégia de testes

### Unitários

- `controllers`: validação de entrada e roteamento de chamadas;
- `presenters`: transformação de saída e mensagens;
- `state`: transições de estado;
- `widgets/views`: contratos mínimos de binding e renderização básica.

### Integração

- GUI + casos de uso reais com adapters substituíveis/mocks;
- fluxos generate/survey/analyze com dados determinísticos;
- validação de boundary: GUI sem acesso direto à infraestrutura concreta.

### End-to-end

- inicialização da aplicação Panel;
- execução de ao menos um fluxo completo por aba;
- validação de elementos renderizados e mensagens.

Diretórios-alvo de testes:

- `tests/interfaces` (GUI/presentação);
- `tests/skymap` e `tests/application/services/skymap` (integração com use cases);
- `tests/e2e` (subida da app + fluxo mínimo).

---

## 13. Critérios de aceite

- GUI inicia e executa sem violar regras de dependência;
- três fluxos (generate, survey, analyze) disponíveis no MVP;
- casos de uso existentes são reutilizados;
- erros aparecem de forma controlada e amigável;
- sem alteração de contratos/DTOs/algoritmos científicos;
- testes existentes continuam passando;
- nova camada possui cobertura mínima de testes unitários e integração.

---

## 14. Riscos técnicos

- acoplamento indevido da GUI a detalhes de infraestrutura;
- custo de renderização de mapas grandes (latência/UI freeze);
- inconsistência de estado entre abas e operações longas;
- variação de dependências opcionais no ambiente local;
- regressão por mudanças em DTOs da aplicação;
- dificuldade de testes e2e de componentes reativos Panel.

Mitigações:

- injeção estrita via bootstrap;
- processamento assíncrono/controlado para tarefas longas;
- contratos de presenter estáveis;
- fixtures determinísticas para testes;
- verificação arquitetural em CI (imports proibidos na GUI).

---

## 15. Plano incremental de implementação

### Fase 0 — Preparação

- criar estrutura de diretórios `interfaces/gui/skymap`;
- criar `bootstrap/skymap_gui.py` apenas com composição básica;
- - verificar e organizar as dependências de GUI já existentes no `pyproject.toml`;
- evitar adicionar novas dependências sem necessidade.

### Fase 1 — Esqueleto da GUI

- layout principal com abas Generate/Survey/Analyze;
- estado mínimo e mensagens;
- controladores com stubs chamando use cases existentes.

### Fase 2 — Fluxo Generate

- formulário completo + validações;
- presenter para metadados, histograma e mapa;
- testes unitários do controller/presenter.

### Fase 3 — Fluxo Survey

- seleção survey + reprojeção;
- tratamento de erros específicos;
- testes de integração com adapters substituíveis.

### Fase 4 — Fluxo Analyze

- carga FITS + estatística + espectro angular;
- tabela Cℓ e gráficos;
- testes e2e básicos dos três fluxos.

### Fase 5 — Hardening

- revisão de dependências arquiteturais;
- melhoria de mensagens/logs;
- documentação final de uso e extensão em `docs/`.

### FLUXO DE ARQUITETURA
Panel GUI
→ interfaces/gui/skymap
→ application/skymap/use cases
→ domain/skymap

bootstrap/skymap_gui
→ cria os adapters de infrastructure/skymap
→ injeta os adapters nas portas da Application
→ injeta os casos de uso nos controllers da GUI