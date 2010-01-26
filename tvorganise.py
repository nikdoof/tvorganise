#!/usr/bin/env python
#encoding:utf-8
"""
tvorganise.py

This parses "Show Name - [01x23] - Episode Name.avi"
filenames and automatically copies them to
the location format defined in the configuration file.
"""

import os, sys, re
from optparse import OptionParser
import shutil

config = {}
regex_config={}

##############################################
# Path configs

# Where to move the files
config['target_path'] = "/mnt/vault/video/TV Shows/%(file_showname)s/Season %(seasno)s/"


##############################################
# Regex configs

# Import shared filename pattern config
from filename_config import tv_regex

# end configs
##############################################

def findFiles(args):
    """
    Takes a list of files/folders, grabs files inside them. Does not recurse
    more than one level (if a folder is supplied, it will list files within)
    """
    allfiles = []
    for cfile in args:
        if os.path.isdir(cfile):
            for sf in os.listdir(cfile):
                newpath = os.path.join(cfile, sf)
                if os.path.isfile(newpath):
                    allfiles.append(newpath)
                #end if isfile
            #end for sf
        elif os.path.isfile(cfile):
            allfiles.append(cfile)
        #end if isdir
    #end for cfile
    return allfiles
#end findFiles

def processNames(names, verbose=False):
    """
    Takes list of names, runs them though the tv_regex['with_ep_name'] regexs
    """
    allEps = []
    for f in names:
        filepath, filename = os.path.split( f )
        filename, ext = os.path.splitext( filename )
        
        # Remove leading . from extension
        ext = ext.replace(".", "", 1)
        
        for r in tv_regex['with_ep_name']:
            match = r.match(filename)
            if match:
                showname, seasno, epno, epname = match.groups()
                
                #remove ._- characters from name (- removed only if next to end of line)
                showname = re.sub("[\._]|\-(?=$)", " ", showname).strip()
                
                seasno, epno = int(seasno), int(epno)
                
                if verbose:
                    print "*"*20
                    print "File:", filename
                    print "Pattern:", r.pattern
                    print "Showname:", showname
                    print "Seas:", seasno
                    print "Ep:", epno
                    print "*"*20
                
                allEps.append({ 'file_showname':showname,
                                'seasno':seasno,
                                'epno':epno,
                                'filepath':filepath,
                                'filename':filename,
                                'ext':ext
                             })
                break # Matched - to the next file!
        else:
            print "Invalid name: %s" % (f)
        #end for r
    #end for f
    
    return allEps
#end processNames

def confirm(question="Rename files?"):
    ans = None
    while ans not in ["q", "quit"]:
        print "y/n/a/q?",
        ans = raw_input()
        if ans.lower() in ["y", "yes"]:
            return True
        elif ans.lower() in ["n", "no"]:
            return False
        elif ans.lower() in ["a", "always"]:
            return "always"
    else:
        sys.exit(1)
#end confirm

def make_path(path):
    try:
        os.makedirs(path)
    except OSError:
        #print "Couldn't make path"
	pass
#end make_path

def does_file_exist(path):
    try:
        os.stat(path)
    except OSError:
        file_exists = False
    else:
        file_exists = True
    return file_exists
    
def same_partition(f1, f2):
    return os.stat(f1).st_dev == os.stat(f2).st_dev

###########################


def main():
    parser = OptionParser(usage="%prog [options] <file or directories>")
    parser.add_option("-a", "--always", dest = "always",
        action="store_true", default = False, 
        help="Do not ask for confirmation before copying")
    
    opts, args = parser.parse_args()
    
    files = findFiles(args)
    files = processNames(files)

    # Warn if no files are found, then exit
    if len(files) == 0:
        print 'No files found'
        sys.exit(0)

    for name in files:
        oldfile = os.path.join(name['filepath'], name['filename']) + "." + name['ext']
        newpath = config['target_path'] % name
        newfile = os.path.join(newpath, name['filename']) + "." + name['ext']
    
        print "Old path:", oldfile
        print "New path:", newfile
        ans= "always"
        if ans == "always": opts.always = True
        
        if ans or opts.always:
            make_path(newpath)
            file_exists = does_file_exist(newfile)
            if file_exists:
                print "[!] File already exists, not copying"
            else:
                if same_partition(oldfile, newpath):
                    print "[*] Moving file"
                    try:
                        os.rename(oldfile, newfile)
                    except Exception, errormsg:
                        print "[!] Error moving file! %s" % (errormsg)
                else:
                    print "[*] Copying file"
                    try:
                        shutil.copy(oldfile, newfile)
                    except Exception, errormsg:
                        print "[!] Error copying file! %s" % (errormsg)
                    else:
                        print "[*] ..done"
        else:
            print "Skipping file"

if __name__ == '__main__':
    main()
