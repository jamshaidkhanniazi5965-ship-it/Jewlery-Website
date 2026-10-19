# Germani Jewellery — website

Showcase website for **Germani Jewellery**, Sydney (Michel Germani). Static HTML/CSS/JS with no build step and no e-commerce. Enquiries and appointments go through the contact form, phone or email.

## Brand rules (from Germani)

The website uses the colours of the Germani brochure:

- **Lapis blue** `#0a1c6b` / `#010e4f`: header, buttons, dark sections. The dark sections use the lapis-and-gold-leaf texture from the brochure cover (`assets/img/lapis-*.webp`).
- **Gold**: metallic gold logo, accents `#a8701c` on ivory, `#f0c867` on lapis. The homepage banner has the brushed-gold sweep from the cover (`assets/img/gold-leaf.webp`).
- **Ivory satin** `#f6efe4` (alternate sections `#eee3d2`): page background.
- **Burgundy** `#773731`: headings, as on the brochure's inside pages. Body text `#2f2f30`.
- **Logo:** G-diamond mark over GERMANI in bold Times Roman (Tinos fallback), metallic gold on lapis.
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
