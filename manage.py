#!/usr/bin/env python
import os
import sys
import logging

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hkwh.settings")

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        logging.exception(e)
