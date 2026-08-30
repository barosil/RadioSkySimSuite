# Relatório Técnico e Auditoria do Módulo SkyMap

**Projeto:** RadioSkySim  
**Contexto:** `skymap`  
**Data:** 23 de julho de 2026  
**Tipo:** auditoria documental, arquitetural, funcional e didática

## 1. Resumo executivo

O contexto `skymap` foi evoluído de um conjunto de classes científicas para um módulo utilizável de ponta a ponta. A solução atual cobre representação HEALPix, criação e transformação de mapas, análise estatística e espectral, geração sintética, ingestão de surveys, FITS, visualização, CLI instalável, GUI web e notebook de demonstração.

A arquitetura segue o fluxo:

```text
Interfaces (CLI/GUI)
        -> Application (casos de uso e ports)
        -> Domain (entidades e regras científicas)
        <- Infrastructure (Healpy, PySM3, HiPS, FITS)

Bootstrap cria as dependências concretas e as injeta nas interfaces.
```

A última suíte global explicitamente compartilhada na sessão apresentou **714 testes aprovados, 13 ignorados, 1 xfail esperado e 0 falhas**. Depois dessa execução foram validados manualmente os fluxos Survey e Analyze da GUI; recomenda-se registrar uma nova execução global no commit final para fechar a evidência de release.

## 2. Escopo implementado

- Domínio HEALPix com `NSide`, `SkyMapDataset` e `SkyMap`.
- Máscaras, suavização, rotação, mudança de resolução e transformadas harmônicas.
- Estatísticas e espectro angular C_l.
- Casos de uso Generate, Survey e Analyze.
- Adapters PySM3, Healpy e HiPS/FITS.
- Visualização, cache, download e telemetria.
- CLI `radioskysims` com saída textual e JSON.
- GUI Panel com Generate, Survey e Analyze.
- Notebook `skymap_howto.ipynb` como guia executável.
- Testes unitários, integração, contratos, performance e E2E.

## 3. Como pensar o módulo

- **Domain:** sabe o que é um mapa válido e como operações científicas se comportam.
- **Application:** sabe qual sequência executar para atender uma intenção do usuário.
- **Infrastructure:** sabe conversar com Healpy, PySM3, FITS, HiPS e sistema de arquivos.
- **Interfaces:** recebe parâmetros e apresenta resultados.
- **Bootstrap:** monta o sistema real sem acoplar as camadas internas.

## 4. Inventário dos módulos

### 4.1 Domain

| Módulo | Função | Observação |
|---|---|---|
| __init__.py | Define a API pública do contexto de domínio e concentra os tipos mais usados. | Importações mais simples para NSide, SkyMap, SkyMapDataset e serviços centrais. |
| exceptions.py | Centraliza exceções específicas do contexto SkyMap. | Separa erros de dataset, NSide e análise de exceções genéricas do Python. |
| value_objects.py | Implementa NSide e SkyMapDataset. | NSide valida a resolução HEALPix; SkyMapDataset abstrai NumPy, Xarray, Dask Array e Dask Delayed. |
| models.py | Implementa a entidade SkyMap. | Mantém dados e metadados, cópia defensiva, igualdade/hash, máscara e transformações harmônicas alm/from_alm. |
| factory.py | Padroniza a criação de SkyMap. | Aplica valores padrão, normaliza nside int/NSide e evita construção inconsistente da entidade. |
| analysis.py | Serviço científico de análise. | Média, RMS, mínimo/máximo e espectro angular C_l. |
| mask.py | Aplica máscaras binárias ou ponderadas. | Valida arrays e compatibilidade de forma antes de multiplicar mapa e máscara. |
| operations.py | Transformações de mapa. | Suavização, rotação e mudança de resolução HEALPix (downgrade/upgrade conforme API disponível). |
| generator.py (removido) | Shim legado que não gerava mapas e apenas lançava RuntimeError. | A remoção evita API obsoleta; geração concreta pertence à infraestrutura via port. |
| utils.py (removido) | Misturava filesystem e Healpy dentro do domínio. | A remoção corrige a direção arquitetural; helpers técnicos foram mantidos na infraestrutura. |

