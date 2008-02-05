#!/bin/bash


usage()
{
	echo "Usage: build.sh [-p PACKAGE_NAME]"
	echo "   -p  Package to build "
	echo "       (valid objects: gimp-publishr,inkscape-publishr)"
}

while getopts "p:h" options; do
	case $options in
		p) PACKAGE=$OPTARG;;
		h) usage;
         exit 1;;
		*) echo $usage
			exit 1;;
	esac
done

TMP_BLDDIR=/tmp/publishr-build
BLDDIR=$HOME/trunk/altcanvas/packages
SRCDIR=$HOME/trunk/altcanvas
PUB_COMMON_DIR=$SRCDIR/common/libpub
PUB_GIMP_DIR=$SRCDIR/gimp/publishr
PUB_INKSCAPE_DIR=$SRCDIR/inkscape/publishr
FILTER="--exclude '.*' --exclude '*.pyc'"
VERSION=0.4.0

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

		python setup.py bdist_debian || exit

		mv dist/*.deb $BLDDIR/
	)

	#rm -rf $TMP_BLDDIR

}

case $PACKAGE in
	"gimp-publishr")
		make_gimp_publishr;
		;;
	"inkscape-publishr")
		make_inkscape_publishr;
		;;
	"maemo-publishr")
		make_maemo_publishr;
		;;
	"publishr")
		make_gimp_publishr;
		make_inkscape_publishr;
		;;
esac

