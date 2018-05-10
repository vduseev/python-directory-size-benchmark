import os
import argparse
import logging
import timeit


METHODS = dict()


class BenchmarkMethod(object):
    def __init__(self, desc=''):
        self.description = desc
    def __call__(self, func):
        name = func.__name__
        def wrapper(*args, **kwargs):
            # Capture beginning of measurement
            t1 = timeit.default_timer()
            # Call to the underlying function
            size = func(*args, **kwargs)
            # Capture end of measurement
            t2 = timeit.default_timer()
            # Log benchmark results
            METHODS[name]['timings'].append(t2 - t1)
            # Return calculation results
            return size
        # Preserve original function name
        wrapper.name = name
        wrapper.desc = self.description
        # Register the decorated method within global collection
        # of methods that we are going to test later
        METHODS[name] = {
            'func': wrapper,
            'desc': self.description,
            'timings': []
        }
        return wrapper


def time_function(func):
    """Time measurement decorator."""
    def wrapper(*args, **kwargs):
        # Capture beginning of measurement
        t1 = timeit.default_timer()
        # Call to the underlying function
        size = func(*args, **kwargs)
        logging.debug('%s: size: %s', time_function.__name__, str(size))
        # Capture end of measurement
        t2 = timeit.default_timer()
        return t2 - t1
    # Preserve original function name
    wrapper.__name__ = func.__name__
    # Register the decorated method within global collection
    # of methods that we are going to test later
    METHODS[wrapper.__name__] = {
        'func': wrapper,
        'timings': []
    }
    return wrapper


@BenchmarkMethod(desc='os.walk with explicit os.lstat call on each file.')
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


@BenchmarkMethod(desc='os.walk with os.path.getsize call on each file.')
def os_walk_getsize_loop(path):
    size = 0
    from os.path import join, getsize
    for root, dirs, files in os.walk(path):
        for filename in files:
            fullname = join(root, filename)
            size += getsize(fullname)
    return size


@BenchmarkMethod(desc='os.walk with list comprehension sum in each directory.')
def os_walk_getsize_sum(path):
    size = 0
    from os.path import join, getsize
    for root, dirs, files in os.walk(path):
        size += sum([getsize(join(root, name)) for name in files])
    return size


@BenchmarkMethod(desc='recursive os.scandir with stat.st_size call')
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


@BenchmarkMethod(desc='subprocess with du -s')
def os_du_subprocess(path):
    import subprocess
    size = subprocess.check_output(
        ['du', '-s', path]
    ).split()[0].decode('utf-8')
    return size


