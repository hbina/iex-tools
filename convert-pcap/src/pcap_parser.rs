use crate::structs::{PcapngEnhancedPacketBlock, PcapngHeader, PcapngSectionHeaderBlock};
use nom::Slice;
use std::fs::File;
use std::io::Read;

pub struct PcapParser<'a> {
    buffer: &'a [u8],
    offset: usize,
}

impl<'a> PcapParser<'a> {
    pub fn new(buffer: &'a [u8]) -> Self {
        Self { buffer, offset: 0 }
    }

    pub fn parse<T>(&mut self, size: usize) -> Option<T>
    where
        T: TryFrom<&'a [u8]>,
    {
        let value = self.buffer.get(self.offset..self.offset + size)?.try_into().ok()?;
        self.offset += size;
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
}

pub enum PcapData<'a> {
    EnhancedPacketBlock(&'a PcapngHeader, &'a PcapngEnhancedPacketBlock, &'a [u8], &'a [u8]),
}

impl<'this> Iterator for PcapParser<'this> {
    type Item = PcapData<'this>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let pcapng_header = self.parse::<&PcapngHeader>(size_of::<PcapngHeader>())?;
            match pcapng_header.block_type {
                // 0x0a0d0d0a => {}
                // 0x00000001 => {}
                0x00000006 => {
                    let enhanced_packet_block =
                        self.parse::<&PcapngEnhancedPacketBlock>(size_of::<
                            PcapngEnhancedPacketBlock,
                        >())?;
                    assert_eq!(
                        enhanced_packet_block.captured_packet_length as usize,
                        enhanced_packet_block.original_packet_length as usize,
                    );
                    let packet_buffer =
                        self.take_buffer(enhanced_packet_block.captured_packet_length as usize)?;
                    let options = self.take_buffer(
                        pcapng_header.block_total_length as usize
                            - size_of::<PcapngHeader>()
                            - size_of::<PcapngEnhancedPacketBlock>()
                            - enhanced_packet_block.captured_packet_length as usize
                            - 4,
                    )?;
                    // Redundant length at the end
                    let _ = self.take_buffer(4)?;
                    return Some(PcapData::EnhancedPacketBlock(
                        pcapng_header,
                        enhanced_packet_block,
                        packet_buffer,
                        options,
                    ));
                }
                _ => {
                    self.take_buffer(
                        pcapng_header.block_total_length as usize - size_of::<PcapngHeader>(),
                    )?;
                }
            }
        }
    }
}
