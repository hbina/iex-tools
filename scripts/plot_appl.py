import datetime

import numpy as np
import tables
import plotly.graph_objs as go

# Define the path to your HDF5 file
hdf5_file_path = "/home/hbina/Downloads/20240226.h5"

# Open the HDF5 file in read mode
fig = go.Figure()

with tables.open_file(hdf5_file_path, mode="r") as file:
    # Iterate through the groups in the HDF5 file
    all_symbols = []
    for symbols in file.walk_nodes(where="/"):
        for symbol in symbols:
            # print(symbol)
            if not isinstance(symbol, tables.Group):
                continue
            symbol_str = symbol._v_name
            all_symbols.append(symbol_str)

    for symbol in all_symbols:
        try:
            trade_node = file.get_node(where=f"/{symbol}/trade_report_message.bin")
        except:
            continue

        trade_data = trade_node.read()

        trade_ts = trade_data["timestamp"]
        trade_ts = np.array([datetime.datetime.utcfromtimestamp(ts / 1_000_000_000) for ts in trade_ts])
        trade_price = trade_data["price"] / 10000

        trade_trace = go.Scatter(x=trade_ts, y=trade_price, mode="lines", name=symbol)
        fig.add_trace(trade_trace)

        # quote_node = file.get_node(where='/AAPL/quote_update_message.bin')
        # quote_data = quote_node.read()
        # quote_ts = quote_data["timestamp"]
        # quote_ts = np.array([datetime.datetime.utcfromtimestamp(ts / 1_000_000_000) for ts in quote_ts])
        # quote_bid_price = quote_data["bid_price"] / 10000
        # quote_ask_price = quote_data["ask_price"] / 10000

    # bid_trace = go.Scatter(x=quote_ts, y=quote_bid_price, mode='lines', name='bid')
    # ask_trace = go.Scatter(x=quote_ts, y=quote_ask_price, mode='lines', name='ask')

    # fig.add_trace(bid_trace)
    # fig.add_trace(ask_trace)

layout = go.Layout(title="Trade Prices", xaxis=dict(title="x"), yaxis=dict(title="y"))
fig.show()
fig.write_html("chart.html")
