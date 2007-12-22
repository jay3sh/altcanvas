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
PUB_COMMON_DIR=/home/jayesh/trunk/altcanvas/common/libpub
PUB_GIMP_DIR=/home/jayesh/trunk/altcanvas/gimp/publishr
PUB_INKSCAPE_DIR=/home/jayesh/trunk/altcanvas/inkscape/publishr
FILTER="--exclude '.*' --exclude '*.pyc'"

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
		tar czf publishr-gimp-0.3.tar.gz *.py libpub
		zip -r publishr-gimp-0.3.zip *.py libpub
	)
	mv $TMP_BLDDIR/publishr-gimp-0.3.{tar.gz,zip} .

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
		tar czf publishr-inkscape-0.3.tar.gz *.py *.inx libpub
		zip -r publishr-inkscape-0.3.zip *.py *.inx libpub
	)
	mv $TMP_BLDDIR/publishr-inkscape-0.3.{tar.gz,zip} .
}

case $PACKAGE in
	"gimp-publishr")
		make_gimp_publishr;
		;;
	"inkscape-publishr")
		make_inkscape_publishr;
		;;
	"publishr")
		make_gimp_publishr;
		make_inkscape_publishr;
		;;
esac

