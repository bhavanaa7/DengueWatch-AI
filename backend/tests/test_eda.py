from src.eda import generate_all
from tests.helpers import small_cfg, synthetic


def test_eda_generates_plots_from_synthetic_data(tmp_path):
    cfg = small_cfg()
    index = generate_all(synthetic(150), cfg, outdir=tmp_path)
    assert len(index) >= 6
    assert all((tmp_path / p["file"].split("/")[-1]).exists() for p in index)
    assert (tmp_path / "index.json").exists()
