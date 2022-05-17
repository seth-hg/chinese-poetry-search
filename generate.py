#!/usr/bin/env python3

import argparse
import csv
import os
import json

import embedding

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m",
                        "--model",
                        help="path to model",
                        type=str,
                        default="./BERT_CCPoem_v1")
    parser.add_argument("-i",
                        "--input",
                        help="path to poetry dataset",
                        type=str,
                        default="./chinese-poetry/quan_tang_shi/json")
    parser.add_argument("-o",
                        "--output",
                        help="path to output dir",
                        type=str,
                        default="./out")
    parser.add_argument("-n",
                        "--num",
                        help="max # of poems to process",
                        type=int,
                        default=0)
    args = parser.parse_args()

    model, formatter = embedding.init(args.model)

    vector_output = open(args.output + "/vectors.csv", "w+")
    content_output = open(args.output + "/content.csv", "w+")
    vector2poem_output = open(args.output + "/vector2poem.csv", "w+")

    vector_writer = csv.writer(vector_output)
    vector_writer.writerow(["id", "feature"])
    content_writer = csv.writer(content_output)
    content_writer.writerow(["id", "content"])
    vector2poem_writer = csv.writer(vector2poem_output)
    vector2poem_writer.writerow(["id", "poem", "paragraph"])

    vector_id = 0
    poem_id = 0
    for data_file in os.listdir(args.input):
        with open(args.input + "/" + data_file) as f:
            poem_list = json.load(f)
            for poem in poem_list:
                content_writer.writerow([poem_id, json.dumps(poem)])
                vectors = embedding.predict_vec_rep(poem["paragraphs"], model,
                                                    formatter)
                for idx, v in enumerate(vectors):
                    vector2poem_writer.writerow([vector_id, poem_id, idx])
                    vector_writer.writerow([vector_id, v])
                    vector_id += 1
                poem_id += 1
                if args.num > 0 and poem_id >= args.num:
                    break
            else:
                continue
            break

    vector_output.close()
    content_output.close()
    vector2poem_output.close()
