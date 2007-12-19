# -*-*- encoding: utf-8 -*-*-
#
# This is the base file for the PicasaWeb python client.
# It is used for lower level operations.
#
# $Id: __init__.py 104 2007-10-18 19:23:59Z havard.gulldahl $
#
# Copyright 2007 Håvard Gulldahl 
# Portions (C) 2006 Google Inc.
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

"""This module provides a pythonic, gdata-centric interface to Google Photos
(a.k.a. Picasa Web Services.

It is modelled after the gdata/* interfaces from the gdata-python-client
project[1] by Google. 

You'll find the user-friendly api in photos.service. Please see the
documentation or live help() system for available methods.

[1]: http://gdata-python-client.googlecode.com/

  """

__author__ = u'havard@gulldahl.no'# (Håvard Gulldahl)' #BUG: api chokes on non-ascii chars in __author__
__license__ = 'Apache License v2'


try:
  from xml.etree import cElementTree as ElementTree
except ImportError:
  try:
    import cElementTree as ElementTree
  except ImportError:
    from elementtree import ElementTree
import libpub.atom as atom
import libpub.gdata as gdata

import media,exif, geo # importing google photo submodules

# XML namespaces which are often used in Google Photo elements
PHOTOS_NAMESPACE = 'http://schemas.google.com/photos/2007'
PHOTOS_TEMPLATE = '{http://schemas.google.com/photos/2007}%s'
MEDIA_NAMESPACE = 'http://search.yahoo.com/mrss/'
MEDIA_TEMPLATE = '{http://search.yahoo.com/mrss/}%s'
EXIF_NAMESPACE = 'http://schemas.google.com/photos/exif/2007'
OPENSEARCH_NAMESPACE = 'http://a9.com/-/spec/opensearchrss/1.0/'
GEO_NAMESPACE = 'http://www.w3.org/2003/01/geo/wgs84_pos#'
GML_NAMESPACE = 'http://www.opengis.net/gml'
GEORSS_NAMESPACE = 'http://www.georss.org/georss'
PHEED_NAMESPACE = 'http://www.pheed.com/pheed/'
BATCH_NAMESPACE = 'http://schemas.google.com/gdata/batch'


class PhotosBaseElement(atom.AtomBase):
  """Base class for elements in the PHOTO_NAMESPACE. To add new elements,
  you only need to add the element tag name to self._tag
  """
  
  _tag = ''
  _namespace = PHOTOS_NAMESPACE
  _children = atom.AtomBase._children.copy()
  _attributes = atom.AtomBase._attributes.copy()

  def __init__(self, name=None, extension_elements=None,
      extension_attributes=None, text=None):
    self.name = name
    self.text = text
    self.extension_elements = extension_elements or []
    self.extension_attributes = extension_attributes or {}
  #def __str__(self):
    #return str(self.text)
  #def __unicode__(self):
    #return unicode(self.text)
  def __int__(self):
    return int(self.text)
  def bool(self):
    return self.text == 'true'

class PhotosBaseFeed(gdata.GDataFeed, gdata.LinkFinder):
  _tag = 'feed'
  _namespace = atom.ATOM_NAMESPACE
  _children = gdata.GDataFeed._children.copy()
  _attributes = gdata.GDataFeed._attributes.copy()
    
  def __init__(self, author=None, category=None, contributor=None,
               generator=None, icon=None, atom_id=None, link=None, logo=None,
               rights=None, subtitle=None, title=None, updated=None,
               entry=None, total_results=None, start_index=None,
               items_per_page=None, extension_elements=None,
               extension_attributes=None, text=None):
    gdata.GDataFeed.__init__(self, author=author, category=category,
                             contributor=contributor, generator=generator,
                             icon=icon,  atom_id=atom_id, link=link,
                             logo=logo, rights=rights, subtitle=subtitle,
                             title=title, updated=updated, entry=entry,
                             total_results=total_results,
                             start_index=start_index,
                             items_per_page=items_per_page,
                             extension_elements=extension_elements,
                             extension_attributes=extension_attributes,
                             text=text)


class Access(PhotosBaseElement):
  "The Google Photo `Access' element"
  
  _tag = 'access'
def AccessFromString(xml_string):
  return atom.CreateClassFromXMLString(Access, xml_string)

class Albumid(PhotosBaseElement):
  "The Google Photo `Albumid' element"
  
  _tag = 'albumid'
def AlbumidFromString(xml_string):
  return atom.CreateClassFromXMLString(Albumid, xml_string)

class BytesUsed(PhotosBaseElement):
  "The Google Photo `BytesUsed' element"
  
  _tag = 'bytesUsed'
