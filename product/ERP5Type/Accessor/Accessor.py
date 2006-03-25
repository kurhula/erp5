##############################################################################
#
# Copyright (c) 2002-2003 Nexedi SARL and Contributors. All Rights Reserved.
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

from MethodObject import Method
from copy import copy
import sys
from zLOG import LOG

class Accessor(Method):
    """
      Generic Accessor - placehold for common methods
    """
    def __getinitargs__(self):
      init = getattr(self, '__init__', None)
      if init is not None:
        varnames = init.func_code.co_varnames
        args = []
        for name in varnames:
          if name == 'self':
            continue
          else:
            args.append(getattr(self, '_' + name))
        return tuple(args)
      return ()

    def dummy_copy(self, id):
      # Copy an accessor and change its id/name
      #self.__call__ = None
      #try:
      #  clone_instance = self.__class__(*self.__getinitargs__())
      #except:
      #  LOG('dummy_copy', 0, '%r could not be generated with %r' % (id, self.__class__), error=sys.exc_info())
      #  raise
      clone_instance = copy(self)
      #delattr(self, '__call__')
      #if hasattr(clone_instance, '__call__'):
      #  delattr(clone_instance, '__call__')
      clone_instance.__name__ = id
      return clone_instance
