#!/usr/bin/env python3
# -*- coding: utf8 -*-

import gzip


def ungzip(data):
    try:
        data = gzip.decompress(data)
    except Exception as e:
        print(e)
    return data
