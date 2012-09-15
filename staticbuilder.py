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

# STATIC BUILDER
class StaticBuilder(object):
    """ Static Builder - "Mo' Static, Less Hassle"

        Uploads content to S3. Similar to unix cp.
        Can operate recusively on directories.  
        Checks hash so as to only upload modified content.
        Import to use as an object or run from the command line.
        Plenty of options to help manage your static content.
        Only dependency is boto - https://github.com/boto/boto
        Warning - dir or directory name variables are really filters on S3.
    """

    # CONSTRUCTOR
    def __init__(self, options):
        """ Constructor validate AWS credentials, Set config/ignore info """

        self.ignorefiles = []     # File types to ignore
        gitignore_files = []      # Possible paths to .gitignore files
        
        # Check cwd and parent directory for .gitignore and .git/info/exclude
        gitignore_files.append(os.path.join(os.getcwd(), ".gitignore"))
        gitignore_files.append(os.path.join(os.getcwd(), ".git/info/exclude"))
        parent_directory = os.path.join(os.getcwd(), "..")
        gitignore_files.append(os.path.join(parent_directory, ".gitignore"))
        gitignore_files.append(os.path.join(parent_directory, ".git/info/exclude"))

        # Check user home for global .gitignore 
        gitignore_files.append("~/.gitignore_global")

        # Add all ignore file types
        for file in gitignore_files:
            _addIgnoreFile(self, file)

        # Set location variable from environment or options
        self.location = "DEFAULT"
        self.location = os.environ['S3_LOCATION']
        if options.location:
            self.location = options.location

        # Check that location exists otherwise error
        if not self.location in dir(Location):
            print "Specified location is invalid."
            sys.exit(2)

        # Check AWS credentials - should be saved in environment (i.e. .bashrc)
        connection = boto.connect_s3()
        try:
            buckets = connection.get_all_buckets()
        except:
            print ('Invalid login credentials, must set in .bashrc')
            sys.exit(2)

    # LIST BUCKETS option
    def listBuckets(self):
        """ List all buckets for an AWS account """
        connection = boto.connect_s3()
        buckets = connection.get_all_buckets()
        print "S-3 Buckets:"
        for bucket in buckets:
            print bucket

    # LIST KEYS option
    def listKeys(self, path):
        """ List keys based upon a path 
            The input path must start with a bucket name
            If only a bucket name then prints all keys
            If a directory is after the bucket name, print only the keys in that directory
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
            print "Must specify bucket name in path to list."
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
    
    # DELETE option 
    def delete(self, options):
        """ Delete a file or directory, options force and recursive. 
            If no -r, assumption is a file
            If -r assumption is a directory
            Prompt for both if no -r
        """
        connection = boto.connect_s3()
        buckets = connection.get_all_buckets()
        normal_path = os.path.normpath(options.delete)
        bucket_name, d, dir_name = normal_path.partition("/")

        # Get the bucket or exit if it doesn't exist
        no_bucket = True
        for bucket in buckets:
            if bucket_name == bucket.name:
                bucket = connection.get_bucket(bucket_name)
                no_bucket = False
                break
        if no_bucket:
            print "Must specify bucket name in path to delete."
            sys.exit(2)

        if options.force:
            confirmation = "y"
        else:
            confirmation = raw_input("Confirm you want to delete " + options.delete + " [y/n]:")
        if not confirmation.lower() == "y" and not confirmation.lower() == "yes":
            print "Canceling deletion."
            sys.exit(0)

        # Delete a file (one key) if not recursive
        if not options.recursive:
            print "Deleting: " + options.delete
            k = Key(bucket)
            k.key = options.delete
            bucket.delete_key(k)
        else: # Delete a whole director (by filter)
            keys = bucket.list()
            for key in keys:
                # TODO: may be redundant w/ line 120
                bucket_name, d, delete_filter = options.delete.partition("/")
                if delete_filter in key.name:
                    print "Deleting: " + key.name
                    bucket.delete_key(key)

    # WEBSITE option
    def website(self, options):
        """ Make a bucket a public website - name must conform to DNS """
        connection = boto.connect_s3()
        buckets = connection.get_all_buckets()
        #make sure bucket exists
        no_bucket = True
        for bucket in buckets:
            if options.website == bucket.name:
                bucket = connection.get_bucket(options.website)
                no_bucket = False
                break
        if no_bucket:
            print "Must specify bucket name to make public."
            sys.exit(2)
        # Set entire bucket policy
        bucket.set_acl('public-read')
        bucket.configure_website('index.html', 'error.html')
        print bucket.get_website_configuration()
    
    # UPLOAD
    def upload(self, paths_in=None, path_out=None, options=None):
        """ Upload files to S3 """

        files = []          # file name to save to AWS
        path_in_dic = {}    # local path to file
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
                    print ("error: Local path doesn't exist: " + path)

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
                else: # A random retard says, "hello"
                    bucket_name = bucketname
                    connection.create_bucket(bucket_name, location=self.location)

        # Upload each path in paths_in
        for path in paths_in:

            # If no path_out check paths_in parts for a bucket name
            if not path_out: 

                files.append("")        # Create an empty first file to add parts to
                local_bucket_path = ""  # Create local bucket path to find .gitignore
                
                # Split apart paths_in and check-for/set bucket name
                normal_path = os.path.normpath(paths_in[0]) # only 1 path since no path_out
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

                # If no bucket, ask to create if directory otherwise error
                if not bucket_name:
                    if os.path.isfile(path): # Error if file
                        print "Must give a bucket name with a file"
                        sys.exit(1)
                    else: # Ask to create bucket (name = directory)
                        bucket_name = path_parts[len(path_parts)-1]
                        create = raw_input('Would you like to create a bucket named "' + 
                                            bucket_name + '" [y/n]: ')
                        if not create == 'y' or not create == 'yes' or not create == 'Y':
                            print "No buckets to create, terminating."
                            sys.exit(1)
                        else:
                            try:
                                connection.create_bucket(
                                    bucket_name, location=self.location)
                            except e:
                                print "Unable to create bucket"
                                sys.exit(2)

                # If bucket_name exists, try to add gitignore files
                gitignore_file = os.path.join(local_bucket_path, ".gitignore")
                _addIgnoreFile(self, gitignore_file)
                gitignore_file = os.path.join(local_bucket_path, bucket_name)
                gitignore_file = os.path.join(gitignore_file, ".gitignore")
                _addIgnoreFile(self, gitignore_file)

                # Add path to file
                if os.path.isfile(path):
                    path_in_dic[files[0]] = path

                # Read in files if path is a directory
                else:
                    temp_files = _fileList(path, folders=options.recursive)
                    for file in temp_files:
                        temp_path_in = file
                        file = file.replace(path + "/", "")
                        file = os.path.join(files[0], file)
                        path_in_dic[file] = temp_path_in
                        files.append(file)
                    #Pop to oblivion the first file since it is just the directory itself
                    files.pop(0)
                break # Only 1 path_in when no path_out, so break out of for loop
            
            # SPLIT PATH - pull apart the path_in, place in head and tail
            # file          => head=None       ; tail=file
            # path/in/file  => head=path/in/   ; tail=file
            # path/in       => head=path/      ; tail=in (dir)
            # path/in/      => head=path/in/   ; tail=None
            # never a slash in tail: empty if path ends in /
            head, tail = os.path.split(path)
            
            # If tail is empty then path is a directory 
            # so remove / and split again
            if tail == "":
                path = path.rstrip('/')
                head, tail = os.path.split(path)

            # If tail is a file add to files
            if os.path.isfile(path):
                files.append(tail)
                path_in_dic[tail] = path 

            # Else tail is a directory so add files in folder (maybe recursively)
            else:
                temp_files = _fileList(path, folders=options.recursive)
                for file in temp_files:
                    temp_path_in = file
                    file = file.replace(path + "/", "")
                    path_in_dic[file] = temp_path_in
                    files.append(file)
        # Upload all the files
        bucket = connection.get_bucket(bucket_name)
        for file in files:
            key = os.path.join(key_name, file)

            # If renaming the file swap in the new name
            if options.name:
                key, d, file_name = key.rpartition("/")
                key = os.path.join(key, options.name)

            # Skip if type of file we ignore (possibly do earlier)
            ignore = False
            for exp in self.ignorefiles:
                if fnmatch.fnmatch(file, exp):
                    ignore = True
                    continue
            if ignore:
                continue
            
            # Add the key with file info to the bucket
            file_name = path_in_dic[file]
            if os.path.isfile(file_name):
                hash_local = _getHash(file_name)
                k = bucket.get_key(key)
                uploadRequired = True
                if k: # Key already exists
                    hash_remote = k.get_metadata('hash')
                    if hash_remote == hash_local:
                        uploadRequired = False
                        print "No change: " + file
                        if options.name:
                            print "as " + options.name
                    else:
                        k.set_metadata('hash', hash_local)
                else: # Create the key on S3
                    k = Key(bucket)
                    k.key = key
                    k.set_metadata('hash', hash_local)
                # Upload only if different hash
                if uploadRequired or options.force:
                    print "Added files: " + file
                    if options.name:
                        print "as " + options.name
                    if options.metadata:
                        k.update_metadata(options.metadata)
                    k.set_contents_from_filename(file_name)
            else: # Key is directory so just add
                k = Key(bucket)
                k.key = key

# Zee Helper Functions...
def _addIgnoreFile(self, gitignore_file):
    """ Uploads a gitignore file's contents to the ignore list """
    if os.path.exists(gitignore_file):
        with open(gitignore_file, 'r') as f:
            for line in f:
                if line[0] == ';' or line[0] == '#' or line[0] == '!':
                    continue
                else:
                    self.ignorefiles.append(line.strip())

