#!/usr/bin/env python3
"""Convenience launcher for the Restaurant POS GUI.

Run this from the project root:

    python run_pos.py

It adds the project root to ``sys.path`` so the ``restaurant_pos`` package
can be imported without installing it first.
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from restaurant_pos.app import main

if __name__ == "__main__":
    main()
