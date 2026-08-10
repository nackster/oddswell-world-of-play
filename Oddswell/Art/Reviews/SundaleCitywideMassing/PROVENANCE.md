# Sundale Business-Clustered Mega-City Replacement Preview Provenance

- Status: noncanonical owner-requested business-clustered mega-city preview; not production Unreal geometry, Phase 2, or final art.
- Supersedes: the `1400x1000 m`, four-district, `72`-mass, twenty-four-tower radial preview. Git history retains that review and the earlier smaller boards.
- Authoring: generated locally in Blender `4.5.5 LTS` by `build_sundale_massing_board.py` from original native primitive geometry only.
- Planning/play envelope: exactly `2400x1800 m` around one central `600x420 m` Commons/Park and six labeled radial districts: Financial/Downtown, Arena/Entertainment, Shopping/Retail, Dining/Nightlife, Home Design/Furniture, and Residential/Neighborhood Services.
- Street massing: exactly `144` street-level masses, `24` per district. Only gameplay-relevant ground-floor scope is contemplated; no interiors are modeled.
- Skyline: exactly `60` proposed skyscrapers. Thirty-six sit inside the envelope on counted street-level bases, distributed `12/6/5/5/4/4` across Financial/Arena/Shopping/Dining/Home/Residential; twenty-four sit outside the play boundary, four per district sector.
- Scenic land-use shell contract: exactly `24` Restaurant shells (`4` per district), `8` Nightlife/Bar shells in Dining/Nightlife, `3` Shopping Center shells in Shopping/Retail, `8` Furniture/Showroom shells in Home Design/Furniture, and `12` Financial/Office shells in Financial/Downtown. These labels describe architectural massing only. They add no restaurant, bar or alcohol service, store, purchase, catalog, economy, age-rating, or gameplay behavior.
- Required landmarks: seven functional building/location identities (Studio/apartment frontage, Job, Clothing, Furniture, Arena, Ticket Booth, and Public Court), one attached Apartment Management kiosk point, and one central Commons/Park area. All nine remain on or near the proposed inner ring.
- Circulation: exactly twelve radial spoke boulevards branch from the park, with three concentric ring roads and forty-eight local streets split eight per district. All are proposed review guides; no route distance, travel time, capacity, collision, or production-road claim is made. The proven production `800 m` route remains unchanged.
- Park placeholders: four lawn quadrants, two promenades, and four tree-grove blocks use native low-poly primitives only. They are not final landscape assets.
- Source material: none. No external model, texture, image, font, marketplace item, paid service, or third-party asset is included.
- Outputs: exactly one `3200x2400` top-down and six `1280x720`, true `1.7 m` district/park/skyline Eevee review PNGs. Each eye camera maintains at least `20 m` horizontal clearance from every mass, tower, court, and park AABB. Cycles is not used.
- Ceiling: no vehicles, World Partition, detailed facades, production materials/textures, interiors, production character, props, traffic, capacity claim, accessibility/usability proof, minimum-PC proof, or beta-readiness claim.

## Rebuild

Run Blender headlessly with the repository script:

```powershell
& 'C:\Users\reali\AppData\Local\Programs\Blender Foundation\blender-4.5.5-windows-x64\blender.exe' --background --python 'Oddswell\Art\Reviews\SundaleCitywideMassing\build_sundale_massing_board.py' -- --build
```

Reopen and validate the saved Blend and manifest with:

```powershell
& 'C:\Users\reali\AppData\Local\Programs\Blender Foundation\blender-4.5.5-windows-x64\blender.exe' --background 'Oddswell\Art\Reviews\SundaleCitywideMassing\SundaleCitywideMassing.blend' --python 'Oddswell\Art\Reviews\SundaleCitywideMassing\build_sundale_massing_board.py' -- --validate-existing
```

The script deletes and deterministically reconstructs only this review artifact. It does not touch production Unreal content.
