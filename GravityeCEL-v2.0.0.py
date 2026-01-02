from manim import *
import numpy as np
import yaml
from pathlib import Path

# Cargar configuración desde YAML
config_path = Path(__file__).parent / "config_ecel.yaml"
with open(config_path, 'r') as f:
    CONFIG = yaml.safe_load(f)


class OceanoeCEL(Scene):
    """
    v2.0.0 - Océano eCEL con efecto de desplazamiento (Arquímedes)

    Fase 1: Campo eCEL uniforme, calmado, sin masas
    El océano eCEL llena todo el espacio de forma homogénea.
    """

    def construct(self):
        # Título
        title = Text("Océano eCEL", font_size=48)
        subtitle = Text("Campo uniforme - Estado base", font_size=24)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Crear océano eCEL uniforme (sin masas)
        oceano_ecel = self.crear_oceano_uniforme()

        # Texto explicativo
        texto_oceano = Text(
            "Campo eCEL uniforme - Sin masas",
            font_size=24,
            color=BLUE_A
        ).to_edge(UP)

        self.play(
            FadeIn(oceano_ecel, run_time=2),
            Write(texto_oceano)
        )

        self.wait(2)

        # Mostrar que está "vivo" con pequeña ondulación
        texto_calma = Text(
            "Océano en calma - Densidad homogénea en todo el espacio",
            font_size=22,
            color=BLUE_B
        ).to_edge(DOWN)

        self.play(Write(texto_calma))

        # Pequeña animación de "respiración" del océano
        self.play(
            oceano_ecel.animate.set_opacity(CONFIG['intensidad']['opacidad_maxima'] * 0.7),
            run_time=1.5,
            rate_func=there_and_back
        )

        self.wait(1)

        self.play(
            oceano_ecel.animate.set_opacity(CONFIG['intensidad']['opacidad_maxima'] * 0.7),
            run_time=1.5,
            rate_func=there_and_back
        )

        self.wait(2)

        # Texto final
        texto_final = Text(
            "Este es el estado base del campo eCEL\nListo para recibir masas...",
            font_size=22,
            color=GREEN
        ).to_edge(DOWN)

        self.play(FadeOut(texto_calma), Write(texto_final))
        self.wait(2)

        self.play(FadeOut(oceano_ecel), FadeOut(texto_oceano), FadeOut(texto_final))

    def crear_oceano_uniforme(self):
        """
        Crea el océano eCEL uniforme que llena todo el espacio.
        Todas las partículas tienen la misma opacidad y tamaño.
        Estado base: sin masas, sin perturbaciones.
        """
        oceano = VGroup()

        np.random.seed(42)

        # Parámetros del YAML
        espaciado = CONFIG['malla']['espaciado']
        radio_base = CONFIG['malla']['radio_base']
        variacion = CONFIG['malla']['variacion']
        opacidad_base = CONFIG['intensidad']['opacidad_minima'] + 0.3  # Visible pero suave

        # Cubrir toda la pantalla - Malla simétrica tipo red de tenis
        for x in np.arange(-7.5, 7.5, espaciado):
            for y in np.arange(-4.5, 4.5, espaciado):
                # Sin variación - malla perfectamente simétrica
                radio = radio_base * 0.8

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=radio,
                    color=BLUE_E,
                    fill_opacity=opacidad_base
                )
                oceano.add(dot)

        return oceano


# Para renderizar:
# manim -pql GravityeCEL-v2.0.0.py OceanoeCEL
