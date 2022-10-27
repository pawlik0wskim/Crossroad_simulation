from multiprocessing import Process, Value, Array
import time

class Simulation:
    def __init__(self, id):
        self.id = id

    def simulate(self, seconds):
        print(f'{id} started simulation')
        time.sleep(seconds)
        print(f'{id} done')

if __name__ == '__main__':
    pass



