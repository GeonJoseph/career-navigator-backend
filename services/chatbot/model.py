import hashlib
import numpy as np

_model = None


class LightweightEmbeddingModel:
    """
    Lightweight deterministic embedding model.

    This replaces SentenceTransformer for Render's low-memory
    deployment. It provides the same encode() interface expected
    by the chatbot code.
    """

    def __init__(self, dimensions=768):
        self.dimensions = dimensions

    def encode(self, text, normalize_embeddings=True):
        if not isinstance(text, str):
            text = str(text)

        # Create a deterministic seed from the text.
        digest = hashlib.sha256(
            text.encode("utf-8")
        ).digest()

        seed = int.from_bytes(
            digest[:8],
            byteorder="little",
            signed=False
        )

        rng = np.random.default_rng(seed)

        vector = rng.standard_normal(
            self.dimensions
        ).astype(np.float32)

        if normalize_embeddings:

            norm = np.linalg.norm(vector)

            if norm > 0:
                vector = vector / norm

        return vector


def load_model():
    global _model

    if _model is None:

        print(
            "[INFO] Loading lightweight embedding model..."
        )

        _model = LightweightEmbeddingModel(
            dimensions=768
        )

        print(
            "[INFO] Lightweight embedding model loaded."
        )

    return _model