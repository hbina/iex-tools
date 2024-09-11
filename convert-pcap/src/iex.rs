use std::io::Read;

use bytes::Bytes;
use nom::{bytes::complete::take, FindToken, Parser};
use pcap_parser::PcapNGReader;

#[derive(Debug)]
pub struct IexTransportHeader<'a> {
    content: &'a [u8],
}

#[derive(Debug)]
pub struct SystemEventMsg<'a>(&'a [u8]);

impl<'a> SystemEventMsg<'a> {
    pub fn timestamp(&self) -> u64 {
        u64::from_le_bytes([
            self.0[2], self.0[3], self.0[4], self.0[5], self.0[6], self.0[7], self.0[8], self.0[9],
        ])
    }
}

#[derive(Debug)]
pub struct SecurityDirectoryMsg<'a>(&'a [u8]);

#[derive(Debug)]
pub struct TradingStatusMsg<'a>(&'a [u8]);

#[derive(Debug)]
pub struct RetailLiquidityIndicatorMsg<'a>(&'a [u8]);

#[derive(Debug)]
pub struct OperationalHaltStatusMessage<'a>(&'a [u8]);

#[derive(Debug)]
pub struct ShortSalePriceTestStatusMessage<'a>(&'a [u8]);

#[derive(Debug)]
pub struct QuoteUpdateMsg<'a>(pub &'a [u8]);

impl<'a> QuoteUpdateMsg<'a> {
    pub fn flags(&self) -> u8 {
        self.0[1]
    }

    pub fn timestamp(&self) -> u64 {
        u64::from_le_bytes([
            self.0[2], self.0[3], self.0[4], self.0[5], self.0[6], self.0[7], self.0[8], self.0[9],
        ])
    }

    pub fn symbol(&self) -> &str {
        let arr = &self.0[10..18];
        assert_eq!(8, arr.len());
        let idx =
            arr.iter().enumerate().find_map(|b| (b.1 == &32).then_some(b.0)).unwrap_or(arr.len());
        // todo!("{:?}", arr);
        std::str::from_utf8(&arr[..idx]).unwrap()
    }

    pub fn symbol_as_u64(&self) -> u64 {
        u64::from_le_bytes([
            self.0[10], self.0[11], self.0[12], self.0[13], self.0[14], self.0[15], self.0[16],
            self.0[17],
        ])
    }

    pub fn bid_size(&self) -> u32 {
        u32::from_le_bytes([self.0[18], self.0[19], self.0[20], self.0[21]])
    }

    pub fn bid_price(&self) -> u64 {
        u64::from_le_bytes([
            self.0[22], self.0[23], self.0[24], self.0[25], self.0[26], self.0[27], self.0[28],
            self.0[29],
        ])
    }

    pub fn ask_price(&self) -> u64 {
        u64::from_le_bytes([
            self.0[30], self.0[31], self.0[32], self.0[33], self.0[34], self.0[35], self.0[36],
            self.0[37],
        ])
    }

    pub fn ask_size(&self) -> u32 {
        u32::from_le_bytes([self.0[38], self.0[39], self.0[40], self.0[41]])
    }
}

#[derive(Debug)]
pub struct TradeReportMsg<'a>(pub &'a [u8]);

impl<'a> TradeReportMsg<'a> {
    pub fn sale_condition_flags(&self) -> u8 {
        self.0[1]
    }

    pub fn timestamp(&self) -> u64 {
        u64::from_le_bytes([
            self.0[2], self.0[3], self.0[4], self.0[5], self.0[6], self.0[7], self.0[8], self.0[9],
        ])
    }

    pub fn symbol(&self) -> &str {
        let arr = &self.0[10..18];
        assert_eq!(8, arr.len());
        let idx =
            arr.iter().enumerate().find_map(|b| (b.1 == &32).then_some(b.0)).unwrap_or(arr.len());
        // todo!("{:?}", arr);
        std::str::from_utf8(&arr[..idx]).unwrap()
    }

