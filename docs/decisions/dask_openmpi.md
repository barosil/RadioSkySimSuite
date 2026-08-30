# Análise e recomendações: Dask e OpenMPI (Open MPI)

Resumo rápido

- Para desenvolvimento local e MVP: usar `dask.distributed` com `LocalCluster` ou `SSHCluster` para reproduzibilidade simples.
- Para execução em ambientes HPC que usam OpenMPI, as opções recomendadas são `dask-mpi` (iniciar scheduler+workers via `mpirun`) ou separar responsabilidades: usar MPI (via `mpi4py`) para código fortemente dependente de MPI e usar Dask para orkestrar tasks de alto nível.
- Misturar Dask threaded scheduler com bibliotecas MPI pode causar conflitos; prefira `Process`-based workers ou `dask.distributed` quando houver MPI.


Contexto técnico

O projeto já usa Dask para manipulação lazy/chunking. Em ambientes HPC, é comum que usuários queiram usar OpenMPI (mpirun/mpiexec) para escalar aplicações.

Problemas comuns ao misturar Dask e MPI

- Lançamento de processos: ambos Dask e OpenMPI controlam subprocessos; iniciar Dask workers com mpirun sem integração específica pode levar a problemas de binding e oversubscription.
- Networking e UCX: ambientes HPC com RDMA utilizam UCX; Dask suporta UCX mas requer configuração adicional (ucx-py, UCX library) e compatibilidade com MPI stack.
- Recursos e oversubscription: mpirun pode já ter reservado CPUs/GPU; é preciso coordenar n_workers, threads e cpus-per-task.
- Bibliotecas compiladas com MPI (e.g., linked to OpenMPI) podem não funcionar corretamente sob threads; preferir processos.


Opções e recomendações práticas

1) MVP (recomendado agora)

- Use `dask.distributed.LocalCluster` para desenvolvimento e testes locais.
- Para runs automáticos (CLI/background) em uma única máquina, prefira `Process` workers (set `n_workers` e `threads_per_worker=1`) para evitar interferência com bibliotecas MPI.

2) Integração com OpenMPI em HPC (v2)

- `dask-mpi` (https://github.com/dask/dask-mpi): projeto que simplifica iniciar um scheduler + workers usando `mpirun` ou `srun`. Exemplo de uso:

```bash
# Inicia scheduler + N workers com mpirun
mpirun -n 8 dask-mpi --scheduler-timeout 100
```

- Configurar `dask-mpi` com UCX se houver suporte a RDMA/UCX na infraestrutura:

  - instalar `ucx-py` e as libs UCX
  - usar dask config para habilitar `distributed.comm.ucx` e parâmetros de pool

- Alternativa: `dask-jobqueue` para managers como SLURM (onde mpirun não é o launcher direto)

3) Separar MPI e Dask (quando houver código MPI nativo)

- Se o código científico depende fortemente da comunicação MPI interna (por exemplo, bibliotecas que usam MPI internamente), considere manter essas seções executando sob `mpirun`/MPI e usar Dask para pré/post-processamento ou para orquestrar múltiplas execuções independentes.


Recomendações de configuração para o projeto

- Documentar duas estratégias: `local` e `hpc-mpi` em `settings.toml` e no docs:
  - `local` → LocalCluster, process workers
  - `hpc-mpi` → instruções para dask-mpi / dask-jobqueue com exemplos de `mpirun` / `srun` / `sbatch`
- Adicionar detecção automática simples no runtime: se detectado MPI (p.ex. variáveis de ambiente `OMPI_COMM_WORLD_SIZE` ou `PMI_RANK`), exibir aviso e recomendar iniciar via `dask-mpi`.
- Incluir testes de integração curta que validem execução com `LocalCluster` e, separadamente, um guia/manual de verificação para `dask-mpi` em HPC (não necessariamente automatizado no CI).


Observações finais

- Para o MVP desta feature (CLI + background runner), não é obrigatório integrar com OpenMPI; ofereça `LocalCluster` e um caminho claro para integrar `dask-mpi` no futuro.
- Se a equipe pretende usar MPI intensamente, agendar tempo para validar `ucx`/`dask-mpi` em um nó de teste HPC é essencial antes de adotar em produção.
