# this code is still WIP

import os
import sys
import hashlib
import zlib
import logging
import time
import argparse
from multiprocessing.pool import ThreadPool

parser = argparse.ArgumentParser(
                    prog='folder_hash_compare.py',
                    description='Compares the hashes of all files in 2 folders',
                    epilog='Folder Hash Compare - https://github.com/jooleer/folder-hash-compare')

parser.add_argument('-p', '--primary', help='Primary directory, f.e. -p \"C:\\folder1\\\" or -p \"/home/user/dir1\"')
parser.add_argument('-s', '--secondary', help='Secondary directory, f.e. -s \"D:\\folder2\\\" or -s \"/home/user/dir2\"')
parser.add_argument('-d', '--disable', action='store_true', help='Disable multithreading (recommended when both directories are on the same drive)')
parser.add_argument('-m', '--missing', action='store_true', help='Search for missing files in secondary directory')
parser.add_argument('-v', '--verbose', action='store_true', help='Enables verbose logging')
parser.add_argument('-c', '--custom', action='store_true', help='Use custom/hardcoded variables in stead of -p -s command-line arguments')

args = parser.parse_args()

# define the paths of the two directories to compare
if(args.custom):
    folder1_path = r""
    folder2_path = r""
    if(args.verbose):
        print(f"Comparing:\n{folder1_path}\nagainst:\n{folder2_path}\n")
else:
    if(not args.primary) or (not args.secondary):
        sys.exit("No primary or secondary folder given, use -h for help")
    folder1_path = args.primary
    folder2_path = args.secondary
    if(args.verbose):
        print(f"Comparing:\n{folder1_path}\nagainst:\n{folder2_path}\n")

# hash algorythm (CRC32, MD5, SHA256)
hash_algorithm = "CRC32"

# text markup
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#generate hash value of file
def generate_file_hash(file_path, hash_algorithm="CRC32"):
    with open(file_path, "rb") as f:
        # sys.stdout.write("Processing file %d of %d (%d%%)\r\n\033[K" % (files, files_amount, (files/files_amount)*100) )
        # sys.stdout.write("Generating hash for file: %s\r\033[F" % (file_path) )
        sys.stdout.flush()
        file_data = f.read()
        if hash_algorithm == "CRC32":
            file_hash = zlib.crc32(file_data)
        elif hash_algorithm == "MD5":
            file_hash = hashlib.md5(file_data).hexdigest()
        elif hash_algorithm == "SHA256":
            file_hash = hashlib.sha256(file_data).hexdigest()

        return file_hash

# get a list of all files in a folder and its subfolders
def get_all_files(folder_path):
    global files_amount
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            all_files.append(file_path)
    return all_files

# get amount of files in a folder and its subfolders
def get_files_amount(folder_path):
    files_amount = 0
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            files_amount += 1
    return files_amount

# generate hash values for each file in folder_path
def folder_generate_hashes(folder_path):
    folder_hashes = {}
    for file_path in get_all_files(folder_path):
        file_hash = generate_file_hash(file_path, hash_algorithm)
        relative_path = os.path.relpath(file_path, folder_path)
        folder_hashes[relative_path] = file_hash
        if(args.verbose):
            print(f"Generated hash for: {file_path} [{file_hash}]")
        logging.info(f"[HASH]: {file_path} -> {file_hash}")
    return folder_hashes

# convert seconds to hours, minutes, seconds
def seconds_to_minutes(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return hours, minutes, seconds


def main():
    files_completed = 0
    files_errors = 0
    files_missing = 0

    # set logging file parameter
    if not os.path.isdir("logs"):
        os.makedirs("logs")
    logging.basicConfig(filename="logs/log_"+str(time.time())+".txt", level=logging.INFO)

    # start time 
    start = time.time()

    f1_amount = get_files_amount(folder1_path)
    f2_amount = get_files_amount(folder2_path)

    # multithreading 
    if(args.disable):
        # run without multithreading
        if(args.verbose):
            print(bcolors.UNDERLINE + "Running jobs without multithreading" + bcolors.ENDC)
        folder1_hashes = folder_generate_hashes(folder1_path)
        folder2_hashes = folder_generate_hashes(folder2_path)

    else:
        # use multithreading
        if(args.verbose):
            print(bcolors.UNDERLINE + "Running jobs with multithreading" + bcolors.ENDC)
        
        pool = ThreadPool(processes=2)
        async_result1 = pool.apply_async(folder_generate_hashes, args = (folder1_path, ))
        async_result2 = pool.apply_async(folder_generate_hashes, args = (folder2_path, ))

        # close and join pools
        pool.close()
        pool.join()

        # get the return value from your function.
        folder1_hashes = async_result1.get()  
        folder2_hashes = async_result2.get()


    if(args.missing):
        # check for missing files in folder 1
        # for file_path in get_all_files(folder2_path):
        #     relative_path = os.path.relpath(file_path, folder2_path)
        #     if relative_path not in folder1_hashes:
        #         if(args.verbose):
        #             print(bcolors.WARNING + f"{relative_path} is missing from {folder1_path}." + bcolors.ENDC)
        #         logging.info(f"[WARNING - MISSING FILE]: {relative_path}")
        #         files_missing += 1

        # check for missing files in folder 2
        for file_path in get_all_files(folder1_path):
            relative_path = os.path.relpath(file_path, folder1_path)
            if relative_path not in folder2_hashes:
                if(args.verbose):
                    print(bcolors.WARNING + f"{relative_path} is missing from {folder2_path}." + bcolors.ENDC)
                logging.info(f"[WARNING - MISSING FILE]: {relative_path}")
                files_missing += 1


    # compare the hash values for each file in both folders
    for relative_path in set(folder1_hashes.keys()).intersection(set(folder2_hashes.keys())):
        if folder1_hashes[relative_path] != folder2_hashes[relative_path]:
            if(args.verbose):
                print(bcolors.FAIL + f"Hash values for {relative_path} do not match." + bcolors.ENDC)
            logging.error(f"[ERROR]: FILE HASH MISMATCH FOR: {relative_path} ({folder1_hashes[relative_path]} <> {folder2_hashes[relative_path]}")
            files_errors += 1
        else:
            if(args.verbose):
                print(bcolors.OKGREEN + f"Hash values for {relative_path} match." + bcolors.ENDC)
            logging.info(f"[OK]: {relative_path}")
            files_completed += 1

    end = time.time()
    total_time = end - start
    files_amount = f1_amount + f2_amount

    # process output information
    if total_time > 60:
        ct = seconds_to_minutes(total_time)
        print(f"Process finished in {round(ct[0])} hours, {round(ct[1])} minutes, {round(ct[2])} seconds")
    else:
        print("\nProcess finished in {:.2f}".format(round((total_time), 2)) + " seconds")
    
    print(f"Processed {files_amount} file(s): "
    + bcolors.OKGREEN + f"\n{files_completed} file(s) OK" + bcolors.ENDC
    + bcolors.FAIL + f"\n{files_errors} file(s) FAILED" + bcolors.ENDC
    + bcolors.WARNING + f"\n{files_missing} file(s) MISSING" + bcolors.ENDC)


if __name__ == '__main__':
    main()
