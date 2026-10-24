"""Regenerate strict-audit, candidate, uncertainty and measured usage reports."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluation.candidate_reports import main

if __name__=='__main__': main()
