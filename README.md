# home-search-gis

Custom property search app with GIS overlay layers not available on MLS portals.

**Live:** [deploy via Vercel below]  
**Phase 1 target geography:** Katy TX 77494, Fort Bend / Harris County

## Phase 1 Features

- Base map (OpenFreeMap / MapLibre GL JS -- no API key required)
- Addicks + Barker reservoir watershed boundaries (live from HCFCD REST service)
- FEMA NFHL flood zone overlay (toggle; live WMS from FEMA hazards portal)
- Address search via Photon geocoding (free, no key required)
- Point-in-polygon check: does this address fall inside the Addicks or Barker watershed?
- Browser geolocation

## Data Sources

| Layer | Source | Key | Update frequency |
|---|---|---|---|
| Base map tiles | OpenFreeMap (openfreemap.org) | None | Weekly |
| Watershed boundaries | HCFCD ArcGIS REST (gis.hctx.net) | None | As-published by HCFCD |
| FEMA flood zones | FEMA NFHL WMS (hazards.fema.gov) | None | Map amendment cycle |
| Geocoding | Photon / Komoot (photon.komoot.io) | None | OSM-based |

### Watershed boundary note

The Addicks and Barker layers show **watershed (drainage catchment) boundaries**, not the exact storm pool extent during Harvey. The watershed boundary indicates that precipitation falling within it drains into the named reservoir. It is a conservative flood-risk indicator for reservoir operations but does not delineate the exact inundation footprint from any specific storm event.

For the precise storm pool extent from Hurricane Harvey, see USACE Galveston District PDF maps at swg.usace.army.mil -- these are not available as machine-readable GeoJSON.

### CORS note

The HCFCD REST service (gis.hctx.net) is a public ArcGIS endpoint and should support browser CORS requests. If the watershed layer fails to load in a deployed environment, run a lightweight proxy via a Vercel serverless function:

```js
// api/watershed.js
export default async function handler(req, res) {
  const upstream = 'https://www.gis.hctx.net/arcgishcpid/rest/services/HCFCD/Watershed/MapServer/1/query'
    + '?where=OBJECTID+IN+(1%2C4)&outFields=WTSHNAME%2CWTSHUNIT&f=geojson&outSR=4326';
  const r = await fetch(upstream);
  const data = await r.json();
  res.setHeader('Cache-Control', 's-maxage=3600');
  res.json(data);
}
```

Then change `WATERSHED_URL` in `index.html` to `'/api/watershed'`.

## Deploy to Vercel

```bash
npm i -g vercel
vercel --prod
```

Or connect the GitHub repo to Vercel dashboard -- zero config, static HTML deployment.

## Phase 2 layers (not yet implemented)

- Fort Bend / Harris County Subsidence District boundaries
- Build-year ranges by subdivision (CSST, lead paint risk windows)
- HOA lien density (aggregated from county deed records)
- School district boundaries
- Property tax delinquency heat map

## Local development

```bash
npx serve .
# open http://localhost:3000
```
