#!/usr/bin/env bash
# ==============================================================================
# SupportTriagingEngine
# ==============================================================================
# Overview
# --------
# This script serves as the entry point for running the SupportTriagingEngine
# microservice locally. It sets up the required environment variables and
# executes the FastAPI application using Uvicorn.
#
# Key Features
# ------------
# 1. Environment Configuration
#    - Sets PYTHONPATH to the current directory to ensure local modules
#      in the 'src' directory are correctly discoverable by Python.
#
# 2. Execution
#    - Launches the Uvicorn ASGI server with hot-reloading enabled for
#      rapid development cycles.
#
# Usage
# -----
# ./run_local.sh
#
# Author
# ------
# Elham Esmaeilnia (elham.e.shirvani@gmail.com)
#
# Version
# -------
# 1.0.0
#
# Date
# ----
# 2026-05-18
# ==============================================================================
export PYTHONPATH=$(pwd)
uvicorn src.api.main:app --reload