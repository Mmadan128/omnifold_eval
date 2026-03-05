from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Union


def weighted_histogram(
    values: np.ndarray,
    weights: Optional[np.ndarray] = None,
    bins: Union[int, np.ndarray] = 50,
    range: Optional[tuple[float, float]] = None,
    normalize: bool = False,
    plot: bool = False,
    xlabel: str = "Observable",
    ylabel: Optional[str] = None,
    title: str = "Weighted Histogram",
    ax: Optional[plt.Axes] = None,
    color: str = "steelblue",
) -> dict[str, np.ndarray]:
    """Compute a weighted histogram and optionally plot it. Returns counts, edges, bin_centres, bin_widths."""
    values = np.asarray(values, dtype=float)

    if values.ndim != 1:
        raise ValueError("values must be 1-D")
    if len(values) == 0:
        raise ValueError("values must not be empty")

    if weights is None:
        weights = np.ones(len(values))
    weights = np.asarray(weights, dtype=float)

    if weights.ndim != 1:
        raise ValueError("weights must be 1-D")
    if len(values) != len(weights):
        raise ValueError(
            f"values and weights must have the same length, "
            f"got {len(values)} and {len(weights)}"
        )
    if np.any(weights < 0):
        raise ValueError("weights must be non-negative")

    counts, edges = np.histogram(values, bins=bins, range=range, weights=weights)
    bin_widths = np.diff(edges)
    bin_centres = edges[:-1] + bin_widths / 2

    if normalize:
        total = counts.sum()
        if total == 0:
            raise ValueError("Cannot normalize: total weighted count is zero")
        counts = counts / total

    if plot:
        own_fig = ax is None
        if own_fig:
            _, ax = plt.subplots(figsize=(8, 5))
        ax.bar(
            bin_centres,
            counts,
            width=bin_widths,
            align="center",
            color=color,
            edgecolor="black",
            linewidth=0.4,
        )
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel if ylabel is not None else ("Density" if normalize else "Counts"))
        ax.set_title(title)
        if own_fig:
            plt.tight_layout()
            plt.show()

    return {
        "counts": counts,
        "edges": edges,
        "bin_centres": bin_centres,
        "bin_widths": bin_widths,
    }


# Tests

# Edge cases tested: a zero weight event should disappear from the histogram,
#Negative weights are useless for our data analysis and they corrupt normalization.
# Mismatched array lengths would disrupt our pipeline when we insert new real data.
# Normalizing when all weights are zero would  produce None bins.
# Uniform weights should give the same result as passing no weights at all.

def test_no_weights_counts_sum_to_n():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    result = weighted_histogram(x, bins=4, range=(0.5, 4.5))
    assert result["counts"].sum() == 4.0


def test_uniform_weights_equal_no_weights():
    rng = np.random.default_rng(42)
    x = rng.uniform(0, 10, 500)
    r1 = weighted_histogram(x, bins=20, range=(0, 10))
    r2 = weighted_histogram(x, weights=np.ones(500), bins=20, range=(0, 10))
    np.testing.assert_array_equal(r1["counts"], r2["counts"])


def test_zero_weight_excludes_event():
    x = np.array([1.0, 2.0, 3.0])
    w = np.array([1.0, 0.0, 1.0])
    result = weighted_histogram(x, weights=w, bins=3, range=(0.5, 3.5))
    assert result["counts"][1] == 0.0


def test_weight_scaling_proportionality():
    x = np.array([1.0, 1.0, 2.0])
    r1 = weighted_histogram(x, bins=2, range=(0.5, 2.5))
    r2 = weighted_histogram(x, weights=np.full(3, 2.0), bins=2, range=(0.5, 2.5))
    np.testing.assert_array_almost_equal(r2["counts"], r1["counts"] * 2)


def test_normalize_sums_to_one():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 1000)
    w = rng.uniform(0.5, 1.5, 1000)
    result = weighted_histogram(x, weights=w, bins=40, normalize=True)
    assert abs(result["counts"].sum() - 1.0) < 1e-12


def test_bin_centres_are_midpoints():
    result = weighted_histogram(np.linspace(0, 10, 100), bins=5, range=(0, 10))
    np.testing.assert_array_almost_equal(result["bin_centres"], [1.0, 3.0, 5.0, 7.0, 9.0])


def test_out_of_range_events_excluded():
    x = np.array([1.0, 5.0, 9.0])
    result = weighted_histogram(x, bins=5, range=(2.0, 8.0))
    assert result["counts"].sum() == 1.0


def test_explicit_bin_edges():
    x = np.array([0.5, 1.5, 2.5])
    edges = np.array([0.0, 1.0, 2.0, 3.0])
    result = weighted_histogram(x, bins=edges)
    np.testing.assert_array_equal(result["counts"], [1.0, 1.0, 1.0])
    np.testing.assert_array_equal(result["edges"], edges)


def test_single_event():
    result = weighted_histogram(np.array([5.0]), weights=np.array([3.0]), bins=10, range=(0, 10))
    assert result["counts"].sum() == 3.0


def test_returns_expected_keys():
    result = weighted_histogram(np.arange(10.0), bins=5)
    assert set(result.keys()) == {"counts", "edges", "bin_centres", "bin_widths"}


def test_mismatched_lengths_raises():
    try:
        weighted_histogram(np.array([1.0, 2.0]), weights=np.array([1.0]))
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_negative_weights_raise():
    try:
        weighted_histogram(np.array([1.0, 2.0]), weights=np.array([1.0, -0.5]))
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_empty_values_raise():
    try:
        weighted_histogram(np.array([]))
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_normalize_all_zero_weights_raise():
    try:
        weighted_histogram(np.array([1.0, 2.0]), weights=np.array([0.0, 0.0]), normalize=True)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