### 4.2 Application

| Módulo | Função | Observação |
|---|---|---|
| dto.py | Contratos de entrada e saída dos casos de uso. | Transporta frequência, NSide, componentes, caminho FITS, lmax e resultados sem expor detalhes de GUI/CLI. |
| ports.py | Portas abstratas da arquitetura Hexagonal. | Define contratos para gerador, analisador e providers, permitindo fakes nos testes e adapters reais no bootstrap. |
| generate.py | Orquestra geração e survey. | GenerateSkyMapUseCase usa SkyMapGeneratorPort; ContinuumSurveyMapUseCase usa provider de survey. |
| analyze.py | Orquestra análise científica. | AnalyzeSkyMapUseCase recebe SkyMap e lmax, chama SkyMapAnalyzerPort e devolve DTO com C_l e metadados. |

### 4.3 Infrastructure

| Módulo | Função | Observação |
|---|---|---|
| providers/pysm.py | Adapter de geração sintética. | Conecta GenerateSkyMapUseCase ao PySM3 e devolve SkyMap coerente com o domínio. |
| providers/healpy.py | I/O e transformações HEALPix/FITS. | Lê, grava e manipula mapas com Healpy sem contaminar Domain/Application com detalhes externos. |
| providers/hips.py | Ingestão de survey HiPS/FITS. | Lê o FITS local do survey, reprojeta WCS para HEALPix e adapta resolução HEALPix quando necessário. |
| adapters/analysis.py | Implementação de SkyMapAnalyzerPort. | Calcula C_l com Healpy e valida tipos/dimensionalidade antes de acessar ndim. |
| adapters/visualization.py | Visualização científica e exportação. | Plota e salva mapa e espectro angular sem levar bibliotecas gráficas ao domínio. |
| io/cache | Cache de produtos e resultados. | CacheStore, HybridCache, chaves e decorator cacheable para reduzir recomputação. |
| io/download.py | Download controlado de arquivos. | Isola rede, validação e persistência de artefatos obtidos externamente. |
| telemetry.py | Medição estruturada. | Registra duração, sucesso/falha e eventos para diagnóstico e desempenho. |
| utils.py | Helpers técnicos HEALPix. | expected_npix, validate_healpix_map, ensure_float_array e mask_invalid. |

### 4.4 CLI

| Módulo | Função | Observação |
|---|---|---|
| interfaces/cli/__main__.py | Permite executar python -m radioskysims.interfaces.cli. | Encaminha a execução ao main da CLI. |
| interfaces/cli/main.py | Parser principal e roteamento de subcomandos. | Cria a árvore radioskysims skymap {generate,survey,analyze}. |
| interfaces/cli/commands/ | Handlers dos três fluxos. | Convertem argumentos em chamadas aos casos de uso e retornam códigos de saída. |
| interfaces/cli/formatters.py | Saída text e JSON. | Mantém a formatação separada da orquestração e facilita integração externa. |
| bootstrap/skymap_cli.py | Composition Root da CLI. | Cria adapters concretos, casos de uso e o comando instalável. |
| pyproject.toml | Entry point do pacote. | Registra radioskysims = radioskysims.bootstrap.skymap_cli:main. |

### 4.5 GUI

| Módulo | Função | Observação |
|---|---|---|
| state.py | Estado da sessão da GUI. | Mapa atual, origem, parâmetros, resultado de análise, mensagens e indicador de processamento. |
| presenters.py | Converte DTOs/resultados em ViewModels. | Prepara metadados, histograma, preview, cobertura e espectro sem importar infraestrutura. |
| controller.py | Coordena eventos Generate/Survey/Analyze. | Constrói DTOs, chama casos de uso injetados, atualiza estado e normaliza erros. |
| widgets.py | Cria controles Panel. | Frequência, NSide, componentes, survey, coordenadas, caminho FITS, lmax e botões. |
| views.py | Renderiza painéis e gráficos. | Mensagens, metadados, mapa, histograma, cobertura, espectro C_l e tabela. |
| app.py | Monta a aplicação Panel. | Conecta callbacks, abas e Reset; não inicia servidor durante importação. |
| bootstrap/skymap_gui.py | Composition Root da GUI. | É o único ponto que cria PySM, HiPS e Healpy e os injeta no controller. |

