use std::path::Path;

use crate::{AppError, Result, Rstb, State};
use botw_utils::extensions::SARC_EXTS;
use roead::sarc::Sarc;
use rstb::{calc, Endian, ResourceSizeTable};
use serde_json::{json, Value};
use std::fs;

fn parse_rstb<P: AsRef<Path>>(file: P) -> Result<Rstb> {
    let data = fs::read(file.as_ref()).map_err(|_| AppError::from("Could not read file"))?;
    for endian in &[rstb::Endian::Big, rstb::Endian::Little] {
        let table = ResourceSizeTable::from_binary(&data, *endian)
            .map_err(|_| AppError::from("Invalid RSTB file"))?;
        let randoms = [
            "EventFlow/PictureMemory.bfevfl",
            "Camera/Demo648_0/C04-0.bcamanim",
            "Effect/FldObj_ScaffoldIronParts_A_01.esetlist",
            "Physics/TeraMeshRigidBody/MainField/9-8.hktmrb",
        ];
        if randoms.iter().any(|e| table.is_in_table(e)) {
            return Ok(Rstb {
                table,
                endian: *endian,
            });
        }
    }
    Err("Invalid RSTB file".into())
}

fn rstb_to_json(
    table: &ResourceSizeTable,
    name_table: &std::collections::HashMap<u32, String>,
) -> Value {
    Value::Object(
        table
            .hash_entries()
            .map(|(h, v)| {
                (
                    match name_table.get(&h) {
                        Some(s) => s.to_owned(),
                        None => h.to_string(),
                    },
                    Value::Number(serde_json::Number::from(*v)),
                )
            })
            .chain(
                table
                    .name_entries()
                    .map(|(n, v)| (n.to_owned(), Value::Number(serde_json::Number::from(*v)))),
            )
            .collect(),
    )
}

#[tauri::command(async)]
pub(crate) fn open_rstb(state: State<'_>, file: String) -> Result<Value> {
    let table = parse_rstb(&file)?;
    let res = json!({
        "path": file,
        "rstb": rstb_to_json(&table.table, &state.lock().unwrap().name_table),
        "be": matches!(table.endian, Endian::Big)
    });
    state.lock().unwrap().open_rstb = Some(table);
    Ok(res)
}

#[tauri::command(async)]
pub(crate) fn save_rstb(state: State<'_>, file: String) -> Result<()> {
    let state = state.lock().unwrap();
    let table = state.open_rstb.as_ref().unwrap();
    let path = std::path::PathBuf::from(&file);
    let data = table
        .table
        .to_binary(
            table.endian,
            path.extension().unwrap().to_string_lossy().starts_with('s'),
        )
        .map_err(|e| AppError::from(format!("Could not save RSTB: {:?}", e).as_str()))?;
    fs::write(path, &data).map_err(|_| AppError::from("Failed to save RSTB"))?;
    Ok(())
}

#[tauri::command(async)]
pub(crate) fn export_rstb(state: State<'_>, file: String) -> Result<()> {
    let state = state.lock().unwrap();
    let table = state.open_rstb.as_ref().unwrap();
    let text = table.table.to_text().unwrap();
    fs::write(&file, text.as_bytes()).map_err(|_| AppError::from("Failed to save file"))?;
    Ok(())
}

#[tauri::command(async)]
pub(crate) fn calc_size(state: State<'_>, file: String) -> Result<u32> {
    Ok(calc::calculate_size(
        file,
        state.lock().unwrap().open_rstb.as_ref().unwrap().endian,
        true,
    )
    .map_err(|e| AppError::from(format!("Failed to calculate: {:?}", e).as_str()))?
    .unwrap_or(0))
}

#[tauri::command]
pub(crate) fn set_size(state: State<'_>, path: String, size: u32) -> Result<()> {
    let mut state = state.lock().unwrap();
    let table = state.open_rstb.as_mut().unwrap();
    table.table.set_size(&path, size);
    state
        .name_table
        .insert(crc::crc32::checksum_ieee(path.as_bytes()), path);
    Ok(())
}

#[tauri::command]
pub(crate) fn delete_entry(state: State<'_>, path: String) -> Result<()> {
    let mut state = state.lock().unwrap();
    let table = state.open_rstb.as_mut().unwrap();
    table.table.delete_entry(&path);
    Ok(())
}

#[tauri::command]
pub(crate) fn add_name(state: State<'_>, name: String) -> u32 {
    let hash = crc::crc32::checksum_ieee(name.as_bytes());
    state.lock().unwrap().name_table.insert(hash, name);
    hash
}

#[tauri::command(async)]
pub(crate) fn scan_mod(state: State<'_>, path: String) -> Result<()> {
    use rayon::prelude::*;
    let files = glob::glob(&Path::new(&path).join("**/*.*").to_string_lossy())
        .unwrap()
        .filter_map(|f| f.ok())
        .filter(|f| f.is_file())
        .collect::<Vec<_>>();

    fn get_nested_names(sarc: &Sarc) -> Vec<String> {
        sarc.files()
            .filter_map(|file| {
                file.name().map(|name| -> Vec<String> {
                    let mut names = vec![botw_utils::get_canon_name_without_root(name)];
                    if file.data().len() > 0x40
                        && file.is_sarc()
                        && !(name.ends_with("sarc")
                            || name.ends_with("farc")
                            || name.ends_with("larc"))
                    {
                        if let Ok(nest_sarc) = file.parse_as_sarc() {
                            names.extend(get_nested_names(&nest_sarc))
                        }
                    }
                    names
                })
            })
            .flatten()
            .collect()
    }

    files.into_par_iter().try_for_each(|file| -> Result<()> {
        if let Some(canon) = botw_utils::get_canon_name(&file) {
            state.lock().unwrap().name_table.insert(
                crc::crc32::checksum_ieee(file.to_string_lossy().as_bytes()),
                canon,
            );
        }
        if SARC_EXTS.contains(
            &file
                .extension()
                .and_then(|ext| ext.to_str())
                .unwrap_or("Dummy"),
        ) {
            if let Ok(sarc) = std::fs::read(&file)
                .map_err(|_| ())
                .and_then(|data| Sarc::read(data).map_err(|_| ()))
            {
                let names = get_nested_names(&sarc);
                names.into_iter().for_each(|name| {
                    state
                        .lock()
                        .unwrap()
                        .name_table
                        .insert(crc::crc32::checksum_ieee(name.as_bytes()), name);
                });
            }
        }
        Ok(())
    })?;

    flush_names(state)?;
    Ok(())
}

#[tauri::command(async)]
pub(crate) fn flush_names(state: State<'_>) -> Result<()> {
    let state = state.lock().unwrap();
    if ::rstb::json::STOCK_NAMES.ne(&state.name_table) {
        let data_dir = tauri::api::path::config_dir().unwrap().join("wildbits");
        let name_file = data_dir.join("names.json");
        if !data_dir.exists() {
            fs::create_dir_all(data_dir).unwrap_or(());
        }
        let diff = state
            .name_table
            .iter()
            .filter_map(|(k, v)| {
                (!::rstb::json::STOCK_NAMES.contains_key(k)).then(|| (*k, v.clone()))
            })
            .collect::<std::collections::HashMap<u32, String>>();
        fs::write(&name_file, serde_json::to_string(&diff).unwrap()).unwrap_or(());
    }
    Ok(())
}
