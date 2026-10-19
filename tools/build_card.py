#!/usr/bin/env python3
"""Build Michel Germani's digital business card (Germani Jewellery Academy) from cards/michel.json.

Writes:
  michel.html                 the digital card, served at /michel
  michel.vcf                  "Save Contact" vCard (with photo)
  cards/img/michel.jpg        web-sized photo for the card
  cards/qr/michel.png         QR code linking to the card (print / digital)
  cards/qr/michel.svg         same QR code as a vector, for professional printers
  cards/print/michel.html     print layout of the physical business card (front + back)

Then run `node tools/print_card.js` to export the print PDF and PNG previews.

Usage (from the repo root):
  pip install segno pillow
  python3 tools/build_card.py
"""
import base64
import html
import io
import json
from pathlib import Path

import segno
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
NAVY = "#0a1c6b"


def photo_jpeg(src, size, quality):
    """Square-crop the photo from the top (keeps the face) and return JPEG bytes."""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im = ImageOps.fit(im, (size, size), Image.LANCZOS, centering=(0.5, 0.2))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


def vesc(v):
    return str(v).replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def fold(line):
    """Fold vCard lines at 75 octets (RFC 6350)."""
    out, b = [], line.encode()
    while len(b) > 75:
        cut = 75 if not out else 74
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode())
        b = b[cut:]
    out.append(b.decode())
    return "\r\n ".join(out)


def vcard(p, url, photo_bytes):
    lines = [
        "BEGIN:VCARD", "VERSION:3.0",
        f'N:{vesc(p["last_name"])};{vesc(p["first_name"])};;;',
        f'FN:{vesc(p["first_name"] + " " + p["last_name"])}',
        f'ORG:{vesc(p["company"])}',
        f'TITLE:{vesc(p["position"] + ", " + p["credentials"])}',
        f'TEL;TYPE=CELL,VOICE:{p["phone"]}',
        f'EMAIL;TYPE=INTERNET,WORK:{p["email"]}',
        f'URL:{p["website"]}',
        f'ADR;TYPE=WORK:;;{vesc(p["street"])};{vesc(p["city"])};{vesc(p["state"])};;{vesc(p["country"])}',
        f'X-SOCIALPROFILE;TYPE=instagram:{p["instagram"]}',
        f'NOTE:{vesc("Also: " + p["academy_website"] + "  Digital card: " + url)}',
        "PHOTO;ENCODING=b;TYPE=JPEG:" + base64.b64encode(photo_bytes).decode(),
        "END:VCARD",
    ]
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


ICON = {
    "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    "email": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "web": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "insta": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8"/>',
    "cap": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
    "save": '<path d="M12 3v12m0 0-4-4m4 4 4-4"/><path d="M5 17v3h14v-3"/>',
    "share": '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="m8.2 10.8 7.6-3.6M8.2 13.2l7.6 3.6"/>',
}


def icon(name):
    return f'<svg class="i" viewBox="0 0 24 24" aria-hidden="true">{ICON[name]}</svg>'


