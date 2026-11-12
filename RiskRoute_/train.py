from pathlib import Path

from src.data import save_dataset
from src.model import train_and_evaluate


ROOT = Path(__file__).resolve().parent


if __name__ == "__main__":
    data_path = ROOT / "data" / "logistics_deliveries.csv"
    data_path.parent.mkdir(exist_ok=True)
    save_dataset(str(data_path))
    metrics = train_and_evaluate(
        str(data_path),
        str(ROOT / "artifacts" / "delay_model.joblib"),
        str(ROOT / "artifacts" / "metrics.json"),
        str(ROOT / "artifacts" / "test_predictions.csv"),
    )
    print("Training complete")
    for name, value in metrics.items():
        print(f"{name}: {value}")
