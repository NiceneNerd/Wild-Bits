# Wild Bits
Simple editor for BOTW file formats

## Setup

Requires the latest (2019) Visual C++ redistributable for x64, downloadable 
[here](https://aka.ms/vs/16/release/vc_redist.x64.exe).

Download the release executable and run it.

## Usage

Wild Bits can edit most of the commonly modded, non-graphical file types in
*The Legend of Zelda: Breath of the Wild*, including SARC archives, the
[Resource Size Table](https://zeldamods.org/wiki/Resource_system#Resource_size_table)
(RSTB), and BYML, AAMP, and MSBT files. Most of the formats are handled by the
powerful and reliable [oead](https://github.com/zeldamods/oead) library, which
ensures accuracy and compatibility with the game.

General usage notes: Wild Bits handles yaz0 compression/decompression
automatically. Yaz0 compressed files are automatically decompressed, and when
saving Wild Bits will determine whether to yaz0 compress based on whether the
file extension has the additonal `.s` prefix. Big/little endian differences are
also mostly handled automatically.

### SARC Editor

![SARC editor preview](https://i.imgur.com/iRG9HYf.png)
*Preview of SARC editor*

The SARC editor allows you to edit SARC files, e.g. `.sbactorpack`, `.pack`,
`.ssarc`, etc. Once opened, the file contents will be displayed as tree view.
Nested SARCs expand like folders and will be automatically repacked correctly.
You can extract all files, update the contents from a source folder, add new
files, or extract/rename/delete any individual file in the SARC. File types
supported by the YAML editor can also be edited directly and saved to the open
SARC. Recognized BOTW files in the SARC which have been modified from the stock
copies are highlighted in yellow for easy identification.

### RSTB Editor

![RSTB editor preview](https://i.imgur.com/fS8zVnt.png)
*Preview of RSTB editor*

The RSTB editor can open a BOTW resource size table file, usually named
`ResourceSizeTable.product.srsizetable`. It lists all of the resource entries
with the option to edit or delete them. You can also add new entries. When
adding or editing an entry, you have the option to calculate the correct value
by providing the resource file. Resource types that cannot be calculated or
estimated will return "0" from the calculator.

To find a specific entry, you can filter the list with the search box at the
bottom of the UI, or you can use the Search button. The filter box will search
any part of a file name, whereas the Search button requires an exact resource
path.

If you cannot find an expected resource, note that entries for files not known
from BOTW will appear as "Unknown" with their hash to identify them. Entries
added by Wild Bits will be added to a list of recognized names, and so will full
paths provided to the Search function (*not* the filter box).

There is also a Scan Mod button to automatically add all canonical paths from
the resources in a mod directory to the name table.

### YAML Editor

![YAML editor preview](https://i.imgur.com/AamxY5Q.png)
*Preview of the YAML editor*

Other formats that Wild Bits supports, namely BYML, AAMP, and MSBT, are edited
using the YAML editor. It works as a normal text/code editor but automatically
handles conversion between the binary formats and YAML representation. Basic
autocomplete is also provided.

## Known Issues

Presently none.

## Building from Source

Building from source requires, in *addition* to the general prerequisites:

-   Node.js v16
-   Rust/Cargo (MSRV 1.61)

Wild Bits is a Tauri app, so you can install the Tauri CLI with `npm i -g @tauri-apps/cli` or `cargo install tauri-cli`. Then run `npm install` to install the NPM packages. From there `tauri dev` will launch Wild Bits in development mode (dev tools enabled and "hot-ish" reloading), and `tauri build` will compile a release build.
