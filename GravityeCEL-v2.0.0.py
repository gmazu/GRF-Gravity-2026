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

    1. Campo eCEL uniforme (océano en calma)
    2. Aparece masa Tierra
    3. eCEL se desplaza del volumen de la masa
    4. eCEL se acumula en la periferia
    5. Densidad decae con 1/r²
    """

    def construct(self):
        # Título
        title = Text("Océano eCEL", font_size=48)
        subtitle = Text("Efecto de desplazamiento (Arquímedes)", font_size=24)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Crear océano eCEL uniforme
        oceano_ecel, posiciones_originales = self.crear_oceano_uniforme()

        texto_oceano = Text(
            "Campo eCEL uniforme - Sin masas",
            font_size=24,
            color=BLUE_A
        ).to_edge(UP)

        self.play(
            FadeIn(oceano_ecel, run_time=2),
            Write(texto_oceano)
        )
        self.wait(1)

        # Texto preparación
        texto_masa = Text(
            "Introduciendo masa M₁ (Tierra)...",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(texto_masa))
        self.wait(1)

        # Crear la Tierra
        radio_tierra = CONFIG['tierra']['radio_visual']
        color_tierra = CONFIG['tierra']['color']

        tierra = Circle(
            radius=radio_tierra,
            color=color_tierra,
            fill_opacity=0.9,
            stroke_width=2
        )
        tierra.move_to(ORIGIN)

        label_tierra = Text("M₁", font_size=24, color=WHITE)
        label_tierra.move_to(tierra.get_center())

        # Mostrar tierra apareciendo
        self.play(
            GrowFromCenter(tierra),
            Write(label_tierra),
            run_time=1.5
        )

        # Efecto de desplazamiento - animar las partículas
        texto_desplaza = Text(
            "eCEL desplazado por el volumen de la masa",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(FadeOut(texto_masa), Write(texto_desplaza))

        # Animar el desplazamiento
        self.animar_desplazamiento(oceano_ecel, posiciones_originales, tierra)

        self.wait(1)

        # Texto acumulación
        texto_acumula = Text(
            "eCEL se acumula en la periferia - Densidad ∝ 1/r²",
            font_size=22,
            color=GREEN
        ).to_edge(DOWN)

        self.play(FadeOut(texto_desplaza), Write(texto_acumula))
        self.wait(2)

        # Texto final
        texto_final = Text(
            "Principio de Arquímedes en campo eCEL\nVolumen desplazado = Volumen de la masa",
            font_size=20,
            color=WHITE
        ).to_edge(DOWN)

        self.play(FadeOut(texto_acumula), Write(texto_final))
        self.wait(3)

        self.play(
            FadeOut(oceano_ecel),
            FadeOut(tierra),
            FadeOut(label_tierra),
            FadeOut(texto_oceano),
            FadeOut(texto_final)
        )

    def crear_oceano_uniforme(self):
        """
        Crea el océano eCEL uniforme.
        Retorna el VGroup y las posiciones originales para animación.
        """
        oceano = VGroup()
        posiciones = []

        espaciado = CONFIG['malla']['espaciado']
        radio_base = CONFIG['malla']['radio_base']
        opacidad_base = CONFIG['intensidad']['opacidad_minima'] + 0.3

        for x in np.arange(-7.5, 7.5, espaciado):
            for y in np.arange(-4.5, 4.5, espaciado):
                pos = np.array([x, y, 0])
                posiciones.append(pos.copy())

                dot = Dot(
                    point=pos,
                    radius=radio_base * 0.8,
                    color=BLUE_E,
                    fill_opacity=opacidad_base
                )
                oceano.add(dot)

        return oceano, posiciones

    def animar_desplazamiento(self, oceano, posiciones_originales, masa):
        """
        Anima el desplazamiento del eCEL por la masa.
        - Partículas dentro de la masa se mueven hacia afuera
        - Partículas cercanas aumentan densidad (opacidad)
        - Decaimiento 1/r²
        """
        centro_masa = masa.get_center()
        radio_masa = CONFIG['tierra']['radio_visual']

        fuerza = CONFIG['perturbacion']['fuerza']
        exponente = CONFIG['perturbacion']['exponente_distancia']
        opacidad_max = CONFIG['intensidad']['opacidad_maxima']
        opacidad_min = CONFIG['intensidad']['opacidad_minima']
        multiplicador = CONFIG['intensidad']['multiplicador']

        animaciones = []

        for i, dot in enumerate(oceano):
            pos_original = posiciones_originales[i]
            distancia = np.linalg.norm(pos_original[:2] - centro_masa[:2])

            if distancia < radio_masa:
                # Partícula DENTRO de la masa → empujar hacia afuera
                if distancia < 0.01:
                    # Muy cerca del centro, empujar en dirección aleatoria
                    direccion = np.array([np.random.uniform(-1, 1), np.random.uniform(-1, 1), 0])
                else:
                    direccion = (pos_original - centro_masa)

                direccion = direccion / (np.linalg.norm(direccion) + 0.001)

                # Mover justo afuera del radio + un poco más
                nueva_distancia = radio_masa + 0.05 + (radio_masa - distancia) * fuerza
                nueva_pos = centro_masa + direccion * nueva_distancia

                animaciones.append(dot.animate.move_to(nueva_pos).set_opacity(opacidad_max * 0.8))

            elif distancia < radio_masa * 3:
                # Partícula CERCA de la masa → acumular (mayor opacidad)
                # Intensidad con 1/r²
                intensidad = 1.0 / (max(distancia - radio_masa, 0.1) ** 2)
                opacidad = min(opacidad_max, intensidad * multiplicador)
                opacidad = max(opacidad_min + 0.2, opacidad)

                # Pequeño desplazamiento hacia afuera (compresión)
                direccion = (pos_original - centro_masa)
                direccion = direccion / (np.linalg.norm(direccion) + 0.001)
                desplazamiento = fuerza * 0.3 / (distancia ** exponente)
                nueva_pos = pos_original + direccion * desplazamiento

                animaciones.append(dot.animate.move_to(nueva_pos).set_opacity(opacidad))

            else:
                # Partícula LEJOS → mantener opacidad base con leve 1/r²
                intensidad = 1.0 / (distancia ** 2)
                opacidad = opacidad_min + 0.1 + intensidad * multiplicador * 0.5
                opacidad = min(opacidad, opacidad_min + 0.3)

                animaciones.append(dot.animate.set_opacity(opacidad))

        # Ejecutar todas las animaciones juntas
        self.play(*animaciones, run_time=2, rate_func=smooth)


# Para renderizar:
# manim -pql GravityeCEL-v2.0.0.py OceanoeCEL
