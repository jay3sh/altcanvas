#!/bin/bash

usage()
{
	echo "Usage: build.sh [-p PACKAGE_NAME]"
	echo "   -p  Package to build "
	echo "       (valid objects: gimp-publishr,"
    echo "                       inkscape-publishr,"
    echo "                       maemo-publishr,"
    echo "                       publishr)"
}


TMP_BLDDIR=/tmp/altcanvas-build
BLDDIR=`pwd`/packages
SRCDIR=`pwd`
PUB_COMMON_DIR=$SRCDIR/common/libpub
PUB_GIMP_DIR=$SRCDIR/gimp/publishr
PUB_INKSCAPE_DIR=$SRCDIR/inkscape/publishr
FILTER="--exclude '.*' --exclude '*.pyc'"
VERSION=0.5.0

REPO_ROOT=/tmp/reporoot

export PYTHON=/usr/bin/python2.5

clean()
{
    rm -rf $BLDDIR
}

make_gimp_publishr()
{
	rm -rf $TMP_BLDDIR
	mkdir $TMP_BLDDIR

	cp -r $PUB_COMMON_DIR $TMP_BLDDIR
	cp $PUB_GIMP_DIR/publishr.py $TMP_BLDDIR
	(
		cd $TMP_BLDDIR;
		find . | grep '\.svn' | xargs rm -rf 
		find . | grep '\.pyc$' | xargs rm -rf 
		tar czfp publishr-gimp-$VERSION.tar.gz *.py libpub
		zip -q -r publishr-gimp-$VERSION.zip *.py libpub
	)

	if ! [ -d $BLDDIR ]; then
		mkdir $BLDDIR;
	fi

	mv $TMP_BLDDIR/publishr-gimp-$VERSION.{tar.gz,zip} $BLDDIR

}

make_inkscape_publishr()
{
	rm -rf $TMP_BLDDIR
	mkdir $TMP_BLDDIR

	cp -r $PUB_COMMON_DIR $TMP_BLDDIR
	cp $PUB_INKSCAPE_DIR/publishr.py $TMP_BLDDIR
	cp $PUB_INKSCAPE_DIR/publishr.inx $TMP_BLDDIR
	(
		cd $TMP_BLDDIR;
		find . | grep '\.svn' | xargs rm -rf 
		find . | grep '\.pyc$' | xargs rm -rf 
		tar czfp publishr-inkscape-$VERSION.tar.gz *.py *.inx libpub
		zip -q -r publishr-inkscape-$VERSION.zip *.py *.inx libpub
	)

	if ! [ -d $BLDDIR ]; then
		mkdir $BLDDIR;
	fi

	mv $TMP_BLDDIR/publishr-inkscape-$VERSION.{tar.gz,zip} $BLDDIR
}

