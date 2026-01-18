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
    LeSage v1.0.1 - Pantalla dividida con lluvia continua

    Izquierda: eCEL (océano estático + masa + halo)
    Derecha: Le Sage (lluvia continua 10 segundos)
    - Partículas desaparecen antes de cruzar al lado izquierdo
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

        # Fade out del océano izquierdo para dejar solo el halo
        self.play(FadeOut(oceano_izq), run_time=1)

        # === LLUVIA CONTINUA LE SAGE - 10 segundos ===
        self.lluvia_continua(duracion=10, particulas_por_segundo=15)

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

    def lluvia_continua(self, duracion=10, particulas_por_segundo=15):
        """
        Lluvia continua estilo Le Sage.

        - Duración: tiempo total en segundos
        - Partículas aparecen constantemente
        - Desaparecen antes de cruzar x=0.3
        """
        # Dirección diagonal (arriba derecha a abajo izquierda)
        dir_x = -1
        dir_y = -1
        norm = np.sqrt(dir_x**2 + dir_y**2)
        dir_x /= norm
        dir_y /= norm

        # Generar oleadas de partículas
        intervalo = 1.0 / particulas_por_segundo * 5  # Cada cuánto lanzar un grupo
        num_oleadas = int(duracion / intervalo)

        for oleada in range(num_oleadas):
            particulas = []
            animaciones = []

            # 5-8 partículas por oleada
            num_particulas = np.random.randint(5, 9)

            for i in range(num_particulas):
                # Posición inicial: borde superior derecho y lateral derecho
                if np.random.random() < 0.7:
                    # Desde arriba
                    x_origen = np.random.uniform(1, 7.5)
                    y_origen = np.random.uniform(3.5, 5)
                else:
                    # Desde la derecha
                    x_origen = np.random.uniform(6.5, 8)
                    y_origen = np.random.uniform(-2, 4)

                # "Profundidad" aleatoria (0 = lejos, 1 = cerca)
                profundidad = np.random.uniform(0, 1)

                # Tamaño según profundidad
                largo_linea = 0.1 + profundidad * 0.25
                grosor = 1 + profundidad * 3

                # Opacidad según profundidad
                opacidad = 0.3 + profundidad * 0.5

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

                # Calcular hasta dónde puede llegar (antes de x=0.3)
                # Distancia máxima en x hasta la línea divisoria
                dist_max_x = x_origen - 0.5  # Margen de seguridad
                dist_max_diagonal = dist_max_x / abs(dir_x)

                # Velocidad según profundidad
                velocidad = 5 + profundidad * 5
                tiempo = dist_max_diagonal / velocidad
                tiempo = min(tiempo, 1.5)  # Máximo 1.5 segundos por partícula

                desplazamiento = velocidad * tiempo

                animaciones.append(
                    Succession(
                        particula.animate(run_time=tiempo, rate_func=linear).shift(
                            np.array([dir_x * desplazamiento, dir_y * desplazamiento, 0])
                        ),
                        FadeOut(particula, run_time=0.1)
                    )
                )

                particulas.append(particula)

            # Agregar y animar esta oleada
            self.add(*particulas)
            self.play(*animaciones, run_time=intervalo)


# Para renderizar:
# manim -pql LeSage-v1.0.1.py LeSageComparacion
