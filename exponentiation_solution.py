from manim import *

class ExponentiationSolution(Scene):
    def construct(self):
        # Problem statement
        problem = MathTex("8^{\\frac{2}{3}} \\times 9^{\\frac{1}{2}}").scale(1.5)
        self.play(Write(problem))
        self.wait(2)

        # Step 1: Expressing 8 and 9 in terms of prime factors
        step1_text = Text("Step 1:").to_edge(UP).set_color(YELLOW)
        eight_prime = MathTex("8 = 2^3").set_color(RED).shift(LEFT * 2 + UP)
        nine_prime = MathTex("9 = 3^2").set_color(BLUE).shift(RIGHT * 2 + UP)

        self.play(Write(step1_text))  # Show step 1 text
        self.play(Write(eight_prime), Write(nine_prime))
        self.wait(2)

        # Fade out previous Text and show next Text
        self.play(FadeOut(step1_text), FadeOut(eight_prime), FadeOut(nine_prime))

        # Step 2: Recall the property
        step2_text = Text("Step 2: Recall:").to_edge(UP).set_color(YELLOW)
        property_text = MathTex("\\left(a^{b}\\right)^c = a^{b \\cdot c}").shift(DOWN)

        self.play(Write(step2_text))  # Show step 2 text
        self.play(Write(property_text))
        self.wait(2)

        # Fade out previous Text and show next Text
        self.play(FadeOut(step2_text), FadeOut(property_text))

        # Step 3: Plug-in and simplify
        step3_text = Text("Step 3: Plug-in:").to_edge(UP).set_color(YELLOW)
        simplify_8 = MathTex("(2^3)^{\\frac{2}{3}} = 2^2 = 4").set_color(RED).shift(LEFT * 3 + DOWN * 2)
        simplify_9 = MathTex("(3^2)^{\\frac{1}{2}} = 3^1 = 3").set_color(BLUE).shift(RIGHT * 3 + DOWN * 2)

        self.play(Write(step3_text))  # Show step 3 text
        self.play(Write(simplify_8), Write(simplify_9))
        self.wait(2)

        # Fade out previous Text and show next Text
        self.play(FadeOut(step3_text), FadeOut(simplify_8), FadeOut(simplify_9))

        # Final answer
        answer_text = Text("Answer:").to_edge(UP).set_color(YELLOW)
        answer = MathTex("4 \\times 3 = 12 \\ \\square").scale(1.5).shift(DOWN)

        self.play(Write(answer_text))  # Show answer text
        self.play(Write(answer))
        self.wait(3)
