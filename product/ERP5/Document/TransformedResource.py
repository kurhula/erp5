##############################################################################
#
# Copyright (c) 2002, 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5Type.Base import TempBase

from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.Transformation import AggregatedAmountList

from Products.CMFCore.Expression import Expression

from zLOG import LOG

class TransformedResource(XMLObject, XMLMatrix, Amount):
    """
        TransformedResource defines which
        resource is being transformed

        - variation
        - quantity

        Maybe defined by mapped values inside the transformed resource

      XXX Transformation works only for a miximum of 3 variation base category...
      Matrixbox must be rewrite for a clean implementation of n base category


    """

    meta_type = 'ERP5 Transformed Resource'
    portal_type = 'Transformed Resource'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.TransformedResource
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )



    ### Variation matrix definition
    #
    security.declareProtected(Permissions.AccessContentsInformation, 'updateVariationCategoryList')
    def updateVariationCategoryList(self):
      """
        Check if variation category list of the resource changed and update transformed resource
        by doing a set cell range
      """
      self.setQVariationBaseCategoryList( self.getQVariationBaseCategoryList() )
      self.setVVariationBaseCategoryList( self.getVVariationBaseCategoryList() )

    security.declareProtected(Permissions.ModifyPortalContent, '_updateQMatrixCellRange')
    def _updateQMatrixCellRange(self):
      cell_range =  self.TransformedResource_asCellRange('quantity')

#      XXX TransformedResource works only for a maximum of 3 variation base category...
#      Matrixbox must be rewrite for a clean implementation of n base category
      if len(cell_range) <= 3:
        self.setCellRange(base_id='quantity', *cell_range)
      else:
        raise MoreThan3VariationBaseCategory

    security.declareProtected(Permissions.ModifyPortalContent, '_setQVariationBaseCategoryList')
    def _setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on
      """
      self._baseSetQVariationBaseCategoryList(value)
      self._updateQMatrixCellRange()

    security.declareProtected(Permissions.ModifyPortalContent, 'setQVariationBaseCategoryList')
    def setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on and reindex the object
      """
      self._setQVariationBaseCategoryList(value)
      self.reindexObject()

    security.declareProtected(Permissions.ModifyPortalContent, '_updateVMatrixCellRange')
    def _updateVMatrixCellRange(self):
      cell_range =  self.TransformedResource_asCellRange('variation')
#      XXX TransformedResource works only for a maximum of 3 variation base category...
#      Matrixbox must be rewrite for a clean implementation of n base category
      if len(cell_range) <= 3:
        self.setCellRange(base_id='variation', *cell_range)
      else:
        raise MoreThan3VariationBaseCategory

    security.declareProtected(Permissions.ModifyPortalContent, '_setVVariationBaseCategoryList')
    def _setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on
      """
      self._baseSetVVariationBaseCategoryList(value)
      self._updateVMatrixCellRange()

    security.declareProtected(Permissions.ModifyPortalContent, 'setVVariationBaseCategoryList')
    def setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on and reindex the object
      """
      self._setVVariationBaseCategoryList(value)
      self.reindexObject()


    security.declareProtected(Permissions.AccessContentsInformation,'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list = ()):
        """
          Returns possible variation category values for the
          transformation according to the default resource.
          Possible category values is provided as a list of
          tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
          Display is left...
        """
        resource = self.getResourceValue()
        result = []
        if resource != None:
          if base_category_list is ():
            base_category_list = resource.getVariationBaseCategoryList()

          result = resource.getVariationRangeCategoryItemList(base_category_list=base_category_list )

        return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
    def getAggregatedAmountList(self, context=None, REQUEST=None, **kw):
      """
        Get all interesting amount value and return TempAmount
      """
      context = self.asContext(context=context, REQUEST=REQUEST, **kw)
      # Create the result object
      aggregated_amount_list = AggregatedAmountList()
      
      # Create temporary object to store amount
      from Products.ERP5Type.Document import newTempAmount
      tmp_amount = newTempAmount(self.getPortalObject(), self.getId())
      
      error_string = ''

      # add resource relation
      resource = self.getDefaultResourceValue()
      if resource != None:
        tmp_amount.setResourceValue(resource)
      else:
        error_string += 'No resource defined on %s' % self.getRelativeUrl()

      # First, we set initial values for quantity and variation
      # Currently, we only consider discrete variations
      # Continuous variations will be implemented in a future version of ERP5

      quantity_unit = self.getQuantityUnit()
      tmp_amount.setQuantityUnitValue(quantity_unit)


      efficiency =  self.getEfficiency()
      if efficiency is None or efficiency is '' or efficiency == 0.0:
        efficiency = 1.0
      else:
        efficiency = float(efficiency)

      quantity_defined_by = None

      # get Quantity
      quantity = None
      if context != None:
        # We will browse the mapped values and determine which apply
        for key in self.getCellKeyList( base_id = 'quantity'):
          if self.hasCell(base_id='quantity', *key):
            mapped_value = self.getCell(base_id='quantity', *key)
            if mapped_value.test(context):
              if 'quantity' in mapped_value.getMappedValuePropertyList():
                quantity = mapped_value.getProperty('quantity')
                quantity_defined_by = mapped_value.getRelativeUrl()

      if quantity in [None,'']:
        quantity = self.getQuantity()
        quantity_defined_by = self.getRelativeUrl()

      # If we have to do this, then there is a problem....
      # We'd better have better API for this, like an update function in the mapped_value
      try:
        quantity = float(quantity)
      except:
        error_string += 'Quantity is not a float.'


      variation_category_list_defined_by = None

      # get Variation Category List
      variation_category_list = None
      if context != None:
        # We will browse the mapped values and determine which apply
        for key in self.getCellKeyList( base_id = 'variation'):
          if self.hasCell(base_id='variation', *key):
            mapped_value = self.getCell(base_id='variation', *key)

            if mapped_value.test(context):
              vcl = mapped_value.getCategoryList()
              if vcl != []:
                variation_category_list = vcl
                variation_category_list_defined_by = mapped_value.getRelativeUrl()

      if variation_category_list in [None,'',[], ()]:
        variation_category_list = self._getVariationCategoryList()
        variation_category_list_defined_by = self.getRelativeUrl()

      tmp_amount._edit(
        # Properties define on transformation line
        description =  self.getDescription(),
        efficiency = efficiency,
        quantity = quantity,

        # This fields only store some informations for debugging if necessary
        quantity_defined_by  = quantity_defined_by,
        variation_category_list_defined_by = variation_category_list_defined_by, 
        error_string = error_string
      )

      tmp_amount.setVariationCategoryList(variation_category_list)
        
      aggregated_amount_list.append( tmp_amount )

      return aggregated_amount_list
