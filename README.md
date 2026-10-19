# Germani Jewellery — website

Showcase website for **Germani Jewellery**, Sydney (Michel Germani). Static HTML/CSS/JS with no build step and no e-commerce. Enquiries and appointments go through the contact form, phone or email.

## Brand rules (from Germani)

- **Logo:** G-diamond mark over GERMANI in bold Times Roman, metallic gold on navy (as on the Germani brochure).
- **Logo font:** Times New Roman (falls back to Tinos, a free Times-compatible web font, on devices without it).
- **Colours:** Navy Blue `#0b1a3a`, Gold `#d9c39a` / `#b8955a`, Ivory `#f8f3e8` (with Light Cream `#efe7d6` for alternate sections).
- **Logo on the website:** gold letters on navy, used in the header and footer. Signage uses white on black or a gold stainless-steel background.
- Logo files: `assets/logo-mark-gold.svg`, `assets/logo-mark-navy.svg`, `assets/logo-mark.svg` (black).

## Pages

| File | Content |
|---|---|
| `index.html` | Home: hero, collections, black opal feature, campaign, founder, bespoke, visit |
| `collections.html` | Filterable gallery of 54 pieces with a lightbox and "Enquire about this piece" link |
| `house.html` | Michel Germani's story and the house values |
| `bespoke.html` | Engagement rings and the bespoke process |
| `contact.html` | Appointment form (Netlify Forms) and direct contact details |
| `404.html` | Not-found page |

## Structure

```
assets/css/site.css      all styles (colours and fonts are variables at the top)
assets/js/site.js        header, mobile menu, filters, lightbox, form
assets/img/              optimised WebP photos + og-image.jpg
assets/logo-mark.svg     G-diamond logo (vector, traced from the brand mark)
favicon.svg / .png, apple-touch-icon.png
netlify.toml, robots.txt, sitemap.xml
```

## Editing

- **Add a piece:** copy a `<figure class="piece">` block in `collections.html`, change the image, name and description, and set `data-cat` to one or more of `necklaces earrings rings bracelets bridal opals morganite gentlemen`. Add `piece__img--studio` for white-background studio photos.
- **Contact details:** the phone, email and Instagram links appear in the header, footer, home page and contact page.
- **Photos:** export to WebP at about 1400px on the long side.

## Hosting

Deploy the repository root on Netlify (`publish = "."`). The appointment form uses Netlify Forms; submissions appear under *Forms* in the Netlify dashboard, where email notifications can be switched on.

To preview locally: `npx http-server .` and open http://localhost:8080.
