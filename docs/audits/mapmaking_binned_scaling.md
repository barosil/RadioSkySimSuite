# Auditoria de Escalabilidade do Mapmaking Binned

## 1. Objetivo

Esta auditoria avalia o comportamento computacional e numérico do algoritmo de *mapmaking* do tipo *binned* utilizado no RadioSkySim.

O objetivo principal é verificar como o algoritmo se comporta quando são modificados dois parâmetros relevantes:

* a resolução espacial do mapa, representada pelo parâmetro HEALPix `NSIDE`;
* o número de amostras temporais do *Time Ordered Data* (TOD), representado por `Nt`.

A análise considera simultaneamente aspectos de desempenho computacional e de qualidade da reconstrução, permitindo identificar limites práticos e possíveis configurações de compromisso entre resolução, precisão e consumo de recursos.

---

## 2. Metodologia

Foi implementado o experimento reprodutível:

```text
scripts/mapmaking_binned_scaling_experiment.py
```

O experimento utiliza um campo de céu analítico e determinístico definido por

[
S(\alpha,\delta)
================

\sin(\delta)
+
0.5\cos(2\alpha),
]

em que (\alpha) representa a ascensão reta e (\delta) a declinação.

O uso de uma função analítica permite conhecer diretamente o valor esperado do céu em cada direção observada e, consequentemente, avaliar quantitativamente o erro introduzido pelo processo de pixelização e *binning*.

A frequência adotada no experimento foi de

[
\nu = 1,\mathrm{GHz}.
]

Foram realizadas duas séries independentes de experimentos.

### 2.1. Sweep em NSIDE

Foram avaliadas as resoluções

[
NSIDE \in
{64,128,256,512,1024}.
]

Para cada configuração foram calculados:

* número total de pixels HEALPix;
* escala angular aproximada dos pixels;
* número de pixels efetivamente observados;
* fração de cobertura do mapa;
* número médio de hits nos pixels observados;
* número máximo de hits;
* erro RMS;
* bias médio;
* tempo mediano de execução;
* pico de memória RSS.

### 2.2. Sweep em número de amostras temporais

Mantendo

[
NSIDE=512,
]

foram considerados

[
N_t \in
{121,500,1000,5000,10000}.
]

Essa análise permite separar o efeito da densidade de amostragem temporal daquele associado à resolução espacial do mapa.

---

## 3. Validação do experimento

Foi implementado o teste de regressão

```text
tests/e2e/test_mapmaking_binned_scaling_regression.py
```

O teste verifica invariantes fundamentais do experimento, incluindo:

* conservação do número total de hits;
* consistência do número de amostras;
* número correto de pixels HEALPix;
* cobertura limitada ao intervalo ([0,1]);
* erro RMS finito;
* bias finito;
* redução da escala angular dos pixels com o aumento de `NSIDE`.

O teste foi executado com sucesso:

```text
1 passed
```

Dessa forma, os resultados apresentados nesta auditoria são reproduzíveis e possuem uma verificação automática básica contra regressões futuras.

---

## 4. Resultados do sweep em NSIDE

Os resultados obtidos foram:

| NSIDE |       Npix | Escala do pixel (graus) | Pixels observados | Hits médios |             RMS (K) | Tempo (s) | Memória (MB) |
| ----: | ---------: | ----------------------: | ----------------: | ----------: | ------------------: | --------: | -----------: |
|    64 |     49 152 |                  0.9161 |               257 |       19.46 | (6.63\times10^{-4}) |    0.0113 |          205 |
|   128 |    196 608 |                  0.4581 |               513 |        9.75 | (2.89\times10^{-4}) |    0.0114 |          216 |
|   256 |    786 432 |                  0.2290 |             1 025 |        4.88 | (2.28\times10^{-4}) |    0.0109 |          259 |
|   512 |  3 145 728 |                  0.1145 |             2 049 |        2.44 | (1.34\times10^{-4}) |    0.0318 |          433 |
|  1024 | 12 582 912 |                  0.0573 |             4 097 |        1.22 | (1.79\times10^{-4}) |    0.5663 |        1 041 |

### 4.1. Resolução espacial

Como esperado para a pixelização HEALPix, o número total de pixels cresce quadraticamente com `NSIDE`:

[
N_{\mathrm{pix}} = 12,NSIDE^2.
]

Consequentemente, dobrar `NSIDE` quadruplica o número total de pixels do mapa.

A escala angular diminui aproximadamente por um fator dois a cada duplicação de `NSIDE`, passando de aproximadamente

[
0.916^\circ
]

em `NSIDE=64` para

[
0.057^\circ
]

em `NSIDE=1024`.

---

## 5. Precisão da reconstrução

O erro RMS apresenta redução significativa à medida que a resolução aumenta inicialmente:

[
6.63\times10^{-4},\mathrm{K}
\quad (NSIDE=64)
]

