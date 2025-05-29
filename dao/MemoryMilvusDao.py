from pymilvus import MilvusClient, DataType


client = MilvusClient(uri="./milvus_memory_conversation.db")

class KnowledgeMilvusDao:

    def create_milvus(self):
        if client.has_collection("memory_conversation"):
            return True

        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=False
        )

        # 2. Add fields to schema
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True,auto_id=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field(field_name="user_id", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="chat_no", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR,max_length=1024)
        schema.add_field(field_name="context_info", datatype=DataType.VARCHAR, max_length=4096)
        schema.add_field(field_name="chat_time", datatype=DataType.INT64)
        schema.add_field(field_name="create_time", datatype=DataType.INT64)

        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="L2"
        )

        index_params.add_index(
            field_name="user_id",
            index_type="INVERTED",  # 倒排索引
        )

        index_params.add_index(
            field_name="chat_no",
            index_type="INVERTED",  # 倒排索引
        )

        # 3. Create a collection
        client.create_collection(
            collection_name="memory_conversation",
            schema=schema,
            index_params=index_params
        )

    def insert_milvus(self,data: list):
        client.insert(collection_name="memory_conversation",data=data)

    def delete(self,ids: list):
        client.delete(collection_name="memory_conversation", ids=ids)
        client.compact(collection_name="memory_conversation")

    def search(self,query: list,userId: str, limit=10):
        # 定义过滤条件

        res = client.search(
            collection_name="memory_conversation",
            data=query,
            output_fields=["text"],
            search_params={"metric_type": "L2"},
            filter=f"user_id == '{userId}'",
            limit=limit
        )
        return res

instance = KnowledgeMilvusDao()

