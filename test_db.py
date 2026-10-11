from db import find_experiment_by_id
def test_find_experiment_not_found():
    result = find_experiment_by_id(999)
    assert result is None


def test_find_experiment_found():
    result = find_experiment_by_id(1)
    assert result is not None
    assert result.id == 1