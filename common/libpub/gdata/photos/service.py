#!/usr/bin/env python
# -*-*- encoding: utf-8 -*-*-
#
# This is the service file for the Google Photo python client.
# It is used for higher level operations.
#
# $Id: service.py 107 2007-10-18 20:08:35Z havard.gulldahl $
#
# Copyright 2007 Håvard Gulldahl 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google PhotoService provides a human-friendly interface to
Google Photo (a.k.a Picasa Web) services[1].

It extends gdata.service.GDataService and as such hides all the
nasty details about authenticating, parsing and communicating with
Google Photos. 

[1]: http://code.google.com/apis/picasaweb/gdata.html

Example:
  import gdata.photos, gdata.photos.service
  pws = gdata.photos.service.PhotosService()
  pws.ClientLogin(username, password)
  #Get all albums
  albums = pws.GetAlbumFeed() 
  # Get all photos in second album
  photos = pws.GetPhotoFeed(albums.entry[1].GetPhotoFeedLink())
  # Get all tags for photos in second album and print them
  tags = pws.GetTagFeed(albums.entry[1].GetTagFeedLink())
  print [ tag.summary.text for tag in tags.entry ]
  # Get all comments for the first photos in list and print them
  comments = pws.GetCommentFeed(photos.entry[0].GetCommentFeedLink())
  print [ c.summary.text for c in comments.entry ]

  # Get a photo to work with
  photo = photos.entry[0]
  # Update metadata

  # Attributes from the <gphoto:*> namespace
  photo.summary.text = u'A nice view from my veranda'
  photo.title.text = u'Verandaview.jpg'

  # Attributes from the <media:*> namespace
  photo.media.keywords.text = u'Home, Long-exposure, Sunset' # Comma-separated

  # Adding attributes to media object
  photo.rotation = gdata.photos.Rotation(text='90') # Rotate 90 degrees clockwise

  # Submit modified photo object
  photo = pws.UpdatePhotoMetadata(photo)
  
  # Make sure you only modify the newly returned object, else you'll get versioning
  # errors. See Optimistic-concurrency

  # Add comment to a picture
  comment = pws.InsertComment(photo, u'I wish the water always was this warm')

  # Remove comment because it was silly
  print "*blush*"
  pws.Delete(comment.GetEditLink().href)

  pws.Logout()

