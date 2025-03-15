use bytes::Bytes;
use zerocopy::*;
use zerocopy_derive::*;

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct EthernetIIHeader {
    pub destination_mac: [u8; 6],
    pub source_mac: [u8; 6],
    pub ethertype: u16,
}

impl<'a> TryFrom<&'a [u8]> for &'a EthernetIIHeader {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 14] = (&value[0..14]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct OfficialPriceMessage {
    pub message_type: u8,
    pub price_type: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub official_price: i64,
}

impl<'a> TryFrom<&'a [u8]> for &'a OfficialPriceMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 26] = (&value[0..26]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct ShortSalePriceTestStatusMessage {
    pub message_type: u8,
    pub short_sale_price_test_status: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub detail: [u8; 1],
}

impl<'a> TryFrom<&'a [u8]> for &'a ShortSalePriceTestStatusMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 19] = (&value[0..19]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct TradingStatusMessage {
    pub message_type: u8,
    pub trading_status: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub reason: [u8; 4],
}

impl<'a> TryFrom<&'a [u8]> for &'a TradingStatusMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 22] = (&value[0..22]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct PcapngSectionHeaderBlock {
    pub byte_order_magic: u32,
    pub major_version: u16,
    pub minor_version: u16,
    pub section_length: i64,
}

impl<'a> TryFrom<&'a [u8]> for &'a PcapngSectionHeaderBlock {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 16] = (&value[0..16]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct TradeBreakMessage {
    pub message_type: u8,
    pub sale_condition_flags: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub size: u32,
    pub price: i64,
    pub trade_id: i64,
}

impl<'a> TryFrom<&'a [u8]> for &'a TradeBreakMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 38] = (&value[0..38]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct PcapngHeader {
    pub block_type: u32,
    pub block_total_length: u32,
}

impl<'a> TryFrom<&'a [u8]> for &'a PcapngHeader {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 8] = (&value[0..8]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct SystemEventMessage {
    pub message_type: u8,
    pub system_event: u8,
    pub timestamp: i64,
}

impl<'a> TryFrom<&'a [u8]> for &'a SystemEventMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 10] = (&value[0..10]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct TradeReportMessage {
    pub message_type: u8,
    pub sale_condition_flags: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub size: u32,
    pub price: i64,
    pub trade_id: i64,
}

impl<'a> TryFrom<&'a [u8]> for &'a TradeReportMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 38] = (&value[0..38]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct OperationalHaltStatusMessage {
    pub message_type: u8,
    pub operational_halt_status: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
}

impl<'a> TryFrom<&'a [u8]> for &'a OperationalHaltStatusMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 18] = (&value[0..18]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct QuoteUpdateMessage {
    pub message_type: u8,
    pub flags: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub bid_size: u32,
    pub bid_price: i64,
    pub ask_price: i64,
    pub ask_size: u32,
}

impl<'a> TryFrom<&'a [u8]> for &'a QuoteUpdateMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 42] = (&value[0..42]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct MessageBlockHeader {
    pub message_length: u16,
}

impl<'a> TryFrom<&'a [u8]> for &'a MessageBlockHeader {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 2] = (&value[0..2]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct SecurityDirectoryMessage {
    pub message_type: u8,
    pub flags: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub round_lot_size: u32,
    pub adjusted_poc_price: i64,
    pub luld_tier: u8,
}

impl<'a> TryFrom<&'a [u8]> for &'a SecurityDirectoryMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 31] = (&value[0..31]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct PcapngEnhancedPacketBlock {
    pub interface_id: u32,
    pub timestamp_upper: u32,
    pub timestamp_lower: u32,
    pub captured_packet_length: u32,
    pub original_packet_length: u32,
}

impl<'a> TryFrom<&'a [u8]> for &'a PcapngEnhancedPacketBlock {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 20] = (&value[0..20]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct PcapngInterfaceDescriptionBlock {
    pub linktype: u16,
    pub reserved: u16,
    pub snaplen: u32,
}

impl<'a> TryFrom<&'a [u8]> for &'a PcapngInterfaceDescriptionBlock {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 8] = (&value[0..8]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct Ipv4Header {
    pub version_ihl: u8,
    pub tos: u8,
    pub total_length: u16,
    pub identification: u16,
    pub flags_fragment_offset: u16,
    pub ttl: u8,
    pub protocol: u8,
    pub header_checksum: u16,
    pub source_ip: [u8; 4],
    pub destination_ip: [u8; 4],
}

impl<'a> TryFrom<&'a [u8]> for &'a Ipv4Header {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 20] = (&value[0..20]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct AuctionInformationMessage {
    pub message_type: u8,
    pub auction_type: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
    pub paired_shares: u32,
    pub reference_price: i64,
    pub indicative_clearing_price: i64,
    pub imbalance_shares: u32,
    pub imbalance_side: u8,
    pub extension_number: u8,
    pub scheduled_auction_time: u32,
    pub auction_book_clearing_price: i64,
    pub collar_reference_price: i64,
    pub lower_auction_collar: i64,
    pub upper_auction_collar: i64,
}

impl<'a> TryFrom<&'a [u8]> for &'a AuctionInformationMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 80] = (&value[0..80]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct TransportProtocolHeader {
    pub version: u8,
    pub reserved: u8,
    pub message_protocol_id: u16,
    pub channel_id: u32,
    pub session_id: u32,
    pub payload_length: u16,
    pub message_count: u16,
    pub stream_offset: i64,
    pub first_message_sequence_number: i64,
    pub send_time: i64,
}

impl<'a> TryFrom<&'a [u8]> for &'a TransportProtocolHeader {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 40] = (&value[0..40]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct UdpHeader {
    pub source_port: u16,
    pub destination_port: u16,
    pub length: u16,
    pub checksum: u16,
}

impl<'a> TryFrom<&'a [u8]> for &'a UdpHeader {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 8] = (&value[0..8]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}

#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct RetailLiquidityIndicatorMessage {
    pub message_type: u8,
    pub retail_liquidity_indicator: u8,
    pub timestamp: i64,
    pub symbol: [u8; 8],
}

impl<'a> TryFrom<&'a [u8]> for &'a RetailLiquidityIndicatorMessage {
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
        let buffer: &[u8; 18] = (&value[0..18]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }
}
