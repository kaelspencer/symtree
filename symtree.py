#!/usr/share/python/

from optparse import OptionParser
import os.path

# Ensure the options are as expected.
def init_options():
    parser = OptionParser(usage="usage: %prog [options] SOURCE DEST")

    parser.add_option("-v", "--verbose", help="verbose output", action="store_true", dest="verbose", default=False)
    parser.add_option("-V", "--veryverbose", help="insanely verbose output", action="store_true", dest="veryverbose", default=False)
    parser.add_option("-c", "--create", help="create destination if it does not exist", action="store_true", dest="create", default=False)
    parser.add_option("-f", "--followsymlinks", help="causes symtree to follow symbolic links for source and destination folders", action="store_true", dest="follow", default=False)

    (options, args) = parser.parse_args()

    # Get the positional arguments SOURCE and DEST
    if len(args) != 2:
        parser.error("incorrect number of arguments: provide SOURCE and DEST")

    source = os.path.abspath(args[0])
    dest = os.path.abspath(args[1])
    print "Source: " + source
    print "Dest  : " + dest

    # If the source and dest are symlink, they could be nested. Default is to fail out unless user says they want to follow symlinks.
    if os.path.islink(source) and not options.follow:
        parser.error("SOURCE is a symbolic link (enable --followsymlinks if this is intentional)")

    if os.path.islink(dest) and not options.follow:
        parser.error("DEST is a symbolic link (enable --followsymlinks if this is intentional)")

def main():
    init_options()

if __name__ == "__main__":
    main()
