mod rstb;

use aamp::ParameterIO;
use byml::Byml;
use msyt::Msyt;
use rstb::ResourceSizeTable;
use sarc_rs::Sarc;
use tauri::{
  api::{self, dialog},
  command,
};

type Result<T> = std::result::Result<T, String>;

#[derive(Debug, Clone, PartialEq)]
struct Rstb {
  table: ResourceSizeTable,
  be: bool,
}

#[derive(Debug)]
enum YamlDoc {
  Aamp(ParameterIO),
  Byml(Byml),
  Msbt(Msyt),
}

#[derive(Debug)]
struct AppState<'a> {
  open_sarc: Option<Sarc<'a>>,
  open_rstb: Option<ResourceSizeTable>,
  open_rstb_be: Option<bool>,
  open_yml: Option<YamlDoc>,
}

fn main() {
  tauri::Builder::default()
    // .invoke_handler(tauri::generate_handler![browse])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
