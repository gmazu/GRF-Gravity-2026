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
        subtitle = Text("v1.0.4 - Campo Uniforme", font_size=24)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Crear malla UNIFORME de eCEL
        ecel_field = self.create_full_ecel_mesh()
        self.play(FadeIn(ecel_field), run_time=1)

        # Texto temporal para indicar el estado actual
        info_text = Text("Estado inicial: Océano eCEL en reposo", font_size=24).to_edge(DOWN)
        self.play(Write(info_text))

        # Dejamos el campo en pantalla para revisión
        self.wait(5)
        
        self.play(FadeOut(info_text))
        ecel_field.clear_updaters()

    def create_full_ecel_mesh(self):
        """
        Crea malla UNIFORME de partículas eCEL con efecto viñeta.
        """
        field = VGroup()

        np.random.seed(42)

        # Parámetros de la malla desde config
        espaciado = CONFIG['malla']['espaciado']
        radio_base = CONFIG['malla']['radio_base']
        variacion = CONFIG['malla']['variacion']
        opacidad_inicial = CONFIG['malla']['opacidad_inicial']
        fuerza_vineta = CONFIG['malla'].get('fuerza_vineta', 0.0) # Usar .get para compatibilidad

        # Dimensiones aproximadas de la pantalla para normalizar la distancia
        max_dist = np.linalg.norm([7, 4]) 

        # Malla densa cubriendo toda la pantalla
        for x in np.arange(-7, 7, espaciado):
            for y in np.arange(-4, 4, espaciado):
                # Pequeña variación para no verse como grid perfecto
                x_var = x + np.random.uniform(-variacion, variacion)
                y_var = y + np.random.uniform(-variacion, variacion)
                pos = np.array([x_var, y_var, 0])

                # Cálculo del efecto viñeta
                dist_centro = np.linalg.norm(pos)
                
                # El factor de la viñeta va de 1 (centro) a (1 - fuerza) en los bordes
                vignette_multiplier = np.clip(1 - fuerza_vineta * (dist_centro / max_dist), 0, 1)
                final_opacity = opacidad_inicial * vignette_multiplier

                dot = Dot(
                    point=pos,
                    radius=radio_base,
                    color=BLUE_E,
                    fill_opacity=final_opacity
                )
                # Guardamos la posición original para futuros cálculos de desplazamiento
                dot.original_center = pos
                field.add(dot)

        return field


# Para renderizar:
# manim -pql GravityeCEL-v1.0.4.py OceanGravity
