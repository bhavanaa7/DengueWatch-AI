"""python -m scripts.train_models  — clean data, run walk-forward evaluation, save artifacts and reports."""
import time
from src.config import load_config
from src.data_loader import build_clean_dataset
from src.train import run_all


def main():
    cfg = load_config()
    df, rep = build_clean_dataset(cfg)
    print(f"Clean dataset: {len(df)} city-weeks; missing before preprocessing: {rep['missing_before']}")
    t0 = time.time()
    cv, ho, best = run_all(df, cfg)
    print(f"Done in {time.time() - t0:.0f}s. Reports in {cfg['paths']['reports_dir']}")


if __name__ == "__main__":
    main()
