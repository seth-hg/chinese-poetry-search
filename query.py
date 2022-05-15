#!/usr/bin/env python3

import argparse
import json
import sqlite3

from pymilvus import connections
from pymilvus import Collection

import embedding


class VdbClient:

    def __init__(self, host, port, collection):
        connections.connect(alias="default", host=host, port=port)
        self.collection = Collection(collection)

    def query(self, column, v, n):
        search_params = {"metric_type": "L2", "params": {"ef": 32}}
        results = self.collection.search(data=[v],
                                         anns_field=column,
                                         param=search_params,
                                         limit=n,
                                         expr=None,
                                         consistency_level="Strong")
        return (results[0].ids, results[0].distances)

    def close(self):
        pass


class RdbClient:

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def query(self, ids):
        conn = sqlite3.connect(self.endpoint)
        c = conn.cursor()
        cursor = c.execute(
            "SELECT vector2poem.id AS vid, poetry.id AS pid, "
            "poetry.content AS poem, vector2poem.paragraph AS paragraph "
            "FROM vector2poem,poetry "
            "WHERE vector2poem.id in (%s) AND vector2poem.poem=poetry.id;" %
            ",".join([str(x) for x in ids]))
        data = []
        for row in cursor:
            data.append({
                "vid": row[0],
                "pid": row[1],
                "content": json.loads(row[2]),
                "paragraph": row[3]
            })
        conn.close()
        return data

    def close(self):
        pass


def query(vdb, db, q):
    ids, scores = vdb.query("feature", q, 5)
    poem = db.query(ids)

    for idx, _ in enumerate(poem):
        poem[idx]["score"] = scores[idx]

    return poem


def build_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m",
                        "--model",
                        help="path to model",
                        type=str,
                        default="./BERT_CCPoem_v1")
    parser.add_argument("--milvus_host",
                        help="milvus host",
                        type=str,
                        default="localhost")
    parser.add_argument("--milvus_port",
                        help="milvus port",
                        type=str,
                        default="19530")
    parser.add_argument("-c",
                        "--collection",
                        help="milvus collection",
                        type=str,
                        default="poetry")
    parser.add_argument("-d",
                        "--db",
                        help="sqlite db",
                        type=str,
                        default="poetry.db")
    return parser


if __name__ == '__main__':
    parser = build_arg_parser()
    parser.add_argument("-q",
                        "--query",
                        help="keyword to query",
                        type=str,
                        default="也无风雨也无晴")

    args = parser.parse_args()

    model, formatter = embedding.init(args.model)
    qv = embedding.predict_vec_rep([args.query], model, formatter)[0]

    vdb = VdbClient(args.milvus_host, args.milvus_port, args.collection)
    db = RdbClient(args.db)

    result = query(vdb, db, qv)
    print(result)

    vdb.close()
    db.close()
