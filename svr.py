#!/usr/bin/env python3

from bottle import get, request, run, template

import embedding
import query


@get('/')
def index():
    kw = ""
    results = []
    if "keyword" in request.query:
        kw = request.query.keyword
        qv = embedding.predict_vec_rep([kw], model, formatter)[0]
        results = query.query(vdb, db, qv)
    return template("index", keyword=kw, results=results)


if __name__ == '__main__':
    global model, formatter, vdb, db
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
    vdb = query.VdbClient(args.proxima_host, args.proxima_port,
                          args.collection)
    db = query.RdbClient(args.db)

    run(host=args.address, port=args.port)

    vdb.close()
    db.close()
