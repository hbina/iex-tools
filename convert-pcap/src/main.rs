use clap::Parser;
use flate2::read::GzDecoder;
use pcap_parser::{traits::PcapReaderIterator, PcapError, PcapNGReader};
use std::{collections::HashMap, fs::File, io::Write};

use crate::iex::IexData;

mod iex;

/// Simple program to greet a person
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg(long)]
    input_path: String,

    #[arg(long)]
    output_path: String,
}

fn print_options(options: &[pcap_parser::PcapNGOption]) {
    for option in options {
        if option.code == pcap_parser::OptionCode::Comment {
            let strr = std::str::from_utf8(&option.value).unwrap();
            println!("comment:\n{}", strr);
        } else if option.code == pcap_parser::OptionCode::ShbHardware {
            let strr = std::str::from_utf8(&option.value).unwrap();
            println!("hardware:\n{}", strr);
        } else if option.code == pcap_parser::OptionCode::ShbUserAppl {
            let strr = std::str::from_utf8(&option.value).unwrap();
            println!("user application:\n{}", strr);
        }
    }
}

fn write_to_file(
    zstd_map: &mut HashMap<String, std::io::BufWriter<std::fs::File>>,
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
        std::fs::create_dir_all(file_path.parent().unwrap()).unwrap();
    }
    let writer = zstd_map.entry(file_path_str.clone()).or_insert(std::io::BufWriter::new(
        std::fs::OpenOptions::new()
            .write(true)
            .append(true)
            .create(true)
            .open(file_path_str)
            .unwrap(),
    ));
    let _ = writer.write_all(buffer).unwrap();
}

fn run_loop(input_path: &str, output_path: &str) {
    let mut file_map: HashMap<String, std::io::BufWriter<std::fs::File>> =
        HashMap::with_capacity(100_000);
    let file = File::open(input_path).unwrap();
    let file = GzDecoder::new(file);
    let mut reader = PcapNGReader::new(65536, file).unwrap();
    let mut global_counter = 0;

    loop {
        match reader.next() {
            Ok((offset, block)) => {
                // println!("---------------------------------");
                match block {
                    pcap_parser::PcapBlockOwned::NG(ng) => match ng {
                        pcap_parser::Block::SectionHeader(shb) => {}
                        pcap_parser::Block::InterfaceDescription(idb) => {
                            print_options(&idb.options);
                        }
                        pcap_parser::Block::EnhancedPacket(epb) => {
                            let mut ok = IexData::parse(epb.data);
                            let mut local_counter = 0;
                            while let Some(msg) = &ok.next_message() {
                                // println!("-----------------------------------");
                                // println!("local_counter:{}", local_counter);
                                local_counter += 1;
                                match msg {
                                    iex::Message::TradingMsg(a) => match a {
                                        iex::TradingMsg::TradeReportMessage(t) => {
                                            let symbol = t.symbol();
                                            let symbol_u64 = t.symbol_as_u64();
                                            // println!("symbol:{}", symbol);

                                            write_to_file(
                                                &mut file_map,
                                                global_counter,
                                                symbol,
                                                symbol_u64,
                                                &output_path,
                                                &t.0,
                                                "trade_report_message",
                                            );
                                        }
                                        iex::TradingMsg::QuoteUpdateMessage(q) => {
                                            let symbol = q.symbol();
                                            let symbol_u64 = q.symbol_as_u64();
                                            // println!("symbol:{}", symbol);

                                            write_to_file(
                                                &mut file_map,
                                                global_counter,
                                                symbol,
                                                symbol_u64,
                                                &output_path,
                                                &q.0,
                                                "quote_update_message",
                                            );
                                        }
                                        _ => {}
                                    },
                                    _ => {}
                                }
                                global_counter += 1;
                            }
                        }
                        _ => todo!(),
                    },
                    _ => todo!(),
                }

                reader.consume(offset);
            }
            Err(PcapError::Eof) => break,
            Err(PcapError::Incomplete(_)) => {
                reader.refill().unwrap();
            }
            Err(e) => panic!("error while reading: {:?}", e),
        }
    }
}

fn main() {
    let args = Args::parse();
    run_loop(&args.input_path, &args.output_path);
}
