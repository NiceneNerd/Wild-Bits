mod rstb;
mod sarc;
mod util;

use std::{cell::{Cell, Ref, RefCell}, collections::HashMap, sync::{Arc, Mutex}};

use botw_utils::hashes::StockHashTable;
use ::rstb::ResourceSizeTable;
use aamp::ParameterIO;
use byml::Byml;
use msyt::Msyt;
use sarc_rs::Sarc;
use serde::Serialize;

type Result<T> = std::result::Result<T, AppError>;
type State<'a> = tauri::State<'a, Mutex<AppState<'static>>>;

#[derive(Debug, Serialize)]
struct AppError {
    message: String,
    backtrace: String,
}

impl<S> From<S> for AppError where S: AsRef<str> {
    fn from(message: S) -> Self {
        let trace = backtrace::Backtrace::new();
        AppError {
            message: message.as_ref().to_owned(),
            backtrace: format!("{:?}", trace),
        }
    }
}

#[derive(Debug)]
struct AppState<'a> {
    open_sarc: Option<Sarc<'a>>,
    hash_table: Option<StockHashTable>,
    open_rstb: Option<Rstb>,
    name_table: HashMap<u32, String>,
    open_yml: Option<YamlDoc>,
}

#[derive(Debug, Clone, PartialEq)]
struct Rstb {
    table: ResourceSizeTable,
    endian: ::rstb::Endian,
}

#[derive(Debug)]
enum YamlDoc {
    Aamp(ParameterIO),
    Byml(Byml),
    Msbt(Msyt),
}

fn main() {
    tauri::Builder::default()
        .manage(Mutex::new(AppState {
            open_rstb: None,
            name_table: ::rstb::json::STOCK_NAMES.clone(),
            open_sarc: None,
            hash_table: None,
            open_yml: None,
        }))
        .invoke_handler(tauri::generate_handler![
            rstb::open_rstb,
            rstb::save_rstb,
            rstb::export_rstb,
            rstb::calc_size,
            rstb::set_size,
            rstb::delete_entry,
            rstb::add_name,
            sarc::open_sarc,
            sarc::create_sarc,
            sarc::save_sarc,
            sarc::get_file_meta,
            sarc::add_file,
            sarc::delete_file,
            sarc::update_folder,
            sarc::extract_sarc,
            sarc::extract_file,
            sarc::rename_file,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
