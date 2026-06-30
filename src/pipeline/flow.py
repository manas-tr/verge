from prefect import flow, task
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_SCRIPT = PROJECT_ROOT / "src" / "models" / "train_model.py"


@task(retries=1, retry_delay_seconds=10)
def run_training_script():
    if not TRAIN_SCRIPT.exists():
        raise FileNotFoundError(f"Training script not found: {TRAIN_SCRIPT}")

    result = subprocess.run(
        [sys.executable, str(TRAIN_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    print("\n--- TRAINING STDOUT ---\n")
    print(result.stdout)

    if result.stderr:
        print("\n--- TRAINING STDERR ---\n")
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Training script failed with exit code {result.returncode}")

    return "Training completed successfully"


@flow(name="verge_pipeline")
def training_pipeline():
    status = run_training_script()
    print(status)


if __name__ == "__main__":
    training_pipeline()
