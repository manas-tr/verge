import pandas as pd

DCGM_PATH = "data/raw/mit/dcgm.csv"
SCHED_PATH = "data/raw/mit/scheduler_data.csv"

OUTPUT_PATH = "data/processed/merged_jobs.csv"


def load_data():
    dcgm = pd.read_csv(DCGM_PATH)
    sched = pd.read_csv(SCHED_PATH)

    print("DCGM shape:", dcgm.shape)
    print("Scheduler shape:", sched.shape)

    return dcgm, sched


def merge_data(dcgm, sched):
    df = pd.merge(dcgm, sched, on="id_job", how="inner")

    print("\nMerged shape:", df.shape)
    return df


def basic_cleaning(df):
    # Convert timestamps to datetime
    df["time_submit"] = pd.to_datetime(df["time_submit"], unit="s")
    df["time_start"] = pd.to_datetime(df["time_start"], unit="s")
    df["time_end"] = pd.to_datetime(df["time_end"], unit="s")

    # Create duration feature
    df["job_duration_sec"] = (df["time_end"] - df["time_start"]).dt.total_seconds()

    # Drop useless columns for now
    drop_cols = [
        "nodelist",
        "constraints",
        "flags",
        "gres_used",  # empty anyway
        "kill_requid"
    ]

    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    return df


def save_data(df):
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved merged dataset to {OUTPUT_PATH}")


if __name__ == "__main__":
    dcgm, sched = load_data()
    df = merge_data(dcgm, sched)
    df = basic_cleaning(df)

    print("\nFinal columns:\n", df.columns.tolist())
    print("\nSample:\n", df.head())

    save_data(df)