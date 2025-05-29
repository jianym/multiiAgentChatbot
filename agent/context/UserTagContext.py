import json
import time
from agent.model.SpacyModel import queryEnt
from common.RedisManager import r

user_tag_prefix = "agent_user_tag_"

def userTag(userId: str, query: str):
    userTags = []
    labels = queryEnt(query)
    if len(labels) > 0:
        for label in labels:
            label["time"] = int(time.time())
            userTags.append(label)

    historyUserTags = r.lrange(user_tag_prefix + userId, 0, -1)
    if historyUserTags:
        for historyUserTag in historyUserTags:
            userTags.append(json.loads(historyUserTag))

    if len(userTags) > 0:
        resultUserTags = []
        userTags = buildUserTag(userTags)
        userTags = compute(userTags)
        userTags = userTags[:49]
        r.delete(user_tag_prefix + userId)
        for userTag in userTags:
            r.rpush(user_tag_prefix + userId, json.dumps(userTag, ensure_ascii=False))
            resultUserTags.append(userTag["label"])
        return resultUserTags
    return userTags


def buildUserTag(userTags: list):
    # 用一个字典来记录每个 label 的累计 number

    unique_userTags = []
    # 遍历 userTags，处理重复的 label 并累加 number
    for userTag in userTags:
        label = userTag["label"]
        number = userTag["number"]

        # 检查是否在 unique_userTags 中找到该 label
        found = False
        for existing_tag in unique_userTags:
            if existing_tag["label"] == label:
                # 如果 label 已经存在，累加 number
                existing_tag["number"] += number
                found = True
                break

        # 如果没有找到 label，说明是第一次出现，加入 unique_userTags
        if not found:
            unique_userTags.append({"label": label,"time":userTag["time"], "number": number})

    return unique_userTags


def compute(userTags: list):
    userTagsByTime = sort(userTags, "time")
    userTagsByNumber = sort(userTags, "number")

    for i, userTag in enumerate(userTagsByTime, start=10):
        userTag["weight"] = i

    for i, userTag in enumerate(userTagsByNumber, start=10):
        userTag["weight"] = i

    for i, userTagByTime in enumerate(userTagsByTime, start=1):
        weight = int(userTagByTime["weight"] * 0.6)
        for userTagByNumer in userTagsByNumber:
            if userTagByNumer["label"] == userTagByTime["label"]:
                weight = weight + int(userTagByNumer["weight"] * 0.4)
                userTagByTime["weight"] = weight
                break
    return sorted(userTagsByTime, reverse=True, key=lambda x: x["weight"])

def sort(userTags: list,key: str):
    return sorted(userTags,key=lambda x: x[key])