def page(p, url):
    name = html.escape(p["first_name"] + " " + p["last_name"])
    addr = f'{p["street"]}, {p["city"]} {p["state"]}'
    maps = "https://www.google.com/maps/search/?api=1&query=" + (addr + " " + p["country"]).replace(" ", "+")
    row = lambda href, ic, label, value, ext=False: (
        f'<a class="row" href="{href}"{" target=\"_blank\" rel=\"noopener\"" if ext else ""}>{icon(ic)}'
        f'<span><small>{label}</small>{html.escape(value)}</span></a>')
    rows = "".join([
        row(f'tel:{p["phone"].replace(" ", "")}', "phone", "Mobile", p["phone_display"]),
        row(f'mailto:{p["email"]}', "email", "Email", p["email"]),
        row(p["website"], "web", "Website", p["website_print"], True),
        row(p["academy_website"], "cap", "Academy website", "germanijewelleryacademy.com", True),
        row(maps, "pin", "Address", addr, True),
        row(p["instagram"], "insta", "Instagram", p["instagram_handle"], True),
    ])
    bio = "".join(f"<p>{html.escape(t)}</p>" for t in p["bio"])
    title = f'{name} | {p["company"]}'
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<title>{title}</title>
<meta name="description" content="{name}, {html.escape(p['position'])}, {html.escape(p['company'])}. Save my contact details.">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(p['position'])}, {html.escape(p['company'])}. Tap to save my contact.">
<meta property="og:image" content="{p['website']}/cards/img/{p['slug']}.jpg">
<meta name="theme-color" content="{NAVY}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400&family=Jost:wght@300;400;500&family=Tinos:wght@700&display=swap" rel="stylesheet">
<style>
:root{{--ivory:#f6efe4;--card:#fbf7f0;--line:#e0d2bc;--navy:{NAVY};--navy-2:#45558a;--gold:linear-gradient(180deg,#fdeaa8 0%,#f1c45e 30%,#c98a22 55%,#e8b34b 78%,#fde39b 100%)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Jost,system-ui,sans-serif;font-weight:300;background:var(--ivory);color:var(--navy);min-height:100vh;display:flex;justify-content:center;padding:0 0 32px}}
.card{{width:100%;max-width:440px;background:var(--card);box-shadow:0 10px 28px rgba(10,28,107,.10)}}
.top{{position:relative;padding:24px 20px 84px;text-align:center;background:linear-gradient(rgba(1,14,79,.55),rgba(1,10,56,.7)),url(/assets/img/lapis-band.webp) center/cover}}
.top::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,#974400,#f1c45e 30%,#fde39b 50%,#c98a22 75%,#974400)}}
.mark{{width:56px;height:37px;margin:0 auto 8px;background:var(--gold);-webkit-mask:url(/assets/logo-mark.svg) center/contain no-repeat;mask:url(/assets/logo-mark.svg) center/contain no-repeat}}
.wm{{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:26px;letter-spacing:.12em;margin-right:-.12em;background:var(--gold);-webkit-background-clip:text;background-clip:text;color:transparent;line-height:1}}
.sub{{font-size:10px;font-weight:500;letter-spacing:.3em;margin-right:-.3em;white-space:nowrap;color:#f0c867;margin-top:6px}}
.photo{{position:relative;z-index:1;width:148px;height:148px;border-radius:50%;object-fit:cover;border:4px solid var(--card);box-shadow:0 0 0 2px #c98a22;margin:-74px auto 0;display:block;background:var(--ivory)}}
.who{{text-align:center;padding:16px 24px 4px}}
h1{{font-family:"Cormorant Garamond",serif;font-weight:600;font-size:34px;line-height:1.1}}
.pos{{font-weight:500;font-size:13px;letter-spacing:.16em;text-transform:uppercase;margin-top:8px}}
.cred{{font-family:"Cormorant Garamond",serif;font-style:italic;font-size:17px;color:var(--navy-2);margin-top:4px}}
.co{{font-size:13px;color:var(--navy-2);margin-top:6px;letter-spacing:.04em}}
.actions{{display:grid;gap:10px;padding:20px 24px 8px}}
.btn{{display:flex;align-items:center;justify-content:center;gap:10px;padding:15px;border-radius:2px;font:500 13px Jost,sans-serif;letter-spacing:.2em;text-transform:uppercase;text-decoration:none;border:0;cursor:pointer;width:100%}}
.btn-save{{background:var(--navy);color:var(--ivory)}}
.btn-share{{background:none;color:var(--navy);border:1px solid var(--navy)}}
.rows{{padding:8px 24px}}
.row{{display:flex;align-items:center;gap:14px;padding:13px 0;border-bottom:1px solid var(--line);color:var(--navy);text-decoration:none;font-size:15px;font-weight:400;word-break:break-word}}
.row:last-child{{border-bottom:0}}
.row small{{display:block;font-size:10.5px;color:var(--navy-2);letter-spacing:.14em;text-transform:uppercase;font-weight:400}}
.i{{width:22px;height:22px;flex:none;fill:none;stroke:var(--navy);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}}
.btn .i{{stroke:currentColor}}
.about{{padding:14px 24px 6px;border-top:1px solid var(--line);margin:8px 24px 0;padding-left:0;padding-right:0}}
.about h2{{font-family:"Cormorant Garamond",serif;font-weight:600;font-size:22px;margin-bottom:8px}}
.about p{{font-size:14.5px;line-height:1.65;margin-bottom:10px}}
footer{{text-align:center;font-size:12px;color:var(--navy-2);padding:16px 24px 26px;letter-spacing:.06em}}
footer a{{color:var(--navy)}}
@media (min-width:480px){{body{{padding-top:32px}}.card{{border-radius:4px;overflow:hidden}}}}
</style>
</head>
<body>
<main class="card">
  <div class="top">
    <div class="mark" aria-hidden="true"></div>
    <div class="wm">GERMANI</div>
    <div class="sub">JEWELLERY ACADEMY</div>
  </div>
  <img class="photo" src="/cards/img/{p['slug']}.jpg" alt="Photo of {name}" width="148" height="148">
  <div class="who">
    <h1>{name}</h1>
    <div class="pos">{html.escape(p['position'])}</div>
    <div class="cred">{html.escape(p['credentials'])}</div>
    <div class="co">{html.escape(p['company'])}</div>
  </div>
  <div class="actions">
    <a class="btn btn-save" href="/{p['slug']}.vcf" download="Michel-Germani.vcf">{icon("save")} Save Contact</a>
    <button class="btn btn-share" id="share" type="button" hidden>{icon("share")} Share this card</button>
  </div>
  <div class="rows">{rows}</div>
  <section class="about">
    <h2>About Michel</h2>
    {bio}
  </section>
  <footer>Germani Jewellery &middot; Sydney<br><a href="{p['website']}">Visit the website</a></footer>
</main>
<script>
(function () {{
  var b = document.getElementById('share');
  if (!navigator.share) return;
  b.hidden = false;
  b.onclick = function () {{ navigator.share({{ title: {json.dumps(title)}, url: {json.dumps(url)} }}).catch(function () {{}}); }};
}})();
</script>
</body>
</html>
"""


def print_page(p):
    """Physical business card, 90 x 55 mm trim with 3 mm bleed on every side (96 x 61 mm pages)."""
    name = html.escape(p["first_name"] + " " + p["last_name"])
    qr_svg = (CARDS / "qr" / f'{p["slug"]}.svg').read_text(encoding="utf-8")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{name} business card</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400&family=Jost:wght@300;400;500&family=Tinos:wght@700&display=swap" rel="stylesheet">
<style>
@page {{ size: 96mm 61mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #888; }}
.side {{ width: 96mm; height: 61mm; position: relative; overflow: hidden; page-break-after: always; }}
.front {{ background: linear-gradient(rgba(1,14,79,.5),rgba(1,10,56,.66)), url(../../assets/img/lapis-band.webp) center/cover; }}
.front .logo {{ position: absolute; inset: 3mm 3mm 3mm 3mm; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.front .mark {{ width: 16mm; height: 10.6mm; margin-bottom: 2.2mm; background: linear-gradient(180deg,#fdeaa8 0%,#f1c45e 30%,#c98a22 55%,#e8b34b 78%,#fde39b 100%);
  -webkit-mask: url(../../assets/logo-mark.svg) center/contain no-repeat; mask: url(../../assets/logo-mark.svg) center/contain no-repeat; }}
.front .wm {{ font-family: "Times New Roman", Tinos, serif; font-weight: 700; font-size: 19pt; letter-spacing: .12em; margin-right: -.12em; line-height: 1;
  background: linear-gradient(180deg,#fdeaa8 0%,#f1c45e 30%,#c98a22 55%,#e8b34b 78%,#fde39b 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.front .sub {{ font-family: Jost, sans-serif; font-weight: 500; font-size: 6pt; letter-spacing: .32em; margin-right: -.32em; white-space: nowrap; color: #f0c867; margin-top: 1.6mm; }}
.front .rule {{ position: absolute; left: 0; right: 0; bottom: 0; height: 4.6mm; background: linear-gradient(90deg,#974400,#f1c45e 30%,#fde39b 50%,#c98a22 75%,#974400); }}
.back {{ background: #f6efe4; color: {NAVY}; font-family: Jost, sans-serif; }}
.back .in {{ position: absolute; left: 3mm; top: 3mm; width: 90mm; height: 55mm; padding: 5mm 5mm 5mm 6mm; display: grid; grid-template-columns: 1fr 23mm; column-gap: 4mm; align-items: center; }}
.back .name {{ font-family: "Cormorant Garamond", serif; font-weight: 600; font-size: 15pt; line-height: 1; }}
.back .pos {{ font-weight: 500; font-size: 5.6pt; letter-spacing: .2em; text-transform: uppercase; margin-top: 1.6mm; }}
.back .cred {{ font-family: "Cormorant Garamond", serif; font-style: italic; font-size: 7.6pt; margin-top: .8mm; color: #2c3d7a; }}
.back .line {{ width: 9mm; height: .25mm; background: #c98a22; margin: 2.6mm 0 2.4mm; }}
.back .d {{ font-size: 6.4pt; line-height: 1.62; font-weight: 400; }}
.back .d b {{ font-weight: 500; }}
.back .qr {{ text-align: center; }}
.back .qr svg {{ width: 23mm; height: 23mm; display: block; }}
.back .qr span {{ display: block; font-size: 4.6pt; letter-spacing: .14em; text-transform: uppercase; margin-top: .8mm; }}
.back .rule {{ position: absolute; left: 0; right: 0; bottom: 0; height: 4.6mm; background: {NAVY}; }}
.back .rule::before {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: .5mm; background: linear-gradient(90deg,#974400,#f1c45e 30%,#fde39b 50%,#c98a22 75%,#974400); }}
</style></head><body>
<section class="side front"><div class="logo"><div class="mark"></div><div class="wm">GERMANI</div><div class="sub">JEWELLERY ACADEMY</div></div><div class="rule"></div></section>
<section class="side back"><div class="in">
  <div>
    <div class="name">{name}</div>
    <div class="pos">{html.escape(p['position'])}</div>
    <div class="cred">{html.escape(p['credentials'])}</div>
    <div class="line"></div>
    <div class="d"><b>M</b>&nbsp; {p['phone_display']}<br><b>E</b>&nbsp; {p['email']}<br>{html.escape(p['street'])}, {html.escape(p['city'])}<br>{p['website_print']}</div>
  </div>
  <div class="qr">{qr_svg}<span>Scan to save</span></div>
</div><div class="rule"></div></section>
</body></html>
"""


def main():
    p = json.loads((CARDS / "michel.json").read_text(encoding="utf-8"))
    slug = p["slug"]
    url = f'{p["website"]}/{slug}'
    for d in ("img", "qr", "print"):
        (CARDS / d).mkdir(exist_ok=True)
    src = CARDS / "photos" / p["photo"]
    (CARDS / "img" / f"{slug}.jpg").write_bytes(photo_jpeg(src, 400, 84))
    (ROOT / f"{slug}.vcf").write_text(vcard(p, url, photo_jpeg(src, 240, 75)), encoding="utf-8", newline="")
    (ROOT / f"{slug}.html").write_text(page(p, url), encoding="utf-8")
    qr = segno.make(url, error="q")
    qr.save(CARDS / "qr" / f"{slug}.png", scale=20, border=4, dark=NAVY)
    qr.save(CARDS / "qr" / f"{slug}.svg", scale=10, border=2, dark=NAVY, light=None, xmldecl=False, svgns=True, omitsize=True)
    (CARDS / "print" / f"{slug}.html").write_text(print_page(p), encoding="utf-8")
    print(f"{slug}: {url}")


if __name__ == "__main__":
    main()
