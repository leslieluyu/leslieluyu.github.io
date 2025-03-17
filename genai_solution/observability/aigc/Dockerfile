FROM python:3.9-slim

# 安装依赖
RUN pip install prometheus-client requests

# 复制 exporter 脚本
COPY custom_exporter.py /app/custom_exporter.py

# 暴露端口
EXPOSE 8000

# 运行 exporter
CMD ["python", "/app/custom_exporter.py"]
