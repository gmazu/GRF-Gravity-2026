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


class LeSageComparacion(Scene):
    """
    LeSage v1.0.0 - Pantalla dividida

    Izquierda: eCEL (océano estático + masa + halo)
    Derecha: Le Sage (solo masa, fondo negro, preparado para lluvia)
    """

    def construct(self):
        nombre = CONFIG['masa_actual']['nombre']
        densidad = CONFIG['masa_actual']['densidad']
        radio_visual = CONFIG['masa_actual']['radio_visual']
        color_masa = CONFIG['masa_actual']['color']

        # Posiciones para pantalla dividida
        POS_IZQUIERDA = LEFT * 3.5
        POS_DERECHA = RIGHT * 3.5

        # Título
        title = Text("eCEL vs Le Sage", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Línea divisoria vertical
        linea = Line(UP * 4, DOWN * 4, color=WHITE, stroke_width=1, stroke_opacity=0.3)
        self.add(linea)

        # Labels para cada lado
        label_ecel = Text("eCEL", font_size=24, color=BLUE_A).to_edge(UP).shift(LEFT * 3.5)
        label_lesage = Text("Le Sage", font_size=24, color=YELLOW).to_edge(UP).shift(RIGHT * 3.5)

        self.play(Write(label_ecel), Write(label_lesage))

        # === LADO IZQUIERDO: eCEL ===
        # Océano de fondo (solo lado izquierdo)
        oceano_izq = self.crear_oceano_fondo(POS_IZQUIERDA)
        self.play(FadeIn(oceano_izq), run_time=1)

        # Masa izquierda
        masa_izq = Circle(
            radius=radio_visual,
            color=color_masa,
            fill_opacity=0.9,
            stroke_width=3
        )
        masa_izq.move_to(POS_IZQUIERDA)
        label_tierra_izq = Text(nombre, font_size=14, color=WHITE).move_to(masa_izq)

        # Halo eCEL
        halo_izq = self.crear_ecel_cascada_suave(POS_IZQUIERDA, densidad, radio_visual)

        self.play(
            GrowFromCenter(masa_izq),
            Write(label_tierra_izq),
            run_time=1
        )
        self.play(FadeIn(halo_izq), run_time=1.5)

        # === LADO DERECHO: Le Sage (solo planeta, fondo negro) ===
        masa_der = Circle(
            radius=radio_visual,
            color=color_masa,
            fill_opacity=0.9,
            stroke_width=3
        )
        masa_der.move_to(POS_DERECHA)
        label_tierra_der = Text(nombre, font_size=14, color=WHITE).move_to(masa_der)

        self.play(
            GrowFromCenter(masa_der),
            Write(label_tierra_der),
            run_time=1
        )

        # Texto explicativo
        texto_comparacion = Text(
            "Izquierda: océano estático  |  Derecha: lluvia de partículas",
            font_size=16,
            color=GRAY
        ).to_edge(DOWN)

        self.play(Write(texto_comparacion))
        self.wait(1)

        # === LLUVIA LE SAGE en lado derecho ===
        # Varias rondas de lluvia
        for ronda in range(3):
            self.lluvia_lesage(POS_DERECHA, radio_visual, num_particulas=30, prob_absorcion=0.15)
            self.wait(0.5)

        self.wait(1)

        # Fade out del océano izquierdo para dejar solo el halo
        self.play(FadeOut(oceano_izq), run_time=1)

        # Texto final
        texto_final = Text(
            "eCEL: océano estático con halo  |  Le Sage: lluvia continua",
            font_size=16,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(FadeOut(texto_comparacion), Write(texto_final))

        # Más lluvia para mostrar el efecto continuo
        for ronda in range(2):
            self.lluvia_lesage(POS_DERECHA, radio_visual, num_particulas=30, prob_absorcion=0.15)
            self.wait(0.3)

        self.wait(2)

    def crear_oceano_fondo(self, centro):
        """Océano eCEL de fondo uniforme (solo mitad izquierda)."""
        oceano = VGroup()

        espaciado = CONFIG['malla']['espaciado']
        radio = CONFIG['malla']['radio_base'] * 0.6
        opacidad = CONFIG['intensidad']['opacidad_minima']
        color = CONFIG['malla']['color_fondo']

        # Solo lado izquierdo (x de -7 a 0)
        for x in np.arange(-7, 0, espaciado):
            for y in np.arange(-4, 4, espaciado):
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

        num_capas = 40  # Menos capas porque es más pequeño
        espaciado_base = distancia_minima * 1.2

        for capa in range(num_capas):
            r = radio_masa + 0.05 + capa * espaciado_base

            # Limitar el halo para que no cruce la línea divisoria
            if centro_arr[0] + r > -0.3:
                max_r = abs(-0.3 - centro_arr[0])
                if r > max_r:
                    continue

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

                # No dibujar si cruza la línea divisoria
                if x > -0.2:
                    continue

                radio_p = radio_particula * (0.8 + factor_r2 * 0.4)

                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=max(radio_p, radio_particula * 0.5),
                    color=color_capa,
                    fill_opacity=opacidad_capa
                )
                ecel.add(dot)

        return ecel

    def lluvia_lesage(self, centro_masa, radio_masa, num_particulas=30, prob_absorcion=0.15):
        """
        Lluvia diagonal estilo Le Sage (solo lado derecho).

        - Diagonal: arriba derecha → abajo izquierda
        - Líneas cortas (disparos), no puntos
        - Perspectiva: más cerca = más grande
        """
        particulas = []
        animaciones = []

        # Dirección diagonal (arriba derecha a abajo izquierda)
        dir_x = -1
        dir_y = -1
        norm = np.sqrt(dir_x**2 + dir_y**2)
        dir_x /= norm
        dir_y /= norm

        for i in range(num_particulas):
            # Posición inicial aleatoria en el borde superior derecho
            # x: de 0.5 a 7, y: de 2 a 4 (arriba)
            x_origen = np.random.uniform(2, 7)
            y_origen = np.random.uniform(2, 4.5)

            # "Profundidad" aleatoria (0 = lejos, 1 = cerca)
            profundidad = np.random.uniform(0, 1)

            # Tamaño según profundidad
            largo_linea = 0.1 + profundidad * 0.25  # 0.1 a 0.35
            grosor = 1 + profundidad * 3  # 1 a 4

            # Opacidad según profundidad
            opacidad = 0.3 + profundidad * 0.5  # 0.3 a 0.8

            # Crear línea corta (disparo)
            x_fin_linea = x_origen + dir_x * largo_linea
            y_fin_linea = y_origen + dir_y * largo_linea

            particula = Line(
                start=np.array([x_origen, y_origen, 0]),
                end=np.array([x_fin_linea, y_fin_linea, 0]),
                color=YELLOW,
                stroke_width=grosor,
                stroke_opacity=opacidad
            )

            # Destino (abajo izquierda, fuera de pantalla)
            desplazamiento = 8  # Distancia total a recorrer
            x_destino = x_origen + dir_x * desplazamiento
            y_destino = y_origen + dir_y * desplazamiento

            # Limitar al lado derecho
            if x_destino < 0.3:
                x_destino = 0.3

            # Velocidad según profundidad (más cerca = más rápido)
            velocidad = 4 + profundidad * 4  # 4 a 8
            distancia = np.sqrt((x_destino - x_origen)**2 + (y_destino - y_origen)**2)
            tiempo = distancia / velocidad

            animaciones.append(
                particula.animate(run_time=tiempo, rate_func=linear).shift(
                    np.array([dir_x * desplazamiento, dir_y * desplazamiento, 0])
                )
            )

            particulas.append(particula)

        # Agregar partículas y animar
        self.add(*particulas)
        self.play(*animaciones)

        # Limpiar
        for p in particulas:
            self.remove(p)


# Para renderizar:
# manim -pql LeSage-v1.0.0.py LeSageComparacion
