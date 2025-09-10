# find libs path
import customtkinter
import google.generativeai as genai
import os

libs_to_find_path = ["customtkinter","genai"]

for lib in libs_to_find_path:
    print(f"Path for {lib}:")
    print(os.path.dirname(customtkinter.__file__))
    print("=" * 100)