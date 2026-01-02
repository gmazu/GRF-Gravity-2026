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

        # Crear dos planetas (núcleos)
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

        # Crear campo eCEL FIJO (no se mueve, cubre ambas zonas)
        field1 = self.create_ecel_field(LEFT * 3, color=BLUE_B)
        field2 = self.create_ecel_field(RIGHT * 3, color=RED_B)

        # Guardar opacidades originales
        field1_opacities = [dot.get_fill_opacity() for dot in field1]
        field2_opacities = [dot.get_fill_opacity() for dot in field2]

        self.play(
            FadeIn(field1, scale=0.5),
            FadeIn(field2, scale=0.5),
            run_time=2
        )
        self.wait(1)

        # Texto explicativo
        explanation1 = Text(
            "Mayor densidad eCEL cerca de la materia",
            font_size=24,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(explanation1))
        self.wait(2)
        self.play(FadeOut(explanation1))

        # Updater: ilumina MÁS las partículas cercanas al núcleo (no reduce)
        def update_field1(field):
            center = planet1.get_center()
            for i, dot in enumerate(field):
                pos = dot.get_center()
                dist = np.linalg.norm(pos[:2] - center[:2])
                base_opacity = field1_opacities[i]

                # Boost de brillo si está cerca del núcleo
                if dist < 1.5:
                    boost = 1.5 / (max(dist, 0.3) ** 0.5)
                    new_opacity = min(1.0, base_opacity * boost)
                else:
                    new_opacity = base_opacity * 0.7

                dot.set_opacity(new_opacity)

        def update_field2(field):
            center = planet2.get_center()
            for i, dot in enumerate(field):
                pos = dot.get_center()
                dist = np.linalg.norm(pos[:2] - center[:2])
                base_opacity = field2_opacities[i]

                if dist < 1.5:
                    boost = 1.5 / (max(dist, 0.3) ** 0.5)
                    new_opacity = min(1.0, base_opacity * boost)
                else:
                    new_opacity = base_opacity * 0.7

                dot.set_opacity(new_opacity)

        # Aplicar updaters
        field1.add_updater(update_field1)
        field2.add_updater(update_field2)

        # Texto
        explanation2 = Text(
            "Zona de menor densidad eCEL entre masas\n→ Presión externa mayor → Empuje hacia adentro",
            font_size=22,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(explanation2))
        self.wait(1)

        # SOLO los núcleos se mueven - el campo eCEL queda FIJO
        self.play(
            planet1.animate.shift(RIGHT * 1.5),
            planet2.animate.shift(LEFT * 1.5),
            planet1_label.animate.shift(RIGHT * 1.5),
            planet2_label.animate.shift(LEFT * 1.5),
            run_time=4,
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

        field1.clear_updaters()
        field2.clear_updaters()

    def create_background_ocean(self):
        """Crea océano de fondo disperso (eCEL lejos de materia)"""
        dots = VGroup()

        np.random.seed(42)
        for _ in range(300):
            x = np.random.uniform(-7, 7)
            y = np.random.uniform(-4, 4)

            dot = Dot(
                point=np.array([x, y, 0]),
                radius=0.008,
                color=BLUE_E,
                fill_opacity=0.25
            )
            dots.add(dot)

        return dots

    def create_ecel_field(self, center, color=BLUE_B, max_radius=2.5):
        """
        Crea campo eCEL denso que se disipa con 1/r²
        IGUAL que v1.0.1 - campo visible
        """
        field = VGroup()

        num_layers = 18

        for i in range(1, num_layers + 1):
            r = 0.35 + (i * max_radius / num_layers)

            density = 1.0 / (r ** 2)
            num_points = int(60 * density) + 4

            opacity = min(0.7, 1.2 / (r ** 1.5))

            for j in range(num_points):
                angle = (2 * PI * j / num_points) + (i * 0.1)

                r_var = r + np.random.uniform(-0.08, 0.08)

                x = center[0] + r_var * np.cos(angle)
                y = center[1] + r_var * np.sin(angle)

                dot_size = max(0.006, 0.025 / (r ** 0.8))

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=dot_size,
                    color=color,
                    fill_opacity=opacity
                )
                field.add(dot)

        return field


# Para renderizar:
# manim -pql GravityeCEL-v1.0.2.py OceanGravity
