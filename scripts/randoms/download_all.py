import logging
import os
import multiprocessing
import subprocess
import sys
import threading
import argparse
import typing


def get_full_links(link_path: str) -> typing.List[typing.Tuple[str, str]]:
    links = [(s.split(",")[0], s.split(",")[1]) for s in open(link_path, "r").read().splitlines()]
    return links


def parse_link(link_name: str) -> typing.Tuple[str, str]:
    words = link_name.split("_")
    assert words[2] == words[3]
    return words[2], words[5].split("pcap")[0][:-1]


def download(link: str, link_name: str, output_path: str):
    date, data_type = parse_link(link_name)
    pcap_path = os.path.join(output_path, f"{date}_{data_type}.pcap.gz")

    if os.path.exists(pcap_path) and os.path.getsize(pcap_path) < 512 * 1024 * 1024:
        logging.info(f"Already exists, skipping {pcap_path}")
        return False, link

    cmd = f'wget "{link}" -O {pcap_path} --no-verbose'
    logging.info(cmd)
    subprocess.run(cmd, shell=True, stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"))
    return True, link


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True)
    parser.add_argument("-o", type=str, required=True)
    args = parser.parse_args()

    input_path = args.i
    output_path = args.o

    links = get_full_links(input_path)
    links.sort(reverse=True)

    args = [(link, link_name, output_path) for (link, link_name) in links]

    with multiprocessing.Pool(processes=3) as pool:
        pool.starmap(download, args)
        # print(result)

    # ps = []
    # for t in links:
    #     link, link_name = t
    #     p = threading.Thread(target=download, args=(link, link_name, output_path))
    #     ps.append(p)

    # for p in ps:
    #     p.start()

    # for p in ps:
    #     p.join()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    main()
