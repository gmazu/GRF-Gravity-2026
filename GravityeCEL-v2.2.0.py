from manim import *
import numpy as np
import yaml
from pathlib import Path

# Cargar configuración desde YAML
config_path = Path(__file__).parent / "config_ecel.yaml"
with open(config_path, 'r') as f:
    CONFIG = yaml.safe_load(f)


def calcular_factor_desplazamiento(densidad):
    """Calcula factor de desplazamiento según densidad."""
    if densidad >= 100:
        return 1.0
    elif densidad >= 19.3:
        return 0.85 + (densidad - 19.3) / (100 - 19.3) * 0.15
    elif densidad >= 11.3:
        return 0.70 + (densidad - 11.3) / (19.3 - 11.3) * 0.15
    elif densidad >= 5.5:
        return 0.50 + (densidad - 5.5) / (11.3 - 5.5) * 0.20
    elif densidad >= 1.0:
        return 0.10 + (densidad - 1.0) / (5.5 - 1.0) * 0.40
    else:
        return densidad * 0.10


class OceanoeCEL(Scene):
    """
    v2.1.4 - Difuminación MÁS SUAVE del halo

    Basado en v2.1.3 pero con gradiente más suave:
    - Capas externas se desvanecen COMPLETAMENTE (opacidad -> 0)
    - Sin borde visible en la última capa
    - Transición suave del centro hacia afuera
    """

    def construct(self):
        nombre = CONFIG['masa_actual']['nombre']
        densidad = CONFIG['masa_actual']['densidad']
        radio_visual = CONFIG['masa_actual']['radio_visual']
        factor = calcular_factor_desplazamiento(densidad)

        # Título
        title = Text("Océano eCEL - Efecto Cascada", font_size=40)
        subtitle = Text(
            f"eCEL desplazado desplaza más eCEL → Halo extendido",
            font_size=20
        )
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(CONFIG['animacion']['duracion_intro'])
        self.play(FadeOut(title), FadeOut(subtitle))

        # 1. Crear océano eCEL de fondo
        oceano_fondo = self.crear_oceano_fondo()

        texto_oceano = Text(
            "Océano eCEL uniforme (estado base)",
            font_size=22,
            color=BLUE_A
        ).to_edge(UP)

        self.play(
            FadeIn(oceano_fondo),
            Write(texto_oceano),
            run_time=CONFIG['animacion']['duracion_oceano']
        )
        self.wait(1)

        # 2. Crear la masa
        color_masa = CONFIG['masa_actual']['color']

        masa = Circle(
            radius=radio_visual,
            color=color_masa,
            fill_opacity=0.9,
            stroke_width=3
        )
        masa.move_to(ORIGIN)

        label = Text(nombre, font_size=18, color=WHITE)
        label.move_to(masa.get_center())

        texto_masa = Text(
            f"Introduciendo {nombre}...",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(texto_masa))
        self.play(
            GrowFromCenter(masa),
            Write(label),
            run_time=CONFIG['animacion']['duracion_masa']
        )

        # 3. eCEL desplazado con efecto cascada
        texto_cascada = Text(
            f"eCEL desplazado se organiza → Halo extendido ({factor*100:.0f}%)",
            font_size=20,
            color=GREEN
        ).to_edge(DOWN)

        self.play(FadeOut(texto_masa), Write(texto_cascada))

        # Crear halo completo con efecto cascada y difuminación suave
        ecel_cascada = self.crear_ecel_cascada_suave(
            masa.get_center(), densidad, radio_visual
        )

        self.play(
            FadeIn(ecel_cascada, scale=0.5),
            run_time=CONFIG['animacion']['duracion_desplazamiento'],
            rate_func=smooth
        )

        self.wait(1)

        # Rayo de luz curvado por gradiente 1/r²
        if CONFIG.get('luz', {}).get('habilitada', False):
            rayo = self.crear_rayo_luz(ORIGIN, radio_visual)
            if rayo is not None:
                self.play(FadeIn(rayo), run_time=1.2)

        # 4. FADE OUT del fondo - solo queda masa + halo
        texto_sin_fondo = Text(
            "Fondo desaparece → Solo halo visible",
            font_size=20,
            color=WHITE
        ).to_edge(DOWN)

        self.play(
            FadeOut(oceano_fondo),
            FadeOut(texto_oceano),
            FadeOut(texto_cascada),
            Write(texto_sin_fondo),
            run_time=1.5
        )

        self.wait(2)

        # 5. Texto final
        texto_final = Text(
            f"Halo extendido sin ruido de fondo\n"
            "ρ_total = ρ_nivel1 + ρ_nivel2 + ρ_nivel3 + ...",
            font_size=18,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(FadeOut(texto_sin_fondo), Write(texto_final))
        self.wait(CONFIG['animacion']['duracion_final'])

        # Fade out final
        self.play(
            FadeOut(masa),
            FadeOut(label),
            FadeOut(ecel_cascada),
            FadeOut(texto_final)
        )

    def crear_oceano_fondo(self):
        """Océano eCEL de fondo uniforme."""
        oceano = VGroup()

        espaciado = CONFIG['malla']['espaciado']
        radio = CONFIG['malla']['radio_base'] * 0.6
        opacidad = CONFIG['intensidad']['opacidad_minima']
        color = CONFIG['malla']['color_fondo']

        for x in np.arange(-7.5, 7.5, espaciado):
            for y in np.arange(-4.5, 4.5, espaciado):
                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=radio,
                    color=color,
                    fill_opacity=opacidad
                )
                oceano.add(dot)

        return oceano

    def crear_ecel_cascada_suave(self, centro, densidad, radio_masa):
        """
        Crea halo con DIFUMINACIÓN SUAVE.

        Diferencia con v2.1.3:
        - Opacidad mínima = 0 (no 0.1)
        - Factor de desvanecimiento adicional para capas externas
        - Las últimas capas desaparecen completamente
        """
        ecel = VGroup()

        centro_arr = np.array([centro[0], centro[1], 0]) if not isinstance(centro, np.ndarray) else centro

        factor = calcular_factor_desplazamiento(densidad)
        opacidad_max = CONFIG['intensidad']['opacidad_acumulacion']
        radio_particula = CONFIG['malla']['radio_base']
        distancia_minima = radio_particula * 2.5

        num_capas = 65  # Suficientes para que opacidad llegue naturalmente bajo 1%
        espaciado_base = distancia_minima * 1.2

        for capa in range(num_capas):
            r = radio_masa + 0.05 + capa * espaciado_base

            factor_r2 = (radio_masa / r) ** 2
            factor_cascada = 1.0 + 0.3 * np.exp(-capa / 5)

            # Opacidad: gradiente continuo de max → 0
            opacidad_capa = opacidad_max * factor_r2 * factor * factor_cascada
            opacidad_capa = min(opacidad_capa, opacidad_max)

            # No crear si muy baja
            if opacidad_capa < 0.01:
                continue

            t_capa = capa / num_capas
            circunferencia = 2 * np.pi * r
            particulas_capa = int(circunferencia / distancia_minima)
            particulas_capa = max(10, particulas_capa)

            color_capa = interpolate_color(BLUE_B, PURPLE_A, t_capa)

            for i in range(particulas_capa):
                angulo = 2 * np.pi * i / particulas_capa

                x = centro_arr[0] + r * np.cos(angulo)
                y = centro_arr[1] + r * np.sin(angulo)

                radio_p = radio_particula * (0.8 + factor_r2 * 0.4)

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=max(radio_p, radio_particula * 0.5),
                    color=color_capa,
                    fill_opacity=opacidad_capa
                )
                ecel.add(dot)

        return ecel

    def crear_rayo_luz(self, centro, radio_masa):
        """Rayo de luz curvado por gradiente 1/r² con efecto arcoíris."""
        cfg = CONFIG['luz']
        start = np.array([cfg['start'][0], cfg['start'][1], 0.0])
        dir_vec = np.array([cfg['dir'][0], cfg['dir'][1], 0.0])
        dir_vec = dir_vec / np.linalg.norm(dir_vec)

        speed = cfg['speed']
        steps = cfg['steps']
        dt = cfg['dt']
        k = cfg['k_curvatura']
        min_dist = radio_masa * cfg['min_dist_factor']

        puntos = []
        p = start.copy()
        v = dir_vec.copy()

        for _ in range(steps):
            r_vec = p - centro
            r = np.linalg.norm(r_vec)
            if r < min_dist:
                r = min_dist
            r_hat = r_vec / r

            # Componente perpendicular para evitar quiebres
            v_hat = v / np.linalg.norm(v)
            proj = np.dot(r_hat, v_hat)
            perp = r_hat - proj * v_hat
            accel = k * (radio_masa ** 2 / (r ** 3)) * perp

            v = v + accel * dt
            v = v / np.linalg.norm(v)
            p = p + v * speed * dt
            puntos.append(p.copy())

        if len(puntos) < 2:
            return None

        base = VMobject()
        base.set_points_smoothly(puntos)
        base.set_color_by_gradient(*cfg['colors_rainbow'])
        base.set_stroke(width=cfg['stroke_width'], opacity=cfg['core_opacity'])

        glow = VGroup()
        for width, opacity in zip(cfg['glow_widths'], cfg['glow_opacities']):
            layer = base.copy()
            layer.set_stroke(width=width, opacity=opacity)
            glow.add(layer)

        return VGroup(glow, base)


# Para renderizar:
# manim -pql GravityeCEL-v2.2.0.py OceanoeCEL
