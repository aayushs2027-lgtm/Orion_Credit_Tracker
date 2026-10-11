import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.model import train
if __name__=='__main__':
    result=train()
    print('Trained version',result['version'],'selected',result['selected'])
