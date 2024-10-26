import os
import sys


def run(source_folder: str):
    assert os.path.exists(source_folder)
    assert os.path.isdir(source_folder)
    

    print(f"processing {source_folder}")
    # Iterate through all files in the folder
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)

        # Only process files, skip directories
        if os.path.isdir(file_path):
            continue

        if not file_path.endswith(".gz"):
            continue

        marker_file = f"{file_path}.downloaded"
        cmd = f"touch {marker_file}"
        print(cmd)
        os.system(cmd)


run(sys.argv[1])
