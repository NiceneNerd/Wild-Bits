#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

mod rstb;
mod sarc;
mod util;
mod yaml;

use ::rstb::ResourceSizeTable;
use botw_utils::{extensions::*, hashes::StockHashTable};
use msyt::Msyt;
use roead::{aamp::ParameterIO, byml::Byml, sarc::Sarc};
use serde::Serialize;
use serde_json::{json, Value};
use std::{collections::HashMap, sync::Mutex};

type Result<T> = std::result::Result<T, AppError>;
type State<'a> = tauri::State<'a, Mutex<AppState<'static>>>;

#[derive(Debug, Serialize)]
struct AppError {
    message: String,
    backtrace: String,
}

impl<S> From<S> for AppError
where
    S: AsRef<str>,
{
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
    open_yml: Option<Yaml>,
}

#[derive(Debug, Clone, PartialEq)]
struct Rstb {
    table: ResourceSizeTable,
    endian: ::rstb::Endian,
}

#[derive(Debug, PartialEq, Clone)]
pub(crate) struct Yaml {
    endian: YamlEndian,
    doc: YamlDoc,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub(crate) enum YamlEndian {
    Big,
    Little,
}

#[derive(Debug, Clone, PartialEq)]
pub(crate) enum YamlDoc {
    Aamp(ParameterIO),
    Byml(Byml),
    Msbt(Msyt),
}

#[tauri::command]
pub(crate) fn has_args() -> bool {
    std::env::args().filter(|arg| arg != "--debug").count() > 1
}

#[tauri::command(async)]
pub(crate) fn open_args(state: State<'_>) -> Value {
    let args = std::env::args();
    if let Some(file) = args.filter(|f| f != "--debug").nth(1) {
        if let Some(ext) = std::path::Path::new(&file)
            .extension()
            .and_then(|ext| ext.to_str())
            .map(|ext| ext.trim_end_matches(".zs"))
        {
            if AAMP_EXTS.contains(&ext)
                || BYML_EXTS.contains(&ext)
                || matches!(ext, "msbt" | "bgyml")
            {
                if let Ok(yaml) = yaml::open_yaml(state, file.clone()) {
                    return json!({
                        "type": "yaml",
                        "data": yaml,
                        "path": file,
                    });
                }
            } else if SARC_EXTS.contains(&ext) {
                if let Ok(sarc) = sarc::open_sarc(state, file.clone()) {
                    return json!({
                        "type": "sarc",
                        "data": sarc,
                        "path": file,
                    });
                }
            } else if ext.ends_with("sizetable") {
                if let Ok(rstb) = rstb::open_rstb(state, file.clone()) {
                    return json!({
                        "type": "rstb",
                        "data": rstb,
                        "path": file,
                    });
                }
            }
        }
    }
    Default::default()
}

fn main() {
    let data_dir = tauri::api::path::config_dir().unwrap().join("wildbits");
    let name_file = data_dir.join("names.json");
    let name_table = match std::fs::read_to_string(name_file)
        .map_err(|e| AppError::from(format!("Failed to open name table: {:?}", e)))
        .and_then(|names| {
            serde_json::from_str::<std::collections::HashMap<u32, String>>(&names)
                .map_err(|e| AppError::from(format!("Failed to parse name table: {:?}", e)))
        }) {
        Ok(name_table) => util::FILES
            .iter()
            .map(|(k, v)| (*k, v.to_string()))
            .chain(name_table.into_iter())
            .collect(),
        Err(e) => {
            println!("Failed to load custom name table: {:?}", e);
            util::FILES
                .iter()
                .map(|(k, v)| (*k, v.to_string()))
                .collect()
        }
    };
    tauri::Builder::default()
        .manage(Mutex::new(AppState {
            open_rstb: None,
            name_table,
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
            rstb::scan_mod,
            rstb::flush_names,
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
            sarc::open_sarc_yaml,
            yaml::open_yaml,
            yaml::save_yaml,
            has_args,
            open_args
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
