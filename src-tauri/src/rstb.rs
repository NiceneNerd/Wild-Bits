use std::path::Path;

use crate::{Result, Rstb};
use rstb::ResourceSizeTable;
use std::fs;
use tauri::command;

fn parse_rstb<P: AsRef<Path>>(file: P) -> Result<Rstb> {
  let data = fs::read(file.as_ref()).map_err(|_| "Could not read file".to_owned())?;
  for endian in &[rstb::Endian::Big, rstb::Endian::Little] {
    let table =
      ResourceSizeTable::from_binary(data, *endian).map_err(|_| "Invalid RSTB file".to_owned())?;
    let randoms = [
      "EventFlow/PictureMemory.bfevfl",
      "Camera/Demo648_0/C04-0.bcamanim",
      "Effect/FldObj_ScaffoldIronParts_A_01.esetlist",
      "Physics/TeraMeshRigidBody/MainField/9-8.hktmrb",
    ];
    if randoms.iter().any(|e| table.is_in_table(e)) {
      return Ok(Rstb {
        table,
        be: matches!(endian, rstb::Endian::Big),
      });
    }
  }
  Err("Invalid RSTB file".into())
}
