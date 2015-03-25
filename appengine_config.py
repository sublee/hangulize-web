import os
import sys
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
for dirname in (x for x in os.listdir(lib_path) if x != 'hangulize'):
    sys.path.insert(0, os.path.join(lib_path, dirname))
sys.path.insert(0, os.path.join(lib_path, 'hangulize'))
sys.path.insert(0, lib_path)
