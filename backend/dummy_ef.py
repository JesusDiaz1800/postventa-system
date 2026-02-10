from chromadb import Documents, EmbeddingFunction, Embeddings

class SimpleDummy(EmbeddingFunction):
    def __init__(self):
        pass
        
    def __call__(self, input: Documents) -> Embeddings:
        return [[0.0]*768 for _ in input]
        
    def name(self): 
        return "simple_dummy"
