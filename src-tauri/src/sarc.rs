use crate::{util, AppError, AppState, Result};
use sarc_rs::{Endian, File, Sarc, SarcWriter};
use serde_json::{json, Map, Value};
use std::{collections::{HashMap, HashSet}, fs, path::PathBuf, sync::Mutex};

// #[derive(Debug, Clone, PartialEq)]
// struct SarcTree(HashMap<String, SarcFile>);

// impl SarcTree {

// }

// #[derive(Debug, Clone, PartialEq)]
// enum SarcFile {
//     Data(Vec<u8>),
//     Sarc(SarcTree)
// }

fn create_tree(sarc: &Sarc) -> Result<(Map<String, Value>, HashSet<String>)> {
    let mut modified_files: HashSet<String> = HashSet::new();
    let mut tree: Map<String, Value> = Map::new();
    for file in sarc.files() {
        if let Some(name) = file.name {
            let path_parts: Vec<&str> = name.split('/').collect();
            let magic = &file.data[0..4];
            let mut nest_tree: Map<String, Value> = Map::new();
            if magic == b"SARC" || (magic == b"Yaz0" && &file.data[0x11..0x15] == b"SARC") {
                let nest_sarc = Sarc::new(file.data)
                    .map_err(|_| AppError::from("Could not read nested SARC"))?;
                let result = create_tree(&nest_sarc)?;
                nest_tree.extend(result.0.iter().map(|(s, v)| (s.to_owned(), v.clone())));
                modified_files.extend(result.1);
            }
            tree_merge(
                &mut tree,
                &path_parts.iter().rev().fold(nest_tree, |res, cur| {
                    let mut map: Map<String, Value> = Map::new();
                    map.insert(cur.to_string(), Value::Object(res.to_owned()));
                    map
                }),
            );
        }
    }
    Ok((tree, modified_files))
}

#[tauri::command(async)]
pub(crate) fn open_sarc(state: tauri::State<'_, Mutex<AppState>>, file: String) -> Result<Value> {
    let mut data = fs::read(&file).map_err(|_| AppError::from("Failed to read file"))?;
    if &data[0..4] == b"Yaz0" {
        data = util::decompress(&data)?;
    }
    let sarc: Sarc = Sarc::new(data).map_err(|_| AppError::from("Could not read SARC"))?;
    let (tree, modified) = create_tree(&sarc).map_err(|_| AppError::from("Failed to make tree"))?;
    let res = json!({
        "modded": modified,
        "sarc": Value::Object(tree),
        "be": matches!(sarc.endian(), Endian::Big)
    });
    state.lock().unwrap().open_sarc = Some(sarc);
    Ok(res)
}

#[tauri::command(async)]
pub(crate) fn save_sarc(state: tauri::State<'_, Mutex<AppState>>, file: String) -> Result<()> {
    let file = PathBuf::from(file);
    let mut writer = SarcWriter::from_sarc(state.lock().unwrap().open_sarc.as_ref().unwrap());
    let data = writer.write_to_bytes().map_err(|_| AppError::from("Failed to build SARC"))?;
    fs::write(
        &file,
        {
            if util::should_compress(&file) {
                util::compress(&data)?
            } else {
                data
            }
        }
    )
    .map_err(|_| AppError::from("Failed to write SARC file"))?;
    Ok(())
}

fn tree_merge(dict: &mut serde_json::Map<String, Value>, dict2: &serde_json::Map<String, Value>) {
    for key in dict2.keys() {
        if dict.contains_key(key) && dict[key].is_object() && dict2[key].is_object() {
            tree_merge(
                dict.get_mut(key).unwrap().as_object_mut().unwrap(),
                &dict2[key].as_object().unwrap(),
            );
        } else if dict.contains_key(key) && dict[key].is_array() && dict2[key].is_array() {
            dict[key]
                .as_array_mut()
                .unwrap()
                .extend(dict2[key].as_array().unwrap().into_iter().cloned());
        } else {
            dict.insert(key.to_owned(), dict2[key].clone());
        }
    }
}
