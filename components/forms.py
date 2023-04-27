import secrets

import zxcvbn
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

class FormEntry(MDBoxLayout):
  def value(self):
    return self.textfield.text
  
  def __init__(self, **kwargs):
    label: str = kwargs.pop('label', '')
    id_: str = kwargs.pop('id', '')
    default: str = kwargs.pop('default', '')
    
    self.orientation = 'horizontal'
    self.spacing = dp(20)
    self.id=id_
    super().__init__(**kwargs)
    
    self.label = MDLabel(
      text=label,
      halign='center',
      size_hint=(0.5, 1),
    )
    
    self.textfield = MDTextField(
      text=default,
      pos_hint={'center_x': 0.5, 'center_y': 0.5},
      mode='round',
      size_hint=(1, 0.7),
      height=dp(15)
    )
    
    self.add_widget(self.label)
    self.add_widget(self.textfield)

score_str = ['Very Weak', 'Weak', 'Average', 'Good', 'Strong']
class PasswordEntry(MDBoxLayout):
  def value(self):
    return self.textfield.text
  
  def check_password(self, password: str):
    if not password: return
    out = zxcvbn.zxcvbn(password)
    score = out['score']
    tips = ''.join(out['feedback']['suggestions'][:1])
    self.pwd_str.text = score_str[score]
    self.tips_label.text = tips
  
  def generate_pwd(self):
    newpwd = secrets.token_urlsafe(15)
    self.textfield.text = newpwd
    self.check_password(newpwd)
  
  def __init__(self, **kwargs):
    label: str = kwargs.pop('label', '')
    id_: str = kwargs.pop('id', '')
    default: str = kwargs.pop('default', '')
    
    self.orientation = 'vertical'
    self.spacing = dp(10)
    self.id=id_
    super().__init__(**kwargs)
    
    self.label = MDLabel(
      text=label,
      halign='center',
      size_hint=(0.5, 1),
    )
    
    self.pwd_generate = MDFillRoundFlatButton(
      text='generate password',
      on_release=lambda _: self.generate_pwd()
    )
    
    self.verify_password =MDFillRoundFlatButton(
      text='validate password',
      on_release=lambda _: self.check_password(self.textfield.text)
    )
    
    self.pwd_str_label = MDLabel(
      text='password strength',
      halign='center',
      size_hint=(0.5, 1),
    )
    self.pwd_str = MDLabel(
      text='-',
      halign='center',
      size_hint=(0.5, 1),
    )
    self.tips_label = MDLabel(
      text='',
      halign='center',
      size_hint=(0.5, 1)
    )

    self.textfield = MDTextField(
      text=default,
      pos_hint={'center_x': 0.5, 'center_y': 0.5},
      on_text_validate=lambda x: self.check_password(x.text),
      mode='round',
      size_hint=(1, 0.7),
      height=dp(5)
    )
    
    self.add_widget(
      MDBoxLayout(
        self.label,
        self.textfield,
        orientation='horizontal'
      )
    )
    self.add_widget(
      MDBoxLayout(
        self.pwd_generate,
        self.verify_password,
        orientation='horizontal',
        spacing=dp(10),
      )
    )
    self.add_widget(
      MDBoxLayout(
        self.pwd_str_label,
        self.pwd_str,
        orientation='horizontal'
      )
    )
    self.add_widget(
      MDBoxLayout(
        self.tips_label
      )
    )
    
    if default:
      self.check_password(password=default)
