# Static Builder
###   Mo'Static Less Hassle

* Easy to use python script for uploading content to Amazon S3. 

* Can either be imported or used from the command line.

* Use to easily create and update a static S3 website.

* By default only uploads modified content.

* Attempts to honor *.gitignore*.

* Requires (https://github.com/boto/boto "boto") with AWS keys saved in
  *.bashrc*.

* MIT license so use or abuse at your own risk.

## To set up for command line:

1. Install boto, sign up for AWS, get keys

2. Copy and paste staticbuilder.py somewhere on your computer.

3. Place AWS keys and S3 location in .bashrc

    AWS_ACCESS_KEY_ID='your AWS access key'   
    AWS_SECRET_ACCESS_KEY='your AWS secret key'   
    S3_LOCATION='DEFAULT'   
    export AWS_ACCESS_KEY_ID   
    export AWS_SECRET_ACCESS_KEY   
    export S3_LOCATION   

4. Make an alias to the file in .bashrc (recursive default)

    alias sb='python ~/your/path/staticbuilder.py -r'

## To use:

Upload a directory or file

    sb <path/to/file_or_directory> <bucket_name/path/to/file_or_directory>

* Option: -f to force upload of unchanged content

* Option: -n to rename uploaded file

* Option: -m to set metadata 

* Paths can be a python list

* If no file or directory specified current directory will be uploaded

* If no bucket or key specified will determine if uploaded directory/file name exists on S3

* If uploaded directoy/file name doesn't exist, will prompt to create

Delete directory or file

    sb -d <path/to/delete>

List buckets
    
    sb -l buckets

List keys in a bucket

    sb -l <bucket_name>

Change an acl policy

    sb -a <bucket_name or key> <acl_policy>

Make a bucket publically available as a website

    sb -w <bucket_name>

See command line options

    sb -h

