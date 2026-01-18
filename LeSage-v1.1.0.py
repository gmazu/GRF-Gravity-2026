from manim import *
import numpy as np
import yaml
from pathlib import Path

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
    LeSage v1.1.0 - Efecto jeringa

    Las partículas se "inyectan" en el planeta:
    - Al tocar la superficie, empiezan a entrar
    - La parte dentro del planeta se oculta (como aguja en piel)
    - Desaparecen gradualmente al ser "tragadas"

    Sin explosiones - transformación gradual.
    """

    def construct(self):
        nombre = CONFIG['masa_actual']['nombre']
        radio_visual = CONFIG['masa_actual']['radio_visual']

        CENTRO = ORIGIN

        # Título
        title = Text("Le Sage: Acumulación de Materia", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Crear planeta
        self.planeta = Circle(
            radius=radio_visual,
            color=BLUE,
            fill_opacity=0.9,
            stroke_width=3
        )
        self.planeta.move_to(CENTRO)
        label_planeta = Text(nombre, font_size=14, color=WHITE).move_to(self.planeta)

        # Atmósfera (empieza invisible)
        self.atmosfera = Circle(
            radius=radio_visual * 1.3,
            color=BLUE_A,
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

        self.estado_titulo = Text("SÓLIDO", font_size=18, color=BLUE)
        self.estado_titulo.next_to(estado_label, DOWN)

        self.estado_subtitulo = Text("Baja temperatura", font_size=9, color=BLUE_A)
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

        # Colores de transición sólido → líquido → gaseoso
        # Planeta: azul sólido → púrpura → aguado transparente
        colores_planeta = [BLUE, BLUE_D, PURPLE_A, PURPLE_B, BLUE_A, BLUE_A]
        colores_particula = [YELLOW, YELLOW, YELLOW_A, YELLOW_A, YELLOW_B, YELLOW_B]

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
            for p in estado['particulas']:
                # Mover
                p.shift(p.dir * p.vel * dt)

                # Obtener puntos actuales de la línea
                inicio = p.get_start()  # Punto trasero (lejos del centro)
                fin = p.get_end()       # Punto delantero (cerca del centro)

                # Distancias al centro del planeta
                dist_inicio = np.sqrt((inicio[0] - centro_x)**2 + (inicio[1] - centro_y)**2)
                dist_fin = np.sqrt((fin[0] - centro_x)**2 + (fin[1] - centro_y)**2)

                # Si el punto trasero ya está dentro, eliminar completamente
                if dist_inicio < radio_planeta:
                    particulas_a_remover.append(p)
                # Si el punto delantero está dentro pero el trasero no: EFECTO JERINGA
                elif dist_fin < radio_planeta:
                    # Calcular punto de intersección con la superficie
                    # Dirección desde inicio hacia el centro
                    dir_norm = p.dir / np.linalg.norm(p.dir[:2])

                    # Resolver intersección línea-círculo
                    # Punto en la superficie del planeta en la dirección de la partícula
                    dx = centro_x - inicio[0]
                    dy = centro_y - inicio[1]
                    dist_a_centro = np.sqrt(dx**2 + dy**2)

                    # Nueva posición del fin: en la superficie del planeta
                    factor = (dist_a_centro - radio_planeta) / dist_a_centro
                    nuevo_fin = np.array([
                        inicio[0] + dx * factor,
                        inicio[1] + dy * factor,
                        0
                    ])

                    # Actualizar la línea para mostrar solo la parte visible
                    p.put_start_and_end_on(inicio, nuevo_fin)

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

            # Actualizar color planeta (sólido → líquido → gaseoso)
            num_colores = len(colores_planeta)
            posicion = progreso * (num_colores - 1)
            idx_bajo = int(posicion)
            idx_alto = min(idx_bajo + 1, num_colores - 1)
            t = posicion - idx_bajo

            color_actual = interpolate_color(colores_planeta[idx_bajo], colores_planeta[idx_alto], t)

            # Opacidad disminuye (se vuelve más gaseoso)
            opacidad_planeta = 0.9 - progreso * 0.3  # 0.9 → 0.6

            self.planeta.set_fill(color_actual, opacity=opacidad_planeta)
            self.planeta.set_stroke(color_actual, width=3)

            # Planeta CRECE ligeramente
            escala_actual = 1 + progreso * 0.15  # crece 15% máximo
            self.planeta.scale_to_fit_width(radio_planeta * 2 * escala_actual)

            # Atmósfera aparece y crece
            opacidad_atm = progreso * 0.25  # máximo 25% opacidad
            radio_atm = radio_planeta * (1.3 + progreso * 0.4)  # crece
            self.atmosfera.scale_to_fit_width(radio_atm * 2)
            self.atmosfera.set_fill(BLUE_A, opacity=opacidad_atm)

            # Actualizar indicador de estado (título + subtítulo)
            if progreso < 0.33:
                titulo_texto = "SÓLIDO"
                subtitulo_texto = "Baja temperatura"
                titulo_color = BLUE
            elif progreso < 0.66:
                titulo_texto = "LÍQUIDO"
                subtitulo_texto = "Alta temperatura"
                titulo_color = PURPLE
            else:
                titulo_texto = "GASEOSO"
                subtitulo_texto = "Crea atmósfera"
                titulo_color = BLUE_A

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
# manim -pqh LeSage-v1.1.0.py LeSageComparacion
