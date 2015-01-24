# Osmic (OSM Icons)

A collection of clean high quality SVG map icons licensed under CC0 (Public Domain).

![Osmic (OSM Icons)](https://github.com/nebulon42/osmic/raw/master/icons-2x.png "Available icons")

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
All icons use a canvas base size of 16px. Where required there exist several versions that are varying in size and amount of detail. The size is indicated by appending the pixel value to the icon name (e.g. hospital-16.svg).

## Why another icon collection?
Bascially there are two collections of icons that are widely used for displaying OSM data: [twain47's Open-SVG-Map-Icons](https://github.com/twain47/Open-SVG-Map-Icons) and [Mapbox' Maki](https://github.com/mapbox/maki).

Osmic does not try to replace any of the two, but aims at addressing shortcomings of both collections. While Open-SVG-Map-Icons comprise a quite comprehensive icon collection they often feature somewhat complex representations and do not work so well at small resolutions. They also do not align to the pixel grid, which may result in a blurry icon representation.

On the other hand, Maki icons have been designed especially for small resolutions but come with a lot of Mapbox or marker specific code. Some icons also have an outline which hinders recolouring of the icons.

Osmic tries to provide simple, clean and legible icons - and just icons.

## How to contribute

Contributions are welcome, please have a look at [this guide](https://github.com/nebulon42/osmic/raw/master/CONTRIBUTING.md).
