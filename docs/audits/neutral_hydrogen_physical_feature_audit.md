Relatório / Auditoria Técnica — Funcionalidade Física: Neutral Hydrogen (HI)

1. Objetivo

Implementar no RadioSkySim uma nova contribuição física de céu difuso baseada em Hidrogênio Neutro (HI / linha de 21 cm), permitindo:

representar HI como uma ContinuumSource;

introduzir um domínio cosmológico independente;

calcular espectros angulares de matéria;

gerar campos de densidade de matéria;

converter frequência observacional em redshift;

calcular a temperatura de brilho do HI;

gerar mapas HEALPix gaussianos e lognormais;

usar esses mapas na geração de Time-Ordered Data (TOD);

persistir e recarregar os mapas em HDF5;

integrar o fluxo completo ao SimOrchestrator.

A implementação foi mantida compatível com a arquitetura em camadas do projeto, evitando dependência direta da Application/Domain em PyCCL ou Healpy.

A transformação utilizada é:

delta_LN = exp(g - sigma_g^2 / 2) - 1

onde g é a realização gaussiana e sigma_g^2 é sua variância.

Essa transformação garante o limite físico:

delta_LN > -1

e preserva aproximadamente média de ensemble nula.

Entretanto, a transformação local não preserva exatamente o espectro angular
C_ell fornecido como entrada. A exponenciação introduz acoplamento entre modos
e modifica a estatística de dois pontos do campo.

Portanto, o adapter atual deve ser interpretado como uma aproximação lognormal
de baixo custo computacional, adequada como baseline físico para o projeto,
mas não como um gerador que reproduz exatamente o C_ell alvo após a
transformação.

2. Status geral

A funcionalidade solicitada foi concluída no escopo atual.

Item solicitado

Status

ContinuumSource -> Neutral Hydrogen

Concluído

Criar domínio cosmology

Concluído

Construção de C_ell para matéria com PyCCL

Concluído

Construção de campos/mapas de densidade de matéria

Concluído

Temperatura de brilho HI em redshift/frequência

Concluído

Mapas HEALPix gaussianos

Concluído

Mapas lognormais

Concluído

Uso dos mapas na Simulation para geração de TOD

Concluído

Persistência e reload HDF5

Concluído

Integração com SimOrchestrator

Concluído



3. Arquitetura implementada

O fluxo físico principal ficou organizado da seguinte forma:

NeutralHydrogen
      |
      v
CosmologyParameters
      |
      v
frequência <-> redshift
      |
      v
PyCCLCosmologyAdapter
      |
      v
AngularPowerSpectrum (C_ell)
      |
      v
MatterFieldPort
      |
      +--> HealpyGaussianMatterFieldAdapter
      |
      +--> HealpyLognormalMatterFieldAdapter
      |
      v
campo de sobredensidade delta_m
      |
      v
temperatura de brilho HI
      |
      v
SkyMap HEALPix por canal
      |
      v
HealpySkyMapTODProjector
      |
      v
pointing + beam
      |
      v
TOD
(T_antenna + power)

A separação segue o princípio:

Application/Domain -> Ports <- Infrastructure

Assim, bibliotecas científicas concretas ficam isoladas em Infrastructure.

4. Domínio cosmológico

Foi criado o domínio:

src/radioskysims/domain/cosmology/

com estruturas e funções responsáveis pela representação física da cosmologia.

Principais estruturas

CosmologyParameters

RedshiftRange

MatterPowerSpectrum

AngularPowerSpectrum

RedshiftWindow

Os parâmetros cosmológicos utilizados no fluxo incluem:

omega_c

omega_b

h

sigma8

n_s

Também foi implementada a propriedade derivada omega_m.

5. Conversão frequência ↔ redshift

Foi implementada a conversão baseada na frequência de repouso da linha de 21 cm:

nu_HI = 1420.405751 MHz

