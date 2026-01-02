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
    v2.0.1 - Océano eCEL con desplazamiento basado en DENSIDAD

    El desplazamiento de eCEL depende de la densidad de la masa:
    - Densidad baja (poroso): eCEL se cuela entre espacios
    - Densidad alta (denso): eCEL desplazado se acumula en periferia
    - Agujero negro (densidad → ∞): todo el eCEL desplazado, singularidad

    Efecto Arquímedes: el eCEL desplazado NO desaparece, se ACUMULA
    en la superficie con gradiente 1/r²
    """

    def construct(self):
        # Título
        nombre_masa = CONFIG['masa_actual']['nombre']
        densidad = CONFIG['masa_actual']['densidad']

        title = Text("Océano eCEL", font_size=48)
        subtitle = Text(f"Desplazamiento por densidad - {nombre_masa} ({densidad} g/cm³)", font_size=22)
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
            f"Introduciendo {nombre_masa} (densidad: {densidad} g/cm³)...",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(texto_masa))
        self.wait(1)

        # Crear la masa
        radio_visual = CONFIG['masa_actual']['radio_visual']
        color_masa = CONFIG['masa_actual']['color']

        masa = Circle(
            radius=radio_visual,
            color=color_masa,
            fill_opacity=0.85,
            stroke_width=2
        )
        masa.move_to(ORIGIN)

        label_masa = Text(nombre_masa, font_size=20, color=WHITE)
        label_masa.move_to(masa.get_center())

        # Mostrar masa apareciendo
        self.play(
            GrowFromCenter(masa),
            Write(label_masa),
            run_time=1.5
        )

        # Efecto de desplazamiento basado en densidad
        texto_desplaza = Text(
            f"eCEL desplazado según densidad ({densidad} g/cm³)",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(FadeOut(texto_masa), Write(texto_desplaza))

        # Animar el desplazamiento con gradiente
        self.animar_desplazamiento_densidad(oceano_ecel, posiciones_originales, masa)

        self.wait(1)

        # Texto acumulación
        texto_acumula = Text(
            "eCEL acumulado en periferia - Gradiente ∝ 1/r²",
            font_size=22,
            color=GREEN
        ).to_edge(DOWN)

        self.play(FadeOut(texto_desplaza), Write(texto_acumula))
        self.wait(2)

        # Texto final explicativo
        texto_final = Text(
            f"Densidad {densidad} g/cm³ → Desplazamiento parcial\n"
            "Agujero negro (∞) → Desplazamiento total (singularidad)",
            font_size=18,
            color=WHITE
        ).to_edge(DOWN)

        self.play(FadeOut(texto_acumula), Write(texto_final))
        self.wait(3)

        self.play(
            FadeOut(oceano_ecel),
            FadeOut(masa),
            FadeOut(label_masa),
            FadeOut(texto_oceano),
            FadeOut(texto_final)
        )

    def crear_oceano_uniforme(self):
        """
        Crea el océano eCEL uniforme.
        Retorna el VGroup y las posiciones originales.
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

    def animar_desplazamiento_densidad(self, oceano, posiciones_originales, masa):
        """
        Desplazamiento basado en DENSIDAD:
        - Calcula factor de desplazamiento según densidad
        - Algunas partículas se "cuelan" (quedan dentro)
        - Las desplazadas se ACUMULAN en la periferia
        - Gradiente 1/r² desde la superficie
        """
        centro_masa = masa.get_center()
        radio_masa = CONFIG['masa_actual']['radio_visual']
        densidad = CONFIG['masa_actual']['densidad']

        # Calcular factor de desplazamiento (0 a 1)
        densidad_max = CONFIG['desplazamiento']['densidad_maxima']
        factor_colado = CONFIG['desplazamiento']['factor_colado']

        # Factor: 0 = nada desplazado, 1 = todo desplazado (agujero negro)
        factor_desplazamiento = min(1.0, densidad / densidad_max)

        opacidad_max = CONFIG['intensidad']['opacidad_maxima']
        opacidad_min = CONFIG['intensidad']['opacidad_minima']
        multiplicador = CONFIG['intensidad']['multiplicador']

        animaciones = []

        # Contar partículas dentro para calcular acumulación
        particulas_dentro = sum(1 for pos in posiciones_originales
                               if np.linalg.norm(pos[:2] - centro_masa[:2]) < radio_masa)

        # eCEL total desplazado (proporcional a densidad)
        ecel_desplazado = particulas_dentro * factor_desplazamiento

        for i, dot in enumerate(oceano):
            pos_original = posiciones_originales[i]
            distancia = np.linalg.norm(pos_original[:2] - centro_masa[:2])

            if distancia < radio_masa:
                # Partícula DENTRO de la masa
                # Probabilidad de "colarse" depende de la densidad
                prob_colarse = factor_colado * (1 - factor_desplazamiento)

                if np.random.random() < prob_colarse:
                    # Se cuela - queda adentro con opacidad reducida
                    animaciones.append(
                        dot.animate.set_opacity(opacidad_min * 0.5).set_color(BLUE_E)
                    )
                else:
                    # Se desplaza hacia la superficie
                    if distancia < 0.01:
                        direccion = np.array([np.random.uniform(-1, 1),
                                            np.random.uniform(-1, 1), 0])
                    else:
                        direccion = (pos_original - centro_masa)

                    direccion = direccion / (np.linalg.norm(direccion) + 0.001)

                    # Mover justo a la superficie (acumulación)
                    # Distancia desde el centro: radio + pequeño offset basado en posición original
                    offset = 0.02 + (radio_masa - distancia) * 0.1
                    nueva_pos = centro_masa + direccion * (radio_masa + offset)

                    # Alta opacidad en la superficie (acumulación)
                    opacidad_superficie = opacidad_max * (0.7 + 0.3 * factor_desplazamiento)

                    animaciones.append(
                        dot.animate.move_to(nueva_pos)
                        .set_opacity(opacidad_superficie)
                        .set_color(BLUE_B)
                    )

            elif distancia < radio_masa * 4:
                # Partícula CERCA - gradiente 1/r²
                dist_desde_superficie = distancia - radio_masa

                # Intensidad con 1/r² desde la superficie
                intensidad = ecel_desplazado / (max(dist_desde_superficie, 0.1) ** 2)
                intensidad = intensidad / particulas_dentro  # Normalizar

                opacidad = opacidad_min + intensidad * multiplicador * 2
                opacidad = min(opacidad_max * 0.9, opacidad)
                opacidad = max(opacidad_min + 0.1, opacidad)

                # Leve desplazamiento hacia afuera (compresión)
                direccion = (pos_original - centro_masa)
                direccion = direccion / (np.linalg.norm(direccion) + 0.001)
                desplazamiento = 0.05 * factor_desplazamiento / (dist_desde_superficie + 0.5)
                nueva_pos = pos_original + direccion * desplazamiento

                # Color más brillante cerca de la superficie
                if dist_desde_superficie < radio_masa * 0.5:
                    color = BLUE_C
                else:
                    color = BLUE_D

                animaciones.append(
                    dot.animate.move_to(nueva_pos)
                    .set_opacity(opacidad)
                    .set_color(color)
                )

            else:
                # Partícula LEJOS - efecto mínimo
                intensidad = 1.0 / (distancia ** 2)
                opacidad = opacidad_min + intensidad * multiplicador * 0.3
                opacidad = min(opacidad, opacidad_min + 0.2)

                animaciones.append(dot.animate.set_opacity(opacidad))

        # Ejecutar todas las animaciones juntas
        self.play(*animaciones, run_time=2.5, rate_func=smooth)


# Para renderizar:
# manim -pql GravityeCEL-v2.0.1.py OceanoeCEL
