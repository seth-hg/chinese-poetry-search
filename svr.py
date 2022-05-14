#!/usr/bin/env python3

from bottle import route, get, request, run, template
from pymilvus import Collection, connections
import sqlite3

import embedding
import query


@get('/')
def index():
    #global m, formatter, collection
    kw = ""
    results = []
    if "keyword" in request.query:
        kw = request.query.keyword
        qv = embedding.predict_vec_rep([kw], model, formatter)[0]
        db = sqlite3.connect('poetry.db')
        results = query.query(collection, db, qv)
    return template("index", keyword=kw, results=results)


if __name__ == '__main__':
    global model, formatter, collection
    parser = query.build_arg_parser()
    parser.add_argument("-a",
                        "--address",
                        help="listening address",
                        type=str,
                        default="localhost")
    parser.add_argument("-p",
                        "--port",
                        help="listening port",
                        type=int,
                        default=8080)
    args = parser.parse_args()

    model, formatter = embedding.init(args.model)
    connections.connect(alias="default",
                        host=args.milvus_host,
                        port=args.milvus_port)
    collection = Collection(args.collection)

    run(host=args.address, port=args.port)
