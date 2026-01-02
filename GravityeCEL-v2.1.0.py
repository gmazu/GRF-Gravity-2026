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

    Retorna valor entre 0 y 1.
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


def calcular_ecel_desplazado(densidad, radio):
    """
    Calcula cantidad de eCEL desplazado.
    Proporcional a masa² (cuadrático).
    masa ∝ densidad × volumen = densidad × r³
    desplazamiento ∝ masa² = (densidad × r³)²

    Para visualización, normalizamos el resultado.
    """
    factor = calcular_factor_desplazamiento(densidad)
    # Masa proporcional a densidad × volumen (r³)
    masa_relativa = densidad * (radio ** 3)
    # Desplazamiento cuadrático
    desplazamiento = factor * (masa_relativa ** 2)
    # Normalizar para visualización (escala logarítmica para que se vea bien)
    return min(desplazamiento, 1000)  # Cap para visualización


class OceanoeCEL(Scene):
    """
    v2.1.0 - Océano eCEL con desplazamiento CORRECTO

    Lógica:
    1. Océano eCEL uniforme de fondo (decorativo)
    2. Masa aparece
    3. eCEL "BROTA" en la periferia (no mover existentes)
    4. Cantidad que brota ∝ masa² (cuadrático)
    5. Gradiente 1/r² desde la superficie
    6. Factor según tabla de densidad real
    """

    def construct(self):
        nombre = CONFIG['masa_actual']['nombre']
        densidad = CONFIG['masa_actual']['densidad']
        factor = calcular_factor_desplazamiento(densidad)

        # Título
        title = Text("Océano eCEL - Desplazamiento", font_size=42)
        subtitle = Text(
            f"{nombre} (ρ={densidad} g/cm³) → {factor*100:.0f}% desplazamiento",
            font_size=22
        )
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(CONFIG['animacion']['duracion_intro'])
        self.play(FadeOut(title), FadeOut(subtitle))

        # 1. Crear océano eCEL de fondo (decorativo, uniforme)
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

        # 3. eCEL "BROTA" en la periferia
        texto_brota = Text(
            f"eCEL desplazado BROTA en periferia ({factor*100:.0f}%)",
            font_size=22,
            color=GREEN
        ).to_edge(DOWN)

        self.play(FadeOut(texto_masa), Write(texto_brota))

        # Crear eCEL acumulado que aparece
        ecel_acumulado = self.crear_ecel_acumulado(masa, densidad, radio_visual)

        # Animar el "brote" del eCEL
        self.play(
            FadeIn(ecel_acumulado, scale=0.5),
            run_time=CONFIG['animacion']['duracion_desplazamiento'],
            rate_func=smooth
        )

        self.wait(1)

        # 4. Mostrar gradiente 1/r²
        texto_gradiente = Text(
            "Gradiente: ρ_eCEL(r) = ρ_superficie × (R/r)²",
            font_size=20,
            color=WHITE
        ).to_edge(DOWN)

        self.play(FadeOut(texto_brota), Write(texto_gradiente))
        self.wait(2)

        # 5. Texto final
        texto_final = Text(
            f"Densidad {densidad} g/cm³ → Desplazamiento {factor*100:.0f}%\n"
            "Agujero negro (∞) → 100% (singularidad, sin luz)",
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
        Océano eCEL de fondo: uniforme, ligero, decorativo.
        Solo para dar contexto visual.
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

    def crear_ecel_acumulado(self, masa, densidad, radio_masa):
        """
        Crea el eCEL que "BROTA" en la periferia.
        - Cantidad proporcional a masa² (cuadrático)
        - Distribuido según gradiente 1/r²
        - NO son partículas movidas, son NUEVAS que aparecen
        """
        ecel = VGroup()

        centro = masa.get_center()
        factor = calcular_factor_desplazamiento(densidad)

        opacidad_max = CONFIG['intensidad']['opacidad_acumulacion']
        color_acum = CONFIG['malla']['color_acumulacion']
        radio_particula = CONFIG['malla']['radio_base']

        # Cantidad de eCEL que brota (proporcional a masa²)
        # masa ∝ densidad × r³
        masa_relativa = densidad * (radio_masa ** 3)
        cantidad_base = int(50 * factor * np.sqrt(masa_relativa))
        cantidad_base = max(30, min(cantidad_base, 500))  # Entre 30 y 500

        # Distribuir en capas concéntricas con gradiente 1/r²
        num_capas = 8

        for capa in range(num_capas):
            # Radio de esta capa (desde superficie hacia afuera)
            r = radio_masa + 0.1 + capa * 0.15

            # Densidad en esta capa según 1/r²
            # ρ(r) = ρ_superficie × (R/r)²
            factor_r2 = (radio_masa / r) ** 2

            # Opacidad proporcional a densidad
            opacidad_capa = opacidad_max * factor_r2 * factor
            opacidad_capa = max(0.1, min(opacidad_capa, opacidad_max))

            # Cantidad de partículas en esta capa
            # Más partículas cerca de la superficie
            particulas_capa = int(cantidad_base * factor_r2)
            particulas_capa = max(8, particulas_capa)

            # Distribuir en círculo
            for i in range(particulas_capa):
                angulo = 2 * np.pi * i / particulas_capa
                # Pequeña variación para no verse perfecto
                r_var = r + np.random.uniform(-0.03, 0.03)
                angulo_var = angulo + np.random.uniform(-0.1, 0.1)

                x = centro[0] + r_var * np.cos(angulo_var)
                y = centro[1] + r_var * np.sin(angulo_var)

                # Radio partícula también decrece con distancia
                radio_p = radio_particula * (1 + factor_r2 * 0.5)

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
    Muestra lado a lado: Agua vs Tierra vs Plomo
    """

    def construct(self):
        title = Text("Comparación: Desplazamiento según Densidad", font_size=36)
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

            # Posición
            x_pos = -4 + i * 4

            # Masa
            masa = Circle(radius=0.5, color=color, fill_opacity=0.9)
            masa.move_to(np.array([x_pos, 0, 0]))

            # Label
            label = Text(f"{nombre}\nρ={densidad}", font_size=14)
            label.next_to(masa, DOWN, buff=0.3)

            # Porcentaje
            pct = Text(f"{factor*100:.0f}%", font_size=20, color=YELLOW)
            pct.next_to(masa, UP, buff=0.3)

            grupo = VGroup(masa, label, pct)
            grupos.add(grupo)

        self.play(FadeIn(grupos))
        self.wait(1)

        # Crear eCEL acumulado para cada uno
        for i, (nombre, densidad, color) in enumerate(materiales):
            x_pos = -4 + i * 4
            centro = np.array([x_pos, 0, 0])

            ecel = self.crear_ecel_simple(centro, densidad, 0.5)
            self.play(FadeIn(ecel, scale=0.5), run_time=0.8)

        self.wait(3)

    def crear_ecel_simple(self, centro, densidad, radio_masa):
        """Versión simplificada del eCEL acumulado."""
        ecel = VGroup()
        factor = calcular_factor_desplazamiento(densidad)

        num_capas = 5
        cantidad_base = int(20 * factor)

        for capa in range(num_capas):
            r = radio_masa + 0.08 + capa * 0.1
            factor_r2 = (radio_masa / r) ** 2
            opacidad = 0.8 * factor_r2 * factor
            particulas = max(6, int(cantidad_base * factor_r2))

            for i in range(particulas):
                angulo = 2 * np.pi * i / particulas + np.random.uniform(-0.1, 0.1)
                r_var = r + np.random.uniform(-0.02, 0.02)

                x = centro[0] + r_var * np.cos(angulo)
                y = centro[1] + r_var * np.sin(angulo)

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=0.02 * (1 + factor_r2),
                    color=BLUE_B,
                    fill_opacity=max(0.1, opacidad)
                )
                ecel.add(dot)

        return ecel


# Para renderizar:
# manim -pql GravityeCEL-v2.1.0.py OceanoeCEL
# manim -pql GravityeCEL-v2.1.0.py ComparacionDensidades
