from manim import *
import numpy as np
import yaml
from pathlib import Path

# Cargar configuración desde YAML
config_path = Path(__file__).parent / "config_ecel.yaml"
with open(config_path, 'r') as f:
    CONFIG = yaml.safe_load(f)


def calcular_factor_desplazamiento(densidad):
    """
    Calcula el factor de desplazamiento (0-1) según la densidad.
    Basado en tabla real:
    - Agua (1.0): 10%
    - Tierra (5.5): 50%
    - Plomo (11.3): 70%
    - Oro (19.3): 85%
    - Agujero negro (100+): 100%
    """
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
    v2.1.1 - Distribución HOMOGÉNEA de eCEL

    Cambios vs v2.1.0:
    - Sin variaciones aleatorias (entropía = estado de menor energía)
    - Distribución uniforme en círculos concéntricos perfectos
    - Distancia mínima entre partículas (cargas iguales se repelen)
    - Sin espacios vacíos
    """

    def construct(self):
        nombre = CONFIG['masa_actual']['nombre']
        densidad = CONFIG['masa_actual']['densidad']
        factor = calcular_factor_desplazamiento(densidad)

        # Título
        title = Text("Océano eCEL - Distribución Homogénea", font_size=40)
        subtitle = Text(
            f"{nombre} (ρ={densidad} g/cm³) → {factor*100:.0f}% desplazamiento",
            font_size=22
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
        radio_visual = CONFIG['masa_actual']['radio_visual']
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

        # 3. eCEL "BROTA" en la periferia - HOMOGÉNEO
        texto_brota = Text(
            f"eCEL acumulado homogéneamente ({factor*100:.0f}%)",
            font_size=22,
            color=GREEN
        ).to_edge(DOWN)

        self.play(FadeOut(texto_masa), Write(texto_brota))

        # Crear eCEL acumulado HOMOGÉNEO
        ecel_acumulado = self.crear_ecel_homogeneo(masa, densidad, radio_visual)

        # Animar el "brote" del eCEL
        self.play(
            FadeIn(ecel_acumulado, scale=0.5),
            run_time=CONFIG['animacion']['duracion_desplazamiento'],
            rate_func=smooth
        )

        self.wait(1)

        # 4. Texto explicativo
        texto_gradiente = Text(
            "Distribución uniforme: cargas iguales se repelen\n"
            "Distancia mínima garantizada (menor energía)",
            font_size=18,
            color=WHITE
        ).to_edge(DOWN)

        self.play(FadeOut(texto_brota), Write(texto_gradiente))
        self.wait(2)

        # 5. Texto final
        texto_final = Text(
            f"Gradiente 1/r² sin espacios vacíos\n"
            "eCEL nunca se toca (repulsión coulombiana)",
            font_size=18,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(FadeOut(texto_gradiente), Write(texto_final))
        self.wait(CONFIG['animacion']['duracion_final'])

        # Fade out
        self.play(
            FadeOut(oceano_fondo),
            FadeOut(masa),
            FadeOut(label),
            FadeOut(ecel_acumulado),
            FadeOut(texto_oceano),
            FadeOut(texto_final)
        )

    def crear_oceano_fondo(self):
        """
        Océano eCEL de fondo: uniforme, decorativo.
        """
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

    def crear_ecel_homogeneo(self, masa, densidad, radio_masa):
        """
        Crea eCEL acumulado con DISTRIBUCIÓN HOMOGÉNEA.

        Características:
        - Círculos concéntricos perfectos (sin variación aleatoria)
        - Espaciado uniforme entre partículas
        - Distancia mínima garantizada (cargas se repelen)
        - Sin espacios vacíos
        - Gradiente 1/r² en opacidad
        """
        ecel = VGroup()

        centro = masa.get_center()
        factor = calcular_factor_desplazamiento(densidad)

        opacidad_max = CONFIG['intensidad']['opacidad_acumulacion']
        color_acum = CONFIG['malla']['color_acumulacion']
        radio_particula = CONFIG['malla']['radio_base']

        # Distancia mínima entre partículas (repulsión)
        distancia_minima = radio_particula * 2.5

        # Más capas para distribución más densa
        num_capas = 12

        # Espaciado entre capas (uniforme)
        espaciado_capas = distancia_minima * 1.2

        for capa in range(num_capas):
            # Radio de esta capa (desde superficie hacia afuera)
            r = radio_masa + 0.05 + capa * espaciado_capas

            # Densidad según 1/r²
            factor_r2 = (radio_masa / r) ** 2

            # Opacidad proporcional a densidad
            opacidad_capa = opacidad_max * factor_r2 * factor
            opacidad_capa = max(0.15, min(opacidad_capa, opacidad_max))

            # Calcular cuántas partículas caben en este círculo
            # respetando distancia mínima
            circunferencia = 2 * np.pi * r
            particulas_capa = int(circunferencia / distancia_minima)
            particulas_capa = max(8, particulas_capa)

            # Distribuir UNIFORMEMENTE en círculo perfecto
            for i in range(particulas_capa):
                # Ángulo exacto, sin variación
                angulo = 2 * np.pi * i / particulas_capa

                # Posición exacta, sin variación
                x = centro[0] + r * np.cos(angulo)
                y = centro[1] + r * np.sin(angulo)

                # Radio partícula decrece con distancia (gradiente)
                radio_p = radio_particula * (0.8 + factor_r2 * 0.4)

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=radio_p,
                    color=color_acum,
                    fill_opacity=opacidad_capa
                )
                ecel.add(dot)

        return ecel


class ComparacionDensidades(Scene):
    """
    Compara el efecto de desplazamiento para diferentes densidades.
    Distribución homogénea.
    """

    def construct(self):
        title = Text("Comparación: Distribución Homogénea", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP).scale(0.7))

        # Tres materiales
        materiales = [
            ("Agua", 1.0, BLUE_A),
            ("Tierra", 5.5, BLUE_D),
            ("Plomo", 11.3, GRAY)
        ]

        grupos = VGroup()

        for i, (nombre, densidad, color) in enumerate(materiales):
            factor = calcular_factor_desplazamiento(densidad)
            x_pos = -4 + i * 4

            masa = Circle(radius=0.5, color=color, fill_opacity=0.9)
            masa.move_to(np.array([x_pos, 0, 0]))

            label = Text(f"{nombre}\nρ={densidad}", font_size=14)
            label.next_to(masa, DOWN, buff=0.3)

            pct = Text(f"{factor*100:.0f}%", font_size=20, color=YELLOW)
            pct.next_to(masa, UP, buff=0.3)

            grupo = VGroup(masa, label, pct)
            grupos.add(grupo)

        self.play(FadeIn(grupos))
        self.wait(1)

        # Crear eCEL homogéneo para cada uno
        for i, (nombre, densidad, color) in enumerate(materiales):
            x_pos = -4 + i * 4
            centro = np.array([x_pos, 0, 0])

            ecel = self.crear_ecel_homogeneo_simple(centro, densidad, 0.5)
            self.play(FadeIn(ecel, scale=0.5), run_time=0.8)

        self.wait(3)

    def crear_ecel_homogeneo_simple(self, centro, densidad, radio_masa):
        """Versión simplificada del eCEL homogéneo."""
        ecel = VGroup()
        factor = calcular_factor_desplazamiento(densidad)

        radio_particula = 0.025
        distancia_minima = radio_particula * 2.5
        num_capas = 6

        for capa in range(num_capas):
            r = radio_masa + 0.05 + capa * distancia_minima * 1.2
            factor_r2 = (radio_masa / r) ** 2
            opacidad = 0.9 * factor_r2 * factor
            opacidad = max(0.15, opacidad)

            circunferencia = 2 * np.pi * r
            particulas = max(6, int(circunferencia / distancia_minima))

            for i in range(particulas):
                angulo = 2 * np.pi * i / particulas
                x = centro[0] + r * np.cos(angulo)
                y = centro[1] + r * np.sin(angulo)

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=radio_particula * (0.8 + factor_r2 * 0.4),
                    color=BLUE_B,
                    fill_opacity=opacidad
                )
                ecel.add(dot)

        return ecel


# Para renderizar:
# manim -pql GravityeCEL-v2.1.1.py OceanoeCEL
# manim -pql GravityeCEL-v2.1.1.py ComparacionDensidades
