"""check_db.py — Diagnóstico e reparo da conexão com o Postgres (RadioSkySim).

Caminho do arquivo: scripts/check_db.py
Breve descrição: verifica a conexão TCP real com o banco (SELECT 1 + contagens)
e, se falhar, detecta bind mount "stale" do container postgres e o recria via
docker compose (renova o mount, dados intactos em data/DB).
Copyright: BINGO Collaboration.
Last modified: 2026-08-03.

Uso:
    .venv/bin/python scripts/check_db.py            # só diagnostica (exit != 0 se falhar)
    .venv/bin/python scripts/check_db.py --fix      # repara automaticamente
    .venv/bin/python scripts/check_db.py --verbose  # mostra contagens das tabelas

Problema típico em pen drive portátil:
  O container postgres inicia normalmente, mas quando o pen drive é remontado
  (reconexão/erro de I/O) o bind mount do container fica "stale" e toda conexão
  passa a falhar com:
      FATAL: could not open file "global/pg_filenode.map": I/O error
  O postmaster continua vivo (pg_isready responde), mas nenhuma conexão TCP real
  funciona. Os dados permanecem intactos no disco; basta recriar o container
  para renovar o bind mount.

Problema típico ao MOVER o projeto (ex.: outro pen drive / pasta):
  O container guarda o bind mount com o caminho absoluto da época em que foi
  criado. Se o projeto mudar de pasta (ex.: /media/lbarosi/barosi_portable2 →
  /media/barosi), o container continua apontando para o caminho antigo, o
  data/DB atual fica vazio e as tabelas "somem". O script compara o mount do
  container com o data/DB deste projeto e, com --fix, recria o container.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
COMPOSE_DIR = ROOT / "docker" / "postgresql"
COMPOSE_FILE = COMPOSE_DIR / "docker-compose.yaml"
DATA_DIR = ROOT / "data" / "DB"

DB_TABLES = [
    "satid",
    "orbital_elements",
    "radiosources",
    "signal",
    "sat_signal_link",
    "solar_flux_cache",
]


def load_db_config() -> dict[str, str]:
    """Lê a seção [DB] do settings.toml na raiz do projeto."""
    with open(ROOT / "settings.toml", "rb") as f:
        cfg = tomllib.load(f)
    db = cfg["DB"]
    return {
        "host": db.get("POSTGRES_HOST", "localhost"),
        "port": int(db.get("POSTGRES_PORT", 5432)),
        "user": db.get("POSTGRES_USER", "radio"),
        "password": db.get("POSTGRES_PASSWORD", "radio"),
        "dbname": db.get("POSTGRES_DB", "radioskysims"),
    }


def _connect():
    import psycopg2

    cfg = load_db_config()
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=cfg["dbname"],
        connect_timeout=5,
    )


def db_healthy() -> tuple[bool, str]:
    """Tenta uma conexão TCP real + SELECT 1. Retorna (ok, mensagem)."""
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("select 1")
        cur.fetchone()
        conn.close()
        return True, "conexão OK"
    except Exception as exc:
        return False, str(exc).strip()


def bind_mount_stale() -> bool:
    """Verifica se o data dir é legível via bind mount FRESCO (docker run --rm).

    Se um container novo lê os dados mas o container postgres não, é mount stale.
    """
    if not DATA_DIR.exists():
        return False
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{DATA_DIR}:/data:ro",
        "alpine",
        "sh",
        "-c",
        "cat /data/PG_VERSION",
    ]
    try:
        res = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)
        return res.returncode == 0 and res.stdout.strip() != ""
    except Exception:
        return False


def container_mount_source() -> str | None:
    """Retorna o Source (host) do bind mount do postgres para /var/lib/postgresql/data.

    Se o container não estiver rodando (ou não tiver o mount), retorna None.
    """
    try:
        cid = subprocess.run(
            ["docker", "compose", "-f", str(COMPOSE_FILE), "ps", "-q", "postgres"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
        if not cid:
            return None
        fmt = (
            '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}'
            "{{.Source}}{{end}}{{end}}"
        )
        res = subprocess.run(
            ["docker", "inspect", cid, "--format", fmt],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return res.stdout.strip() or None
    except Exception:
        return None


def mount_mismatch() -> tuple[bool, str | None]:
    """Verifica se o bind mount do postgres aponta para o data/DB DESTE projeto.

    O container criado em outra pasta (ex.: outro pen drive) mantém o mount com
    caminho absoluto antigo; o data/DB atual fica vazio e as tabelas "somem".
    Retorna (True, detalhe) se o mount aponta para outro lugar.
    """
    expected = str((ROOT / "data" / "DB").resolve())
    actual = container_mount_source()
    if actual is None:
        return False, None  # container não rodando; a conexão falhará e tratará depois
    if actual.rstrip("/") == expected.rstrip("/"):
        return False, None
    return True, f"container aponta para '{actual}', esperado '{expected}'"


def recreate_postgres() -> bool:
    """Recria o container postgres via docker compose (renova o bind mount)."""
    for step in (["down"], ["up", "-d"]):
        cmd = ["docker", "compose", "-f", str(COMPOSE_FILE)] + step
        print(f"  docker compose {' '.join(step)} ...")
        res = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=180)
        if res.returncode != 0:
            print(f"  ERRO em 'docker compose {' '.join(step)}':\n{res.stderr}")
            return False
    # Aguarda a conexão voltar (o compose pode levar ~30s até healthy)
    for _ in range(45):
        ok, _ = db_healthy()
        if ok:
            return True
        time.sleep(2)
    return False


def print_counts() -> None:
    """Imprime contagens das tabelas principais (diagnóstico de integridade)."""
    conn = _connect()
    cur = conn.cursor()
    for table in DB_TABLES:
        try:
            cur.execute(f"select count(*) from {table}")
            print(f"   {table:20s} {cur.fetchone()[0]}")
        except Exception as exc:
            print(f"   {table:20s} ERRO: {exc}")
    conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica/repara o Postgres do RadioSkySim.")
    parser.add_argument(
        "--fix", action="store_true", help="Recria o container se a conexão falhar."
    )
    parser.add_argument("--verbose", action="store_true", help="Mostra contagens das tabelas.")
    args = parser.parse_args()

    cfg = load_db_config()
    print(f"[check_db] Projeto : {ROOT}")
    print(
        f"[check_db] Conectando em {cfg['host']}:{cfg['port']}/{cfg['dbname']} como {cfg['user']} ..."
    )

    ok, msg = db_healthy()

    # ── Detecta bind mount apontando para caminho errado (problema recorrente) ──
    mismatch, detail = mount_mismatch()
    if mismatch:
        print("[check_db] ⚠️  Bind mount do postgres NÃO aponta para este projeto:")
        print(f"[check_db]     {detail}")
        expected = (ROOT / "data" / "DB").resolve()
        print(f"[check_db]     Esperado: {expected}")
        print("[check_db]     O data/DB atual pode estar vazio (tabelas 'sumiram').")
        if args.fix:
            print("[check_db] Recriando container (renova o mount para o caminho atual)...")
            if not recreate_postgres():
                print("[check_db] ERRO ao recriar o container.")
                return 1
            ok, msg = db_healthy()
            print(f"[check_db] Pós-recreate: {msg}")
        else:
            print("[check_db] Dica: rode com --fix para recriar o container com o mount correto.")
    elif ok:
        print("[check_db] Bind mount do postgres OK.")

    if ok:
        print(f"[check_db] OK: {msg}")
        if args.verbose:
            print("[check_db] Contagens:")
            print_counts()
        return 0

    print(f"[check_db] FALHA: {msg}")
    print("[check_db] Dica: verifique se o pen drive está montado (df -h) e tente novamente.")
    if not args.fix:
        print(
            "[check_db] Rode com --fix para tentar reparo automático (recria o container postgres)."
        )
        return 1

    print("[check_db] Detectando causa...")
    if bind_mount_stale():
        print("[check_db] Mount stale detectado: dados intactos, container com bind antigo.")
        print("[check_db] Recriando container postgres (renova o bind mount)...")
        if recreate_postgres():
            print("[check_db] REPARADO: conexão OK após recriar o container.")
            if args.verbose:
                print("[check_db] Contagens:")
                print_counts()
            return 0
        print("[check_db] ERRO: falha ao reparar. Verifique o docker e o filesystem.")
        return 1

    print("[check_db] Não parece mount stale — dados inacessíveis até via bind novo.")
    print("[check_db] Possível problema no disco/pen drive. Verifique dmesg e o mount:")
    print(f"    df -h {ROOT}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
