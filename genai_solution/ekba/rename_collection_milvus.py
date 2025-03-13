from pymilvus import MilvusClient

# Connect to Milvus
#client = MilvusClient(uri="http://10.105.169.68:19530", token="root:Milvus")
client = MilvusClient(uri="http://10.105.216.131:19530", token="root:Milvus")

# Rename the collection
client.rename_collection(old_name="intel_xeon6", new_name="Xeon6Docs")
#client.rename_collection(old_name="intel_product_new", new_name="IntelProducts")

