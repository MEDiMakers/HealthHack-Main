import os

base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of app.py
reference_path = os.path.join(base_dir, "references")
ref_audio = os.path.join(reference_path, "audio/converted.wav")
ref_img = os.path.join(reference_path, "image/converted.png")

print(ref_img)
