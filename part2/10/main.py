import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

def compile_file(file_path: str):
    # Read input Jack file
    with open(file_path, "r") as f:
        jack_code = f.read()

    tokenizer = JackTokenizer(jack_code)
    compiler = CompilationEngine(tokenizer)
    compiler.compile_class()

    # Output file (replace .jack with .xml)
    output_path = file_path.replace(".jack", ".xml")
    with open(output_path, "w") as f:
        f.write(compiler.get_output())

    print(f"✅ Compiled: {os.path.basename(file_path)} → {os.path.basename(output_path)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file.jack>")
        return

    path = sys.argv[1]
    if not os.path.exists(path):
        print("❌ File not found:", path)
        return

    if os.path.isdir(path):
        # compile all .jack files in folder
        for filename in os.listdir(path):
            if filename.endswith(".jack"):
                compile_file(os.path.join(path, filename))
    else:
        compile_file(path)

if __name__ == "__main__":
    main()
