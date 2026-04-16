# VuurkorfPersoonlijk — Brand Guide

## Brand Identity

**Brand Name:** VuurkorfPersoonlijk  
**Tagline:** *Uw eigen motief in metaal*  
**Parent Brand:** Growdzen  
**Language:** Dutch (primary), English (secondary)

---

## Brand Essence

VuurkorfPersoonlijk transforms personal photos into laser-cut metal fire pits. The brand sits at the intersection of **craftsmanship**, **personalization**, and **modern technology**. Every fire pit tells a story — a family portrait, a beloved pet, a meaningful symbol — cut into metal and brought to life by firelight.

**Brand Personality:**
- Premium but approachable
- Warm and personal (not cold/industrial)
- Dutch craftsmanship meets AI innovation
- Emotional connection through physical products

**Tone of Voice:**
- Confident, not boastful
- Warm, inviting — like sitting around a fire
- Clear and direct (Dutch directness)
- Technical when needed, never jargon-heavy

---

## Color Palette

### Primary Colors

| Color | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| Fire Orange | `#d94f28` | `fire` / `brand-500` | CTAs, accents, brand mark |
| Fire Dark | `#9f2c19` | `fire-dark` / `brand-700` | Hover states, depth |
| Fire Light | `#f5c8b0` | `fire-light` / `brand-200` | Backgrounds, highlights |

### Extended Brand Scale

| Shade | Hex | Token |
|-------|-----|-------|
| 50 | `#fdf4f0` | `brand-50` |
| 100 | `#fae5d8` | `brand-100` |
| 200 | `#f5c8b0` | `brand-200` |
| 300 | `#eda07c` | `brand-300` |
| 400 | `#e4724a` | `brand-400` |
| 500 | `#d94f28` | `brand-500` |
| 600 | `#c0391d` | `brand-600` |
| 700 | `#9f2c19` | `brand-700` |
| 800 | `#82261b` | `brand-800` |
| 900 | `#6b231a` | `brand-900` |

### Neutral Colors

- **Background:** `hsl(0, 0%, 98%)` — near-white warmth
- **Foreground:** `hsl(20, 14%, 10%)` — warm dark, not pure black
- **Muted text:** `hsl(20, 10%, 45%)` — warm gray

### Material Colors (Product)

| Material | Background | Border |
|----------|-----------|--------|
| Cortenstaal | `amber-50` | `amber-200` |
| RVS | `slate-50` | `slate-200` |
| Zwart staal | `gray-50` | `gray-300` |

---

## Typography

**Primary Font:** Inter  
**Fallback:** system-ui, sans-serif

| Element | Weight | Size |
|---------|--------|------|
| Hero heading | Bold (700) | 4xl-6xl (responsive) |
| Section heading | Bold (700) | 3xl |
| Subheading | Semibold (600) | lg |
| Body | Regular (400) | base |
| Small / caption | Regular (400) | sm |

---

## Logo

**Primary:** "Vuurkorf" in bold + "Persoonlijk" in fire orange (`#d94f28`)  
**Icon:** Stylized flame in fire pit bowl (see `images/vuurkorf_logo_mark.jpeg`)  
**Temporary:** Fire emoji used as placeholder in header

### Logo Usage
- Always pair the wordmark with the icon when space allows
- Icon alone works for favicon, app icon, social profile picture
- Minimum clear space: equal to the height of the flame icon

---

## Brand Assets

| Asset | File | Purpose |
|-------|------|---------|
| OG Image | `images/vuurkorf_og_image.jpeg` | Social media link previews (Facebook, LinkedIn, WhatsApp) |
| Logo Mark | `images/vuurkorf_logo_mark.jpeg` | Favicon, app icon, social profile picture |
| Hero - Product | `images/generated_fb27e301.png` | Landing page hero (product shot) |
| Hero - Lifestyle | `images/generated_9f9dbe72.jpeg` | Landing page hero (lifestyle/family shot) |

---

## UI Components

### Buttons
- **Primary:** `bg-orange-600 hover:bg-orange-500` with white text, rounded-xl, shadow-lg
- **Secondary:** White with `text-orange-600`, rounded-xl
- **Transition:** all 150ms

### Cards (Radio Select)
- **Selected:** `border-fire bg-fire/5` (2px border)
- **Unselected:** `border-gray-200 hover:border-gray-300`

### Step Indicators
- **Active:** `bg-fire text-white` (round)
- **Completed:** `bg-green-500 text-white`
- **Pending:** `bg-gray-200 text-gray-500`

---

## Photography Direction

### Product Shots
- Dark, moody backgrounds (charcoal, deep gray)
- Warm firelight illuminating the laser-cut pattern
- Show the metal texture and craftsmanship detail
- Corten steel patina is a hero element

### Lifestyle Shots
- Outdoor garden/terrace settings
- Evening/dusk lighting with warm fire glow
- People enjoying the fire pit (family, friends)
- Dutch residential contexts (terraces, gardens)

### Process Shots
- Before/after: photo to laser-cut pattern
- Close-ups of laser cutting in action
- Material texture details

---

## Social Media

### OG Meta Tags (for implementation)
```html
<meta property="og:title" content="VuurkorfPersoonlijk | Uw eigen motief in metaal" />
<meta property="og:description" content="Upload een foto en wij zetten het om naar een uniek lasersnijpatroon voor uw vuurkorf." />
<meta property="og:image" content="/og-image.jpg" />
<meta property="og:type" content="website" />
<meta property="og:locale" content="nl_NL" />
```

---

## Next Steps (Creative Roadmap)

- [ ] Convert logo mark to SVG for crisp rendering at all sizes
- [ ] Generate favicon set (16x16, 32x32, 180x180 apple-touch)
- [ ] Create product photography for each material type (corten, RVS, zwart staal)
- [ ] Design email templates (order confirmation, shipping)
- [ ] Create social media templates (Instagram stories, Facebook posts)
- [ ] Develop video content showing the personalization process

---

*Last updated: 2026-04-15 by Creative Director*
