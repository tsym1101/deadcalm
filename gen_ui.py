import os
import subprocess

# Get the directory of the script (where .ui files are located)
script_dir = os.path.dirname(os.path.abspath(__file__)) + '/client/ui'

# Loop through all .ui files in the directory
for filename in os.listdir(script_dir):
    if filename.endswith(".ui"):
        input_file = os.path.join(script_dir, filename)
        output_file = os.path.join(script_dir, f"ui_{os.path.splitext(filename)[0]}.py")

        # Convert the .ui file to .py using pyside2-uic
        try:
            subprocess.run(
                ["pyside2-uic", input_file, "-o", output_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Converted: {filename} -> {os.path.basename(output_file)}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting {filename}: {e.stderr}")


# try:
#     subprocess.run(
#         ["pyside2-rcc", 'gui_resources.qrc', "-o", 'gui_resources_rc.py'],
#         check=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )
#     print(f"pyside2-rcc finished")
# except subprocess.CalledProcessError as e:
#     print(f"Error pyside2-rcc failed: {e.stderr}")

print("All .ui files have been processed.")
