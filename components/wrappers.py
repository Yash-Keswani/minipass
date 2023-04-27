from pykeepass import PyKeePass, icons
from pykeepass.group import Group as _Group
from pykeepass.entry import Entry as _Entry

from components.utils import otpParse, otpGen

class PEntry():
  def __init__(self, entry: _Entry, group: 'PGroup'):
    self.X = entry
    self.group = group
  
  def delete(self):
    self.X.delete()
    self.group.manager.X.save()
    
  @classmethod
  def new(cls, group: 'PGroup', title: str = '', username: str = '', password: str = '', otp: str = '') -> 'PEntry':
    x = group.manager.X.add_entry(destination_group=group.X, title=title, username=username, password=password, otp=otp)
    group.manager.X.save()
    return cls(x, group)
    
  @property
  def username(self): return self.X.username
  
  @username.setter
  def username(self, username: str):
    self.X.username = username
    self.group.manager.X.save()

  @property
  def password(self): return self.X.password
  
  @password.setter
  def password(self, password: str):
    self.X.password = password
    self.group.manager.X.save()
  
  @property
  def title(self): return self.X.title
  
  @title.setter
  def title(self, title: str):
    self.X.title = title
    self.group.manager.X.save()

  @property
  def otp(self):
    return otpParse(self.X.otp)
  
  @otp.setter
  def otp(self, seed_or_url):
    if not seed_or_url.startswith('otpauth://'):
      self.X.otp = otpGen(seed_or_url)
    else: self.X.otp = seed_or_url
    self.group.manager.X.save()
  
  
class PGroup():
  manager: 'PManager' = None
  
  def __init__(self, group: _Group, manager: 'PManager'):
    self.X: _Group = group
    PGroup.manager = manager
    
  def delete(self):
    self.X.delete()
    self.manager.X.save()

  @classmethod
  def new(cls, name: str,):
    _grp = cls.manager.X.add_group(destination_group=cls.manager.X.root_group, group_name=name, icon=icons.FOLDER)
    cls.manager.X.save()
    return PGroup(_grp, cls.manager)
    
  @property
  def entries(self) -> list[PEntry]:
    return [PEntry(x, self) for x in self.X.entries]

  def add_entry(self, title: str, username: str, password: str, otp: str):
    self.manager.X.add_entry(destination_group=self.X, username=username,
                             password=password, otp=otp, title=title)
  
  def __str__(self):
    return self.X.name


class PManager():
  def __init__(self, db_name: str, pwd: str):
    self.X: PyKeePass = PyKeePass(db_name, pwd)
  
  def search(self, title: str) -> list[PEntry]:
    return [PEntry(entry, PGroup(entry.group, self)) for entry in self.X.find_entries_by_title(title)]
  
  @property
  def groups(self) -> dict[str, PGroup]:
    return {x.name: PGroup(x, self) for x in self.X.groups}

  def get_grp(self, group_name: str) -> PGroup:
    return self.groups[group_name]
  
  def add_grp(self, group_name: str) -> None:
    self.X.add_group(group_name=group_name, destination_group='')
