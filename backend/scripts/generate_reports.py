"""python -m scripts.generate_reports  — EDA plots (needs data) and evaluation figures (needs trained reports)."""
from src.config import load_config
from src.data_loader import build_clean_dataset
from src.eda import generate_all as eda_all
from src.visualization import generate_all as eval_all


def main():
    cfg = load_config()
    df, _ = build_clean_dataset(cfg)
    eda = eda_all(df, cfg)
    print(f"EDA: {len(eda)} plots in {cfg['paths']['reports_dir'] / 'eda'}")
    ev = eval_all(cfg)
    print(f"Evaluation figures: {len(ev)}" if ev else "Evaluation figures skipped: run python -m scripts.train_models first.")


if __name__ == "__main__":
    main()