def BytesUsedFromString(xml_string):
  return atom.CreateClassFromXMLString(BytesUsed, xml_string)

class Client(PhotosBaseElement):
  "The Google Photo `Client' element"
  
  _tag = 'client'
def ClientFromString(xml_string):
  return atom.CreateClassFromXMLString(Client, xml_string)

class Checksum(PhotosBaseElement):
  "The Google Photo `Checksum' element"
  
  _tag = 'checksum'
def ChecksumFromString(xml_string):
  return atom.CreateClassFromXMLString(Checksum, xml_string)

class CommentCount(PhotosBaseElement):
  "The Google Photo `CommentCount' element"
  
  _tag = 'commentCount'
def CommentCountFromString(xml_string):
  return atom.CreateClassFromXMLString(CommentCount, xml_string)

class CommentingEnabled(PhotosBaseElement):
  "The Google Photo `CommentingEnabled' element"
  
  _tag = 'commentingEnabled'
def CommentingEnabledFromString(xml_string):
  return atom.CreateClassFromXMLString(CommentingEnabled, xml_string)

class Height(PhotosBaseElement):
  "The Google Photo `Height' element"
  
  _tag = 'height'
def HeightFromString(xml_string):
  return atom.CreateClassFromXMLString(Height, xml_string)

class Id(PhotosBaseElement):
  "The Google Photo `Id' element"
  
  _tag = 'id'
def IdFromString(xml_string):
  return atom.CreateClassFromXMLString(Id, xml_string)

class Location(PhotosBaseElement):
  "The Google Photo `Location' element"
  
  _tag = 'location'
def LocationFromString(xml_string):
  return atom.CreateClassFromXMLString(Location, xml_string)

class MaxPhotosPerAlbum(PhotosBaseElement):
  "The Google Photo `MaxPhotosPerAlbum' element"
  
  _tag = 'maxPhotosPerAlbum'
def MaxPhotosPerAlbumFromString(xml_string):
  return atom.CreateClassFromXMLString(MaxPhotosPerAlbum, xml_string)

class Name(PhotosBaseElement):
  "The Google Photo `Name' element"
  
  _tag = 'name'
def NameFromString(xml_string):
  return atom.CreateClassFromXMLString(Name, xml_string)

class Nickname(PhotosBaseElement):
  "The Google Photo `Nickname' element"
  
  _tag = 'nickname'
def NicknameFromString(xml_string):
  return atom.CreateClassFromXMLString(Nickname, xml_string)

class Numphotos(PhotosBaseElement):
  "The Google Photo `Numphotos' element"
  
  _tag = 'numphotos'
def NumphotosFromString(xml_string):
  return atom.CreateClassFromXMLString(Numphotos, xml_string)

class Numphotosremaining(PhotosBaseElement):
  "The Google Photo `Numphotosremaining' element"
  
  _tag = 'numphotosremaining'
def NumphotosremainingFromString(xml_string):
  return atom.CreateClassFromXMLString(Numphotosremaining, xml_string)

class Position(PhotosBaseElement):
  "The Google Photo `Position' element"
  
  _tag = 'position'
def PositionFromString(xml_string):
  return atom.CreateClassFromXMLString(Position, xml_string)

class Photoid(PhotosBaseElement):
  "The Google Photo `Photoid' element"
  
  _tag = 'photoid'
def PhotoidFromString(xml_string):
  return atom.CreateClassFromXMLString(Photoid, xml_string)

class Quotacurrent(PhotosBaseElement):
  "The Google Photo `Quotacurrent' element"
  
  _tag = 'quotacurrent'
def QuotacurrentFromString(xml_string):
  return atom.CreateClassFromXMLString(Quotacurrent, xml_string)

class Quotalimit(PhotosBaseElement):
  "The Google Photo `Quotalimit' element"
  
  _tag = 'quotalimit'
def QuotalimitFromString(xml_string):
  return atom.CreateClassFromXMLString(Quotalimit, xml_string)

class Rotation(PhotosBaseElement):
  "The Google Photo `Rotation' element"
  
  _tag = 'rotation'
def RotationFromString(xml_string):
  return atom.CreateClassFromXMLString(Rotation, xml_string)

class Size(PhotosBaseElement):
  "The Google Photo `Size' element"
  
  _tag = 'size'
def SizeFromString(xml_string):
  return atom.CreateClassFromXMLString(Size, xml_string)

class Thumbnail(PhotosBaseElement):
  "The Google Photo `Thumbnail' element (Not to be confused with the <media:thumbnail> element."
  
  _tag = 'thumbnail'
