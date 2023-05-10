# Folder Hash Compare
Compares hash values for 2 directories

<br/>

# Description:

Folder Hash Compare generates hashes for all files in 2 directories and then compares those hashes against eachother.

<br/>

# Installation/Requirements:

Can be run as-is with python 3.x

<br/>

# Usage:

FHC can be run with several parameters:
`folder_hash_compare.py [-h] [-p PRIMARY] [-s SECONDARY] [-a] [-d] [-m] [-n] [-v] [-l] [-c]`
```
-h, --help                            shows help message and exits
-p PRIMARY, --primary PRIMARY         path of primary directory f.e. -p "/home/user/dir1" or -p "C:\folder1"  
-s SECONDARY, --secondary SECONDARY   path of secondary directory f.e. -p "/home/user/dir2" or -p "D:\folder2"
-a, --algorithm                       set algorithm to CRC32, MD5 or SHA256 (CRC32 by default)
-d, --disable                         disabled multithreading, when disabled the hashing will be done sequentially, by default they will be done simultaneously
-m, --missing                         searches for missing files in secondary directory (i.e. present in PRIMARY but not present in SECONDARY)
-n, --nmissing                        searches for missing files in primary directory (i.e. present in SECONDARY but not present in PRIMARY)
-v, --verbose                         enables verbose logging, outputs all steps in terminal
-l, --logging                         disables logging to txt file in logs/ folder
-c, --custom                          disables use of -p and -s parameters and allows to set hardcoded directory paths (for jobs that have to be done frequently with the same paths)
```

`-p PRIMARY` and `-s SECONDARY` are not required when using `-c`, when using the `-c, --custom` parameter, make sure to fill in the `primary_directory` and `secondary_directory` variables in `folder_hash_compare.py`.

`-p PRIMARY` and `-s SECONDARY` can be any path starting from the root to deeper directories. Directories can only be scanned and processed granted the user has access to them.

`-a, --algorithm` allows the user to change the default algorithm to any of the 3 available ones: __CRC32__, __MD5__ or __SHA256__. __CRC32__ is faster but not secure, __MD5__ is slower than __CRC32__ but faster than __SHA256__ but is nowadays considered insecure. __SHA256__ is slower than both __CRC32__ and __MD5__ but is also more secure than either of them. For the purposes of this program I didn't feel the need to have a higher than 256-bit algorithm as it's generally just to verify if a directories' contents copied without errors to another one.

`-d, --disable` disables multithreading. By default multithreading is enabled but if comparing 2 directories that are on the same drive it might be faster to have multithreading disabled. When disabled files will be hashes sequentially, starting from the primary directory and then processing the secondary directory. When multithreading is enabled file hashes are generated simultaneously. 

`-l, --logging` disables logging _(when enabled logs will be stored as a .txt file in logs/ folder)_, recomendded to keep enabled, especially when you expect to encounter missing files (also see `-m, --missing` & `-n, --nmissing` below)

`-m, --missing` and `-n, --nmissing` search for missing files. `-m` will report missing files in the secondary directory, i.e. files that are present in the PRIMARY directory but missing in the SECONDARY directory. `-n` will search for missing files the other way around, i.e. files that are present in the SECONDARY directory but missing in the PRIMARY directory. Recommended to use `-l, --logging` when using either of these settings.

`-v, --verbose` displays a verbose logging output as the program runs, notifying the user of each step.

<br/>

# Final notes:
I made Folder Hash Compare because there wasn't a program that suited my needs and worked cross-platform. After backing up a large amount of data to an external source I had some trouble finding a solution to make sure that all files were copied correctly. FHC started as a small script to quickly check folders but I added several functions and options (multithreading, enabling and disabling features) that other solutions didn't provide.

<br/><br/>

_This software was created for educational purposes for my final project for CS50P and is licensed under the [MIT License](https://github.com/jooleer/folder-hash-compare/blob/main/LICENSE)._

