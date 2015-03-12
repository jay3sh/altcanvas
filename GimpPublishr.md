# Publish to Flickr, Picasaweb right from Gimp! #

### Drop this plugin into your Gimp plugin directory and publish your images to your **Flickr** or **Picasaweb** account right from Gimp ###

Download the latest (0.5) version from [Downloads ](http://code.google.com/p/altcanvas/downloads/list)

Please email you problems to jayeshsalvi AT gmail DOT com. Your input is highly appreciated.

**Note:** If you do not see the "Publish to web" option in menu even after deploying the plugin and do not get any crashes either, make sure that Gimp python is installed. One check to verify that is checking existence of python directory in your Gimp installation directory (On windows C:\Program Files\GIMP-2.0\lib\gimp\2.0\python, on Linuxes /usr/lib(64)/gimp/2.0/python/). If it's not installed the plugin never gets invoked (even though it shows up in startup splash screen) so it cannot report that problem

[Changelog and Known issues](http://code.google.com/p/altcanvas/wiki/PublishrChangelog)

**Installation:**

  1. Download publishr-

&lt;version&gt;

.tar.gz or publishr-

&lt;version&gt;

.zip
  1. Untar/Unzip the contents of this file into your Gimp plugins directory in your home directory:
    * For linux this path will be $HOME/.gimp-

&lt;version&gt;

/plug-ins/
    * For windows this path will be something like C:\Document and Settings\

&lt;username&gt;

\.gimp-

&lt;version&gt;

\plug-ins\
  1. Restart Gimp if it's already running.


**Usage:**

_**Flickr:**_
  * Once you are ready to publish your image to Flickr, save the image you want to publish in JPG or GIF format.
  * Invoke **File -> Publish to Flickr**
> > ![http://farm3.static.flickr.com/2098/2055674973_6d7e4cc10f_o_d.jpg](http://farm3.static.flickr.com/2098/2055674973_6d7e4cc10f_o_d.jpg)
  * If this is your first usage or if you had signed out during last usage, you will be asked to "Sign into Flickr!"
> > ![http://farm3.static.flickr.com/2052/2070206555_612fb216ec_o_d.jpg](http://farm3.static.flickr.com/2052/2070206555_612fb216ec_o_d.jpg)
  * Once you click on "Sign in", you will be presented with a URL and a button to proceed further.
> > ![http://farm3.static.flickr.com/2094/2055672961_039f571c1b_o_d.jpg](http://farm3.static.flickr.com/2094/2055672961_039f571c1b_o_d.jpg)
  * Open the URL in your browser. If you are not logged into your Flickr account, you will be asked to do so by Flickr at this point.
  * Once you have logged into your Flickr account, you will have to authorize **"altcanvas"** so that it can upload to your account.
  * Click on **"OK, I'll allow it"** and then press the button on the dialog to proceed further.
  * You will be presented with Image upload dialog, where you can fill in Title and other details
> > ![http://farm3.static.flickr.com/2381/2055678623_d6c0e3c9e4_o_d.jpg](http://farm3.static.flickr.com/2381/2055678623_d6c0e3c9e4_o_d.jpg)
  * Hit upload and your are done!
  * Henceforth (until you sign out of Flickr) you will see **"Publish to Flickr"** button which will directly lead you to above Image upload dialog.
> > ![http://farm3.static.flickr.com/2190/2072631979_8846534aab_o_d.jpg](http://farm3.static.flickr.com/2190/2072631979_8846534aab_o_d.jpg)

_**Picasaweb**_
  * After invoking the plugin click on **"Sign into Picasaweb"**
  * You will be led to a login screen where you can enter your Picasaweb (i.e. Google) username and password info. (If you are hesitant about entering your accound info, note that your password will NOT be stored or transmitted over network in plaintext. It is passed to Google's GData library which transmits the password over encrypted SSL connection)
> > ![http://farm3.static.flickr.com/2249/2073423010_1144cdba9e_o_d.jpg](http://farm3.static.flickr.com/2249/2073423010_1144cdba9e_o_d.jpg)
  * Once you are successfully signed into Picasaweb, you will be led to the upload screen.
> > ![http://farm3.static.flickr.com/2171/2072643209_2adf238e49_o_d.jpg](http://farm3.static.flickr.com/2171/2072643209_2adf238e49_o_d.jpg)
  * Some fields are not yet supported in this version. They will be enabled in future versions.

**Debug tip**

> If you don't see the 'Publish to web' item in drop down menu - then Gimp didn't load the publish plugin successfully. This may happen if you haven't placed the plugin in right location, or Gimp incurrend an exception while loading the plugin. This can be found by running Gimp from command line with verbose option - **'gimp --verbose'**. This will tell if and why loading of the plugin failed.