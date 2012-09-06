#!/usr/share/python/

from optparse import OptionParser
import os.path
import json
import re
from pprint import pprint

class LogLevel:
    Error = 0
    Warning = 1
    Verbose = 2

log_level = LogLevel.Error
options = []

def log(message, level):
    if level == LogLevel.Error:
        message = "ERROR! " + message

    if level <= log_level:
        print message

# Ensure the options are as expected.
def init_options():
    global log_level, options
    parser = OptionParser(usage="usage: %prog [options] SOURCE DEST")

    parser.add_option("-v", "--verbose", help="verbose output", action="store_true", dest="verbose", default=False)
    parser.add_option("-V", "--veryverbose", help="insanely verbose output", action="store_true", dest="veryverbose", default=False)
    parser.add_option("-c", "--create", help="create destination if it does not exist", action="store_true", dest="create", default=False)
    parser.add_option("-f", "--followsymlinks", help="causes symtree to follow symbolic links for source and destination folders",
        action="store_true", dest="follow", default=False)
    parser.add_option("-o", "--overwritesymlinks", help="when set symtree will overwrite symlinks in the destination directory",
        action="store_true", dest="overwrite", default=False)

    (options, args) = parser.parse_args()

    # Get the positional arguments SOURCE and DEST
    if len(args) != 2:
        parser.error("incorrect number of arguments: provide SOURCE and DEST")

    if options.verbose:
        log_level = LogLevel.Warning

    if options.veryverbose:
        log_level = LogLevel.Verbose

    options.source = os.path.abspath(args[0])
    options.dest = os.path.abspath(args[1])
    log("Source: " + options.source, LogLevel.Warning)
    log("Dest  : " + options.dest, LogLevel.Warning)

    return check_paths(options.source, options.dest, options.follow)

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

    log("Entering " + source, LogLevel.Verbose)

    for dir in os.listdir(source):
        dest_dir = dest + dir
        dir = source + dir

        if os.path.isdir(dir):
            create_folder(dest_dir)
            symtree(dir, dest_dir)
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
        if options.overwrite:
            os.remove(link_name)
        else:
            log("(" + link_name + ") alread exists. Skipping...", LogLevel.Warning)
            return
    elif os.path.lexists(link_name):
        # symlink exists but is broken
        os.remove(link_name)

    log("Linking file (" + source + ")", LogLevel.Verbose)
    os.symlink(source, link_name)

def load_settings(file):
    try:
        f = open(file)
        json_data = f.read()
        f.close()

        json_data = re.sub("//.*?\n", "", json_data)
        settings = json.loads(json_data)
        pprint(settings)
    except IOError as e:
        log("IO error({0}): {1}".format(e.errno, e.strerror), LogLevel.Error)

def main():

    if not init_options():
        return

    load_settings("symtree.json")

    if not os.path.exists(options.dest):
        if options.create:
            create_folder(options.dest)
        else:
            log("Destination does not exist (" + options.dest + ")", LogLevel.Error)
            return

    symtree(options.source, options.dest);

if __name__ == "__main__":
    main()
