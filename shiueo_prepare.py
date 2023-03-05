import subprocess

try:
    command = f"pip install Nuitka black zstandard ordered-set imageio"
    subprocess.run(command, shell=True)

    print("requirements.txt done")
except Exception as e:
    print(e)