def ThumbnailFromString(xml_string):
  return atom.CreateClassFromXMLString(Thumbnail, xml_string)

class Timestamp(PhotosBaseElement):
  "The Google Photo `Timestamp' element"
  
  _tag = 'timestamp'
def TimestampFromString(xml_string):
  return atom.CreateClassFromXMLString(Timestamp, xml_string)

class User(PhotosBaseElement):
  "The Google Photo `User' element"
  
  _tag = 'user'
def UserFromString(xml_string):
  return atom.CreateClassFromXMLString(User, xml_string)

class Version(PhotosBaseElement):
  "The Google Photo `Version' element"
  
  _tag = 'version'
def VersionFromString(xml_string):
  return atom.CreateClassFromXMLString(Version, xml_string)

class Width(PhotosBaseElement):
  "The Google Photo `Width' element"
  
  _tag = 'width'
def WidthFromString(xml_string):
  return atom.CreateClassFromXMLString(Width, xml_string)

class Weight(PhotosBaseElement):
  "The Google Photo `Weight' element"
  
  _tag = 'weight'
def WeightFromString(xml_string):
  return atom.CreateClassFromXMLString(Weight, xml_string)

class AlbumEntry(gdata.GDataEntry):
  """A Google Photo Album meta Entry flavor of an Atom Entry

  Notes:
    To avoid name clashes, and to create a more sensible api, some
    objects have names that differ from the original elements:
  
    o media:group -> self.media,
    o geo:where -> self.geo,
    o photo:id -> self.gphoto_id
  """
  
  _tag = 'entry'
  _namespace = atom.ATOM_NAMESPACE
  _children = gdata.GDataEntry._children.copy()
  _attributes = gdata.GDataEntry._attributes.copy()
  ## NOTE: storing photo:id as self.gphoto_id, to avoid name clash with atom:id
  _children['{%s}id' % PHOTOS_NAMESPACE] = ('gphoto_id', Id) 
  _children['{%s}name' % PHOTOS_NAMESPACE] = ('name', Name)
  _children['{%s}location' % PHOTOS_NAMESPACE] = ('location', Location)
  _children['{%s}access' % PHOTOS_NAMESPACE] = ('access', Access)
  _children['{%s}timestamp' % PHOTOS_NAMESPACE] = ('timestamp', Timestamp)
  _children['{%s}numphotos' % PHOTOS_NAMESPACE] = ('numphotos', Numphotos)
  _children['{%s}user' % PHOTOS_NAMESPACE] = ('user', User)
  _children['{%s}nickname' % PHOTOS_NAMESPACE] = ('nickname', Nickname)
  _children['{%s}commentingEnabled' % PHOTOS_NAMESPACE] = ('commentingEnabled', CommentingEnabled)
  _children['{%s}commentCount' % PHOTOS_NAMESPACE] = ('commentCount', CommentCount)
  _children['{%s}thumbnail' % MEDIA_NAMESPACE] = ('thumbnail', Thumbnail) 
  ## NOTE: storing media:group as self.media, to create a self-explaining api
  _children['{%s}group' % MEDIA_NAMESPACE] = ('media', media.Group)
  ## NOTE: storing geo:where as self.geo, to create a self-explaining api
  _children['{%s}where' % GEORSS_NAMESPACE] = ('geo', geo.Where) 
  def __init__(self, author=None, category=None, content=None,
      atom_id=None, link=None, published=None,
      title=None, updated=None,
      #GPHOTO NAMESPACE:
      gphoto_id=None, name=None, location=None, access=None, 
      timestamp=None, numphotos=None, user=None, nickname=None,
      commentingEnabled=None, commentCount=None, thumbnail=None,
      # MEDIA NAMESPACE:
      mediagroup=None, 
      # GEORSS NAMESPACE:
      geo=None,
      extended_property=None,
      extension_elements=None, extension_attributes=None, text=None):
    gdata.GDataEntry.__init__(self, author=author, category=category,
                        content=content, atom_id=atom_id, link=link,
                        published=published, title=title,
                        updated=updated, text=text)

    ## NOTE: storing photo:id as self.gphoto_id, to avoid name clash with atom:id
    self.gphoto_id = gphoto_id 
    self.name = name
    self.location = location
    self.access = access
    self.timestamp = timestamp
    self.numphotos = numphotos
    self.user = user
    self.nickname = nickname
    self.commentingEnabled = commentingEnabled
    self.commentCount = commentCount
    self.thumbnail = thumbnail
    self.extended_property = extended_property or []
    self.text = text
    self.extension_elements = extension_elements or []
    self.extension_attributes = extension_attributes or {}
    ## NOTE: storing media:group as self.media, and geo:where as geo,
    ## to create a self-explaining api
    self.media = mediagroup 
    self.geo = geo

  def GetAlbumId(self):
    "Return the id of this album"
    
    return self.GetFeedLink().href.split('/')[-1]
          
  def GetPhotoFeedLink(self):
    "Return the uri to this album's PhotoFeed"
    
    href = self.GetFeedLink().href
    sep = '?'
    if '?' in href: sep = '&'
    return '%s%skind=photo' % (href, sep)
         
  def GetTagFeedLink(self):
    "Return the uri to this album's TagFeed"
    
    href = self.GetFeedLink().href
    sep = '?'
    if '?' in href: sep = '&'
    return '%s%skind=tag' % (href, sep)
  