Isso permite que os canais definidos em FrequencyRange sejam transformados nos redshifts correspondentes.

O objetivo é fazer com que cada canal observacional do radiotelescópio seja associado à região cosmológica adequada para o cálculo do sinal HI.

6. NeutralHydrogen como fonte física

Foi criada a fonte:

NeutralHydrogen

integrada à estrutura de ContinuumSource.

A fonte possui parâmetros físicos como:

omega_hi_0
hi_bias_0

e representa a contribuição cosmológica da linha de 21 cm no pipeline de simulação.

7. Integração com PyCCL

Foi implementado:

PyCCLCosmologyAdapter

em Infrastructure.

O adapter fornece ao restante do sistema cálculos cosmológicos sem expor PyCCL às camadas superiores.

Foram implementados contratos para:

P(k, z)

e:

C_ell

de matéria.

Dessa forma, futuramente PyCCL pode ser substituído por outro backend sem alterar o caso de uso de HI.

8. Ports cosmológicos

Foram definidos ports para desacoplar os algoritmos científicos concretos.

Entre eles:

CosmologyPowerSpectrumPort
AngularPowerSpectrumPort
MatterFieldPort

Inicialmente existia:

GaussianMatterFieldPort

Durante a implementação lognormal, o contrato foi generalizado para:

MatterFieldPort

mantendo compatibilidade com o nome anterior.

Essa alteração permite que o mesmo caso de uso aceite diferentes modelos de campo:

Gaussian
Lognormal

sem duplicar o pipeline de HI.

9. Campo gaussiano HEALPix

Foi implementado:

HealpyGaussianMatterFieldAdapter

O adapter:

recebe AngularPowerSpectrum;

prepara o espectro angular;

gera uma realização aleatória com Healpy;

retorna um campo de sobredensidade adimensional delta_m;

suporta seed para reprodutibilidade.

Também foram adicionadas validações relacionadas a nside, formato e valores produzidos.

10. Temperatura de brilho do Hidrogênio Neutro

Foi implementada a conversão do campo de matéria em temperatura de brilho HI.

O fluxo considera:

cosmologia
+ omega_HI
+ bias_HI
+ redshift
+ delta_m

para produzir flutuações da temperatura de brilho.

A saída dos mapas HI é armazenada inicialmente em:

uK

e posteriormente convertida para Kelvin na geração do TOD.

11. Geração de mapa HI por canal

Foi criado:

GenerateNeutralHydrogenMapUseCase

Responsabilidades:

receber a fonte NeutralHydrogen;

receber os parâmetros cosmológicos;

determinar o redshift do canal;

calcular o C_ell;

gerar o campo de matéria;

calcular a temperatura HI;

construir um SkyMap.

Cada resultado possui metadados como:

nside
unit = "uK"
frame = "galactic"
field = "I"
freq_ghz

12. Geração multi-frequência

Foi implementado:

GenerateNeutralHydrogenMapsUseCase

Esse caso de uso percorre:

FrequencyRange.value

e gera um SkyMap para cada canal de frequência.

Isso permite representar o sinal HI como um conjunto espectral de mapas HEALPix.

13. Integração SkyMap -> TOD

O TODSimulator foi estendido para trabalhar também com mapas.

Foi implementado o caminho:

SkyMap
-> projeção no pointing
-> beam opcional
-> temperatura de antena
-> potência

A projeção é realizada por:

HealpySkyMapTODProjector

que realiza a transformação necessária entre coordenadas equatoriais e galácticas e interpola os valores do mapa no pointing do telescópio.

Saídas

O dataset final contém:

T_antenna
power

com unidades:

T_antenna -> K
power     -> W/Hz

14. Integração com beam

Foi validada também a geração de TOD com convolução/resposta do beam.

Assim, o pipeline de HI não está restrito ao caso ideal sem beam.

O fluxo suporta:

HI map
-> pointing
-> beam
-> TOD

