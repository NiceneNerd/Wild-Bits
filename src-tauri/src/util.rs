use lazy_static::lazy_static;
pub(crate) use roead::yaz0::{compress, decompress, decompress_if};
use std::{
    collections::HashMap,
    path::Path,
    sync::Mutex,
};

lazy_static! {
    pub(crate) static ref DECOMP_MAP: Mutex<HashMap<usize, Vec<u8>>> = Mutex::new(HashMap::new());
}

pub(crate) fn should_compress<P: AsRef<Path>>(file: P) -> bool {
    if let Some(ext) = file.as_ref().extension() {
        let ext = ext.to_str().unwrap();
        ext.starts_with('s') && ext != "sarc"
    } else {
        false
    }
}
