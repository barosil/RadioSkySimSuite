"""RFI mitigation (ArPLS + SumThreshold) — ferramentas do projeto.

Flagging de RFI no padrão rádio-astronômico:

- ``ArPLS`` / ``arpls_baseline``: baseline suave (Baek et al. 2015) — ajusta a
  componente lisa de um espectro/SED sem seguir as features (RFI, transitos).
- ``arpls_mask``: máscara ArPLS-ST — computa a SED (média espectral), ajusta a
  baseline com ArPLS, detecta **linhas** (canais) de RFI por SumThreshold no
  resíduo e **blobs** (regiões 2D) no dado com a baseline removida.
- ``st_mask``: máscara SumThreshold pura, com suavização gaussiana opcional.

O fluxo recomendado (item 6 do roteiro — pré-processamento) é:

1. ``sed = data.mean(axis=tempo)``  → espectro médio por canal (SED);
2. ``bl = ArPLS(sed)``              → baseline espectral (forma da banda);
3. ``diff = sed - bl``              → resíduo da SED;
4. ``line_mask = SumThreshold(diff)`` → canais de RFI persistentes;
5. ``res = data - baseline``        → remoção de baseline na imagem;
6. ``blob_mask = SumThreshold(res)`` → RFI localizada (transitória);
7. ``mask = line_mask | blob_mask`` → máscara final de RFI.

Todas as funções operam em medidas **lineares** (ADU/W/Hz), sem conversão para
escala logarítmica.
"""

from .baseline import ArPLS, gaussian_filter
from .mitigation import (
    arpls_mask,
    get_di_kwargs,
    get_sm_kwargs,
    st_mask,
)

__all__ = [
    "ArPLS",
    "arpls_mask",
    "gaussian_filter",
    "get_di_kwargs",
    "get_sm_kwargs",
    "st_mask",
]