@BenchmarkMethod(desc='find with exec of ls -l and sum done by awk')
def os_find_ls_awk_subprocess(path):
    cmd = ('find {1} -type -f '
           '-exec ls -l \'{}\' \; | '
           'awk \'{sum+=$5} END {print sum}\'')
    def __desc_():
        return cmd
    import subprocess
    size = subprocess.check_output(
        cmd,
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


def remove_tree(path):
    logging.info('Removing test benchmark directory at %s', path)
    import shutil
    shutil.rmtree(path)

def benchmark(path, method, count):
    # Warm up file system's block cache
    logging.info('Priming the system\'s cache...')
    os_scandir_recursive(path)

    # Filter which methods are going to be tested
    if method == 'all':
        methods = METHODS
        logging.info('All available methods will be benchmarked...')
    else:
        methods = { method: METHODS[method] }
        logging.info('Only {0} method will be benchmarked...'.format(method))


    # At each ietration run all methods and capture their timings
    for i in range(count):
        logging.debug('Benchmarking iteration #%i/%i...', i+1, count)
        for m in methods:
            size = methods[m]['func'](path)

    # Print results for each method
    for m in methods:
        logging.info(
            '%s method; best: %.3f; average: %.3f',
            m,
            min(methods[m]['timings']),
            sum(methods[m]['timings']) / len(methods[m]['timings'])
        )


def configure_logging():
    fmt = '%(asctime)s %(filename)s %(levelname)8s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=fmt)


def configure_argument_parser():
    # Define argument parser with a detailed description.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            'Directory size measurement benchmark.\n'
            '\n'
            'Benchmarks different approaches to directory size '
            'determination in Python.\n'
            'Note: some approaches are platform dependant!'
        )
    )

    # Specify path argument
    parser.add_argument(
        '-p', '--path',
        type=str,
        default=None,
        help=(
            'Path to the measured directory.\n'
            'Examples:\n'
            '  - test on current directory:\n'
            '    %(prog)s -p . \n'
            '  - create a temporary test directory:\n'
            '    %(prog)s \n'
            '  - supply a path to another directory:\n'
            '    %(prog)s --path /usr/local/bin \n'
            'Default:\n'
            '  - creates a temporary test directory and then deletes it.\n'
            'Exceptions:\n'
            '  - path is not a directory\n'
            '    action: logs an error and quits.'
        )
    )

    # Specify method argument.
    # List all methods.
    methods = '\n'.join(
        [
            '  - {0}\n    description: {1}'.format(
                m, METHODS[m]['desc']
            ) for m in METHODS
        ]
    )

    parser.add_argument(
        '-m', '--method',
        type=str,
        default='all',
        dest='METHOD',
        choices=['all'].extend(METHODS.keys()),
        help=(
            'Name of the measurement method to invoke.\n'
            'Choices:\n'
            '  - all \n'
            '    description: test all methods.\n' + methods + '\n'
            'Default:\n'
            '  - %(default)s \n'
        )
    )

    parser.add_argument(
        '-c', '--invocation-count',
        type=int,
        default=3,
        dest='COUNT',
        help=(
            'Number of invocations of the benchmarked methods.\n'
            'Default:\n'
            '  - %(default)s invocations.'
        )
    )

    parser.add_argument(
        '--depth',
        type=int,
        default=4,
        dest='DEPTH',
        help=(
            'Depth of the temporary test directory.\n'
            'Ignored, when path is specified.\n'
            'Default:\n'
            '  - %(default)s levels of nesting.'
        )
    )

    parser.add_argument(
        '--dir-count',
        type=int,
        default=5,
        dest='DIRS_COUNT',
        metavar='COUNT',
        help=(
            'Number of subdirectories created at each nesting level.\n'
            'Ignored, when path is specified.\n'
            'Default:\n'
            '  - %(default)s subdirectories.'
        )
    )

    parser.add_argument(
        '--file-count',
        type=int,
        default=50,
        dest='FILE_COUNT',
        metavar='COUNT',
        help=(
            'Number of files created at each nesting level.\n'
            'Ignored, when path is specified.\n'
            'Default:\n'
            '  - %(default)s files in each directory.'
        )
    )

    # Return configured parser
    return parser


def assert_existing_dir(path):
    if not os.path.isdir(tree_dir):
        import sys
        logging.error(
            ('{0}, specified in PATH argument, '
             'is not a directory!').format(tree_dir)
        )
        sys.exit(1)
    else:
        logging.debug('Using existing directory: %s', args.path)


if __name__ == '__main__':
    # Set up config format and default display level
    configure_logging()

    # Parse arguments
    parser = configure_argument_parser()
    args = parser.parse_args()

    # Create test tree if path is not specified
    is_benchmark_tree_created = False  # Remember we created a tree
    if args.path:
        tree_dir = args.path
        # Exits if directory does not exist or not a directory
        assert_existing_dir(tree_dir)
    else:
        tree_dir = os.path.join(os.path.dirname(__file__), 'benchmark_tree')
        if not os.path.exists(tree_dir):
            logging.info('Creating test benchmark directory at %s', tree_dir)
            create_tree(tree_dir, args.levels, args.num_dirs, args.num_files)
            is_benchmark_tree_created = True  # rm -rf tree later
        else:
            logging.info('Using existing test benchmark directory at %s', tree_dir)

    # Run benchmark test
    benchmark(tree_dir, args.METHOD, args.COUNT)

    # Erase tree if it was created for a test
    if is_benchmark_tree_created:
        remove_tree(tree_dir)
