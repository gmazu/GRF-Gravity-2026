from manim import *
import numpy as np
import matplotlib.pyplot as plt
from noise import pnoise2

class TestHeatmap(Scene):
    """
    Test rápido: 3 técnicas de heatmap
    1. Perlin Noise (puntos)
    2. Matplotlib (imagen)
    3. Gradiente radial (círculos)
    """

    def construct(self):
        titulo = Text("Comparación Heatmap", font_size=30)
        self.play(Write(titulo))
        self.wait(0.5)
        self.play(FadeOut(titulo))

        # === TÉCNICA 1: PERLIN NOISE ===
        t1 = Text("1. Perlin Noise", font_size=24).to_edge(UP)
        self.play(Write(t1))

        planeta1 = self.crear_perlin(LEFT * 4)
        self.play(FadeIn(planeta1))
        self.wait(1)

        # === TÉCNICA 2: MATPLOTLIB ===
        t2 = Text("2. Matplotlib - Colores NASA", font_size=24).to_edge(UP)
        self.play(ReplacementTransform(t1, t2))

        # Generar imagen matplotlib
        self.generar_heatmap_matplotlib()
        planeta2 = ImageMobject("temp_heatmap.png").scale(1.5)  # MÁS GRANDE
        planeta2.move_to(ORIGIN)

        # Borde
        circulo_clip = Circle(radius=2.2, color=WHITE, stroke_width=2)
        circulo_clip.move_to(ORIGIN)

        self.play(FadeIn(planeta2), Create(circulo_clip))
        self.wait(2)

        # === TÉCNICA 3: GRADIENTE RADIAL ===
        t3 = Text("3. Gradiente Radial", font_size=24).to_edge(UP)
        self.play(ReplacementTransform(t2, t3))

        planeta3 = self.crear_gradiente_radial(RIGHT * 4)
        self.play(FadeIn(planeta3))
        self.wait(1)

        # Mostrar los 3 juntos
        t_final = Text("Comparación", font_size=24).to_edge(UP)
        self.play(
            ReplacementTransform(t3, t_final),
            planeta1.animate.move_to(LEFT * 4),
            planeta2.animate.move_to(ORIGIN),
            circulo_clip.animate.move_to(ORIGIN),
            planeta3.animate.move_to(RIGHT * 4)
        )

        labels = VGroup(
            Text("Perlin", font_size=16).move_to(LEFT * 4 + DOWN * 2),
            Text("Matplotlib", font_size=16).move_to(DOWN * 2),
            Text("Radial", font_size=16).move_to(RIGHT * 4 + DOWN * 2)
        )
        self.play(Write(labels))
        self.wait(2)

    def crear_perlin(self, pos):
        """Técnica 1: Perlin Noise con puntos"""
        puntos = VGroup()
        radio = 1.2
        espaciado = 0.08
        colores = [PURPLE_E, BLUE, BLUE_A, YELLOW, ORANGE, RED]

        for x in np.arange(-radio, radio, espaciado):
            for y in np.arange(-radio, radio, espaciado):
                if x**2 + y**2 <= radio**2:
                    val = (pnoise2(x * 3, y * 3, octaves=4) + 1) / 2
                    idx = int(val * (len(colores) - 1))
                    color = colores[min(idx, len(colores) - 1)]

                    punto = Dot(
                        point=pos + np.array([x, y, 0]),
                        radius=espaciado * 0.5,
                        color=color
                    )
                    puntos.add(punto)

        borde = Circle(radius=radio, stroke_width=2, color=WHITE)
        borde.move_to(pos)
        return VGroup(puntos, borde)

    def generar_heatmap_matplotlib(self):
        """Técnica 2: Generar heatmap con matplotlib - colores NASA/AIRS"""
        from matplotlib.colors import LinearSegmentedColormap

        size = 400  # Mayor resolución
        x = np.linspace(-2, 2, size)
        y = np.linspace(-2, 2, size)
        X, Y = np.meshgrid(x, y)

        # Patrón tipo atmosférico
        Z = np.sin(X * 2.5) * np.cos(Y * 2.5) + np.sin(X * 4 + Y * 2) * 0.4
        Z += np.cos(X * 1.5 - Y * 3) * 0.3
        Z = (Z - Z.min()) / (Z.max() - Z.min())

        # Máscara circular
        mask = X**2 + Y**2 > 1.8**2
        Z[mask] = np.nan

        # Paleta NASA/AIRS: Púrpura → Azul → Cyan → Amarillo → Naranja → Rojo
        colors_nasa = [
            '#4B0082',  # Púrpura oscuro (frío)
            '#0000FF',  # Azul
            '#00BFFF',  # Cyan
            '#00FF00',  # Verde
            '#FFFF00',  # Amarillo
            '#FFA500',  # Naranja
            '#FF0000',  # Rojo (caliente)
        ]
        cmap_nasa = LinearSegmentedColormap.from_list('nasa_thermal', colors_nasa)

        fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
        ax.imshow(Z, cmap=cmap_nasa, extent=[-2, 2, -2, 2])
        ax.axis('off')
        ax.set_aspect('equal')
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        plt.savefig('temp_heatmap.png', bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close()

    def crear_gradiente_radial(self, pos):
        """Técnica 3: Círculos concéntricos con gradiente"""
        capas = VGroup()
        radio = 1.2
        num_capas = 15
        colores = [PURPLE_E, BLUE, BLUE_A, YELLOW, ORANGE, RED]

        for i in range(num_capas, 0, -1):
            r = radio * (i / num_capas)
            t = i / num_capas
            idx = int(t * (len(colores) - 1))
            color = colores[min(idx, len(colores) - 1)]

            circulo = Circle(
                radius=r,
                fill_opacity=0.8,
                fill_color=color,
                stroke_width=0
            )
            circulo.move_to(pos)
            capas.add(circulo)

        borde = Circle(radius=radio, stroke_width=2, color=WHITE)
        borde.move_to(pos)
        return VGroup(capas, borde)


# manim -pql test_heatmap.py TestHeatmap
