use crate::iex::{IexGenerator, IexMessage};
use crate::pcap_parser::{PcapData, PcapParser};
use clap::Parser;
use memmap2::Mmap;
use std::fs::{create_dir_all, OpenOptions};
use std::io::{BufWriter, Read};
use std::{collections::HashMap, fs::File, io::Write};

mod iex;
mod pcap_parser;
mod structs;

/// Simple program to greet a person
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg(long)]
    input_path: String,

    #[arg(long)]
    output_path: String,
}

// fn print_options(options: &[PcapNGOption]) {
//     for option in options {
//         if option.code == OptionCode::Comment {
//             let strr = std::str::from_utf8(&option.value).unwrap();
//             println!("comment:\n{}", strr);
//         } else if option.code == OptionCode::ShbHardware {
//             let strr = std::str::from_utf8(&option.value).unwrap();
//             println!("hardware:\n{}", strr);
//         } else if option.code == OptionCode::ShbUserAppl {
//             let strr = std::str::from_utf8(&option.value).unwrap();
//             println!("user application:\n{}", strr);
//         }
//     }
// }

fn write_to_file(
    zstd_map: &mut HashMap<String, BufWriter<File>>,
    counter: u64,
    symbol: &str,
    symbol_u64: u64,
    output_path: &str,
    buffer: &[u8],
    file_name: &'static str,
) {
    let file_path =
        std::path::Path::new(&output_path).join(symbol).join(format!("{}.bin", file_name));
    let file_path_str = file_path.to_str().unwrap().to_owned();
    if !zstd_map.contains_key(&file_path_str) {
        println!("file_map:{} {} {}", zstd_map.len(), counter, file_path_str);
        create_dir_all(file_path.parent().unwrap()).unwrap();
    }
    let writer = zstd_map.entry(file_path_str.clone()).or_insert(BufWriter::new(
        OpenOptions::new().write(true).append(true).create(true).open(file_path_str).unwrap(),
    ));
    let _ = writer.write_all(buffer).unwrap();
}

fn run_loop(input_path: &str, output_path: &str) {
    let mut input_file = File::open(input_path).unwrap();
    // let mut buffer = vec![0; 100 * 1024 * 1024];
    // input_file.read_to_end(&mut buffer).unwrap();
    let buffer = unsafe { Mmap::map(&input_file).unwrap() };
    let pcap_parser = PcapParser::new(&buffer);
    let mut pcap_count = 0;
    let mut message_count = 0;
    for (pcap_idx, pcap_data) in pcap_parser.enumerate() {
        pcap_count += 1;
        match pcap_data {
            PcapData::EnhancedPacketBlock(
                pcapng_header,
                pcapng_enhanced_packet_block,
                packet_buffer,
                options,
            ) => {
                // println!("pcap_idx:{}", pcap_idx);
                // println!("{:?}", pcapng_header);
                // println!("{:?}", pcapng_enhanced_packet_block);
                // println!("{:?}", packet_buffer);
                // println!("{:?}", options);

                let iex_generator = IexGenerator::new(packet_buffer).unwrap();
                for (message_idx, message) in iex_generator.enumerate() {
                    // println!("message_idx:{}", message_idx);
                    // match message {
                    //     IexMessage::AdminMessage(msg) => println!("{:#?}", msg),
                    //     IexMessage::TradingMessage(msg) => {
                    //         println!("{:#?}", msg)
                    //     }
                    //     IexMessage::AuctionMessage(msg) => {
                    //         println!("{:#?}", msg)
                    //     }
                    // }
                    message_count += 1;
                }
            }
        }

        if (pcap_count % 1_000_000 == 0) {
            println!("pcap_count:{} message_count:{}", pcap_count, message_count);
        }
    }
    println!("pcap_count:{} message_count:{}", pcap_count, message_count);

    // let mut file_map: HashMap<String, BufWriter<File>> = HashMap::with_capacity(100_000);
    // // let file = zstd::Decoder::new(file).unwrap();
    // let mut global_counter = 0;
    //
    // let iex_gen = IexGenerator::new(input_path);
    //
    // for msg in iex_gen {
    //     match msg {
    //         iex::Message::TradingMsg(a) => match a {
    //             iex::TradingMsg::TradeReportMessage(t) => {
    //                 let symbol = t.symbol();
    //                 let symbol_u64 = t.symbol_as_u64();
    //                 // println!("symbol:{}", symbol);
    //
    //                 write_to_file(
    //                     &mut file_map,
    //                     global_counter,
    //                     symbol,
    //                     symbol_u64,
    //                     &output_path,
    //                     &t.0,
    //                     "trade_report_message",
    //                 );
    //             }
    //             iex::TradingMsg::QuoteUpdateMessage(q) => {
    //                 let symbol = q.symbol();
    //                 let symbol_u64 = q.symbol_as_u64();
    //                 // println!("symbol:{}", symbol);
    //
    //                 write_to_file(
    //                     &mut file_map,
    //                     global_counter,
    //                     symbol,
    //                     symbol_u64,
    //                     &output_path,
    //                     &q.0,
    //                     "quote_update_message",
    //                 );
    //             }
    //             iex::TradingMsg::OfficialPriceMessage(official_price_msg) => {}
    //             iex::TradingMsg::TradeBreakMsg(trade_break_msg) => {}
    //         },
    //         iex::Message::AdminMsg(admnin_msg) => {}
    //         iex::Message::AuctionMsg(auction_message) => {}
    //     }
    //     global_counter += 1;
    // }
}

fn main() {
    let args = Args::parse();
    run_loop(&args.input_path, &args.output_path);
}
