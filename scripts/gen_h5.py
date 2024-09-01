import os
import numpy as np
import tables
import argparse


trade_report_message_dtype = np.dtype(
    [
        ("message_type", "<u1"),
        ("sale_condition_flags", "<u1"),
        ("timestamp", "<u8"),
        ("symbol", "S8"),
        ("size", "<u4"),
        ("price", "<u8"),
        ("trade_id", "<u8"),
    ]
)

quote_update_message_dtype = np.dtype(
    [
        ("message_type", "<u1"),
        ("flags", "<u1"),
        ("timestamp", "<u8"),
        ("symbol", "S8"),
        ("bid_size", "<u4"),
        ("bid_price", "<u8"),
        ("ask_price", "<u8"),
        ("ask_size", "<u4"),
    ]
)


def get_dtype_from_filename(filename: str):
    if filename == "trade_report_message.bin":
        return trade_report_message_dtype
    elif filename == "quote_update_message.bin":
        return quote_update_message_dtype
    assert False


def run(
    input_path: str, output_path: str, compression_level: int, compression_library: str
):
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True)
    parser.add_argument("-o", type=str, required=True)
    args = parser.parse_args()

    run(
        args.i,
        args.o,
        5,
        "blosc:zstd",
    )


if __name__ == "__main__":
    main()