para

[
1.34\times10^{-4},\mathrm{K}
\quad (NSIDE=512).
]

Isso representa uma redução de aproximadamente 80% no erro RMS.

Entretanto, o comportamento deixa de ser monotônico em `NSIDE=1024`, para o qual foi obtido

[
1.79\times10^{-4},\mathrm{K}.
]

Esse resultado não significa que uma maior resolução HEALPix seja intrinsecamente menos precisa. Neste experimento, o aumento da resolução reduz o número médio de amostras disponíveis por pixel.

Em `NSIDE=512`, cada pixel observado recebe em média aproximadamente

[
2.44
]

amostras, enquanto em `NSIDE=1024` esse valor diminui para aproximadamente

[
1.22.
]

Assim, a resolução espacial passa a superar a densidade de amostragem disponível no TOD. O ganho obtido pela redução do tamanho dos pixels passa a competir com a perda de redundância estatística dentro de cada pixel.

Esse comportamento evidencia que a escolha de `NSIDE` não deve ser realizada isoladamente. Ela precisa ser compatível com a estratégia de varredura e com a densidade temporal das observações.

---

## 6. Bias

O bias apresentou comportamento decrescente com o aumento de `NSIDE`.

Os valores evoluíram aproximadamente de

[
-4.06\times10^{-5},\mathrm{K}
]

em `NSIDE=64` para

[
-1.59\times10^{-7},\mathrm{K}
]

em `NSIDE=1024`.

Isso indica que o estimador *binned* não apresenta, neste experimento, evidência de um erro sistemático crescente associado ao aumento da resolução.

A redução do bias também é compatível com a diminuição da diferença espacial entre a posição efetivamente observada e a posição representativa do pixel HEALPix.

---

## 7. Cobertura e hits

A fração global de cobertura diminui com o aumento de `NSIDE`.

Esse comportamento é esperado, pois a trajetória simulada permanece essencialmente a mesma enquanto o número total de pixels do céu cresce como

[
NSIDE^2.
]

Portanto, a redução da fração de cobertura não representa perda da região observada. Ela reflete o aumento do número total de pixels disponíveis na esfera.

O número médio de hits apresentou o comportamento:

[
19.46
\rightarrow
9.75
\rightarrow
4.88
\rightarrow
2.44
\rightarrow
1.22
]

para `NSIDE` de 64 a 1024.

Essa sequência demonstra diretamente a relação entre resolução espacial e redundância de amostragem.

---

## 8. Escalabilidade computacional com NSIDE

O custo computacional permaneceu baixo até `NSIDE=256`.

Os tempos medianos foram aproximadamente:

[
0.0113,;
0.0114,;
0.0109,;
0.0318,;
0.5663\ \mathrm{s}.
]

A transição para `NSIDE=1024` provoca um aumento expressivo no tempo de execução.

Em relação a `NSIDE=512`, o tempo passa aproximadamente de

[
0.032\ \mathrm{s}
]

para

[
0.566\ \mathrm{s},
]

correspondendo a um crescimento superior a uma ordem de grandeza.

O mesmo comportamento aparece no consumo de memória:

[
205,;
216,;
259,;
433,;
1041\ \mathrm{MB}.
]

Em `NSIDE=1024`, o experimento ultrapassa aproximadamente (1,\mathrm{GB}) de pico RSS.

Esse resultado é coerente com a necessidade de representar estruturas cujo tamanho depende de

[
N_{\mathrm{pix}} = 12,NSIDE^2.
]

---

## 9. Resultados do sweep em Nt

Mantendo `NSIDE=512`, foram obtidos:

|     Nt | Pixels observados | Hits médios |             RMS (K) | Tempo (s) | Memória (MB) |
| -----: | ----------------: | ----------: | ------------------: | --------: | -----------: |
|    121 |               121 |        1.00 | (6.36\times10^{-4}) |    0.0418 |          385 |
|    500 |               500 |        1.00 | (6.29\times10^{-4}) |    0.0318 |          454 |
|  1 000 |             1 000 |        1.00 | (6.28\times10^{-4}) |    0.0316 |          457 |
|  5 000 |             2 049 |        2.44 | (1.34\times10^{-4}) |    0.0315 |          457 |
| 10 000 |             2 049 |        4.88 | (1.10\times10^{-4}) |    0.0317 |          457 |

---

## 10. Efeito do número de amostras

Entre `Nt=121` e `Nt=1000`, praticamente cada amostra ocupa um pixel diferente:

[
\langle N_{\mathrm{hits}}\rangle \approx 1.
]

Nessa região, o RMS permanece próximo de

[
6.3\times10^{-4},\mathrm{K}.
]

Quando `Nt` aumenta para 5000, o número de pixels observados deixa de crescer proporcionalmente e passa a ocorrer acumulação de múltiplas amostras nos mesmos pixels.

Para `Nt=5000`:

