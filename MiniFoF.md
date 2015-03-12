MiniFoF is a fork of Frets-on-Fire 1.3.110. It is a trimmed version to run on handheld devices like Nokia tablets.


### Steps to try MiniFoF on n810 ###

Perform the following steps on your n810 device.

```
# Minimum prerequisite packages - python2.5-pygame, python2.5-numeric, ogg-support (optional - more on it later)
# Download the source tarball
wget http://altcanvas.googlecode.com/files/minifof-0.0.1.tar.gz

# Download Frets on Fire 1.3.110. This is needed for the data files. The media files are not distributed under GPL, so better download them from original source
wget http://downloads.sourceforge.net/fretsonfire/FretsOnFire-1.3.110.tar.gz?use_mirror=jaist

# Untar source tarball
tar xzf minifof-0.0.1.tar.gz

# Untar Frets on Fire tarball
tar xzf FretsOnFire-1.3.110.tar.gz

# Copy the data directory to minifof
cp -r "Frets on Fire-1.3.110/data" minifof/

# Run FretsOnFire.py
cd minifof/src
python2.5 FretsOnFire.py

```

FoF media files are in ogg format. I however could not get pygame to run them in Diablo scratchbox even with the ogg-support package. If you know how to fix it, let me know. Otherwise a workaround is to convert all ogg files to .wav files and make a one-line change in Config.py to do the switch.

ogg-to-wav conversion can be done on desktop using ffmpeg
```
cd <FoF directory>/data

for f in `find . -name "*.ogg"`
do
   WAV_NAME=`echo $f | sed 's/ogg/wav/g'`
   ffmpeg -i $f $WAV_NAME
done

# Copy these wav files onto n810. Note that they are huge in size. So allow enough space.

# Open minifof/src/Config.py
# Change AUDIO_FORMAT from "ogg" to "wav"
```