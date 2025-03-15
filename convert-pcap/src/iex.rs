use crate::structs::*;

#[derive(Debug)]
pub enum AdmninMessage<'a> {
    SystemEventMessage(&'a SystemEventMessage),
    SecurityDirectoryMessage(&'a SecurityDirectoryMessage),
    TradingStatusMessage(&'a TradingStatusMessage),
    RetailLiquidityIndicatorMessage(&'a RetailLiquidityIndicatorMessage),
    OperationalHaltStatusMessage(&'a OperationalHaltStatusMessage),
    ShortSalePriceTestStatusMessage(&'a ShortSalePriceTestStatusMessage),
}

#[derive(Debug)]
pub enum TradingMessage<'a> {
    QuoteUpdateMessage(&'a QuoteUpdateMessage),
    TradeReportMessage(&'a TradeReportMessage),
    OfficialPriceMessage(&'a OfficialPriceMessage),
    TradeBreakMessage(&'a TradeBreakMessage),
}

#[derive(Debug)]
pub enum AuctionMessage<'a> {
    AuctionInformationMessage(&'a AuctionInformationMessage),
}

#[derive(Debug)]
pub enum IexMessage<'a> {
    AdminMessage(AdmninMessage<'a>),
    TradingMessage(TradingMessage<'a>),
    AuctionMessage(AuctionMessage<'a>),
}

pub struct IexGenerator<'a> {
    buffer: &'a [u8],
    offset: usize,
    message_idx: usize,
    ethernet_header: &'a EthernetIIHeader,
    ipv4_header: &'a Ipv4Header,
    udp_header: &'a UdpHeader,
    tp_header: &'a TransportProtocolHeader,
}

impl<'a> IexGenerator<'a> {
    pub fn new(buffer: &[u8]) -> Option<IexGenerator> {
        let offset_start = 0;
        let offset_end = offset_start + size_of::<EthernetIIHeader>();
        let ethernet_header: &EthernetIIHeader =
            buffer.get(offset_start..offset_end)?.try_into().ok()?;

        let offset_start = offset_end;
        let offset_end = offset_start + size_of::<Ipv4Header>();
        let ipv4_header: &Ipv4Header = buffer.get(offset_start..offset_end)?.try_into().ok()?;

        let offset_start = offset_end;
        let offset_end = offset_start + size_of::<UdpHeader>();
        let udp_header: &UdpHeader = buffer.get(offset_start..offset_end)?.try_into().ok()?;

        let offset_start = offset_end;
        let offset_end = offset_start + size_of::<TransportProtocolHeader>();
        let tp_header: &TransportProtocolHeader =
            buffer.get(offset_start..offset_end)?.try_into().ok()?;

        Some(IexGenerator {
            buffer,
            ethernet_header,
            ipv4_header,
            udp_header,
            tp_header,
            message_idx: 0,
            offset: size_of::<EthernetIIHeader>()
                + size_of::<Ipv4Header>()
                + size_of::<UdpHeader>()
                + size_of::<TransportProtocolHeader>(),
        })
    }
    pub fn parse<T>(&self, buffer: &'a [u8]) -> Option<&'a T>
    where
        &'a T: TryFrom<&'a [u8]> + 'a,
    {
        let value = <&'a T>::try_from(buffer).ok()?;
        Some(value)
    }
    pub fn take_parse<T>(&mut self) -> Option<&'a T>
    where
        &'a T: TryFrom<&'a [u8]> + 'a,
    {
        let size = size_of::<T>();
        let buffer = self.buffer.get(self.offset..self.offset + size)?;
        self.offset += size;
        let value = <&'a T>::try_from(buffer).ok()?;
        Some(value)
    }

    pub fn take_buffer(&mut self, size: usize) -> Option<&'a [u8]> {
        let buffer = self.buffer.get(self.offset..self.offset + size)?;
        self.offset += size;
        if buffer.len() != size {
            return None;
        }
        Some(buffer)
    }

    pub fn peek_buffer(&self, size: usize) -> Option<&'a [u8]> {
        let buffer = self.buffer.get(self.offset..self.offset + size)?;
        if buffer.len() != size {
            return None;
        }
        Some(buffer)
    }
}

impl<'a> Iterator for IexGenerator<'a> {
    type Item = IexMessage<'a>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            if self.message_idx == self.tp_header.message_count as usize {
                return None;
            }
            let message_block_header = self.take_parse::<MessageBlockHeader>()?;
            if message_block_header.message_length == 0 {
                return None;
            }
            self.message_idx += 1;
            let message_buffer = self.peek_buffer(1)?;
            let message_type = message_buffer[0];
            // println!(
            //     "t:{} l:{}",
            //     message_type as char, message_block_header.message_length as usize,
            // );

            let message = match message_type {
                b'S' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<SystemEventMessage>(),
                    );
                    IexMessage::AdminMessage(AdmninMessage::SystemEventMessage(
                        self.take_parse::<SystemEventMessage>()?,
                    ))
                }
                b'D' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<SecurityDirectoryMessage>(),
                    );
                    IexMessage::AdminMessage(AdmninMessage::SecurityDirectoryMessage(
                        self.take_parse::<SecurityDirectoryMessage>()?,
                    ))
                }
                b'H' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<TradingStatusMessage>(),
                    );
                    IexMessage::AdminMessage(AdmninMessage::TradingStatusMessage(
                        self.take_parse::<TradingStatusMessage>()?,
                    ))
                }
                b'I' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<RetailLiquidityIndicatorMessage>(),
                    );
                    IexMessage::AdminMessage(AdmninMessage::RetailLiquidityIndicatorMessage(
                        self.take_parse::<RetailLiquidityIndicatorMessage>()?,
                    ))
                }
                b'O' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<OperationalHaltStatusMessage>(),
                    );
                    IexMessage::AdminMessage(AdmninMessage::OperationalHaltStatusMessage(
                        self.take_parse::<OperationalHaltStatusMessage>()?,
                    ))
                }
                b'P' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<ShortSalePriceTestStatusMessage>(),
                    );
                    IexMessage::AdminMessage(AdmninMessage::ShortSalePriceTestStatusMessage(
                        self.take_parse::<ShortSalePriceTestStatusMessage>()?,
                    ))
                }
                b'Q' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<QuoteUpdateMessage>(),
                    );
                    IexMessage::TradingMessage(TradingMessage::QuoteUpdateMessage(
                        self.take_parse::<QuoteUpdateMessage>()?,
                    ))
                }
                b'T' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<TradeReportMessage>(),
                    );
                    IexMessage::TradingMessage(TradingMessage::TradeReportMessage(
                        self.take_parse::<TradeReportMessage>()?,
                    ))
                }
                b'X' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<OfficialPriceMessage>(),
                    );
                    IexMessage::TradingMessage(TradingMessage::OfficialPriceMessage(
                        self.take_parse::<OfficialPriceMessage>()?,
                    ))
                }
                b'B' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<TradeBreakMessage>(),
                    );
                    IexMessage::TradingMessage(TradingMessage::TradeBreakMessage(
                        self.take_parse::<TradeBreakMessage>()?,
                    ))
                }
                b'A' => {
                    assert_eq!(
                        message_block_header.message_length as usize,
                        size_of::<AuctionInformationMessage>(),
                    );
                    IexMessage::AuctionMessage(AuctionMessage::AuctionInformationMessage(
                        self.take_parse::<AuctionInformationMessage>()?,
                    ))
                }
                _ => {
                    println!("Unknown message_type {:?}", message_type as char);
                    continue;
                }
            };
            return Some(message);
        }
    }
}

// pub fn nom_take(
//     count: usize,
// ) -> impl Fn(Bytes) -> Result<(Bytes, Bytes), nom::Err<nom::error::Error<Bytes>>> {
//     take::<_, &[u8], nom::error::Error<Bytes>>(count)
// }
