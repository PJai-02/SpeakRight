@echo off
REM Activate Conda base environment
call C:\ProgramData\Miniconda3\Scripts\activate.bat

REM Activate your specific Conda environment
call conda activate pro_ai

REM Navigate to your project directory
cd /d D:\AI-Based-Pronunciation-Evaluation-System

REM Running Web App
python webApp.py
