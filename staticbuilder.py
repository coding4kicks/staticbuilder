#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import types
import fnmatch

import boto
from boto.s3.key import Key

class StaticBuilder(object):
    """ Static Builder
        Mo' Static, Less Hassle

        Input - Local path to directory or file, 
                Output bucket name or path,
                Website true/public or false
                (All inputs are optional)
        Uploads contents to S3.  Operates recusively on directories.  
        Checks hash so as to only upload modified content.
        Import and use as an object or run from the command line.
        KISS - keep it simple stupid.

        Only dependency is boto
        https://github.com/boto/boto

        Credits to Koen Bok - a few snippets were taken from cactus
        https://github.com/koenbok/Cactus/tree/master/cactus
    """


    def __init__(self, path_in, path_out, website=False):
        """ Validate path_in, path_out, and AWS credentials """

        self.path_in = path_in
        self.path_out = path_out
        self.website = website
        self.is_dir = True
        self.bucket_name = None
        self.key_name = ""
        self.files = []
        self.paths = {}

        # NEED TO REFACTOR TO CONFIG DICTIONARY
        # set ignore patterns
        self.ignorefiles = []
        gitignore_file = os.path.join(os.getcwd(), ".gitignore")
        if os.path.exists(gitignore_file):
            with open(gitignore_file, 'r') as f:
                for line in f:
                    if line[0] == ';' or line[0] == '#' or line[0] == '!':
                        continue
                    else:
                        self.ignorefiles.append(line.strip())

        #
        #   Validate and set path_in
        #

        # Check if path_in equals None, yes => path_in = cwd
        if not path_in:
            path_in = os.getcwd()
            self.is_dir = True

        # Check if path_in exists
        elif not os.path.exists(path_in):
            print "Local path doesn't exist"
            help()
            sys.exit()

        # Check if path_in is a directory
        elif os.path.isdir(path_in):
            self.is_dir = True

        # Check if path_in is a file
        elif os.path.isfile(path_in):
            self.is_dir = False

        # How did you get here?
        else:
            print 'How did you get here?'

        # pull apart path_in
        head, tail = os.path.split(path_in)

        # If head none add current working directory
        if not head:
            self.path_in = os.path.join(os.getcwd(), tail)
            head, tail = os.path.split(self.path_in)
        
        #self.bucket_name = tail
        #print "Head: " + head
        #print "Tail: " + tail
        #print "Full path name: " + self.path_in
        #print "Is directory:" + str(self.is_dir)

        #
        #   Validate and set AWS credentials
        #

        # Check credentials - should be saved in .bashrc or other environment
        connection = boto.connect_s3()
        
	# Exit if the AWS information was not correct
        try:
            buckets = connection.get_all_buckets()
        except:
            print ('Invalid login credentials, must set in .bashrc')
            sys.exit()

        #
        #   Validate and set path_out / bucket name
        #

        # If no path_out, check path_in parts for a bucket name
        if not self.path_out:

            # Normalize path_in
            normal_path = os.path.normpath(self.path_in)

            # Split path_in check for bucket name
            path_parts = normal_path.split("/")
            #print path_parts
            for path_part in path_parts:
                #print path_part

                if self.bucket_name == None:
                    for bucket in buckets:
                        #print bucket.name
                        if path_part == bucket.name:
                            self.bucket_name = bucket.name
                else:
                    # Once found bucket name, remaining parts of path are are the key
                    self.key_name = os.path.join(self.key_name, path_part)
            
            # If still no bucket name, then error if file, else ask to create
            if not self.bucket_name:
                if not self.is_dir:
                    print "Must give a bucket name with a file"
                    help()
                    sys.exit()
                else:
                    create = raw_input('Would you like to create a bucket named "' + tail + '" [y/n]: ')
                    if not create == 'y' or create == 'yes':
                        print "No buckets to create, terminating."
                        help()
                        sys.exit()
                    else:
                        self.bucket_name = tail
                        connection.create_bucket(self.bucket_name)

        # If path_out check that it contains a bucket name
        if path_out:

            # Set key name to tail of path in
            #self.key_name = tail

            # Normalize path and pull apart
            normal_path = os.path.normpath(self.path_out)
            bucketname, d, self.key_name = normal_path.partition("/")
            for bucket in buckets:
                if bucket.name == bucketname:
                    self.bucket_name = bucketname

            if not self.bucket_name:
                print "Specified path out doesn't contain a bucket name"
                create = raw_input('Would you like to create a bucket named "' + bucketname + '" [y/n]: ')
                if not create == 'y' or create == 'yes':
                    print "No buckets to create, terminating."
                    help()
                    sys.exit()
                else:
                    self.bucket_name = bucketname
                    connection.create_bucket(self.bucket_name)

            # If no bucket name in path out ask if want to create bucket named tail

        #print "Bucket name: " + self.bucket_name
        #print "Key name: " + self.key_name        
        #print buckets
        #print path_in
        #print path_out

        #self.paths = {
        #    'config': os.path.join(path, '.config'),
        #    'script': os.path.join(os.getcwd(), __file__)
        #}

        #self.config = config(self.paths['config'])

    def upload(self):
        """ Upload files to S3 """

        # Double check bucket name exists
        if not self.bucket_name:
             print 'Error, bucket name should exists'
             help()
             sys.exit()

        # If path_in is a directory, scan recursively
        if self.is_dir:
            files = fileList(self.path_in, folders=True)

            # remove initial path and save to self.files
            for file in files:
                print file
                print self.path_in
                file = file.replace( self.path_in + '/', '')
                self.files.append(file)
        
        # Else it's a file so add key to files and erase
        elif self.files == []:
            self.files.append(self.key_name)
            self.path_in = self.path_in.replace(self.key_name, "")
            self.key_name = ""

        else: 
            print "You shouldn't be here dude!"

        # Connect to S3 and create the bucket
        connection = boto.connect_s3()
        cwd = os.getcwd()
        bucket = connection.get_bucket(self.bucket_name)

        print 'Adding to bucket: ' + self.bucket_name
        for file in self.files:
            key = os.path.join(self.key_name, file)

            print "key: " + key
            
            # Ignore file expressions
            ignore = False
            for exp in self.ignorefiles:
                if fnmatch.fnmatch(file, exp):
                    ignore = True
                    continue
            if ignore:
                continue

            print "added key"
            # Add the key to the bucket
            k = Key(bucket)
            k.key = key
            # if is a file, set content
            #file_name = cwd

            file_name = self.path_in

            #print "File name at start: " + file_name
            #print "Path in: " + self.path_in
            #print "Bucket name: " + self.bucket_name
            #if not self.bucket_name in file_name:
            #    file_name = os.path.join(cwd, self.bucket_name)
            file_name = os.path.join(file_name, file)
            #print "File name at end: " + file_name
            if os.path.isfile(file_name):
                print "added as file"
                k.set_contents_from_filename(file_name)

        # Else uploading a single file so just add key name
        #else:
        #    head, tail = os.path.split(self.path_in)
        #    self.files.append(tail)

