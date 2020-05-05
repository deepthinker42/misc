import os
import sys
import yaml
import pprint

pp = pprint.PrettyPrinter()
with open('test.yml') as f:
    docs = yaml.load_all(f, Loader=yaml.FullLoader)
    for doc in docs:
        pp.pprint(doc)
        print (doc['all']['children']['aperture']['hosts']['rg-rhel8-ap2.ticom-geo.com']['cert']['email'])

    """
        for k, v in doc.items():
            print(k, "->", v)
    """