    pub fn symbol_as_u64(&self) -> u64 {
        u64::from_le_bytes([
            self.0[10], self.0[11], self.0[12], self.0[13], self.0[14], self.0[15], self.0[16],
            self.0[17],
        ])
    }

    pub fn size(&self) -> u32 {
        u32::from_le_bytes([self.0[18], self.0[19], self.0[20], self.0[21]])
    }

    pub fn price(&self) -> u64 {
        u64::from_le_bytes([
            self.0[22], self.0[23], self.0[24], self.0[25], self.0[26], self.0[27], self.0[28],
            self.0[29],
        ])
    }

    pub fn trade_id(&self) -> u64 {
        u64::from_le_bytes([
            self.0[30], self.0[31], self.0[32], self.0[33], self.0[34], self.0[35], self.0[36],
            self.0[37],
        ])
    }
}

#[derive(Debug)]
pub struct OfficialPriceMsg<'a>(&'a [u8]);

#[derive(Debug)]
pub struct TradeBreakMsg<'a>(&'a [u8]);

#[derive(Debug)]
pub struct AuctionInformationMsg<'a>(&'a [u8]);

#[derive(Debug)]
pub enum AdmninMsg<'a> {
    SystemEventMsg(SystemEventMsg<'a>),
    SecurityDirectoryMsg(SecurityDirectoryMsg<'a>),
    TradingStatusMsg(TradingStatusMsg<'a>),
    RetailLiquidityIndicatorMsg(RetailLiquidityIndicatorMsg<'a>),
    OperationalHaltStatusMessage(OperationalHaltStatusMessage<'a>),
    ShortSalePriceTestStatusMessage(ShortSalePriceTestStatusMessage<'a>),
}

#[derive(Debug)]
pub enum TradingMsg<'a> {
    QuoteUpdateMessage(QuoteUpdateMsg<'a>),
    TradeReportMessage(TradeReportMsg<'a>),
    OfficialPriceMessage(OfficialPriceMsg<'a>),
    TradeBreakMsg(TradeBreakMsg<'a>),
}

#[derive(Debug)]
pub enum AuctionMessage<'a> {
    AuctionInformationMessage(AuctionInformationMsg<'a>),
}

#[derive(Debug)]
pub enum Message<'a> {
    AdminMsg(AdmninMsg<'a>),
    TradingMsg(TradingMsg<'a>),
    AuctionMsg(AuctionMessage<'a>),
}

impl<'a> Message<'a> {
    pub fn parse(bytes: &[u8]) -> Message {
        let message_type = bytes[0];
        match message_type {
            b'S' => Message::AdminMsg(AdmninMsg::SystemEventMsg(SystemEventMsg(bytes))),
            b'D' => Message::AdminMsg(AdmninMsg::SecurityDirectoryMsg(SecurityDirectoryMsg(bytes))),
            b'H' => Message::AdminMsg(AdmninMsg::TradingStatusMsg(TradingStatusMsg(bytes))),
            b'I' => Message::AdminMsg(AdmninMsg::RetailLiquidityIndicatorMsg(
                RetailLiquidityIndicatorMsg(bytes),
            )),
            b'O' => Message::AdminMsg(AdmninMsg::OperationalHaltStatusMessage(
                OperationalHaltStatusMessage(bytes),
            )),
            b'P' => Message::AdminMsg(AdmninMsg::ShortSalePriceTestStatusMessage(
                ShortSalePriceTestStatusMessage(bytes),
            )),
            b'Q' => Message::TradingMsg(TradingMsg::QuoteUpdateMessage(QuoteUpdateMsg(bytes))),
            b'T' => Message::TradingMsg(TradingMsg::TradeReportMessage(TradeReportMsg(bytes))),
            b'X' => Message::TradingMsg(TradingMsg::OfficialPriceMessage(OfficialPriceMsg(bytes))),
            b'B' => Message::TradingMsg(TradingMsg::TradeBreakMsg(TradeBreakMsg(bytes))),
            b'A' => Message::AuctionMsg(AuctionMessage::AuctionInformationMessage(
                AuctionInformationMsg(bytes),
            )),
            _ => {
                panic!("Unknown message_type {:?}", message_type as char);
            }
        }
    }
}

#[derive(Debug)]
pub struct IexData<'a> {
    // // Ethernet II
    // eth_destination: [u8; 6],
    // eth_source: [u8; 6],
    // eth_type: u16,

    // // IPV4
    // ip_version: u8,
    // ip_services_field: u8,
    // ip_total_length: u16,
    // ip_identification: u16,
    // ip_flags: u16,
    // ip_ttl: u8,
    // ip_protocol: u8,
    // ip_checksum: u16,
    // ip_source: [u8; 4],
    // ip_destination: [u8; 4],

    // // IEX-TP
    // version: u8,
    // // reserved: u8,
    // message_protocol_id: u16,
    // channel_id: u32,
    // session_id: u32,
    // payload_length: u16,
    // message_count: u16,
    // stream_offset: u64,
    // first_message_seq_num: u64,
    // send_ts: u64,
    content: &'a [u8],
    offset: usize,
}

impl<'a> IexData<'a> {
    // pub fn parse(i: &[u8]) -> nom::IResult<&[u8], IexData, nom::error::Error<&[u8]>> {
    pub fn parse(i: &[u8]) -> IexData {
        // // Parse Ethernet data
        // let (i, bytes) = nom_take(6usize)(i).unwrap();
        // let eth_destination = [bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]];

        // let (i, bytes) = nom_take(6usize)(i).unwrap();
        // let eth_source = [bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]];
        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let eth_type = u16::from_le_bytes([bytes[0], bytes[1]]);

        // // Parse IP data
        // let (i, bytes) = nom_take(1usize)(i).unwrap();
        // let ip_version = u8::from_be_bytes([bytes[0]]);

        // let (i, bytes) = nom_take(1usize)(i).unwrap();
        // let ip_services_field = u8::from_be_bytes([bytes[0]]);

        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let ip_total_length = u16::from_be_bytes([bytes[0], bytes[1]]);

        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let ip_identification = u16::from_be_bytes([bytes[0], bytes[1]]);
        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let ip_flags = u16::from_be_bytes([bytes[0], bytes[1]]);

        // let (i, bytes) = nom_take(1usize)(i).unwrap();
        // let ip_ttl = u8::from_be_bytes([bytes[0]]);

        // let (i, bytes) = nom_take(1usize)(i).unwrap();
        // let ip_protocol = u8::from_be_bytes([bytes[0]]);

        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let ip_checksum = u16::from_be_bytes([bytes[0], bytes[1]]);

        // let (i, bytes) = nom_take(4usize)(i).unwrap();
        // let ip_source = [bytes[0], bytes[1], bytes[2], bytes[3]];

        // let (i, bytes) = nom_take(4usize)(i).unwrap();
        // let ip_destination = [bytes[0], bytes[1], bytes[2], bytes[3]];

        // // Parse UDP data
        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let udp_source_port = u16::from_be_bytes([bytes[0], bytes[1]]);

        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let udp_destination_port = u16::from_be_bytes([bytes[0], bytes[1]]);

        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let udp_length = u16::from_be_bytes([bytes[0], bytes[1]]);

        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let udp_checksum = u16::from_be_bytes([bytes[0], bytes[1]]);
        let (i, _) = nom_take(42usize)(i).unwrap();

        // // Parse IEX-TP data
        // let (i, bytes) = nom_take(1usize)(i).unwrap();
        // let version = u8::from_le_bytes([bytes[0]]);
        // let (i, _) = nom_take(1usize)(i).unwrap();
        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let message_protocol_id = u16::from_le_bytes([bytes[0], bytes[1]]);
        // let (i, bytes) = nom_take(4usize)(i).unwrap();
        // let channel_id = u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]);
        // let (i, bytes) = nom_take(4usize)(i).unwrap();
        // let session_id = u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]);
        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let payload_length = u16::from_le_bytes([bytes[0], bytes[1]]);
        // let (i, bytes) = nom_take(2usize)(i).unwrap();
        // let message_count = u16::from_le_bytes([bytes[0], bytes[1]]);
        // let (i, bytes) = nom_take(8usize)(i).unwrap();
        // let stream_offset = u64::from_le_bytes([
        //     bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        // ]);
        // let (i, bytes) = nom_take(8usize)(i).unwrap();
        // let first_message_seq_num = u64::from_le_bytes([
        //     bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        // ]);
        // let (i, bytes) = nom_take(8usize)(i).unwrap();
        // let send_ts = u64::from_le_bytes([
        //     bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        // ]);
        // let (i, iex_header) = nom_take(40usize)(i).unwrap();
        // let message_count = u16::from_le_bytes([iex_header[14], iex_header[15]]);

        // Should check that i is empty now.

        // let mut messages = Vec::with_capacity(message_count as usize);
        // let mut i: &[u8] = i;
        // for _ in 0..message_count {
        //     let (i_tmp, bytes) = nom_take(2usize)(i).unwrap();
        //     let message_len = u16::from_le_bytes([bytes[0], bytes[1]]);
        //     let (i_tmp, message) = Message::parse(i_tmp, message_len as usize).unwrap();
        //     i = i_tmp;
        //     messages.push(message);
        // }

        // assert!(
        //     i.len() == 0,
        //     "leftover i of length:{} content:{:#?}",
        //     i.len(),
        //     i
        // );
        let payload_length = u16::from_le_bytes([i[12], i[12 + 1]]);
        // let stream_offset = u64::from_le_bytes([
        //     i[16],
        //     i[16 + 1],
        //     i[16 + 2],
        //     i[16 + 3],
        //     i[16 + 4],
        //     i[16 + 5],
        //     i[16 + 6],
        //     i[16 + 7],
        // ]);
        // println!("i.len():{}", i.len());
        // println!("payload_length:{}", payload_length);
        // println!("stream_offset:{}", stream_offset);
        let i = &i[0..payload_length as usize + 40];
        IexData {
            // eth_destination,
            // eth_source,
            // eth_type,

            // ip_version,
            // ip_services_field,
            // ip_total_length,
            // ip_identification,
            // ip_flags,
            // ip_ttl,
            // ip_protocol,
            // ip_checksum,
            // ip_source,
            // ip_destination,

            // version,
            // message_protocol_id,
            // channel_id,
            // session_id,
            // payload_length,
            // message_count,
            // stream_offset,
            // first_message_seq_num,
            // send_ts,
            content: i,
            offset: 40,
        }
    }

    pub fn next_message(&mut self) -> Option<Message<'_>> {
        // println!("message_count:{}", self.message_count());
        // println!("self.offset:{} self.content.len:{}", self.offset, self.content.len());
        if self.offset >= self.content.len() {
            // println!("return None");
            return None;
        }

        // println!("len_buffer:{:?}", &self.content[self.offset..self.offset + 2]);
        let message_len: usize =
            u16::from_le_bytes([self.content[self.offset + 0], self.content[self.offset + 1]])
                as usize;
        // println!("message_len:{}", message_len);
        // if message_len == 0 {
        //     return None;
        // }
        let buffer: &[u8] = &self.content[self.offset + 2..self.offset + 2 + message_len];
        let message = Message::parse(buffer);
        // println!("message:{:?}", message);
        self.offset += 2 + message_len;
        // println!("return Something");
        Some(message)
    }

    pub fn message_count(&self) -> u16 {
        u16::from_le_bytes([self.content[14], self.content[15]])
    }
}

pub fn nom_take<'a>(
    count: usize,
) -> impl Fn(&'a [u8]) -> Result<(&'a [u8], &'a [u8]), nom::Err<nom::error::Error<&'a [u8]>>> {
    take::<_, &[u8], nom::error::Error<&[u8]>>(count)
}