def AlbumEntryFromString(xml_string):
  return atom.CreateClassFromXMLString(AlbumEntry, xml_string)
  
class AlbumFeed(PhotosBaseFeed):
  """A Google Photo Album meta feed flavor of an Atom Feed"""
  
  _children = gdata.GDataEntry._children.copy()
  _children['{%s}entry' % atom.ATOM_NAMESPACE] = ('entry', [AlbumEntry])

def AlbumFeedFromString(xml_string):
  return atom.CreateClassFromXMLString(AlbumFeed, xml_string)


class PhotoEntry(gdata.GDataEntry, gdata.LinkFinder):
  """A Google Photo meta Entry flavor of an Atom Entry

  Notes:
    To avoid name clashes, and to create a more sensible api, some
    objects have names that differ from the original elements:
  
    o media:group -> self.media,
    o exif:tags -> self.exif,
    o geo:where -> self.geo,
    o photo:id -> self.gphoto_id
  """
  
  _tag = 'entry'
  _namespace = atom.ATOM_NAMESPACE
  _children = gdata.GDataEntry._children.copy()
  _attributes = gdata.GDataEntry._attributes.copy()
  ## NOTE: storing photo:id as self.gphoto_id, to avoid name clash with atom:id
  _children['{%s}id' % PHOTOS_NAMESPACE] = ('gphoto_id', Id) 
  _children['{%s}albumid' % PHOTOS_NAMESPACE] = ('albumid', Albumid)
  _children['{%s}checksum' % PHOTOS_NAMESPACE] = ('checksum', Checksum)
  _children['{%s}client' % PHOTOS_NAMESPACE] = ('client', Client)
  _children['{%s}height' % PHOTOS_NAMESPACE] = ('height', Height)
  _children['{%s}position' % PHOTOS_NAMESPACE] = ('position', Position)
  _children['{%s}rotation' % PHOTOS_NAMESPACE] = ('rotation', Rotation)
  _children['{%s}size' % PHOTOS_NAMESPACE] = ('size', Size)
  _children['{%s}timestamp' % PHOTOS_NAMESPACE] = ('timestamp', Timestamp)
  _children['{%s}version' % PHOTOS_NAMESPACE] = ('version', Version)
  _children['{%s}width' % PHOTOS_NAMESPACE] = ('width', Width)
  _children['{%s}commentingEnabled' % PHOTOS_NAMESPACE] = ('commentingEnabled', CommentingEnabled)
  _children['{%s}commentCount' % PHOTOS_NAMESPACE] = ('commentCount', CommentCount)
  ## NOTE: storing media:group as self.media, exif:tags as self.exif, and
  ## geo:where as self.geo, to create a self-explaining api
  _children['{%s}group' % MEDIA_NAMESPACE] = ('media', media.Group) 
  _children['{%s}tags' % EXIF_NAMESPACE] = ('exif', exif.Tags) 
  _children['{%s}where' % GEORSS_NAMESPACE] = ('geo', geo.Where)
        
  def __init__(self, author=None, category=None, content=None,
      atom_id=None, link=None, published=None, summary=None,
      title=None, updated=None, text=None,
      # GPHOTO NAMESPACE:
      gphoto_id=None, albumid=None, checksum=None, client=None, height=None, position=None,
      rotation=None, size=None, timestamp=None, version=None, width=None,
      commentCount=None, commentingEnabled=None,
      # MEDIARSS NAMESPACE:
      mediagroup=None, 
      # EXIF_NAMESPACE:
      exif=None,
      # GEORSS NAMESPACE:
      geo=None,
      extension_elements=None, extension_attributes=None):
    gdata.GDataEntry.__init__(self, author=author, category=category,
                        content=content, atom_id=atom_id, link=link,
                        published=published, title=title, summary=summary,
                        updated=updated, text=text)

    ## NOTE: storing photo:id as self.gphoto_id, to avoid name clash with atom:id
    self.gphoto_id = gphoto_id
    self.albumid = albumid
    self.checksum = checksum
    self.client = client
    self.height = height
    self.position = position
    self.rotation = rotation
    self.size = size
    self.timestamp = timestamp
    self.version = version
    self.width = width
    self.commentingEnabled = commentingEnabled
    self.commentCount = commentCount
    ## NOTE: storing media:group as self.media, to create a self-explaining api
    self.media = mediagroup 
    self.exif = exif
    self.geo = geo

  def GetPostLink(self):
    "Return the uri to this photo's `POST' link (use it for updates of the object)"

    return self.GetFeedLink()

  def GetCommentFeedLink(self):
    "Return the uri to this photo's CommentFeed"
    
    href = self.GetFeedLink().href
    sep = '?'
    if '?' in href: sep = '&'
    return '%s%skind=comment' % (href, sep)

  def GetTagFeedLink(self):
    "Return the uri to this photo's TagFeed"
    
    href = self.GetFeedLink().href
    sep = '?'
    if '?' in href: sep = '&'
    return '%s%skind=tag' % (href, sep)

