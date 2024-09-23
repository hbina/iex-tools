import numpy as np

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
