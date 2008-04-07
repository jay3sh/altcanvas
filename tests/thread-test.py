

import thread
import time

(UNBLOCKED,BLOCKED) = range(2)

class App:
    input = UNBLOCKED
    def second_thread(self):
        self.input = BLOCKED
        
        time.sleep(5)
        print 'Unblocking'
        
        self.input = UNBLOCKED
        
        
    def run(self):
        print self.input
        thread.start_new_thread(self.second_thread, ())
        
        while True:
            print self.input 
            time.sleep(1)
        
if __name__ == '__main__':
    App().run()
    