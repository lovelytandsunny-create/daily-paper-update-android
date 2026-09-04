"""自定义 python3 recipe：为 Python 3.12 在 NDK r28c 上编译时禁用 grp 模块。

NDK r28 移除了 getgrent/setgrent/endgrent 声明，但 Python 3.11/3.12 的
grpmodule.c 仍会调用它们，导致编译失败。通过 ac_cv_header_grp_h=no
让 CPython 的 configure 跳过 grp 模块构建。
"""
from pythonforandroid.recipes.python3 import Python3Recipe as Python3RecipeBase


class Python3Recipe(Python3RecipeBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_args = list(self.configure_args)
        if "ac_cv_header_grp_h=no" not in self.configure_args:
            self.configure_args.append("ac_cv_header_grp_h=no")


recipe = Python3Recipe()
