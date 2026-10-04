# Programación de un UR5e en URSim (Docker) y control compartido con ROS2

**Integrantes:** Joshua Antonio Tapias Triviño · Samuel Jerónimo Moreno Mora

**Entorno:** Ubuntu 22.04 sobre WSL2 · ROS2 Humble · Docker · URSim e-Series 5.26.1 (UR5e) · External Control URCap 1.0.6

## Archivos del repositorio

| Archivo | Descripción |
|---|---|
| `programa1_iniciales.script` | **Programa 1**: trayectorias de las iniciales J, T, S, M con un popup antes de cada letra |
| `Programa2_estructura.txt` | **Programa 2**: árbol de PolyScope (DO[0] en alto, popup, espera de 5 s, External Control) |
| `programa1.urp`, `programa2.urp` | Programas de PolyScope exportados desde el contenedor Docker |
| `Reporte_IEEE_UR5e.docx` | Reporte de la actividad en formato IEEE |
| `comandos.sh` | Comandos para lanzar URSim y el driver de ROS2 |
| `exportar_programas.sh` | Exportación de los programas del contenedor al PC (`docker cp`) |
| `simular_programa1.py` | Verificación cinemática offline (IK del UR5e) del Programa 1 |
| `diagramas_programa2.py` | Diagrama de tiempos del Programa 2 y arquitectura del sistema |
| `requirements.txt` | Dependencias de Python para la simulación |
| `fig5_arbol_programa1.png` | Evidencia: árbol del Programa 1 en PolyScope |
| `fig6_popup_letra_J.png` | Evidencia: popup antes de simular la letra J |
| `fig7_config_external_control.png` | Evidencia: configuración del URCap External Control |
| `fig8_arbol_programa2.png` | Evidencia: árbol del Programa 2 en PolyScope |
| `fig9_popup_programa2.png` | Evidencia: popup del Programa 2 |
| `sim_*.png`, `resultados_simulacion.json` | Resultados de la verificación offline |

## Programa 1
Iniciales de nombre y primer apellido: **J** (Joshua), **T** (Tapias), **S** (Samuel), **M** (Moreno).
Antes de cada letra se muestra un popup indicando la letra a simular. Las letras se trazan
con `movel` y `movec` sobre un plano horizontal (100 mm de alto, 60 mm de ancho) con la
herramienta apuntando hacia abajo.

Uso:
```bash
docker cp programa1_iniciales.script ursim:/ursim/programs/
```
Luego, en PolyScope: *Program → Advanced → Script → File* y seleccionar el archivo.

## Programa 2
`Set DO[0]=On` → popup de aviso → `Wait 5.0 s` → nodo **External Control** (host `192.168.56.1`, puerto `50002`).

## Ejecución en WSL2
La red creada por `start_ursim.sh` solo es visible dentro de WSL2. Para abrir PolyScope desde Windows:
```bash
socat TCP-LISTEN:6080,fork,reuseaddr TCP:192.168.56.101:6080
```
y en el navegador de Windows: `http://localhost:6080/vnc.html`.

## Verificación offline
```bash
pip install -r requirements.txt
python3 simular_programa1.py
python3 diagramas_programa2.py
```

## Exportación desde Docker
```bash
./exportar_programas.sh ursim .
```

## Nota
El bono (planificación con MoveIt 2) no se realizó; `comandos.sh` deja los comandos como referencia.