15. Integração com SimOrchestrator

A contribuição de HI foi integrada ao fluxo principal da simulação.

Foram adicionadas opções como:

include_neutral_hydrogen
neutral_hydrogen_nside
neutral_hydrogen_seed

O SimOrchestrator passou a:

gerar os mapas HI quando solicitado;

reutilizar os mesmos mapas entre diferentes antenas/pointings;

projetar cada conjunto de mapas no pointing correspondente;

combinar a contribuição HI com outras componentes difusas;

combinar a contribuição difusa com fontes baseadas em tracks/fluxos.

O fluxo Galaxy já existente foi preservado.

16. Combinação de componentes difusas

Foi implementada lógica para combinar TODs de diferentes componentes de mapa, por exemplo:

Galaxy
+
Neutral Hydrogen

sem simplesmente empilhar mapas de mesma frequência.

O resultado combina corretamente:

T_antenna
power

para canais alinhados.

17. Correção adicional multi-antena

Durante a integração foi identificado e corrigido um problema no fluxo de múltiplas antenas.

O resultado de cada antena não estava sendo anexado corretamente dentro do loop.

Após a correção, o SimOrchestrator passou a preservar todos os resultados antes da consolidação na dimensão de pointing.

Foi criada/validada regressão específica para múltiplas antenas.

18. Persistência HDF5

A geração HI foi integrada ao mecanismo existente de persistência de SkyMap.

Foi utilizado:

HDF5SkyMapRepository

O GenerateNeutralHydrogenMapsUseCase agora suporta:

persist
overwrite

Cada mapa é armazenado com chave semelhante a:

neutral_hydrogen_1000mhz_nside8
neutral_hydrogen_1001mhz_nside8
neutral_hydrogen_1002mhz_nside8

Os arquivos mantêm:

pixels;

frequência;

nside;

unidade;

frame;

field.

19. Reload HDF5 -> TOD

Foi validado o round-trip completo:

HI
-> SkyMap
-> HDF5
-> load
-> SkyMap
-> TOD

Os mapas recarregados preservaram pixels e metadados.

Também foi confirmado que mapas carregados do repositório podem ser usados diretamente para gerar TOD.

20. Persistência pela API pública do SimOrchestrator

As flags:

persist_skymaps
skymap_overwrite

foram propagadas também para o fluxo de HI.

Foi validada uma execução real:

SimOrchestrator.run()
-> HI
-> HDF5
-> TOD

com três canais:

1000 MHz
1001 MHz
1002 MHz

Os três arquivos HDF5 foram criados com sucesso.

21. Modelo lognormal

Além do campo gaussiano, foi implementado:

HealpyLognormalMatterFieldAdapter

seguindo o contrato genérico:

MatterFieldPort

A implementação atual parte de uma realização gaussiana e aplica uma transformação lognormal.

O objetivo é produzir um campo com limite físico inferior compatível com densidade:

delta_m > -1

Foram avaliadas alternativas como FLASK e nbodykit.

FLASK é mais apropriado quando se deseja controle rigoroso de campos
lognormais correlacionados, tomografia e correlação entre shells, porém
introduz uma nova dependência externa e aumenta significativamente a
complexidade operacional.

nbodykit oferece ferramentas mais amplas para Large Scale Structure e
pipelines de simulação cosmológica, mas possui custo de integração e
dependências ainda maiores para o escopo atual.

Para esta entrega foi mantida a implementação interna baseada em Healpy,
sem adicionar novas dependências. A arquitetura via MatterFieldPort permite
incorporar futuramente um adapter FLASK, nbodykit ou equivalente sem alterar
os casos de uso de HI.

Essa escolha pode ser revista futuramente caso sejam necessários mapas lognormais tomográficos mais sofisticados ou campos correlacionados entre shells.

22. Seleção Gaussian / Lognormal

Foi adicionada configuração:

