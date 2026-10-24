# 1) Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
#source .venv/bin/activate

# 2) Upgrade pip tooling
python -m pip install --upgrade pip setuptools wheel

# 3) Install OpenCV from PyPI (choose ONE)
#python -m pip install opencv-python          # main package (most users)
# or
python -m pip install opencv-contrib-python  # + extra modules (contrib)
# or
#python -m pip install opencv-python-headless # no GUI/backends (servers/CI)
# or
#python -m pip install opencv-contrib-python-headless # no GUI/backends with extra modules (servers/CI)