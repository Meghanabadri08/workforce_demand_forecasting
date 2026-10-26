import json
import pandas as pd
from src.data_generator import generate
from src.validation import validate

def test_starter_generation(tmp_path):
    data_dir = tmp_path / "data"
    tables, gt = generate("starter", 20261022, data_dir)
    assert len(tables["employees"]) == 100
    assert len(tables["skills"]) == 20
    assert len(tables["projects"]) == 10
    assert len(gt) >= 3
    report = validate(data_dir)
    assert report["passed"]

def test_fixed_seed_reproducible(tmp_path):
    a, _ = generate("starter", 20261022, tmp_path/"a")
    b, _ = generate("starter", 20261022, tmp_path/"b")
    assert {k:len(v) for k,v in a.items()} == {k:len(v) for k,v in b.items()}
    for k in a:
        assert a[k].to_csv(index=False) == b[k].to_csv(index=False)
