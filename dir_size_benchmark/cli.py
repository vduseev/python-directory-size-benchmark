from cleo import Application, Command, argument, option
import ilexconf
from loguru import logger

from .config import Config
from .directory import Directory


class RunCommand(Command):
    name = "run"
    description = "Run one or all measuring methods in a given directory."

    arguments = [
        argument(
            name="method",
            description="Name of the measurement method to invoke. ",
            optional=True,
            default=Config.defaults.method,
        ),
        argument(
            name="path",
            description="Path of the directory to measure.",
            optional=True,
            default=Config.defaults.path,
        ),
    ]

    options = [
        option(
            long_name="count",
            short_name="c",
            description="Number of times method should be invoked",
            flag=False,
            value_required=True,
            default=Config.defaults.count,
        )
    ]

    def __init__(self, cfg):
        self.cfg: ilexconf.Config = cfg
        super().__init__()

    def handle(self):
        args = self.argument()
        options = self.option()
        self.cfg.merge(args, options)


class CreateCommand(Command):
    name = "create"
    description = "Create benchmark directory filled with files."

    arguments = [
        argument(
            name="path",
            description="Path at which measured directory must be created.",
            optional=True,
            default=Config.defaults.path,
        )
    ]

    options = [
        option(
            long_name="dir-count",
            short_name="d",
            description="Number of subdirectories created at each nesting level.",
            flag=False,
            value_required=True,
            default=Config.defaults.dir_count,
        ),
        option(
            long_name="file-count",
            short_name="f",
            description="Number of files created at each nesting level.",
            flag=False,
            value_required=True,
            default=Config.defaults.file_count,
        ),
        option(
            long_name="recurse",
            short_name="r",
            description="Nesting depth.",
            flag=False,
            value_required=True,
            default=Config.defaults.recurse,
        ),
    ]

    def __init__(self, cfg):
        self.cfg = cfg
        super().__init__()

    def handle(self):
        args = self.argument()
        options = self.option()
        self.cfg.merge(args, options)

        directory = Directory(self.cfg)

        try:
            directory.create()
        except Exception as e:
            self.line(f"<error>{e}</error>")


def run():
    cfg = Config()

    application = Application("dir-size-benchmark", "1.0.1")
    application.config.set_terminate_after_run(False)

    application.add(RunCommand(cfg))
    application.add(CreateCommand(cfg))
    application.run()

    # cfg.submerge(cfg.defaults)
    # from pprint import pprint

    # pprint(cfg)


# def take_action(params):
#     # filter which methods are going to be tested
#     if method == "all":
#         methods = METHODS
#         logging.info("All available methods will be benchmarked...")
#     else:
#         methods = {method: METHODS[method]}
#         logging.info("Only {0} method will be benchmarked...".format(method))

#     # Warm up file system's block cache
#     logging.info("Priming the system's cache...")
#     for m in methods:
#         methods[m]["func"](path, ignore=True)

#     # At each ietration run all methods and capture their timings
#     for i in range(count):
#         logging.debug("Benchmarking iteration #%i/%i...", i + 1, count)
#         for m in methods:
#             methods[m]["func"](path)

#     # Print results for each method
#     for m in methods:
#         results = methods[m]["results"]
#         timings = [r["time"] for r in results]
#         sizes = [r["size"] for r in results]
#         # Determine if sizes are equal
#         is_same_sizes = sum(sizes) / len(sizes) == sizes[0]
#         if is_same_sizes:
#             sizes_msg = ""  # Do not print anything, if size is equal
#         else:
#             sizes_msg = "\n    Sizes are not equal: (" + ", ".join(sizes) + ")\n"
#         logging.info(
#             (
#                 "Results of {} method:\n"
#                 "  -  Average time: {:.3f}\n"
#                 "  -     Best time: {:.3f}\n"
#                 "  - Measured size: {:d}{}"
#             ).format(m, sum(timings) / len(timings), min(timings), sizes[0], sizes_msg)
#         )


# def take_action_2():
#     # Create test tree if path is not specified
#     is_benchmark_tree_created = False  # Remember we created a tree
#     if args.path:
#         tree_dir = args.path
#         # Exits if directory does not exist or not a directory
#         assert_existing_dir(tree_dir)
#     else:
#         tree_dir = os.path.join(os.path.dirname(__file__), "benchmark_tree")
#         if not os.path.exists(tree_dir):
#             logging.info("Creating test benchmark directory at %s", tree_dir)
#             create_tree(tree_dir, args.DEPTH, args.DIR_COUNT, args.FILE_COUNT)
#             is_benchmark_tree_created = True  # rm -rf tree later
#         else:
#             logging.info("Using existing test benchmark directory at %s", tree_dir)

#     # Run benchmark test
#     benchmark(tree_dir, args.METHOD, args.COUNT)

#     # Erase tree if it was created for a test
#     if is_benchmark_tree_created:
#         remove_tree(tree_dir)
