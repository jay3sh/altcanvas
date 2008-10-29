import simpy

for i in range(1,100):
    f = simpy.create_foo()
    print f.i
