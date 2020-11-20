import time
import datetime
import SegueBot as SB
import numpy as np
import os
from importlib import reload

while True:
    reload(SegueBot)
    date = datetime.datetime.utcnow()
    if date.weekday()==0 and date.hour<1 or not os.path.exists('chain.npy'):
        SB.main()
    else:
        SB.main(np.load('chain'))
    time.sleep(60*60)
