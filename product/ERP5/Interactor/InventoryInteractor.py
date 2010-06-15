# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.Interactor.Interactor import Interactor

class InventoryInteractor(Interactor):
  """
  This interactor invokes reindex on Inventory document when its
  subdocuments are modified.
  """
  def install(self):
    from Products.ERP5Type.Document.InventoryLine import InventoryLine
    self.on(InventoryLine.reindexObject).doAfter(self.reindexInventory)
    from Products.ERP5Type.Document.InventoryCell import InventoryCell
    self.on(InventoryCell.reindexObject).doAfter(self.reindexInventory)

  def reindexInventory(self, method_call_object, *args, **kw):
    """
      Reset _aq_dynamic
    """
    inventory = method_call_object.instance.getDeliveryValue()
    # No need to reindex recursively, so we call _reindexObject() not
    # reindexObject() that is defined in Delivery.py as recursiveReindexObject().
    inventory._reindexObject(**method_call_object.kw)
