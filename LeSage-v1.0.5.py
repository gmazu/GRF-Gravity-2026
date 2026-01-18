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
    LeSage v1.0.4 - Calentamiento progresivo con contador

    Demuestra el problema fatal de Le Sage:
    Con la densidad de partículas necesaria para explicar la gravedad,
    el planeta se calentaría hasta quemarse.

    Meta: 10³⁰ partículas/m³ (cálculo de Le Sage)
    Spoiler: el planeta (o tu compu) muere antes
    """

    def construct(self):
        nombre = CONFIG['masa_actual']['nombre']
        radio_visual = CONFIG['masa_actual']['radio_visual']

        CENTRO = ORIGIN

        # Título
        title = Text("Le Sage: El Problema del Calentamiento", font_size=36)
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

        # Colores de temperatura para interpolación suave
        # Planeta: azul frío → rojo → naranja → blanco caliente
        colores_planeta = [BLUE, PURPLE, RED, ORANGE, YELLOW, WHITE]
        colores_particula = [YELLOW, ORANGE, ORANGE, RED, RED, WHITE]

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

                    particula = Line(
                        start=np.array([x_origen, y_origen, 0]),
                        end=np.array([x_origen + dir_x * largo, y_origen + dir_y * largo, 0]),
                        color=color_particula,
                        stroke_width=grosor,
                        stroke_opacity=opacidad
                    )

                    # Velocidad suave y constante (fluidez)
                    particula.vel = vel_base * (0.9 + profundidad * 0.2)
                    particula.dir = np.array([dir_x, dir_y, 0])

                    contenedor.add(particula)
                    estado['particulas'].append(particula)

            # Mover partículas existentes
            particulas_a_remover = []
            for p in estado['particulas']:
                # Mover
                p.shift(p.dir * p.vel * dt)

                # Verificar si llegó al planeta - sin pausa, desaparece AL TOCAR
                pos = p.get_center()
                dist = np.sqrt((pos[0] - centro_x)**2 + (pos[1] - centro_y)**2)

                # Se INTRODUCE en el planeta antes de desaparecer (sin frenar)
                if dist < radio_planeta * 0.5:
                    particulas_a_remover.append(p)

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

            # Actualizar color planeta CON INTERPOLACIÓN SUAVE (como acero calentándose)
            # progreso va de 0 a 1, mapeamos a posición en el gradiente
            num_colores = len(colores_planeta)
            posicion = progreso * (num_colores - 1)
            idx_bajo = int(posicion)
            idx_alto = min(idx_bajo + 1, num_colores - 1)
            t = posicion - idx_bajo  # fracción entre los dos colores

            # Interpolación suave entre colores adyacentes
            color_actual = interpolate_color(colores_planeta[idx_bajo], colores_planeta[idx_alto], t)

            self.planeta.set_fill(color_actual, opacity=0.9)
            self.planeta.set_stroke(color_actual, width=3)

            # Label se oscurece gradualmente cuando planeta es muy brillante
            if label and progreso > 0.6:
                label.set_color(interpolate_color(WHITE, BLACK, (progreso - 0.6) / 0.4))

            self.wait(tiempo_por_update)

        contenedor.remove_updater(lluvia_updater)

        # Limpiar partículas restantes
        self.play(FadeOut(contenedor), run_time=0.3)

        # EXPLOSIÓN FINAL
        self.explosion_final(centro)

    def explosion_final(self, centro):
        """El planeta no sobrevive a 10³⁰ partículas/m³."""
        # Glow de muerte
        glows = VGroup()
        for i in range(5):
            glow = Circle(
                radius=CONFIG['masa_actual']['radio_visual'] * (1.2 + i * 0.3),
                color=interpolate_color(WHITE, ORANGE, i/5),
                fill_opacity=0.3 - i * 0.05,
                stroke_width=0
            )
            glow.move_to(centro)
            glows.add(glow)

        self.play(FadeIn(glows), run_time=0.3)

        # Flash blanco
        flash = Circle(radius=0.1, color=WHITE, fill_opacity=1.0, stroke_width=0)
        flash.move_to(centro)

        self.play(
            flash.animate.scale(50).set_opacity(0),
            glows.animate.set_opacity(0),
            self.planeta.animate.set_opacity(0),
            run_time=1.5
        )

        # Mensaje final
        muerte = VGroup(
            Text("☠️ PLANETA VAPORIZADO ☠️", font_size=28, color=RED),
            Text("Le Sage requiere densidad físicamente imposible", font_size=18, color=GRAY),
            Text("La materia se desintegraría antes de sentir gravedad", font_size=16, color=GRAY)
        ).arrange(DOWN, buff=0.3)

        self.play(Write(muerte))
        self.wait(3)


# Para renderizar:
# manim -pql LeSage-v1.0.4.py LeSageCalentamiento
