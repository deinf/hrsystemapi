import os

BASE_DIR_0_LVL = os.path.dirname(__file__)
BASE_DIR_1_LVL = os.path.dirname(os.path.dirname(__file__))
BASE_DIR_2_LVL = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def join_path(base_dir, path, file):
    return os.path.join(base_dir, path, file)