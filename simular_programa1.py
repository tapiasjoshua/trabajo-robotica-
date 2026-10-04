"""
Simulacion cinematica offline del Programa 1 (iniciales J, T, S, M) en un UR5e.

Reproduce la misma geometria del archivo programas/programa1_iniciales.script:
  - movel -> segmento recto en espacio cartesiano con perfil trapezoidal
  - movec -> arco circular definido por (inicio, via, fin)
Para cada muestra calcula la cinematica inversa numerica con los parametros DH
oficiales del UR5e, verifica alcanzabilidad y cercania a singularidades y genera
las figuras de evidencia en ../evidencias/.

Nota: es una verificacion geometrica y cinematica; no reemplaza la ejecucion en URSim.
Uso:  python3 simular_programa1.py      (requiere numpy, scipy, matplotlib)
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidencias")
os.makedirs(OUT, exist_ok=True)

# ------------------------- Parametros DH del UR5e -------------------------
D = [0.1625, 0, 0, 0.1333, 0.0997, 0.0996]
A = [0, -0.425, -0.3922, 0, 0, 0]
ALPHA = [np.pi / 2, 0, 0, np.pi / 2, -np.pi / 2, 0]


def dh(i, qi):
    ct, st = np.cos(qi), np.sin(qi)
    ca, sa = np.cos(ALPHA[i]), np.sin(ALPHA[i])
    return np.array([[ct, -st * ca, st * sa, A[i] * ct],
                     [st, ct * ca, -ct * sa, A[i] * st],
                     [0, sa, ca, D[i]],
                     [0, 0, 0, 1]])


def fk(q):
    T = np.eye(4)
    for i in range(6):
        T = T @ dh(i, q[i])
    return T


def eslabones(q):
    T, P = np.eye(4), [np.zeros(3)]
    for i in range(6):
        T = T @ dh(i, q[i])
        P.append(T[:3, 3])
    return np.array(P)


def jacobiano(q, eps=1e-6):
    J, T0 = np.zeros((6, 6)), fk(q)
    for i in range(6):
        dq = np.array(q, float)
        dq[i] += eps
        T1 = fk(dq)
        J[:3, i] = (T1[:3, 3] - T0[:3, 3]) / eps
        J[3:, i] = R.from_matrix(T1[:3, :3] @ T0[:3, :3].T).as_rotvec() / eps
    return J


def manipulabilidad(q):
    J = jacobiano(q)
    return float(np.sqrt(abs(np.linalg.det(J @ J.T))))


def ik(T_des, q_semilla):
    def error(q):
        T = fk(q)
        ep = T[:3, 3] - T_des[:3, 3]
        eo = R.from_matrix(T[:3, :3] @ T_des[:3, :3].T).as_rotvec()
        return np.concatenate([ep, 0.2 * eo])
    sol = least_squares(error, q_semilla, xtol=1e-12, ftol=1e-12, max_nfev=500)
    e = error(sol.x)
    return sol.x, float(np.linalg.norm(e[:3])), float(np.linalg.norm(e[3:]) / 0.2)


# --------------- Mismos parametros que el script URScript -----------------
ORIGEN = np.array([-0.25, -0.45, 0.20])
ROT = R.from_rotvec([0, 3.1416, 0]).as_matrix()      # herramienta hacia abajo
ALTO, ANCHO, SEP, Z_SEG = 0.10, 0.06, 0.09, 0.05
V_RAP, V_TRA, ACC = 0.25, 0.10, 0.50
Q_SEGURA = np.array([0, -1.5708, 1.5708, -1.5708, -1.5708, 0])


def pto(ox, u, v, dz):
    return ORIGEN + np.array([ox + u * ANCHO, v * ALTO, dz])


# ---------------------- Construccion de los segmentos ----------------------
segmentos = []          # dict(tipo, p0, p1, via, v, letra)
estado = {"pos": pto(0, 0, 0, 0.10), "letra": None}


def movel(p, v):
    segmentos.append(dict(tipo="L", p0=estado["pos"].copy(), p1=p, via=None, v=v, letra=estado["letra"]))
    estado["pos"] = p.copy()


def movec(via, fin, v):
    segmentos.append(dict(tipo="C", p0=estado["pos"].copy(), p1=fin, via=via, v=v, letra=estado["letra"]))
    estado["pos"] = fin.copy()


def bajar(ox, u, v):
    movel(pto(ox, u, v, Z_SEG), V_RAP)
    movel(pto(ox, u, v, 0), V_TRA)


def trazar(ox, u, v):
    movel(pto(ox, u, v, 0), V_TRA)


def arco(ox, uv, vv, uf, vf):
    movec(pto(ox, uv, vv, 0), pto(ox, uf, vf, 0), V_TRA)


def subir(ox, u, v):
    movel(pto(ox, u, v, Z_SEG), V_RAP)


def letra_J(ox):
    bajar(ox, 0, 1); trazar(ox, 1, 1); subir(ox, 1, 1)
    bajar(ox, 0.6, 1); trazar(ox, 0.6, 0.18); arco(ox, 0.3, 0, 0, 0.18); subir(ox, 0, 0.18)


def letra_T(ox):
    bajar(ox, 0, 1); trazar(ox, 1, 1); subir(ox, 1, 1)
    bajar(ox, 0.5, 1); trazar(ox, 0.5, 0); subir(ox, 0.5, 0)


def letra_S(ox):
    bajar(ox, 1, 0.9); arco(ox, 0.5, 1, 0, 0.75); trazar(ox, 1, 0.25); arco(ox, 0.5, 0, 0, 0.1); subir(ox, 0, 0.1)


def letra_M(ox):
    bajar(ox, 0, 0); trazar(ox, 0, 1); trazar(ox, 0.5, 0.45); trazar(ox, 1, 1); trazar(ox, 1, 0); subir(ox, 1, 0)


LETRAS = [("J", letra_J, 0.0), ("T", letra_T, SEP), ("S", letra_S, 2 * SEP), ("M", letra_M, 3 * SEP)]
for nombre, funcion, ox in LETRAS:
    estado["letra"] = nombre
    funcion(ox)


# ----------------------------- Perfiles -----------------------------------
def duracion_trap(L, v, a):
    if L < 1e-9:
        return 0.0
    return 2 * np.sqrt(L / a) if L < v * v / a else L / v + v / a


def s_trap(t, T, L, v, a):
    if L < v * v / a:
        vp = np.sqrt(L * a)
    else:
        vp = v
    ta = vp / a
    if t < ta:
        return 0.5 * a * t * t
    if t > T - ta:
        return L - 0.5 * a * (T - t) ** 2
    return 0.5 * a * ta * ta + vp * (t - ta)


def geometria_arco(p0, pv, p1):
    u, w = pv - p0, p1 - p0
    n = np.cross(u, w)
    c = p0 + (np.dot(u, u) * np.cross(w, n) + np.dot(w, w) * np.cross(n, u)) / (2 * np.dot(n, n))
    r = np.linalg.norm(p0 - c)
    e1 = (p0 - c) / r
    e2 = np.cross(n / np.linalg.norm(n), e1)
    ang = np.arctan2(np.dot(p1 - c, e2), np.dot(p1 - c, e1)) % (2 * np.pi)
    return c, r, e1, e2, ang


# -------------------------- Muestreo temporal ------------------------------
DT = 0.02
t_acum, tiempos, puntos, letras = 0.0, [], [], []
inicio_letra, long_trazo, t_letra = {}, {}, {}
for s in segmentos:
    p0, p1 = s["p0"], s["p1"]
    if s["tipo"] == "L":
        L = float(np.linalg.norm(p1 - p0))
        def g(x, p0=p0, p1=p1, L=L):
            return p0 + (p1 - p0) * (x / L if L > 0 else 0)
    else:
        c, r, e1, e2, ang = geometria_arco(p0, s["via"], p1)
        L = float(r * ang)
        def g(x, c=c, r=r, e1=e1, e2=e2):
            return c + r * (np.cos(x / r) * e1 + np.sin(x / r) * e2)
    T = duracion_trap(L, s["v"], ACC)
    s["L"], s["T"] = L, T
    inicio_letra.setdefault(s["letra"], t_acum)
    t_letra[s["letra"]] = t_letra.get(s["letra"], 0.0) + T
    en_plano = abs(p0[2] - ORIGEN[2]) < 1e-6 and abs(p1[2] - ORIGEN[2]) < 1e-6
    if en_plano:
        long_trazo[s["letra"]] = long_trazo.get(s["letra"], 0.0) + L
    for t in np.arange(0, T, DT):
        tiempos.append(t_acum + t)
        puntos.append(g(s_trap(t, T, L, s["v"], ACC)))
        letras.append(s["letra"])
    t_acum += T
tiempos.append(t_acum)
puntos.append(segmentos[-1]["p1"])
letras.append(segmentos[-1]["letra"])
tiempos, puntos, letras = np.array(tiempos), np.array(puntos), np.array(letras)

# --------------------------- Cinematica inversa -----------------------------
T_aprox = np.eye(4); T_aprox[:3, :3] = ROT; T_aprox[:3, 3] = pto(0, 0, 0, 0.10)
q, _, _ = ik(T_aprox, Q_SEGURA)
Q, err_p, err_o, manip = [], [], [], []
for p in puntos:
    Td = np.eye(4); Td[:3, :3] = ROT; Td[:3, 3] = p
    q, ep, eo = ik(Td, q)
    Q.append(q); err_p.append(ep); err_o.append(eo); manip.append(manipulabilidad(q))
Q, err_p, err_o, manip = map(np.array, (Q, err_p, err_o, manip))
salto = np.degrees(np.max(np.abs(np.diff(Q, axis=0)), axis=1))

COLORES = {"J": "#1f4e9c", "T": "#c0392b", "S": "#1e8449", "M": "#7d3c98"}
NOMBRES = {"J": "J (Joshua)", "T": "T (Tapias)", "S": "S (Samuel)", "M": "M (Moreno)"}
plt.rcParams.update({"font.family": "serif", "font.size": 9})

# ---------------- Figura 1: vista superior de las iniciales ----------------
fig, ax = plt.subplots(figsize=(6.5, 2.9))
en_plano = np.abs(puntos[:, 2] - ORIGEN[2]) < 1e-5
for i in range(len(puntos) - 1):
    xy = puntos[i:i + 2, :2] * 1000
    if en_plano[i] and en_plano[i + 1]:
        ax.plot(xy[:, 0], xy[:, 1], color=COLORES[letras[i]], lw=2.6, solid_capstyle="round")
    else:
        ax.plot(xy[:, 0], xy[:, 1], color="0.65", lw=0.8, ls="--")
for k in COLORES:
    ax.plot([], [], color=COLORES[k], lw=2.6, label=NOMBRES[k])
ax.plot([], [], color="0.65", ls="--", label="Herramienta elevada")
ax.set_xlabel("X base [mm]")
ax.set_ylabel("Y base [mm]")
ax.set_aspect("equal")
ax.grid(alpha=0.3)
ax.set_ylim(-462, -338)
ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=5, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sim_iniciales_vista_superior.png"), dpi=220)
plt.close(fig)

# ------------------ Figura 2: trayectoria 3D y el robot --------------------
fig = plt.figure(figsize=(5.6, 4.4))
ax = fig.add_subplot(projection="3d")
for k in COLORES:
    m = letras == k
    ax.plot(puntos[m, 0], puntos[m, 1], puntos[m, 2], color=COLORES[k], lw=1.8, label=NOMBRES[k])
for qv, alfa, etiqueta in [(Q_SEGURA, 0.25, "Pose segura"), (Q[0], 0.55, "Inicio letra J"), (Q[-1], 0.95, "Fin letra M")]:
    P = eslabones(qv)
    ax.plot(P[:, 0], P[:, 1], P[:, 2], "-o", color="0.25", alpha=alfa, ms=3, lw=2.2)
ax.plot([0, 0], [0, 0], [0, 0.05], color="k", lw=6)
ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]"); ax.set_zlabel("Z [m]")
ax.set_xlim(-0.6, 0.3); ax.set_ylim(-0.75, 0.15); ax.set_zlim(0, 0.75)
ax.set_xticks([-0.6, -0.4, -0.2, 0.0, 0.2]); ax.set_yticks([-0.6, -0.4, -0.2, 0.0])
ax.set_zticks([0, 0.2, 0.4, 0.6]); ax.set_box_aspect((1, 1, 0.8))
ax.view_init(elev=24, azim=-62)
ax.legend(fontsize=7, loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sim_trayectoria_3d.png"), dpi=220)
plt.close(fig)

# ---------------- Figura 3: perfil articular y altura del lapiz --------------
fig, axs = plt.subplots(2, 1, figsize=(6.5, 4.4), sharex=True, gridspec_kw={"height_ratios": [3, 1.2]})
ETIQ = ["q1 Base", "q2 Hombro", "q3 Codo", "q4 Muneca 1", "q5 Muneca 2", "q6 Muneca 3"]
for i in range(6):
    axs[0].plot(tiempos, np.degrees(Q[:, i]), lw=1.3, label=ETIQ[i])
for k, t0 in inicio_letra.items():
    for a_ in axs:
        a_.axvline(t0, color="k", ls=":", lw=0.8)
    axs[0].text(t0 + 0.25, 182, f"Popup {k}", fontsize=7, va="top")
axs[0].set_ylabel("Angulo [deg]")
axs[0].set_ylim(-200, 190)
axs[0].grid(alpha=0.3)
axs[0].legend(fontsize=6.5, ncol=3, loc="lower right")
axs[1].plot(tiempos, (puntos[:, 2] - ORIGEN[2]) * 1000, color="k", lw=1.1)
axs[1].set_ylabel("Z rel. [mm]")
axs[1].set_xlabel("Tiempo de movimiento [s] (sin contar la espera en los popups)")
axs[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sim_perfil_articular.png"), dpi=220)
plt.close(fig)

# ------------------------------ Resumen -----------------------------------
resumen = {
    "segmentos_de_movimiento": len(segmentos),
    "muestras_ik": int(len(puntos)),
    "duracion_movimiento_s": round(float(t_acum), 2),
    "error_posicion_ik_max_mm": float(f"{err_p.max() * 1000:.2e}"),
    "error_orientacion_ik_max_rad": float(f"{err_o.max():.2e}"),
    "salto_articular_max_entre_muestras_deg": round(float(salto.max()), 3),
    "manipulabilidad_min_trayectoria": round(float(manip.min()), 5),
    "manipulabilidad_max_trayectoria": round(float(manip.max()), 5),
    "pose_segura_tcp_m": [round(float(x), 4) for x in fk(Q_SEGURA)[:3, 3]],
    "por_letra": {k: {"longitud_trazo_mm": round(long_trazo[k] * 1000, 1),
                      "tiempo_movimiento_s": round(t_letra[k], 2)} for k in "JTSM"},
    "rango_articular_deg": {ETIQ[i]: [round(float(np.degrees(Q[:, i].min())), 1),
                                      round(float(np.degrees(Q[:, i].max())), 1)] for i in range(6)},
}
with open(os.path.join(OUT, "resultados_simulacion.json"), "w", encoding="utf-8") as f:
    json.dump(resumen, f, indent=2, ensure_ascii=False)
print(json.dumps(resumen, indent=2, ensure_ascii=False))
