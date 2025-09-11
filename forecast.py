"""Forecast next value in a series using linear regression without external deps.

This script builds a simple linear regression model via the normal equation
and predicts the next value of a series based on the last ``time_steps``
observations.

Usage:
    python forecast.py --series 1 2 3 4 5 6 --time_steps 3
"""

from __future__ import annotations

import argparse
from typing import List, Tuple


def create_dataset(series: List[float], time_steps: int) -> Tuple[List[List[float]], List[float]]:
    """Create feature windows and targets from the series."""
    X, y = [], []
    for i in range(len(series) - time_steps):
        X.append(series[i : i + time_steps])
        y.append(series[i + time_steps])
    return X, y


def transpose(matrix: List[List[float]]) -> List[List[float]]:
    return [list(row) for row in zip(*matrix)]


def matmul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    result = []
    for i in range(len(A)):
        row = []
        for j in range(len(B[0])):
            val = 0.0
            for k in range(len(B)):
                val += A[i][k] * B[k][j]
            row.append(val)
        result.append(row)
    return result


def matvec(A: List[List[float]], v: List[float]) -> List[float]:
    return [sum(a * b for a, b in zip(row, v)) for row in A]


def solve_system(A: List[List[float]], b: List[float]) -> List[float]:
    """Solve linear system Ax=b using Gaussian elimination."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    for k in range(n):
        # Pivot selection with partial pivoting
        max_row = max(range(k, n), key=lambda i: abs(M[i][k]))
        if abs(M[max_row][k]) < 1e-12:
            raise ValueError("Matrix is singular")
        if max_row != k:
            M[k], M[max_row] = M[max_row], M[k]
        pivot = M[k][k]
        # Normalize pivot row
        for j in range(k, n + 1):
            M[k][j] /= pivot
        # Eliminate below
        for i in range(k + 1, n):
            factor = M[i][k]
            for j in range(k, n + 1):
                M[i][j] -= factor * M[k][j]

    # Back substitution
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
    return x


def predict_next(series: List[float], time_steps: int) -> Tuple[List[float], float]:
    if len(series) <= time_steps:
        raise ValueError("Series must contain more elements than time_steps")

    X, y = create_dataset(series, time_steps)
    X = [[1.0] + row for row in X]  # Add intercept column
    Xt = transpose(X)
    XtX = matmul(Xt, X)
    XtY = matvec(Xt, y)
    theta = solve_system(XtX, XtY)

    last_seq = [1.0] + series[-time_steps:]
    forecast = sum(w * x for w, x in zip(theta, last_seq))
    return series[-time_steps:], forecast


def main() -> None:
    parser = argparse.ArgumentParser(description="Forecast next value using linear regression")
    parser.add_argument("--series", type=float, nargs="+", required=True, help="Series values")
    parser.add_argument("--time_steps", type=int, required=True, help="Number of time steps")
    args = parser.parse_args()

    last_seq, prediction = predict_next(args.series, args.time_steps)
    print("Последовательность:", last_seq)
    print("Прогноз следующего значения:", prediction)


if __name__ == "__main__":
    main()
