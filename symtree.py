#!/usr/share/python/

import argparse
import os.path
import json
import re
import pprint

class LogLevel:
    Error = 0
    Warning = 1
    Verbose = 2

log_level = LogLevel.Error
options = []
regexes = []

def log(message, level):
    if level == LogLevel.Error:
        message = "ERROR! " + message

    if level <= log_level:
        print message

# Ensure the options are as expected.
def init_options():
    global log_level, options
    parser = argparse.ArgumentParser(description="Create a mirrored folder structure with symlinked files.")

    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('-V', '--veryverbose', action='store_true', help='insanely verbose output')
    parser.add_argument('-c', '--create', action='store_true', help='create destination if it does not exist')
    parser.add_argument('-f', '--followsymlinks', action='store_true', help='symtree will follow symbolic links for source folders')
    parser.add_argument('-o', '--overwritesymlinks', action='store_true', help='symtree will overwrite symlinks in the destination directory')
    parser.add_argument('--settings', default='symtree.json', help='override the default settings file of symtree.json')
    parser.add_argument('source', help='the source directory')
    parser.add_argument('dest', help='the target directory, will be the highest level mirror of source')

    options = parser.parse_args()

    if options.verbose:
        log_level = LogLevel.Warning

    if options.veryverbose:
        log_level = LogLevel.Verbose

    options.source = os.path.abspath(options.source)
    options.dest = os.path.abspath(options.dest)
    log("Source: " + options.source, LogLevel.Warning)
    log("Dest  : " + options.dest, LogLevel.Warning)

    return check_paths(options.source, options.dest, options.followsymlinks)

# Check the validity of the paths.
def check_paths(source, dest, follow):
    # If the source and dest are symlink, they could be nested. Default is to fail out unless user says they want to follow symlinks.
    if os.path.islink(source) and not follow:
        log("SOURCE is a symbolic link (enable --followsymlinks if this is intentional)", LogLevel.Error)
        return False

    if os.path.islink(dest) and not follow:
        log("DEST is a symbolic link (enable --followsymlinks if this is intentional)", LogLevel.Error)
        return False

    # Check to make sure one path isn't below another.
    if source.startswith(dest):
        log("SOURCE is nested under DEST. This is not allowed.", LogLevel.Error)
        return False

    if dest.startswith(source):
        log("DEST is nested under SOURCE. This is not allowed.", LogLevel.Error)
        return False

    return True

# Start the loop
def symtree(source, dest):
    source = source + "/"
    dest = dest + "/"

    log("\nEntering " + source + "\n", LogLevel.Verbose)

    for dir in os.listdir(source):
        dest_dir = dest + normalize_string(dir)
        dir = source + dir

        if os.path.isdir(dir):
            if not os.path.islink(dir) or options.followsymlinks:
                create_folder(dest_dir)
                symtree(dir, dest_dir)
            else:
                log('Ignoring symlink source folder (' + dir + ')', LogLevel.Warning)
        elif os.path.isfile(dir):
            create_link(dir, dest_dir)

# Create the folder if necessary.
def create_folder(folder):
    if not os.path.exists(folder):
        log("Creating folder (" + folder + ")", LogLevel.Warning)
        os.mkdir(folder)

# Create link.
def create_link(source, link_name):
    global options

    if os.path.exists(link_name):
        if options.overwritesymlinks:
            os.remove(link_name)
        else:
            log("(" + link_name + ") alread exists. Skipping...", LogLevel.Warning)
            return
    elif os.path.lexists(link_name):
        # symlink exists but is broken
        os.remove(link_name)

    log("Linking file (" + source + ")", LogLevel.Verbose)
    os.symlink(source, link_name)

# Load the settings file.
def load_settings(file):
    global regexes

    # Add default regex in case of failure.
    default_regex_raw = r'<>:"\\|?*'
    regexes.append({ 'regex': re.compile('[' + default_regex_raw + ']'), 'replace': '_', 'regex_raw': default_regex_raw})

    try:
        f = open(file)
        json_data = f.read()
        f.close()

        json_data = re.sub("//.*?\n", "", json_data)
        settings = json.loads(json_data)

        if 'regular_expressions' in settings:
            # Remove default.
            regexes = []

            for regex, replace in settings['regular_expressions'].items():
                log('Loading regex from file: s/' + regex + '/' + replace + '/g', LogLevel.Warning)
                regexes.append({ 'regex': re.compile('[' + regex + ']'), 'replace': replace, 'regex_raw': regex})
        else:
            # Append default regex.
            regexes.append({ 'regex': re.compile('[' + default_regex_raw + ']'), 'replace': '_', 'regex_raw': default_regex_raw})

    except IOError as e:
        log("IO error({0}): {1}".format(e.errno, e.strerror), LogLevel.Error)

    log(pprint.pformat(regexes), LogLevel.Warning)

# Apply the regular expression to the string to normalize it.
def normalize_string(source):
    result = source

    for regex in regexes:
        result = re.sub(regex['regex'], regex['replace'], result)

    if source != result:
        log('Renaming (' + source + ') to (' + result + ')', LogLevel.Verbose)

    return result

def main():
    if not init_options():
        return

    load_settings(options.settings)

    if not os.path.exists(options.dest):
        if options.create:
            create_folder(options.dest)
        else:
            log("Destination does not exist (" + options.dest + ")", LogLevel.Error)
            return

    symtree(options.source, options.dest);

if __name__ == "__main__":
    main()
