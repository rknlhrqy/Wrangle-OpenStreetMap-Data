# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 23:03:38 2016

@author: kenren
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "san-jose_california.osm/san-jose_california.osm"  # Replace this with your osm file
SAMPLE_FILE = "san-jose_california.osm/san-jose_california_sample.osm"

def find_path(filename):
    script_dir = os.path.dirname(__file__)
    rel_path = filename
    abs_file_path = os.path.join(script_dir, rel_path)
    return abs_file_path 

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def test():
    abs_file_path1 = find_path(SAMPLE_FILE)
    abs_file_path2 = find_path(OSM_FILE)    
    with open(abs_file_path1, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        # Write every 10th top level element
        for i, element in enumerate(get_element(abs_file_path2)):
            if i % 10 == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write('</osm>')
    
if __name__ == "__main__":
    test()    