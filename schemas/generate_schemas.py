#!/usr/bin/env python3
import argparse
import os
import sys
import stat
import pwd
import grp
import time

import convert_yaml


def collect_python_code_gen(input_path: str):
    # Verify that the provided path is a directory
    if not os.path.isdir(input_path):
        print(f"Error: {input_path} is not a valid directory")
        sys.exit(1)

    result = []
    for entry in os.scandir(input_path):
        if entry.is_file():
            print(str(entry.path))
            res = convert_yaml.generate_numpy_parser(entry.path)
            result.append(res)

    return result


def generate_python_code(input_path: str):
    code_gens = collect_python_code_gen(input_path)

    code_dtype = "\n".join([s[0] for s in code_gens])
    code_itemsize = "\n".join([s[1] for s in code_gens])
    code_parse = "\n\n".join([s[2] for s in code_gens])

    result_txt = f"import numba\nimport numpy as np\n\n{code_dtype}\n\n{code_itemsize}\n\n{code_parse}"
    print(result_txt)

    os.makedirs("build", exist_ok=True)

    fd = open("build/parsers.py", "w")
    fd.write(result_txt)
    fd.close()


def collect_rust_code_gen(input_path: str):
    # Verify that the provided path is a directory
    if not os.path.isdir(input_path):
        print(f"Error: {input_path} is not a valid directory")
        sys.exit(1)

    result = []
    for entry in os.scandir(input_path):
        if entry.is_file():
            print(str(entry.path))
            res = convert_yaml.generate_rust_struct(entry.path)
            result.append(res)

    return result


def generate_rust_code(input_path: str):
    code_gens = collect_rust_code_gen(input_path)
    print(code_gens)
    result_txt = """use bytes::Bytes;
use zerocopy::*;
use zerocopy_derive::*;\n
"""
    result_txt += "\n".join(code_gens)
    fd = open("build/parsers.rs", "w")
    fd.write(result_txt)
    fd.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()

    generate_python_code(args.path)
    generate_rust_code(args.path)


if __name__ == "__main__":
    main()
