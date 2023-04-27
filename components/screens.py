from functools import partial

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFlatButton, MDFillRoundFlatButton, \
  MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.snackbar import Snackbar, MDSnackbar
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar, MDActionBottomAppBarButton
from kivymd.uix.transition import MDSwapTransition

from components.forms import FormEntry, PasswordEntry
from components.tables import group_to_table, GROUP_TABLES, CustomMDDataTable
from components.utils import otpGen, alert
from components.wrappers import PEntry, PGroup

class GroupTab(MDFloatLayout, MDTabsBase):
  def __init__(self, *args, **kwargs):
    self.group = kwargs.pop('group')
    super().__init__(*args, **kwargs)

class CustomMDTabs(MDTabs):
  @property
  def tabs(self):
    return [x.children[0] for x in self.children[1].children[0].children]
  
class CustomMDScreenManager(MDScreenManager):
  def goto(self, screen: str) -> None:
    self.call_stack.append(self.current)
    self.current = screen
  
  def go_back(self) -> None:
    self.current = self.call_stack.pop()
    
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.call_stack = []
    self.transition = MDSwapTransition(duration=0.5)

class GroupForm(MDBoxLayout):
  def __init__(self, screen):
    self.screen = screen
    super().__init__(
      FormEntry(id='name', label='groupname', default='Temporary', size_hint=(1, 0.2)),
      orientation='vertical',
      padding=dp(10),
      size_hint=(1, 0.65),
      pos_hint={'center_x': 0.5, 'center_y': 0.5},
    )
  
  def submit(self):
    name = self.ids.name.value()
    self.screen.sm.home_screen.add_group(name)
    self.screen.sm.go_back()

class EntryForm(MDBoxLayout):
  def __init__(self, screen, entry: PEntry = None, group: PGroup = None):
    self.entry = entry
    self.group = group
    if entry is None:
      title, username, password, otp = '', '', '', ''
    else:
      title, username, password, otp = entry.title, entry.username, entry.password, entry.otp
    self.screen = screen
    self.pwd = PasswordEntry(id='password', label='password', default=password, size_hint=(1, 0.6))
    super().__init__(
      FormEntry(id='title', label='title', default=title, size_hint=(1, 0.15)),
      FormEntry(id='username', label='username', default=username, size_hint=(1, 0.15)),
      FormEntry(id='otp', label='otp seed / url', default='', size_hint=(1, 0.15)),
      self.pwd,
      orientation='vertical',
      padding=dp(10),
      size_hint=(1, 0.65),
      pos_hint={'center_x': 0.5, 'center_y': 0.5},
    )
    
  def submit(self):
    title = self.ids.title.value()
    username = self.ids.username.value()
    password = self.ids.password.value()
    otp = self.ids.otp.value()
    if not otp.startswith('otpauth://'):
      otp = otpGen(otp)
    
    if self.entry is None:
      # entry may already exist
      self.entry = PEntry.new(self.group, title=title, username=username, password=password, otp=otpGen(otp))
    else:
      self.entry.title = title
      self.entry.username = username
      self.entry.password = password
      
      if otp: self.entry.otp = otp
    
    alert(f'entry {title} edited successfully.')
    self.screen.sm.home_screen.reset_group(self.entry.group)
    self.screen.sm.go_back()


class NewGroupScreen(MDScreen):
  def __init__(self, **kwargs):
    self.sm: CustomMDScreenManager = kwargs.pop('sm')
    
    self.name = 'new_group'
    super().__init__(**kwargs)
    
    form = GroupForm(self)
    
    self.add_widget(
      MDCard(
        MDTopAppBar(
          right_action_items=[
            ['close-box', lambda _: self.sm.go_back(), 'Close', 'Close'],
          ],
          title="Add Group", type_height='small'
        ),
        MDBoxLayout(
          form,
          MDFillRoundFlatIconButton(icon='content-save', text='save', halign='center',
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    on_release=lambda x: form.submit()),
          size_hint=(1, 0.3),
          pos_hint={'center_x': 0.5, 'center_y': 0.5},
          orientation='vertical',
          padding=dp(20)
        ),
        orientation='vertical',
        size_hint=(0.5, 0.6),
        elevation=4,
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
      ),
    )

class EditEntryScreen(MDScreen):
  def __init__(self, **kwargs):
    try:
      entry: PEntry | None = kwargs.pop('entry')
      grp = entry.group
    except KeyError:
      entry = None
      grp = kwargs.pop('group')
    self.sm: CustomMDScreenManager = kwargs.pop('sm')
    
    self.name = str(hash(entry))
    super().__init__(**kwargs)
    form = EntryForm(self, entry=entry, group=grp)
    
    self.add_widget(
      MDCard(
        MDTopAppBar(
          right_action_items=[
            ['close-box', lambda _: self.sm.go_back(), 'Close', 'Close'],
          ],
          title="Edit Entry", type_height='small'
        ),
        MDBoxLayout(
          form,
          MDFillRoundFlatIconButton(icon='content-save', text='save', halign='center',
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    on_release=lambda x: form.submit()),
          size_hint=(1, 0.3),
          pos_hint={'center_x': 0.5, 'center_y': 0.5},
          orientation='vertical',
          padding=dp(20)
        ),
        orientation='vertical',
        size_hint=(0.4, 0.9),
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
        elevation=4,
      ),
    )

  
