import os
import stat
import subprocess


def du(path):
    size = subprocess.check_output(
        ['du', '-s', path]
    ).split()[0].decode('utf-8')
    size = int(size) * 512
    return size


def find_ls_awk(path):
    cmd = ('find ' + path + ' -type f '
           '-exec ls -l \'{}\' \; | '
           'awk \'{sum+=$5} END {print sum}\'')
    size = subprocess.check_output(
        cmd, shell=True
    ).split()[0].decode('utf-8')
    return int(size)


def find_while_read_cat_wc(path):
    cmd = ('find ' + path + ' -type f | '
           'while read s; do cat $s; done | '
           'wc -c')
    size = subprocess.check_output(
        cmd, shell=True
    ).split()[0].decode('utf-8').strip()
    return int(size)


def find_xargs_cat_wc(path):
    cmd = ('find ' + path + ' -type f | '
           'xargs cat | '
           'wc -c')
    size = subprocess.check_output(
        cmd, shell=True
    ).split()[0].decode('utf-8').strip()
    return int(size)


def scandir(path):
    size = 0

    def scan(path):
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from scan(entry.path)
            else:
                yield entry

    for entry in scan(path):
        try:
            size += entry.stat().st_size
        except FileNotFoundError:
            continue
    return size


def walk_getsize_sum(path):
    size = 0
    for root, _, files in os.walk(path):
        size += sum([
            os.path.getsize(
                os.path.join(root, name)
            ) for name in files
        ])
    return size


def walk_getsize(path):
    size = 0
    for root, _, files in os.walk(path):
        for filename in files:
            fullname = os.path.join(root, filename)
            size += os.path.getsize(fullname)
    return size


def walk_lstat(path):
    size = 0
    for root, _, files in os.walk(path):
        for filename in files:
            fullname = os.path.join(root, filename)
            st = os.lstat(fullname)
            if not stat.S_ISLNK(st.st_mode):
                size += st.st_size
    return size
