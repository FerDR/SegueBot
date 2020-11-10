import time
import datetime
import SegueBot as SB
import numpy as np

while True:
    date = datetime.datetime.utcnow()
    if date.weekday()==0 and date.hour<1:
        SB.main()
    else:
        SB.main(np.load('chain'))
    time.sleep(60*60)
