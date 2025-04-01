import asyncio


from pymilvus import MilvusClient, DataType
from pymilvus import utility

import spacy
# from agent.model.DeepseekModel import llm
# from agent.AgentRelation import AgentRelation
# from agent.AgentSimple import AgentSimple

# nlp = spacy.load("zh_core_web_trf")

client = MilvusClient(uri="./milvus_demo.db")

class KnowledgeMilvusDao:

    def createMilvus(self):
        if client.has_collection("knowledge_file"):
            return True

        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=False
        )

        # 2. Add fields to schema
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True,auto_id=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field(field_name="chat_no", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="user_id", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="file_path", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR,max_length=2048)
        schema.add_field(field_name="create_time", datatype=DataType.INT64)

        # schema.add_field(field_name="source_id", datatype=DataType.STRING, dim=5)

        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="L2"
        )

        # 为 `text` 字段创建倒排索引
        index_params.add_index(
            field_name="chat_no",
            index_type="INVERTED",  # 倒排索引
        )

        # 为 `text` 字段创建倒排索引
        index_params.add_index(
            field_name="user_id",
            index_type="INVERTED",  # 倒排索引
        )

        # 3. Create a collection
        client.create_collection(
            collection_name="knowledge_file",
            schema=schema,
            index_params=index_params
        )

    def insertMilvus(self,data: list):
        client.insert(collection_name="knowledge_file",data=data)

    def delete(self,ids: list):
        client.delete(collection_name="knowledge_file", ids=ids)
        client.compact(collection_name="knowledge_file")

    def search(self,query: list,chatNo: str,userId: str):
        # 定义过滤条件

        res = client.search(
            collection_name="knowledge_file",
            data=query,
            output_fields=["text"],
            search_params={"metric_type": "L2"},
            filter=f"chat_no == '{chatNo}' and user_id == '{userId}'",
            limit=10
        )
        return res

instance = KnowledgeMilvusDao()

