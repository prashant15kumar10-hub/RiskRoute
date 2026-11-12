@echo off
python train.py
python evaluate_counterfactuals.py
streamlit run app.py
