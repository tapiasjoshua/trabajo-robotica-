#!/usr/bin/env bash
# Exporta los programas de PolyScope desde el contenedor de URSim al PC local.
set -e
CONTENEDOR=${1:-ursim}            # ver nombre con: docker ps
DESTINO=${2:-./programas/exportados}
mkdir -p "$DESTINO"
docker cp "$CONTENEDOR":/ursim/programs/. "$DESTINO"/
echo "Programas exportados en $DESTINO:"
ls -l "$DESTINO"
