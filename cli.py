import cmd

from pykeepass.exceptions import CredentialsError

from components.wrappers import PGroup, PManager, PEntry

class PMShell(cmd.Cmd):
  intro = 'CLI tool for MiniPass. Enter DB path and password to unlock.\n'
  base_prompt = '(MiniPass) '
  prompt = 'enter username - '
  file = None
  
  manager: PManager
  group: PGroup
  entry: PEntry
  
  # >> commands << #
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.kp = None
    self.password = None
    self.db_name = None
  
  def do_list_groups(self, _):
    print(self.kp.groups)

  def do_exit(self, _) -> bool:
    print('thank you for using MiniPass')
    self.close()
    return True
  
  # >> GROUP/ << #
  def do_get_entry(self, name):
    if not self.group:
      print('please select a group first')
      return
    self.entry = self.group.get_entry(name)
  
  def do_write_entry(self, title, username, password, otp):
    if not self.group:
      print('please select a group first')
      return
    self.group.add_entry(title, username, password, otp)
  # >> /GROUP << #
  
  # >> ENTRY/ << #
  def do_show_entry(self):
    e = self.entry
    print(e.title, e.username, e.password, e.otp)
  # >> /ENTRY << #
  
  def default(self, line):
    if not self.db_name:
      self.db_name, self.prompt = line, 'enter password'
    elif not self.password:
      self.password, self.prompt = line, ''
      self.login()

  def login(self):
    try:
      self.manager = PManager(self.db_name, self.password)
      print('login successful')
    except CredentialsError:
      print('invalid credentials')
    self.db_name, self.password = None, None
    self.prompt = '(MiniPass) '
    
  def do_log(self, arg):
    self.file = open(arg, 'w')
  
  def precmd(self, line) -> str:
    if self.file: print(line, file=self.file)
    return line
  
  def close(self):
    if self.file:
      self.file.close()
      self.file = None

if __name__ == '__main__':
  PMShell().cmdloop()
