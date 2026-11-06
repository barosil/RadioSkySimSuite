#!/usr/bin/env bash
# Uniformiza a instalação/atualização dos 9 submódulos do RadioSkySimSuite.
#
# Os pacotes em `packages/*` são submódulos git (repos `barosil/<nome>`).
# Este script garante que:
#   1. As URLs dos submódulos estão sincronizadas com `.gitmodules`
#      (`git submodule sync --recursive`);
#   2. Todos estão inicializados e no commit registrado pelo meta-repo
#      (`git submodule update --init --recursive`);
#   3. O estado final (branch/commit) é impresso para conferência.
#
# Uso:
#   bash scripts/sync_submodules.sh
#   make submodules
#
# Copyright BINGO Collaboration
# Last modified: 2026-11-06
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Sincronizando URLs dos submódulos (.gitmodules)"
git submodule sync --recursive

echo "==> Inicializando/atualizando submódulos (commits registrados no meta)"
git submodule update --init --recursive

echo ""
echo "==> Estado final dos submódulos"
git submodule status

echo ""
echo "Dica — para desenvolver em um submódulo (branch própria):"
echo '  git -C packages/<nome> checkout -b fix/... main'
echo "Lembre-se: alterações em um submódulo são commitadas NELE e o ponteiro"
echo "é atualizado no meta-repo (AGENTS.md)."