def _getHash(filePath):
    """md5 hash of file"""
    file = open(filePath, 'rb')
    m = hashlib.md5()
    while True:
        data = file.read(8192)
        if not data:
            break
        m.update(data)
    return m.hexdigest()

def _extract_meta(metadata):
    """ Convert metadata to Python dictionary """
    meta_dic = {}
    metas = metadata.split(";")  
    for meta in metas:
        key, d, value = meta.partition(":")
        meta_dic[key] = value
    return meta_dic

def _fileList(paths, folders=False):
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
                        files += _fileList(filePath, folders=folders)
                else:
                    files.append(filePath)
        else:
            files.append(path)
    return files

def main():
    """ Static Builder command line """

    # Parse command line options and arguments.
    usage = "usage: %prog [options] [paths_in] [bucket/path_out]"
    parser = OptionParser(usage)
    parser.add_option("-r", "-R", "--recursive", action="store_true",
                      dest="recursive", default=False,
                      help="Copy directory recursively [default: %default]")
    parser.add_option("-l", "-L", "--list", action="store",
                      dest="list", help="List 'buckets' or key path")
    parser.add_option("-p", "-P", "--location", action="store",
                      dest="location", help="Specify bucket location")
    parser.add_option("-n", "-N", "--name", action="store",
                      dest="name", help="Rename uploaded file")
    parser.add_option("-d", "-D", "--delete", action="store",
                      dest="delete", help="Delete a file or directory")
    parser.add_option("-f", "-F", "--force", action="store_true",
                      dest="force", default=False,
                      help="Force deletion or upload [default: %default]")
    parser.add_option("-w", "-W", "--website", action="store",
                      dest="website", help="Set all keys public for a website")
    parser.add_option("-m", "-M", "--metadata", action="store",
                      dest="metadata", help="Set meta data for path")
    (options, args) = parser.parse_args()

    sb = StaticBuilder(options) # Da Static Builder
    paths_in = []               # Files and Directories to load

    # Handle option for DELETIONS 
    # TODO- When complete put all option parts in alphabetical order:
    # both the parser.add (above), the if option. (below) and the Method Declarations
    if options.delete:
        sb.delete(options)
        sys.exit(0)
  
    # Handle option for LISTING buckets and keys
    if options.list:
        if options.list == "buckets":
            sb.listBuckets()
        else:
            sb.listKeys(options.list)
        sys.exit(0)
    
    # Handle option for setting public WEBSITE
    if options.website:
        sb.website(options)
        sys.exit(0)

    # Convert METADATA to a Python dictionary
    if options.metadata:
        options.metadata = _extract_meta(options.metadata)
        print options.metadata

    # Check and set arguments.
    if len(args) > 2:
        if options.name:
            parser.error("Can only change 1 file's name")
        for arg in args:
            paths_in.append(arg)
        path_out = paths_in.pop() # Last item is path_out
    else:
        paths_in.append(args[0]) if len(args) > 0 else None
        path_out = args[1] if len(args) == 2 else None
        if len(args) < 1 and options.name: # must have a file to rename
            parser.error("Must specify a file to upload as " + options.name)

    # If no paths_in, set current working directory as the paths_in.
    if not paths_in:
        paths_in.append(os.getcwd())
        head, path_out = os.path.split(paths_in[0])

    # Check that the paths_in exist.
    else:
        for path in paths_in:
            if not os.path.exists(path):
                parser.error("Local path doesn't exist: " + path)

    # paths_in exists so run UPLOAD
    sb.upload(paths_in, path_out, options)

if __name__ == "__main__":
    sys.exit(main())
