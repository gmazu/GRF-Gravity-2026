from manim import *
import numpy as np

class OceanGravity(Scene):
    def construct(self):
        # Título
        title = Text("Gravedad como Océano eCEL", font_size=48)
        subtitle = Text("Densidad de campo eCEL ~ 1/r²", font_size=24)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Crear océano de fondo disperso (lejos de materia)
        background_ocean = self.create_background_ocean()
        self.play(FadeIn(background_ocean), run_time=1)

        # Crear dos planetas
        planet1 = Circle(radius=0.3, color=BLUE, fill_opacity=0.9)
        planet1.move_to(LEFT * 3)
        planet1_label = Text("M₁", font_size=20).next_to(planet1, UP, buff=0.1)

        planet2 = Circle(radius=0.3, color=RED, fill_opacity=0.9)
        planet2.move_to(RIGHT * 3)
        planet2_label = Text("M₂", font_size=20).next_to(planet2, UP, buff=0.1)

        self.play(
            FadeIn(planet1),
            FadeIn(planet2),
            Write(planet1_label),
            Write(planet2_label)
        )
        self.wait(1)

        # Mostrar campo eCEL denso alrededor de cada planeta (1/r²)
        field1 = self.create_ecel_field(planet1.get_center(), color=BLUE_B)
        field2 = self.create_ecel_field(planet2.get_center(), color=RED_B)

        self.play(
            FadeIn(field1, scale=0.5),
            FadeIn(field2, scale=0.5),
            run_time=2
        )
        self.wait(1)

        # Texto explicativo - más eCEL cerca
        explanation1 = Text(
            "Mayor densidad eCEL cerca de la materia",
            font_size=24,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(explanation1))
        self.wait(2)
        self.play(FadeOut(explanation1))

        # Mostrar gradiente de presión entre planetas
        gradient_zone = self.create_pressure_gradient(
            planet1.get_center(),
            planet2.get_center()
        )

        self.play(FadeIn(gradient_zone), run_time=2)

        # Texto - zona de menor densidad entre planetas
        explanation2 = Text(
            "Zona de menor densidad eCEL entre masas\n→ Presión externa mayor → Empuje hacia adentro",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(explanation2))
        self.wait(2)

        # Planetas se acercan (empujados por océano externo)
        self.play(
            planet1.animate.shift(RIGHT * 1.5),
            planet2.animate.shift(LEFT * 1.5),
            planet1_label.animate.shift(RIGHT * 1.5),
            planet2_label.animate.shift(LEFT * 1.5),
            field1.animate.shift(RIGHT * 1.5),
            field2.animate.shift(LEFT * 1.5),
            run_time=3,
            rate_func=smooth
        )
        self.wait(2)

    def create_background_ocean(self):
        """Crea océano de fondo disperso (eCEL lejos de materia)"""
        dots = VGroup()

        # Puntos dispersos representando océano eCEL de fondo
        np.random.seed(42)
        for _ in range(200):
            x = np.random.uniform(-7, 7)
            y = np.random.uniform(-4, 4)

            dot = Dot(
                point=np.array([x, y, 0]),
                radius=0.02,
                color=BLUE_E,
                fill_opacity=0.3
            )
            dots.add(dot)

        return dots

    def create_ecel_field(self, center, color=BLUE_B, max_radius=2.5):
        """
        Crea campo eCEL denso que se disipa con 1/r²
        Más partículas cerca del centro, menos lejos
        """
        field = VGroup()

        # Múltiples capas concéntricas con densidad 1/r²
        num_layers = 15

        for i in range(1, num_layers + 1):
            r = 0.35 + (i * max_radius / num_layers)

            # Densidad proporcional a 1/r²
            density = 1.0 / (r ** 2)
            num_points = int(50 * density) + 3

            # Opacidad también disminuye con distancia
            opacity = min(0.8, 1.5 / (r ** 1.5))

            for j in range(num_points):
                angle = (2 * PI * j / num_points) + (i * 0.1)  # Offset para no alinear

                # Añadir variación radial
                r_var = r + np.random.uniform(-0.1, 0.1)

                x = center[0] + r_var * np.cos(angle)
                y = center[1] + r_var * np.sin(angle)

                # Tamaño de punto disminuye con distancia
                dot_size = max(0.015, 0.06 / (r ** 0.8))

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=dot_size,
                    color=color,
                    fill_opacity=opacity
                )
                field.add(dot)

        return field

    def create_pressure_gradient(self, c1, c2):
        """
        Muestra zona de menor densidad eCEL entre los dos planetas
        (el océano se "sombrea" mutuamente)
        """
        gradient = VGroup()

        # Línea entre centros
        mid_point = (c1 + c2) / 2

        # Zona de baja densidad (menos puntos, más transparentes)
        # Rectángulo vertical en el medio
        for i in range(20):
            # Posición entre los planetas
            t = np.random.uniform(0.3, 0.7)
            x = c1[0] + t * (c2[0] - c1[0])
            y = np.random.uniform(-1.5, 1.5)

            dot = Dot(
                point=np.array([x, y, 0]),
                radius=0.03,
                color=PURPLE_A,
                fill_opacity=0.15
            )
            gradient.add(dot)

        # Indicador visual de "zona de sombra"
        shadow_zone = Rectangle(
            width=2,
            height=3,
            color=PURPLE,
            fill_opacity=0.05,
            stroke_width=1,
            stroke_opacity=0.3
        ).move_to(mid_point)

        gradient.add(shadow_zone)

        return gradient


# Para renderizar:
# manim -pql GravityeCEL-v1.0.0.py OceanGravity
