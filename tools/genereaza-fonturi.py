#!/usr/bin/env python3
"""
Generează fonturile bitmap pentru previzualizarea din ntc-display.html.

Glifele sunt randate cu FreeType exact ca în ESPHome (componenta `font`,
bpp = 1): aceeași dimensiune în pixeli, același mod mono, aceleași offseturi
și aceeași împachetare a biților. Astfel textul din preview e identic, pixel
cu pixel, cu cel de pe OLED.

Rulează-l doar dacă modifici fonturile/glifele din esphome/senzor-ntc.yaml:

    pip install freetype-py
    python3 tools/genereaza-fonturi.py <director_cu_ttf> custom_components/casa_3d/frontend/ntc-display.html

<director_cu_ttf> conține Roboto@400@False@v1.ttf și Roboto@700@False@v1.ttf
(le găsești în .esphome/font/ după prima compilare ESPHome).
"""
import base64
import json
import re
import sys
from pathlib import Path

import freetype

TEXT = (
    " !\"#%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]_"
    "abcdefghijklmnopqrstuvwxyz°…ĂÂÎȘȚăâîșțŞşŢţΩ"
)

# Trebuie să corespundă blocului `font:` din senzor-ntc.yaml
FONTURI = {
    "mare": ("Roboto@700@False@v1.ttf", 28, "0123456789.-°CF"),
    "mediu": ("Roboto@700@False@v1.ttf", 14, TEXT),
    "mic": ("Roboto@400@False@v1.ttf", 10, TEXT),
}


def px(v):  # identic cu pt_to_px din ESPHome
    return v // 64


def randeaza(face, size, ch):
    face.set_pixel_sizes(size, 0)
    face.load_char(ch, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
    bmp = face.glyph.bitmap
    w, h, pitch, buf = bmp.width, bmp.rows, bmp.pitch, bmp.buffer
    data = bytearray((w * h + 7) // 8)
    pos = 0
    for y in range(h):
        for x in range(w):
            if buf[y * pitch + x // 8] & (1 << (7 - x % 8)):
                data[pos // 8] |= 0x80 >> (pos % 8)
            pos += 1
    asc = px(face.size.ascender)
    return [
        ord(ch),
        px(face.glyph.metrics.horiAdvance),
        face.glyph.bitmap_left,
        asc - face.glyph.bitmap_top,
        w,
        h,
        base64.b64encode(bytes(data)).decode(),
    ]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    ttf_dir, html = Path(sys.argv[1]), Path(sys.argv[2])
    out = {}
    for nume, (fisier, size, glife) in FONTURI.items():
        face = freetype.Face(str(ttf_dir / fisier))
        face.set_pixel_sizes(size, 0)
        caractere = sorted(set(glife), key=ord)
        out[nume] = {
            "b": px(face.size.ascender),
            "h": px(face.size.height),
            "g": [randeaza(face, size, c) for c in caractere],
        }
    js = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    text = html.read_text(encoding="utf-8")
    nou, n = re.subn(
        r"(/\*@@FONTURI-START@@\*/).*?(/\*@@FONTURI-END@@\*/)",
        lambda m: m.group(1) + js + m.group(2),
        text,
        flags=re.S,
    )
    if n != 1:
        sys.exit("Nu am găsit markerii /*@@FONTURI-START@@*/ ... /*@@FONTURI-END@@*/ în " + str(html))
    html.write_text(nou, encoding="utf-8")
    print(f"Fonturi scrise în {html} ({len(js) // 1024} KB)")


if __name__ == "__main__":
    main()
