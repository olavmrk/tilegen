#!/usr/bin/env python3
import argparse
import itertools
import math
import os
import sys

import PIL.Image


def parse_args():
    parser = argparse.ArgumentParser(description='Build image tiles')
    parser.add_argument('file')
    parser.add_argument('zoom', type=int)
    parser.add_argument('x_min', type=int)
    parser.add_argument('y_min', type=int)
    return parser.parse_args()


def main():
    args = parse_args()

    output_directory = os.path.join(os.path.abspath(os.path.dirname(args.file)), 'output')
    if os.path.exists(output_directory):
        print('Output directory already exists: {output_directory}'.format(output_directory=output_directory), file=sys.stderr)
        sys.exit(1)
    os.mkdir(output_directory)

    PIL.Image.MAX_IMAGE_PIXELS = None  # Disable decompression bomb error
    with PIL.Image.open(args.file) as image:
        image.load()
        print('Loaded {width}x{height} image'.format(width=image.width, height=image.height))
        for zoom in range(0, args.zoom + 1):
            print('Processing zoom level {zoom}'.format(zoom=zoom))
            scale = 2**(args.zoom - zoom)
            zoom_x_min = args.x_min // scale
            zoom_y_min = args.y_min // scale
            scaled = image.resize(
                size=(math.ceil(image.width/scale), math.ceil(image.height/scale)),
                resample=PIL.Image.BICUBIC,
            )
            for y in itertools.count(zoom_y_min):
                y_offset = math.floor((y * scale - args.y_min) * 256 / scale)
                if y_offset > scaled.height:
                    break
                for x in itertools.count(zoom_x_min):
                    print('Tile: {zoom}-{x}-{y}'.format(zoom=zoom, x=x, y=y))
                    x_offset = math.floor((x * scale - args.x_min) * 256 / scale)
                    if x_offset > scaled.width:
                        break
                    x_max = x_offset + 256
                    y_max = y_offset + 256
                    print('Source data:', x_offset, y_offset, x_max, y_max)
                    tile = scaled.transform(
                        size=(256,256),
                        method=PIL.Image.EXTENT,
                        data=(x_offset, y_offset, x_max, y_max),
                        resample=PIL.Image.NEAREST,
                        fillcolor='transparent',
                    )
                    tile_filename = '{zoom}-{x}-{y}.png'.format(zoom=zoom, x=x, y=y)
                    tile_path = os.path.join(output_directory, tile_filename)
                    tile.save(tile_path)


if __name__ == '__main__':
    main()
