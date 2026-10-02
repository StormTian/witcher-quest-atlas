# Witcher 3 factual regional map research

Verified 2026-10-02. No generated or fictional maps. Research and exported assets only; no site edits.

## Selected matching tile/quest source

- Source project: https://github.com/reubengann/Witcher3MapViewer
- Frozen source commit: `fb674dbff7df087d0a45f9b3938ba6d5317295af`
- Quest data source: https://github.com/reubengann/Witcher3MapViewer/blob/fb674dbff7df087d0a45f9b3938ba6d5317295af/Witcher3MapViewer/Quests.xml
- Map pin data source: https://github.com/reubengann/Witcher3MapViewer/blob/fb674dbff7df087d0a45f9b3938ba6d5317295af/Witcher3MapViewer/MapPins.xml
- Calibration: https://github.com/reubengann/Witcher3MapViewer/blob/fb674dbff7df087d0a45f9b3938ba6d5317295af/Witcher3MapViewer/Settings.xml
- Author's original transform: https://github.com/reubengann/Witcher3MapViewer/blob/fb674dbff7df087d0a45f9b3938ba6d5317295af/Witcher3MapViewer.Core/RealToGameSpaceConversion.cs
- Original map assets folder: https://github.com/reubengann/Witcher3MapViewer/tree/fb674dbff7df087d0a45f9b3938ba6d5317295af/Witcher3MapViewer/Maps
- Raw asset URL template: `https://raw.githubusercontent.com/reubengann/Witcher3MapViewer/fb674dbff7df087d0a45f9b3938ba6d5317295af/Witcher3MapViewer/Maps/{WhiteOrchard,VelenNovigrad,Skellige,KaerMorhen,Toussaint}.mbtiles`

`mapviewer-deploy-xyz/{WO,NO,SK,KM,TO}/{z}/{x}/{y}.png` is an independent tile export suitable for ordinary Leaflet XYZ use (`tms:false`). Original MBTiles `tile_row` uses bottom-origin TMS; the export flips each row by `xyzY=2^z-1-tmsY`. All PNG tiles are 256x256. Export includes WO zoom 0-4 and other regions zoom 0-3. Native zoom can be overzoomed with Leaflet `maxNativeZoom`, with reduced detail. Total 601 files / 27,049,833 bytes.

The original MBTiles full-world bounds/center are synthetic Mercator coordinates, not Earth locations. The original display engine places transformed game coordinates as projected meters. Original metadata center is `0,0,2`. Bounds: WO longitude -180..180 / latitude -77.6929..76.5985; other maps -180..180 / -85.0511..85.0511. Original maximum native zoom is WO 4 and other maps 5.

| Region code | Region | slope | xi | yi |
|---|---|---:|---:|---:|
| WO | White Orchard | 0.000038 | 60 | 19.2 |
| NO (alias VE) | Velen / Novigrad | 0.000114 | 968.6 | 706.4 |
| SK | Skellige | 0.000164 | 209.9 | 305.7 |
| KM | Kaer Morhen | 0.0000568 | 10.1 | 244.2 |
| TO | Toussaint | 0.0000897 | -153.3 | -717.7 |

For game X/Y, compute projected meters `xm=(X-xi)/slope`, `ym=(Y-yi)/slope`; then `lng=(xm/6378137)*180/pi`, `lat=(2*atan(exp(ym/6378137))-pi/2)*180/pi`. These numbers are only a mapping into Leaflet's map projection. For an image covering the entire Mercator square, normalized top-left-origin image coordinates are `nx=(xm+pi*6378137)/(2*pi*6378137)`, `ny=(pi*6378137-ym)/(2*pi*6378137)`.

## Verification and roles

- `deploy-map-manifest.json`: native zoom, bounds, byte/file counts and calibration constants.
- `mapviewer-map-metadata.json`: all original asset metadata and raw source URLs.
- `sample-quest-calibration.json`: independently transformed source quest prompts.
- `sample-signpost-calibration.json`: independently transformed anchors for all five regions.
- `mapviewer-map-pins.json`: independently transformed 1,205 source marker facts. These are not claimed to include every current-game pin.
- `source-file-sha256.json`: SHA-256 for source XML, readme, transform code and all five original MBTiles.
- `verification/`: actual tile composites and overlaid factual coordinate checks, inspected visually.

All four sampled quest pins visually land on plausible source start features: Missing in Action in Ransacked Village; Twisted Firestarter at a smith's building in White Orchard; Of Swords and Dumplings in the Novigrad smith quarter; There Can Be Only One at a Beauclair notice board. The last source coordinate is explicitly a notice-board discovery prompt, not the quest objective at Lac Celavy. Signposts were checked in all five regions; White Orchard's Woesong Bridge/Ford/Nilfgaardian Garrison/Mill/Sawmill line up with visible map features, and other region sample anchors line up with their mapped features. This validates the projection/tile orientation; it does not independently certify every quest coordinate or all game-version behavior.

## Rights and alternative source

MapViewer README says map imagery comes from game screenshots and tiles were created with TileMill; marker data was extracted from uncooked game files. No standalone license file or explicit project reuse license was found in the cloned tracked files. Maps remain CD PROJEKT RED game assets; attribution is provenance, not an asserted license grant. Do not apply the alternative project's Creative Commons license to this repository.

Alternative primary fan-map project: https://github.com/witcher3map/witcher3map, frozen commit `437241a978a13a1ca9114301d9ef887fadf4f260`. README licenses that project's contribution under CC BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/ ; it separately identifies the Witcher 3 logo, icons and map as CD PROJEKT RED property and references a historical User Agreement noncommercial user-generated-content provision. The asset repository repeats the CDPR ownership note: https://github.com/witcher3map/witcher3map-maps (frozen commit `df7fa74609df7587afc324e569d2574cf5b4f1ec`). This historical reference is not an independent verification of current CDPR terms.

Live source pages: https://witcher3map.com/w/ (White Orchard), https://witcher3map.com/v/ (Velen/Novigrad), https://witcher3map.com/s/ (Skellige), https://witcher3map.com/k/ (Kaer Morhen), https://witcher3map.com/t/ (Toussaint).

Alternative tile URL template: `https://raw.githubusercontent.com/witcher3map/witcher3map-maps/df7fa74609df7587afc324e569d2574cf5b4f1ec/{white_orchard,velen,skellige,kaer_morhen,toussaint}/{z}/{x}/{y}.png`; sample existing image: `https://raw.githubusercontent.com/witcher3map/witcher3map-maps/df7fa74609df7587afc324e569d2574cf5b4f1ec/white_orchard/3/0/0.png`. Full archive used by the original build: https://github.com/witcher3map/witcher3map-maps/releases/download/1.1/witcher3map-maps-master.zip . Source scripts contain all five region marker files in `assets/scripts/custom/mapdata-*.js` and English labels in `assets/locales/en/`.

Do not combine the alternative map tiles directly with MapViewer coordinates. The alternative uses CRS.Simple for Velen/Toussaint/Kaer Morhen, default Leaflet Mercator for White Orchard/Skellige, plus TMS y tiles. Its coordinate values are a different calibration.
