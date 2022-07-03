use once_cell::sync::Lazy;
pub(crate) use roead::yaz0::{compress, decompress_if};
use std::{collections::HashMap, path::Path, sync::Mutex};

pub(crate) static DECOMP_MAP: Lazy<Mutex<HashMap<usize, Vec<u8>>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

pub(crate) fn should_compress<P: AsRef<Path>>(file: P) -> bool {
    if let Some(ext) = file.as_ref().extension() {
        let ext = ext.to_str().unwrap();
        ext.starts_with('s') && ext != "sarc"
    } else {
        false
    }
}
