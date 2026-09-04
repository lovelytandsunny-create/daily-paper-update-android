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
        # NDK r28c 移除了 grp/pwd/crypt/部分 posix 函数声明，
        # 而 Python 3.11/3.12 仍会调用它们。这些系统用户管理模块对本应用无用，全部禁用。
        for flag in (
            "ac_cv_header_grp_h=no",        # grp 模块
            "ac_cv_func_getgrouplist=no",   # posix 模块
            "ac_cv_func_initgroups=no",     # posix 模块
            "ac_cv_header_pwd_h=no",        # pwd 模块
            "ac_cv_func_getpwent=no",
            "ac_cv_func_setpwent=no",
            "ac_cv_func_endpwent=no",
            "ac_cv_func_getpwnam=no",
            "ac_cv_func_getpwuid=no",
            "ac_cv_header_crypt_h=no",      # crypt 模块
            "ac_cv_func_crypt=no",
        ):
            if flag not in self.configure_args:
                self.configure_args.append(flag)


recipe = Python3Recipe()