"""

__author__ = u'havard@gulldahl.no'# (Håvard Gulldahl)' #BUG: api chokes on non-ascii chars in __author__
__license__ = 'Apache License v2'
__version__ = '0.5'


import sys, types, os.path
import libpub.gdata.service 
import libpub.gdata 
import libpub.atom.service 
import libpub.atom 
import time
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree

import libpub.gdata.photos 

UNKOWN_ERROR=1000

class GooglePhotosException(Exception):
  def __init__(self, response):

    self.args = response
    try:
      self.element_tree = ElementTree.fromstring(response['body'])
      self.error_code = int(self.element_tree[0].attrib['errorCode'])
      self.reason = self.element_tree[0].attrib['reason']
      self.invalidInput = self.element_tree[0].attrib['invalidInput']
    except:
      self.error_code = UNKOWN_ERROR


class PhotosService(libpub.gdata.service.GDataService):
  userUri = '/data/feed/api/user/%s'
  
  def __init__(self, email=None, password=None, 
    source=None, server='picasaweb.google.com', additional_headers=None):
    """ GooglePhotosService constructor.
      
    Arguments:
    email: string (optional) The e-mail address of the account to use for
           authentication.
    password: string (optional) The password of the account to use for
              authentication.
    source: string (optional) The name of the user's application.
    server: string (optional) The server the feed is hosted on.
    additional_headers: dict (optional) Any additional HTTP headers to be
                        transmitted to the service in the form of key-value
                        pairs.

    Returns:
    A PhotosService object used to communicate with the Google Photos
    service.
    """
    self.email = email
    self.client = source
    libpub.gdata.service.GDataService.__init__(self, email=self.email, password=password,
                                        service='lh2', source=source,
                                        server=server,
                                        additional_headers=additional_headers)
    
  def GetAlbumFeed(self, uri='/data/feed/api/user/default?kind=album'):
    """Get all albums for the given uri, defaults to all albums for the given user.

     The albums are ordered by the values of their `updated' elements,
     with the most recently updated entry appearing first in the feed.
    
    Arguments:
    uri: the uri to the album feed, e.g. `/data/feed/api/user/default?kind=album'
     
    Returns:
    libpub.gdata.photos.AlbumFeed

    See:
    http://code.google.com/apis/picasaweb/libpub.gdata.html#Get_Album_Feed_Manual
    """
    return libpub.gdata.photos.AlbumFeedFromString(str(self.Get(uri)))
              
  def GetPhotoFeed(self, uri):
    """Get all photos for the given uri.

    The photos are ordered by the values of their `updated' elements,
    with the most recently updated photo appearing first in the feed.

    Arguments:
    uri: the uri to the photo feed, e.g.
    `/data/feed/api/user/liz/album/NetherfieldPark?kind=photo'
    
    Returns:
    libpub.gdata.photos.PhotoFeed
    
    See:
    http://code.google.com/apis/picasaweb/libpub.gdata.html#Get_Photo_Feed_Manual
    """
    return libpub.gdata.photos.PhotoFeedFromString(str(self.Get(uri)))

  def GetTaggedPhotoFeed(self, tag, user='default'):
    """Get all photos belonging to a specific user that have a special tag (a.k.a. keyword)

    Arguments:
    tag: The tag you're looking for, e.g. `dog'
    user (optional): Whose images/videos you want to search, defaults to current user

    Returns:
    libpub.gdata.photos.PhotoFeed
    """
    uri = '/data/feed/api/user/default?kind=photo&tag=%s' % tag
    return self.GetPhotoFeed(uri)

  def GetCommunityPhotoFeed(self, query, limit=100):
    """Search through all public photos.
    This will look for matches in file names and image tags (a.k.a. keywords)

    Arguments:
    query: The string you're looking for, e.g. `vacation'
    limit (optional): Don't return more than `limit' hits, defaults to 100

    Returns:
    libpub.gdata.photos.PhotoFeed
    """
    uri='/data/feed/api/all?q=%s&max-results=%s' % (query, limit)
    return self.GetPhotoFeed(uri)

  def GetTagFeed(self, uri='/data/feed/api/user/default/?kind=tag'):
    """Get a feed of tags for a given uri.
    Returns a TagFeed for the current user by default.

    Arguments:
    uri: the uri to the tag feed, e.g. `/data/feed/api/user/liz/?kind=tag'

    Returns:
    libpub.gdata.photos.TagFeed
    """
    #uri='http://picasaweb.google.com/data/feed/api/user/default/?kind=tag'):
    #http://picasaweb.google.com/data/feed/projection/user/userID/?kind=kinds
    return libpub.gdata.photos.TagFeedFromString(str(self.Get(uri)))

  def GetCommentFeed(self, uri):
    """Get a feed of comments for a given uri.
    Returns a CommentFeed for the current user by default.

    Arguments:
    uri: the uri to the comment feed, e.g. `/data/feed/api/user/liz/?kind=comment'

    Returns:
    libpub.gdata.photos.CommentFeed
    """
    return libpub.gdata.photos.CommentFeedFromString(str(self.Get(uri)))

  def InsertAlbum(self, title, summary, location=None, access='public', commenting_enabled='true', timestamp=None):
    """Add an album.

    Needs authentication, see self.ClientLogin()

    Arguments:
    title: Album title 
    summary: Album summary / description
    access (optional): `private' or `public'. Public albums are searchable
      by everyone on the internet. Defaults to `public'
    commenting_enabled (optional): `true' or `false'. Defaults to `true'.
    timestamp (optional): A date and time for the album, in milliseconds since
      Unix epoch[1] UTC. Defaults to now.

    Returns:
    The newly created libpub.gdata.photos.AlbumEntry

    See:
    http://code.google.com/apis/picasaweb/gdata.html#Add_Album_Manual_Installed
    [1]: http://en.wikipedia.org/wiki/Unix_epoch
    """
    album = libpub.gdata.photos.AlbumEntry()
    album.category.append(libpub.atom.Category(term='http://schemas.google.com/photos/2007#album',
                                        scheme='http://schemas.google.com/g/2005#kind'))
    album.title = libpub.atom.Title(text=title, title_type='text')
    album.summary = libpub.atom.Summary(text=summary, summary_type='text')
    if location is not None:
      album.location = libpub.gdata.photos.Location(text=location)
    album.access = libpub.gdata.photos.Access(text=access)
    if commenting_enabled in ('true', 'false'):
      album.commentingEnabled = libpub.gdata.photos.CommentingEnabled(text=commenting_enabled)
    if timestamp is None:
      timestamp = '%i' % int(time.time() * 1000)
    album.timestamp = libpub.gdata.photos.Timestamp(text=timestamp)
    newAlbum = self.Post(album, self.userUri % self.email)
    return newAlbum

  def InsertPhoto(self, title, summary, album_uri, filename_or_handle,
      content_type='image/jpeg', keywords=None, client=None):
    """Add a photo.

    Needs authentication, see self.ClientLogin()

    Arguments:
    title: Photo title
    summary: Photo summary / description
    album_uri: Uri of the album where the photo should go
    filename_or_handle: A file-like object or file name where the image/video
      will be read from
    content_type (optional): Internet media type (a.k.a. mime type) of
      media object. Currently Google Photos supports these types:
       o image/bmp
       o image/gif
       o image/jpeg
       o image/png
       
      Images will be converted to jpeg on upload. Defaults to `image/jpeg'
    keywords (optional): a comma separated string of keywords (a.k.a. tags)
      to add to the image, e.g. `dog, vacation, happy'
    client (optional): Name of uploading client, if any
    
    Returns:
    The newly created gdata.photos.AlbumEntry

    See:
    http://code.google.com/apis/picasaweb/gdata.html#Add_Album_Manual_Installed
    [1]: http://en.wikipedia.org/wiki/Unix_epoch
    """
    ## TODO: Duck type the file object detection
    if type(filename_or_handle) in types.StringTypes: # it's a file name
      file_handle = file(filename_or_handle, 'r')
      size = os.path.getsize(filename_or_handle)
    else: 
      file_handle = filename_or_handle # it's a file-like resource 
      file_handle.seek(0) # rewind pointer to the start of the file
      size = file_handle.len
    photo = libpub.gdata.MediaSource(file_handle, content_type, size)
    metadata = libpub.gdata.photos.PhotoEntry()
    metadata.title=libpub.atom.Title(text=title)
    metadata.summary = libpub.atom.Summary(text=summary, summary_type='text')
    if keywords is not None:
      metadata.keywords = libpub.gdata.photos.media.Keywords(text=keywords)
    if client is None and self.client is not None:
      client = self.client
    metadata.client = libpub.gdata.photos.Client(text=client)
    metadata.category.append(libpub.atom.Category(scheme='http://schemas.google.com/g/2005#kind', 
                                    term = 'http://schemas.google.com/photos/2007#photo'))
    media = self.Post(metadata, album_uri, media_source=photo)
    return media

  def UpdatePhotoMetadata(self, photo):
    """Update a photo's metadata. 

     Needs authentication, see self.ClientLogin()

     You can update any or all of the following metadata properties:
      * <title>
      * <description>
      * <gphoto:checksum>
      * <gphoto:client>
      * <gphoto:rotation>
      * <gphoto:timestamp>
      * <gphoto:commentingEnabled>

      Arguments:
      photo: a gdata.photos.PhotoEntry object with updated elements

      Returns:
      The modified libpub.gdata.photos.PhotoEntry

      Example:
      p = GetPhotoFeed(uri)
      p.title.text = u'My new text'
      p.commentingEnabled.text = 'false'
      p = UpdatePhotoMetadata(p)

      It is important that you don't keep the old object around, once
      it has been updated. See
      http://code.google.com/apis/gdata/reference.html#Optimistic-concurrency
      """
    media = self.Put(photo, photo.GetEditLink().href)
    return media
  
  def UpdatePhotoBlob(self, photo, filename_or_handle, content_type = 'image/jpeg'):
    """Update a photo's binary data.

    Needs authentication, see self.ClientLogin()

    Arguments:
    photo: a libpub.gdata.photos.PhotoEntry that will be updated
    filename_or_handle:  A file-like object or file name where the image/video
      will be read from
    content_type (optional): Internet media type (a.k.a. mime type) of
      media object. Currently Google Photos supports these types:
       o image/bmp
       o image/gif
       o image/jpeg
       o image/png
    Images will be converted to jpeg on upload. Defaults to `image/jpeg'

    Returns:
    The modified libpub.gdata.photos.PhotoEntry

    Example:
    p = GetPhotoFeed(uri)
    p = UpdatePhotoBlob(p, '/tmp/newPic.jpg')

    It is important that you don't keep the old object around, once
    it has been updated. See
    http://code.google.com/apis/gdata/reference.html#Optimistic-concurrency
    """
    ## TODO: Duck type this (see InsertPhoto)
    if type(filename_or_handle) in types.StringTypes: # it's a file name
      file_handle = file(filename_or_handle, 'r')
      size = os.path.getsize(filename_or_handle)
    else: 
      file_handle = filename_or_handle # it's a file-like resource 
      file_handle.seek(0) # rewind pointer to the start of the file
      size = file_handle.len
    photoblob = libpub.gdata.MediaSource(file_handle, content_type, size)
    media = self.Put(photoblob, photo.GetEditMediaLink().href)
    return media

  def InsertTag(self, photo, tag):
    """Add a tag (a.k.a. keyword) to a photo.

    Needs authentication, see self.ClientLogin()

    Arguments:
    photo: The libpub.gdata.photos.PhotoEntry that is about to be tagged
    tag: The tag/keyword

    Returns:
    The new libpub.gdata.photos.TagEntry

    Example:
    p = GetPhotoFeed(uri)
    tag = InsertTag(p, 'Beautiful sunsets')

    """
    tag = libpub.gdata.photos.TagEntry(title=libpub.atom.Title(text=tag))
    res = self.Post(tag, photo.GetFeedLink().href)
    return res
                  
  def InsertComment(self, photo, comment):
    """Add a comment to a photo.

    Needs authentication, see self.ClientLogin()

    Arguments:
    photo: The libpub.gdata.photos.PhotoEntry that is about to be commented
    comment: The actual comment

    Returns:
    The new libpub.gdata.photos.CommentEntry

    Example:
    p = GetPhotoFeed(uri)
    tag = InsertComment(p, 'OOOH! I would have loved to be there. Who's that in the back?')

    """
    comment = libpub.gdata.photos.CommentEntry(content=libpub.atom.Content(text=comment))
    res = self.Post(comment, photo.GetPostLink().href)
    return res

def GetSmallestThumbnail(media_thumbnail_list):
  """Helper function to get the smallest thumbnail of a list of
    libpub.gdata.photos.media.Thumbnail.
  Returns libpub.gdata.photos.media.Thumbnail """
  r = {}
  for thumb in media_thumbnail_list:
      r[int(thumb.width)*int(thumb.height)] = thumb
  return r[r.keys()[0]]

def ConvertAtomTimestampToEpoch(timestamp):
  """Helper function to convert a timestamp string, for instance
    from atom:updated or atom:published, to milliseconds since Unix epoch
    (a.k.a. POSIX time).

    `2007-07-22T00:45:10.000Z' -> """
  return time.mktime(time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.000Z')) ## TODO: Timezone aware
