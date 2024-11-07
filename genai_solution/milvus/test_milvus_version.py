from pymilvus import connections, utility

# Connect to Milvus
connections.connect(host='172.21.139.37', port='19530')

# Get server version
version = utility.get_server_version()
print("Milvus Server Version:", version)
