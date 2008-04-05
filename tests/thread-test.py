

import thread
import time

(UNBLOCKED,BLOCKED) = range(2)

i = UNBLOCKED

def second_thread(sleeptime):
    global i
    i = BLOCKED
    
    time.sleep(sleeptime)
    print 'Unblocking'
    
    i = UNBLOCKED
    
    
def main():
    global i
    print i
    thread.start_new_thread(second_thread, (5,))
    
    while True:
        print i
        time.sleep(1)
        
if __name__ == '__main__':
    main()
    