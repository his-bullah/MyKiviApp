from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android import AndroidService

class MyApp(App):

    def on_start(self):
        if platform == "android":
            request_permissions([
                Permission.INTERNET,
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.FOREGROUND_SERVICE,
                Permission.WAKE_LOCK
            ])
        self.update_ui("Listening...")
        self.start_service()

    def build(self):
        self.label = Label(text="Starting...")
        layout = BoxLayout()
        layout.add_widget(self.label)
        return layout

    def start_service(self):
        service = AndroidService(
            "Background Service Started.",
            "Listening in background..."
        )
        service.start("service started")

    def update_ui(self, text, sec=0):
        Clock.schedule_once(lambda dt: setattr(self.label, "text", text),sec)

MyApp().run()
