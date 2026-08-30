# Relatório

Analisando como especialista em desenvolvimento de software científico, voltado para radioastronomia, com experiência em processamento de dados para cosmologia e astrofísica aplicada a máquinas com restrição de memória, desenvolvimento em sistemas não distribuidos com DASK e GPU

- Descrição resumida do projeto
- Adesão a aquitetura DDD
- Tech stack comentado
- Entrypoints
- Casos de Uso
- Qualidade de Código:
    - Total de linhas de código
    - Módulos (com total de linhas)
    - Linting, formatação, docstrings, type annotations, documentação
    - Análise de módulos muito grandes que merecem refatoração
    - comentário sobre melhores módulos
- Detalhamento da função de simulação TOD, indicando os passos utilizados, uso de settings, repositorio, funcionamento do processor, cliente dask, materializaç;ão dos lazy array e controle de memoria.
- Analise de eficiência de código, detecção de gargalos e possíveis melhorias
- Novos features
- Roadmap evolução 
- reordenar documentos /docs movendo outdates para _archive
- preparar sprints para melhoria de engenharia

# Análise de desempenho

- Verificar funcionamento de TOD simulation tendo em vista um caso típico de uso para observações de 24h registradas de minuto em minuto com satelites, radiofontes e fontes locais.
- Uso do processor para disciplinar materialização das computações lazy
- Otimizar calculo de radiosources para utilizar fluxo integrado e segregar a informação de sources no beam para events.
- possibilidade de materializar dataset por tipo de fonte
- verificar o orquestrador para garantir que ele usa os parametros passados no construtor sobrepondo o settings onde apropriado.
- manter o dataset eventos lazy
- verificar o modelo de observações utilizado para o banco para permitir buscas mais abrangentes e serialização
- prover metodos _repr adequados e simples para os simulation_results
- Garantir que o cliente dask local seja criado e seja informado no notebook que estiver rodando qual é o endereço para conexão do dashboard
- Criação de suite de testes de benchmarking para o TOD simulation

# Funcionalidade Física

- ContinuumSource --> Galaxia
    - constroi contribuição da via lactea usando pysm3, (sincroton, dust, free-free) para bins de frequencia do frequency_range.
    - Construção de TOD a partir do mapa, usando map_rotate com os apontamentos do telescopio e convolução do feixe.
    - TOD_simulation deve ter métodos separados para dados a partir de fluxos e tracks (como já existe) e dados a partir de mapas, com um método de mais alto nível que orquestra a criação deles conforme necessário de acordo com os componentes específicos.
    - Mapas healpy construídos devem ser persistidos se um flag for setado. Persistencia em repositorio e em disco via hdf5
    - Mapas healpy podem ser carregados pelo repositorio e usados para construir TODs.

# Funcionalidade Física

- ContinuumSource --> Neutral Hydrogen
    - Criar domínio cosmology
    - Construção de Cls para matéria com códigos boltzmann (pyccl)
    - Construção de mapas de densidade de matéria com pyccl
    - Construção da Temperatura de brilho do hidrogênio neutro em range de redshift --> frequencia
    - Construção de mapas healpy (gaussianos)
    - Construção de mapas lognormais (avaliar uso de flask ou nbodykit)
    - Verificar funcionamento de simulation com este mapa para geração de tod

# Funcionalidade Física

- Construção de mapas a partir da TOD

    - criação de modelo de dominio
    - criação de modelo de db
    - criação de modelo de repositorio
    - criação de modelo de serviço


# Revisão Signal Chain

A diretividade $$D = \frac{4\pi}{\iint B(\theta, \phi) d\Omega} = \frac{4\pi}{\Omega}$$

Para uma fonte puntiforme
$$T_A[K] = 10^{-26} \frac{\lambda^2}{2k_B \Omega} S_\nu[Jy] B_n(\hat \theta, \hat \phi)$$

- Para fontes GNSS, temos a potencia do sinal emitida pelo satélite e a Power Spectral Density, o fluxo $S$ é determinado considerando a free path loss e a ganho da antena do satélite e a distância do satélite.

- Para radiofontes, os catálogos fornecem diretamente o fluxo S em Jy ou mJy e a determinação de S para as frequencias da simulação é realizada com um modelo espectral de acordo com os catálogos.

- Para localsources como o Sol, acessamos os dados do observatório de learmonth e determinamos o fluxo a partir de uma média dos dados em uma janela temporal (15min - 1h), obtido em SFU e convertido para Jy, com interpolação para obter os valores nas frequencias da simulação.

A partir das simulações de $S_\nu$, conhecendo o angulo entre a fonte e o boresight da antena, o padrão de radiação da antena e a diretividade como função da frequencia (por interpolação), utiliza-se a expressão acima para a obtenção de T_A.