#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import types
import fnmatch
from optparse import OptionParser

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

        Only dependency is boto
        https://github.com/boto/boto
    """


    def __init__(self, paths_in=None, path_out=None, options=None):
        """ Validate paths_in, path_out, and AWS credentials, and set config/ignore 
        
            paths_in is either a single file or directory, or a lists of files and directories
            if path_out is not specified, a bucket name must exist in path in.
        """

        self.paths_in = paths_in
        self.path_out = path_out
        self.options = options
        self.is_dir = False # remove
        self.bucket_name = None
        self.key_name = ""

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

        # Check if path_in equals None, yes => paths_in = cwd
        if not self.paths_in:
            self.paths_in.append(os.getcwd())
            self.is_dir = True

        # Else check that the paths_in exist.
        else:
            if not type(self.paths_in) == types.ListType:
                self.paths_in = [self.paths_in]
            for path in self.paths_in:
                if not os.path.exists(path):
                    print ("error: local path doesn't exist: " + path)

        # Check if path_in is a directory
        #elif os.path.isdir(path_in):
        #    self.is_dir = True

        # Check if path_in is a file
        #elif os.path.isfile(path_in):
        #    self.is_dir = False

        # How did you get here?
        #else:
        #    print 'How did you get here?'

        # pull apart path_in
        head, tail = os.path.split(self.paths_in[0])

        # If head none add current working directory
        if not head:
            self.paths_in[0] = os.path.join(os.getcwd(), tail)
            head, tail = os.path.split(self.paths_in[0])
        
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
            normal_path = os.path.normpath(self.paths_in[0])

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
        else:

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

        # if path_out is None, key should be empty
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

        # Connect to S3 and create the bucket
        connection = boto.connect_s3()
        bucket = connection.get_bucket(self.bucket_name)
        buckets = connection.get_all_buckets()

        files = []
        path_in = {}
        for path in self.paths_in:

            # If no path_out then only one path in, so check path_in parts for a bucket name
            if not self.path_out:
                self.key_name = ""
                self.bucket_name = None
                files.append("")
                connection = boto.connect_s3()

                # Normalize path_in
                normal_path = os.path.normpath(self.paths_in[0])

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
                        files[0] = os.path.join(files[0], path_part)
            
                path_in[files[0]] = path
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
                
                break

            # file          => head=None , tail=file
            # path/in/file  => head=path/in/ , tail=file
            # path/in       => head=path/ , tail=in (dir)
            # path/in/      => head=path/in/ , tail=None
            # never a slash in tail: empty if path ends in /
            head, tail = os.path.split(path)
 
            # if no path out, then only one path in

            # if tail is empty then path is a directory so remove / and split again
            if tail == "":
                path = path.rstrip('/')
                head, tail = os.path.split(path)

            # if tail == file
            if os.path.isfile(path):
                files.append(tail)
                path_in[tail] = path  
            # else tail == directory
            else:
                temp_files = fileList(path, folders=self.options.recursive)
                for file in temp_files:
                    path_in[file] = os.path.join(path, file)
                    files.append(file)
            
        print files
        print path_in
        # If paths_in is a directory, scan recursively
        #if self.is_dir:
        #    files = fileList(self.paths_in, folders=self.options.recursive)

        #    # remove initial path and save to self.files
        #    for file in files:
        #        print file
        #        #print self.paths_in
        #        file = file.replace( self.paths_in[0] + '/', '')
        #        self.files.append(file)
        
        # Else it's a file so add key to files and erase
        #elif self.files == []:
        #    self.files.append(self.key_name)
        #    self.path_in = self.paths_in[0].replace(self.key_name, "")
        #    self.key_name = ""

        #else: 
        #    print "You shouldn't be here dude!"

        cwd = os.getcwd()

        print 'Adding to bucket: ' + self.bucket_name
        bucket = connection.get_bucket(self.bucket_name)

        for file in files:
            key = os.path.join(self.key_name, file)

            print "key: " + key
            
            # Skip if type of file to ignore
            # TODO - MOVE THIS VALIDATION EARLIER
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

            file_name = path_in[file]

            print "File name at start: " + file_name
            #print "Path in: " + self.path_in
            #print "Bucket name: " + self.bucket_name
            #if not self.bucket_name in file_name:
            #    file_name = os.path.join(cwd, self.bucket_name)
            #file_name = os.path.join(file_name, file)
            #print "File name at end: " + file_name
            if os.path.isfile(file_name):
                print "added as file"
                k.set_contents_from_filename(file_name)
                print "finished"

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
        if os.path.isdir(path):
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
        else:
            files.append(path)

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

    # Parse command line options and arguments.
    usage = "usage: %prog [options] [paths_in] [bucket/path_out]"
    parser = OptionParser(usage)
    parser.add_option("-r", "-R", "--recursive", action="store_true",
                      dest="recursive", default=False,
                      help="Copy directory recursively [default: %default]")
    (options, args) = parser.parse_args()

    paths_in = []

    # Check and set arguments.
    if len(args) > 2:
        for arg in args:
            paths_in.append(arg)
        path_out = paths_in.pop() # last item is path_out
    else:
        paths_in.append(args[0]) if len(args) > 0 else None
        path_out = args[1] if len(args) == 2 else None

    # If no paths_in, set current working directory as the paths_in.
    if not paths_in:
        paths_in.append(os.getcwd())

    # Else check that the paths_in exist.
    else:
        for path in paths_in:
            if not os.path.exists(path):
                parser.error("local path doesn't exist: " + path)

    # paths_in exists so create and run builder
    sb = StaticBuilder(paths_in, path_out, options)
    sb.upload()

if __name__ == "__main__":
    sys.exit(main())
