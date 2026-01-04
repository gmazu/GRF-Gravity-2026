from manim import *
import numpy as np
import yaml
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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
    LeSage v1.2.2.1 - Planeta calentado por impactos

    - Heatmap con matplotlib para textura térmica base
    - Planeta se calienta DONDE las partículas impactan
    - Calor se propaga desde puntos de impacto
    """

    def _color(self, value):
        if isinstance(value, str):
            if value.startswith("#"):
                return ManimColor(value)
            if value in globals():
                return globals()[value]
        return value

    def _colors(self, values):
        return [self._color(v) for v in values]

    def _corner(self, name):
        mapping = {
            "UR": UR,
            "UL": UL,
            "DR": DR,
            "DL": DL,
        }
        return mapping.get(name, UR)

    def _shift_vec(self, xy):
        return np.array([xy[0], xy[1], 0])

    def _exponente_a_superindice(self, exponente):
        superindices = self.cfg_contador['superindices']
        return "".join(superindices[int(d)] for d in str(exponente))

    def _color_por_exponente(self, exponente):
        for item in self.cfg_contador['thresholds']:
            if exponente < item['max']:
                return self._color(item['color'])
        return self._color(self.cfg_contador['thresholds'][-1]['color'])

    def _estado_por_temp(self, temp_promedio):
        for item in self.cfg_estado['thresholds']:
            if temp_promedio < item['max']:
                return item
        return self.cfg_estado['thresholds'][-1]

    def noise_a_color(self, valor):
        """Convierte valor 0-1 a color térmico."""
        colores = self.colores_termicos
        valor = max(0, min(1, valor))  # Clamp 0-1

        pos = valor * (len(colores) - 1)
        idx1 = int(pos)
        idx2 = min(idx1 + 1, len(colores) - 1)
        t = pos - idx1

        return interpolate_color(colores[idx1], colores[idx2], t)

    def _crear_cmap_nasa(self):
        colors_nasa = self.cfg_heatmap['colors_nasa']
        cmap = LinearSegmentedColormap.from_list('nasa_thermal', colors_nasa)
        cmap.set_bad(alpha=0)
        return cmap

    def _init_heatmap(self, radio_visual):
        size = self.cfg_heatmap['size']
        x = np.linspace(-radio_visual, radio_visual, size)
        y = np.linspace(-radio_visual, radio_visual, size)
        X, Y = np.meshgrid(x, y)

        escala = self.cfg_heatmap['scale'] / radio_visual
        Xn = X * escala
        Yn = Y * escala
        lat = np.abs(Y) / radio_visual
        grad_lat = 1 - np.clip(lat, 0, 1)

        ruido_cfg = self.cfg_heatmap['noise']
        Z = np.sin(Xn * ruido_cfg['sin_x']) * np.cos(Yn * ruido_cfg['sin_y'])
        Z += np.sin(Xn * ruido_cfg['sin_mix_x'] + Yn * ruido_cfg['sin_mix_y']) * ruido_cfg['sin_mix_amp']
        Z += np.cos(Xn * ruido_cfg['cos_x'] - Yn * ruido_cfg['cos_y']) * ruido_cfg['cos_amp']
        Z = (Z - Z.min()) / (Z.max() - Z.min())
        self.heat_noise = Z

        base = self.cfg_heatmap['lat_weight'] * grad_lat + self.cfg_heatmap['noise_weight'] * Z
        self.heat_grid = np.clip(base * self.cfg_heatmap['base_intensity'], 0, 1)
        self.heat_mask = X**2 + Y**2 > (radio_visual * self.cfg_heatmap['mask_factor']) ** 2
        self.heat_size = size
        self.heat_x_min = x[0]
        self.heat_y_min = y[0]
        self.heat_dx = x[1] - x[0]
        self.heat_dy = y[1] - y[0]

        self.cmap_nasa = self._crear_cmap_nasa()

        heat_radius = self.cfg_heatmap['kernel_radius']
        k = max(1, int(heat_radius / self.heat_dx))
        kx = np.arange(-k, k + 1) * self.heat_dx
        ky = np.arange(-k, k + 1) * self.heat_dy
        KX, KY = np.meshgrid(kx, ky)
        dist = np.sqrt(KX**2 + KY**2)
        kernel = np.clip(1 - (dist / heat_radius), 0, 1)

        self.heat_kernel = kernel
        self.heat_kernel_radius = k

    def _render_heatmap(self, ruta_salida, radio_visual):
        img_cfg = self.cfg_heatmap['image']
        Z = self.heat_grid.copy()
        Z[self.heat_mask] = np.nan

        fig, ax = plt.subplots(figsize=tuple(img_cfg['figsize']), dpi=img_cfg['dpi'])
        ax.imshow(
            Z,
            cmap=self.cmap_nasa,
            extent=[-radio_visual, radio_visual, -radio_visual, radio_visual],
            origin='lower'
        )
        ax.axis('off')
        ax.set_aspect('equal')
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        plt.savefig(
            ruta_salida,
            bbox_inches=img_cfg['bbox_inches'],
            pad_inches=img_cfg['pad_inches'],
            transparent=img_cfg['transparent']
        )
        plt.close(fig)

    def _crear_planeta_heatmap(self, centro, radio_visual):
        self._render_heatmap(self.heatmap_path, radio_visual)
        imagen = ImageMobject(self.heatmap_path)
        imagen.scale_to_fit_width(radio_visual * 2)
        imagen.move_to(centro)
        return imagen

    def _actualizar_planeta_heatmap(self, centro, radio_visual):
        self._render_heatmap(self.heatmap_path, radio_visual)
        nueva = ImageMobject(self.heatmap_path)
        nueva.scale_to_fit_width(radio_visual * 2)
        nueva.move_to(centro)
        self.planeta_imagen.become(nueva)

    def _aplicar_calor(self, ix, iy, calor):
        col = int(round((ix - self.heat_x_min) / self.heat_dx))
        row = int(round((iy - self.heat_y_min) / self.heat_dy))

        if row < 0 or row >= self.heat_size or col < 0 or col >= self.heat_size:
            return
        if self.heat_mask[row, col]:
            return

        r = self.heat_kernel_radius
        r0 = max(row - r, 0)
        r1 = min(row + r + 1, self.heat_size)
        c0 = max(col - r, 0)
        c1 = min(col + r + 1, self.heat_size)

        k_r0 = r0 - (row - r)
        k_c0 = c0 - (col - r)
        k_r1 = k_r0 + (r1 - r0)
        k_c1 = k_c0 + (c1 - c0)

        self.heat_grid[r0:r1, c0:c1] += calor * self.heat_kernel[k_r0:k_r1, k_c0:k_c1]

    def construct(self):
        self.cfg_heatmap = LESAGE['heatmap']
        self.cfg_calor = LESAGE['calor']
        self.cfg_exponente = LESAGE['exponente']
        self.cfg_contador = LESAGE['contador']
        self.cfg_planeta = LESAGE['planeta']
        self.cfg_lluvia = LESAGE['lluvia']
        self.cfg_updates = LESAGE['updates']
        self.cfg_calentamiento = LESAGE['calentamiento']
        self.cfg_estado = LESAGE['estado']
        self.cfg_ui = LESAGE['ui']

        nombre = CONFIG['masa_actual']['nombre']
        radio_visual = CONFIG['masa_actual']['radio_visual']

        CENTRO = ORIGIN

        # Título
        title_cfg = self.cfg_ui['title']
        title = Text(
            title_cfg['text'],
            font_size=title_cfg['font_size'],
            color=self._color(title_cfg['color'])
        )
        self.play(Write(title))
        self.wait(title_cfg['wait'])
        self.play(FadeOut(title))

        # Crear planeta con heatmap generado por matplotlib
        # Paleta térmica: Púrpura → Azul → Cyan → Amarillo → Naranja → Rojo
        self.colores_termicos = self._colors(self.cfg_heatmap['palette_termica'])
        self.heatmap_path = str(Path(__file__).parent / self.cfg_heatmap['image']['filename'])
        self._init_heatmap(radio_visual)
        self.planeta_imagen = self._crear_planeta_heatmap(CENTRO, radio_visual)

        # Borde del planeta
        self.borde_planeta = Circle(
            radius=radio_visual,
            color=self._color(self.cfg_planeta['borde_color']),
            fill_opacity=0,
            stroke_width=self.cfg_planeta['borde_base_width']
        )
        self.borde_planeta.move_to(CENTRO)

        self.planeta = Group(self.planeta_imagen, self.borde_planeta)

        label_cfg = self.cfg_ui['label_planeta']
        label_planeta = Text(
            nombre,
            font_size=label_cfg['font_size'],
            color=self._color(label_cfg['color'])
        ).move_to(CENTRO)

        self.play(
            GrowFromCenter(self.planeta),
            Write(label_planeta),
            run_time=self.cfg_ui['grow_run_time']
        )

        self.centro = CENTRO
        self.radio_visual = radio_visual
        self.impactos_acumulados = []

        # CONTADOR DE DENSIDAD (arriba derecha)
        self.densidad_actual = self.cfg_contador['densidad_inicial']
        self.densidad_meta = self.cfg_contador['densidad_meta']

        contador_label_cfg = self.cfg_ui['contador_label']
        contador_label = Text(
            contador_label_cfg['text'],
            font_size=contador_label_cfg['font_size'],
            color=self._color(contador_label_cfg['color'])
        )
        contador_label.to_corner(self._corner(contador_label_cfg['corner']))
        contador_label.shift(self._shift_vec(contador_label_cfg['shift']))

        exp_inicial = self._exponente_a_superindice(self.cfg_exponente['min'])
        self.contador_valor = Text(
            f"10{exp_inicial}",
            font_size=self.cfg_contador['valor_font_size'],
            color=self._color(self.cfg_ui['contador_valor']['color'])
        )
        self.contador_valor.next_to(contador_label, DOWN)

        meta_cfg = self.cfg_ui['meta_label']
        meta_label = Text(
            meta_cfg['text'],
            font_size=meta_cfg['font_size'],
            color=self._color(meta_cfg['color'])
        )
        meta_label.next_to(self.contador_valor, DOWN, buff=meta_cfg['buff'])

        self.add(contador_label, self.contador_valor, meta_label)

        # Barra de progreso
        barra_cfg = self.cfg_ui['barra']
        barra_fondo = Rectangle(
            width=barra_cfg['width'],
            height=barra_cfg['height'],
            color=self._color(barra_cfg['bg_color']),
            fill_opacity=barra_cfg['bg_opacity']
        )
        barra_fondo.next_to(meta_label, DOWN, buff=barra_cfg['buff'])

        self.barra_progreso = Rectangle(
            width=barra_cfg['fg_min_width'],
            height=barra_cfg['height'],
            color=self._color(barra_cfg['fg_color']),
            fill_opacity=barra_cfg['fg_opacity']
        )
        self.barra_progreso.align_to(barra_fondo, LEFT)
        self.barra_progreso.move_to(barra_fondo.get_left(), aligned_edge=LEFT)

        self.add(barra_fondo, self.barra_progreso)

        # INDICADOR DE ESTADO (arriba izquierda)
        estado_label_cfg = self.cfg_ui['estado_label']
        estado_label = Text(
            estado_label_cfg['text'],
            font_size=estado_label_cfg['font_size'],
            color=self._color(estado_label_cfg['color'])
        )
        estado_label.to_corner(self._corner(estado_label_cfg['corner']))
        estado_label.shift(self._shift_vec(estado_label_cfg['shift']))

        estado_inicial = self.cfg_estado['thresholds'][0]
        self.estado_titulo = Text(
            estado_inicial['title'],
            font_size=self.cfg_ui['estado_titulo']['font_size'],
            color=self._color(estado_inicial['color'])
        )
        self.estado_titulo.next_to(estado_label, DOWN)

        self.estado_subtitulo = Text(
            estado_inicial['subtitle'],
            font_size=self.cfg_ui['estado_subtitulo']['font_size'],
            color=self._color(estado_inicial['color'])
        )
        self.estado_subtitulo.next_to(self.estado_titulo, DOWN, buff=self.cfg_ui['estado_subtitulo']['buff'])

        self.add(estado_label, self.estado_titulo, self.estado_subtitulo)

        # FASE PRINCIPAL: Calentamiento con contador
        self.calentamiento_con_contador(
            duracion=self.cfg_calentamiento['duracion'],
            centro=CENTRO,
            label=label_planeta,
            barra_fondo=barra_fondo
        )

        # Final
        self.wait(self.cfg_calentamiento['post_wait'])

    def actualizar_contador(self, exponente):
        """Actualiza el texto del contador."""
        # Convertir exponente a superíndice
        exp_str = self._exponente_a_superindice(exponente)

        nuevo_texto = Text(f"10{exp_str}", font_size=self.cfg_contador['valor_font_size'])

        # Color según peligro
        nuevo_texto.set_color(self._color_por_exponente(exponente))

        nuevo_texto.move_to(self.contador_valor)
        return nuevo_texto

    def calentamiento_con_contador(self, duracion=None, centro=ORIGIN, label=None, barra_fondo=None):
        """Calentamiento progresivo con lluvia CONTINUA usando updater."""
        if duracion is None:
            duracion = self.cfg_calentamiento['duracion']
        centro_x = centro[0]
        centro_y = centro[1]
        radio_spawn = LESAGE['area']['radio_spawn']
        radio_planeta = CONFIG['masa_actual']['radio_visual']
        calor_por_impacto = self.cfg_calor['impacto']

        # Velocidad base MUY lenta para fluidez
        vel_base = self.cfg_lluvia['vel_base']

        # Paleta térmica NASA/AIRS para partículas (frío → caliente)
        colores_particula = self._colors(self.cfg_lluvia['particula_color'])

        # Estado compartido para el updater
        estado = {
            'tiempo': 0,
            'ultimo_spawn': 0,
            'exponente': self.cfg_exponente['min'],
            'particulas': []
        }

        # Contenedor de partículas
        contenedor = VGroup()
        self.add(contenedor)

        def lluvia_updater(mob, dt):
            estado['tiempo'] += dt
            progreso = min(estado['tiempo'] / duracion, 1.0)

            # Exponente actual (10 → 30)
            exp_min = self.cfg_exponente['min']
            exp_max = self.cfg_exponente['max']
            estado['exponente'] = int(exp_min + progreso * (exp_max - exp_min))
            exponente = estado['exponente']

            # Spawn constante y rápido
            spawn_interval = self.cfg_lluvia['spawn_interval']

            # Spawn nuevas partículas
            if estado['tiempo'] - estado['ultimo_spawn'] > spawn_interval:
                estado['ultimo_spawn'] = estado['tiempo']

                # DENSIDAD SIN MIEDO - tu PC aguanta
                densidad_mult = self.cfg_lluvia['densidad_mult_base']
                densidad_mult += (exponente - exp_min) * self.cfg_lluvia['densidad_mult_step']
                num_nuevas = int(self.cfg_lluvia['num_base'] * densidad_mult)
                num_nuevas = min(num_nuevas, self.cfg_lluvia['num_max'])

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
                    linea_cfg = self.cfg_lluvia['linea']
                    largo = linea_cfg['largo_base'] + profundidad * linea_cfg['largo_gain']
                    grosor = linea_cfg['grosor_base'] + profundidad * linea_cfg['grosor_gain']
                    opacidad = linea_cfg['opacidad_base'] + profundidad * linea_cfg['opacidad_gain']

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
                    particula.vel = vel_base * (
                        self.cfg_lluvia['vel_depth_base'] + profundidad * self.cfg_lluvia['vel_depth_gain']
                    )
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

            if impactos:
                self.impactos_acumulados.extend(impactos)

            # Remover partículas absorbidas
            for p in particulas_a_remover:
                if p in estado['particulas']:
                    estado['particulas'].remove(p)
                contenedor.remove(p)

        contenedor.add_updater(lluvia_updater)

        # Actualizar contador y planeta mientras corre la lluvia
        num_updates = self.cfg_updates['num_updates']
        tiempo_por_update = duracion / num_updates

        for i in range(num_updates):
            progreso = i / num_updates
            exponente = int(
                self.cfg_exponente['min']
                + progreso * (self.cfg_exponente['max'] - self.cfg_exponente['min'])
            )

            # Actualizar contador
            nuevo_contador = self.actualizar_contador(exponente)
            self.remove(self.contador_valor)
            self.contador_valor = nuevo_contador
            self.add(self.contador_valor)

            # Actualizar barra
            progreso_barra = progreso
            barra_cfg = self.cfg_ui['barra']
            nueva_anchura = max(barra_cfg['fg_min_width'], barra_cfg['width'] * progreso_barra)
            self.barra_progreso.stretch_to_fit_width(nueva_anchura)
            self.barra_progreso.align_to(barra_fondo, LEFT)

            self.barra_progreso.set_fill(self._color_por_exponente(exponente))

            impactos = self.impactos_acumulados
            self.impactos_acumulados = []
            if impactos:
                for (ix, iy) in impactos:
                    self._aplicar_calor(ix, iy, calor_por_impacto)
                self.heat_grid = np.clip(self.heat_grid, 0, 1)

            calor_global = self.cfg_calor['global_base'] + progreso * self.cfg_calor['global_gain']
            self.heat_grid = np.clip(self.heat_grid + calor_global, 0, 1)

            homogenize = min(1.0, progreso * self.cfg_calor['homogenize_gain'])
            warm_target = np.clip(
                self.cfg_calor['warm_floor']
                + self.cfg_calor['warm_noise_weight'] * self.heat_noise,
                0,
                1
            )
            self.heat_grid = (1 - homogenize) * self.heat_grid + homogenize * warm_target
            self._actualizar_planeta_heatmap(self.centro, self.radio_visual)

            # Borde del planeta cambia según temperatura promedio
            temp_promedio = float(np.mean(self.heat_grid[~self.heat_mask]))
            color_borde = self.noise_a_color(temp_promedio)
            self.borde_planeta.set_stroke(
                color_borde,
                width=self.cfg_planeta['borde_base_width'] + temp_promedio * self.cfg_planeta['borde_gain']
            )

            # Actualizar indicador de estado según TEMPERATURA real
            estado_actual = self._estado_por_temp(temp_promedio)
            titulo_color = self._color(estado_actual['color'])

            nuevo_titulo = Text(
                estado_actual['title'],
                font_size=self.cfg_ui['estado_titulo']['font_size'],
                color=titulo_color
            )
            nuevo_titulo.move_to(self.estado_titulo)

            nuevo_subtitulo = Text(
                estado_actual['subtitle'],
                font_size=self.cfg_ui['estado_subtitulo']['font_size'],
                color=titulo_color
            )
            nuevo_subtitulo.next_to(nuevo_titulo, DOWN, buff=self.cfg_ui['estado_subtitulo']['buff'])

            self.remove(self.estado_titulo, self.estado_subtitulo)
            self.estado_titulo = nuevo_titulo
            self.estado_subtitulo = nuevo_subtitulo
            self.add(self.estado_titulo, self.estado_subtitulo)

            self.wait(tiempo_por_update)

        contenedor.remove_updater(lluvia_updater)

        # Limpiar partículas restantes suavemente
        self.play(FadeOut(contenedor), run_time=self.cfg_ui['fadeout_run_time'])

        # Mensaje final (sin explosión)
        conclusion_cfg = self.cfg_ui['conclusion']
        conclusion = VGroup(
            Text(
                conclusion_cfg['line1_text'],
                font_size=conclusion_cfg['line1_font_size'],
                color=self._color(conclusion_cfg['line1_color'])
            ),
            Text(
                conclusion_cfg['line2_text'],
                font_size=conclusion_cfg['line2_font_size'],
                color=self._color(conclusion_cfg['line2_color'])
            ),
        ).arrange(DOWN, buff=conclusion_cfg['buff'])
        conclusion.to_edge(DOWN)

        self.play(Write(conclusion))
        self.wait(self.cfg_ui['final_wait'])


# Para renderizar:
# pip install noise  (si no está instalado)
# manim -pqh LeSage-v1.2.2.1.py LeSageComparacion
