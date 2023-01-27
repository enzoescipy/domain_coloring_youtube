from manim import *
#target:
"""
1. x^2 - 1 graph appears.
2. vertical colorline of what color has to mapped where in numerical line of y, appears in right-side of graph.
3. some unordered-pairs in y=x^2-1 graph show as blank circle, and filled by correct color from the 2.'s colorline.
4. 3.'s pairs are started to drop to the x axis.
5. all(kind of?) of the points in the graph randomly changed to colored-circle and dropped to the x-axis, finally making x-axis colorful.

"""


class Main(Scene):
    def construct(self):
        m1a = Square().set_color(RED).shift(LEFT)
        m1b = Circle().set_color(RED).shift(LEFT)
        m2a= Square().set_color(BLUE).shift(RIGHT)
        m2b= Circle().set_color(BLUE).shift(RIGHT)

        points = m2a.points
        points = np.roll(points, int(len(points)/4), axis=0)
        m2a.points = points

        self.play(Transform(m1a,m1b),Transform(m2a,m2b), run_time=1)
