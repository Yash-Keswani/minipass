import traceback

import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy import LOG_LEVELS, Logger
from kivy.config import Config
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldRect
from pykeepass.exceptions import CredentialsError

from components.screens import CustomMDScreenManager, HomeScreen, NewGroupScreen, SearchScreen
from components.utils import alert
from components.wrappers import PManager
from ctypes import windll, c_int64
import sys

windll.user32.SetProcessDpiAwarenessContext(c_int64(-4))

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'log_level', 'error')
Config.set('kivy', 'window_icon', 'icon.ico')
Logger.setLevel(LOG_LEVELS["error"])

DB_NAME = r"testdb.kdbx"
PASSWORD = 'fifty one dancing unicorns'
manager = PManager(DB_NAME, PASSWORD)

def open_db(db_name: str, password):
  global manager
  
  pwd = password.text
  password.text = ''
  try:
    manager = PManager(db_name, pwd)
  except CredentialsError:
    alert('incorrect password')
    return
  app_.app_init(manager.groups)
    

class SplashScreen(MDScreen):
  def __init__(self, *args, **kwargs):
    self.name='splash'
    super().__init__(*args, **kwargs)
    db_name_label = MDLabel(
              id='db_name',
              text=f'{DB_NAME}'
    )
    password = MDTextField(
                id='password'
    )
    self.add_widget(
      MDCard(
        MDBoxLayout(
          MDBoxLayout(
            db_name_label,
            MDBoxLayout(
              MDLabel(
                text='enter database password'
              ),
              password,
              orientation='horizontal'
            ),
            orientation='vertical',
            size_hint=(1, 0.7)
          ),
          MDRectangleFlatButton(
            text='submit',
            size_hint=(1, 0.3),
            on_release=lambda me: open_db(db_name_label.text, password)
          ),
          orientation='vertical',
          spacing=dp(25)
        ),
        size_hint=(0.6, 0.4),
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
        padding=dp(30)
      )
    )

class MainApp(MDApp):
  icon='icon.png'
  
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # self.DEBUG = False
    self.sm = CustomMDScreenManager()

  def build(self, first=False):
    Window.size = (900, 600)
    self.theme_cls.theme_style = "Dark"
    self.theme_cls.primary_palette = "BlueGray"
    
    self.sm.add_widget(SplashScreen())
    self.sm.app = self
    return self.sm
  
  def app_init(self, groups):
    home = HomeScreen(groups=groups.values(), sm=self.sm)
    self.sm.home_screen = home
    
    self.sm.add_widget(home)
    self.sm.add_widget(NewGroupScreen(sm=self.sm))
    self.sm.add_widget(SearchScreen(sm=self.sm))
    self.sm.goto('home')
  
  def lock(self):
    self.sm.goto('splash')

global app_
if __name__ == '__main__':
  global app_
  try:
    app_ = MainApp()
    app_.run()
  except Exception as e:
    print('\n'.join(traceback.format_exception(e)))
