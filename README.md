# Installation
This project was built using Python 3.8 \
Install the required third-party libraries by running
`pip install -r requirements.txt` \
Set "tile_import_path" within config.json to the folder containing PPSSPP texture dumps
# Usage
Unpack the contents of data.cpk and locate the "pack" folder \
Generate the texture hash database by typing
`db.py build <path to pack folder>` \
Generate tiles.json file containing tile info for a given texture by typing
`db.py query <path to PPSSPP-dumped PNG texture>` \
Use img.py for image manipulation
## Splitting:
`img.py split` \
Takes the file "image.png" and chops it into correctly named tiles in the "cropped" folder
## Merging:
`img.py merge` \
Grabs PNG files from texture dump directory and outputs them to "image.png"
## Additinonal Credits
LZSS0 code: [QuickBMS by Luigi Auriemma](aluigi.altervista.org/quickbms.htm) \
quick texture hash code: [PPSSPP](https://github.com/hrydgard/ppsspp)
