# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import pytest
import numpy as np
from pairtools.lib import stats
import yaml
from io import StringIO
import copy

testdir = os.path.dirname(os.path.realpath(__file__))


def test_mock_pairsam():
    mock_pairsam_path = os.path.join(testdir, "data", "mock.4stats.pairs")
    try:
        result = subprocess.check_output(
            ["python", "-m", "pairtools", "stats", "--yaml", mock_pairsam_path],
        ).decode("ascii")
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(sys.exc_info())
        raise e

    stats = yaml.safe_load(result)

    # for k in stats["no_filter"]:
    #     try:
    #         stats["no_filter"][k] = int(stats["no_filter"][k])
    #     except (ValueError, TypeError):
    #         stats["no_filter"][k] = float(stats["no_filter"][k])

    assert stats["no_filter"]["total"] == 9
    assert stats["no_filter"]["total_single_sided_mapped"] == 2
    assert stats["no_filter"]["total_mapped"] == 6
    assert stats["no_filter"]["total_dups"] == 1
    assert stats["no_filter"]["cis"] == 3
    assert stats["no_filter"]["trans"] == 2
    assert stats["no_filter"]["pair_types"]["UU"] == 4
    assert stats["no_filter"]["pair_types"]["NU"] == 1
    assert stats["no_filter"]["pair_types"]["WW"] == 1
    assert stats["no_filter"]["pair_types"]["UR"] == 1
    assert stats["no_filter"]["pair_types"]["MU"] == 1
    assert stats["no_filter"]["pair_types"]["DD"] == 1
    assert stats["no_filter"]["chrom_freq"]["chr1/chr2"] == 1
    assert stats["no_filter"]["chrom_freq"]["chr1/chr1"] == 3
    assert stats["no_filter"]["chrom_freq"]["chr2/chr3"] == 1
    for orientation in ("++", "+-", "-+", "--"):
        s = stats["no_filter"]["dist_freq"][orientation]
        for k, val in s.items():
            if orientation == "++" and k in [1, 2, 32]:
                assert s[k] == 1
            else:
                assert s[k] == 0

    assert stats["no_filter"]["summary"]["frac_cis"] == 0.6
    assert stats["no_filter"]["summary"]["frac_cis_1kb+"] == 0
    assert stats["no_filter"]["summary"]["frac_cis_2kb+"] == 0
    assert stats["no_filter"]["summary"]["frac_cis_4kb+"] == 0
    assert stats["no_filter"]["summary"]["frac_cis_10kb+"] == 0
    assert stats["no_filter"]["summary"]["frac_cis_20kb+"] == 0
    assert stats["no_filter"]["summary"]["frac_cis_40kb+"] == 0
    assert np.isclose(stats["no_filter"]["summary"]["frac_dups"], 1 / 6)


def test_read_stats():
    mock_pairsam_path = os.path.join(testdir, "data", "mock.4stats.pairs")
    try:
        result = subprocess.check_output(
            [
                "python",
                "-m",
                "pairtools",
                "stats",
                "--with-chromsizes",
                mock_pairsam_path,
            ],
        ).decode("ascii")
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(sys.exc_info())
        raise e
    f = StringIO(result)
    counter = stats.PairCounter().from_file(f)
    counter_doubled = counter + counter
    assert len(counter_doubled._stat["no_filter"]["chromsizes"]) == 3
    counter_wrong_copy = copy.deepcopy(counter)
    counter_wrong_copy._stat["no_filter"]["chromsizes"]["chr3"] = 101
    with pytest.raises(ValueError):
        counter_sum = counter + counter_wrong_copy
    counter_missingchromsizes_copy = copy.deepcopy(counter)
    counter_missingchromsizes_copy._stat["no_filter"]["chromsizes"] = {}
    with pytest.warns():
        counter_sum = counter + counter_missingchromsizes_copy
