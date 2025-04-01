from sentence_transformers import SentenceTransformer

# 加载 bge-m3 的嵌入模型

model = SentenceTransformer("BAAI/bge-m3")

class BgeModel:

    def getEmbedding(self,text: str):
        """计算文本的嵌入向量"""
        return model.encode(text, normalize_embeddings=True)

bgeModel = BgeModel()