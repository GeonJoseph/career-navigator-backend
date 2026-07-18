import numpy as np


def cosine(a, b):
    """
    Compute cosine similarity between two vectors.
    Handles zero vectors safely.
    """

    denom = np.linalg.norm(a) * np.linalg.norm(b)

    if denom == 0:
        return 0.0

    return np.dot(a, b) / denom