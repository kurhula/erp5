##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

class TransformedResource:
    """
        TransformedResource which allows to define possible
        variations for a Resource, a Transformation, etc.
    """

    _properties = (
        # Definition of the variation domain
        {   'id'          : 'q_variation_base_category',
            'storage_id'  : 'q_variation_base_category_list', # Coramy Compatibility
            'description' : 'A list of base categories which define possible discrete variations. '\
                            'Variation ranges are stored as category membership. '\
                            '(prev. variation_category_list).',
            'type'        : 'lines',
            'default'     : [],
            'mode'        : 'w' },
        {   'id'          : 'v_variation_base_category',
            'storage_id'  : 'v_variation_base_category_list', # Coramy Compatibility
            'description' : 'A list of base categories which define possible discrete variations. '\
                            'Variation ranges are stored as category membership. '\
                            '(prev. variation_category_list).',
            'type'        : 'lines',
            'default'     : [],
            'mode'        : 'w' },
        {   'id'          : 'identical_variation_base_category',
            'storage_id'  : 'identical_variation_base_category_list', # Coramy Compatibility
            'description' : 'A list of base categories which keep an identical value to the default resource.',
            'type'        : 'lines',
            'default'     : [],
            'mode'        : 'w' },
        {   'id'          : 'specialise_id',
            'type'        : 'string',
            'description' : '',
            'acquisition_base_category' : ('specialise',),
            'acquisition_portal_type'   : ('Grille Consommation',),
            'acquisition_copy_value'    : 0,
            'acquisition_mask_value'    : 0,
            'acquisition_sync_value'    : 0,
            'acquisition_accessor_id'   : 'getId',
            'acquisition_depends'       : None,
            'mode'        : 'w' },

    )

    _categories = ('specialise', 'industrial_phase', )
