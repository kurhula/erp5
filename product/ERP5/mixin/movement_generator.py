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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5.MovementCollectionDiff import _getPropertyAndCategoryList

class MovementGeneratorMixin:
  """Movement Generator interface specification

  Documents which implement IMovementGenerator
  can be used to generate an IMovementList from
  an existing IMovementCollection, IMovementList or
  IMovement. Typical IMovementGenerator are Rules
  and Trade Conditions.
  """

  # Implementation of IMovementGenerator
  def getGeneratedMovementList(context, movement_list=None, rounding=False):
    """
    Returns an IMovementList generated by a model applied to the context

    context - an IMovementCollection, an IMovementList or an IMovement

    movement_list - optional IMovementList which can be passed explicitely
                    whenever context is an IMovementCollection and whenever
                    we want to filter context.getMovementList

    rounding - boolean argument, which controls if rounding shall be applied on
               generated movements or not

    NOTE:
      - implement rounding appropriately (True or False seems
        simplistic)
    """
    raise NotImplementedError

  def _getInputMovementAndPathTupleList(self, context):
    """Returns list of tuples (movement, business_path)"""
    input_movement_list = self._getInputMovementList(context)
    business_process = context.getBusinessProcessValue()

    # In non-BPM case, we have no business path.
    if business_process is None:
      return [(input_movement, None) for input_movement in input_movement_list]

    input_movement_and_path_list = []
    business_path_list = []
    trade_phase_list = context.getSpecialiseValue().getTradePhaseList()
    for input_movement in input_movement_list:
      for business_path in business_process.getPathValueList(
                          trade_phase_list,
                          input_movement):
        input_movement_and_path_list.append((input_movement, business_path))
        business_path not in business_path_list and business_path_list \
            .append(business_path)

    if len(business_path_list) > 1:
      raise NotImplementedError

    return input_movement_and_path_list

  def _getInputMovementList(self, context):
    raise NotImplementedError

  def _getPropertyAndCategoryList(self, movement, business_path):
    property_dict = _getPropertyAndCategoryList(movement)

    if business_path is None:
      return property_dict

    # Arrow
    for base_category in \
        business_path.getSourceArrowBaseCategoryList() +\
        business_path.getDestinationArrowBaseCategoryList():
      category_url = business_path.getDefaultAcquiredCategoryMembership(
          base_category, context=movement)
      if category_url not in ['', None]:
        property_dict[base_category] = [category_url]
      else:
        property_dict[base_category] = []
    # Amount
    if business_path.getQuantity():
      property_dict['quantity'] = business_path.getQuantity()
    elif business_path.getEfficiency():
      property_dict['quantity'] = movement.getQuantity() *\
        business_path.getEfficiency()
    else:
      property_dict['quantity'] = movement.getQuantity()

    movement_start_date = movement.getStartDate()
    movement_stop_date = movement.getStopDate()
    if movement_start_date == movement_stop_date:
      property_dict['start_date'] = business_path.getExpectedStartDate(
          movement)
      property_dict['stop_date'] = business_path.getExpectedStopDate(movement)
      # in case of not fully working BPM get dates from movement
      # XXX: as soon as BPM will be fully operational this hack will not be
      #      needed anymore
      if property_dict['start_date'] is None:
        property_dict['start_date'] = movement_start_date
      if property_dict['stop_date'] is None:
        property_dict['stop_date'] = movement_stop_date
    else: # XXX shall not be used, but business_path.getExpectedStart/StopDate
          # do not works on second path...
      property_dict['start_date'] = movement_start_date
      property_dict['stop_date'] = movement_stop_date

    # save a relation to business path
    property_dict['causality_list'] = [business_path.getRelativeUrl()]

    return property_dict