class HomeScreen(MDScreen):
  def theme_switch(self):
    theme_styles = ('Light', 'Dark')
    self.sm.app.theme_cls.theme_style = theme_styles[1 - theme_styles.index(self.sm.app.theme_cls.theme_style)]
  
  def __init__(self, **kwargs):
    groups = kwargs.pop('groups')
    self.sm: CustomMDScreenManager = kwargs.pop('sm')
    
    super().__init__(**kwargs)
    self.name='home'
    self.tabs = CustomMDTabs(id="tabs")
    self.add_widget(MDBoxLayout(
      MDTopAppBar(title="MiniPass", type_height='small'),
      self.tabs,
      MDBottomAppBar(size_hint=(1, 0.5), icon_color="#cccccc", action_items=[
        MDActionBottomAppBarButton(icon="lock", icon_size='30dp', pos_hint={'center_y': 0.5},
                                   on_release=lambda _: self.sm.goto('splash')),
        MDActionBottomAppBarButton(icon="magnify", icon_size='30dp',
                                   on_release=lambda _: self.sm.goto('search'),
                                   pos_hint={'center_y': 0.5}),
        MDActionBottomAppBarButton(icon="brightness-6", on_release=lambda _: self.theme_switch(),
                                   icon_size='30dp', pos_hint={'center_y': 0.5}),
      ]),
      orientation="vertical",
    ))
    
    for group in groups:
      self._render_tab(group)
  
  def add_group(self, grp: str):
    new_group = PGroup.new(grp)
    self._render_tab(new_group)
    alert(f'group {grp} added successfully')

  def delete_group(self, grp: PGroup, tab: GroupTab):
    self.tabs.remove_widget(tab)
    grp.delete()
    alert(f'group {grp.X.name} deleted successfully')

  def _render_tab(self, grp):
    def get_create_goto_addscreen(group: PGroup, *_, **__):
      if str(hash(None)) in self.sm.screen_names:
        self.sm.screens[self.sm.screen_names.index(str(hash(None)))] = EditEntryScreen(
          sm=self.sm,
          group=group
        )
      else:
        self.sm.add_widget(EditEntryScreen(sm=self.sm, group=group))
      self.sm.goto(str(hash(None)))
    
    action_buttons = MDBoxLayout(
      MDRaisedButton(text='new entry', on_release=partial(get_create_goto_addscreen, grp),
                    pos_hint={'center_x': 0.5}),
      MDRaisedButton(text='new group',
                   on_release=lambda _: self.sm.goto('new_group')),
      size_hint=(0.9, 0.2),
      spacing=dp(10)
    )
    
    tab = GroupTab(
      MDBoxLayout(
        group_to_table(grp, self.sm),
        action_buttons,
        orientation='vertical',
        padding=dp(20),
      ),
      group=grp,
      title=str(grp),
    )
    
    action_buttons.add_widget(MDRaisedButton(text='delete group',
                                           on_release=lambda _: self.delete_group(grp, tab)))
    
    self.tabs.add_widget(
      tab
    )
    
  def reset_group(self, grp: PGroup):
    # could just update one entry at a time
    tbl = GROUP_TABLES[str(grp)]
    tbl.entries = grp.entries
    tbl.update_row_data(None,
      [(entry.title, entry.username, '*' * len(entry.password))
       for entry in grp.entries]
    )
    
class SearchScreen(MDScreen):
  def search(self):
    from app import manager
    self._render_tab(manager.search(self.search_field.text))
    
  def __init__(self, **kwargs):
    self.sm: CustomMDScreenManager = kwargs.pop('sm')
    
    super().__init__(**kwargs)
    self.name = 'search'
    self.search_field = MDTextField(helper_text='title', size_hint=(0.3, None), mode='round')
    self.layout = MDBoxLayout(
      MDBoxLayout(self.search_field,
                  MDRaisedButton(text='search', on_release=lambda _: self.search(), size_hint=(0.1, None)),
                  orientation='horizontal', spacing=dp(15), padding=dp(20), size_hint=(1, 0.2)),
      orientation='vertical',
      spacing=dp(15),
      padding=dp(20)
    )
    self._render_tab([])
    self.add_widget(MDCard(
      MDTopAppBar(title='Search', right_action_items=[
        ['close-box', lambda _: self.sm.go_back(), 'Close', 'Close']
      ]
      ),
      self.layout,
      orientation="vertical",
      size_hint=(0.9, 0.9),
      pos_hint={'center_x': 0.5, 'center_y': 0.5},
    ))
    self.layout.add_widget(self.tbl)

  def _render_tab(self, entries: list[PEntry]):
    if not hasattr(self, 'tbl'):
      self.tbl = CustomMDDataTable(
        size_hint=(0.9, 0.9),
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
        column_data=[
          ('Website', dp(50)),
          ('Username', dp(50)),
          ('Password', dp(50)),
        ],
        row_data=[
          (entry.title, entry.username, '*'*len(entry.password))
          for entry in entries
        ],
        entries=entries,
        elevation=4,
        sm=self.sm,
        rows_num=3,
        use_pagination=True,
        background_color_selected_cell=[0, 0, 0, 0]
      )
    self.tbl.update_row_data(None,
      [(entry.title, entry.username, '*' * len(entry.password)) for entry in entries]
    )
    self.tbl.entries = entries
