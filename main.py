import sys
import os
import time
import random
import json
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize, QUrl
from PyQt6.QtGui import QMovie, QTransform
from PyQt6.QtMultimedia import QSoundEffect
from pynput import keyboard, mouse

# Load config
_base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_base, "config.json")) as f:
    config = json.load(f)

DISTRACTION_THRESHOLD = config["distraction_threshold"]


class DesktopCat(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.state = ""
        self.last_activity_time = time.time()
        self.is_alert = False
        self.running_direction = 1
        self.target_x = 0
        self.target_y = 0
        self.move_speed = config["move_speed"]
        self.pause_probability = config["pause_probability"]
        self.pause_duration = config["pause_duration"]
        self.is_pausing = False
        self.size_map = {
            "eat":  config["eat_size"],
            "move": config["move_size"],
        }

        # Transparent, frameless, always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        initial_size = self.size_map["eat"]
        self.setFixedSize(initial_size, initial_size)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.x() + screen.width() - initial_size - 20,
                  screen.y() + screen.height() - initial_size - 10)

        # Label for displaying GIF
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, initial_size, initial_size)

        # Load GIF movies
        self.movies = {
            "eat":  QMovie(os.path.join(_base, "cat_eat.gif")),
            "move": QMovie(os.path.join(_base, "cat_move.gif")),
        }
        for movie in self.movies.values():
            movie.finished.connect(movie.start)
            movie.start()

        # Load sounds
        self.sound_pause = None

        if config.get("sound_on_pause") and config.get("sound_pause_file"):
            self.sound_pause = QSoundEffect()
            self.sound_pause.setSource(QUrl.fromLocalFile(
                os.path.join(_base, config["sound_pause_file"])))
            # End pause automatically when audio finishes
            self.sound_pause.playingChanged.connect(self._on_pause_sound_finished)

        # Activity check timer: every second
        self.activity_timer = QTimer()
        self.activity_timer.timeout.connect(self.check_activity)
        self.activity_timer.start(1000)

        # Movement timer: moves cat when alert
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_cat)

        # Keyboard and mouse listeners
        self.kb_listener = keyboard.Listener(on_press=self.on_activity)
        self.mouse_listener = mouse.Listener(
            on_move=self.on_activity,
            on_click=self.on_activity,
            on_scroll=self.on_activity
        )
        self.kb_listener.start()
        self.mouse_listener.start()

        self.set_state("eat")

    def on_frame_changed(self):
        pixmap = self.movies[self.state].currentPixmap()
        if self.state == "move" and self.running_direction == 1:
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))
        self.label.setPixmap(pixmap)

    def on_activity(self, *args):
        self.last_activity_time = time.time()

    def check_activity(self):
        idle_time = time.time() - self.last_activity_time
        if idle_time > DISTRACTION_THRESHOLD and not self.is_alert:
            self.start_alert()
        elif idle_time <= DISTRACTION_THRESHOLD and self.is_alert:
            self.stop_alert()

    def start_alert(self):
        self.is_alert = True
        self.set_state("move")
        self.pick_new_target()
        self.move_timer.start(16)

    def stop_alert(self):
        self.is_alert = False
        self.is_pausing = False
        self.move_timer.stop()
        if self.sound_pause and self.sound_pause.isPlaying():
            self.sound_pause.stop()
        self.set_state("eat")

    def pick_new_target(self):
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 50
        self.target_x = random.randint(
            screen.x() + margin,
            screen.x() + screen.width() - self.size_map["move"] - margin)
        self.target_y = random.randint(
            screen.y() + margin,
            screen.y() + screen.height() - self.size_map["move"] - margin)

    def move_cat(self):
        if self.is_pausing:
            return
        dx = self.target_x - self.x()
        dy = self.target_y - self.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 10:
            if random.random() < self.pause_probability:
                self.start_pause()
            else:
                self.pick_new_target()
            return
        self.running_direction = 1 if dx > 0 else -1
        self.move(self.x() + int(dx / distance * self.move_speed),
                  self.y() + int(dy / distance * self.move_speed))

    def start_pause(self):
        self.is_pausing = True
        if self.sound_pause:
            self.sound_pause.play()
            # Pause duration matches audio — handled by _on_pause_sound_finished
        else:
            QTimer.singleShot(int(self.pause_duration * 1000), self.end_pause)

    def _on_pause_sound_finished(self):
        if not self.sound_pause.isPlaying():
            self.end_pause()

    def end_pause(self):
        self.is_pausing = False
        self.pick_new_target()

    def set_state(self, state):
        if self.state == state:
            return
        try:
            self.movies[self.state].frameChanged.disconnect(self.on_frame_changed)
        except Exception:
            pass
        self.state = state
        size = self.size_map[state]
        self.setFixedSize(size, size)
        self.label.setGeometry(0, 0, size, size)
        self.movies[state].setScaledSize(QSize(size, size))
        self.movies[state].frameChanged.connect(self.on_frame_changed)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def contextMenuEvent(self, event):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cat = DesktopCat()
    cat.show()
    sys.exit(app.exec())
