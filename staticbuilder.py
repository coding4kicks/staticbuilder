#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import types
import fnmatch
import hashlib
from optparse import OptionParser

import boto
from boto.s3.key import Key
from boto.s3.connection import Location

class StaticBuilder(object):
    """ Static Builder - "Mo' Static, Less Hassle"

        Uploads content to S3. Similar to unix cp.
        Can operate recusively on directories.  
        Checks hash so as to only upload modified content.
        Import and use as an object or run from the command line.
        Plenty of options to manage your static content.
        Only dependency is boto - https://github.com/boto/boto
    """

    def __init__(self, options):
        """ Validate AWS credentials, Set config/ignore info """

        self.ignorefiles = [] # files to ignore
        # Load Configurations from environment and .gitignore
        # TODO: set location from bashrc
        # set ignore patterns TODO - set global
        # TODO: set .ignore based upon in path.
        gitignore_file = os.path.join(os.getcwd(), ".gitignore")
        addIgnoreFile(self, gitignore_file)
        gitignore_file = os.path.join(os.getcwd(), ".git/info/exclude")
        addIgnoreFile(self, gitignore_file)
        gitignore_file = "~/.gitignore_global"
        addIgnoreFile(self, gitignore_file)
        # Check folder above for case of no input
        gitignore_file = os.path.join(os.getcwd(), "..")
        gitignore_file = os.path.join(gitignore_file, ".gitignore")
        addIgnoreFile(self, gitignore_file)
        gitignore_file = os.path.join(os.getcwd(), "..")
        gitignore_file = os.path.join(gitignore_file, ".git/info/exclude")


        # Set location variable from environment or options
        self.location = "DEFAULT"
        self.location = os.environ['S3_LOCATION']
        if options.location:
            self.location = options.location
        # Check location exists else error
        if not self.location in dir(Location):
            print "Specified location is invalid."
            sys.exit(2)

        # Check AWS credentials - should be saved in .bashrc or elsewhere
        connection = boto.connect_s3()
        try:
            buckets = connection.get_all_buckets()
        except:
            print ('Invalid login credentials, must set in .bashrc')
            sys.exit(2)

    def upload(self, paths_in=None, path_out=None, options=None):
        """ Upload files to S3 """

        files = []          # file name to save to AWS
        path_in_dic = {}        # local path to file
        key_name = ""       # Extra key info to add to each file
        bucket_name = None  # Bucket to save files to

        # If paths_in = None => paths_in = cwd
        if not paths_in:
            paths_in = []
            paths_in.append(os.getcwd())
            head, path_out = os.path.split(paths_in[0])

        # Else check that the paths_in exist.
        else:
            if not type(paths_in) == types.ListType:
                paths_in = [paths_in]
            for path in paths_in:
                if not os.path.exists(path):
                    print ("error: local path doesn't exist: " + path)

        # Connect to S3 and get the buckets
        connection = boto.connect_s3()
        buckets = connection.get_all_buckets()

        # If path_out exists check it for a bucket name
        if path_out:
            normal_path = os.path.normpath(path_out)
            bucketname, d, key_name = normal_path.partition("/")
            for bucket in buckets:
                if bucket.name == bucketname:
                    bucket_name = bucketname
            if not bucket_name: # Ask to create (name = start of path)
                print "Specified path out doesn't contain a bucket name"
                create = raw_input('Would you like to create a bucket named "' + 
                                    bucketname + '" [y/n]: ')
                if not create == 'y' or create == 'yes':
                    print "No buckets to create, terminating."
                    sys.exit(0)
                else:
                    bucket_name = bucketname
                    connection.create_bucket(bucket_name, location=self.location)

        # Upload each path in paths_in
        for path in paths_in:

            # If no path_out check paths_in parts for a bucket name
            if not path_out: 
                files.append("") # Create an empty first file to add parts to
                local_bucket_path = "" # Create local bucket path to find .gitignore
                # Split apart paths_in and check-for/set bucket name
                normal_path = os.path.normpath(paths_in[0]) # only 1 path
                path_parts = normal_path.split("/")
                for path_part in path_parts:
                    if bucket_name == None:
                        for bucket in buckets:
                            if path_part == bucket.name:
                                bucket_name = bucket.name
                        if bucket_name == None:
                            local_bucket_path = os.path.join(local_bucket_path, path_part)
                    else: # Once found bucket name, remaining parts are the key
                        files[0] = os.path.join(files[0], path_part)
                path_in_dic[files[0]] = path # Set path_in to local file
                
                # if bucket_name exists, try to add gitignore files
                if bucket_name:
                    gitignore_file = os.path.join(local_bucket_path, ".gitignore")
                    addIgnoreFile(self, gitignore_file)
                    gitignore_file = os.path.join(local_bucket_path, bucket_name)
                    gitignore_file = os.path.join(gitignore_file, ".gitignore")
                    addIgnoreFile(self, gitignore_file)
                else:
                    if os.path.isfile(path): # error if file
                        print "Must give a bucket name with a file"
                        sys.exit(1)
                    else: # Ask to create bucket (name = directory)
                        bucket_name = path_parts[len(path_parts)-1]
                        create = raw_input('Would you like to create a bucket named "' + 
                                            bucket_name + '" [y/n]: ')
                        if not create == 'y' or create == 'yes' or create == 'Y':
                            print "No buckets to create, terminating."
                            sys.exit(1)
                        else:
                            try:
                                connection.create_bucket(
                                    bucket_name, location=self.location)
                            except e:
                                print "Unable to create bucket"
                                sys.exit(2)
                break # Only 1 path_in when no path_out, so break out of for loop
           
            # Pull apart the path_in
            # file          => head=None       ; tail=file
            # path/in/file  => head=path/in/   ; tail=file
            # path/in       => head=path/      ; tail=in (dir)
            # path/in/      => head=path/in/   ; tail=None
            # never a slash in tail: empty if path ends in /
            head, tail = os.path.split(path)
            
            # if tail is empty then path is a directory 
            # so remove / and split again
            if tail == "":
                path = path.rstrip('/')
                head, tail = os.path.split(path)

            # if tail == file add to files
            if os.path.isfile(path):
                files.append(tail)
                path_in_dic[tail] = path 

            # else tail == directory so add files in folder (maybe recursively)
            else:
                temp_files = fileList(path, folders=options.recursive)
                for file in temp_files:
                    temp_path_in = file
                    file = file.replace(path + "/", "")
                    path_in_dic[file] = temp_path_in
                    files.append(file)

        # Upload all the files
        bucket = connection.get_bucket(bucket_name)
        for file in files:
            key = os.path.join(key_name, file)

            # Skip if type of file to ignore
            # TODO - MOVE THIS VALIDATION EARLIER SO DON'T READ UNECESSARILY
            ignore = False
            for exp in self.ignorefiles:
                if fnmatch.fnmatch(file, exp):
                    ignore = True
                    continue
            if ignore:
                continue

            # Add the key to the bucket
            file_name = path_in_dic[file]
            if os.path.isfile(file_name):
                hash_local = getHash(file_name)
                k = bucket.get_key(key)
                uploadRequired = True
                if k:
                    hash_remote = k.get_metadata('hash')
                    if hash_remote == hash_local:
                        uploadRequired = False
                        print "No upload"
                    else:
                        k.set_metadata('hash', hash_local)
                else:
                    k = Key(bucket)
                    k.key = key
                    k.set_metadata('hash', hash_local)
                
                if uploadRequired:
                    print "added files: " + file
                    k.set_contents_from_filename(file_name)
            else:
                k = Key(bucket)
                k.key = key

