use crate::{AppError, Result};
use lazy_static::lazy_static;
use std::{
    collections::HashMap,
    io::{BufWriter, Cursor},
    path::Path,
    sync::Mutex,
};
use yaz0::*;

pub(crate) fn decompress<B: AsRef<[u8]>>(data: B) -> Result<Vec<u8>> {
    let data = data.as_ref();
    let mut decomp =
        Yaz0Archive::new(Cursor::new(&data)).map_err(|_| AppError::from("Failed to decompress"))?;
    Ok(decomp
        .decompress()
        .map_err(|_| AppError::from("Failed to decompress"))?)
}

lazy_static! {
    pub(crate) static ref DECOMP_MAP: Mutex<HashMap<usize, Vec<u8>>> = Mutex::new(HashMap::new());
}

pub(crate) fn decompress_if<'a>(data: &'a [u8]) -> Result<&'a [u8]> {
    if &data[0..4] == b"Yaz0" {
        let decomp = decompress(data)?;
        let mut map = DECOMP_MAP.lock().unwrap();
        map.insert(data.as_ptr() as usize, decomp);
        Ok(unsafe {
            std::mem::transmute::<&'_ Vec<u8>, &'static Vec<u8>>(
                map.get(&(data.as_ptr() as usize)).unwrap(),
            )
        })
    } else {
        Ok(data)
    }
}

pub(crate) fn compress<B: AsRef<[u8]>>(data: B) -> Result<Vec<u8>> {
    let mut compressed: Vec<u8> = Vec::with_capacity(data.as_ref().len());
    let mut buffer = BufWriter::new(&mut compressed);
    let writer = Yaz0Writer::new(&mut buffer);
    writer
        .compress_and_write(data.as_ref(), CompressionLevel::Lookahead { quality: 6 })
        .map_err(|_| AppError::from("Failed to compress"))?;
    drop(buffer);
    Ok(compressed)
}

pub(crate) fn should_compress<P: AsRef<Path>>(file: P) -> bool {
    if let Some(ext) = file.as_ref().extension() {
        let ext = ext.to_str().unwrap();
        ext.starts_with('s') && ext != "sarc"
    } else {
        false
    }
}
