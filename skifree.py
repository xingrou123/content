from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from functools import partial
from kivy.graphics import Color, Rectangle
import random


class Skier(Image):
    def __init__(self, game):
        super(Skier, self).__init__(source='images/skier_down.png')
        self.game = game
        self.angle = 0
        self.center_x = Window.width / 2
        self.center_y = 100
        self.v_x = 0

    def turn(self, direction):
        self.angle += direction
        self.angle = max(-2, min(2, self.angle))
        if self.angle == 0:
            self.source = 'images/skier_down.png'

    def move(self):
        self.center_x += self.v_x
        if self.center_x < 20:
            self.center_x = 20
        if self.center_x > Window.width - 20:
            self.center_x = Window.width - 20


class Obstacle(Image):
    def __init__(self, game, image_file, location, type):
        super(Obstacle, self).__init__(source=image_file, center=location)
        self.game = game
        self.type = type

    def update(self, dt):
        self.center_y -= self.game.speed[1]
        if self.center_y < -32:
            self.game.remove_widget(self)
            self.game.obstacles.remove(self)


class GameOver(BoxLayout):
    def __init__(self, game, score, **kwargs):
        super(GameOver, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10

        self.game = game  # Store a reference to the game instance

        score_label = Label(text="Your Score: {}".format(score), font_size=30, size_hint=(1, 0.5))
        self.add_widget(score_label)

        play_again_button = Button(text="Play Again", on_press=self.game.restart_game, size_hint=(1, 0.2))
        self.add_widget(play_again_button)

        exit_button = Button(text="Exit", on_press=self.exit_app, size_hint=(1, 0.2))
        self.add_widget(exit_button)

    def exit_app(self, instance):
        App.get_running_app().stop()


class SkiGame(Widget):
    def __init__(self):
        super(SkiGame, self).__init__()
        self.skier = Skier(self)
        self.add_widget(self.skier)
        self.speed = [0, 6]
        self.obstacles = []
        self.score = 0

        self.score_label = Label(text="Score: " + str(self.score), font_size=20)
        self.add_widget(self.score_label)

        # Set the background color of the score label to black
        with self.score_label.canvas.before:
            Color(0, 0, 0, 1)  # Black color (RGBA)
            self.score_label_rect = Rectangle(size=self.score_label.size, pos=self.score_label.pos)

        self.score_label.bind(size=self._update_score_label_rect, pos=self._update_score_label_rect)

        self.game_over_popup = None

        Clock.schedule_interval(self.update, 1.0 / 30.0)

        # Set the background color
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White color (RGBA)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def _update_score_label_rect(self, instance, value):
        self.score_label_rect.size = instance.size
        self.score_label_rect.pos = instance.pos

    def on_key_down(self, window, key, *args):
        if key in (97, 276):  # 'a' key or left arrow
            self.skier.v_x = -5  # Adjust the speed as needed
        elif key in (100, 275):  # 'd' key or right arrow
            self.skier.v_x = 5  # Adjust the speed as needed

    def on_key_up(self, window, key, *args):
        if key in (97, 276, 100, 275):  # 'a' key or left arrow or 'd' key or right arrow
            self.skier.v_x = 0

    def create_map(self, dt=None):
        if len(self.obstacles) < 5:  # Limit the number of obstacles
            row = random.randint(0, 9)
            col = random.randint(0, 9)
            location = (col * 64 + 20, row * 64 + 20 + 640)
            obstacle_type = random.choice(["tree", "flag"])
            if obstacle_type == "tree":
                img = "images/skier_tree.png"
            elif obstacle_type == "flag":
                img = "images/skier_flag.png"
            obstacle = Obstacle(self, image_file=img, location=location, type=obstacle_type)
            self.obstacles.append(obstacle)
            self.add_widget(obstacle)

    def update(self, dt):
        self.skier.move()
        for obstacle in self.obstacles[:]:
            obstacle.update(dt)
            if self.skier.collide_widget(obstacle):
                if obstacle.type == "tree":
                    self.skier.source = "images/skier_crash.png"
                    Clock.schedule_once(self.game_over, 1)
                elif obstacle.type == "flag":
                    self.score += 10
                    self.remove_widget(obstacle)
                    self.obstacles.remove(obstacle)
        self.create_map()
        self.score_label.text = "Score: " + str(self.score)

    def game_over(self, dt):
        self.game_over_popup = Popup(title="Game Over", content=GameOver(game=self, score=self.score),
                                     size_hint=(None, None), size=(300, 200), auto_dismiss=False)
        self.game_over_popup.open()

    def restart_game(self, *args):
        if self.game_over_popup:
            self.game_over_popup.dismiss()  # Dismiss the Popup
        Clock.schedule_once(self.play_restart, 0.5)  # Delay the restart to allow time for the dismissal

    def play_restart(self, *args):
        self.clear_widgets()
        self.__init__()  # Reinitialize the game
        self.create_map()


class SkiApp(App):
    def build(self):
        game = SkiGame()
        game.create_map()
        Window.bind(on_key_down=game.on_key_down, on_key_up=game.on_key_up)
        return game


if __name__ == "__main__":
    SkiApp().run()
