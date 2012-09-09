symtree
=======

A tool to create a mirrored symlink directory tree. The main use case is when the source files have characters in their name that are not always desirable. For example, a tree of files that contain Unix valid characters (eg, :"*>) that you want to share with Windows via Samba. You can use this tool to create file names that are valid in Windows without duplicating the content.

Folders are created in the target directory. These are actual folders and not links. The files are symbolic links to the source folder. Optionally, enabled by default, a regular expression can be ran on each folder and file name before the destination is created.

Usage
-----

Basic usage `python symtree.py SOURCE DEST`. To mirror a folder `files` into a folder `windows_files` you would use `python symtree.py files windows_files`.

    usage: symtree.py [-h] [-v] [-V] [-c] [-f] [-o] [--settings SETTINGS]
                      source dest

    Create a mirrored folder structure with symlinked files.

    positional arguments:
      source                the source directory
      dest                  the target directory, will be the highest level mirror
                            of source

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose output
      -V, --veryverbose     insanely verbose output
      -c, --create          create destination if it does not exist
      -f, --followsymlinks  symtree will follow symbolic links for source folders
      -o, --overwritesymlinks
                            symtree will overwrite symlinks in the destination
                            directory
      --settings SETTINGS   override the default settings file of symtree.json

Settings File
-------------

A settings file can be supplied which allows a set of regular expressions to be loaded into symtree, each of which are run on the on the file and folder names before they are linked. If an invalid setting file is provided, the default regular expression is `s/<>:"\\|?*/_`.

To add regular expressions to the settings file, follow this format:

    "regular_expressions": {
        "<>\"\\\\|*": "_",
        "?": "",
        ":": " -"
    }
