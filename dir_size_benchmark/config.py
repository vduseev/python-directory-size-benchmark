import ilexconf

import dir_size_benchmark.methods as bm


class Config(ilexconf.Config):
    defaults = ilexconf.Config(
        path=".",
        method="all",
        count=3,
        recurse=4,
        dir_count=5,
        file_count=50,
        methods={
            bm.du.__name__: bm.du,
            bm.find_ls_awk.__name__: bm.find_ls_awk,
            bm.find_while_read_cat_wc.__name__: bm.find_while_read_cat_wc,
            bm.find_xargs_cat_wc.__name__: bm.find_xargs_cat_wc,
            bm.scandir.__name__: bm.scandir,
            bm.walk_getsize_sum.__name__: bm.walk_getsize_sum,
            bm.walk_getsize.__name__: bm.walk_getsize,
            bm.walk_lstat.__name__: bm.walk_lstat,
            "all": None,
        },
    )

    def __init__(self):
        super().__init__(self.defaults)
