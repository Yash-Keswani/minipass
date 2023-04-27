from kivy.metrics import dp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from pyperclip import copy

from components.utils import alert
from components.wrappers import PGroup, PEntry

GROUP_TABLES = {}

def get_row_entry(row) -> PEntry:
  tbl = row.table.parent.parent
  entry = tbl.entries[row.index // len(tbl.column_data)]
  return entry

def copy_password(row):
  row.menu.dismiss()
  entry = get_row_entry(row)
  copy(entry.password)
  alert('password copied to clipboard')

def copy_username(row):
  row.menu.dismiss()
  entry = get_row_entry(row)
  copy(entry.username)
  alert('username copied to clipboard')

def copy_otp(row):
  row.menu.dismiss()
  entry = get_row_entry(row)
  copy(entry.otp)
  alert(f'otp {entry.otp} copied to clipboard')

def delete(row, tbl: MDDataTable):
  row.menu.dismiss()
  get_row_entry(row).delete()
  tbl.update_row_data(None,
                      [(entry.title, entry.username, '*' * len(entry.password))
                       for entry in tbl.group.entries]
                      )
  tbl.entries = tbl.group.entries
  alert('entry deleted successfully')

def group_to_table(group: PGroup, sm):
  tbl = CustomMDDataTable(
    size_hint=(0.9, 0.9),
    pos_hint={'center_x': 0.5, 'center_y': 0.5},
    column_data=[
      ('Website', dp(50)),
      ('Username', dp(50)),
      ('Password', dp(50)),
    ],
    row_data=[
      (entry.title, entry.username, '*'*len(entry.password))
      for entry in group.entries
    ],
    group=group,
    entries=group.entries,
    elevation=4,
    sm=sm,
    rows_num=3,
    use_pagination=True,
    background_color_selected_cell=[0, 0, 0, 0]
  )
  
  GROUP_TABLES[str(group)] = tbl
  return tbl

class CustomMDDataTable(MDDataTable):
  def __init__(self, **kwargs):
    from components.screens import CustomMDScreenManager
    self.sm: CustomMDScreenManager = kwargs.pop('sm')
    self.entries = kwargs.pop('entries')
    self.group = kwargs.pop('group', None)
    super().__init__(**kwargs)
  
  def on_row_press(self, row):
    def open_edit(row):
      from components.screens import EditEntryScreen
      
      row.menu.dismiss()
      if str(hash(get_row_entry(row))) not in self.sm.screen_names:
        self.sm.add_widget(EditEntryScreen(entry=get_row_entry(row), sm=self.sm))
      self.sm.goto(str(hash(get_row_entry(row))))
    
    if row.last_touch.button == 'right':
      if not hasattr(row, 'menu'):
        menu_items = [
          {"text": "Copy OTP", "viewclass": "OneLineListItem",
           "on_release": lambda: copy_otp(row)},
          {"text": "Copy Password", "viewclass": "OneLineListItem",
           "on_release": lambda: copy_password(row)},
          {"text": "Copy Username", "viewclass": "OneLineListItem",
           "on_release": lambda: copy_username(row)},
          {"text": "Edit", "viewclass": "OneLineListItem",
           "on_release": lambda: open_edit(row)},
          {"text": "Delete", "viewclass": "OneLineListItem",
           "on_release": lambda: delete(row, self)},
        ]
        row.menu = MDDropdownMenu(
          caller=row,
          items=menu_items,
        )
      row.menu.open()
    
    return super().on_row_press(row)
