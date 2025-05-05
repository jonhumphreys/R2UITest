from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.metrics import dp
import serial
from kivy.core.audio import SoundLoader
from functools import partial

# ─── Serial 연결 설정 (에러 방지용 try/except 포함) ───
try:
    ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
except Exception as e:
    ser = None
    print(f"[WARNING] Serial not connected: {e}")

# ─── Kivy 레이아웃 로드 ───
Builder.load_file("main.kv")


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.global_index = 1
        self.HP_index = 0
        self.emotions = [
            ("Angry", "btn_angry.png"),
            ("Happy", "btn_happy.png"),
            ("Sad", "btn_sad.png"),
            ("Scared", "btn_scared.png"),
            ("Curious", "btn_curious.png"),
            ("Confused", "btn_confused.png"),
            ("Proud", "btn_proud.png"),
            ("Nervous", "btn_nervous.png"),
            ("Idle", "btn_idle.png"),
        ]

    def show_audio_buttons(self):
        self.ids.dynamic_area.clear_widgets()

        self.buttons = []  # 버튼 리스트 저장
        for idx, (label, img) in enumerate(self.emotions):
            btn = Button(
                background_normal=f"assets/{img}",
                background_down=f"assets/{img}",
                size_hint=(0.15, 0.1),
                on_press=partial(self.send_emotion_signal, label),
            )
            self.buttons.append(btn)
            self.ids.dynamic_area.add_widget(btn)

        self.spinner_left()

    def update_button_highlight(self):
        for idx, btn in enumerate(self.buttons):
            btn.canvas.after.clear()

            if idx == self.global_index:

                def draw_border(instance, value):
                    instance.canvas.after.clear()
                    with instance.canvas.after:
                        Color(0, 0, 0, 1)  # 검정 테두리
                        Line(
                            rectangle=(
                                instance.x,
                                instance.y,
                                instance.width,
                                instance.height,
                            ),
                            width=3,
                        )

                # 버튼 사이즈/위치 바뀔 때마다 테두리 갱신
                btn.bind(pos=draw_border, size=draw_border)

                # 한 번은 직접 실행
                draw_border(btn, None)

    def spinner_right(self):
        if self.global_index < len(self.emotions) - 1:
            self.global_index += 1
            self.update_button_highlight()

    def spinner_left(self):
        if self.global_index > 0:
            self.global_index -= 1
            self.update_button_highlight()

    def spinner_click(self):
        emotion_name, _ = self.emotions[self.global_index]
        print(f"[SPINNER] Clicked → Playing: {emotion_name}")
        self.send_emotion_signal(emotion_name)

    def HP_joystick_click(self):
        if self.HP_index == 0:
            self.HP_index = 1
            self.send_HP_change_signal()
            print(f"joystick clicked")
        else:
            self.HP_index = 0
            self.send_HP_change_signal()
            print(f"joystick clicked")

    def send_HP_change_signal(self):
        self.ids.what_HP.text = f"Current HP: {self.HP_index}"

    def send_emotion_signal(self, emotion_name, *args):
        print(f"[SOUND] Playing emotion: {emotion_name}")
        sound = SoundLoader.load(f"sounds/{emotion_name.lower()}.mp3")
        self.ids.what_sound.text = f"Playing: {emotion_name}"
        if sound:
            sound.play()
        else:
            print(f"[ERROR] Sound not found: {emotion_name}")


class R2UIApp(App):
    def build(self):
        screen = MainScreen()
        screen.show_audio_buttons()
        return screen


if __name__ == "__main__":
    R2UIApp().run()