[cosmology]
field_model = "gaussian"

Os valores suportados atualmente são:

gaussian
lognormal

O Composition Root seleciona automaticamente:

HealpyGaussianMatterFieldAdapter

ou:

HealpyLognormalMatterFieldAdapter

e injeta a implementação no mesmo caso de uso.

Portanto, o pipeline científico permanece independente da implementação concreta do campo.

23. Validação do modo lognormal

Foi validado manualmente o caminho:

settings.toml
-> field_model = "lognormal"
-> Composition Root
-> HealpyLognormalMatterFieldAdapter
-> NeutralHydrogen
-> SkyMap

Foram gerados mapas em:

1.000 GHz
1.001 GHz
1.002 GHz

com valores finitos e não nulos.

Também foi validado:

HI lognormal
-> SkyMap
-> TOD

com:

time = 4
frequency = 3

e valores finitos para:

T_antenna
power

Também foram adicionadas validações estatísticas do campo lognormal.

Foi verificado que:

a média do contraste é aproximadamente nula quando avaliada sobre múltiplas
realizações com seeds diferentes;

o espectro angular estimado da realização lognormal é finito;

a potência angular estimada apresenta comportamento não patológico e não
nulo.

Esses testes não exigem igualdade entre o C_ell observado e o C_ell de entrada,
pois a transformação lognormal local não preserva exatamente o espectro
gaussiano original.

24. Testes realizados

Foram executados testes progressivos durante toda a implementação.

Entre os grupos validados:

tests/application/cosmology
tests/infrastructure/cosmology
tests/integration/cosmology
tests/application/services/test_sim_orchestrator_neutral_hydrogen.py
tests/application/services/test_sim_orchestrator_galaxy.py
tests/application/services/test_tod_orchestrator.py

Marcos observados durante a implementação:

25 testes focados -> passed
36 testes de cosmologia/integração -> passed
32 testes de regressão HI/Galaxy/TOD -> passed
33 testes após persistência no SimOrchestrator -> passed
8 testes específicos do adapter lognormal -> passed

Após a inclusão do teste de integração lognormal, a regressão relacionada continuou passando.

Os dois testes adicionais cobrem:

média aproximadamente nula em ensemble;

consistência espectral básica por healpy.anafast, verificando finitude,
potência não patológica e presença de sinal.

25. Validações físicas e funcionais realizadas

Foram verificadas:

dimensões corretas dos mapas HEALPix;

pixels finitos;

seed reproduzível;

campos gaussianos e lognormais diferentes;

limite inferior delta_m > -1 no lognormal;

frequência correta por canal;

conversão uK -> K;

TOD não nulo;

T_antenna finito;

power finito;

frequências do TOD em Hz;

suporte com e sem beam;

persistência dos mapas;

reload de mapas;

múltiplas antenas;

composição Galaxy + HI;

execução pela API pública do SimOrchestrator.

média lognormal aproximadamente nula em ensemble;

espectro angular estimado finito;

potência angular estimada não patológica;

limitação explícita de que a transformação lognormal local não preserva
exatamente o C_ell alvo;

26. Exemplo prático de uso

Gaussian

No settings.toml:

[cosmology]
field_model = "gaussian"

Então:

orchestrator = SimOrchestrator.from_settings("bingo")

result = orchestrator.run(
    include_neutral_hydrogen=True,
    neutral_hydrogen_nside=64,
    neutral_hydrogen_seed=42,
)

Lognormal

No settings.toml:

[cosmology]
field_model = "lognormal"

O mesmo código de simulação é utilizado.

Apenas a implementação de MatterFieldPort muda no Composition Root.

27. Pontos que não são bloqueadores, mas podem ser evoluídos

27.1 Seleção do modelo diretamente no run()

Atualmente a seleção Gaussian/Lognormal está configurada via settings.toml.

Uma evolução de usabilidade seria permitir:

