"""Read-only round-three replay, with output redirected to a new filename."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'round3'))
import bagging
original=bagging.f.write_csv
bagging.f.write_csv=lambda p,name:original(p,'submission_round4_reference_reproduced.csv')
if __name__=='__main__':bagging.reproduce()
