mod rstb;

use std::{collections::HashMap, sync::Mutex};

use ::rstb::ResourceSizeTable;
use aamp::ParameterIO;
use byml::Byml;
use msyt::Msyt;
use sarc_rs::Sarc;
use serde::Serialize;

type Result<T> = std::result::Result<T, AppError>;

#[derive(Debug, Serialize)]
struct AppError {
    message: String,
    backtrace: String,
}

impl From<&str> for AppError {
    fn from(message: &str) -> Self {
        let trace = backtrace::Backtrace::new();
        AppError {
            message: message.to_owned(),
            backtrace: format!("{:?}", trace),
        }
    }
}

#[derive(Debug)]
struct AppState<'a> {
    open_sarc: Option<Sarc<'a>>,
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
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
