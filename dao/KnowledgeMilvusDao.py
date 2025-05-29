import asyncio


from pymilvus import MilvusClient, DataType,Function, FunctionType, AnnSearchRequest, RRFRanker

client = MilvusClient(
    uri="http://localhost:19530",
    token="root:Milvus"
)

class KnowledgeMilvusDao:

    def createMilvus(self):
        if client.has_collection("knowledge_file"):
            return True

        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=False
        )

        analyzer_params = {
            "type": "chinese",
        }

        # 2. Add fields to schema
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True,auto_id=True)
        schema.add_field(field_name="chat_no", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="user_id", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="file_path", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR,max_length=2048, enable_analyzer=True, analyzer_params=analyzer_params, enable_match=True)
        schema.add_field(field_name="sparse_bm25_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
        schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field(field_name="para", datatype=DataType.VARCHAR, max_length=8192)
        schema.add_field(field_name="uuid_str", datatype=DataType.VARCHAR, max_length=256)
        schema.add_field(field_name="create_time", datatype=DataType.INT64)


        # schema.add_field(field_name="source_id", datatype=DataType.STRING, dim=5)
        bm25_function = Function(
            name="bm25",
            function_type=FunctionType.BM25,
            input_field_names=["text"],
            output_field_names=["sparse_bm25_vector"],
        )
        schema.add_function(bm25_function)

        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="dense_vector",
            index_type="IVF_FLAT",
            metric_type="L2"
        )

        index_params.add_index(
            field_name="sparse_bm25_vector",
            index_name="sparse_bm25_index",
            index_type="SPARSE_WAND",
            metric_type="BM25"
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

    def search(self, query: str, query_embeddings: list, chatNo: str, userId: str, top_k=50, radius=0.8,offset=0):
        other_kwargs = {
            "offset": offset,
            # "group_by_field": "uuid_str",
            # "strict_group_size": True,
        }

        res = client.search(
            collection_name="knowledge_file",
            data=query_embeddings,
            output_fields=["text","para","uuid_str","file_path"],
            anns_field="dense_vector",
            search_params={
                "metric_type": "L2",
                "params": {
                    "nprobe": 4,
                    "radius": radius,
                    "range_filter": 0
                },
            },
            filter=f"chat_no == '{chatNo}' and user_id == '{userId}'",
            limit=top_k,
            **other_kwargs
        )
        return res

    def hybrid_search(self,query: str,query_embeddings: list,chatNo: str,userId: str,top_k=20,radius=0.8):
        # 定义过滤条件

        # res = client.search(
        #     collection_name="knowledge_file",
        #     data=query_embedding,
        #     output_fields=["text","para","uuid_str","file_path"],
        #     search_params={"metric_type": "L2"},
        #     filter=f"chat_no == '{chatNo}' and user_id == '{userId}'",
        #     limit=top_k
        # )
        # "radius": radius,
        # "range_filter": 0
        # Define the parameters for the dense vector search
        search_params_dense = {
            "metric_type": "L2",
            "params": {
                "nprobe": 4,
            }
        }
        filter = f"chat_no == '{chatNo}' and user_id == '{userId}'"
        # Create a dense vector search request
        request_dense = AnnSearchRequest(query_embeddings, "dense_vector", search_params_dense, limit=top_k,expr=filter)

        # Define the parameters for the BM25 text search
        search_params_bm25 = {
            "metric_type": "BM25",
            "params": {
            }
        }

        # Create a BM25 text search request
        request_bm25 = AnnSearchRequest([query], "sparse_bm25_vector", search_params_bm25, limit=top_k,expr=filter)

        # Combine the two requests
        reqs = [request_dense, request_bm25]

        # Initialize the RRF ranking algorithm
        ranker = RRFRanker(100)

        # "group_by_field": "uuid_str",
        # "strict_group_size": True,
        other_kwargs = {
            "offset": 0,
            "group_by_field": "uuid_str",
            "strict_group_size": True,
        }

        # Perform the hybrid search
        hybrid_search_res = client.hybrid_search(
            collection_name="knowledge_file",
            reqs=reqs,
            ranker=ranker,
            limit=top_k,
            output_fields=["text","para","uuid_str","file_path"],
            **other_kwargs
        )

        # Extract the context from hybrid search results
        # context = []
        # for hits in hybrid_search_res:  # Use the correct variable here
        #     for hit in hits:
        #         context.append({"text": hit['entity']['text']})
        #         context.append(hit['entity']['text'])  # Extract text content to the context list
        #         print(hit['entity']['text'])  # Output each retrieved document

        return hybrid_search_res



instance = KnowledgeMilvusDao()

