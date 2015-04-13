# How to request icons
New icons may be requested via GitHub issues. Please search through existing issues first to see if your request is not already covered. Please also limit issues to a
single icon or a small number of very closely related icons.

# How to contribute

Osmic uses "Fork & Pull" for contributions (see https://help.github.com/articles/using-pull-requests). Both adjustments and improvements to existing icons as well as
new icons are welcome.

Please limit new icon pull requests to one icon each unless they are very closely related in concept and design.

## Legal aspects

By contributing you agree to release your work under CC0 (or Public Domain), see the [license](https://github.com/nebulon42/osmic/blob/master/LICENSE.txt) for details.
If submitting new icons or substantial modifications you confirm that this is your own work and it is free of the rights of others.

## Technical aspects

It is recommended to use Inkscape (https://inkscape.org) for creating or modifying SVG files. Please do not submit files in Inkscape's own SVG-like format as it contains
a lot of clutter. Instead use File > Save As ... and select "Plain SVG".

Icon standard canvas size is 14x14px without any padding i.e. the icon can use all of the available space. The icon file name should use dashes for whitespace and append the canvas size (e.g. `waste-basket-14.svg`).

All icon content has the colour black (`#000000`) and consists of a single path (parts merged together). The path's ID is similar to the file name without the canvas size part (e.g. `waste-basket-14.svg` has id `waste-basket`).

In the background all icons have a invisible rectangle spanning the whole canvas to avoid up-/downscaling of the shape alone when using `marker-width` or `marker-height` in CartoCSS. The style of this rectangle has set `visibility:hidden` and uses the id `canvas`. See one of the icons for an example how this looks.
