# Wild Bits
Simple editor for BOTW file formats

## Setup

Requires the latest (2019) Visual C++ redistributable for x64, downloadable 
[here](https://aka.ms/vs/16/release/vc_redist.x64.exe).

Install Python 3.7+ (**64-bit version**), then run `pip install wildbits`.

## Usage

To run Wild Bits, type `wildbits` into your command console. Alternatively, run `python -m wildbits`.

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

### YAML Editor

![YAML editor preview](https://i.imgur.com/AamxY5Q.png)
*Preview of the YAML editor*

Other formats that Wild Bits supports, namely BYML, AAMP, and MSBT, are edited
using the YAML editor. It works as a normal text/code editor but automatically
handles conversion between the binary formats and YAML representation. Basic
autocomplete is also provided.

## Known Issues

With some system configurations, the `wildbits` command does not work properly,
and the app must be launched with `python -m wildbits`.

## Building from Source

Building from source requires, in *addition* to the general prerequisites:

-   Node.js v14
-   The following Python packages:
    -   botw-utils >= 0.2.2
    -   oead >= 1.1.1
    -   rstb >= 1.2.0
    -   pymsyt >= 0.1.5
    -   xxhash ~= 1.4.3
    -   pywebview ~= 3.2

To build from source, you will first need to prepare the webpack bundle. Enter
the `wildbits/assets` folder, run `npm install` to collect dependencies, and then
run `npm build` or `npm test`.

Finally, back at the root folder, you can install using
`python setup.py install`. You can also run without installing by using `python -m wildbits`.
