##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Accessor import Translation
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.ERP5Type.Base import Base, PropertyHolder
from Products.ERP5Type.Utils import setDefaultClassProperties, setDefaultProperties

from zLOG import LOG, ERROR, BLATHER

class PropertySheetTool(BaseTool):
  """
  Provides a configurable registry of property sheets
  """
  id = 'portal_property_sheets'
  meta_type = 'ERP5 Property Sheet Tool'
  portal_type = 'Property Sheet Tool'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declarePublic('getTranslationDomainNameList')
  def getTranslationDomainNameList(self):
    return (['']+
            [object_.id
             for object_ in getToolByName(self, 'Localizer').objectValues()
             if object_.meta_type=='MessageCatalog']+
            [Translation.TRANSLATION_DOMAIN_CONTENT_TRANSLATION]
            )

  @staticmethod
  def _guessFilesytemPropertyPortalType(attribute_dict):
    """
    Guess the Portal Type of a filesystem-based Property Sheet from
    the attributes of the given property
    """
    for key in attribute_dict:
      if key.startswith('acqui') or \
         key in ('alt_accessor_id',
                 # Specific to 'content' type
                 'portal_type',
                 'translation_acquired_property'):
        return 'Acquired Property'

    return 'Standard Property'

  security.declareProtected(Permissions.ModifyPortalContent,
                            'createPropertySheetFromFilesystemClass')
  def createPropertySheetFromFilesystemClass(self, klass):
    """
    Create a new Property Sheet in portal_property_sheets from a given
    filesystem-based Property Sheet definition.
    """
    new_property_sheet = self.newContent(id=klass.__name__,
                                         portal_type='Property Sheet')

    for attribute_dict in getattr(klass, '_properties', []):
      # The property could be either a Standard or an Acquired
      # Property
      portal_type = self._guessFilesytemPropertyPortalType(attribute_dict)

      # Create the new property and set its attributes
      new_property = new_property_sheet.newContent(portal_type=portal_type)
      new_property.importFromFilesystemDefinition(attribute_dict)

    for category in getattr(klass, '_categories', []):
      # A category may be a TALES Expression rather than a plain
      # string
      if isinstance(category, Expression):
        new_category = new_property_sheet.newContent(
          portal_type='Dynamic Category Property')

        # Set the category TALES expression
        new_category.importFromFilesystemDefinition(category)

      else:
        new_property_sheet.newContent(id=category,
                                      portal_type='Category Property')

    return new_property_sheet

  security.declareProtected(Permissions.ManagePortal,
                            'createAllPropertySheetsFromFilesystem')
  def createAllPropertySheetsFromFilesystem(self):
    """
    Create Property Sheets in portal_property_sheets from _all_
    filesystem Property Sheets

    XXX: only meaningful for testing?
    """
    from Products.ERP5Type import PropertySheet

    # Get all the filesystem Property Sheets
    for name, klass in PropertySheet.__dict__.iteritems():
      if name[0] == '_':
        continue

      if name not in self.portal_property_sheets:
        LOG("Tool.PropertySheetTool", BLATHER,
            "Creating %s in portal_property_sheets" % repr(name))

        self.createPropertySheetFromFilesystemClass(klass)

      else:
        LOG("Tool.PropertySheetTool", BLATHER,
            "%s already exists in portal_property_sheets" % repr(name))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportPropertySheetToFilesystemDefinitionTuple')
  def exportPropertySheetToFilesystemDefinitionTuple(self, property_sheet):
    """
    Export a given ZODB Property Sheet to its filesystem definition as
    tuple (properties, categories, constraints)

    XXX: Move this code and the accessor generation code (from Utils)
         within their respective documents
    """
    properties = []
    constraints = []
    categories = []

    for property in property_sheet.contentValues():
      portal_type = property.getPortalType()

      if portal_type == "Standard Property" or \
         portal_type == "Acquired Property":
        properties.append(property.exportToFilesystemDefinition())

      elif portal_type == "Category Property":
        categories.append(property.getId())

      elif portal_type == "Dynamic Category Property":
        categories.append(property.exportToFilesystemDefinition())

      elif portal_type.endswith('Constraint'):
        from Acquisition import aq_base
        constraints.append(aq_base(property.asContext()))

    return (properties, categories, constraints)

  def _createCommonPropertySheetAccessorHolder(self,
                                               property_holder,
                                               property_sheet_id,
                                               accessor_holder_module_name):
    """
    Create a new accessor holder class from the given Property Holder
    within the given accessor holder module (when the migration will
    be finished, there should only be one accessor holder module)
    """
    setDefaultClassProperties(property_holder)

    try:
      setDefaultProperties(property_holder, portal=self.getPortalObject())
    except:
      import traceback
      LOG("Tool.PropertySheetTool", ERROR,
          "Could not generate accessor holder class for %s (module=%s): %s" %\
          (property_sheet_id,
           accessor_holder_module_name,
           traceback.format_exc()))

      return None

    # Create the new accessor holder class and set its module properly
    accessor_holder_class = type(property_sheet_id, (object,), dict(
      __module__ = accessor_holder_module_name,
      constraints = property_holder.constraints,
      # The following attributes have been defined only because they
      # are being used in ERP5Type.Utils when getting all the
      # property_sheets of the property_holder (then, they are added
      # to the local properties, categories and constraints lists)
      _properties = property_holder._properties,
      # Necessary for getBaseCategoryList
      _categories = property_holder._categories,
      _constraints = property_holder._constraints
      ))

    # Set all the accessors (defined by a tuple) from the Property
    # Holder to the new accessor holder class (code coming from
    # createAccessor in Base.PropertyHolder)
    for id, fake_accessor in property_holder._getItemList():
      if not isinstance(fake_accessor, tuple):
        continue

      if fake_accessor is ('Base._doNothing',):
        # Case 1 : a workflow method only
        accessor = Base._doNothing
      else:
        # Case 2 : a workflow method over an accessor
        (accessor_class, accessor_args, key) = fake_accessor
        accessor = accessor_class(id, key, *accessor_args)

      # Add the accessor to the accessor holder
      setattr(accessor_holder_class, id, accessor)

    return accessor_holder_class

  security.declarePrivate('createFilesystemPropertySheetAccessorHolder')
  def createFilesystemPropertySheetAccessorHolder(self, property_sheet):
    """
    Create a new accessor holder from the given filesystem Property
    Sheet (the accessors are created through a Property Holder)

    XXX: Workflows?
    XXX: Remove as soon as the migration is finished
    """
    property_holder = PropertyHolder()

    property_holder._properties = getattr(property_sheet, '_properties', [])
    property_holder._categories = getattr(property_sheet, '_categories', [])
    property_holder._constraints = getattr(property_sheet, '_constraints', [])

    return self._createCommonPropertySheetAccessorHolder(
      property_holder,
      property_sheet.__name__,
      'erp5.filesystem_accessor_holder')

  security.declarePrivate('createZodbPropertySheetAccessorHolder')
  def createZodbPropertySheetAccessorHolder(self, property_sheet):
    """
    Create a new accessor holder from the given ZODB Property Sheet
    (the accessors are created through a Property Holder)

    XXX: Workflows?
    """
    definition_tuple = \
      self.exportPropertySheetToFilesystemDefinitionTuple(property_sheet)

    property_holder = PropertyHolder()

    # Prepare the Property Holder
    property_holder._properties, \
      property_holder._categories, \
      property_holder._constraints = definition_tuple

    return self._createCommonPropertySheetAccessorHolder(
      property_holder,
      property_sheet.getId(),
      'erp5.zodb_accessor_holder')
