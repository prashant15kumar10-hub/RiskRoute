#!/usr/bin/env bash
set -e
python3 train.py
python3 evaluate_counterfactuals.py
streamlit run app.py
