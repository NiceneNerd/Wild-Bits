use std::path::Path;

use crate::{AppError, State, Result, Rstb};
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

fn rstb_to_json(table: &ResourceSizeTable) -> Value {
    Value::Object(
        table
            .hash_entries()
            .map(|(h, v)| {
                (
                    rstb::json::string_from_hash(*h),
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
        "rstb": rstb_to_json(&table.table),
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
            path.extension().unwrap().to_string_lossy().starts_with("s"),
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
pub(crate) fn set_size(
    state: State<'_>,
    path: String,
    size: u32,
) -> Result<()> {
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
