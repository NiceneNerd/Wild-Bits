use std::{fs, io::Cursor, sync::Mutex};

use aamp::{names::NameTable, ParameterIO};
use byml::Byml;
use lazy_static::lazy_static;
use msyt::Msyt;
use serde_json::{json, Value};
use serde_yaml;

use crate::{util, AppError, Result, State, Yaml, YamlDoc, YamlEndian};

lazy_static! {
    static ref NAME_TABLE: Mutex<NameTable> = Mutex::new(aamp::names::get_default_name_table());
}

fn init_name_table() {
    let mut table = NAME_TABLE.lock().unwrap();
    if table.get_name(1596346337).is_none() {
        (0..10000).for_each(|i| table.add_name(&format!("File{}", i)));
    }
}

#[tauri::command(async)]
pub(crate) fn open_yaml(state: State<'_>, file: String) -> Result<Value> {
    parse_yaml(
        state,
        &fs::read(&file).map_err(|_| AppError::from("Failed to open file"))?,
    )
}

#[tauri::command(async)]
pub(crate) fn save_yaml(state: State<'_>, text: String, file: String) -> Result<Value> {
    let mut state_lock = state.lock().unwrap();
    let yaml = state_lock.open_yml.as_mut().unwrap();
    yaml.update(&text)?;
    let mut data = yaml.to_binary();
    if util::should_compress(&file) {
        data = util::compress(data)?; 
    }
    if file.starts_with("SARC:") {
        let path = file.trim_end_matches("/").trim_start_matches("SARC:");
        let levels: Vec<&str> = path.split("//").collect();
        let filename = *levels.last().unwrap();
        drop(state_lock);
        crate::sarc::modify_sarc(state, &path, |sw| {
            sw.files.insert(filename.to_owned(), data);
        })
    } else {
        fs::write(&file, data).map_err(|_| AppError::from("Failed to save file"))?;
        Ok(json!({}))
    }
}

pub(crate) fn parse_yaml(state: State<'_>, data: &[u8]) -> Result<Value> {
    let data = util::decompress_if(data)?;
    let yaml = Yaml::from_binary(data)?;
    let y_type = match &yaml.doc {
        YamlDoc::Aamp(_) => {
            init_name_table();
            "aamp"
        }
        YamlDoc::Byml(_) => "byml",
        YamlDoc::Msbt(_) => "msbt",
    };
    let res = json!({
        "yaml": yaml.to_text(),
        "be": matches!(&yaml.endian, YamlEndian::Big),
        "type": y_type
    });
    state.lock().unwrap().open_yml = Some(yaml);
    Ok(res)
}

impl Yaml {
    pub(crate) fn to_binary(&self) -> Vec<u8> {
        match &self.doc {
            YamlDoc::Aamp(pio) => pio.to_binary().unwrap(),
            YamlDoc::Byml(byml) => byml
                .to_binary(
                    match self.endian {
                        YamlEndian::Big => byml::Endian::Big,
                        YamlEndian::Little => byml::Endian::Little,
                    },
                    2,
                )
                .unwrap(),
            YamlDoc::Msbt(msbt) => msbt
                .clone()
                .into_msbt_bytes(match self.endian {
                    YamlEndian::Big => msyt::Endianness::Big,
                    YamlEndian::Little => msyt::Endianness::Little,
                })
                .unwrap(),
        }
    }

    pub(crate) fn to_text(&self) -> String {
        match &self.doc {
            YamlDoc::Aamp(pio) => pio.to_text().unwrap(),
            YamlDoc::Byml(byml) => byml.to_text().unwrap(),
            YamlDoc::Msbt(msbt) => serde_yaml::to_string(msbt).unwrap(),
        }
    }

    pub(crate) fn from_binary(data: &[u8]) -> Result<Self> {
        let data = util::decompress_if(data)?;
        if &data[0..4] == b"AAMP" {
            let pio = ParameterIO::from_binary(&mut Cursor::new(&data))
                .map_err(|_| AppError::from("Failed to parse AAMP"))?;
            Ok(Self {
                doc: YamlDoc::Aamp(pio),
                endian: YamlEndian::Little,
            })
        } else if [b"BY", b"YB"].contains(&&[data[0], data[1]]) {
            let byml =
                Byml::from_binary(&data).map_err(|_| AppError::from("Failed to parse BYML"))?;
            Ok(Self {
                doc: YamlDoc::Byml(byml),
                endian: match &data[0..2] {
                    b"BY" => YamlEndian::Big,
                    b"YB" => YamlEndian::Little,
                    _ => unreachable!(),
                },
            })
        } else if &data[0..8] == b"MsgStdBn" {
            let msbt =
                Msyt::from_msbt_bytes(&data).map_err(|_| AppError::from("Failed to parse MSBT"))?;
            Ok(Self {
                doc: YamlDoc::Msbt(msbt),
                endian: match &data[0x08..0x0A] {
                    b"\xfe\xff" => YamlEndian::Big,
                    b"\xff\xfe" => YamlEndian::Little,
                    _ => unreachable!(),
                },
            })
        } else {
            Err(AppError::from("Not an AAMP, BYML, or MSBT file"))
        }
    }

    pub(crate) fn update(&mut self, text: &str) -> Result<()> {
        Ok(match &self.doc {
            YamlDoc::Aamp(_) => {
                self.doc = YamlDoc::Aamp(
                    ParameterIO::from_text(text)
                        .map_err(|_| AppError::from("Failed to update, invaid YAML"))?,
                );
            }
            YamlDoc::Byml(_) => {
                self.doc = YamlDoc::Byml(
                    Byml::from_text(text)
                        .map_err(|_| AppError::from("Failed to update, invaid YAML"))?,
                )
            }
            YamlDoc::Msbt(_) => {
                self.doc = YamlDoc::Msbt(
                    serde_yaml::from_str(text)
                        .map_err(|_| AppError::from("Failed to update, invaid YAML"))?,
                )
            }
        })
    }
}
