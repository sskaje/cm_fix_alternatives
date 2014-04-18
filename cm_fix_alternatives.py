#!/usr/bin/python
"""
Fix alternatives for CDH
Author: sskaje (https://sskaje.me/)

Blog posts:
    https://sskaje.me/2014/04/fix-alternatives-cloudera-manager-cdh/
    https://sskaje.me/2014/02/fix-hadoop-conf-alternatives-cdh5/


"""
import os
import json


CDH_ROOT = "/opt/cloudera/parcels/CDH"
ALTERNATIVES_JSON = CDH_ROOT + "/meta/alternatives.json"
ALTERNATIVES_BIN = "alternatives"

DRY_RUN = False


def run_command(command):
    """ run command """
    if DRY_RUN is True:
        print "Dry Run: " + command
    else:
        os.system(command)


def alternatives_install(link, name, path, priority):
    """ alternatives --install """
    run_command(ALTERNATIVES_BIN + " --install " + link + " " + name + " '" + path + "' " + str(priority))


def alternatives_remove(name, path):
    """ alternatives --remove """
    run_command(ALTERNATIVES_BIN + " --remove " + name + " '" + path + "'")


def alternatives_set(name, path):
    """ alternatives --set """
    run_command(ALTERNATIVES_BIN + " --set " + name + " '" + path + "'")


def fix(key, config):
    """ Fix alternatives """
    print "Fix " + key

    # get files
    # f = os.popen(ALTERNATIVES_BIN + " --display " + key + " |  grep -E '^/'")
    f = os.popen(ALTERNATIVES_BIN + " --display " + key + " |  grep priority")

    path_to_be_saved = []

    # read all current options and delete invalid from alternatives
    for i in f.readlines():
        # split and get the full path
        p = i.rsplit(' - ', 2)
        path = p[0].strip()

        print "Checking " + path + " ..."

        if not os.path.exists(path):
            # if file/dir not exists, delete it
            print "File not found"

        elif path.endswith('.dist') or path.endswith('.empty'):
            # if file/dir is linked to be default, keep it but set a lower priority
            print "Using default"

        elif config['isDirectory'] is True and not os.path.isdir(path):
            print "Directory required"

        elif config['isDirectory'] is False and not os.path.isfile(path):
            print "File required"

        else:
            print "OK"
            path_to_be_saved.append(path)

        # Remove in any case
        alternatives_remove(key, path)

    print "Reinstalling defaults"
    # Default source
    if not config['source'].startswith("/"):
        default_source = CDH_ROOT + "/" + config['source']
    else:
        default_source = config['source']

    alternatives_install(config['destination'], key, default_source, config['priority'])

    for path in path_to_be_saved:
        print "Set path: " + path
        alternatives_set(key, path)

    print ""



def get_alternatives_from_meta():
    """ get all default alternatives configurations from meta/ in CDH's parcel """
    if not os.path.exists(ALTERNATIVES_JSON):
        raise Exception(ALTERNATIVES_JSON + " not found!")

    fp = open(ALTERNATIVES_JSON)
    try:
        json_content = fp.read()
    finally:
        fp.close()

    return json.loads(json_content)


def main():
    print "Fix alternatives for CDH"
    print "Author: sskaje (https://sskaje.me/)"
    print "!!!WARNING: RUN AT YOUR OWN RISK!!!"

    alternatives = get_alternatives_from_meta()
    for i in alternatives:
        fix(i, alternatives[i])

    print "Please deploy client configuration in Cloudera Manager"

if __name__ == "__main__":
    main()