## 5. Guia de utilização

### 5.1 Instalação editável

```bash
conda activate radiosky
python -m pip install -e .
which radioskysims
radioskysims --help
```

### 5.2 CLI - gerar mapa

```bash
radioskysims skymap generate \
  --frequency-ghz 30 \
  --nside 8 \
  --components synchrotron dust
```

### 5.3 CLI - carregar survey NVSS

```bash
radioskysims skymap survey \
  --survey-id NVSS \
  --ra-deg 180 \
  --dec-deg 0 \
  --fov-deg 2 \
  --nside 64 \
  --frequency-ghz 1.4 \
  --field I \
  --base-path outputs/skymap_howto/hips_provider
```

O arquivo esperado é `outputs/skymap_howto/hips_provider/NVSS.fits`.

### 5.4 CLI - analisar FITS HEALPix

```bash
radioskysims skymap analyze \
  --input outputs/skymap_howto/analytic_skymap_healpix.fits \
  --lmax 16 \
  --unit uK_CMB \
  --frame galactic \
  --field I
```

Para integração com scripts, acrescente `--output-format json`.

### 5.5 GUI

```bash
python -m radioskysims.bootstrap.skymap_gui
```

Abra o endereço exibido no terminal. A GUI possui três abas:

- **Generate:** frequência, NSide e componentes físicos.
- **Survey:** catálogo, coordenadas, FOV, NSide e diretório do FITS.
- **Analyze:** caminho FITS, lmax, unidade, frame e Stokes.

### 5.6 API Python - criar e analisar mapa

```python
import numpy as np
from radioskysims.domain.skymap import NSide, SkyMap, SkyMapAnalysis

nside = NSide(16)
data = np.ones(nside.npix, dtype=np.float64)

sky_map = SkyMap.from_array(
    data=data,
    nside=nside,
    unit="K",
    frame="galactic",
    freq_ghz=30.0,
    field="I",
)

mean = SkyMapAnalysis.mean(sky_map.data)
rms = SkyMapAnalysis.rms(sky_map.data)
minimum, maximum = SkyMapAnalysis.min_max(sky_map.data)
cls = SkyMapAnalysis.angular_power_spectrum(sky_map.data, lmax=16)
```

### 5.7 API Python - máscaras e operações

```python
import numpy as np
from radioskysims.domain.skymap.mask import SkyMask
from radioskysims.domain.skymap.operations import SkyMapOperations

mask = np.ones_like(sky_map.data)
mask[:100] = 0.0
masked = SkyMask.apply(sky_map.data, mask)
smoothed = SkyMapOperations.smooth(sky_map.data, fwhm_rad=0.01)
downgraded = SkyMapOperations.downgrade(sky_map.data, target_nside=NSide(8))
```

### 5.8 Notebook

Abra `notebooks/notebooks/bagunca/skymap_howto.ipynb`, selecione o kernel **Python (radiosky)** e execute as células em ordem. O notebook cobre Domain, Application, Infrastructure, HiPS/NVSS, visualização, cache, telemetria e fluxo end-to-end.

## 6. Regras de uso importantes

1. `NSide` deve ser válido para HEALPix, normalmente potência de 2.
2. O número de pixels é `12 * NSide**2`.
3. A frequência dos DTOs e interfaces é informada em GHz.
4. Survey usa um FITS local previamente obtido do HiPS.
5. Analyze espera um FITS HEALPix compatível.
6. Arquivos em `outputs/` são artefatos reproduzíveis e devem permanecer ignorados pelo Git.
7. GUI e CLI não devem construir adapters concretos; isso pertence ao bootstrap.

## 7. Auditoria de qualidade

