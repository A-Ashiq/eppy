# Copyright (c) 2016 Santosh Philip
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""pytest for iddgroups"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import eppy.iddgroups as iddgroups

iddtxt = """!      W/m2, W or deg C
!      W/s
!      W/W
!      years
! **************************************************************************

Lead Input;

Simulation Data;

\\group G1

Version,
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\required-field
      \\default 7.0

Version1,
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\required-field
      \\default 7.0

Version2,
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\required-field
      \\default 7.0

\\group G2

VersionG,
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\required-field
      \\default 7.0

VersionG1,
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\required-field
      \\default 7.0

VersionG2,
      \\unique-object
      \\format singleLine
  A1 ; \\field Version Identifier
      \\required-field
      \\default 7.0

"""


def test_idd2groups():
    """py.test for idd2groups"""
    data = ((
        {
            'G2': ['VersionG', 'VersionG1', 'VersionG2'],
            'G1': ['Version', 'Version1', 'Version2'],
            None: ['Lead Input', 'Simulation Data']
        },
    ), # gdict
  )
    for gdict, in data:
        result = iddgroups.iddtxt2groups(iddtxt)
        assert result == gdict
