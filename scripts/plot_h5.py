import tables
import plotly.graph_objs as go

# Define the path to your HDF5 file
hdf5_file_path = "/home/hbina/Downloads/2024026.h5"

# Open the HDF5 file in read mode
with tables.open_file(hdf5_file_path, mode="r") as file:
    # Iterate through the groups in the HDF5 file
    for symbols in file.walk_nodes(where="/"):
        for symbol in symbols:
            # print(symbol)
            symbol_str = symbol._v_name

            if symbol_str != "AAPL":
                continue

            for table in symbol:
                # print(table)
                table_str = table._v_name

                data = table.read()
                print(data)
                # print(f"Group: {group._v_pathname}")

                # trace = go.Scatter(x=x, y=y, mode='lines', name='Sine Wave')
                # layout = go.Layout(title='Sine Wave', xaxis=dict(title='x'), yaxis=dict(title='y'))
                # fig = go.Figure(data=[trace], layout=layout)
                # fig.show()
        #
        # # Iterate through the tables (or nodes) within each group
        # for node in file.walk_nodes(group, classname='Table'):
        #     print(f"  Table: {node._v_pathname}")
        #     print(f"  Number of rows: {node.nrows}")
        #
        #     # Optionally, print the first row as an example
        #     if node.nrows > 0:
        #         print(f"  First row: {node[0]}")

    # You can also iterate over all nodes if you don't want to limit to tables
    print("\nIterating through all nodes:")
    for node in file.walk_nodes("/"):
        print(f"Node: {node._v_pathname} (Type: {type(node)})")