[
\langle N_{\mathrm{hits}}\rangle \approx 2.44,
]

e o RMS diminui para

[
1.34\times10^{-4},\mathrm{K}.
]

Para `Nt=10000`:

[
\langle N_{\mathrm{hits}}\rangle \approx 4.88,
]

com RMS de

[
1.10\times10^{-4},\mathrm{K}.
]

Esse resultado demonstra a importância da redundância observacional no estimador *binned*. Uma vez que uma região do céu recebe múltiplas amostras, a média realizada dentro de cada pixel fornece uma representação mais estável do sinal associado àquele pixel.

---

## 11. Escalabilidade com Nt

No intervalo analisado, o aumento de `Nt` apresentou impacto relativamente pequeno sobre o tempo mediano de execução após a inicialização.

Entre `Nt=500` e `Nt=10000`, o tempo permaneceu próximo de

[
0.032\ \mathrm{s}.
]

O pico RSS também estabilizou aproximadamente em

[
457\ \mathrm{MB}.
]

Esses resultados indicam que, para a faixa analisada, o custo dominante está mais relacionado à estrutura do mapa HEALPix em `NSIDE=512` do que ao aumento do número de amostras temporais entre 500 e 10000.

Essa conclusão deve ser restrita ao intervalo experimental utilizado. Valores muito maiores de `Nt`, múltiplos detectores, canais de frequência adicionais ou estratégias de varredura distintas podem alterar esse comportamento.

---

## 12. Compromisso entre resolução e custo

Dentro das configurações avaliadas, `NSIDE=512` apresenta um compromisso particularmente favorável.

Nessa configuração foram obtidos:

[
N_{\mathrm{pix}} = 3,145,728,
]

escala angular aproximada de

[
0.115^\circ,
]

erro RMS de

[
1.34\times10^{-4},\mathrm{K},
]

tempo mediano de aproximadamente

[
0.032\ \mathrm{s},
]

e pico RSS de aproximadamente

[
433\ \mathrm{MB}.
]

A passagem para `NSIDE=1024` reduz a escala angular pela metade, porém:

* aumenta o número total de pixels em quatro vezes;
* eleva o pico RSS para aproximadamente (1.04,\mathrm{GB});
* aumenta expressivamente o tempo de execução;
* reduz os hits médios para aproximadamente 1.22;
* não produz redução do RMS no experimento realizado.

Portanto, `NSIDE=512` pode ser considerado, para esta configuração experimental específica, um ponto de compromisso entre resolução espacial, redundância de amostragem e custo computacional.

Essa conclusão não deve ser interpretada como uma recomendação universal de `NSIDE`. O valor adequado depende da resolução instrumental, estratégia de varredura, frequência de amostragem, duração da observação e objetivos científicos.

---

## 13. Limitações

O experimento possui algumas limitações que devem ser consideradas na interpretação dos resultados:

1. foi utilizado um céu analítico suave e determinístico;
2. não foram adicionados ruído instrumental ou ruído correlacionado;
3. a geometria de varredura utilizada é controlada e simplificada;
4. a análise foi realizada para uma única frequência;
5. os tempos medidos são curtos e podem sofrer influência do sistema operacional;
6. RSS representa memória do processo e de bibliotecas associadas, não exclusivamente das estruturas internas do *mapmaker*;
7. apenas uma faixa limitada de `Nt` foi avaliada;
8. os resultados não representam diretamente uma observação completa do BINGO.

Assim, o experimento deve ser interpretado como uma auditoria controlada de escalabilidade e consistência do algoritmo, e não como um benchmark definitivo da pipeline completa.

---

## 14. Conclusão

O experimento confirmou o funcionamento consistente do *mapmaker binned* e permitiu caracterizar seu comportamento diante do aumento da resolução espacial e da densidade de amostragem temporal.

O aumento de `NSIDE` reduz inicialmente o erro de reconstrução devido à maior resolução espacial. Entretanto, quando a pixelização se torna muito mais fina que a densidade da amostragem disponível, o número de hits por pixel diminui e o benefício adicional da maior resolução deixa de ser evidente.

Paralelamente, o custo computacional cresce significativamente em resoluções elevadas devido à dependência quadrática entre `NSIDE` e o número de pixels HEALPix.

O sweep em `Nt` mostrou que o aumento da redundância temporal pode reduzir significativamente o erro RMS quando múltiplas observações passam a contribuir para os mesmos pixels.

Dentro do domínio testado, `NSIDE=512` apresentou o melhor compromisso observado entre resolução, precisão e custo computacional. A utilização de resoluções superiores deve, portanto, ser acompanhada por densidade de amostragem suficiente para justificar o aumento de custo.

Os resultados fornecem uma referência quantitativa inicial para a seleção de parâmetros do *mapmaking* e estabelecem uma base reprodutível para futuras avaliações de desempenho do RadioSkySim.
