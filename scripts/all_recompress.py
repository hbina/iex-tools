import logging
import os
import multiprocessing
import subprocess
import sys
import threading
import argparse
import typing


def generate_args(input_path: str, output_path: str) -> typing.List[str]:
    files = os.listdir(input_path)
    result = []

    for file in files:
        if not file.endswith(".gz"):
            continue

        input_file = os.path.join(input_path, file)
        recompressed_file = os.path.join(output_path, file[:-3] + ".zst")
        cmd = f"gzip -ck {input_file} | zstd --ultra -22 -o {recompressed_file}"

        result.append(cmd)

    return result


def recompress(cmd: str):
    logging.info(cmd)
    subprocess.run(cmd, shell=True, stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"))
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True)
    parser.add_argument("-o", type=str, required=True)
    args = parser.parse_args()

    input_path = args.i
    output_path = args.o

    args = generate_args(input_path, output_path)

    with multiprocessing.Pool(processes=1) as pool:
        pool.map(recompress, args)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    main()