make_maemo_publishr()
{
	rm -rf $TMP_BLDDIR
	mkdir $TMP_BLDDIR

	(
		cd $TMP_BLDDIR
		ln -s $SRCDIR/install/setup.py ./setup.py
		ln -s $SRCDIR/install/bdist_debian.py ./bdist_debian.py
		ln -s $SRCDIR/common/libpub ./libpub
		ln -s $SRCDIR/maemo/publishr/publishr.py ./publishr.py
		ln -s $SRCDIR/maemo/publishr/publishr-start.py ./publishr-start.py
		ln -s $SRCDIR/install/publishr.desktop ./publishr.desktop

		$PYTHON setup.py bdist_debian || exit

		if ! [ -d $BLDDIR ]; then
			mkdir $BLDDIR;
		fi

		mv dist/*.deb $BLDDIR/
	)

	#rm -rf $TMP_BLDDIR

}

make_inklib()
{
	rm -rf $TMP_BLDDIR
	mkdir $TMP_BLDDIR

	(
		cd $TMP_BLDDIR
        ln -s $SRCDIR/inkface/inklib/python/setup.py ./setup.py
        ln -s $SRCDIR/install/bdist_debian.py ./bdist_debian.py
        ln -s $SRCDIR/inkface/inklib/python/inklib ./inklib

		$PYTHON setup.py bdist_debian || exit

		if ! [ -d $BLDDIR ]; then
			mkdir $BLDDIR;
		fi

		mv dist/*.deb $BLDDIR/
    )

	rm -rf $TMP_BLDDIR
}
make_twitink()
{
	rm -rf $TMP_BLDDIR
	mkdir $TMP_BLDDIR

	(
		cd $TMP_BLDDIR
        ln -s $SRCDIR/inkface/apps/twit/setup.py ./setup.py
        ln -s $SRCDIR/install/bdist_debian.py ./bdist_debian.py

        ln -s $SRCDIR/inkface/apps/twit/twitink.desktop ./twitink.desktop
        ln -s $SRCDIR/inkface/apps/twit/twitink ./twitink

        ln -s $SRCDIR/inkface/apps/twit/twit.py ./twit.py

        ln -s $SRCDIR/inkface/apps/twit/login.svg ./login.svg
        ln -s $SRCDIR/inkface/apps/twit/public.svg ./public.svg
        ln -s $SRCDIR/inkface/apps/twit/keyboard-lite.svg ./keyboard-lite.svg

		$PYTHON setup.py bdist_debian || exit

		if ! [ -d $BLDDIR ]; then
			mkdir $BLDDIR;
		fi

		mv dist/*.deb $BLDDIR/
    )

	rm -rf $TMP_BLDDIR
}

make_altplayer()
{
	rm -rf $TMP_BLDDIR
	mkdir $TMP_BLDDIR

	(
		cd $TMP_BLDDIR

        ln -s $SRCDIR/altplayer/setup.py ./setup.py
        ln -s $SRCDIR/install/bdist_debian.py ./bdist_debian.py
        ln -s $SRCDIR/altplayer/altplayerlib ./altplayerlib
        ln -s $SRCDIR/altplayer/altplayer.py ./altplayer.py
        ln -s $SRCDIR/altplayer/altplayer.desktop ./altplayer.desktop

		$PYTHON setup.py bdist_debian || exit

		if ! [ -d $BLDDIR ]; then
			mkdir $BLDDIR;
		fi

		mv dist/*.deb $BLDDIR/
    )

	rm -rf $TMP_BLDDIR

}

make_altmaemo_publishr()
{
	rm -rf $TMP_BLDDIR
	mkdir $TMP_BLDDIR

	(
		cd $TMP_BLDDIR
		ln -s $SRCDIR/install/alt-setup.py ./setup.py
		ln -s $SRCDIR/install/bdist_debian.py ./bdist_debian.py
		ln -s $SRCDIR/common/libpub ./libpub
		ln -s $SRCDIR/maemo/publishr-prime/publishrX.py ./altpublishr.py
		ln -s $SRCDIR/install/altpublishr.desktop ./altpublishr.desktop

        for img in altpublishr note globe dropdown
        do
		    ln -s $SRCDIR/install/$img.png ./$img.png
        done

		$PYTHON setup.py bdist_debian || exit

		if ! [ -d $BLDDIR ]; then
			mkdir $BLDDIR;
		fi

		mv dist/*.deb $BLDDIR/
	)

	rm -rf $TMP_BLDDIR

    #scp $BLDDIR/altpublishr-maemo*deb root@192.168.1.100:/root/

    #ssh root@192.168.1.100 "(dpkg --purge altpublishr-maemo; cd /root/; dpkg -i altpublishr-maemo*deb)"

}

make_canvasx()
{
    (
        cd altX;
        #dpkg-buildpackage -rfakeroot
        dpkg-buildpackage -rfakeroot -sa -S -i
        scp ../canvasx*deb root@192.168.1.100:/root/

        ssh root@192.168.1.100 \
        "(dpkg --purge canvasx; cd /root/; dpkg -i canvasx*deb; rm -f canvasx*deb)"
    )
}

make_inkface_python()
{
    (
        cd inkface;
        scons-1.1.0 -c 2>/dev/null
        #scons -Q native-debian
        scons-1.1.0 -Q python-debian 2>/dev/null
        mv *.deb $BLDDIR/
    )
}


make_libaltsvg()
{
    (
        HOST_ARCH=`dpkg --print-architecture`
        cd libaltsvg;
        sed "s/@ARCH@/$HOST_ARCH/g" debian/control.in > debian/control
        dpkg-buildpackage -rfakeroot 
        mv ../libaltsvg*deb ../packages/
        #scp ../inkface*deb root@192.168.1.100:/root/

        #ssh root@192.168.1.100 \
        #"(dpkg --purge inkface; cd /root/; dpkg -i inkface*deb; rm -f inkface*deb)"
    )

}

die()
{
    echo $1
    exit 1
}

make_stackless()
{
    VANILLA_STACKLESS_ARCHIVE=stackless-252-export.tar.bz2
    VANILLA_STACKLESS_DIR=stackless-2.5.2-r63812
    VANILLA_STACKLESS_ARCHIVE_URL=http://www.stackless.com/binaries/$VANILLA_STACKLESS_ARCHIVE
    (
        cd stackless;
        
        if [ ! -f $VANILLA_STACKLESS_ARCHIVE ]
        then
            wget $VANILLA_STACKLESS_ARCHIVE_URL || die "Failed to download stackless"
        fi

        echo "Cleaning old source"
        rm -rf $VANILLA_STACKLESS_DIR

        echo "Extracting vanilla source $VANILLA_STACKLESS_ARCHIVE"
        tar xjf $VANILLA_STACKLESS_ARCHIVE || die "Failed to extract stackless archive"

        patch -p0 < maemo-sb.patch || die "Failed to patch vanilla stackless source"

        cd $VANILLA_STACKLESS_DIR || dir "Failed to change into vanila source dir"

        ln -s ../debian ./debian
        ln -s ../autogen.sh ./autogen.sh

        dpkg-buildpackage -rfakeroot

        #autoreconf
        #./configure --prefix=/tmp/usr || die "Build (configure) failed"
        #make || die "Build (make) failed"

    )
}

build_repo()
{
    rm -rf $REPO_ROOT && mkdir -p $REPO_ROOT

    mkdir $REPO_ROOT/dists
    mkdir $REPO_ROOT/dists/testing
    mkdir $REPO_ROOT/dists/testing/main
    mkdir $REPO_ROOT/dists/testing/main/binary-armel

    cp $BLDDIR/*deb $REPO_ROOT/dists/testing/main/binary-armel/

    cd $REPO_ROOT/dists/testing/main
    dpkg-scanpackages binary-armel /dev/null | \
        gzip -9c > binary-armel/Packages.gz

    mv binary-armel/Packages.gz $BLDDIR/

    rm -rf $REPO_ROOT 
}

if [ "$1" = "" ]; then
	usage
	exit 1
fi

while getopts "p:hc" options; do
	case $options in
		p) PACKAGE=$OPTARG;;
        c) clean;
		   exit 1;;
		h) usage;
		   exit 1;;
		*) usage
		   exit 1;;
	esac
done

PACKAGE=`echo $PACKAGE | sed 's/,/ /g'`

for PKG in $PACKAGE
do

case $PKG in
	"gimp-publishr")
		make_gimp_publishr;
		;;
	"inkscape-publishr")
		make_inkscape_publishr;
		;;
	"maemo-publishr")
		make_altmaemo_publishr;
		;;
	"publishr")
		make_gimp_publishr;
		make_inkscape_publishr;
		make_maemo_publishr;
        ;;
    "canvasx")
        make_canvasx;
		;;
    "inkface-python")
        make_inkface_python;
        ;;
    "libaltsvg")
        make_libaltsvg;
        ;;
    "altplayer")
        make_altplayer;
        ;;
    "stackless")
        make_stackless;
        ;;
     "inklib")
        make_inklib;
        ;;
     "twitink")
        make_twitink;
        ;;
     "debrepo")
        build_repo;
        ;;
esac

done
