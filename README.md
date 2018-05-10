# Python directory size calculation benchmark

This repository compliments the article about [fastest approach to directory calculation in Python](https://duseev.com/articles/fastest-directory-size-python/) published in the [duseev.com](https://duseev.com) blog.

## Installation

The repository is published with PyEnv `.python-version` file and Pipenv's `Pipfile`. However, it should run just fine on Python >= 3.5 on a Unix like system.

```console
pipenv install
```

## Usage

```console
usage: benchmark.py [-h] [-p PATH] [-m METHOD] [-c COUNT] [--depth DEPTH]
                    [--dir-count COUNT] [--file-count COUNT]

Directory size measurement benchmark.

Benchmarks different approaches to directory size determination in Python.
Note: some approaches are platform dependant!

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the measured directory.
                        Examples:
                          - test on current directory:
                            benchmark.py -p .
                          - create a temporary test directory:
                            benchmark.py
                          - supply a path to another directory:
                            benchmark.py --path /usr/local/bin
                        Default:
                          - creates a temporary test directory and then deletes it.
                        Exceptions:
                          - path is not a directory
                            action: logs an error and quits.
  -m METHOD, --method METHOD
                        Name of the measurement method to invoke.
                        Choices:
                          - all
                            description: test all methods.
                          - os_walk_lstat
                            description: os.walk with explicit os.lstat call on each file.
                          - os_walk_getsize_loop
                            description: os.walk with os.path.getsize call on each file.
                          - os_walk_getsize_sum
                            description: os.walk with list comprehension sum in each directory.
                          - os_scandir_recursive
                            description: recursive os.scandir with stat.st_size call
                          - os_du_subprocess
                            description: subprocess with du -s
                          - os_find_ls_awk_subprocess
                            description: find with exec of ls -l and sum done by awk
                        Default:
                          - all
  -c COUNT, --invocation-count COUNT
                        Number of invocations of the benchmarked methods.
                        Default:
                          - 3 invocations.
  --depth DEPTH         Depth of the temporary test directory.
                        Ignored, when path is specified.
                        Default:
                          - 4 levels of nesting.
  --dir-count COUNT     Number of subdirectories created at each nesting level.
                        Ignored, when path is specified.
                        Default:
                          - 5 subdirectories.
  --file-count COUNT    Number of files created at each nesting level.
                        Ignored, when path is specified.
                        Default:
                          - 50 files in each directory.
```

## Example

Here is an example of benchmark's output for 
```console
python benchmark.py --number 3 --levels 4 --num-dirs 5
```

**Output:**
```console
2018-05-06 04:32:26,009 Creating test benchmark directory at benchmark_tree
2018-05-06 04:32:28,101 Priming the system's cache...
2018-05-06 04:32:28,287 Benchmark iteration #1/3...
2018-05-06 04:32:28,691 Benchmark iteration #2/3...
2018-05-06 04:32:29,291 Benchmark iteration #3/3...
2018-05-06 04:32:29,990 os_walk_lstat method; best: 0.115; average: 0.141
2018-05-06 04:32:29,990 os_walk_getsize_loop method; best: 0.093; average: 0.131
2018-05-06 04:32:29,990 os_walk_getsize_sum method; best: 0.091; average: 0.142
2018-05-06 04:32:29,991 os_scandir_recursive method; best: 0.074; average: 0.109
2018-05-06 04:32:29,991 os_du_subprocess method; best: 0.031; average: 0.043
2018-05-06 04:32:29,991 Removing test benchmark directory at benchmark_tree
```

