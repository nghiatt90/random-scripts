#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pythonProject.utils
# Date: 2022/03/09
# Filename: utils

__author__ = "Yoshi Truong"
__date__ = "2022/03/09"


IMAGE_EXTENSIONS = ("jpg", "jpeg", "png")


def is_image(path: str):
    return any(path.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
