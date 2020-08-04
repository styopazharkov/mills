import sys
from cx_Freeze import setup, Executable 
  
base = None
if sys.platform == "win32":
      base = "Win32GUI"

target = Executable(
    script="NineMensMorris.py",
    base=base,
    icon="Z.ico"
    )

setup(name = "NineMensMorris" , 
      version = "0.1.9" , 
      description = "an AI for Nine Mens Morris" , 
      author="Stepan (Styopa) Zharkov",
      data_files = [('', ['README.txt'])],
      executables = [target])