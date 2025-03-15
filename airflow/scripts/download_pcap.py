import logging
import os
import subprocess
import argparse
import pandas as pd


def download(input_path: str, date: str, md_type: str, output_path: str):
    df = pd.read_csv(input_path)
    for _, row in df.iterrows():
        name = row["name"]
        link = row["link"]
        if date not in name or md_type not in link:
            continue

        pcap_path = os.path.join(output_path, name)
        cmd = f'wget "{link}" -O {pcap_path} --verbose'
        logging.info(cmd)
        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
            stdout=open(os.devnull, "w"),
            stderr=open(os.devnull, "w"),
        )
        if result.returncode != 0:
            logging.info("failed to download the PCAP")
            exit(result.returncode)
        logging.info("successfully downloaded the PCAP")
        exit(0)
    print("cannot find a matching PCAP to download")
    exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True)
    parser.add_argument("-o", type=str, required=True)
    parser.add_argument("-d", type=str, required=True)
    parser.add_argument("-t", type=str, required=True)
    args = parser.parse_args()

    input_path = args.i
    output_path = args.o
    date_str = args.d
    md_type = args.t

    download(input_path, date_str, md_type, output_path)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    main()
