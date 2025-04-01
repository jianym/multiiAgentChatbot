import numpy as np


# 计算余弦相似度
def cosineSimilarity(x, y):
    dot_product = np.dot(x, y)
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)
    return dot_product / (norm_x * norm_y)

# 计算点积
def dotProduct(x, y):
    return np.dot(x, y)

# 计算相似度
def computeSimilarity(x, y,similarityMeasure):

    if similarityMeasure == 'cosine':
        return cosineSimilarity(x, y)
    elif similarityMeasure == 'dot':
        return dotProduct(x, y)
    else:
        raise ValueError('Invalid similarity measure')