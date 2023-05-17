import os
import sys
import hashlib
import zlib
import logging
import time
import argparse
from multiprocessing.pool import ThreadPool

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
        # in case program is not run directly
        if __name__ == '__main__':
            file_hash = generate_file_hash(file_path, hash_algorithm)
        else:
            file_hash = generate_file_hash(file_path, "CRC32")
        relative_path = os.path.relpath(file_path, folder_path)
        folder_hashes[relative_path] = file_hash
        # in case program is not run directly
        if __name__ == '__main__':
            if(args.verbose):
                print(f"Generated hash for: {file_path} [{file_hash}]")
            if(not args.logging):
                logging.info(f"[HASH] {file_path} -> {file_hash}")
    return folder_hashes

# convert seconds to hours, minutes, seconds
def seconds_to_minutes(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return hours, minutes, seconds


def search_missing_files(directory, folder_hashes):
    files_missing = 0
    for file_path in get_all_files(directory):
        relative_path = os.path.relpath(file_path, directory)
        if relative_path not in folder_hashes:
            if(args.verbose):
                print(bcolors.WARNING + f"{relative_path} is missing from {directory}." + bcolors.ENDC)
            if(not args.logging):
                logging.warning(f"[MISSING FILE] {directory} -> {relative_path}")
            files_missing += 1
    if files_missing > 0:
        print(bcolors.FAIL + f"{files_missing} files missing from directory: {directory} " + bcolors.ENDC)
        if(not args.logging):
            print("(see log for details)")
    else:
        print(bcolors.OKGREEN + f"No files missing from directory: {directory}" + bcolors.ENDC)
    return files_missing


def main():
    files_completed = 0
    files_errors = 0
    files_missing_total = 0
    start = time.time()

    if(not args.logging):
        if not os.path.isdir("logs"):
            os.makedirs("logs")
        log_name = str(time.time())
        logging.basicConfig(filename="logs/log_"+log_name+".txt", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
        print(f"Log file: logs/log_{log_name}.txt\n")
        logging.info(f"[SETTINGS] -p {args.primary} -s {args.secondary} -a {args.algorithm} -d {args.disable} -m {args.missing} -n {args.nmissing} -v {args.verbose} -l {args.logging} -c {args.custom}\n")

    f1_amount = get_files_amount(primary_directory)
    f2_amount = get_files_amount(secondary_directory)

    logging.info("Generating hashes..")
    # multithreading
    if(args.disable):
        # run without multithreading
        if(args.verbose):
            print(bcolors.UNDERLINE + "Running jobs without multithreading" + bcolors.ENDC)
        folder1_hashes = folder_generate_hashes(primary_directory)
        folder2_hashes = folder_generate_hashes(secondary_directory)

    else:
        # use multithreading
        if(args.verbose):
            print(bcolors.UNDERLINE + "Running jobs with multithreading" + bcolors.ENDC)

        pool = ThreadPool(processes=2)
        async_result1 = pool.apply_async(folder_generate_hashes, args = (primary_directory, ))
        async_result2 = pool.apply_async(folder_generate_hashes, args = (secondary_directory, ))

        pool.close()
        pool.join()

        folder1_hashes = async_result1.get()
        folder2_hashes = async_result2.get()

    # check for missing files in primary directory
    if(args.nmissing):
        logging.info(f"Searching for missing files in primary directory: {primary_directory}")
        files_missing_total += search_missing_files(primary_directory, folder2_hashes)

    # check for missing files in secondary directory
    if(args.missing):
        logging.info(f"Searching for missing files in secondary directory: {secondary_directory}")
        files_missing_total += search_missing_files(secondary_directory, folder1_hashes)

    # compare the hash values for each file in both folders
    logging.info(f"Comparing hash values..")
    for relative_path in set(folder1_hashes.keys()).intersection(set(folder2_hashes.keys())):
        if folder1_hashes[relative_path] != folder2_hashes[relative_path]:
            if(args.verbose):
                print(bcolors.FAIL + f"Hash values for {relative_path} do not match." + bcolors.ENDC)
            if(not args.logging):
                logging.error(f"[HASH MISMATCH] {secondary_directory} -> {relative_path} ({folder1_hashes[relative_path]} <> {folder2_hashes[relative_path]})")
            files_errors += 1
        else:
            if(args.verbose):
                print(bcolors.OKGREEN + f"Hash values for {relative_path} match." + bcolors.ENDC)
            if(not args.logging):
                logging.info(f"[HASH OK] {relative_path}")
            files_completed += 1

    end = time.time()
    total_time = end - start
    files_amount = f1_amount + f2_amount

    # process output information
    if total_time > 60:
        ct = seconds_to_minutes(total_time)
        print(f"\nProcess finished in {round(ct[0])} hours, {round(ct[1])} minutes, {round(ct[2])} seconds")
        logging.info(f"Process finished in {round(ct[0])} hours, {round(ct[1])} minutes, {round(ct[2])} seconds")
    else:
        print(f"\nProcess finished in {round((total_time), 2)} seconds")
        logging.info(f"Process finished in {round((total_time), 2)} seconds")

    print(f"Processed {files_amount} file(s): "
    + bcolors.OKGREEN + f"\n{files_completed} file(s) OK" + bcolors.ENDC
    + bcolors.FAIL + f"\n{files_errors} file(s) FAILED" + bcolors.ENDC
    + bcolors.WARNING + f"\n{files_missing_total} file(s) MISSING" + bcolors.ENDC)

    logging.info(f"Processed {files_amount} file(s): ")
    logging.info(f"{files_completed} file(s) OK")
    logging.info(f"{files_errors} file(s) FAILED")
    logging.info(f"{files_missing_total} file(s) MISSING")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='folder_hash_compare.py',
                    description='Compares the hashes of all files in 2 folders',
                    epilog='Folder Hash Compare - https://github.com/jooleer/folder-hash-compare')

    parser.add_argument('-p', '--primary', help='Primary directory, f.e. -p \"C:\\folder1\\\" or -p \"/home/user/dir1\"')
    parser.add_argument('-s', '--secondary', help='Secondary directory, f.e. -s \"D:\\folder2\\\" or -s \"/home/user/dir2\"')
    parser.add_argument('-a', '--algorithm', help='Set algorithm: CRC32 (default), MD5, SHA256')
    parser.add_argument('-d', '--disable', action='store_true', help='Disable multithreading (recommended when both directories are on the same drive)')
    parser.add_argument('-m', '--missing', action='store_true', help='Search for missing files in secondary directory')
    parser.add_argument('-n', '--nmissing', action='store_true', help='Search for missing files in primary directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enables verbose logging')
    parser.add_argument('-l', '--logging', action='store_true', help='Disables logging to txt file in logs/ folder')
    parser.add_argument('-c', '--custom', action='store_true', help='Use custom/hardcoded variables in stead of -p -s command-line arguments')
    args = parser.parse_args()

    # define the paths of the two directories to compare
    if(args.custom):
        primary_directory = r""
        secondary_directory = r""
    else:
        if(not args.primary) or (not args.secondary):
            sys.exit("No primary or secondary folder given, use -h for help")
        primary_directory = args.primary
        secondary_directory = args.secondary
    
    if(args.verbose):
        print(f"Comparing:\n{primary_directory}\nagainst:\n{secondary_directory}\n")
        logging.info(f"Comparing: {primary_directory} against: {secondary_directory}")

    # hash algorithm (CRC32, MD5, SHA256)
    if(not args.algorithm):
        hash_algorithm = "CRC32"
    else:
        hash_algorithm = args.algorithm

    main()
