"""
Genera dos figuras de apoyo para el Programa 2:
  sim_secuencia_programa2.png : diagrama de tiempos esperado (DO0, popup, espera, External Control)
  sim_arquitectura.png        : arquitectura URSim (Docker) <-> ur_robot_driver (ROS2)
El instante de confirmacion del popup depende del usuario; aqui se asume t = 4 s.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 9})

# ------------------------- Diagrama de tiempos ------------------------------
T_CONF = 4.0      # instante supuesto en que el usuario confirma el popup
ESPERA = 5.0
T_EXT = T_CONF + ESPERA
T_FIN = 16.0

fig, ax = plt.subplots(figsize=(6.5, 2.7))
filas = ["DO[0]", "Popup", "Wait", "External\nControl"]
y = {k: i for i, k in enumerate(reversed(filas))}
h = 0.6


def señal(fila, tramos, color):
    for t0, t1 in tramos:
        ax.broken_barh([(t0, t1 - t0)], (y[fila] - h / 2, h), facecolors=color, edgecolor="k", lw=0.6)


señal("DO[0]", [(0.0, T_FIN)], "#f5b041")
señal("Popup", [(0.05, T_CONF)], "#5dade2")
señal("Wait", [(T_CONF, T_EXT)], "#aab7b8")
señal("External\nControl", [(T_EXT, T_FIN)], "#58d68d")
ax.text(T_FIN / 2, y["DO[0]"], "Salida digital 0 = ALTO", ha="center", va="center", fontsize=8)
ax.text(T_CONF / 2, y["Popup"], "Mensaje al usuario", ha="center", va="center", fontsize=8)
ax.text((T_CONF + T_EXT) / 2, y["Wait"], "Espera 5.0 s", ha="center", va="center", fontsize=8)
ax.text((T_EXT + T_FIN) / 2, y["External\nControl"], "Control desde ROS2", ha="center", va="center", fontsize=8)
for t, etiqueta in [(T_CONF, "Usuario confirma"), (T_EXT, "Conexion a ROS2")]:
    ax.axvline(t, color="k", ls=":", lw=0.8)
    ax.text(t, len(filas) - 0.35, etiqueta, ha="center", fontsize=7.5, bbox=dict(fc="white", ec="none", pad=1))
ax.annotate("", xy=(T_EXT, -0.62), xytext=(T_CONF, -0.62), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text((T_CONF + T_EXT) / 2, -0.85, "5 s", ha="center", fontsize=8)
ax.set_yticks(list(y.values()))
ax.set_yticklabels(list(y.keys()))
ax.set_ylim(-1.1, len(filas) - 0.15)
ax.set_xlim(0, T_FIN)
ax.set_xlabel("Tiempo [s] (confirmacion supuesta en t = 4 s)")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sim_secuencia_programa2.png"), dpi=220)
plt.close(fig)

# --------------------------- Arquitectura -----------------------------------
fig, ax = plt.subplots(figsize=(5.7, 3.0))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis("off")


def caja(x, y0, w, hh, titulo, lineas, color):
    ax.add_patch(FancyBboxPatch((x, y0), w, hh, boxstyle="round,pad=0.05,rounding_size=0.15",
                                fc=color, ec="k", lw=0.8))
    ax.text(x + w / 2, y0 + hh - 0.28, titulo, ha="center", va="top", fontweight="bold", fontsize=8.5)
    for i, l in enumerate(lineas):
        ax.text(x + w / 2, y0 + hh - 0.75 - 0.36 * i, l, ha="center", va="top", fontsize=7.3)


ax.add_patch(FancyBboxPatch((0.15, 0.25), 3.7, 4.45, boxstyle="round,pad=0.05", fc="none", ec="#2e86c1", ls="--", lw=1))
ax.text(2.0, 4.55, "Contenedor Docker (192.168.56.101)", ha="center", fontsize=7.5, color="#2e86c1")
caja(0.4, 2.45, 3.2, 1.85, "URSim e-Series (UR5e)", ["PolyScope 5.26.1 (VNC :6080)", "programa1.urp", "programa2.urp"], "#d6eaf8")
caja(0.4, 0.45, 3.2, 1.75, "URCap External Control", ["Host IP: 192.168.56.1", "Puerto: 50002", "Nodo en Programa2"], "#d5f5e3")

ax.add_patch(FancyBboxPatch((5.25, 0.25), 4.6, 4.45, boxstyle="round,pad=0.05", fc="none", ec="#ca6f1e", ls="--", lw=1))
ax.text(7.55, 4.55, "Ubuntu 22.04 en WSL2 (192.168.56.1)", ha="center", fontsize=7.5, color="#ca6f1e")
caja(5.5, 2.45, 4.1, 1.9, "ur_robot_driver (ROS2 Humble)", ["Recibe la conexion del nodo", "External Control", "Puertos 50001-50004"], "#fdebd0")
caja(5.5, 0.45, 4.1, 1.75, "Puente socat (WSL2)", ["localhost:6080 -> 192.168.56.101:6080", "PolyScope en el navegador", "de Windows"], "#e8daef")

flecha = dict(arrowstyle="<->", lw=1.2, color="k")
ax.annotate("", xy=(5.45, 3.6), xytext=(3.65, 3.6), arrowprops=flecha)
ax.text(4.55, 3.75, "TCP/IP", ha="center", fontsize=7.5)
ax.text(4.55, 3.3, "estado / comandos", ha="center", fontsize=6.8)
ax.annotate("", xy=(5.45, 3.0), xytext=(3.65, 1.35), arrowprops=dict(arrowstyle="->", lw=1.0, color="#1e8449"))
ax.text(4.55, 1.55, "solicita el script\n(puerto 50002)", ha="center", fontsize=6.8, color="#1e8449", bbox=dict(fc="white", ec="none", pad=1))
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sim_arquitectura.png"), dpi=220)
plt.close(fig)
print("Figuras del Programa 2 generadas")
