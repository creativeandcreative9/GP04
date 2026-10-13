# Background image provenance

Generated on 2026-10-13 using the available ChatGPT image generation tool. The tool did not provide a model/version identifier; no specific model name is claimed. Native image: 1672×941 PNG. Original generated image was copied unchanged to `dream-cloud-concept.png`, visually inspected, and used as the static video backdrop. The original generated file was retained in the environment.

Generation prompt:

Create an exquisite 16:9 landscape concept background painting for a calm fantasy animated film: a dream-world moon-cookie atelier suspended over lavender clouds at blue hour. Hand-painted animation background, nuanced painterly watercolor and gouache textures, luminous but subdued, elegant fine architectural details. Fixed straight-on wide camera, no perspective vanishing conveyor. A delicate huge crescent moon hangs high on the LEFT outside graceful pale lilac stone arches. Through the arches see floating islets, distant tiny dream castles, hazy blue mountains and endless clouds. Wispy wisteria and tiny warm lanterns frame top corners; quiet teal, dusty lavender, pearl, soft antique gold. The top 55 percent is beautiful and visually rich. The center lower part must remain EMPTY and dark muted blue-purple to accommodate three animated machines added later: no actual machines, no tables, no counters, no conveyor belts, no cookies, no characters, no text or logo. In the lower 35 percent a simple softly shaded smooth dark lavender workshop floor/platform; subtle architectural border only along far left and right. Middle foreground from x=5% to95%, y=45% to90% should be quiet enough for a readable animation overlay. A real illustrated world with fine depth and dreamy atmosphere, not a flat vector UI, not a screenshot, no photorealism, no flashing lights. Maintain a soothing low contrast composition suitable for a sleep loop. Render a complete high quality production background, not a storyboard or collage.

Video foreground: original procedural geometry in `render.py`. Audio: original programmatic synthesis from the approved GP04 sound version, with no third-party recordings or music. The image generator is not required to regenerate the supplied video: reuse the supplied background file.

## Foreground refinement (2026-10-13)

Two additional RGBA images were generated using the available ChatGPT image generation capability, with the unchanged background as a style and lighting reference. No model version identifier was supplied.

`refined-machine.png` (2172×724): isolated panoramic conveyor and three OPEN processing arches, lavender porcelain and antique brass, intricate moon ornament, material reflections, soft upper-left moonlight, transparent arch openings. Requested no tools, products, scenery, text or labels. Final composition is a front view with a shallow view of the conveyor surface.

`refined-sprites.png` (1774×887): four-by-two transparent sprite sheet. Top row: dough ball, thick golden shortbread disc, right-opening crescent biscuit, same crescent with satin ivory coating. Bottom row: separate brass press piston, crescent-shaped die piston, porcelain/brass icing nozzle, empty cell. Consistent shallow top view and upper-left light. Requested painted texture, browned pastry edges, visible thickness, subtle glaze highlights, no colored matte or text.

The originals are retained unchanged in assets. Runtime processing isolates atlas cells, removes near-transparent / saturated matte fringes, resizes, and animates them. Source sprites are not painted over the background as a static final frame; the independent product and tool positions and product state are recomputed for every frame.

## Independent drifting cloud layer (2026-10-13)

`drifting-clouds.png` was generated with the unchanged background as reference. Prompt: isolated soft distant cloud wisps on true transparency; long low panoramic painterly lavender-blue moonlit bank, subdued peach ivory ridges and violet undersides, tapered translucent edges, no architecture, moon, stars, land, text or matte. It is masked to window apertures and drifted independently at runtime; the original background is unchanged.

## Perceptible motion correction

The previous delivered MP4 retained stationary dominant cloud banks and used only a 34%-opacity moving haze. This was visually insufficient.

`cloud-free-plate.png`: generated edit of the original background to remove prominent lower-sky puffy cloud banks and upper-sky wisps; reconstruct coherent atmospheric sky behind the floating islands while retaining moon, architecture, lanterns, wisteria and floor. The original background is retained separately.

`cloud-clusters.png`: generated RGBA sheet of three substantial, distinct puffy cloud masses; largely opaque bodies, soft translucent outer edges, moonlit peach-ivory ridges and lavender-blue undersides. Background image supplied as a style reference. Clouds are individually separated at runtime and move independently of the clean plate and machinery. They are not static scenery or an illusion caused by camera motion.
