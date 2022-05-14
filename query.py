#!/usr/bin/env python3

import argparse
import os
import json
import logging
import re
import sqlite3

from pymilvus import connections
from pymilvus import Collection

import embedding

logging.basicConfig(
    format=
    '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    level=logging.INFO)


def content_query(conn, ids):
    c = conn.cursor()
    cursor = c.execute("SELECT id, content FROM poetry WHERE id in (%s)" %
                       ",".join([str(x) for x in ids]))
    poem = {}
    for row in cursor:
        poem[row[0]] = json.loads(row[1])
    return poem


def vector_query(collection, v):
    search_params = {"metric_type": "L2", "params": {"ef": 32}}
    results = collection.search(data=[v],
                                anns_field="feature",
                                param=search_params,
                                limit=10,
                                expr=None,
                                consistency_level="Strong")

    return collection.query(expr="id in [%s]" %
                            ",".join([str(x) for x in results[0].ids]),
                            output_fields=["poem", "paragraph"],
                            consistency_level="Strong")


def query(collection, conn, q):
    res = vector_query(collection, q)

    poem_ids = set()
    for r in res:
        poem_ids.add(r["poem"])
    poem = content_query(conn, set(poem_ids))

    all_res = []
    for idx, r in enumerate(res):
        p = poem[r["poem"]]
        all_res.append({"content": p, "paragraph": r["paragraph"]})
    conn.close()

    return all_res


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

    connections.connect(alias="default",
                        host=args.milvus_host,
                        port=args.milvus_port)
    collection = Collection(args.collection)

    db = sqlite3.connect(args.db)
    result = query(collection, db, qv)
    print(result)
