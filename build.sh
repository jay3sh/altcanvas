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
        dpkg-buildpackage -rfakeroot
        scp ../canvasx*deb root@192.168.1.100:/root/

        ssh root@192.168.1.100 \
        "(dpkg --purge canvasx; cd /root/; dpkg -i canvasx*deb; rm -f canvasx*deb)"
    )
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

case $PACKAGE in
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
    "altplayer")
        make_altplayer;
        ;;
esac

