#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pruefe_t1_bildbytes.py - Rechtliche & technische T1-Pruefung (Etappe 4)

Prueft vollautomatisch:
1. Dass weder NORDLANDTRILOGIE.EXE noch irgendeine Datei in Starter/release/,
   Starter/src/ oder Starter/einstellungen.ini ein nicht-triviales 64-Byte-Fenster
   aus den Original-Bilddateien von Schicksalsklinge, Sternenschweif oder
   Schatten ueber Riva enthaelt:
   - Rohbytes der Original-Bilddateien (.ULI, .AIF, KARTE.DAT)
   - Entpackte 320x200 Pixel-Bytes (indiziert)
   - 6-Bit-VGA-Paletten und 8-Bit-skalierte RGB-Paletten
2. Dass keine gecachten Bilddateien (.png, .bmp, .raw, .cache, .uli, .aif)
   in Starter/release/ oder Starter/einstellungen.ini abgelegt wurden.
"""

import collections
import json
import os
import struct
import sys

WINDOW_SIZE = 64


def win_to_host_path(p: str) -> str:
    if os.name != "nt" and len(p) >= 3 and p[1] == ":" and p[2] in ("\\", "/"):
        drive = p[0].lower()
        rest = p[3:].replace("\\", "/")
        return f"/{'mnt'}/{drive}/{rest}"
    return p


def is_nontrivial_window(w: bytes, is_raw: bool) -> bool:
    if len(w) != WINDOW_SIZE:
        return False
    counts = collections.Counter(w)
    most_common_count = counts.most_common(1)[0][1]
    if is_raw:
        return most_common_count <= 56 and len(counts) >= 4
    return most_common_count <= 52 and len(counts) >= 6


def decomp_rle7f(src: bytes, expected_len: int) -> bytes:
    out = bytearray()
    i = 0
    n = len(src)
    while i < n and (expected_len == 0 or len(out) < expected_len):
        b = src[i]
        if b == 0x7F and i + 2 < n:
            cnt = src[i + 1]
            val = src[i + 2]
            i += 3
            if expected_len > 0 and len(out) + cnt > expected_len:
                cnt = expected_len - len(out)
            out.extend([val] * cnt)
        else:
            out.append(b)
            i += 1
    return bytes(out)


def decomp_packbits(src: bytes, expected_len: int) -> bytes:
    out = bytearray()
    i = 0
    n = len(src)
    while i < n and (expected_len == 0 or len(out) < expected_len):
        c = struct.unpack_from("b", src, i)[0]
        i += 1
        if c >= 0:
            cnt = c + 1
            chunk = src[i:i + cnt]
            i += len(chunk)
            out.extend(chunk)
        elif c != -128:
            cnt = 1 - c
            if i < n:
                val = src[i]
                i += 1
                out.extend([val] * cnt)
    if expected_len > 0 and len(out) > expected_len:
        return bytes(out[:expected_len])
    return bytes(out)


def decode_uli(data: bytes):
    if len(data) < 26 or data[:3] != b"ULI":
        return b"", b"", b""
    comp_type = data[4]
    pal_colors = data[22] + 1
    pal_bytes = pal_colors * 3
    payload = data[26:]
    if comp_type == 0:
        unp = payload
    elif comp_type == 1:
        unp = decomp_rle7f(payload, 0)
    elif comp_type == 2:
        unp = decomp_packbits(payload, 0)
    else:
        return b"", b"", b""
    if len(unp) < pal_bytes + 8000:
        return b"", b"", b""
    pal6 = unp[:pal_bytes]
    pal8 = bytes(((v & 0x3F) << 2) | ((v & 0x3F) >> 4) for v in pal6)
    pix = unp[pal_bytes:pal_bytes + 64000]
    return pix, pal6, pal8


def decode_aif(data: bytes):
    if len(data) < 30 or data[:3] != b"AIF":
        return b"", b"", b""
    pack = data[4]
    no_pal = data[5]
    w, h, ncolors, _ = struct.unpack_from("<hhhh", data, 6)
    if w <= 0 or w > 640 or h <= 0 or h > 480:
        return b"", b"", b""
    pal_len = 0 if no_pal else max(0, ncolors) * 3
    if 30 + pal_len > len(data):
        return b"", b"", b""
    comp_data = data[30:len(data) - pal_len]
    pal6 = data[len(data) - pal_len:] if pal_len > 0 else b""
    pal8 = bytes(((v & 0x3F) << 2) | ((v & 0x3F) >> 4) for v in pal6) if pal6 else b""
    total = w * h
    if pack == 0:
        pix = comp_data[:total]
    elif pack == 1:
        pix = decomp_rle7f(comp_data, total)
    elif pack == 2:
        pix = decomp_packbits(comp_data, total)
    else:
        pix = b""
    return pix, pal6, pal8


def read_iso_file(iso_path: str, rel_path: str) -> bytes:
    if not os.path.isfile(iso_path):
        return b""
    with open(iso_path, "rb") as fp:
        def read_sec(lba: int, raw2352: bool, hdr: int) -> bytes:
            if raw2352:
                fp.seek(lba * 2352 + hdr)
            else:
                fp.seek(lba * 2048)
            return fp.read(2048)

        raw2352 = False
        hdr = 0
        pvd = read_sec(16, False, 0)
        if pvd[1:6] != b"CD001":
            for cand in (16, 24):
                pvd = read_sec(16, True, cand)
                if pvd[1:6] == b"CD001":
                    raw2352 = True
                    hdr = cand
                    break
            else:
                return b""

        cur_lba = struct.unpack_from("<I", pvd, 156 + 2)[0]
        cur_size = struct.unpack_from("<I", pvd, 156 + 10)[0]
        parts = [p for p in rel_path.replace("\\", "/").split("/") if p]
        for idx, part in enumerate(parts):
            is_last = idx == len(parts) - 1
            nsecs = (cur_size + 2047) // 2048
            dir_buf = b"".join(read_sec(cur_lba + s, raw2352, hdr) for s in range(min(nsecs, 64)))
            pos = 0
            found = False
            while pos < len(dir_buf):
                rlen = dir_buf[pos]
                if rlen == 0:
                    pos = ((pos // 2048) + 1) * 2048
                    continue
                if pos + rlen > len(dir_buf) or rlen < 34:
                    break
                elba = struct.unpack_from("<I", dir_buf, pos + 2)[0]
                esize = struct.unpack_from("<I", dir_buf, pos + 10)[0]
                eflags = dir_buf[pos + 25]
                nlen = dir_buf[pos + 32]
                ename = dir_buf[pos + 33:pos + 33 + nlen].split(b";", 1)[0].decode("latin1", errors="ignore").rstrip(".")
                if ename.upper() == part.upper():
                    if is_last or (eflags & 2):
                        cur_lba = elba
                        cur_size = esize
                        found = True
                        break
                pos += rlen
            if not found:
                return b""
        nsecs = (cur_size + 2047) // 2048
        out = bytearray()
        for s in range(nsecs):
            sec_data = read_sec(cur_lba + s, raw2352, hdr)
            take = min(2048, cur_size - len(out))
            out.extend(sec_data[:take])
        return bytes(out)


def load_dsa1_blobs(dsa1_dir: str):
    blobs = []
    dir_p = os.path.join(dsa1_dir, "INTRODAT.DIR")
    vol_p = os.path.join(dsa1_dir, "INTRODAT.VOL")
    if os.path.isfile(dir_p) and os.path.isfile(vol_p):
        d = open(dir_p, "rb").read()
        v = open(vol_p, "rb").read()
        for i in range(0, len(d) - 31, 32):
            nlen = d[i]
            if 1 <= nlen <= 12:
                name = d[i + 1:i + 1 + nlen].decode("latin1", errors="ignore")
                off = struct.unpack_from("<I", d, i + 26)[0]
                sz = struct.unpack_from("<H", d, i + 30)[0]
                if name.upper() in ("DSAART.ULI", "TITLE.ULI", "DSATIT.ULI", "TLOGO.ULI") and sz > 0:
                    chunk = v[off:off + sz]
                    blobs.append((f"DSA1:INTRODAT.VOL:{name}(raw)", chunk, True))
                    pix, pal6, pal8 = decode_uli(chunk)
                    if pix:
                        blobs.append((f"DSA1:INTRODAT.VOL:{name}(pix)", pix, False))
                    if pal6:
                        blobs.append((f"DSA1:INTRODAT.VOL:{name}(pal6)", pal6, False))
                        blobs.append((f"DSA1:INTRODAT.VOL:{name}(pal8)", pal8, False))

    schick_p = os.path.join(dsa1_dir, "SCHICK.DAT")
    if os.path.isfile(schick_p):
        with open(schick_p, "rb") as fp:
            offs = fp.read(32)
            off5 = struct.unpack_from("<I", offs, 5 * 4)[0]
            off6 = struct.unpack_from("<I", offs, 6 * 4)[0]
            if off6 > off5:
                fp.seek(off5)
                chunk = fp.read(off6 - off5)
                blobs.append(("DSA1:SCHICK.DAT:KARTE#5(raw)", chunk, True))
    return blobs


def load_dsa2_blobs(dsa2_dir: str):
    blobs = []
    star_p = os.path.join(dsa2_dir, "DATA", "STAR.DAT")
    if os.path.isfile(star_p):
        data = open(star_p, "rb").read()
        cnt = struct.unpack_from("<I", data, 0)[0]
        hdr_base = 24842
        for i in range(cnt - 1):
            rec = data[4 + i * 20:4 + (i + 1) * 20]
            name = rec[:14].split(b"\x00", 1)[0].decode("latin1", errors="ignore")
            off = struct.unpack_from("<I", rec, 14)[0]
            flg = struct.unpack_from("<H", rec, 18)[0]
            if flg == 1 and name.upper() in ("LOWANGEN.AIF", "CREDITS.AIF"):
                next_off = len(data) - hdr_base
                for j in range(i + 1, cnt - 1):
                    o2 = struct.unpack_from("<I", data, 4 + j * 20 + 14)[0]
                    f2 = struct.unpack_from("<H", data, 4 + j * 20 + 18)[0]
                    if f2 == 1 and o2 > off:
                        next_off = o2
                        break
                chunk = data[hdr_base + off:hdr_base + next_off]
                blobs.append((f"DSA2:STAR.DAT:{name}(raw)", chunk, True))
                pix, pal6, pal8 = decode_aif(chunk)
                if pix:
                    blobs.append((f"DSA2:STAR.DAT:{name}(pix)", pix, False))
                if pal6:
                    blobs.append((f"DSA2:STAR.DAT:{name}(pal6)", pal6, False))
                    blobs.append((f"DSA2:STAR.DAT:{name}(pal8)", pal8, False))

    iso_p = os.path.join(dsa2_dir, "gamea.gog")
    star_cd = read_iso_file(iso_p, "DATA/STAR.DAT")
    if len(star_cd) > 24844:
        cnt = struct.unpack_from("<I", star_cd, 0)[0]
        hdr_base = 24842
        for i in range(cnt - 1):
            rec = star_cd[4 + i * 20:4 + (i + 1) * 20]
            name = rec[:14].split(b"\x00", 1)[0].decode("latin1", errors="ignore")
            if name.upper() in ("DSA.AIF", "ARTWORK.AIF", "FLAME1.AIF"):
                off = struct.unpack_from("<I", rec, 14)[0]
                next_off = (
                    struct.unpack_from("<I", star_cd, 4 + (i + 1) * 20 + 14)[0]
                    if (i + 1 < cnt - 1)
                    else (len(star_cd) - hdr_base)
                )
                chunk = star_cd[hdr_base + off:hdr_base + next_off]
                blobs.append((f"DSA2:gamea.gog:{name}(raw)", chunk, True))
                pix, pal6, pal8 = decode_aif(chunk)
                if pix:
                    blobs.append((f"DSA2:gamea.gog:{name}(pix)", pix, False))
                if pal6:
                    blobs.append((f"DSA2:gamea.gog:{name}(pal6)", pal6, False))
                    blobs.append((f"DSA2:gamea.gog:{name}(pal8)", pal8, False))
    return blobs


def load_dsa3_blobs(dsa3_dir: str):
    blobs = []
    alf_p = os.path.join(dsa3_dir, "DATA", "RIVA.ALF")
    if os.path.isfile(alf_p):
        with open(alf_p, "rb") as fp:
            hdr = fp.read(48)
            cnt = struct.unpack_from("<H", hdr, 8)[0]
            dir_off = struct.unpack_from("<I", hdr, 10)[0]
            data_base = struct.unpack_from("<I", hdr, 16)[0]
            fp.seek(dir_off)
            dir_buf = fp.read(cnt * 28)
            for i in range(cnt):
                rec = dir_buf[i * 28:(i + 1) * 28]
                name = rec[:14].split(b"\x00", 1)[0].decode("latin1", errors="ignore")
                sz = struct.unpack_from("<I", rec, 14)[0]
                off = struct.unpack_from("<I", rec, 24)[0]
                if name.upper() == "GPMASK00.AIF" and sz >= 30:
                    fp.seek(data_base + off)
                    chunk = fp.read(sz)
                    blobs.append(("DSA3:RIVA.ALF:GPMASK00.AIF(raw)", chunk, True))
                    pix, pal6, pal8 = decode_aif(chunk)
                    if pix:
                        blobs.append(("DSA3:RIVA.ALF:GPMASK00.AIF(pix)", pix, False))
                    if pal6:
                        blobs.append(("DSA3:RIVA.ALF:GPMASK00.AIF(pal6)", pal6, False))
                        blobs.append(("DSA3:RIVA.ALF:GPMASK00.AIF(pal8)", pal8, False))
                    break

    iso_p = os.path.join(dsa3_dir, "game.gog")
    chunk = read_iso_file(iso_p, "DATA/SCHATTEN.AIF")
    if chunk:
        blobs.append(("DSA3:game.gog:SCHATTEN.AIF(raw)", chunk, True))
        pix, pal6, pal8 = decode_aif(chunk)
        if pix:
            blobs.append(("DSA3:game.gog:SCHATTEN.AIF(pix)", pix, False))
        if pal6:
            blobs.append(("DSA3:game.gog:SCHATTEN.AIF(pal6)", pal6, False))
            blobs.append(("DSA3:game.gog:SCHATTEN.AIF(pal8)", pal8, False))
    return blobs


def main():
    starter_dir = os.path.dirname(os.path.abspath(__file__))
    spiele_json_path = os.path.join(starter_dir, "spiele.json")
    gog_dirs = {}
    if os.path.isfile(spiele_json_path):
        cfg = json.load(open(spiele_json_path, "r", encoding="utf-8"))
        for g in cfg.get("spiele", []):
            gid = g.get("id", "")
            for p in g.get("gog_pfade", []):
                hp = win_to_host_path(p)
                if os.path.isdir(hp):
                    gog_dirs[gid] = hp
                    break

    print("=== T1 Rechtliche Pruefung: 64-Byte-Fenster aus Original-Bilddateien ===")
    blobs = []
    if "schicksalsklinge" in gog_dirs:
        blobs.extend(load_dsa1_blobs(gog_dirs["schicksalsklinge"]))
    if "sternenschweif" in gog_dirs:
        blobs.extend(load_dsa2_blobs(gog_dirs["sternenschweif"]))
    if "riva" in gog_dirs:
        blobs.extend(load_dsa3_blobs(gog_dirs["riva"]))

    if not blobs:
        print("FEHLER: Keine Original-Bilddateien fuer den Vergleich gefunden!", file=sys.stderr)
        return 2

    print(f"Geladene Original-Bilddatenbloecke (roh + entpackt + Paletten): {len(blobs)}")

    window_map = {}
    for label, data, is_raw in blobs:
        if len(data) < WINDOW_SIZE:
            continue
        for i in range(len(data) - WINDOW_SIZE + 1):
            w = data[i:i + WINDOW_SIZE]
            if is_nontrivial_window(w, is_raw) and w not in window_map:
                window_map[w] = f"{label}+0x{i:X}"

    print(f"Eindeutige nicht-triviale 64-Byte-Fenster aus Originalbildern: {len(window_map):,}")

    targets = [
        os.path.join(starter_dir, "build", "NORDLANDTRILOGIE.EXE"),
        os.path.join(starter_dir, "einstellungen.ini"),
        os.path.join(starter_dir, "spiele.json"),
    ]
    for sub in ("src", "release", os.path.join("trilogie", "Nordlandtrilogie")):
        subdir = os.path.join(starter_dir, sub)
        if os.path.isdir(subdir):
            for root, _, files in os.walk(subdir):
                for fn in sorted(files):
                    targets.append(os.path.join(root, fn))

    total_hits = 0
    forbidden_ext = (".png", ".bmp", ".gif", ".jpg", ".jpeg", ".uli", ".aif", ".nvf", ".cache")

    for t in targets:
        if not os.path.isfile(t):
            continue
        rel = os.path.relpath(t, os.path.dirname(starter_dir))
        if (rel.startswith("Starter/release/") or rel.startswith("Starter/trilogie/Nordlandtrilogie/")) and t.lower().endswith(forbidden_ext):
            print(f"  VERBOTENE BILD-/CACHEDATEI in Release: {rel}")
            total_hits += 1

        content = open(t, "rb").read()
        file_hits = 0
        if len(content) >= WINDOW_SIZE:
            for i in range(len(content) - WINDOW_SIZE + 1):
                w = content[i:i + WINDOW_SIZE]
                if w in window_map:
                    if file_hits < 5:
                        print(f"  TREFFER in {rel} @ 0x{i:X} -> {window_map[w]}")
                    file_hits += 1
                    total_hits += 1
        print(f"  Geprueft: {rel:<48} ({len(content):>10,} Bytes) -> {file_hits} Treffer")

    print(f"=== ERGEBNIS T1-PRUEFUNG: {total_hits} Treffer (64-Byte-Fenster & Bild-Cache) ===")
    return 0 if total_hits == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
