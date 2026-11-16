"""Regenerate the finite inventory from the repository's editable ruglab install."""

import json
from pathlib import Path

from ruglab.sampler_comparison import (
    ComparisonUnavailable,
    base_pool,
    isometric_bases,
    isometric_equalities,
    isometric_order_extras,
    isometric_window_orders,
    power_groups,
)


def inventory():
    rows = []
    for size in (8, 16, 32, 64, 128):
        for group in power_groups(size):
            row = {"side": size, "group": str(group), "powers": list(group.powers)}
            try:
                entries, bases = base_pool(size, group, 4096)
                row.update(base_descriptions=len(bases), raw_partitions=len(entries))
                row["isometric_representative_powers"] = sorted({b.q for b in isometric_bases(size, group, 4096)})
                row["isometric_equalities"] = len(isometric_equalities(size, group, 4096))
                for name, operation in (
                    (
                        "isometric_extra_orders",
                        lambda size=size, group=group: isometric_order_extras(size, group, 4096, 50000),
                    ),
                    (
                        "isometric_window_orders",
                        lambda size=size, group=group: isometric_window_orders(size, group, 4096, (0, 1, 2), 50000),
                    ),
                ):
                    try:
                        row[name] = len(operation())
                    except ComparisonUnavailable as error:
                        row[name] = {"unavailable": str(error)}
            except ComparisonUnavailable as error:
                row["unavailable"] = str(error)
            rows.append(row)
    return {
        "limits": {"base_descriptions": 4096, "retained_grid_cells": 16000000, "isometry_tables": 50000},
        "groups": rows,
    }


if __name__ == "__main__":
    target = Path(__file__).with_name("results.json")
    target.write_text(json.dumps(inventory(), indent=2) + "\n")
    print(target)
