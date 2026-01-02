from manim import *
import numpy as np
import yaml
from pathlib import Path

# Cargar configuración desde YAML
config_path = Path(__file__).parent / "config_ecel.yaml"
with open(config_path, 'r') as f:
    CONFIG = yaml.safe_load(f)

class OceanGravity(Scene):
    def construct(self):
        # Título
        title = Text("Gravedad como Océano eCEL", font_size=48)
        subtitle = Text("Densidad de campo eCEL ~ 1/r²", font_size=24)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Crear malla COMPLETA de eCEL (cubre todo el espacio)
        ecel_field = self.create_full_ecel_mesh()
        self.play(FadeIn(ecel_field), run_time=1)

        # Crear dos núcleos (planetas)
        radio_nucleo = CONFIG['nucleos']['radio']

        planet1 = Circle(radius=radio_nucleo, color=BLUE, fill_opacity=0.9)
        planet1.move_to(LEFT * 3)
        planet1_label = Text("M₁", font_size=20).next_to(planet1, UP, buff=0.1)

        planet2 = Circle(radius=radio_nucleo, color=RED, fill_opacity=0.9)
        planet2.move_to(RIGHT * 3)
        planet2_label = Text("M₂", font_size=20).next_to(planet2, UP, buff=0.1)

        self.play(
            FadeIn(planet1),
            FadeIn(planet2),
            Write(planet1_label),
            Write(planet2_label)
        )

        # Parámetros desde config
        multiplicador = CONFIG['intensidad']['multiplicador']
        opacidad_min = CONFIG['intensidad']['opacidad_minima']
        opacidad_max = CONFIG['intensidad']['opacidad_maxima']
        dist_minima = CONFIG['nucleos']['distancia_minima']

        # Updater: ilumina partículas según 1/r² a los núcleos
        def update_ecel_field(field):
            c1 = planet1.get_center()
            c2 = planet2.get_center()

            for dot in field:
                pos = dot.get_center()

                # Distancia a cada núcleo
                dist1 = np.linalg.norm(pos[:2] - c1[:2])
                dist2 = np.linalg.norm(pos[:2] - c2[:2])

                # Intensidad con 1/r² para cada núcleo
                intensity1 = 1.0 / (max(dist1, dist_minima) ** 2)
                intensity2 = 1.0 / (max(dist2, dist_minima) ** 2)

                # Opacidad proporcional a intensidad combinada
                total_intensity = intensity1 + intensity2
                opacity = min(opacidad_max, total_intensity * multiplicador)
                opacity = max(opacidad_min, opacity)

                dot.set_opacity(opacity)

                # Color según núcleo dominante
                if intensity1 > intensity2 * 1.5:
                    dot.set_color(BLUE_B)
                elif intensity2 > intensity1 * 1.5:
                    dot.set_color(RED_B)
                else:
                    dot.set_color(PURPLE_A)

        # Aplicar updater
        ecel_field.add_updater(update_ecel_field)
        update_ecel_field(ecel_field)  # Primera actualización

        self.wait(1)

        # Texto explicativo
        explanation1 = Text(
            "Mayor densidad eCEL cerca de la materia (1/r²)",
            font_size=24,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(explanation1))
        self.wait(2)
        self.play(FadeOut(explanation1))

        # Texto zona de sombra
        explanation2 = Text(
            "Zona de menor densidad eCEL entre masas\n→ Presión externa mayor → Empuje hacia adentro",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(explanation2))
        self.wait(1)

        # Parámetros de animación desde config
        duracion = CONFIG['animacion']['duracion_movimiento']
        desplazamiento = CONFIG['animacion']['desplazamiento']

        # SOLO los núcleos se mueven - el campo eCEL queda FIJO
        # Las partículas se iluminan según nueva posición
        self.play(
            planet1.animate.shift(RIGHT * desplazamiento),
            planet2.animate.shift(LEFT * desplazamiento),
            planet1_label.animate.shift(RIGHT * desplazamiento),
            planet2_label.animate.shift(LEFT * desplazamiento),
            run_time=duracion,
            rate_func=smooth
        )

        self.wait(1)

        # Texto final
        explanation3 = Text(
            "El océano eCEL permanece fijo\nLos núcleos iluminan nuevas zonas",
            font_size=22,
            color=GREEN
        ).to_edge(DOWN)

        self.play(FadeOut(explanation2), Write(explanation3))
        self.wait(2)

        ecel_field.clear_updaters()

    def create_full_ecel_mesh(self):
        """
        Crea malla COMPLETA de partículas eCEL cubriendo todo el espacio.
        La opacidad se controlará dinámicamente por los updaters.
        """
        field = VGroup()

        np.random.seed(42)

        espaciado = CONFIG['malla']['espaciado']
        radio = CONFIG['malla']['radio_particula']
        variacion = CONFIG['malla']['variacion']

        # Malla densa cubriendo toda la pantalla
        for x in np.arange(-7, 7, espaciado):
            for y in np.arange(-4, 4, espaciado):
                # Pequeña variación para no verse como grid perfecto
                x_var = x + np.random.uniform(-variacion, variacion)
                y_var = y + np.random.uniform(-variacion, variacion)

                dot = Dot(
                    point=np.array([x_var, y_var, 0]),
                    radius=radio,
                    color=BLUE_E,
                    fill_opacity=0.02  # Opacidad inicial baja
                )
                field.add(dot)

        return field


# Para renderizar:
# manim -pql GravityeCEL-v1.0.3.py OceanGravity
