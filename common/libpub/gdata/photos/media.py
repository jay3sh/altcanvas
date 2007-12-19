# -*-*- encoding: utf-8 -*-*-
#
# This is the base file for the PicasaWeb python client.
# It is used for lower level operations.
#
# $Id: __init__.py 81 2007-10-03 14:41:42Z havard.gulldahl $
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

"""Contains extensions to ElementWrapper objects, for use with Google Photo services"""

__author__ = u'havard.gulldahl@gmail.com'# (Håvard Gulldahl)' #BUG: api chokes on non-ascii chars in __author__

class MediaBaseElement(PhotosBaseElement):
  """Base class for elements in the MEDIA_NAMESPACE. New elements need only add the tag name to self._tag"""
  _tag = ''

  def _TransferToElementTree(self, element_tree):
    atom.AtomBase._TransferToElementTree(self, element_tree)
    element_tree.tag = MEDIA_TEMPLATE % self._tag 
    return element_tree

class MediaGroup(MediaBaseElement):
  _tag = 'group'
class MediaContent(MediaBaseElement):
  _tag = 'content'
class MediaCredit(MediaBaseElement):
  _tag = 'credit'
class MediaDescription(MediaBaseElement):
  _tag = 'description'
class MediaGroup(MediaBaseElement):
  _tag = 'group'
class MediaKeywords(MediaBaseElement):
  _tag = 'keywords'
class MediaThumbnail(MediaBaseElement):
  _tag = 'thumbnail'
  
  def __init__(self, extension_elements=None, url=None, width=None, height=None,
      extension_attributes=None, text=None, value=None):
    self.url = url
    self.width = width
    self.height = height
    self.extension_elements = extension_elements or []
    self.extension_attributes = extension_attributes or {}

  def _TransferToElementTree(self, element_tree):
    if self.url:
      element_tree.attrib['url'] = self.url
    if self.width:
      element_tree.attrib['width'] = self.width
    if self.height:
      element_tree.attrib['height'] = self.height
    atom.AtomBase._TransferToElementTree(self, element_tree)
    element_tree.tag = MEDIA_TEMPLATE % self._tag 
    return element_tree

  def _TakeAttributeFromElementTree(self, attribute, element_tree):
    if attribute == 'url':
      self.url = element_tree.attrib[attribute]
      del element_tree.attrib[attribute]
    elif attribute == 'width':
      self.width = element_tree.attrib[attribute]
      del element_tree.attrib[attribute]
    elif attribute == 'height':
      self.height = element_tree.attrib[attribute]
      del element_tree.attrib[attribute]
    else:
      atom.AtomBase._TakeAttributeFromElementTree(self, attribute,
          element_tree)

class MediaTitle(MediaBaseElement):
  _tag = 'title'
