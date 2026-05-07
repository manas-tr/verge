import os
import pandas as pd

DATA_PATH = "data/raw/mit"


def list_files():
    print("\nFiles inside dataset:\n")
    for f in os.listdir(DATA_PATH):
        print(f)


def inspect_file(file_path):
    
    df = pd.read_csv(file_path)

    print("Shape:", df.shape)
    print("\nColumns:\n", df.columns.tolist())
    print("\nHead:\n", df.head())

    print("\nInfo:")
    print(df.info())


def main():
    files = [f for f in os.listdir(DATA_PATH) if f.endswith(".csv")]

    if not files:
        print("No CSV files found.")
        return

    list_files()


    for f in files[:2]:
        inspect_file(os.path.join(DATA_PATH, f))


if __name__ == "__main__":
    main()