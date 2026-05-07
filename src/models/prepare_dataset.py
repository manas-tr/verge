import pandas as pd

DATA_PATH = "data/processed/merged_jobs.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    print("Loaded:", df.shape)
    return df


def clean_data(df):
    # Remove invalid durations
    df = df[df["job_duration_sec"] > 10]

    # Remove zero/negative energy
    df = df[df["energyconsumed_joules"] > 0]

    print("After cleaning:", df.shape)
    return df


def select_features(df):
    # Target
    y = df["energyconsumed_joules"]

    # Features
    features = [
        "cpus_req",
        "mem_req",
        "nodes_alloc",
        "priority",
        "timelimit",
        "job_duration_sec",
        "powerusage_watts_avg",
        "avgmemoryutilization_pct",
        "avgsmutilization_pct"
    ]

    X = df[features]

    print("\nFeatures used:", features)
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    return X, y


if __name__ == "__main__":
    df = load_data()
    df = clean_data(df)
    X, y = select_features(df)

    print("\nSample X:\n", X.head())
    print("\nSample y:\n", y.head())