def fileList(paths, relative=False, folders=False):
    """
        Generate a recursive list of files from a given path.
    """

    if not type(paths) == types.ListType:
        paths = [paths]

    files = []

    for path in paths:  
        for fileName in os.listdir(path):

            # Ignore hidden files
            if fileName.startswith('.'):
                continue

            filePath = os.path.join(path, fileName)
            
            if os.path.isdir(filePath):
                if folders:
                    files.append(filePath)
                    files += fileList(filePath, folders=folders)
            else:
                files.append(filePath)

        if relative:
             files = map(lambda x: x[len(path)+1:], files)

    return files

# TODO: make helper functions module private
def help():
    print
    print 'Usage: staticbuilder [path_in] [path_out] [website boolean]'
    print
    print ' path_in: Directory or file location to upload to S3'
    print '     (Defaults to current working directory.'
    print '      Directories upload recuresively)'
    print ' path_out: Optional name of S3 bucket path.'
    print '     (Defaults to dicrectory or file name in path'
    print ' website: If true saves directory as public website'
    print 

def exit(msg):
    print msg
    sys.exit(1)

def main():

    # Three arguments: path, bucket_name, and website boolean
    path_in = sys.argv[1] if len(sys.argv) > 1 else None
    path_out = sys.argv[2] if len(sys.argv) > 2 else None
    website = sys.argv[3] if len(sys.argv) > 3 else None
    
    # If no path set current working directory as the path
    if not path_in:
        path_in = os.getcwd()
        
    # Check if path is for help
    elif path_in == "-help" or path_in == "--help" or path_in == "help":
        print "Requesting help"
        help()
        sys.exit(2)

    # Check if path exists
    elif not os.path.exists(path_in):
        print "Local path doesn't exist"
        help()
        sys.exit(1)

    # Make sure website is boolean
    if not (website == None or website == True or website == False):
        print "Website is a boolean"
        help()
        sys.exit(3)

    # path_in exists so create and run builder
    sb = StaticBuilder(path_in, path_out, website)
    sb.upload()

if __name__ == "__main__":
    sys.exit(main())
