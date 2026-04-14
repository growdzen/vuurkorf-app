# Vuurkorf Personalisatie

AI-gedreven webapplicatie waarmee klanten een foto uploaden die automatisch wordt omgezet naar een lasersnijbaar silhouet voor een gepersonaliseerde vuurkorf.

## Architectuur

```
vuurkorf/
├── backend/          # FastAPI + Python AI pipeline
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/  (upload, process, preview, orders)
│   │   ├── services/ (image_processor, vectorizer, template_integrator,
│   │   │              validator, dxf_generator, pricing)
│   │   ├── models/   (job, order)
│   │   └── utils/    (svg_utils)
│   ├── assets/templates/vuurkorf_standaard.svg
│   ├── pyproject.toml
│   └── requirements.txt
└── frontend/         # Next.js 14 App Router + TypeScript + Tailwind
    ├── app/
    │   ├── page.tsx             (landingspagina)
    │   ├── configurator/page.tsx (5-stappen wizard)
    │   └── bevestiging/page.tsx  (bedankpagina)
    └── lib/api.ts               (typed API client)
```

## AI Pipeline

1. **Upload** — JPG/PNG/WEBP tot 20MB
2. **Background removal** — via `rembg` (U2-Net model)
3. **Silhouet** — Otsu threshold via OpenCV
4. **Vectorisering** — raster PNG naar SVG via `vtracer`
5. **Template integratie** — silhouet in vuurkorf SVG template (lxml)
6. **Validatie** — maakbaarheidschecks (eilanden, dunne features)
7. **DXF export** — lasersnijbestand via `ezdxf` (R2010, mm, 1:1)

## Vereisten

- Python 3.11+
- Node.js 18+
- `uv` (Python package manager)

## Backend installeren & starten

```bash
cd backend

# Installeer uv (als nog niet geinstalleerd)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installeer dependencies
uv pip install -r requirements.txt

# Maak upload/output directories
mkdir -p /tmp/uploads /tmp/outputs data

# Start de server (poort 8000)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs beschikbaar op: http://localhost:8000/docs

## Frontend installeren & starten

```bash
cd frontend

# Installeer Node.js dependencies
npm install

# Start de dev server (poort 3000)
npm run dev
```

App beschikbaar op: http://localhost:3000

## Configuratie

### Backend
Geen configuratie nodig voor MVP. Jobs worden in-memory opgeslagen.

### Frontend
`.env.local` bevat:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Voor productie: vervang door de publieke backend URL.

## API Endpoints

| Method | Endpoint | Omschrijving |
|--------|----------|-------------|
| POST | `/upload` | Upload afbeelding (max 20MB) |
| POST | `/process/{job_id}` | Start AI pipeline |
| GET | `/preview/{job_id}` | Haal job status + SVG op |
| POST | `/orders` | Plaats bestelling |
| GET | `/orders` | Lijst alle bestellingen |
| GET | `/docs` | Swagger UI |

## Materialen & Prijzen

| Materiaal | Basisprijs | Omschrijving |
|-----------|-----------|-------------|
| Cortenstaal | €89 | Roestpatina, voor buiten |
| RVS | €149 | Weerbestendig, modern |
| Zwart staal | €69 | Klassiek mat zwart |

Diktes: 2mm, 3mm, 4mm, 6mm (met dikte-multiplier op prijs).

## Productie deployment

1. Backend: deploy als Docker container of via `uvicorn` achter nginx
2. Frontend: `npm run build && npm start` of deploy op Vercel/Netlify
3. Stel `NEXT_PUBLIC_API_URL` in op de publieke backend URL
4. Vervang in-memory `jobs_store` door Redis voor multi-instance setup

## Ontwikkeld door

Growdzen — [dennis@growdzen.com](mailto:dennis@growdzen.com)
