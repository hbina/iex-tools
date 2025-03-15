import os


directory = "/tank/iex/pcapng/"
files = []
for root, dirs, filenames in os.walk(directory):
    for filename in filenames:
        files.append(os.path.join(root, filename))


# print(files)

for f in files:
    # print(f)

    if f.endswith(".zst"):
        # print(f)
        old = f.split("/")
        new = list(old)
        new[3] = "pcap"

        old = "/".join(old)
        new = "/".join(new)
        new = new[:-6]
        # new = new + "ng.zst"

        # # print(f"from {old} to {new}")
        cmd = f"zstdcat {old} | tshark -F pcap -i - -w {new}"
        print(cmd)
        os.system(cmd)
