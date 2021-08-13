#!/usr/bin/env python3

import sys
import os
import json
import re
import yaml

if __name__ == "__main__":
    index_json = sys.argv[1]
    config_yaml = sys.argv[2]
    src_adoc = sys.argv[3]
    build_dir = sys.argv[4]
    build_adoc = sys.argv[5]
    output_subdir = os.path.basename(os.path.dirname(build_adoc))
    adoc_filename = os.path.basename(build_adoc)

    with open(config_yaml) as config_fh:
        site_config = yaml.safe_load(config_fh)

    index_title = None
    with open(index_json) as json_fh:
        data = json.load(json_fh)
        for tab in data['tabs']:
            if 'path' in tab and tab['path'] == output_subdir:
                for subitem in tab['subitems']:
                    if 'subpath' in subitem and subitem['subpath'] == adoc_filename:
                        index_title = subitem['title']
                        break
                if index_title is not None:
                    break
    if index_title is None:
        raise Exception("Couldn't find title for {} in {}".format(os.path.join(output_subdir, adoc_filename), index_json))

    new_contents = ''
    seen_header = False
    with open(src_adoc) as in_fh:
        for line in in_fh.readlines():
            if line.startswith('== '):
                if not seen_header:
                    seen_header = True
                    line += "Edit this {}[on GitHub]\n\n".format(os.path.join(site_config['githuburl'], 'blob', site_config['githubbranch_edit'], src_adoc))
            else:
                m = re.match('^(include::)(.+)(\[\]\n?)$', line)
                if m:
                    line = m.group(1) + os.path.join('{includedir}/{parentdir}', m.group(2)) + m.group(3)
            new_contents += line

    with open(build_adoc, 'w') as out_fh:
        out_fh.write(""":parentdir: {}
:page-layout: docs
:includedir: {}
:doctitle: {}
:page-sub_title: {}

{}
""".format(output_subdir, build_dir, '{} - {}'.format(site_config['title'], index_title), index_title, new_contents))
