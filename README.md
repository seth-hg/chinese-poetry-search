# 古诗词搜索演示

一个使用 [Milvus](https://github.com/milvus-io/milvus) 向量数据库实现的唐诗搜索演示程序。

NLP 模型使用清华大学提供的[BERT-CCPoem](https://github.com/THUNLP-AIPoet/BERT-CCPoem)，运行本项目之前请先下载并解压到项目根目录。[这里](https://github.com/lonePatient/awesome-pretrained-chinese-nlp-models)还有很多其他的预训练模型可供参考。古诗词来自[这里](https://github.com/chinese-poetry/chinese-poetry)整理好的数据库。

**前置条件**

- Python 3.7 及以上版本
- Milvus，可以参考[文档](https://milvus.io/docs/v2.0.x/install_standalone-docker.md)进行快速部署。
- [可选] Attu，Milvus 的图形化前端，方便进行管理。部署方法见[这里](https://milvus.io/docs/v2.0.x/attu_install-docker.md)。

**运行项目**

1.  clone submodule

    ```
    git submodule update --init
    ```

2.  安装 Python 库

    ```
    pip3 install -r requirements.txt
    ```

3.  使用`generate.py`脚本对古诗词数据进行预处理。处理完后会在输出目录生成 3 个文件，`content.csv`包含了诗词的全部数据，`vectors.csv`包含了诗词的每个段落经过模型编码之后的向量数据，`vector2poem.csv`包含了向量 id 到诗词 id 和段落的映射关系。

    ```
    ./generate.py -i ./chinese-poetry/quan_tang_shi/json -o out
    ```

4.  使用 sqlite3 创建数据库和表，并导入`content.csv`和`vector2poem.csv`。

    ```
    sqlite3 poetry.db

    sqlite> CREATE TABLE poetry(id INT PRIMARY KEY NOT NULL, content TEXT);
    sqlite> CREATE TABLE vector2poem(id INT PRIMARY KEY NOT NULL, poem INT NOT NULL, paragraph INT NOT NULL);
    sqlite> .mode csv
    sqlite> .import --skip 1 out/content.csv poetry
    sqlite> .import --skip 1 out/vector2poem.csv vector2poem
    ```

5.  在 Milvus 中创建名为`poetry`的 collection 并导入向量数据。导入数据可以通过 Attu 进行。注意 Milvus 导入的 csv 文件不能超过 150MB，如果`vectors.csv`文件过大，可以用 split 命令切分成小文件分多次导入。Collection 的信息如下。

    ```
    +---------------+-----------------------------------+
    | Name          | poetry                            |
    +---------------+-----------------------------------+
    | Description   |                                   |
    +---------------+-----------------------------------+
    | Is Empty      | False                             |
    +---------------+-----------------------------------+
    | Entities      | 125504                            |
    +---------------+-----------------------------------+
    | Primary Field | id                                |
    +---------------+-----------------------------------+
    | Schema        | Description:                      |
    |               |                                   |
    |               | Auto ID: False                    |
    |               |                                   |
    |               | Fields(* is the primary field):   |
    |               |  - *id INT64                      |
    |               |  - feature FLOAT_VECTOR dim: 512  |
    +---------------+-----------------------------------+
    | Partitions    | - _default                        |
    +---------------+-----------------------------------+
    | Indexes       | - feature                         |
    +---------------+-----------------------------------+
    ```

6.  建立向量索引并加载 collection。索引参数可以参考下面。索引建好之后要通过 Attu 或者 milvus_cli 的 load 命令加载 collection，之后才能进行查询。

    ```
    +--------------------------+----------------------+
    | Corresponding Collection | poetry               |
    +--------------------------+----------------------+
    | Corresponding Field      | feature              |
    +--------------------------+----------------------+
    | Index Type               | HNSW                 |
    +--------------------------+----------------------+
    | Metric Type              | L2                   |
    +--------------------------+----------------------+
    | Params                   | M: 16                |
    |                          | - efConstruction: 32 |
    +--------------------------+----------------------+
    ```

7.  运行`query.py`进行命令行查询。

    ```
    ./query.py --milvus_host [Milvus服务地址] --milvus_port [Milvus服务端口] -c poetry -q [查询关键词]
    ```

8.  运行`svr.py`启动服务，之后可以在浏览器中打开 http://localhost:8080 进行查询。

    ```
    ./svr.py --milvus_host [Milvus服务地址] --milvus_port [Milvus服务端口] -c poetry
    ```