orchestrator.run(
    include_neutral_hydrogen=True,
    neutral_hydrogen_field_model="lognormal",
)

Isso facilitaria estudos comparativos em notebooks sem editar configuração global.

Não é necessário para considerar a funcionalidade física atual concluída.

27.2 Correlação entre canais

Atualmente os canais são gerados como realizações individuais, usando seed derivada por canal.

Para maior realismo físico, uma evolução futura importante é modelar:

correlação entre frequência/redshift

ou seja, produzir shells/canais cosmológicos correlacionados.

Esse ponto é relevante principalmente para estudos tomográficos de 21 cm.

27.3 FLASK / nbodykit

FLASK e nbodykit foram avaliados como alternativas para evoluções futuras
do modelo de campo de matéria.

FLASK é particularmente adequado para geração de campos lognormais
correlacionados e tomográficos, oferecendo maior controle estatístico sobre
shells e espectros cruzados. Entretanto, sua integração adicionaria uma
dependência externa relevante e exigiria preparação consistente dos
espectros/covariâncias.

nbodykit oferece uma infraestrutura mais ampla para Large Scale Structure e
pipelines de simulação cosmológica, mas sua integração possui maior custo de
dependências, ambiente e validação, excedendo o escopo necessário para a
entrega atual.

A decisão adotada foi manter:

HealpyLognormalMatterFieldAdapter

como baseline lognormal interno.

Essa implementação apresenta baixo custo, é reproduzível, não introduz novas
dependências e satisfaz o contrato MatterFieldPort.

A principal limitação conhecida é que a transformação lognormal local não
preserva exatamente o C_ell de entrada.

Caso futuros estudos exijam correlação entre shells, tomografia ou controle
mais rigoroso das estatísticas de dois pontos, recomenda-se implementar
FLASK, nbodykit ou ferramenta equivalente como novo adapter de
MatterFieldPort, sem alterar a camada de domínio ou os casos de uso.

28. Dívida arquitetural identificada

Existe no projeto mais de uma estrutura denominada SimulationContext, com responsabilidades diferentes.

A composição atual utiliza o contexto definido no módulo de SimOrchestrator.

Não foi feita refatoração desse ponto nesta funcionalidade para evitar mudança de escopo e risco de regressão.

Recomenda-se registrar essa duplicidade como dívida técnica futura.

29. Conclusão

A funcionalidade física de Hidrogênio Neutro está implementada e integrada ao RadioSkySim.

O sistema atualmente consegue executar:

Cosmologia
-> frequência/redshift
-> C_ell de matéria
-> campo de densidade
-> Gaussian ou Lognormal
-> temperatura de brilho HI
-> mapas HEALPix por canal
-> persistência opcional HDF5
-> pointing
-> beam
-> TOD

O pipeline foi integrado ao SimOrchestrator, preservando o caminho existente de Galaxy e fontes baseadas em fluxos/tracks.

A implementação utiliza ports para manter PyCCL e Healpy isolados na camada Infrastructure e possui testes unitários, de aplicação, infraestrutura e integração cobrindo os principais caminhos.

Status final

FUNCIONALIDADE FÍSICA — NEUTRAL HYDROGEN: CONCLUÍDA

Próximas evoluções recomendadas, sem impedir o fechamento desta entrega:

seleção Gaussian/Lognormal diretamente pela API run();

correlação física entre canais de frequência/redshift;

eventual adapter alternativo usando FLASK ou outra ferramenta tomográfica;

documentação científica detalhada das hipóteses e equações usadas no modelo HI.

O modo lognormal foi validado também em propriedades estatísticas básicas.

A implementação atual é considerada adequada como baseline lognormal para a
entrega, com a limitação de preservação não exata de C_ell explicitamente
documentada.

FLASK e nbodykit foram avaliados como alternativas futuras e não foram
incorporados nesta entrega, evitando aumento desnecessário de dependências e
complexidade.