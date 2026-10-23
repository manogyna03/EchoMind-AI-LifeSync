import sys, os
# Add the project root (two levels up) to PYTHONPATH so that top-level packages like 'app' can be imported.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
