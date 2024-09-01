import os
import multiprocessing
import subprocess
import sys
import threading
import argparse


def download(download_link: str, output_path: str, filename: str):
    # print(download_link, filename)
    output_file = os.path.join(output_path, filename)
    cmd = f'wget "{download_link}" -O {output_file}'
    print(cmd)
    # os.system(cmd)
    subprocess.run(
        cmd, shell=True, stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w")
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True)
    parser.add_argument("-o", type=str, required=True)
    parser.add_argument("-n", type=int, required=True)
    args = parser.parse_args()

    input_path = args.i
    output_path = args.o
    count = args.n

    links = open(input_path, "r").readlines()
    ps = []
    for line in links[len(links) - count :]:
        download_link, filename = line.strip().split(",")
        p = threading.Thread(
            target=download, args=(download_link, output_path, filename)
        )
        ps.append(p)

    for p in ps:
        p.start()

    for p in ps:
        p.join()


if __name__ == "__main__":
    main()
