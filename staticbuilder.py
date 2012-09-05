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
    """ Static Builder - "Mo' Static, Less Hassle"

        Uploads contents to S3. Similar to unix cp.
        Can operate recusively on directories.  
        Checks hash so as to only upload modified content.
        Import and use as an object or run from the command line.
        Plenty of options to manage your static content.
        Only dependency is boto - https://github.com/boto/boto
    """

    def __init__(self, paths_in=None, path_out=None, options=None):
        """ Validate paths_in, path_out, and AWS credentials, and set config/ignore 
            TODO: only check aws credentials and load config/ingore info in _init_
            paths_in is either a single file or directory,
            or a lists of files and directories
            if path_out is not specified, a bucket name must exist in path in.
        """

        self.paths_in = paths_in
        self.path_out = path_out
        self.options = options

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

        # Check if path_in equals None, yes => paths_in = cwd
        if not self.paths_in:
            self.paths_in.append(os.getcwd())
            #self.is_dir = True

        # Else check that the paths_in exist.
        else:
            if not type(self.paths_in) == types.ListType:
                self.paths_in = [self.paths_in]
            for path in self.paths_in:
                if not os.path.exists(path):
                    print ("error: local path doesn't exist: " + path)
        
        # Check AWS credentials - should be saved in .bashrc or other environment
        connection = boto.connect_s3()
        try:
            buckets = connection.get_all_buckets()
        except:
            print ('Invalid login credentials, must set in .bashrc')
            sys.exit(2)

    def upload(self):
        """ Upload files to S3 """

        files = []          # file name to save to AWS
        path_in = {}        # local path to file
        key_name = ""       # Extra key info to add to each file
        bucket_name = None  # Bucket to save files to

        # Connect to S3 and get the buckets
        connection = boto.connect_s3()
        buckets = connection.get_all_buckets()

        # If path_out exists check it for a bucket name
        if self.path_out:
            normal_path = os.path.normpath(self.path_out)
            bucketname, d, key_name = normal_path.partition("/")
            for bucket in buckets:
                if bucket.name == bucketname:
                    bucket_name = bucketname

            # If no bucket, ask if wish to create with first path part
            if not bucket_name:
                print "Specified path out doesn't contain a bucket name"
                create = raw_input('Would you like to create a bucket named "' + 
                                    bucketname + '" [y/n]: ')
                if not create == 'y' or create == 'yes':
                    print "No buckets to create, terminating."
                    sys.exit(0)
                else:
                    bucket_name = bucketname
                    connection.create_bucket(bucket_name)

        # Upload each path_in
        for path in self.paths_in:

            # If no there path_out check path_in parts for a bucket name
            if not self.path_out:
                
                # Create an empty first file to add parts to
                files.append("")

                # Split apart path_in and check-for/set bucket name
                normal_path = os.path.normpath(self.paths_in[0])
                path_parts = normal_path.split("/")
                for path_part in path_parts:
                    if bucket_name == None:
                        for bucket in buckets:
                            if path_part == bucket.name:
                                bucket_name = bucket.name
                    else:
                        # Once found bucket name, remaining parts of path are are the key
                        files[0] = os.path.join(files[0], path_part)
            
                # Set path to local file
                path_in[files[0]] = path

                # If still no bucket name, then error if it's a file, 
                # otherwise ask if they wish to create a bucket with the
                # same name as the directory
                if not bucket_name:
                    if os.path.isfile(path):
                        print "Must give a bucket name with a file"
                        sys.exit(1)
                    else:
                        create = raw_input('Would you like to create a bucket named "' + 
                                            tail + '" [y/n]: ')
                        if not create == 'y' or create == 'yes':
                            print "No buckets to create, terminating."
                            sys.exit(1)
                        else:
                            bucket_name = tail
                            connection.create_bucket(bucket_name)
                
                # Since there is no path_out there must
                # be only 1 path_in so break out of for loop
                break

            # Pull apart the path_in
            # file          => head=None , tail=file
            # path/in/file  => head=path/in/ , tail=file
            # path/in       => head=path/ , tail=in (dir)
            # path/in/      => head=path/in/ , tail=None
            # never a slash in tail: empty if path ends in /
            head, tail = os.path.split(path)
 
            # if tail is empty then path is a directory 
            # so remove / and split again
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
                    temp_path_in = file
                    file = file.replace(head + "/", "")
                    #file = os.path.join(head, file)
                    print file
                    print path
                    print head
                    print tail
                    path_in[file] = temp_path_in
                    files.append(file)
            
        print files
        print path_in

        cwd = os.getcwd()

        print 'Adding to bucket: ' + bucket_name
        bucket = connection.get_bucket(bucket_name)

        # Upload all the files
        for file in files:
            key = os.path.join(key_name, file)

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

# TODO: make helper functions module private
def fileList(paths, relative=False, folders=False):
    """ Generate a recursive list of files from a given path. """

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

        # TODO - remove or use?
        if relative:
             files = map(lambda x: x[len(path)+1:], files)

    return files

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
