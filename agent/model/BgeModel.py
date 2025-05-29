from sentence_transformers import SentenceTransformer
import torch
import torch.nn.functional as F
# 加载 bge-m3 的嵌入模型

model = SentenceTransformer("BAAI/bge-m3")

class BgeModel:

    def getEmbedding(self,text: str):
        """计算文本的嵌入向量"""
        return model.encode(text, normalize_embeddings=True)

    def classify(self,text: str,labels: list):
        label_embs = torch.vstack([torch.from_numpy(self.getEmbedding(label)) for label in labels])
        text_emb = self.getEmbedding(text)
        cos_scores = F.cosine_similarity(torch.tensor(text_emb), label_embs)
        best_idx = torch.argmax(cos_scores).item()
        print(f"预测标签：{labels[best_idx]}，相似度：{cos_scores[best_idx].item():.4f}")

        return best_idx

bgeModel = BgeModel()
# # 分类标签
# labels = ["需要大模型回答这个问题", "模型不需要回答这个问题"]
# # 输入文本
# input_text = "今天天气怎么样"
# bgeModel.classify(input_text,labels)
