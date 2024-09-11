import os
import numpy as np
import tables
import multiprocessing

from scripts.dtypes import trade_report_message_dtype, quote_update_message_dtype


def get_dtype_from_filename(filename: str):
    if filename == "trade_report_message.bin":
        return trade_report_message_dtype
    elif filename == "quote_update_message.bin":
        return quote_update_message_dtype
    assert False


def run(input_path: str, output_path: str, compression_level: int, compression_library: str):
    with tables.open_file(output_path, "w") as h5_file:
        # Iterate over all files in the input directory
        for symbol in os.listdir(input_path):
            for filename in os.listdir(os.path.join(input_path, symbol)):
                binary_path = os.path.join(input_path, symbol, filename)
                # print(binary_path)
                file_dtype = get_dtype_from_filename(filename)
                # print(file_dtype)
                data = np.fromfile(binary_path, dtype=file_dtype)
                h5_file.create_table(
                    where=f"/{symbol}",
                    name=f"{filename}",
                    createparents=True,
                    filters=tables.Filters(
                        complevel=compression_level,
                        complib=compression_library,
                        shuffle=True,
                    ),
                    # description=file_dtype,
                    obj=data,
                )


def main():
    input_path = "/mnt/usb_ssd/usb_ssd/iex/split"
    output_path = "/mnt/usb_ssd/usb_ssd/iex/h52/"

    # print(tables.filters.all_complibs)
    for compression_level in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        ps = []
        for compression_library in tables.filters.all_complibs:
            real_output_path = os.path.join(
                output_path,
                f"{compression_library.replace(':','_')}_{compression_level}.h5",
            )
            p = multiprocessing.Process(
                target=run,
                args=(
                    input_path,
                    real_output_path,
                    compression_level,
                    compression_library,
                ),
            )
            ps.append(p)

        for p in ps:
            p.start()

        for p in ps:
            p.join()


if __name__ == "__main__":
    main()
