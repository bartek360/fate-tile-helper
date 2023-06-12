import argparse, json, os, sqlite3, struct, xxhash
from array import array
import fate

def get_dim(w,h):
	return (w.bit_length() - 1) | (h.bit_length() - 1) << 8 | 0xF0

def hashToCacheKey(clutHash_, palFmt):
	step1 = (clutHash_ ^ 0xC5000000) # gstate.clutformat << 24
	step2 = step1 ^ palFmt
	dim = get_dim(1024, 32)
	step3 = step2 ^ (dim ^ 0xFFFF)
	return step3

def db_query(args):
	conn = sqlite3.connect("texhashes.sqlite")
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	name = os.path.basename(args.input)
	clut = name[8:16]
	bmp = name[16:24]
	c.execute('''SELECT * FROM hashes JOIN files on tex_id = file_id
	WHERE clut_hash = 0x''' + clut + " and bmp_hash = 0x" + bmp)
	rows = c.fetchall()
	print(f"Found {len(rows)} match(es) for C:{clut} B:{bmp}")
	if len(rows):
		row = rows[0]
		print(f"tile #{row[1]:4} in {row[4]}")
		out = {k: row[k] for k in row.keys()}
		lut = array('h')
		lut.frombytes(row["tileLUT"])
		out["tileLUT"] = lut.tolist()
		with open("tiles.json", "w") as infofile:
			c.execute(f"SELECT * FROM hashes WHERE tex_id = {row[3]}")
			tiles = c.fetchall()
			out["tileData"] = [ tile["bmp_hash"] for tile in tiles ]
			json.dump(out, infofile)
	c.close()

def db_build(args):
	fate.init_lzss0()
	# fate.init_hash()
	conn = sqlite3.connect("texhashes.sqlite")
	directory = os.fsencode(args.input)
	c = conn.cursor()
	c.execute('''DROP TABLE IF EXISTS hashes''')
	c.execute('''DROP TABLE IF EXISTS files''')
	c.execute('''CREATE TABLE files (
	file_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	path TEXT, clut_hash INTEGER,
	tileLUT BLOB,
	tileH INTEGER,
	tileV INTEGER,
	tileW INTEGER,
	tileSize INTEGER,
	tileNumBlits INTEGER,
	tileNumUniqueBlits INTEGER
	)''')
	c.execute('''CREATE TABLE hashes (
	bmp_hash INTEGER, tile_index INTEGER, tex_id INTEGER,
	FOREIGN KEY(tex_id) REFERENCES files(file_id)
	)''')
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if filename.endswith(".cmp"):
			cmp = fate.load_cmp(os.fsdecode(directory) + "\\" + filename)
			pak = fate.load_pak(None, cmp)
		elif filename.endswith("pak"):
			pak = fate.load_pak(os.fsdecode(directory) + "\\" + filename)
		else:
			continue
		for txb in [f for f in pak if f[0].endswith(".txb")]:
			txb_data = fate.load_pak(None, txb[1])
			for texIdx, txbEntry in enumerate(txb_data):
				if txbEntry[0] is None:
					txbEntry = ("NONAMETEX_%d" % texIdx, txbEntry[1])
				path = ':'.join((filename,txb[0],txbEntry[0]))
				tex = fate.TEXFile()
				if tex.from_bytes(txbEntry[1], True) is None:
					continue
				hash = xxhash.xxh32(tex.palData, seed=0xC0108888)
				cluthash = hashToCacheKey(hash.intdigest(),tex.palType)
				c.execute('''INSERT INTO files VALUES(NULL,?,?,?,?,?,?,?,?,?)''',
					(path, cluthash, tex.tileLUT, tex.tileH, tex.tileV,
					tex.tileW, tex.tileSize, tex.tileNumBlits,
					tex.tileNumUniqueBlits))
				ts = tex.tileSize
				for i in range(tex.tileNumUniqueBlits):
					texhash = xxhash.xxh64(tex.texData[i*ts:i*ts+ts], seed=0xBACD7814)
					# texhash = fate.quick(tex.texData[i*ts:i*ts+ts])
					c.execute('''INSERT INTO hashes(bmp_hash, tile_index, tex_id)
					VALUES (?,?,(SELECT seq FROM sqlite_sequence WHERE name="files"))''',
						(texhash.intdigest() & 0xFFFFFFFF, i))
	conn.commit()
	c.close()

parser = argparse.ArgumentParser()
actions = {"query": db_query, "build": db_build}
parser.add_argument("action", choices=actions)
parser.add_argument("input", help="PNG path for query, pack folder for build")
args = parser.parse_args()
f = actions.get(args.action)
f(args)