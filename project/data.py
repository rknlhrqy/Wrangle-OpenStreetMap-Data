# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 19:46:09 2016

@author: kenren
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import os
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
address_re = re.compile(r'addr:[a-z]*$')
address_street_re = re.compile(r'addr:street:[a-z]*$')
phone_re = re.compile(r'phone')
amenity_re = re.compile(r'amenity')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def find_path(filename):
    script_dir = os.path.dirname(__file__)
    rel_path = filename
    abs_file_path = os.path.join(script_dir, rel_path)
    return abs_file_path 

def set_dict_value(element, element_attrib, data_dict):
    if element_attrib in element.attrib:
        data_dict[element_attrib] = element.attrib[element_attrib]

def shape_element(element):
    created = {}
    address = {}
    pos = []
    node = {}
    node_refs = []
    if element.tag == "node" or element.tag == "way" or element.tag == "relation":
        # YOUR CODE HERE
        # Get the element's tag.
        node['element_type'] = element.tag
        # Get the element's 'visible' and 'id'
        set_dict_value(element, 'visible', node)
        set_dict_value(element, 'id', node)
        # Get the element's attribute defined in "CREATED".
        for each in CREATED:
            set_dict_value(element, each, created)
        # If Dictionary "created" is not empty, write it to Dictionary "node"
        if len(created) != 0:
            node['created'] = created
        # If the element's attribute has 'lat' and 'lon'
        if 'lat' in element.attrib:
            pos.append(float(element.attrib['lat']))
            pos.append(float(element.attrib['lon']))
        # If list 'pos' is not empty, write it to Dictionary 'node'
        if len(pos) != 0:            
            node['pos'] = pos
        # Check all elements under the element of 'node' and 'way'
        for child in element:
            # if there is element "ref", add its value to list "node_refs".
            if 'ref' in child.attrib:
                node_refs.append(child.attrib['ref'])
                continue
            # if 'k' exists,
            if 'k' in child.attrib:
                # find if any 'v' value has problem charactors.
                # if yes, drop it.
                m = problemchars.search(child.attrib['k'])
                if m:
                    continue
                # find if any 'k' is 'phone', 
                # if yes, get its phone number and extract the 10-digit
                # phone number
                m = phone_re.search(child.attrib['k'])
                if m:
                    # Get phone number string
                    # extract the digits from the phone number string
                    # if the length is more than 10, it has the 
                    # country code "1". It will be removed.
                    raw_phone = child.attrib['v']
                    phone = re.findall(r'\d+', raw_phone)
                    phone_str1 = ""                    
                    phone_str = phone_str1.join(phone)
                        
                    # Add Dictionary "phone" to Dictionary "node'.
                    if len(phone_str) != 10:
                        node['phone'] = phone_str[1:]
                    else:
                        node['phone'] = phone_str
                    
                    continue
                # find if 'k' is 'amenity:XXXX',
                # if so, only pick up 'amenity'
                m = amenity_re.search(child.attrib['k'])
                if m:
                    node['amenity'] = child.attrib['v']
                    continue                    
                
                # find if 'k' is 'addr:street:XXXX',
                # if yes, drop it.
                m = address_street_re.search(child.attrib['k'])
                if m:
                    continue
                # find if 'k' is 'addr:XXXX',                    
                m = address_re.search(child.attrib['k'])
                if m:
                    # Get the 'k' value
                    addr_str = m.group()
                    # Split it based on ":", and get the second part.
                    addr_item = re.split(":", addr_str)[1]
                    # Add 'v' value to Dictionary "address"
                    # If it is postcode, and the format is 95014-2969,
                    # it should be changed as 95014.
                    if addr_item == "postcode":
                        postcode = child.attrib['v']
                        address[addr_item] = postcode[0:5]
                    else:                        
                        address[addr_item] = child.attrib['v']
                    # Add Dictionary "address" to Dictionary "node'.
                    node['address'] = address
                    continue
                # Write other values into Dictionary "node"
                node[child.attrib['k']] = child.attrib['v']
        #
        if len(address) != 0:
            node['address'] = address
        if len(node_refs) != 0:
            node['node_refs'] = node_refs
        
        return node
    else:
        return None


def process_map(filename, pretty = False):
    # You do not need to change this file
    file_in = find_path(filename)
    file_out = "{0}.json".format(file_in)
    #data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                #data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    #return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    #data = process_map('san-jose_california.osm/san-jose_california.osm', True)
    process_map('san-jose_california.osm/san-jose_california.osm', True)
    #pprint.pprint(data)

if __name__ == "__main__":
    test()