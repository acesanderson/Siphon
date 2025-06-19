from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(description="Siphon file to LLM context")
    parser.add_argument("file", type=str, help="Path to the file to convert")
    # parser.add_argument(
    #     "-l", "llm", action="store_true", help="Use LLM for conversion if applicable"
    # )
    args = parser.parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    try:
        context = retrieve_file_context(file_path)
        print(f"Converted context for {file_path}:")
        print(context)
    except Exception as e:
        print(f"Error converting file {file_path}: {e}")


if __name__ == "__main__":
    main()