# TODO: make helper functions module private
def addIgnoreFile(self, gitignore_file):
    """ Uploads a gitignore file's contents to the ignore list """
    print gitignore_file
    if os.path.exists(gitignore_file):
        print "here mothafucker"
        with open(gitignore_file, 'r') as f:
            for line in f:
                if line[0] == ';' or line[0] == '#' or line[0] == '!':
                    continue
                else:
                    self.ignorefiles.append(line.strip())

def getHash(filePath):
    """md5 hash of file"""
    file = open(filePath, 'rb')
    m = hashlib.md5()
    while True:
        data = file.read(8192)
        if not data:
            break
        m.update(data)
    return m.hexdigest()


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
            print "I should never ever see you around here! Please..."
            files = map(lambda x: x[len(path)+1:], files)

    return files

def listBuckets():
    """ List all buckets for an aws account """
    connection = boto.connect_s3()
    buckets = connection.get_all_buckets()
    print "S-3 Buckets:"
    for bucket in buckets:
      print bucket

def listKeys(path):
    """ List keys based upon a path 
        The input path must start with a bucket name
        If only a bucket name then prints all keys
        If directory after bucket name, prints only keys in directory
    """
    connection = boto.connect_s3()
    buckets = connection.get_all_buckets()
    normal_path = os.path.normpath(path)
    bucket_name, d, dir_name = normal_path.partition("/")

    # Get the bucket or exit if it doesn't exist
    no_bucket = True
    for bucket in buckets:
        if bucket_name == bucket.name:
            bucket = connection.get_bucket(bucket_name)
            no_bucket = False
            break
    if no_bucket:
        print "Must specify bucket name in path"
        sys.exit(2)

    # Get the keys and print if not filtered
    keys = bucket.list()
    print "Keys in bucket: " + bucket_name
    print "Filtered by: " + (dir_name or "nothing")
    for key in keys:
        if dir_name == "":
            print key
        else:
            if dir_name in key.name:
                 print key

def main():
    # Parse command line options and arguments.
    usage = "usage: %prog [options] [paths_in] [bucket/path_out]"
    parser = OptionParser(usage)
    parser.add_option("-r", "-R", "--recursive", action="store_true",
                      dest="recursive", default=False,
                      help="Copy directory recursively [default: %default]")
    parser.add_option("-l", "-L", "--list", action="store",
                      dest="list", default="", help="List 'buckets' or key path")
    parser.add_option("-p", "-P", "--place", action="store",
                      dest="location", default="", help="Specify bucket location")

    (options, args) = parser.parse_args()

    paths_in = []
  
    # handle option for listing buckets and keys
    if options.list:
        if options.list == "buckets":
            # list buckets
            listBuckets()
        else:
            # list keys in path
            listKeys(options.list)
        sys.exit(0)
           
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
        head, path_out = os.path.split(paths_in[0])
        print head
        print "path out: " + path_out

    # Else check that the paths_in exist.
    else:
        for path in paths_in:
            if not os.path.exists(path):
                parser.error("local path doesn't exist: " + path)

    # paths_in exists so create and run builder
    sb = StaticBuilder(options)
    sb.upload(paths_in, path_out, options)

if __name__ == "__main__":
    sys.exit(main())
