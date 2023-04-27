import pyotp
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

def otpParse(uri: str):
  if not uri or uri == 'otpauth://totp/Secret?secret=':
    alert("this entry doesn't have any OTP configured")
    return 'NA'
  return pyotp.parse_uri(uri).now()

def otpGen(secret: str):
  return pyotp.totp.TOTP(secret).provisioning_uri()

def alert(text: str):
  MDSnackbar(
    MDLabel(text=text),
    size_hint_x=(Window.width - (dp(10) * 2)) / Window.width,
    x=dp(10),
    y=dp(10),
    duration=1.5
  ).open()
