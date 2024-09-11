import logging
import os
import sqlite3
import subprocess
import sys
import typing


class MyConn:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def create_links_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            "date" TEXT,
            "data_type" TEXT,
            "completed" INTEGER,
            "link" TEXT UNIQUE
        );
        """)
        self.connection.commit()

    def insert_link(self, date: str, data_type: str, link: str) -> bool:
        try:
            cmd = """
            INSERT INTO "links" ("date", "data_type", "completed", "link") VALUES (?, ?, 0, ?);
            """
            self.cursor.execute(
                cmd,
                (
                    date,
                    data_type,
                    link,
                ),
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def is_link_done(self, link: str) -> bool:
        cmd = """
            SELECT "date", "link", "data_type", "completed" FROM "links" WHERE link = ?;
           """
        res = self.cursor.execute(cmd, (link,))
        rows = res.fetchall()
        assert len(rows) == 1
        return rows[0][3] == 1

    def set_link_done(self, link: str):
        cmd = """
            UPDATE "links" SET "completed" = ? WHERE "link" = ?;
           """
        self.cursor.execute(
            cmd,
            (
                1,
                link,
            ),
        )
        self.connection.commit()


def get_full_links(link_path: str) -> typing.List[typing.Tuple[str, str]]:
    links = [(s.split(",")[0], s.split(",")[1]) for s in open(link_path, "r").read().splitlines()]
    return links


def parse_link(link_name: str) -> typing.Tuple[str, str]:
    # print("link", link_name)
    words = link_name.split("_")
    # print("words", words)
    # print(words)
    assert words[2] == words[3]
    return words[2], words[5].split("pcap")[0][:-1]


def main():
    link_path = "/mnt/extra/usb_ssd/git/iex-tools/scripts/full_links.csv"
    root_pcap_path = "/mnt/btrfs/pcap"
    root_raw_path = "/mnt/btrfs/raw"
    root_h5_path = "/mnt/btrfs/h5"
    sqlite_path = "/mnt/btrfs/iex.db"

    # if os.path.exists(sqlite_path):
    #     os.remove(sqlite_path)

    my_conn = MyConn(sqlite_path)
    my_conn.create_links_table()

    links = get_full_links(link_path)
    links.sort(reverse=True)

    for link, link_name in links:
        date, data_type = parse_link(link_name)
        logging.info(f"{date}, {data_type}, {link}")
        # print(f"Attempting to insert {date} {data_type}")
        # link_inserted = my_conn.insert_link(date, data_type, link)
        # if not link_inserted:
        #     print(f"Duplicate values for {date} {data_type}")

        # # for link in links:
        # #     date, data_type, link = parse_link(link)
        # link_done = my_conn.is_link_done(link)
        # if link_done:
        #     print(f"Skipping {date} {data_type}")
        #     continue

        # Do stuff here
        pcap_path = os.path.join(root_pcap_path, f"{date}_{data_type}.pcap.gz")
        raw_path = os.path.join(root_raw_path, date)
        h5_path = os.path.join(root_h5_path, f"{date}.h5")

        if not os.path.exists(pcap_path):
            continue

        if "TOPS1.6" != data_type:
            continue

        cmds = [
            f'wget "{link}" -O "{pcap_path} --no-verbose"',  #
            # f"convert-pcap --input-path {pcap_path} --output-path {raw_path}",  #
            # f"python gen_h5.py -i {raw_path} -o {h5_path}",
            # f"rm -rf {raw_path}",
        ]
        for cmd in cmds:
            logging.info(cmd)
            os.system(f"{cmd} &> {date}.txt")
            # process = subprocess.run(cmd, stdout=open(f"{date}.txt", "w"), stderr=subprocess.STDOUT)
            # if process.returncode != 0:
            #     logging.warning("failed")
            #     sys.exit(1)

        # my_conn.set_link_done(link)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    main()