| Critério | Avaliação | Fundamentação |
|---|---|---|
| Arquitetura | Muito boa | Separação Domain/Application/Infrastructure/Interfaces e Composition Roots dedicados. |
| Modelagem científica | Muito boa | NSide, SkyMapDataset e SkyMap tornam invariantes explícitos. |
| Testabilidade | Muito boa | Ports, fakes e cobertura em domínio, aplicação, interfaces e E2E. |
| Usabilidade | Boa a muito boa | Notebook, CLI e GUI cobrem perfis técnico, automatizado e interativo. |
| Observabilidade | Boa | Telemetria, logging e mensagens controladas de erro. |
| Prontidão de produção científica | Boa, com hardening pendente | Browser E2E, dependências opcionais e certificação pós-alteração final ainda merecem pipeline formal. |

## 8. Riscos e recomendações

| Risco | Impacto | Recomendação |
|---|---|---|
| Dependências opcionais científicas | Ambientes incompletos podem falhar na coleta/importação. | Organizar extras test/gui/science e manter lock/environment reproduzível. |
| Artefatos locais FITS | Survey/Analyze dependem de arquivos em outputs que podem ser removidos. | Criar comandos/documentação de obtenção e fixtures pequenas determinísticas. |
| Mapas grandes na GUI | Renderização síncrona pode bloquear a interface. | Amostragem para preview, tarefas assíncronas e limites de NSide para visualização. |
| Cobertura final da GUI | A última cobertura compartilhada foi 84% durante o estágio Generate. | Executar cobertura após Survey/Analyze e registrar a referência no CI. |
| E2E da GUI | O E2E formal existente é da CLI, não do navegador. | Adicionar Playwright/Selenium apenas como hardening posterior. |
| Contrato de caminhos | Base path x arquivo completo pode confundir usuários. | Padronizar nomenclatura e mostrar caminho resolvido antes de executar. |

## 9. Estratégia de testes

- **Unitários de domínio:** NSide, datasets, entidade, factory, análise, máscaras e operações.
- **Application:** DTOs, ports e casos de uso com fakes.
- **Infrastructure:** contratos de adapters, FITS, análise, visualização e integrações.
- **Interfaces:** parser/formatadores da CLI e estado/controller/presenters/callbacks da GUI.
- **E2E:** execução real da CLI Analyze por subprocesso com FITS temporário.
- **Suíte global:** última evidência compartilhada foi 714 passed, 13 skipped, 1 xfailed, 0 failed.

Comandos recomendados:

```bash
python -m pytest -q tests/interfaces/gui/skymap
python -m pytest -q tests/skymap tests/application/services/skymap tests/interfaces tests/e2e
python -m pytest -q
python -m pytest --cov=src/radioskysims/interfaces/gui/skymap --cov-report=term-missing -q tests/interfaces/gui/skymap
```

## 10. Troubleshooting

### Executável `radioskysims` não encontrado

```bash
python -m pip install --no-deps --no-cache-dir -e .
hash -r
which radioskysims
```

### Survey informa arquivo inexistente

Confirme o diretório e o arquivo:

```bash
find . -type f -iname 'NVSS*.fits' -print
```

No campo Base Path use o diretório que contém `NVSS.fits`, não um caminho inexistente.

### Analyze não encontra o FITS

```bash
find . -type f -iname '*.fits' -print
```

Use o caminho completo ou relativo à raiz do repositório.

### NSide inválido

Use valores como 1, 2, 4, 8, 16, 32, 64. Verifique também se o array possui exatamente `12 * NSide**2` pixels.

### Interface lenta

Reduza o NSide para preview e mantenha o mapa científico original fora da renderização detalhada.

## 11. Conclusão

O módulo SkyMap atingiu o objetivo de MVP científico integrado. O domínio está explícito, os casos de uso estão desacoplados por ports, as integrações estão isoladas na infraestrutura e o usuário dispõe de notebook, CLI e GUI para os mesmos fluxos principais. A evolução futura deve se concentrar em automação de browser, gerenciamento formal de dependências opcionais, processamento assíncrono para mapas grandes e certificação contínua da suíte após cada alteração de apresentação.

## 12. Fontes da auditoria

- `skymap_howto.ipynb`: guia executável das camadas Domain, Application e Infrastructure.
- `pyproject.toml`: dependências, qualidade, entry point e configuração de testes.
- Saídas de testes e validações manuais compartilhadas na sessão de 23/07/2026.
- Inventário e decisões arquiteturais discutidos durante a implementação do MVP SkyMap.
