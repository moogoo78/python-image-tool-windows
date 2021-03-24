#!/usr/bin/env python3

'''
integrated tools for camera-trap

main.py -m get-config -i camera-trap-desktop.ini -o std
main.py -m set-config -i camera-trap-desktop.ini -s Folders:foo:foo_path -o std
main.py -m add-folder -d camera-trap.db -f d:\path\to\images
'''

import argparse
import json

from clam import (
    Config,
    Source
)


MOD_CHOICES = [
    'get-config',
    'set-config',
    'add-folder',
]

#sys.stdout.reconfigure(encoding='utf-8')

def main(args):
    print (args)
    result = {
        'is_success': False,
        'data': None,
        'foo': '中文',
    }
    if args.mod == 'get-config':
        config = Config(args.ini_file)
        res = config.get_config()
        result['data'] = res

    elif args.mod == 'set-config':
        if sov := args.section_option_value.split(':'):
            # check input value
            if len(sov) < 3 or sov[1] == '':
                result['error'] = 'section:option:value syntax error'
                return result
            else:
                config = Config(args.ini_file)
                res = config.set_config(sov[0], sov[1], sov[2])
                result['data'] = res
    elif args.mod == 'add-folder':
        if not args.folder:
            result['error'] = 'no set folder path'
        else:
            src = Source('database', name=args.db_file)
            res = src.from_folder(args.folder)
            result['data'] = res
    else:
        result['is_success'] = False
        result['error'] = 'no module'
        return result
    result['is_success'] = True
    return result

parser = argparse.ArgumentParser(description='python tools for camera-trap-desktop')

parser.add_argument('-m', '--mod',
                    dest='mod',
                    choices=MOD_CHOICES,
                    required=True,
                    help='action')
parser.add_argument('-s', '--set-config',
                    dest='section_option_value',
                    help='section:option:value')
parser.add_argument('-f', '--from-folder',
                    dest='folder',
                    help='folder path')
parser.add_argument('-i', '--ini',
                    dest='ini_file',
                    help='ini file path')
parser.add_argument('-d', '--db',
                    dest='db_file',
                    help='save to sqlite3')
parser.add_argument('-o', '--output',
                    dest='output',
                    choices=['json', 'std'],
                    help='')
args = parser.parse_args()

if __name__ == '__main__':
    ret = main(args)
    if args.output:
        if args.output == 'std':
            print (ret)
        elif args.output == 'json':
            print (json.dumps(ret))

#im = Image.open("otter.JPG")
#im.thumbnail((300,300), Image.ANTIALIAS)

#im.save('thumb.jpg', "JPEG")
