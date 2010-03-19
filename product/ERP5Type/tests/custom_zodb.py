import os
import shutil
import sys
import glob
import ZODB
from ZODB.DemoStorage import DemoStorage
from ZODB.FileStorage import FileStorage
from Products.ERP5Type.tests.utils import getMySQLArguments

def _print(message):
  sys.stderr.write(message + "\n")

instance_home = os.environ.get('INSTANCE_HOME')
data_fs_path = os.environ.get('erp5_tests_data_fs_path',
                              os.path.join(instance_home, 'Data.fs'))
load = int(os.environ.get('erp5_load_data_fs', 0))
save = int(os.environ.get('erp5_save_data_fs', 0))

_print("Cleaning static files ... ")
static_dir_list = 'Constraint', 'Document', 'PropertySheet', 'Extensions'
for dir in static_dir_list:
  for f in glob.glob(os.path.join(instance_home, dir, '*')):
    os.remove(f)

if load:
  dump_sql = os.path.join(instance_home, 'dump.sql')
  if os.path.exists(dump_sql):
    _print("Restoring MySQL database ... ")
    ret = os.system("mysql %s < %s" % (getMySQLArguments(), dump_sql))
    assert not ret
  else:
    os.environ['erp5_tests_recreate_catalog'] = '1'
  _print("Restoring static files ... ")
  for dir in static_dir_list:
    full_path = os.path.join(instance_home, dir)
    if os.path.exists(full_path + '.bak'):
      os.rmdir(full_path)
      shutil.copytree(full_path + '.bak', full_path, symlinks=True)
elif save and os.path.exists(data_fs_path):
  os.remove(data_fs_path)

if save:
  Storage = FileStorage(data_fs_path)
elif load:
  Storage = DemoStorage(base=FileStorage(data_fs_path))
else:
  Storage = DemoStorage()

_print("Instance at %r loaded ... " % instance_home)
