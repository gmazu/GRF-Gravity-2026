from manim import *
import numpy as np

class OceanGravity(Scene):
    def construct(self):
        # Título
        title = Text("Gravedad como Océano eCEL", font_size=48)
        subtitle = Text("Push Gravity via Pressure Gradients", font_size=24)
        subtitle.next_to(title, DOWN)
        
        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Crear océano de fondo (grid eCEL)
        ocean_grid = self.create_ocean_grid()
        self.play(Create(ocean_grid), run_time=2)
        
        # Crear dos planetas
        planet1 = Circle(radius=0.3, color=BLUE, fill_opacity=0.8)
        planet1.move_to(LEFT * 3)
        planet1_label = Text("M₁", font_size=20).next_to(planet1, UP, buff=0.1)
        
        planet2 = Circle(radius=0.3, color=RED, fill_opacity=0.8)
        planet2.move_to(RIGHT * 3)
        planet2_label = Text("M₂", font_size=20).next_to(planet2, UP, buff=0.1)
        
        self.play(
            FadeIn(planet1), 
            FadeIn(planet2),
            Write(planet1_label),
            Write(planet2_label)
        )
        self.wait(1)
        
        # Mostrar presión océano (flechas empujando)
        arrows1 = self.create_pressure_arrows(planet1, direction="inward")
        arrows2 = self.create_pressure_arrows(planet2, direction="inward")
        
        self.play(
            *[GrowArrow(arrow) for arrow in arrows1],
            *[GrowArrow(arrow) for arrow in arrows2],
            run_time=2
        )
        self.wait(1)
        
        # Deformar océano (gradient de presión)
        deformed_grid = self.create_deformed_grid(planet1, planet2)
        self.play(
            Transform(ocean_grid, deformed_grid),
            run_time=3
        )
        self.wait(1)
        
        # Planetas se acercan (empujados por océano)
        self.play(
            planet1.animate.shift(RIGHT * 1.5),
            planet2.animate.shift(LEFT * 1.5),
            planet1_label.animate.shift(RIGHT * 1.5),
            planet2_label.animate.shift(LEFT * 1.5),
            run_time=3,
            rate_func=smooth
        )
        self.wait(1)
        
        # Texto explicativo
        explanation = Text(
            "Océano eCEL empuja desde afuera\n"
            "Presión diferencial → Atracción aparente",
            font_size=28,
            color=YELLOW
        ).to_edge(DOWN)
        
        self.play(Write(explanation))
        self.wait(3)
        
    def create_ocean_grid(self):
        """Crea grid representando océano eCEL"""
        grid = VGroup()
        
        # Grid horizontal
        for y in np.arange(-3, 3.5, 0.5):
            line = Line(
                start=LEFT * 6 + UP * y,
                end=RIGHT * 6 + UP * y,
                color=BLUE_E,
                stroke_width=1
            )
            grid.add(line)
        
        # Grid vertical
        for x in np.arange(-6, 6.5, 0.5):
            line = Line(
                start=RIGHT * x + UP * 3,
                end=RIGHT * x + DOWN * 3,
                color=BLUE_E,
                stroke_width=1
            )
            grid.add(line)
        
        grid.set_opacity(0.3)
        return grid
    
    def create_pressure_arrows(self, obj, direction="inward"):
        """Crea flechas de presión alrededor de objeto"""
        arrows = VGroup()
        center = obj.get_center()
        radius = 1.5
        
        for angle in np.arange(0, 2*PI, PI/4):
            start_point = center + radius * np.array([
                np.cos(angle), 
                np.sin(angle), 
                0
            ])
            
            if direction == "inward":
                end_point = center + (radius * 0.7) * np.array([
                    np.cos(angle), 
                    np.sin(angle), 
                    0
                ])
            else:  # outward
                end_point = center + (radius * 1.3) * np.array([
                    np.cos(angle), 
                    np.sin(angle), 
                    0
                ])
            
            arrow = Arrow(
                start=start_point,
                end=end_point,
                color=YELLOW,
                stroke_width=3,
                buff=0
            )
            arrows.add(arrow)
        
        return arrows
    
    def create_deformed_grid(self, obj1, obj2):
        """Crea grid deformado por presencia de masa"""
        grid = VGroup()
        
        c1 = obj1.get_center()
        c2 = obj2.get_center()
        
        # Grid deformado
        for y in np.arange(-3, 3.5, 0.5):
            points = []
            for x in np.arange(-6, 6.5, 0.2):
                point = np.array([x, y, 0])
                
                # Deformación por obj1
                dist1 = np.linalg.norm(point[:2] - c1[:2])
                if dist1 > 0:
                    deform1 = 0.3 * np.exp(-dist1) * (c1[:2] - point[:2]) / dist1
                else:
                    deform1 = np.array([0, 0])
                
                # Deformación por obj2
                dist2 = np.linalg.norm(point[:2] - c2[:2])
                if dist2 > 0:
                    deform2 = 0.3 * np.exp(-dist2) * (c2[:2] - point[:2]) / dist2
                else:
                    deform2 = np.array([0, 0])
                
                deformed = point + np.array([
                    deform1[0] + deform2[0],
                    deform1[1] + deform2[1],
                    0
                ])
                points.append(deformed)
            
            line = VMobject()
            line.set_points_smoothly(points)
            line.set_color(BLUE_E)
            line.set_stroke(width=1)
            grid.add(line)
        
        # Grid vertical deformado
        for x in np.arange(-6, 6.5, 0.5):
            points = []
            for y in np.arange(-3, 3.5, 0.2):
                point = np.array([x, y, 0])
                
                dist1 = np.linalg.norm(point[:2] - c1[:2])
                if dist1 > 0:
                    deform1 = 0.3 * np.exp(-dist1) * (c1[:2] - point[:2]) / dist1
                else:
                    deform1 = np.array([0, 0])
                
                dist2 = np.linalg.norm(point[:2] - c2[:2])
                if dist2 > 0:
                    deform2 = 0.3 * np.exp(-dist2) * (c2[:2] - point[:2]) / dist2
                else:
                    deform2 = np.array([0, 0])
                
                deformed = point + np.array([
                    deform1[0] + deform2[0],
                    deform1[1] + deform2[1],
                    0
                ])
                points.append(deformed)
            
            line = VMobject()
            line.set_points_smoothly(points)
            line.set_color(BLUE_E)
            line.set_stroke(width=1)
            grid.add(line)
        
        grid.set_opacity(0.3)
        return grid


# Para renderizar:
# manim -pql ocean_gravity.py OceanGravity
