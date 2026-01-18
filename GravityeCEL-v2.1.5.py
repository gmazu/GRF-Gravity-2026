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


class TierraLuna(Scene):
    """
    v2.1.5 - Tierra y Luna con halos eCEL

    - Tierra en LEFT * 3.5 (misma posición que LeSage)
    - Luna en RIGHT * 3.5 (misma posición que LeSage)
    - Ambos con halo eCEL independiente
    - Probando si los halos se tocan a esta distancia
    """

    def construct(self):
        # Datos Tierra (desde config)
        nombre_tierra = CONFIG['masa_actual']['nombre']
        densidad_tierra = CONFIG['masa_actual']['densidad']
        radio_tierra = CONFIG['masa_actual']['radio_visual']
        color_tierra = CONFIG['masa_actual']['color']

        # Datos Luna (hardcoded por ahora)
        nombre_luna = "Luna"
        densidad_luna = 3.34  # g/cm³
        radio_luna = 0.27 * radio_tierra  # Luna es ~27% del radio de Tierra
        color_luna = "#c0c0c0"  # Gris plateado

        # Posiciones (mismas que LeSage)
        POS_TIERRA = LEFT * 3.5
        POS_LUNA = RIGHT * 3.5

        # Título
        title = Text("Tierra y Luna - Halos eCEL", font_size=40)
        subtitle = Text(
            "¿Se tocan los halos a esta distancia?",
            font_size=20
        )
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

        # 1. Crear océano eCEL de fondo
        oceano_fondo = self.crear_oceano_fondo()

        texto_oceano = Text(
            "Océano eCEL uniforme",
            font_size=22,
            color=BLUE_A
        ).to_edge(UP)

        self.play(
            FadeIn(oceano_fondo),
            Write(texto_oceano),
            run_time=CONFIG['animacion']['duracion_oceano']
        )
        self.wait(1)

        # 2. Crear Tierra
        tierra = Circle(
            radius=radio_tierra,
            color=color_tierra,
            fill_opacity=0.9,
            stroke_width=3
        )
        tierra.move_to(POS_TIERRA)
        label_tierra = Text(nombre_tierra, font_size=14, color=WHITE).move_to(tierra)

        texto_tierra = Text(
            f"Introduciendo {nombre_tierra}...",
            font_size=20,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(texto_tierra))
        self.play(
            GrowFromCenter(tierra),
            Write(label_tierra),
            run_time=1
        )

        # Halo Tierra
        halo_tierra = self.crear_ecel_cascada_suave(
            POS_TIERRA, densidad_tierra, radio_tierra
        )
        self.play(FadeIn(halo_tierra), run_time=1.5)

        # 3. Crear Luna
        luna = Circle(
            radius=radio_luna,
            color=color_luna,
            fill_opacity=0.9,
            stroke_width=2
        )
        luna.move_to(POS_LUNA)
        label_luna = Text(nombre_luna, font_size=12, color=WHITE).move_to(luna)

        texto_luna = Text(
            f"Introduciendo {nombre_luna}...",
            font_size=20,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(FadeOut(texto_tierra), Write(texto_luna))
        self.play(
            GrowFromCenter(luna),
            Write(label_luna),
            run_time=1
        )

        # Halo Luna
        halo_luna = self.crear_ecel_cascada_suave(
            POS_LUNA, densidad_luna, radio_luna
        )
        self.play(FadeIn(halo_luna), run_time=1.5)

        self.play(FadeOut(texto_luna))
        self.wait(1)

        # 4. Fade out océano
        texto_halos = Text(
            "Halos eCEL independientes",
            font_size=20,
            color=GREEN
        ).to_edge(DOWN)

        self.play(
            FadeOut(oceano_fondo),
            FadeOut(texto_oceano),
            Write(texto_halos),
            run_time=1.5
        )

        self.wait(3)

        # Fade out final
        self.play(
            FadeOut(tierra), FadeOut(luna),
            FadeOut(label_tierra), FadeOut(label_luna),
            FadeOut(halo_tierra), FadeOut(halo_luna),
            FadeOut(texto_halos)
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
        """Crea halo con difuminación suave."""
        ecel = VGroup()

        if isinstance(centro, np.ndarray):
            centro_arr = centro
        else:
            centro_arr = np.array([centro[0], centro[1], 0])

        factor = calcular_factor_desplazamiento(densidad)
        opacidad_max = CONFIG['intensidad']['opacidad_acumulacion']
        radio_particula = CONFIG['malla']['radio_base']
        distancia_minima = radio_particula * 2.5

        num_capas = 65
        espaciado_base = distancia_minima * 1.2

        for capa in range(num_capas):
            r = radio_masa + 0.05 + capa * espaciado_base

            factor_r2 = (radio_masa / r) ** 2
            factor_cascada = 1.0 + 0.3 * np.exp(-capa / 5)

            opacidad_capa = opacidad_max * factor_r2 * factor * factor_cascada
            opacidad_capa = min(opacidad_capa, opacidad_max)

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


# Para renderizar:
# manim -pql GravityeCEL-v2.1.5.py TierraLuna
