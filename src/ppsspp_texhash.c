#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned int u32;
typedef unsigned short u16;
// from PPSSPP TextureDecoder.cpp
u32 __declspec(dllexport) QuickTexHashNonSSE(const void *checkp, u32 size) {
	u32 check = 0;

	if (((intptr_t)checkp & 0xf) == 0 && (size & 0x3f) == 0) {
		static const u16 cursor2_initial[8] = {0xc00bU, 0x9bd9U, 0x4b73U, 0xb651U, 0x4d9bU, 0x4309U, 0x0083U, 0x0001U};
		typedef union u32x4_u16x8_t {
			u32 x32[4];
			u16 x16[8];
		} u32x4_u16x8;
		u32x4_u16x8 cursor;
		memset(&cursor,0,sizeof(u32x4_u16x8));
		u32x4_u16x8 cursor2;
		static const u16 update[8] = {0x2455U, 0x2455U, 0x2455U, 0x2455U, 0x2455U, 0x2455U, 0x2455U, 0x2455U};

		for (u32 j = 0; j < 8; ++j) {
			cursor2.x16[j] = cursor2_initial[j];
		}

		const u32x4_u16x8 *p = (const u32x4_u16x8 *)checkp;
		for (u32 i = 0; i < size / 16; i += 4) {
			for (u32 j = 0; j < 8; ++j) {
				const u16 temp = p[i + 0].x16[j] * cursor2.x16[j];
				cursor.x16[j] += temp;
			}
			for (u32 j = 0; j < 4; ++j) {
				cursor.x32[j] ^= p[i + 1].x32[j];
				cursor.x32[j] += p[i + 2].x32[j];
			}
			for (u32 j = 0; j < 8; ++j) {
				const u16 temp = p[i + 3].x16[j] * cursor2.x16[j];
				cursor.x16[j] ^= temp;
			}
			for (u32 j = 0; j < 8; ++j) {
				cursor2.x16[j] += update[j];
			}
		}

		for (u32 j = 0; j < 4; ++j) {
			cursor.x32[j] += cursor2.x32[j];
		}
		check = cursor.x32[0] + cursor.x32[1] + cursor.x32[2] + cursor.x32[3];
	} else {
		const u32 *p = (const u32 *)checkp;
		for (u32 i = 0; i < size / 8; ++i) {
			check += *p++;
			check ^= *p++;
		}
	}

	return check;
}