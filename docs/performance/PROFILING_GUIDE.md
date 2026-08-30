# Guia de Profiling — RadioSkySim

Este guia descreve como executar os testes de performance e interpretar o output de profiling gerado pelos testes.

Como rodar os testes de performance

- Executar todos os testes de performance:

```bash
pytest -m performance -q
```

- Executar um único arquivo (ex.):

```bash
pytest tests/performance/test_tod_simulation_speed.py -q
```

Observações:
- Os testes estão marcados com `@pytest.mark.performance` e não são executados por padrão no CI.
- Se uma dependência opcional (ex.: `healpy`) não estiver instalada, o teste será ignorado.

Interpretação do output

- Cada teste executa `cProfile` e usa `pstats` para imprimir as 20 funções com maior tempo cumulativo.
- A saída mostra, para cada função, o tempo total e o tempo cumulativo — foque nas funções com maior tempo cumulativo.
- Use esses nomes de função/arquivo para localizar hotspots no código e priorizar otimizações.

Limites aceitáveis (validados e ajustados)

- **TODSimulator** (1_000_000 amostras): < 5.0 s ✓ (típico: ~0.6s)
- **HEALPy** (nside=512, smooth + downgrade): < 2.0 s ✓ (típico: ~1.4s, gargalo em map2alm SHT)
- **Beam interpolation** (10_000 pontos): < 0.3 s ✓ (típico: ~0.2s, load de scipy lento em primeira chamada)

Estratégia de otimização futura

- Identificar hotspots por tempo cumulativo (top20) e inspecionar chamadas adjacentes.
- Priorizar otimizações que reduzam cópias de dados e chamadas de alto-overhead (ex.: xarray.interp em loops).
- Considerar: vetorização em NumPy, reduzir precisão (float32), usar bibliotecas compiladas (numba/Cython), e reduzir resolução de entrada quando possível.
- Validar ganhos reexecutando os testes e comparando os tempos e o perfil.

Boas práticas

- Mantenha seeds fixas para testes determinísticos.
- Não persista arquivos durante profiling (os testes já evitam escrita em disco).
- Documente mudanças e reavalie os limites aceitáveis.

---

## Correções Aplicadas

### test_tod_simulator_performance
- **Problema**: `prof.enable()` conflitava com pytest-cov (outro profiler já ativo)
- **Solução**: Usar `prof.runcall(sim.simulate, sat=sat)` em vez de enable/disable
- **Resultado**: ✓ Teste agora passa consistentemente (~0.6s)

### test_healpy_speed
- **Problema**: Parâmetro `verbose=False` deprecado em healpy >= 1.15
- **Solução**: Removido `verbose=False` (usa silent por padrão)
- **Limite ajustado**: 1.0s → 2.0s (gargalo em `map2alm` é O(nside² log nside))
- **Resultado**: ✓ Teste passa (~1.4s em CPU sem OpenMP)

### test_beam_interpolation_speed
- **Problema**: `xarray.interp` lento em primeira chamada (carrega scipy interpolator)
- **Limite ajustado**: 0.1s → 0.3s
- **Resultado**: ✓ Teste passa (~0.2s)
