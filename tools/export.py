#!/usr/bin/env python

# export to SVG or PNG (incl. retina output), re-colour, add padding,
# add halo, generate sprites

from __future__ import print_function
import argparse
import copy
import glob
import lxml.etree
import lxml.objectify
import math
import os
import re
import shutil
import subprocess
import sys
import yaml


def main():
    parser = argparse.ArgumentParser(description='Exports Osmic (OSM Icons).')
    parser.add_argument('configfile',
                        metavar='config-file',
                        help='the configuration file for the export')
    parser.add_argument('--basedir', dest='basedir',
                        metavar='base-directory',
                        help='specify the working directory of the script',
                        required=False,
                        default=None)
    args = parser.parse_args()

    try:
        configfile = open(args.configfile)
    except IOError:
        sys.exit('Could not open configuration file, please check if it exists. Exiting.')

    config = yaml.safe_load(configfile)
    configfile.close()

    defaultValues(config)

    # command line specified basedir value overwrites config file value
    if args.basedir:
        config['basedir'] = args.basedir

    # set basedir (evaluation from cwd, if not specified always cwd)
    if 'basedir' in config:
        os.chdir(os.path.dirname(config['basedir']))

    # empty output directory if it exists and config param is set
    if config['empty_output'] == True and os.path.exists(config['output']):
        for the_file in os.listdir(config['output']):
            file_path = os.path.join(config['output'], the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except:
                pass

    if not isinstance(config['retina'], bool):
        config['retina'] = False
        print('The retina flag must be boolean. Defaulting to false.')

    if not isinstance(config['dpi'], int):
        config['dpi'] = 90
        print('The dpi parameter must be a number. Defaulting to 90 dpi.')

    # filter by size
    size_filter = 0

    if 'size_filter' in config:
        try:
            size_filter = int(config['size_filter'])

            if size_filter < 0:
                print('A negative number of pixels for the size filter is not allowed.')
        except ValueError:
            print('The size filter is not a number.')

    num_icons = 0

    # loop through all specified directories
    for directory in config['input_dirs']:
        dir_path = os.path.join(config['input'], directory)

        # loop through all SVG files in this directory
        for icon_path in glob.glob(os.path.join(dir_path, '*.svg')):
            name_match = re.search('^([a-z-]+)\-([0-9]+)', os.path.splitext(os.path.basename(icon_path))[0])
            if name_match is not None:
                icon_id = name_match.group(1)
                size = int(name_match.group(2))

            if (size_filter > 0 and size != size_filter):
                continue

            # read in file contents
            try:
                iconfile = open(icon_path)
            except IOError:
                continue
            icon = iconfile.read()
            iconfile.close()

            # add remove canvas option for font output
            if config['format'] == 'font':
                config['global_style']['canvas'] = False

            # override global config with icon specific options
            mod_config = copy.deepcopy(config['global_style'])
            if icon_id in config:
                for option in config[icon_id]:
                    # when generating sprites only the fill colour can be overridden
                    if not config['format'] == 'sprite' or option == 'fill':
                        mod_config[option] = config[icon_id][option]

            try:
                # do modifications
                (size, icon) = modifySVG(mod_config, icon_id, size, icon)

                # create subdirs
                if not config['format'] == 'font':
                    if config['subdirs'] == True:
                        icon_out_path = os.path.join(config['output'], directory, icon_id + '-' + str(size) + '.svg')
                    else:
                        icon_out_path = os.path.join(config['output'], icon_id + '-' + str(size) + '.svg')
                else:
                    # remove subdirs and size info for font output
                    icon_out_path = os.path.join(config['output'], icon_id + '.svg')

                if not os.path.exists(os.path.dirname(icon_out_path)):
                    os.makedirs(os.path.dirname(icon_out_path))

                # save modified file
                try:
                    iconfile = open(icon_out_path, 'w')
                    iconfile.write(icon)
                    iconfile.close()
                except IOError:
                    print('Could not save the modified file ' + icon_out_path + '.')
                    continue

                num_icons += 1

                if config['format'] not in ['svg', 'png', 'sprite', 'font']:
                    print('Format must be either svg, png, sprite or font. Defaulting to svg.')

                # if PNG export generate PNG file and delete modified SVG
                if config['format'] == 'png':
                    if config['subdirs'] == True:
                        destination = os.path.join(config['output'], directory, icon_id + '-' + str(size) + '.png')
                    else:
                        destination = os.path.join(config['output'], icon_id + '-' + str(size) + '.png')

                    exportPNG(icon_out_path, destination, config['dpi'], config['retina'])
                    os.remove(icon_out_path)
            except Exception, e:
                print(e)
                continue


    if config['format'] == 'font':
        exportFont(config['output'], config['font']['output'], size)

    # generate sprite
    if config['format'] == 'sprite':
        sprite_cols = 12
        if 'cols' in config['sprite']:
            try:
                sprite_cols = int(config['sprite']['cols'])

                if sprite_cols <= 0:
                    print('A negative number of sprite columns or zero columns are not allowed. Defaulting to 12 columns.')
            except ValueError:
                print('Sprite columns is not a number. Defaulting to 12 columns.')

        outer_padding = 4
        if 'outer_padding' in config['sprite']:
            try:
                outer_padding = int(config['sprite']['outer_padding'])

                if outer_padding < 0:
                    print('A negative number of sprite outer padding is not allowed. Defaulting to a padding of 4.')
            except ValueError:
                print('Sprite outer padding is not a number. Defaulting to a padding of 4.')

        icon_padding = 4
        if 'icon_padding' in config['sprite']:
            try:
                icon_padding = int(config['sprite']['icon_padding'])

                if icon_padding < 0:
                    print('A negative number of sprite icon padding is not allowed. Defaulting to a padding of 4.')
            except ValueError:
                print('Sprite outer padding is not a number. Defaulting to a padding of 4.')

        sprite_background = None
        if 'background' in config['sprite']:
            sprite_background = config['sprite']['background']
            if re.match('^#[0-9a-f]{6}$', sprite_background) == None:
                sprite_background = None
                print('The specified shield fill is invalid. Format it as HEX (e.g. #1a1a1a). Defaulting to none (transparent).')

        sprite_file_name = 'sprite'
        if 'filename' in config['sprite']:
            sprite_file_name = config['sprite']['filename']
        sprite_out_path = os.path.join(config['output'], sprite_file_name)

        sprite_width = outer_padding * 2 + sprite_cols * (icon_padding * 2 + size)
        sprite_height = outer_padding * 2 + (icon_padding * 2 + size) * math.ceil(float(num_icons) / sprite_cols)

        sprite = lxml.etree.Element('svg')
        sprite.set('width', str(sprite_width))
        sprite.set('height', str(sprite_height))

        if sprite_background is not None:
            bg_rect = lxml.etree.Element('rect')
            bg_rect.set('width', str(sprite_width))
            bg_rect.set('height', str(sprite_height))
            bg_rect.set('style', 'fill:'+sprite_background+';')
            sprite.append(bg_rect)

        # loop through all specified directories (for sprite again)

        col = 1
        row = 1
        x = outer_padding + icon_padding
        y = outer_padding + icon_padding

        for directory in config['input_dirs']:
            dir_path = os.path.join(config['output'], directory)

            # loop through all SVG files in this directory (in alphabetical order)
            for icon_path in sorted(glob.glob(os.path.join(dir_path, '*.svg'))):
                name_match = re.search('^([a-z-]+)\-([0-9]+)', os.path.splitext(os.path.basename(icon_path))[0])
                if name_match is not None:
                    icon_id = name_match.group(1)
                    size = int(name_match.group(2))

                # read in file contents
                try:
                    iconfile = open(icon_path)
                except IOError:
                    continue
                icon_str = iconfile.read()
                iconfile.close()

                icon_xml = lxml.etree.fromstring(icon_str)
                icon_sprite = lxml.etree.Element('g')
                icon_sprite.set('id', icon_id)
                icon_sprite.set('transform', 'translate('+str(x)+','+str(y)+')')

                for child in list(icon_xml):
                    if child.attrib['id'] != 'metadata8' and child.attrib['id'] != 'defs6':
                        icon_sprite.append(child)

                sprite.append(icon_sprite)

                col += 1
                x += size + icon_padding * 2
                if col > sprite_cols:
                    row += 1
                    col = 1
                    x = outer_padding + icon_padding
                    y += size + icon_padding * 2

                # after adding to sprite delete SVG
                os.remove(icon_path)

            # after finishing directory remove it
            if os.path.isdir(dir_path):
                os.rmdir(dir_path)

        # save sprite SVG to file
        try:
            spritefile = open(sprite_out_path+'.svg', 'w')
            spritefile.write(lxml.etree.tostring(sprite, pretty_print=True))
            spritefile.close()
        except IOError:
            print('Could not save the sprite SVG file ' + sprite_out_path + '.svg' + '.')

        # export sprite as PNG
        exportPNG(sprite_out_path+'.svg', sprite_out_path+'.png', config['dpi'], config['retina'])

    return


# set config default values
def defaultValues(config):
    # config default values
    if 'input_dirs' not in config:
        config['input_dirs'] = ''

    if 'input' not in config:
        config['input'] = os.getcwd()

    if 'output' not in config:
        config['output'] = os.path.join(os.getcwd(), 'export')

    if 'empty_output' not in config:
        config['empty_output'] = False

    if 'format' not in config:
        config['format'] = 'png'

    if 'retina' not in config:
        config['retina'] = False

    if 'subdirs' not in config:
        config['subdirs'] = True

    if 'dpi' not in config:
        config['dpi'] = 90

    if 'global_style' not in config:
        config['global_style'] = {}

    if config['format'] == 'font':
        if 'font' not in config:
            config['font'] = {}

        if 'size_filter' not in config:
            config['size_filter'] = 14

        if 'output' not in config['font']:
            config['font']['output'] = os.path.join(os.getcwd(), 'font')

    return


# export PNG
def exportPNG(source, destination, dpi, retina):
    for i in range(0, 2):
        # TODO Windows?
        try:
            # rsvg is preferred because faster, but fallback to Inkscape when rsvg is not installed
            subprocess.call(['rsvg', '-a', '--zoom='+str(round(float(dpi) / 90, 2)), '--format=png', source, destination])
        except OSError:
            try:
                subprocess.call(['inkscape', '--export-dpi='+str(dpi), '--export-png='+destination, source])
            except OSError:
                # if neither is installed print a message and exit
                sys.exit('Export to PNG requires either rsvg or Inkscape. Please install one of those. rsvg seems to be faster (if you just want to export). Exiting.')

        if not retina:
            break
        else:
            dpi *= 2
            # append @2x to file name
            split_name = os.path.splitext(destination)
            destination = split_name[0]+'@2x'+split_name[1]

    return


# export icon font
def exportFont(source, destination, size):
    copyright_message = 'Osmic icon font (https://github.com/nebulon42/osmic), License: SIL OFL'
    # TODO Windows?
    try:
        subprocess.call(['fontcustom', 'compile', source, '--force', '--output=' + destination, '--font-name=osmic', '--no-hash', '--font-design-size=' + str(size), '--css-selector=.oc-{{glyph}}', '--copyright=' + copyright_message])

        # strip out metadata of SVG font
        svg_font = os.path.join(destination, 'osmic.svg')
        try:
            fontfile = open(svg_font)
            font = fontfile.read()
            fontfile.close()

            xml = lxml.etree.fromstring(font)
            xpEval = lxml.etree.XPathEvaluator(xml)
            xpEval.register_namespace('def', 'http://www.w3.org/2000/svg')
            metadata = xpEval('//def:metadata')[0]
            metadata.text = copyright_message
            lxml.etree.ElementTree(xml).write(svg_font, pretty_print=True)
        except IOError:
            # if we cannot read the file we just let it be
            pass
    except OSError:
        # fontcustom is not installed
        sys.exit('Export as icon font requires Font Custom. See http://fontcustom.com. Exiting.')
    return


# modifications to the SVG
def modifySVG(config, icon_id, size, icon):
    xml = lxml.etree.fromstring(icon)
    # cleanup namespaces as Inkscape adds a (unnecessary?) xmlns:svg namespace,
    # which leads to unwanted svg:path elements for halos
    lxml.objectify.deannotate(xml, cleanup_namespaces=True)
    xpEval = lxml.etree.XPathEvaluator(xml)
    xpEval.register_namespace('def', 'http://www.w3.org/2000/svg')

    # sanity checks
    paths = xpEval("//def:path")
    if len(paths) > 1:
        raise Exception("Icon '"+icon_id+"' contains more than one path. Skipping.")
    if paths[0].get("id") == None:
        raise Exception("Icon '"+icon_id+"' contains no path with id attribute. Skipping.")
    if paths[0].get("id") != icon_id:
        raise Exception("Icon file name ("+icon_id+") and path id attribute ("+paths[0].get("id")+") do not match. Skipping.")

    # set padding of icon
    padding = 0
    if 'padding' in config:
        try:
            padding = int(config['padding'])

            if padding < 0:
                padding = 0
                print('Negative padding is not allowed. Defaulting to 0.')
        except ValueError:
            print('Padding is not a number.')



    # add shield
    shield_size = size
    if 'shield' in config:
        if 'padding' in config['shield']:
            try:
                shield_padding = int(config['shield']['padding'])

                if shield_padding > 0:
                    shield_size += int(config['shield']['padding']) * 2
                else:
                    print('Negative shield padding is not allowed. Defaulting to 0.')
            except ValueError:
                print('Shield padding is not a number. Defaulting to 0.')

        shield_rounded = 0
        if 'rounded' in config['shield']:
            try:
                shield_rounded = int(config['shield']['rounded'])

                if shield_rounded <= 0:
                    shield_rounded = 0
                    print('A negative shield corner radius is not allowed. Defaulting to unrounded corners.')
            except ValueError:
                print('Shield corner radius is not a number. Defaulting to unrounded corners.')

        shield_fill = '#000000'
        if 'fill' in config['shield']:
            shield_fill = config['shield']['fill']
            if re.match('^#[0-9a-f]{6}$', shield_fill) == None:
                shield_fill = '#000000'
                print('The specified shield fill is invalid. Format it as HEX (e.g. #1a1a1a). Defaulting to #000000 (black).')
        else:
            print('Shield fill not specified. Defaulting to #000000 (black).')

        stroke = 'stroke:none;'
        stroke_fill = None
        if 'stroke_fill' in config['shield']:
            stroke_fill = config['shield']['stroke_fill']
            if re.match('^#[0-9a-f]{6}$', stroke_fill) == None:
                print('The specified shield stroke fill is invalid. Format it as HEX (e.g. #1a1a1a).')

        stroke_width = None
        if 'stroke_width' in config['shield']:
            try:
                stroke_width = float(config['shield']['stroke_width'])

                if stroke_width < 0:
                    stroke_width = 1
                    print('Negative shield stroke widths are not allowed. Defaulting to width=1.')
            except ValueError:
                print('The specified shield stroke width is not a number.')

        if stroke_fill is not None and stroke_width is not None:
            # do not specify stroke if stroke_width = 0 was specified
            if stroke_width > 0:
                stroke = 'stroke:'+stroke_fill+';stroke-width:'+str(stroke_width)+';'
        else:
            # do not print warning if stroke width = 0 or none was specified
            if stroke_width > 0:
                print('Shield: Defined either stroke_fill without stroke_width or vice versa. Both are required for strokes to appear.')

        shield = lxml.etree.Element('rect')
        shield.set('x', str(padding))
        shield.set('y', str(padding))
        shield.set('width', str(shield_size))
        shield.set('height', str(shield_size))
        if shield_rounded > 0:
            shield.set('rx', str(shield_rounded))
            shield.set('ry', str(shield_rounded))
        shield.set('id', 'shield')
        shield.set('style', 'fill:'+shield_fill+';'+stroke)

        canvas = xpEval("//def:rect[@id='canvas']")[0]
        canvas.addnext(shield)


    # add icon halo
    halo_width = 0
    if 'halo' in config:
        halo_fill = '#fffff'
        if 'fill' in config['halo']:
            halo_fill = config['halo']['fill']
            if re.match('^#[0-9a-f]{6}$', halo_fill) == None:
                halo_fill = '#ffffff'
                print('The specified halo fill is invalid. Format it as HEX (e.g. #1a1a1a). Defaulting to #ffffff (white).')
        else:
            print('Halo fill not specified. Defaulting to #ffffff (white).')

        if 'width' in config['halo']:
            try:
                halo_width = float(config['halo']['width'])

                if halo_width < 0:
                    halo_width = 1
                    print('Halo widths < 0 do not make sense. Defaulting to width=1.')
            except ValueError:
                print('The specified halo width is not a number.')

        halo_opacity = None
        if 'opacity' in config['halo']:
            try:
                halo_opacity = float(config['halo']['opacity'])

                if halo_opacity <= 0 or halo_opacity > 1:
                    halo_opacity = 0.3
                    print('Halo opacity must lie between 0 and 1 (e.g. 0.5). Opacities of 0 do not make sense. Defaulting to 0.3.')
            except ValueError:
                print('The specified halo opacity is not a number.')

        if not halo_width == 0:
            icon_element = xpEval("//def:path[@id='"+icon_id+"']")[0]
            halo = copy.deepcopy(icon_element)
            halo.set('id', 'halo')
            halo.set('style', 'fill:'+halo_fill+';stroke:'+halo_fill+';stroke-width:'+str(halo_width * 2)+';opacity:'+str(halo_opacity)+';')
            halo.set('transform', 'translate('+str(padding + halo_width)+','+str(padding + halo_width)+')')
            icon_element.addprevious(halo)


    # change fill colour of icon
    if 'fill' in config:
        if not re.match('^#[0-9a-f]{6}$', config['fill']) == None:
            path = xpEval("//def:path[@id='"+icon_id+"']")[0]
            path.attrib['style'] = re.sub('fill:#[0-9a-f]{6};?', 'fill:'+config['fill']+';', path.attrib['style'])
        else:
            print('The specified fill is invalid. Format it as HEX (e.g. #1a1a1a).')


    # adjust document and canvas size, icon position
    shieldIncrease = shield_size - size
    size += int(max((shield_size - size), halo_width * 2) + padding * 2)
    xml.attrib['viewBox'] = '0 0 ' + str(size) + ' ' + str(size)
    canvas = xpEval("//def:rect[@id='canvas']")[0]
    canvas.attrib['width'] = str(size)
    canvas.attrib['height'] = str(size)
    icon_xml = xpEval("//def:path[@id='"+icon_id+"']")[0]
    icon_xml.set('transform', 'translate('+str(max(shieldIncrease / 2, halo_width) + padding)+','+str(max(shieldIncrease / 2, halo_width) + padding)+')')

    # strip 'stroke:none' from style attributes
    icon_xml.attrib['style'] = re.sub(';stroke:none', '', icon_xml.attrib['style'])

    # remove canvas for font output
    if 'canvas' in config and config['canvas'] == False:
        canvas.getparent().remove(canvas)

    icon = lxml.etree.tostring(xml, encoding='utf-8', xml_declaration=True, pretty_print=True)
    return (size, icon)

if __name__ == "__main__":
    main()

