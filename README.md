# Osmic (OSM Icons)

A collection of 100+ clean high quality SVG map icons licensed under CC0 (Public Domain) and also available as [icon font](https://github.com/nebulon42/osmic/tree/master/font). Below you see a possible preview (these are 2x the [original size](https://github.com/nebulon42/osmic/raw/master/icons.png)).

![Osmic (OSM Icons)](https://github.com/nebulon42/osmic/raw/master/icons@2x.png "Available icons")

Icons are heavily inspired by
* Maki ([mapbox/maki](https://github.com/mapbox/maki))
* Nori (as referenced in [hotosm/HDM-CartoCSS](https://github.com/hotosm/HDM-CartoCSS/blob/master/icons/poi/_nori.svg))
* Open-SVG-Map-Icons ([twain47/Open-SVG-Map-Icons](https://github.com/twain47/Open-SVG-Map-Icons))

## Icon Features
All icons should adhere to the following features
* flat (single colour, no gradients, no outlines)
* clean (reduced complexity where possible)
* sharp (aligned to pixel grid)
* single point of view (avoid use of perspective where possible)
* common canvas size

## SVG code
* avoid Inkscape specific code, use plain SVG
* no groups, one path
* invsibile background rectangle spanning the whole canvas to avoid up-/downscaling of the shape alone when using `marker-width` or `marker-height`

## Icon specifications
All icons use a canvas base size of 14px. Where required there exist several versions that are varying in size and amount of detail. The size is indicated by appending the pixel value to the icon name (e.g. hospital-14.svg).

## Create a customised collection
With the Python export script ([tools/export.py](https://github.com/nebulon42/osmic/blob/master/tools/export.py)) the appearance of the icons can be customised. You can
* add padding
* add halos
* add shields
* re-colour icons
* create icon sprites
* export as SVG, PNG or icon font

by changing a YAML configuration file.

Have a look at the [export guide](https://github.com/nebulon42/osmic/blob/master/tools/export.md) for more details.

## How to contribute

Contributions are welcome, please have a look at this [guide](https://github.com/nebulon42/osmic/blob/master/CONTRIBUTING.md).
