
env = Environment()

######
# libinface.so
######

# Configuration
conf = Configure(env)
if not conf.CheckLib('altsvg'):
    print "Didn't find libaltsvg"
    Exit(1)
env = conf.Finish()

env.ParseConfig("pkg-config --cflags --libs libaltsvg")

# Build

env.SharedLibrary(target='inkface',
                source=['inkface.c'])
                


# Get our configuration options:
opts = Options('wm.conf') # Change wm to the name of your app
opts.Add(PathOption('PREFIX', 'Directory to install under', '/usr'))
opts.Update(env)
opts.Save('wm.conf', env) # Save, so user doesn't have to 
                          # specify PREFIX every time

Help(opts.GenerateHelpText(env))


# Install
# Here are our installation paths:
idir_prefix = '$PREFIX'
idir_lib    = '$PREFIX/lib'
idir_bin    = '$PREFIX/bin'
idir_inc    = '$PREFIX/include'
idir_data   = '$PREFIX/share'
Export('env idir_prefix idir_lib idir_bin idir_inc idir_data')

env.Install(idir_lib, ['libinkface.so'])
env.Install(idir_inc, ['inkface.h'])
install = env.Alias('install', idir_prefix)


