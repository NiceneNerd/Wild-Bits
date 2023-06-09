use once_cell::sync::Lazy;
pub(crate) use roead::yaz0::{compress, decompress_if};
use std::{collections::HashMap, path::Path, sync::Mutex};

pub(crate) static DECOMP_MAP: Lazy<Mutex<HashMap<usize, Vec<u8>>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

pub(crate) static FILES: Lazy<HashMap<u32, &str>> = Lazy::new(|| {
    static DATA: Lazy<Vec<u8>> =
        Lazy::new(|| include_bytes_zstd::include_bytes_zstd!("data/files.txt", 10));
    unsafe { std::str::from_utf8_unchecked(&DATA) }
        .lines()
        .map(|line| (roead::aamp::hash_name(line), line))
        .collect()
});

pub(crate) fn should_compress<P: AsRef<Path>>(file: P) -> bool {
    if let Some(ext) = file.as_ref().extension() {
        let ext = ext.to_str().unwrap();
        ext.starts_with('s') && ext != "sarc"
    } else {
        false
    }
}
