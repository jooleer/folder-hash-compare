# Folder Hash Compare
Compares hash values for 2 directories

#### Video Demo: tbd

## Description:

Folder Hash Compare generates hashes for all files in 2 directories and then compares those hashes against eachother.

# Installation/Requirements:

Can be run as-is with python 3.x

# Usage:

FHC can be run with several parameters:
`folder_hash_compare.py [-h] [-p PRIMARY] [-s SECONDARY] [-d] [-m] [-n] [-v] [-c]`
```
-h, --help                            shows help message and exits
-p PRIMARY, --primary PRIMARY         path of primary directory f.e. -p "/home/user/dir1" or -p "C:\folder1"  
-s SECONDARY, --secondary SECONDARY   path of secondary directory f.e. -p "/home/user/dir2" or -p "D:\folder2"
-d, --disable                         disabled multithreading, when disabled the hashing will be done sequentially, by default they will be done simultaniously
-m, --missing                         searches for missing files in secondary directory (i.e. present in PRIMARY but not present in SECONDARY)
-n, --nmissing                        searches for missing files in primary directory (i.e. present in SECONDARY but not present in PRIMARY)
-v, --verbose                         enables verbose logging, outputs all steps in terminal
-l, --logging                         enables logging to txt file in logs/ folder
-c, --custom                          disables use of -p and -s parameters and allows to set hardcoded directory paths (for jobs that have to be done frequently with the same paths)
```



# Sources:




# Final notes:
I made Folder Hash Compare because there wasn't a program that suited my needs and worked cross-platform. After backing up a large amount of data to an external source I had some trouble finding a solution to make sure that all files were copied correctly. FHC started as a small script to quickly check folders but I added several functions and options (multithreading, enabling and disabling features) that other solutions didn't provide.

<br/>
_This software was created for educational purposes for my final project for CS50P and is licensed under the [MIT License](https://github.com/jooleer/folder-hash-compare/blob/main/LICENSE)._

