import os
import argparse
import logging
import timeit


METHODS = []


def time_function(func):
    """Time measurement decorator
    """
    def wrapper(*args, **kwargs):
        t1 = timeit.default_timer()
        size = func(*args, **kwargs)
        t2 = timeit.default_timer()
        return t2 - t1
    # Preserve original function name
    wrapper.__name__ = func.__name__
    # Register the decorated method within global collection
    # of methods that we are going to test later
    METHODS.append({
        'func': wrapper,
        'timings': []
    })
    return wrapper


@time_function
def os_walk_lstat(path):
    size = 0
    import stat
    for root, dirs, files in os.walk(path):
        for filename in files:
            fullname = os.path.join(root, filename)
            st = os.lstat(fullname)
            if not stat.S_ISLNK(st.st_mode):
                size += st.st_size
    return size


@time_function
def os_walk_getsize_loop(path):
    size = 0
    from os.path import join, getsize
    for root, dirs, files in os.walk(path):
        for filename in files:
            fullname = join(root, filename)
            size += getsize(fullname)
    return size


@time_function
def os_walk_getsize_sum(path):
    size = 0
    from os.path import join, getsize
    for root, dirs, files in os.walk(path):
        size += sum([
            getsize(join(root, name)) for name in files
        ])
    return size


@time_function
def os_scandir_recursive(path):
    size = 0

    def scandir_recursive(path):
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from scandir_recursive(entry.path)
            else:
                yield entry

    for entry in scandir_recursive(path):
        try:
            size += entry.stat().st_size
        except FileNotFoundError:
            continue
    return size


@time_function
def os_du_subprocess(path):
    import subprocess
    size = subprocess.check_output(
        ['du', '-sh', path]
    ).split()[0].decode('utf-8')
    return size


@time_function
def os_ls_subprocess(path):
    import subprocess
    size = subprocess.check_output(
        'find ' + path + ' -type f -exec ls -l \'{}\' \; | awk \'{sum+=$5} END {print sum}\'',
        shell=True
    ).split()[0].decode('utf-8')
    return size


def create_tree(path, depth, num_dirs, num_files):
    os.mkdir(path)
    for fi in range(num_files):
        filename = os.path.join(path, 'file{0:03}.txt'.format(fi))
        with open(filename, 'wb') as f:
            f.write(b'foo')
    if depth <= 1:
        return
    for di in range(num_dirs):
        dirname = os.path.join(path, 'dir{0:03}'.format(di))
        create_tree(dirname, depth - 1, num_dirs, num_files)


def benchmark(path, number):
    # Warm up file system's block cache
    logging.info('Priming the system\'s cache...')
    os_scandir_recursive(path)

    # At each ietration run all methods and capture their timings
    for i in range(number):
        logging.debug('Benchmarking iteration #%i/%i...', i+1, number)
        for m in METHODS:
            time = m['func'](path)
            m['timings'].append(time)

    # Print results for each method
    for m in METHODS:
        logging.info(
            '%s method; best: %.3f; average: %.3f',
            m['func'].__name__,
            min(m['timings']),
            sum(m['timings']) / len(m['timings']))


if __name__ == '__main__':
    # Set up config format and default display level
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s %(levelname)8s %(message)s')

    # Parse arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, default=None)
    parser.add_argument('-n', '--number', type=int, default=3)
    parser.add_argument('-l', '--levels', type=int, default=4)
    parser.add_argument('-d', '--num-dirs', type=int, default=5, dest='num_dirs')
    parser.add_argument('-f', '--num-files', type=int, default=50, dest='num_files')
    args = parser.parse_args()

    # Create test tree if path is not specified
    is_benchmark_tree_created = False  # Remember we created a tree
    if args.path:
        tree_dir = args.path
        logging.debug('Using existing directory: %s', args.path)
    else:
        tree_dir = os.path.join(os.path.dirname(__file__), 'benchmark_tree')
        if not os.path.exists(tree_dir):
            logging.info('Creating test benchmark directory at %s', tree_dir)
            create_tree(tree_dir, args.levels, args.num_dirs, args.num_files)
            is_benchmark_tree_created = True  # rm -rf tree later
        else:
            logging.info('Using existing test benchmark directory at %s', tree_dir)

    # Run benchmark test
    benchmark(tree_dir, args.number)

    # Erase tree if it was created for a test
    if is_benchmark_tree_created:
        logging.info('Removing test benchmark directory at %s', tree_dir)
        import shutil
        shutil.rmtree(tree_dir)
