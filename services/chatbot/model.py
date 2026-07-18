try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    import numpy as np
    
    class MockSentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name
            print(f"[WARNING] sentence_transformers is not installed. Using MockSentenceTransformer for '{model_name}'.")

        def encode(self, text, normalize_embeddings=True):
            # Return a mock 768-dimensional vector based on the text hash
            h = hash(text)
            np.random.seed(h & 0xffffffff)
            vec = np.random.randn(768)
            if normalize_embeddings:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
            return vec

_model = None  # 🔥 cache


def load_model():
    global _model

    if _model is None:
        print("[INFO] Loading embedding model...")
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                _model = SentenceTransformer("BAAI/bge-base-en-v1.5")
            except Exception as e:
                print(f"[ERROR] Error loading SentenceTransformer: {e}. Falling back to mock model.")
                _model = MockSentenceTransformer("BAAI/bge-base-en-v1.5")
        else:
            _model = MockSentenceTransformer("BAAI/bge-base-en-v1.5")

    return _model