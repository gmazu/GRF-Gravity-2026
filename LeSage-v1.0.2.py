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
    LeSage v1.0.2 - Lluvia rotativa + isotrópica

    Izquierda: eCEL (océano estático + masa + halo)
    Derecha: Le Sage
    - Fase 1: Lluvia rota como aguja del reloj (360°)
    - Fase 2: Lluvia isotrópica desde todas direcciones
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

        # === FASE 1: Lluvia rotativa (vuelta completa 360°) ===
        texto_rotacion = Text(
            "Partículas desde cada dirección...",
            font_size=16,
            color=YELLOW
        ).to_edge(DOWN)
        self.play(FadeOut(texto_comparacion), Write(texto_rotacion))

        self.lluvia_rotacion(duracion_vuelta=8)  # 8 segundos para dar la vuelta

        # === FASE 2: Lluvia isotrópica ===
        texto_isotropico = Text(
            "Lluvia isotrópica: desde TODAS las direcciones",
            font_size=16,
            color=GREEN
        ).to_edge(DOWN)
        self.play(FadeOut(texto_rotacion), Write(texto_isotropico))

        self.lluvia_isotropica(duracion=5)  # 5 segundos isotrópico

        self.wait(1)

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

    def lluvia_rotacion(self, duracion_vuelta=8):
        """
        Lluvia que rota como aguja del reloj.
        Da una vuelta completa de 360°.
        """
        # Centro del lado derecho (donde está la masa)
        centro_x = 3.5
        centro_y = 0
        radio_spawn = 4  # Distancia desde donde aparecen las partículas

        # Número de pasos para la vuelta completa
        num_pasos = 24  # 24 direcciones (cada 15°)
        tiempo_por_paso = duracion_vuelta / num_pasos

        for paso in range(num_pasos):
            # Ángulo actual (en sentido horario, empezando desde arriba-derecha)
            # 0° = arriba, 90° = derecha, 180° = abajo, 270° = izquierda
            angulo_origen = -np.pi/4 + (paso / num_pasos) * 2 * np.pi  # Empieza arriba-derecha

            # Dirección de las partículas (hacia el centro)
            dir_x = -np.cos(angulo_origen)
            dir_y = -np.sin(angulo_origen)

            particulas = []
            animaciones = []

            # 4-6 partículas por paso
            num_particulas = np.random.randint(4, 7)

            for i in range(num_particulas):
                # Posición inicial en el borde, con variación
                variacion_angulo = np.random.uniform(-0.2, 0.2)
                ang = angulo_origen + variacion_angulo

                x_origen = centro_x + radio_spawn * np.cos(ang)
                y_origen = centro_y + radio_spawn * np.sin(ang)

                # Limitar al área visible del lado derecho
                x_origen = max(0.5, min(7.5, x_origen))
                y_origen = max(-4, min(4, y_origen))

                # Profundidad
                profundidad = np.random.uniform(0, 1)
                largo_linea = 0.1 + profundidad * 0.25
                grosor = 1 + profundidad * 3
                opacidad = 0.3 + profundidad * 0.5

                # Crear línea
                x_fin = x_origen + dir_x * largo_linea
                y_fin = y_origen + dir_y * largo_linea

                particula = Line(
                    start=np.array([x_origen, y_origen, 0]),
                    end=np.array([x_fin, y_fin, 0]),
                    color=YELLOW,
                    stroke_width=grosor,
                    stroke_opacity=opacidad
                )

                # Calcular desplazamiento (hasta salir del lado derecho o llegar al borde)
                desplazamiento = 8
                velocidad = 5 + profundidad * 5
                tiempo = min(desplazamiento / velocidad, 1.2)
                desplazamiento_real = velocidad * tiempo

                animaciones.append(
                    Succession(
                        particula.animate(run_time=tiempo, rate_func=linear).shift(
                            np.array([dir_x * desplazamiento_real, dir_y * desplazamiento_real, 0])
                        ),
                        FadeOut(particula, run_time=0.05)
                    )
                )
                particulas.append(particula)

            self.add(*particulas)
            self.play(*animaciones, run_time=tiempo_por_paso)

    def lluvia_isotropica(self, duracion=5):
        """
        Lluvia desde TODAS las direcciones a la vez.
        Efecto isotrópico completo.
        """
        centro_x = 3.5
        centro_y = 0
        radio_spawn = 4

        intervalo = 0.3  # Cada 0.3 segundos una oleada
        num_oleadas = int(duracion / intervalo)

        for oleada in range(num_oleadas):
            particulas = []
            animaciones = []

            # 12-18 partículas por oleada (desde todas direcciones)
            num_particulas = np.random.randint(12, 19)

            for i in range(num_particulas):
                # Ángulo aleatorio (cualquier dirección)
                angulo_origen = np.random.uniform(0, 2 * np.pi)

                # Dirección hacia el centro
                dir_x = -np.cos(angulo_origen)
                dir_y = -np.sin(angulo_origen)

                # Posición inicial
                x_origen = centro_x + radio_spawn * np.cos(angulo_origen)
                y_origen = centro_y + radio_spawn * np.sin(angulo_origen)

                # Limitar al área visible
                x_origen = max(0.5, min(7.5, x_origen))
                y_origen = max(-4, min(4, y_origen))

                # Profundidad
                profundidad = np.random.uniform(0, 1)
                largo_linea = 0.1 + profundidad * 0.25
                grosor = 1 + profundidad * 3
                opacidad = 0.3 + profundidad * 0.5

                # Crear línea
                x_fin = x_origen + dir_x * largo_linea
                y_fin = y_origen + dir_y * largo_linea

                particula = Line(
                    start=np.array([x_origen, y_origen, 0]),
                    end=np.array([x_fin, y_fin, 0]),
                    color=YELLOW,
                    stroke_width=grosor,
                    stroke_opacity=opacidad
                )

                # Desplazamiento
                desplazamiento = 8
                velocidad = 5 + profundidad * 5
                tiempo = min(desplazamiento / velocidad, 1.0)
                desplazamiento_real = velocidad * tiempo

                animaciones.append(
                    Succession(
                        particula.animate(run_time=tiempo, rate_func=linear).shift(
                            np.array([dir_x * desplazamiento_real, dir_y * desplazamiento_real, 0])
                        ),
                        FadeOut(particula, run_time=0.05)
                    )
                )
                particulas.append(particula)

            self.add(*particulas)
            self.play(*animaciones, run_time=intervalo)


# Para renderizar:
# manim -pql LeSage-v1.0.2.py LeSageComparacion
