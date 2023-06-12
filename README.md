# Fate Tile Helper

## Installation
* This project was built using Python 3.8
* Install the required third-party libraries:
```
pip install -r requirements.txt
```
* Set "tile_import_path" within *config.json* to the folder containing PPSSPP texture dumps
## Usage
* Unpack the contents of data.cpk and locate the *pack* folder
* Generate the texture hash database:
```
db.py build <path to pack folder>
```
* Generate tiles.json file containing tile info for a given texture:
```
db.py query <path to PPSSPP-dumped PNG texture>
```
* Use img.py for image manipulation
### Splitting:
`img.py split` takes the file *image.png* and chops it into correctly named tiles in the *cropped* folder
### Merging:
`img.py merge` joins tiles from the texture dump directory and outputs the result to *image.png*
## Additional Credits
LZSS0 code: [QuickBMS by Luigi Auriemma](http://aluigi.altervista.org/quickbms.htm) \
quick texture hash code: [PPSSPP](https://github.com/hrydgard/ppsspp)
