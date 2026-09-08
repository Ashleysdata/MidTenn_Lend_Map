import numpy as np
import psycopg2

# 读取现有的npz数据
data = np.load('knowledge_base.npz', allow_pickle=True)
chunks = data['chunks']
sources = data['sources']
embeddings = data['embeddings']

# 连接pgvector容器
conn = psycopg2.connect(
    host='localhost',
    port=5435,
    dbname='postgres',
    user='postgres',
    password='yourpassword'
)
cur = conn.cursor()

# 逐条插入
for chunk, source, embedding in zip(chunks, sources, embeddings):
    # pgvector的Python驱动接受list或字符串形式的向量，这里转成list
    embedding_list = embedding.tolist()
    cur.execute(
        "INSERT INTO knowledge_chunks (chunk_text, source, embedding) VALUES (%s, %s, %s)",
        (str(chunk), str(source), embedding_list)
    )

conn.commit()
cur.close()
conn.close()

print(f"迁移完成，共插入 {len(chunks)} 条记录")