def PhotoEntryFromString(xml_string):
  return atom.CreateClassFromXMLString(PhotoEntry, xml_string)

class PhotoFeed(PhotosBaseFeed):
  """A Google Photo meta feed flavor of an Atom Feed"""
  
  _children = gdata.GDataEntry._children.copy()
  _children['{%s}entry' % atom.ATOM_NAMESPACE] = ('entry', [PhotoEntry])

def PhotoFeedFromString(xml_string):
  return atom.CreateClassFromXMLString(PhotoFeed, xml_string)

class TagEntry(gdata.GDataEntry, gdata.LinkFinder):
  """A Google Photo meta Entry flavor of an Atom Entry """
  
  _tag = 'entry'
  _namespace = atom.ATOM_NAMESPACE
  _children = gdata.GDataEntry._children.copy()
  _attributes = gdata.GDataEntry._attributes.copy()
  _children['{%s}weight' % PHOTOS_NAMESPACE] = ('weight', Weight)

  def __init__(self, author=None, category=None, content=None,
               atom_id=None, link=None, published=None,
               title=None, updated=None,
               # GPHOTO NAMESPACE:
               weight=None,
               extended_property=None,
               extension_elements=None, extension_attributes=None, text=None):
    gdata.GDataEntry.__init__(self, author=author, category=category,
                              content=content,
                              atom_id=atom_id, link=link, published=published,
                              title=title, updated=updated)
    
    self.weight = weight
    self.category.append(atom.Category(scheme='http://schemas.google.com/g/2005#kind', 
                                        term = 'http://schemas.google.com/photos/2007#tag'))

def TagEntryFromString(xml_string):
  return atom.CreateClassFromXMLString(TagEntry, xml_string)


class TagFeed(PhotosBaseFeed):
  """A Google Photo tag feed flavor of an Atom Feed"""
  
  _children = gdata.GDataEntry._children.copy()
  _children['{%s}entry' % atom.ATOM_NAMESPACE] = ('entry', [TagEntry])

def TagFeedFromString(xml_string):
  return atom.CreateClassFromXMLString(TagFeed, xml_string)

class CommentEntry(gdata.GDataEntry, gdata.LinkFinder):
  """A Google Photo comment Entry flavor of an Atom Entry """
  
  def __init__(self, author=None, category=None, content=None,
               atom_id=None, link=None, published=None,
               title=None, updated=None,
               # GPHOTO NAMESPACE:
               photoid=None,
               extended_property=None,
               extension_elements=None, extension_attributes=None, text=None):
    
    gdata.GDataEntry.__init__(self, author=author, category=category,
                              content=content,
                              atom_id=atom_id, link=link, published=published,
                              title=title, updated=updated)
    
    self.photoid = photoid
    self.category.append(atom.Category(scheme='http://schemas.google.com/g/2005#kind', 
                                        term = 'http://schemas.google.com/photos/2007#comment'))

  def GetCommentId(self):
      return self.GetSelfLink().href.split('/')[-1]

def CommentEntryFromString(xml_string):
  return atom.CreateClassFromXMLString(CommentEntry, xml_string)

class CommentFeed(PhotosBaseFeed):
  """A Google Photo comment feed flavor of an Atom Feed"""
  
  _children = gdata.GDataEntry._children.copy()
  _children['{%s}entry' % atom.ATOM_NAMESPACE] = ('entry', [CommentEntry])

def CommentFeedFromString(xml_string):
  return atom.CreateClassFromXMLString(CommentFeed, xml_string)
  
