from manim import *
import numpy as np
import yaml
from pathlib import Path
from noise import pnoise2  # pip install noise

# Cargar configuración desde YAML
config_path = Path(__file__).parent / "config_ecel.yaml"
with open(config_path, 'r') as f:
    CONFIG = yaml.safe_load(f)

# Cargar configuración Le Sage
lesage_path = Path(__file__).parent / "config_lesage.yaml"
with open(lesage_path, 'r') as f:
    LESAGE = yaml.safe_load(f)


class LeSageComparacion(Scene):
    """
    LeSage v1.2.2 - Planeta calentado por impactos

    - Más puntos para mejor patrón visible
    - Planeta se calienta DONDE las partículas impactan
    - Calor se propaga desde puntos de impacto
    """

    def noise_a_color(self, valor):
        """Convierte valor 0-1 a color térmico."""
        # Paleta: Púrpura → Azul → Cyan → Amarillo → Naranja → Rojo
        colores = [PURPLE_E, BLUE, BLUE_A, YELLOW, ORANGE, RED]
        valor = max(0, min(1, valor))  # Clamp 0-1

        pos = valor * (len(colores) - 1)
        idx1 = int(pos)
        idx2 = min(idx1 + 1, len(colores) - 1)
        t = pos - idx1

        return interpolate_color(colores[idx1], colores[idx2], t)

    def construct(self):
        nombre = CONFIG['masa_actual']['nombre']
        radio_visual = CONFIG['masa_actual']['radio_visual']

        CENTRO = ORIGIN

        # Título
        title = Text("Le Sage: Acumulación de Materia", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Crear planeta con PERLIN NOISE heatmap
        # Paleta térmica: Púrpura → Azul → Cyan → Amarillo → Naranja → Rojo
        self.colores_termicos = [PURPLE_E, BLUE, BLUE_A, YELLOW, ORANGE, RED]

        # Crear puntos en el planeta con colores basados en Perlin noise
        self.puntos_planeta = VGroup()
        self.datos_puntos = []  # Guardar posición y valor noise para actualizar

        # Parámetros del noise
        noise_scale = 4.0
        noise_octaves = 4

        # Crear grid de puntos dentro del círculo - MÁS DENSO
        espaciado = 0.05  # Más puntos para mejor patrón
        for x in np.arange(-radio_visual, radio_visual + espaciado, espaciado):
            for y in np.arange(-radio_visual, radio_visual + espaciado, espaciado):
                # Solo puntos dentro del círculo
                dist = np.sqrt(x**2 + y**2)
                if dist <= radio_visual * 0.98:
                    # Valor de Perlin noise (0 a 1)
                    noise_val = (pnoise2(x * noise_scale, y * noise_scale,
                                        octaves=noise_octaves) + 1) / 2

                    # Mapear a color (inicio frío: valores bajos)
                    temp_inicial = noise_val * 0.35  # Empezar frío
                    color = self.noise_a_color(temp_inicial)

                    punto = Dot(
                        point=np.array([x + CENTRO[0], y + CENTRO[1], 0]),
                        radius=espaciado * 0.55,
                        color=color,
                        fill_opacity=0.95
                    )
                    self.puntos_planeta.add(punto)
                    self.datos_puntos.append({
                        'x': x, 'y': y,
                        'noise_base': noise_val,
                        'temperatura': temp_inicial,  # Temperatura actual
                        'punto': punto
                    })

        # Borde del planeta
        self.borde_planeta = Circle(
            radius=radio_visual,
            color=PURPLE_E,
            fill_opacity=0,
            stroke_width=2
        )
        self.borde_planeta.move_to(CENTRO)

        self.planeta = VGroup(self.puntos_planeta, self.borde_planeta)

        label_planeta = Text(nombre, font_size=14, color=WHITE).move_to(CENTRO)

        # Atmósfera (empieza invisible, terminará ROJA brillante)
        self.atmosfera = Circle(
            radius=radio_visual * 1.3,
            color=RED,
            fill_opacity=0,
            stroke_width=0
        )
        self.atmosfera.move_to(CENTRO)
        self.add(self.atmosfera)

        self.play(GrowFromCenter(self.planeta), Write(label_planeta), run_time=1)

        # CONTADOR DE DENSIDAD (arriba derecha)
        self.densidad_actual = 1e10  # Empezamos en 10^10
        self.densidad_meta = 1e30   # Meta de Le Sage

        contador_label = Text("Densidad partículas/m³:", font_size=14, color=GRAY)
        contador_label.to_corner(UR).shift(DOWN * 0.5 + LEFT * 0.5)

        self.contador_valor = Text(
            f"10¹⁰",
            font_size=24,
            color=YELLOW
        )
        self.contador_valor.next_to(contador_label, DOWN)

        meta_label = Text("Meta Le Sage: 10³⁰", font_size=12, color=RED_A)
        meta_label.next_to(self.contador_valor, DOWN, buff=0.3)

        self.add(contador_label, self.contador_valor, meta_label)

        # Barra de progreso
        barra_fondo = Rectangle(
            width=2.5, height=0.2,
            color=GRAY, fill_opacity=0.3
        )
        barra_fondo.next_to(meta_label, DOWN, buff=0.2)

        self.barra_progreso = Rectangle(
            width=0.01, height=0.2,
            color=YELLOW, fill_opacity=0.8
        )
        self.barra_progreso.align_to(barra_fondo, LEFT)
        self.barra_progreso.move_to(barra_fondo.get_left(), aligned_edge=LEFT)

        self.add(barra_fondo, self.barra_progreso)

        # INDICADOR DE ESTADO (arriba izquierda)
        estado_label = Text("Estado:", font_size=14, color=GRAY)
        estado_label.to_corner(UL).shift(DOWN * 0.5 + RIGHT * 0.3)

        self.estado_titulo = Text("SÓLIDO", font_size=18, color=PURPLE)
        self.estado_titulo.next_to(estado_label, DOWN)

        self.estado_subtitulo = Text("Frío", font_size=9, color=BLUE)
        self.estado_subtitulo.next_to(self.estado_titulo, DOWN, buff=0.1)

        self.add(estado_label, self.estado_titulo, self.estado_subtitulo)

        # Texto explicativo
        texto_intro = Text(
            "Aumentando densidad de partículas...",
            font_size=16,
            color=YELLOW
        ).to_edge(DOWN)
        self.play(Write(texto_intro))

        # FASE PRINCIPAL: Calentamiento con contador
        self.calentamiento_con_contador(
            duracion=25,
            centro=CENTRO,
            label=label_planeta,
            barra_fondo=barra_fondo
        )

        # Final
        self.wait(2)

    def actualizar_contador(self, exponente):
        """Actualiza el texto del contador."""
        # Convertir exponente a superíndice
        superindices = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        exp_str = "".join(superindices[int(d)] for d in str(exponente))

        nuevo_texto = Text(f"10{exp_str}", font_size=24)

        # Color según peligro
        if exponente < 15:
            nuevo_texto.set_color(YELLOW)
        elif exponente < 20:
            nuevo_texto.set_color(ORANGE)
        elif exponente < 25:
            nuevo_texto.set_color(RED)
        else:
            nuevo_texto.set_color(WHITE)

        nuevo_texto.move_to(self.contador_valor)
        return nuevo_texto

    def calentamiento_con_contador(self, duracion=25, centro=ORIGIN, label=None, barra_fondo=None):
        """Calentamiento progresivo con lluvia CONTINUA usando updater."""
        centro_x = centro[0]
        centro_y = centro[1]
        radio_spawn = LESAGE['area']['radio_spawn']
        radio_planeta = CONFIG['masa_actual']['radio_visual']

        # Velocidad base MUY lenta para fluidez
        vel_base = 0.8

        # Paleta térmica NASA/AIRS para partículas (frío → caliente)
        colores_particula = [BLUE_A, YELLOW, YELLOW, ORANGE, ORANGE, RED]

        # Estado compartido para el updater
        estado = {
            'tiempo': 0,
            'ultimo_spawn': 0,
            'exponente': 10,
            'particulas': []
        }

        # Contenedor de partículas
        contenedor = VGroup()
        self.add(contenedor)

        def lluvia_updater(mob, dt):
            estado['tiempo'] += dt
            progreso = min(estado['tiempo'] / duracion, 1.0)

            # Exponente actual (10 → 30)
            estado['exponente'] = int(10 + progreso * 20)
            exponente = estado['exponente']

            # Spawn constante y rápido
            spawn_interval = 0.02  # Cada 20ms

            # Spawn nuevas partículas
            if estado['tiempo'] - estado['ultimo_spawn'] > spawn_interval:
                estado['ultimo_spawn'] = estado['tiempo']

                # DENSIDAD SIN MIEDO - tu PC aguanta
                densidad_mult = 1 + (exponente - 10) * 0.25
                num_nuevas = int(8 * densidad_mult)
                num_nuevas = min(num_nuevas, 60)  # Lluvia torrencial

                # Color partículas también interpolado suavemente
                num_cols = len(colores_particula)
                pos = progreso * (num_cols - 1)
                idx_b = int(pos)
                idx_a = min(idx_b + 1, num_cols - 1)
                color_particula = interpolate_color(colores_particula[idx_b], colores_particula[idx_a], pos - idx_b)

                for _ in range(num_nuevas):
                    angulo = np.random.uniform(0, 2 * np.pi)
                    profundidad = np.random.uniform(0, 1)

                    x_origen = centro_x + radio_spawn * np.cos(angulo)
                    y_origen = centro_y + radio_spawn * np.sin(angulo)

                    # Líneas cortas pero MUCHAS
                    largo = 0.1 + profundidad * 0.15
                    grosor = 1 + profundidad * 1.5
                    opacidad = 0.2 + profundidad * 0.5

                    dir_x = -np.cos(angulo)
                    dir_y = -np.sin(angulo)

                    punto_inicio = np.array([x_origen, y_origen, 0])
                    punto_fin = np.array([x_origen + dir_x * largo, y_origen + dir_y * largo, 0])

                    particula = Line(
                        start=punto_inicio,
                        end=punto_fin,
                        color=color_particula,
                        stroke_width=grosor,
                        stroke_opacity=opacidad
                    )

                    # Velocidad suave y constante (fluidez)
                    particula.vel = vel_base * (0.9 + profundidad * 0.2)
                    particula.dir = np.array([dir_x, dir_y, 0])
                    particula.largo_original = largo

                    contenedor.add(particula)
                    estado['particulas'].append(particula)

            # Mover partículas existentes con EFECTO JERINGA
            particulas_a_remover = []
            impactos = []  # Guardar puntos de impacto para calentar

            for p in estado['particulas']:
                # Mover
                p.shift(p.dir * p.vel * dt)

                # Obtener puntos actuales de la línea
                inicio = p.get_start()  # Punto trasero (lejos del centro)
                fin = p.get_end()       # Punto delantero (cerca del centro)

                # Distancias al centro del planeta
                dist_inicio = np.sqrt((inicio[0] - centro_x)**2 + (inicio[1] - centro_y)**2)
                dist_fin = np.sqrt((fin[0] - centro_x)**2 + (fin[1] - centro_y)**2)

                # Si el punto trasero ya está dentro, eliminar y registrar impacto
                if dist_inicio < radio_planeta:
                    particulas_a_remover.append(p)
                    # Registrar punto de impacto (donde tocó la superficie)
                    impactos.append((inicio[0] - centro_x, inicio[1] - centro_y))
                # Si el punto delantero está dentro pero el trasero no: EFECTO JERINGA
                elif dist_fin < radio_planeta:
                    dx = centro_x - inicio[0]
                    dy = centro_y - inicio[1]
                    dist_a_centro = np.sqrt(dx**2 + dy**2)

                    factor = (dist_a_centro - radio_planeta) / dist_a_centro
                    nuevo_fin = np.array([
                        inicio[0] + dx * factor,
                        inicio[1] + dy * factor,
                        0
                    ])
                    p.put_start_and_end_on(inicio, nuevo_fin)

            # CALENTAR PLANETA donde impactan las partículas
            radio_calor = 0.3  # Radio de influencia del calor
            calor_por_impacto = 0.015  # Cuánto calienta cada impacto

            for (ix, iy) in impactos:
                for dato in self.datos_puntos:
                    # Distancia del punto al impacto
                    dist = np.sqrt((dato['x'] - ix)**2 + (dato['y'] - iy)**2)
                    if dist < radio_calor:
                        # Calentar según cercanía (más cerca = más calor)
                        factor_calor = 1 - (dist / radio_calor)
                        dato['temperatura'] += calor_por_impacto * factor_calor
                        dato['temperatura'] = min(1.0, dato['temperatura'])

                        # Actualizar color
                        nuevo_color = self.noise_a_color(dato['temperatura'])
                        dato['punto'].set_fill(nuevo_color, opacity=0.95)

            # Remover partículas absorbidas
            for p in particulas_a_remover:
                if p in estado['particulas']:
                    estado['particulas'].remove(p)
                contenedor.remove(p)

        contenedor.add_updater(lluvia_updater)

        # Actualizar contador y planeta mientras corre la lluvia
        num_updates = 50
        tiempo_por_update = duracion / num_updates

        for i in range(num_updates):
            progreso = i / num_updates
            exponente = int(10 + progreso * 20)

            # Actualizar contador
            nuevo_contador = self.actualizar_contador(exponente)
            self.remove(self.contador_valor)
            self.contador_valor = nuevo_contador
            self.add(self.contador_valor)

            # Actualizar barra
            progreso_barra = progreso
            nueva_anchura = max(0.01, 2.5 * progreso_barra)
            self.barra_progreso.stretch_to_fit_width(nueva_anchura)
            self.barra_progreso.align_to(barra_fondo, LEFT)

            if exponente < 15:
                self.barra_progreso.set_fill(YELLOW)
            elif exponente < 20:
                self.barra_progreso.set_fill(ORANGE)
            elif exponente < 25:
                self.barra_progreso.set_fill(RED)
            else:
                self.barra_progreso.set_fill(WHITE)

            # Borde del planeta cambia según temperatura promedio
            temp_promedio = sum(d['temperatura'] for d in self.datos_puntos) / len(self.datos_puntos)
            color_borde = self.noise_a_color(temp_promedio)
            self.borde_planeta.set_stroke(color_borde, width=2 + temp_promedio * 3)

            # Atmósfera: según temperatura del planeta
            opacidad_atm = temp_promedio * 0.7
            radio_atm = radio_planeta * (1.2 + temp_promedio * 0.4)
            color_atm = self.noise_a_color(temp_promedio)
            self.atmosfera.scale_to_fit_width(radio_atm * 2)
            self.atmosfera.set_fill(color_atm, opacity=opacidad_atm)
            self.atmosfera.set_stroke(color_atm, width=temp_promedio * 4, opacity=temp_promedio * 0.8)

            # Actualizar indicador de estado según TEMPERATURA real
            if temp_promedio < 0.2:
                titulo_texto = "SÓLIDO"
                subtitulo_texto = "Frío"
                titulo_color = PURPLE
            elif temp_promedio < 0.4:
                titulo_texto = "SÓLIDO"
                subtitulo_texto = "Calentando"
                titulo_color = BLUE
            elif temp_promedio < 0.6:
                titulo_texto = "LÍQUIDO"
                subtitulo_texto = "Caliente"
                titulo_color = YELLOW
            elif temp_promedio < 0.8:
                titulo_texto = "LÍQUIDO"
                subtitulo_texto = "Muy caliente"
                titulo_color = ORANGE
            else:
                titulo_texto = "PLASMA"
                subtitulo_texto = "Como un sol"
                titulo_color = RED

            nuevo_titulo = Text(titulo_texto, font_size=18, color=titulo_color)
            nuevo_titulo.move_to(self.estado_titulo)

            nuevo_subtitulo = Text(subtitulo_texto, font_size=9, color=titulo_color)
            nuevo_subtitulo.next_to(nuevo_titulo, DOWN, buff=0.1)

            self.remove(self.estado_titulo, self.estado_subtitulo)
            self.estado_titulo = nuevo_titulo
            self.estado_subtitulo = nuevo_subtitulo
            self.add(self.estado_titulo, self.estado_subtitulo)

            self.wait(tiempo_por_update)

        contenedor.remove_updater(lluvia_updater)

        # Limpiar partículas restantes suavemente
        self.play(FadeOut(contenedor), run_time=1)

        # Mensaje final (sin explosión)
        conclusion = VGroup(
            Text("Planeta transformado por absorción", font_size=22, color=BLUE_A),
            Text("Sólido → Líquido → Gaseoso", font_size=16, color=GRAY),
        ).arrange(DOWN, buff=0.2)
        conclusion.to_edge(DOWN)

        self.play(Write(conclusion))
        self.wait(2)


# Para renderizar:
# pip install noise  (si no está instalado)
# manim -pqh LeSage-v1.2.2.py LeSageComparacion
