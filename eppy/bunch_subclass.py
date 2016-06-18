# Copyright (c) 2012 Santosh Philip
# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================

"""Sub class Bunch to represent an IDF object.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy

from munch import Munch as Bunch
import eppy.function_helpers as fh


class BadEPFieldError(AttributeError):
    """An Exception"""
    pass


class RangeError(ValueError):
    """An Exception"""
    pass


def somevalues(ddtt):
    """returns some values"""
    return ddtt.Name, ddtt.Construction_Name, ddtt.obj

def extendlist(lst, i, value=''):
    """extend the list so that you have i-th value"""
    if i < len(lst):
        pass
    else:
        lst.extend([value, ] * (i - len(lst) + 1))
        


def return42(self, *args, **kwargs):
    # proof of concept - to be removed
    return 42        

def addfunctions(abunch):
    """add functions to epbunch"""

    # proof of concept - remove
    abunch['__functions'].update({'return42':return42}) 
    abunch['__functions'].update({'buildingname':fh.buildingname}) 
    # proof of concept
    
    key = abunch.obj[0].upper()
    snames = [
        "BuildingSurface:Detailed",
        "Wall:Detailed",
        "RoofCeiling:Detailed",
        "Floor:Detailed",
        "FenestrationSurface:Detailed",
        "Shading:Site:Detailed",
        "Shading:Building:Detailed",
        "Shading:Zone:Detailed", ]
    snames = [sname.upper() for sname in snames]
    if key in snames:
        func_dict = {
            'area': fh.area,
            'height': fh.height,  # not working correctly
            'width': fh.width,  # not working correctly
            'azimuth': fh.azimuth,
            'tilt': fh.tilt,
            'coords': fh.getcoords,  # needed for debugging
        }
        abunch.__functions.update(func_dict)
    return abunch

class EpBunch(Bunch):
    """
    Fields, values, and descriptions of fields in an EnergyPlus IDF object 
    stored in a `bunch` which is a `dict` extended to allow access to dict 
    fields as attributes as well as by keys.
    
    """
    def __init__(self, obj, objls, objidd, theidf, *args, **kwargs):
        super(EpBunch, self).__init__(*args, **kwargs)
        self.obj = obj        # field names
        self.objls = objls    # field values
        self.objidd = objidd  # field metadata (minimum, maximum, type, etc.)
        self.theidf = theidf  # pointer to the idf this epbunch belongs to
                              # This is None if there is no idf - a standalone epbunch      
        self['__functions'] = {} # initialize the funcitons
        addfunctions(self)
        
    @property
    def fieldnames(self):
        """Friendly name for objls.
        """
        return self.objls

    @property
    def fieldvalues(self):
        """Friendly name for obj.
        """
        return self.obj    
    
    def checkrange(self, fieldname):
        """Check if the value for a field is within the allowed range.
        """
        return checkrange(self, fieldname)
    
    def getrange(self, fieldname):
        """Get the allowed range of values for a field.
        """
        return getrange(self, fieldname)
        
    def getidd(self, fieldname):
        """return the idd for the field"""
        return getidd(self, fieldname)
        
    def get_retaincase(self, fieldname):
        """check if the field should retain case"""
        return get_retaincase(self, fieldname)
    
    def __setattr__(self, name, value):
        try:
            origname = self['__functions'][name]
            # TODO: unit test never hits here so what is it for?
            self[origname] = value
        except KeyError:
            pass

        try:
            name = self['__aliases'][name]  # get original name of the alias
        except KeyError:
            pass

        if name in ('__functions', '__aliases'):  # just set the new value
            self[name] = value
            return None
        elif name in ('obj', 'objls', 'objidd', 'theidf'):  # let Bunch handle it
            super(EpBunch, self).__setattr__(name, value)
            return None
        elif name in self.fieldnames:  # set the value, extending if needed
            i = self.fieldnames.index(name)
            try:
                self.fieldvalues[i] = value
            except IndexError:
                extendlist(self.fieldvalues, i)
                self.fieldvalues[i] = value
        else:
            astr = "unable to find field %s" % (name, )
            raise BadEPFieldError(astr)  # TODO: could raise AttributeError
        
    def __getattr__(self, name):
        try:
            func = self['__functions'][name]
            return func(self)
        except KeyError:
            pass

        try:
            name = self['__aliases'][name]
        except KeyError:
            pass

        if name == '__functions':
            return self['__functions']
        elif name in ('__aliases', 'obj', 'objls', 'objidd', 'theidf'):
            # unit test
            return super(EpBunch, self).__getattr__(name)
        elif name in self.fieldnames:
            i = self.fieldnames.index(name)
            try:
                return self.fieldvalues[i]
            except IndexError:
                return ''
        else:
            astr = "unable to find field %s" % (name, )
            raise BadEPFieldError(astr)
        
    def __getitem__(self, key):
        if key in ('obj', 'objls', 'objidd', 
                '__functions', '__aliases', 'theidf'):
            return super(EpBunch, self).__getitem__(key)
        elif key in self.fieldnames:
            i = self.fieldnames.index(key)
            try:
                return self.fieldvalues[i]
            except IndexError:
                return ''
        else:
            astr = "unknown field %s" % (key, )
            raise BadEPFieldError(astr)
    
    def __setitem__(self, key, value):
        if key in ('obj', 'objls', 'objidd', 
                '__functions', '__aliases', 'theidf'):
            super(EpBunch, self).__setitem__(key, value)
            return None
        elif key in self.fieldnames:
            i = self.fieldnames.index(key)
            try:
                self.fieldvalues[i] = value
            except IndexError:
                extendlist(self.fieldvalues, i)
                self.fieldvalues[i] = value
        else:
            astr = "unknown field %s" % (key, )
            raise BadEPFieldError(astr)

    def __repr__(self):
        """print this as an idf snippet"""
        lines = [str(val) for val in self.obj]
        comments = [comm.replace('_', ' ') for comm in self.objls]
        lines[0] = "%s," % (lines[0], ) # comma after first line
        for i, line in enumerate(lines[1:-1]):
            lines[i + 1] = '    %s,' % (line, ) # indent and comma
        lines[-1] = '    %s;' % (lines[-1], )# ';' after last line
        lines = [line.ljust(26) for line in lines] # ljsut the lines
        filler = '%s    !- %s'
        nlines = [filler % (line, comm) for line,
                  comm in zip(lines[1:], comments[1:])]# adds comments to line
        nlines.insert(0, lines[0])# first line without comment
        astr = '\n'.join(nlines)
        return '\n%s\n' % (astr, )
    
    def __str__(self):
        """same as __repr__"""
        # needed if YAML is installed. See issue 67
        # unit test
        return self.__repr__()


def getrange(bch, fieldname):
    """get the ranges for this field"""
    keys = ['maximum', 'minimum', 'maximum<', 'minimum>', 'type']
    index = bch.objls.index(fieldname)
    fielddct_orig = bch.objidd[index]
    fielddct = copy.deepcopy(fielddct_orig)
    therange = {}
    for key in keys:
        therange[key] = fielddct.setdefault(key, None)
    if therange['type']:
        therange['type'] = therange['type'][0]
    if therange['type'] == 'real':
        for key in keys[:-1]:
            if therange[key]:
                therange[key] = float(therange[key][0])
    if therange['type'] == 'integer':
        for key in keys[:-1]:
            if therange[key]:
                therange[key] = int(therange[key][0])
    return therange


def checkrange(bch, fieldname):
    """throw exception if the out of range"""
    fieldvalue = bch[fieldname]
    therange = bch.getrange(fieldname)
    if therange['maximum'] != None:
        if fieldvalue > therange['maximum']:
            astr = "Value %s is not less or equal to the 'maximum' of %s"
            astr = astr % (fieldvalue, therange['maximum'])
            raise RangeError(astr)
    if therange['minimum'] != None:
        if fieldvalue < therange['minimum']:
            astr = "Value %s is not greater or equal to the 'minimum' of %s"
            astr = astr % (fieldvalue, therange['minimum'])
            raise RangeError(astr)
    if therange['maximum<'] != None:
        if fieldvalue >= therange['maximum<']:
            astr = "Value %s is not less than the 'maximum<' of %s"
            astr = astr % (fieldvalue, therange['maximum<'])
            raise RangeError(astr)
    if  therange['minimum>'] != None:
        if fieldvalue <= therange['minimum>']:
            astr = "Value %s is not greater than the 'minimum>' of %s"
            astr = astr % (fieldvalue, therange['minimum>'])
            raise RangeError(astr)
    return fieldvalue
    
def getidd(bch, fieldname):
    """get the idd for this field"""
    fieldindex = bch.objls.index(fieldname)
    fieldidd = bch.objidd[fieldindex]
    return fieldidd
    
def get_retaincase(bch, fieldname):
    """Check if the field should retain case"""
    fieldidd = bch.getidd(fieldname)
    return fieldidd.has_key('retaincase')
    
