import glob
import json
import argparse
from PIL import Image

with open("config.json", "r") as f:
	conf = json.load(f)

def img_merge(args):
	with open(conf["info_path"], "r") as f:
		j = json.load(f)
	th = j["tileH"]
	tv = j["tileV"]
	tw = j["tileW"]
	out_img = Image.new('RGBA', (th*tw, tv*tw))
	for x in range(th):
		for y in range(tv):
			idx = j["tileLUT"][y*th+x]
			if idx < 0:
				continue
			tile = j["tileData"][idx]
			clut_fmt = f"{j['clut_hash']:08X}"
			bmp_fmt =  f"{tile:08X}"
			for match in glob.glob(conf["tile_import_path"]+clut_fmt+bmp_fmt+".png"):
				tmp = Image.open(match)
				out_img.paste(tmp, (x*32, y*32))
	out_img.save(conf["image_path"])

def img_split(args):
	with open(conf["info_path"], "r") as f:
		j = json.load(f)
	img = Image.open(conf["image_path"])
	th = j["tileH"]
	tv = j["tileV"]
	tw = img.width // th
	for x in range(0,img.width,tw):
		for y in range(0,img.height,tw):
			idx = j["tileLUT"][y//tw*th+x//tw]
			if idx < 0:
				continue
			tile = j["tileData"][idx]
			clut_fmt = f"{j['clut_hash']:08X}"
			bmp_fmt =  f"{tile:08X}"
			tile = img.crop( (x,y,x+tw,y+tw) )
			tile.save(conf["tile_export_path"] + f"00000000{clut_fmt}{bmp_fmt}.png")

parser = argparse.ArgumentParser()
actions = {"merge": img_merge, "split": img_split}
parser.add_argument("action", choices=actions)
args = parser.parse_args()
f = actions.get(args.action)
f(args)