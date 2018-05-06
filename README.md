# Python directory size calculation benchmark

This repository compliments the article about [fastest approach to directory calculation in Python](https://duseev.com/articles/fastest-directory-size-python/) published in the [duseev.com](https://duseev.com) blog.

## Installation

The repository is published with PyEnv `.python-version` file and Pipenv's `Pipfile`. However, it should run just fine on Python >= 3.5 on a Unix like system.

```console
pipenv install
```

## Usage

```console
usage: benchmark.py [-h] [-p PATH] [-n NUMBER] [-l LEVELS] [-d NUM_DIRS]
                    [-f NUM_FILES]

optional arguments:
  -h,           --help                show this help message and exit
  -p PATH,      --path PATH           path to the directory;
                                      creates temporary test directory, if omitted
  -n NUMBER,    --number NUMBER       number of times to run the benchmark
  -l LEVELS,    --levels LEVELS       nesting level when creating test dir
  -d NUM_DIRS,  --num-dirs NUM_DIRS   number of directories in each test dir
  -f NUM_FILES, --num-files NUM_FILES number of files in each test dir
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

