#-------------------------------------------------------------------------------
#Name:              refprop
#Purpose:           Call out fluid properties from REFPROP
#
#Author:            Thelen, B.J.
#                   thelen_ben@yahoo.com
#-------------------------------------------------------------------------------
#
#Recognitions
#-------------------------------------------------------------------------------
#Creators / Developers of REFPROP,
#Lemmon, E.W.,
#Huber, M.L.,
#McLinden, M.O.,
#NIST Standard Reference Database 23:  Reference Fluid Thermodynamic and
#Transport Properties-REFPROP,
#Version 9.0,
#National Institute of Standards and Technology,
#Standard Reference Data Program, Gaithersburg, 2010.
#
#Initial developer of Python link to REFPROP,
#Bruce Wernick
#-------------------------------------------------------------------------------
u''' This Python module compiled and linked the Database REFPROP (REFerence
fluid PROPerties) for usage in Python.

REFPROP software is a proprietary and need to be installed on the computer
in order for this module to function. Please contact the National Institute
ofStandards and Technology (NIST) to obtain REFPROP

The subroutine SETUP must be called to initialize the pure fluid or mixture
components. The call to SETUP will allow the choice of one of three
standard reference states for entropy and enthalpy and will automatically
load the "NIST-recommended" models for the components as well as mixing
rules.The routine SETMOD allows the specification of other models. To
define another reference state, or to apply one of the standard states to a
mixture of a specified composition, the subroutine SETREF may be used.These
additional routines should be called only if the fluids and/or models (or
reference state) are changed. The sequence is:

call SETMOD (optional) or GERG04 (Optional)
call SETUP  (REQUIRED)
call SETKTV (optional)
call PREOS  (optional)
call SETAGA (optional)
call SETREF (optional)

Subroutine PUREFLD allows the user to calculate the properties of a pure
fluid when a mixture has been loaded and the fluid is one of the
constituents in the mixture.

Units
----------------------------------------------------------------------------
temperature                         K
pressure, fugacity                  kPa
density                             mol/L
composition                         mole fraction
quality                             mole basis (moles vapor/total moles)
enthalpy, internal energy           J/mol
Gibbs, Helmholtz free energy        J/mol
entropy, heat capacity              J/(mol.K)
speed of sound                      m/s
Joule-Thompson coefficient          K/kPa
d(p)/d(rho)                         kPa.L/mol
d2(p)/d(rho)2                       kPa.(L/mol)^2
viscosity                           microPa.s (10^-6 Pa.s)
thermal conductivity                W/(m.K)
dipole moment                       debye
surface Tension                     N/m
----------------------------------------------------------------------------
'''

#imports
from __future__ import division
import ctypes, _ctypes
import fnmatch
import os, sys, platform
import copy
from decimal import Decimal



#Declarations
#Global Declarations
_set = {}
_setwarning = u'on'
_seterror = u'on'
_seterrordebug = u'off'
_rp = None
_fixicomp = 0
refpropso = u''
refpropdll = u''
_fpath = u''
_setupprop = {}
_gerg04_pre_rec = None
_setmod_pre_rec = None
testresult = u''
_setup_rec = None
_setmod_rec = None
_nc_rec = 0
_gerg04_rec = None
_setref_rec = None
_purefld_rec = None
_setktv_rec = None
_setaga_rec = None
_preos_rec = None

#Input Declarations
_nmxpar = 6
_maxcomps = 20

_icomp = ctypes.c_long()
_jcomp = ctypes.c_long()
_kph = ctypes.c_long()
_kq = ctypes.c_long()
_kguess = ctypes.c_long()
_nc = ctypes.c_long()
_ixflag = ctypes.c_long()
_v = ctypes.c_long()

_hrf = ctypes.create_string_buffer(3)
_htype = ctypes.create_string_buffer(3)
_hmodij = ctypes.create_string_buffer(3)
_hmix = ctypes.create_string_buffer(3)
_hpth = ctypes.create_string_buffer(255)
_hmxnme = ctypes.create_string_buffer(255)
_hfmix = ctypes.create_string_buffer(225)
_hfld = ctypes.create_string_buffer(255 * _maxcomps)
_routine = ctypes.create_string_buffer(2)

_x = (ctypes.c_double * _maxcomps)()
_x0 = (ctypes.c_double * _maxcomps)()

_fij = (ctypes.c_double * _nmxpar)()

_hcomp = ((ctypes.c_char * 3) * _maxcomps)()

#output declarations
#c_double
(_tcrit, _pcrit, _Dcrit, _zcrit, _t, _D, _p, _e, _h, _s, _A, _G, _cv, _cp, _w,
 _Z, _hjt, _xkappa, _beta, _dpdD, _d2pdD2, _dpdt, _dDdt, _dDdp, _spare1,
 _spare2, _spare3, _spare4, _xisenk, _xkt, _betas, _bs, _xkkt, _thrott, _pint,
 _spht, _Ar, _Gr, _dhdt_D, _dhdt_p, _dhdD_t, _dhdD_p, _dhdp_t, _dhdp_D, _b,
 _dbt, _c, _d, _Dliq, _Dvap, _t1, _p1, _D1, _t2, _p2, _D2, _t3, _p3, _D3, _csat,
 _cv2p, _tcx, _qkg, _wmix, _wmm, _ttrp, _tnbpt, _acf, _dip, _Rgas, _tmin, _tmax,
 _Dmax, _pmax, _Dmin, _tbub, _tdew, _pbub, _pdew, _Dlbub, _Dvdew, _wliq, _wvap,
 _de, _sigma, _eta, _h0, _s0, _t0, _p0, _vE, _eE, _hE, _sE, _aE, _gE, _pr, _er,
 _hr, _sr, _cvr, _cpr, _ba, _ca, _dct, _dct2, _Fpv, _dadn, _dnadn, _cs, _ts,
 _Ds, _ps, _ws, _var1, _var2,
 _q)=(ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double(),
      ctypes.c_double())

#create_string_buffer
(_hname, _hn80, _hcas, _hbinp, _hmxrul, _hfm, _hcode, _hcite,
 _herr) = (ctypes.create_string_buffer(12), ctypes.create_string_buffer(80),
           ctypes.create_string_buffer(12), ctypes.create_string_buffer(255),
           ctypes.create_string_buffer(255), ctypes.create_string_buffer(255),
           ctypes.create_string_buffer(3), ctypes.create_string_buffer(255),
           ctypes.create_string_buffer(255))

#c_double * _maxcomps
(_xliq, _xvap, _xkg, _xbub, _xdew, _xlkg, _xvkg, _u,
 _f) = ((ctypes.c_double * _maxcomps)(), (ctypes.c_double * _maxcomps)(),
         (ctypes.c_double * _maxcomps)(), (ctypes.c_double * _maxcomps)(),
         (ctypes.c_double * _maxcomps)(), (ctypes.c_double * _maxcomps)(),
         (ctypes.c_double * _maxcomps)(), (ctypes.c_double * _maxcomps)(),
         (ctypes.c_double * _maxcomps)())

#c_long
(_nroot, _k1, _k2, _k3, _ksat, _ierr,
 _kr) = (ctypes.c_long(), ctypes.c_long(), ctypes.c_long(), ctypes.c_long(),
         ctypes.c_long(), ctypes.c_long(), ctypes.c_long())

#c_char
#some error with ctypes or refpropdll the following should work but doesnot
#_hfij = ((ctypes.c_char * 8) * _nmxpar)()
_hfij = ((ctypes.c_char * (8 * _nmxpar)) * _nmxpar)()



#classes
class _Setuprecord(object):
    u'record setmod, setup, setktv, setref, purefld input values for def reset'
    object_list = []

    #add record
    def __init__(self, record, objectname):
        self.record = record
        self.objectname = objectname
        self.object_list.append(self.objectname)

    #del record
    def __del__(self):
        self.object_list.remove(self.objectname)

class RefpropError(Exception):
    u'General RepropError for python module'
    pass

class RefpropdllError(RefpropError):
    u'General RepropError from refprop'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RefpropicompError(RefpropError):
    u'Error for incorrect component no input'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RefpropinputError(RefpropError):
    u'Error for incorrect def input'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RefpropnormalizeError(RefpropError):
    u'Error if sum component input does not match value 1'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RefproproutineError(RefpropError):
    u'Error if routine input is unsupported'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RefpropWarning(RefpropError):
    u'General Warning for python module'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RefpropdllWarning(RefpropWarning):
    u'General RepropWarning from refprop'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SetupWarning(RefpropWarning):
    u'General SetupWarning from refprop'
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SetWarning(object):
    u'Return RefpropdllWarning status (on / off)'
    def __repr__(self):
        return _setwarning
    @staticmethod
    def on():
        u'Sets RefpropdllWarning on, initiate Error on Refpropdll ierr value < 0'
        global _setwarning, _set
        _setwarning = u'on'
        if u'SetWarning' in _set: _set.pop(u'SetWarning')
        return _prop()
    @staticmethod
    def off():
        u'Sets RefpropdllWarning off, no Error raised on Refpropdll ierr value < 0'
        global _setwarning, _set
        _setwarning = u'off'
        _set[u'SetWarning'] = u'off'
        return _prop()

class SetError(object):
    u'Return RefpropdllError status (on / off)'
    def __repr__(self):
        return _seterror
    @staticmethod
    def on():
        u'Sets RefpropdllError on, initiate Error on Refpropdll ierr value != 0'
        global _seterror, _set
        _seterror = u'on'
        if u'SetError' in _set: _set.pop(u'SetError')
        return _prop()
    @staticmethod
    def off():
        u'Sets RefpropdllError off, no Error raised on Refpropdll ierr value != 0'
        global _seterror, _set
        _seterror = u'off'
        _set[u'SetError'] = u'off'
        return _prop()

class SetErrorDebug(object):
    u'Return SetErrorDebug status (on / off)'
    def __repr__(self):
        return _seterrordebug
    @staticmethod
    def on():
        u'Sets error debug mode on, displays error message only'
        global _seterrordebug, _set
        _seterrordebug = u'on'
        _set[u'SetDebug'] = u'on'
        return _prop()
    @staticmethod
    def off():
        u'Sets error debug mode off, displays error message only'
        global _seterrordebug, _set
        _seterrordebug = u'off'
        if u'SetDebug' in _set: _set.pop(u'SetDebug')
        return _prop()

class FluidModel():
    u'''return string of current loaded fluid model

    array includes:
    setmod / gerg04
    setup
    setktv
    preos
    setaga
    setref
    purefld'''
    def __repr__(self):
        fldsetup = u''
        if u'_setmod_rec' in _Setuprecord.object_list:
            fldsetup += u'setmod ==> ' + unicode(_setmod_rec.record) + u'\n'
        if u'_gerg04_rec' in _Setuprecord.object_list:
            fldsetup += u'gerg04 ==> ' + unicode(_gerg04_rec.record) + u'\n'
        if u'_setup_rec' in _Setuprecord.object_list:
            fldsetup += u'setup ==> ' + unicode(_setup_rec.record) + u'\n'
        if u'_setktv_rec' in _Setuprecord.object_list:
            fldsetup += u'setktv ==> ' + unicode(_setktv_rec.record) + u'\n'
        if u'_preos_rec' in _Setuprecord.object_list:
            fldsetup += u'preos ==> ' + unicode(_preos_rec.record) + u'\n'
        if u'_setaga_rec' in _Setuprecord.object_list:
            fldsetup += u'setaga ==> ' + unicode(_setaga_rec.record) + u'\n'
        if u'_setref_rec' in _Setuprecord.object_list:
            fldsetup += u'setref ==> ' + unicode(_setref_rec.record) + u'\n'
        if u'_purefld_rec' in _Setuprecord.object_list:
            fldsetup += u'purefld ==> ' + unicode(_purefld_rec.record) + u'\n'
        return fldsetup



#Functions
#additional functions (not from refprop)
def _load():
    global _rp, _fixicomp
    #reset _rp from system
    if _rp != None:
        #create exception for errors
        if unicode(SetError()) == u'off':
            se = SetError.off
        elif unicode(SetError()) == u'on':
            se = SetError.on
        SetError.off()

        #reset fixicomp from def purefld()
        _fixicomp = 0

        if u'_purefld_rec' in _Setuprecord.object_list:
            purefld()
        if u'_setref_rec' in _Setuprecord.object_list:
            setref()
        if u'_setaga_rec' in _Setuprecord.object_list:
            unsetaga()
        if u'_preos_rec' in _Setuprecord.object_list:
            preos()
        if u'_setktv_rec' in _Setuprecord.object_list:
            setktv(1, 1, u'RST')
        if u'_gerg04_pre_rec' not in _Setuprecord.object_list:
            if u'_gerg04_rec' in _Setuprecord.object_list:
                gerg04()
        if u'_setmod_pre_rec' not in _Setuprecord.object_list:
            if u'_setmod_rec' in _Setuprecord.object_list:
                setmod()

            u"""
@@ -395,10 +395,15 @@ def _load():
             _rp = ctypes.cdll.LoadLibrary(u"/usr/local/lib/librefprop.so")
         except OSError:#either file is not there or file has problem
             global refpropso
-            if refpropso not in globals():
-                print u'can not find "librefprop.so" \n' + \
-                       u'please enter fullpath of "librefprop.so": '
-                refpropso = sys.stdin.readline()
+            if 'refpropso' not in globals():
+    try:
+      #look relative to this file
+      refpropso=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,os.pardir,'REFPROPBinaries/librefprop.so'))
+      _rp = ctypes.cdll.LoadLibrary(refpropso)
+    except:
+            print u'can not find "librefprop.so" \n' + \
+                   u'please enter fullpath of "librefprop.so" (not just its folder path): '
+            refpropso = raw_input()
             _rp = ctypes.cdll.LoadLibrary(unicode(refpropso))
     #confirm platform system is Windows
     elif platform.system() == u'Windows':
@@ -409,7 +414,7 @@ def _load():
             if refpropdll not in globals():
                 print u'can not find "refprop.dll" \n' + \
                        u'please enter fullpath of "refprop.dll": '
-                refpropdll = sys.stdin.readline()
+                refpropdll = raw_input()
             _rp = ctypes.windll.LoadLibrary(unicode(refpropdll))
     #raise error if not defined platform system
     else:
@@ -490,8 +495,12 @@ def setpath(path=None):
     #Linux
     if platform.system()==u'Linux':
         if path == None:
-            #use standard input else user input
-            path = u'/usr/local/lib/refprop/'
+    if 'refpropso' in globals():
+      #use the same directory as librefprop.so is located in
+      path=os.path.dirname(refpropso)+'/'
+    else:
+              #use standard input else user input
+              path = u'/usr/local/lib/refprop/'
         #test if path exist
         os.listdir(path)
     #windows 
            """

        se() #resore SetError
    #confirm platform system is Linux
    if platform.system() == u'Linux':
        _rp = ctypes.cdll.LoadLibrary(u"/usr/local/lib/librefprop.so")##!
        try:
            _rp = ctypes.cdll.LoadLibrary(u"/usr/local/lib/librefprop.so")
        except OSError:#either file is not there or file has problem
            global refpropso
            if refpropso == u'':
                print u'can not find "librefprop.so" \n' + \
                       u'please enter fullpath of "librefprop.so": '
                refpropso = sys.stdin.readline()
            _rp = ctypes.cdll.LoadLibrary(unicode(refpropso))
    #confirm platform system is Windows
    elif platform.system() == u'Windows':
        try:
            _rp = ctypes.windll.LoadLibrary(u'refprop.dll')
        except WindowsError:
            global refpropdll
            if refpropdll == u'':
                print u'can not find "refprop.dll" \n' + \
                       u'please enter fullpath of "refprop.dll": '
                refpropdll = sys.stdin.readline()
            _rp = ctypes.windll.LoadLibrary(unicode(refpropdll))
    #raise error if not defined platform system
    else:
        raise RefpropError(u'undefined platform system')
    #set system path
    setpath()


def getphase(fld):
    u'''Return fluid phase

    input:
        fld--fluid dictionary containing:
            p--pressure
            t--temperature
            x--fluid composition
            q--quality (optional)*
            h--enthalpy (optional)*
            s--entropy (optional)*
                *one of these three needs to be included
    output:
        fluid phase:
            "vapor"--vapor phase
            "saturated vapor"--fluid at dew point
            "gas"--gasious phase (e.g. above critical temperature
            "liquid"--liquid phase
            "saturated liquid"--fluid at bubble point
            "compressible liquid"--(e.g. above critical pressure)
            "Supercritical fluid"
            "2 phase"--both liquid and vapor phase"'''
    _inputerrorcheck(locals())
    #get critical parameters
    crit = critp(fld[u'x'])
    #check if fld above critical pressure
    if fld[u'p'] > crit[u'pcrit']:
        #check if fld above critical pressure
        if fld[u't'] > crit[u'tcrit']:
            return u"Supercritical fluid"
        else:
            return u"compressible liquid"
    #check if fld above critical pressure
    elif fld[u't'] > crit[u'tcrit']:
        return u"gas"
    #check if ['q'] in fld
    if not u'q' in fld.keys():
        if u'h' in fld.keys():
            fld[u'q'] = flsh(u'ph', fld[u'p'], fld[u'h'], fld[u'x'])[u'q']
        elif u's' in fld.keys():
            fld[u'q'] = flsh(u'ps', fld[u'p'], fld[u's'], fld[u'x'])[u'q']
    #check q
    if fld[u'q'] > 1:
        return u"vapor"
    elif fld[u'q'] == 1:
        return u"saturated vapor"
    elif 0 < fld[u'q'] < 1:
        return u"2 phase"
    elif fld[u'q'] == 0:
        return u"saturated liquid"
    elif fld[u'q'] < 0:
        return u"liquid"


def setpath(path=None):
    u'''Set Directory to refprop root containing fluids and mixtures. Default
    value = 'c:/program files/refprop/'. This function must be called before
    SETUP if path is not default. Note, all fluids and mxtures to be filed
    under root/fluids and root/mixtures. Input in string format.

    try and exception will also allow for:
    'c:/program files/refprop/'
    'c:/program files (x86)/refprop/'
    '/usr/local/lib/refprop/' (for Linux)'
    '''
    global _fpath
    #re-use path from globals if no user input
    if path == None and _fpath != u'':
        path = _fpath
    #Linux
    if platform.system()==u'Linux':
        if path == None:
            #use standard input else user input
            path = u'/usr/local/lib/refprop/'
        #test if path exist
        os.listdir(path)
    #windows
    elif platform.system()==u'Windows':
        if path == None:
            #use the standard 2 windows options
            path=u'c:/program files/refprop/'
            #test 1
            try: os.listdir(path)
            except WindowsError:
                path=u'c:/program files (x86)/refprop/'
                #test 2
                os.listdir(path)
        #use the user input
        else: os.listdir(path)
    #set global path value
    _fpath = path
    #set path for refprop
    _setpath(path)


def fluidlib():
    u'''Displays all fluids and mixtures available on root directory. If root
    other then default directories:
            'c:/program files/refprop/'
            'c:/program files (x86)/refprop/'
            '/usr/local/lib/refprop/
    call setpath to correct'''
    print _fluidextention()


def normalize(x):
    u'''Normalize the sum of list x value's to 1'''
    x = [Decimal(each) for each in x]
    while float(sum(x)) != 1:
        norm = sum(x)
        x = [each / norm for each in x]
    return _prop(x = x)


def _setpath(hpth):
    u'''set the path where the fluid files are located

    inputs:
        hpth--location of the fluid files [character*255 variable].

        The path does not need to contain the ending "/" and it can point
        directly to the location where the DLL is stored, if a fluids
        subdirectory (with the corresponding fluid files) is located there.
        Default:
        hpth='C:/Program Files/Refprop/'
        hpth='C:/Program Files (x86)/Refprop/
        hpth='/usr/local/lib/refprop/'
        '''
    _hpth.value = hpth.encode(u'ascii')
    if platform.system() == u'Linux':
        _rp.setpath_(ctypes.byref(_hpth), ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SETPATHdll(ctypes.byref(_hpth), ctypes.c_long(255))


def _fluidextention():
    u"""return fluid library"""
    _fldext = {}
    _fldext[_fpath + u'fluids/'] = [(each[:-4].upper()) for each in
                                   os.listdir(_fpath + u'fluids/') if
                                   fnmatch.fnmatch(each, u'*.FLD')]
    _fldext[_fpath + u'fluids/'].extend([each for each in
                                        os.listdir(_fpath + u'fluids/') if
                                        fnmatch.fnmatch(each, u'*.PPF')])
    _fldext[_fpath + u'mixtures/'] = [(each[:-4].upper()) for each in
                                     os.listdir(_fpath + u'mixtures/') if
                                     fnmatch.fnmatch (each, u'*.MIX')]
    return _fldext


def _prop(**prop):
    global _fixicomp, _setupprop, _set
    prop.update(_setupprop)
    prop.update(_set)

    #one time hfld correction by icomp
    if u'icomp' in prop and u'nc' in prop:
        if prop[u'icomp'] == 0 or prop[u'icomp'] > prop[u'nc']:
            raise RefpropicompError (u'undefined "icomp: ' +
            unicode(prop[u'icomp']) + u'" value, select mixture component ' +
            u'number between 1 and ' + unicode(prop[u'nc']))
        prop[u'icomp'] = [prop[u'icomp'], prop[u'hfld'][prop[u'icomp'] - 1]]

    #one time hfld correction by jcomp
    if u'jcomp' in prop and u'nc' in prop:
        if prop[u'jcomp'] == 0 or prop[u'jcomp'] > prop[u'nc']:
            raise RefpropicompError (u'undefined "jcomp: ' +
            unicode(prop[u'jcomp']) + u'" value, select mixture component ' +
            u'number between 1 and ' + unicode(prop[u'nc']))
        prop[u'jcomp'] = [prop[u'jcomp'], prop[u'hfld'][prop[u'jcomp'] - 1]]

    #multiple time hfld correction by fixicomp / purefld
    if u'fixicomp' in prop:
        _fixicomp = prop[u'fixicomp']
        del prop[u'fixicomp']

    #assign purefluid in prop
    if u'nc' in prop and _fixicomp > prop[u'nc']:
        raise RefpropicompError (u'undefined "icomp: ' +
                                  unicode(_fixicomp) +
                                  u'" value, select mixture component ' +
                                  u'number below ' + unicode(prop[u'nc']))
    elif _fixicomp == 0:
        if u'purefld' in prop: del prop[u'purefld']
    elif u'nc' in prop and 0 < _fixicomp <= prop[u'nc']:
        prop[u'purefld'] = [_fixicomp, prop[u'hfld'][_fixicomp - 1]]

    #raise error
    if u'ierr' in prop:
        _outputierrcheck(prop[u'ierr'], prop[u'herr'], prop[u'defname'], prop)
        prop.__delitem__(u'ierr')
        prop.__delitem__(u'herr')
        prop.__delitem__(u'defname')

    return prop


def _inputerrorcheck(deflocals):
    checkstring = [u'hmxnme', u'hrf', u'htype', u'hmix', u'path', u'routine',
                   u'hmodij', u'hfmix']
    checkint = [u'icomp', u'kph', u'nc', u'ixflag', u'kguess', u'ksat', u'jcomp', u'kq']
    checkfloat = [u't', u'D', u'h0', u's0', u't0', u'p0', u's', u'h', u'e', u'p', u'var1',
                  u'var2', u'tbub', u'tdew', u'pbub', u'pdew', u'Dlbub', u'Dvdew',
                  u'q', u'qkg', u'v']
    checklistcomp = [u'x', u'xkg', u'xbub', u'xdew', u'xlkg', u'xvkg']
    checklist = [u'fij', u'x0']
    checkliststring = [u'hfld', u'hcomp']

    for each in checkstring:
        if each in deflocals and not isinstance(deflocals[each], unicode):
            raise RefpropinputError (u'expect "str" input for ' + unicode(each) +
                                      u' instead of "' +
                                      unicode((deflocals[each]).__class__) +u'"')
    for each in checkint:
        if each in deflocals and not isinstance(deflocals[each], int):
            raise RefpropinputError (u'expect "int" input for ' +
                                      unicode(each) + u' instead of "' +
                                      unicode((deflocals[each]).__class__) +u'"')
    for each in checkfloat:
        if (each in deflocals and not isinstance(deflocals[each], float)
             and not isinstance(deflocals[each], int)):
            raise RefpropinputError (u'expect "float" or "int" input for ' +
                                      unicode(each) + u' instead of "' +
                                      unicode((deflocals[each]).__class__) +u'"')
    for each in checklistcomp:
        if each in deflocals:
            if not deflocals[each]: pass
            else:
                if not isinstance(deflocals[each], list):
                    raise RefpropinputError(u'expect "list" input for ' +
                                             unicode(each) + u' instead of "' +
                                             unicode((deflocals[each]).__class__) +
                                             u'"')
                elif u'_purefld_rec' in _Setuprecord.object_list:
                    if len(deflocals[each]) != _nc_rec.record \
                    and len(deflocals[each]) != 1:
                        raise RefpropicompError(u'input value ' + unicode(each) +
                                                 u' does not match the setup '
                                                 u'fluid selection.')
                elif len(deflocals[each]) != _nc_rec.record:
                    raise RefpropicompError(u'input value ' + unicode(each) +
                                             u' does not match the setup '
                                             u'fluid selection')
                if float(sum(deflocals[each])) != 1:
                    raise RefpropnormalizeError(u'sum input value ' +
                                                 unicode(each) +
                                                 u' is unequal to 1')
    for each in checklist:
        if each in deflocals:
            if not isinstance(deflocals[each], list):
                raise RefpropinputError (u'expect "list" input for ' +
                unicode(each) + u' instead of "' +
                unicode((deflocals[each]).__class__) +u'"')
            else:
                if len(deflocals[each]) > _nmxpar:
                    raise RefpropinputError (u'input value ' + unicode(each) +
                    u' larger then max. value ' + _nmxpar)
    for each in checkliststring:
        if each in deflocals:
            for items in deflocals[each]:
                if isinstance(items, list):
                    for others in items:
                        if not isinstance(others, unicode):
                            raise RefpropinputError (u'expect "list of str"' +
                            u' or "strs' + u''''s" input for ''' + each +
                            u' instead of "' + unicode((others).__class__) +u'"')
                elif not isinstance(items, unicode):
                    raise RefpropinputError (u'expect "list of str" or' +
                    u''' "strs's" input for ''' + each + u' instead of "' +
                    unicode((items).__class__) +u'"')


def _outputierrcheck(ierr, herr, defname, prop):
    #_ierr correction for Linux system, some unknown reason the value is
    # increased by 2**32
    while ierr > 9999:
        ierr -= 2**32
    def mes_string(ERorWA):
        string = u'*' * 80 + u'\n'
        string += u'*' * 80 + u'\n'
        string += ERorWA + u' raised' + u'\n'
        string += u'setup details' + u'\n'
        string += unicode(FluidModel()) + u'\n'
        string += u'refprop dll call details' + u'\n'
        string += unicode(defname) + u'\n'
        string += u'error details' + u'\n'
        string += unicode(ierr) + u'\n'
        string += unicode(herr) + u'\n'
        string += u'prop output' + u'\n'
        string += unicode(prop) + u'\n'
        string += u'*' * 80 + u'\n'*3
        return string
    if ierr < 0 \
    and unicode(SetWarning()) == u'on' \
    and unicode(SetError()) == u'on': #raise warning
        #warning string
        if unicode(SetErrorDebug()) == u'on':
            print mes_string(u'warning')
        raise RefpropdllWarning(herr.decode(u'utf-8'))
    elif ierr > 0 and unicode(SetError()) == u'on': #raise error
        #error string
        if unicode(SetErrorDebug()) == u'on':
            print mes_string(u'error')
        raise RefpropdllError(herr.decode(u'utf-8'))


def _checksetupmodel(model):
    u'Raise warning if multiple models are being set'
    models = []
    #add setmod if called already
    if u'_setmod_rec' in _Setuprecord.object_list:
        models.append(u'setmod')
    #add setktv if called already
    if u'_setktv_rec' in _Setuprecord.object_list:
        models.append(u'setktv')
    #add gerg04 if called already
    if u'_gerg04_rec' in _Setuprecord.object_list:
        models.append(u'gerg04')
    #add called model if not included already
    if model not in models:
        models.append(model)
    #raise warning on multiple model calls and if warning is on
    if len(models) > 1 and unicode(SetWarning()) == u'on':
        raise SetupWarning(u'''Warning, calling multiple model setups (setmod,
        setktv and gerg04 and others) could result in unexpected results.
        Furthermore these multiple model calls are not supported by function
        "resetup' and consequentely in the extention module "multiRP"''')


def resetup(prop, force=False):
    u"""Resetup models and re-initialize  arrays.

    This will compare the loaded models vs requested model and re-setup
    refprop models if deemed required in the following sequence:
        setmod / gerg04
        setup
        setktv
        preos
        setaga
        setref
        purefld

    This enables calculating of dual fluid flows through exchangers, static
    mixures etc.

    input:
        props--standard dictinary output from refprop functions
        force--force resetup (True or False (standard input)"""
    global _gerg04_pre_rec, _setmod_pre_rec
    prop = setup_details(prop)
    #only resetup if loaded models are unequal to request (or force)
    if force == True or setup_setting() != prop:
        #delete any pre-setup request such as gerg04 and setmod
        if u'_setmod_pre_rec' in _Setuprecord.object_list:
            _setmod_pre_rec = None
        if u'_gerg04_pre_rec' in _Setuprecord.object_list:
            _gerg04_pre_rec = None

        #initialize setmod if deemed req.
        if u'setmod' in prop:
            setmod(prop[u'setmod'][u'htype'],
                   prop[u'setmod'][u'hmix'],
                   prop[u'setmod'][u'hcomp'])

        #initialize gerg04 if deemed req.
        if u'gerg04' in prop:
            gerg04(prop[u'gerg04'][u'ixflag'])

        #initialize setup:
        setup(prop[u'hrf'],  prop[u'hfld'], hfmix=prop[u'hfmix'])

        #initialize setktv
        if u'setktv' in prop:
            setktv(prop[u'setktv'][u'icomp'],
                   prop[u'setktv'][u'jcomp'],
                   prop[u'setktv'][u'hmodij'],
                   prop[u'setktv'][u'fij'],
                   prop[u'setktv'][u'hfmix'])

        #initialize preos
        if u'preos' in prop:
            preos(prop[u'preos'][u'ixflag'])

        #initialize setaga
        if u'setaga' in prop:
            setaga()

        #initialize setref
        if u'setref' in prop:
            if not u'ixflag' in prop[u'setref']:
                prop[u'setref'][u'ixflag'] = 1
            if not u'x0' in prop[u'setref']:
                prop[u'setref'][u'x0'] = [1]
            if not u'h0' in prop[u'setref']:
                prop[u'setref'][u'h0'] = 0
            if not u's0' in prop[u'setref']:
                prop[u'setref'][u's0'] = 0
            if not u't0' in prop[u'setref']:
                prop[u'setref'][u't0'] = 273
            if not u'p0' in prop[u'setref']:
                prop[u'setref'][u'p0'] =100
            setref(prop[u'setref'][u'hrf'][0],
                   prop[u'setref'][u'ixflag'],
                   prop[u'setref'][u'x0'],
                   prop[u'setref'][u'h0'],
                   prop[u'setref'][u's0'],
                   prop[u'setref'][u't0'],
                   prop[u'setref'][u'p0'])
            if len(prop[u'setref'][u'hrf']) == 2:
                setref(prop[u'setref'][u'hrf'][1],
                       prop[u'setref'][u'ixflag'],
                       prop[u'setref'][u'x0'],
                       prop[u'setref'][u'h0'],
                       prop[u'setref'][u's0'],
                       prop[u'setref'][u't0'],
                       prop[u'setref'][u'p0'])

        #initialize purefld
        if u'purefld' in prop:
            purefld(prop[u'purefld'][0])

        #reset SetError
        if u'SetError' in prop:
            SetError.off()
        else: SetError.on()

        #reset SetWarning
        if u'SetWarning' in prop:
            SetWarning.off()
        else: SetWarning.on()

        #reset SetErrorDebug
        if u'SetDebug' in prop:
            SetErrorDebug.on()
        else: SetErrorDebug.off()

    return setup_details(_prop())


def setup_setting():
    u"""Returns current loaded setup settings
    output--Minimized dict. with basic refprop settings"""
    return setup_details(_prop())


def setup_details(prop):
    u'''Returns basic setup details of input fluid.

    Setup details from the following module functions:
        setmod / gerg04
        setup
        setktv
        preos
        setags
        setref
        purefld

    input:
        prop--standard dictinary output from refprop functions
    output
        prop--Minimized dict. with basic refprop settings'''
    prps = {}

    if prop.__class__ == dict:
        #setmod
        if u'setmod' in prop:
            prps[u'setmod'] = prop[u'setmod']

        #gerg04
        if u'gerg04' in prop:
            prps[u'gerg04'] = prop[u'gerg04']

        #setup
        if u'hrf' in prop:
            prps[u'hrf'] = prop[u'hrf']
        if u'hfld' in prop:
            prps[u'hfld'] = prop[u'hfld']
        if u'hfmix' in prop:
            prps[u'hfmix'] = prop[u'hfmix']
        if u'hmxnme' in prop:
            prps[u'hmxnme'] = prop[u'hmxnme']
        if u'nc' in prop:
            prps[u'nc'] = prop[u'nc']

        #setktv
        if u'setktv' in prop:
            prps[u'setktv'] = prop[u'setktv']

        #preos
        if u'preos' in prop:
            prps[u'preos'] = prop[u'preos']

        #setaga
        if u'setaga' in prop:
            prps[u'setaga'] = prop[u'setaga']

        #setref
        if u'setref' in prop:
            prps[u'setref'] = prop[u'setref']

        #purefld
        if u'purefld' in prop:
            prps[u'purefld'] = prop[u'purefld']

        #seterror
        if u'SetError' in prop:
            prps[u'SetError'] = u'off'

        #setwarning
        if u'SetWarning' in prop:
            prps[u'SetWarning'] = u'off'

        #seterrordebug
        if u'SetDebug' in prop:
            prps[u'SetDebug'] = u'on'

    return prps


def _test():
    u"""execute detailed test run of refprop"""
    import rptest
    rptest.settest(u'refprop')

def test(criteria=0.00001):
    u'''verify that the user's computer is returning proper calculations The
    calculated values are compared with NIST calculated values.

    The percent difference between Calculated and NIST should be within the
    acceptance criteria '0.00001' is standard.

    input:
        criteria--acceptance criteria between Calculated and NIST value
    output:
        print screen of NIST value, Calculated value, abs. difference and
        True / False for acceptance.'''
    global testresult
    truefalse = True
    testresult = u''

    #create def for printout
    def printresults(nist, calculated, truefalse):
        global testresult
        calculated = float(calculated)
        testresult += u'\nNIST = ' + unicode(nist)
        testresult += u'\nCalculated = ' + unicode(calculated)
        testresult += u'\nabs relative difference = ' + unicode(
            abs((nist - calculated) / nist))
        testresult += u'\n' + unicode(abs((nist - calculated) / nist) <
            criteria) + u'\n\n'
        truefalse = truefalse and abs((nist - calculated) / nist) < criteria
        return truefalse

    #SetWarning off due to many warnings displayed
    if unicode(SetWarning()) == u'off':
        sw = SetWarning.off
    elif unicode(SetWarning()) == u'on':
        sw = SetWarning.on
        SetWarning.off()

    #test no. 1
    prop = setup(u'def', u'air')
    prop = wmol(prop[u'x'])
    testresult += u'check molar mass of air'
    truefalse = printresults(28.958600656, prop[u'wmix'], truefalse)

    #test no. 2
    setup(u'def', u'argon')
    prop = flsh(u'pD', 2 * 1000, 15 / wmol([1])[u'wmix'], [1])
    testresult += u'check temperature of Argon'
    truefalse = printresults(637.377588657857, prop[u't'], truefalse)

    #test no. 3
    setup(u'def', u'r134a')
    prop = flsh(u'tD', 400, 50 / wmol([1])[u'wmix'], [1])
    testresult += u'check pressure of r134a'
    truefalse = printresults(1.45691892789737, prop[u'p'] / 1000, truefalse)

    ##test no. 4
    #setup('def', 'ethylene')
    #setref(ixflag=2, x0=[1])
    #wmix = wmol([1])['wmix']
    #prop = flsh('ts', 300, 3 * wmix, [1])
    #testresult += 'check enthalphy of ethylene'
    #truefalse = printresults(684.996521090598, prop['h'] / wmix, truefalse)
    ##NIST(as per spreadsheet) = 684.996521090598
    ##Calculated(confirmed by NIST GUI) = 651.5166149584808

    #test no. 5
    setup(u'def', u'oxygen')
    prop = trnprp(100, tprho(100, 1 * 1000, [1], 1)[u'D'], [1])
    testresult += u'check Viscosity of Oxygen'
    truefalse = printresults(153.886680663753, prop[u'eta'], truefalse)

    #test no. 6
    setup(u'def', u'nitrogen')
    prop = trnprp(100, satt(100, [1], 1)[u'Dliq'], [1])
    testresult += u'check Thermal Conductivity of Nitrogen'
    truefalse = printresults(100.111748964945, prop[u'tcx'] * 1000, truefalse)

    #test no. 7
    setup(u'def', u'air')
    x = setup(u'def', u'air')[u'x']
    setref(ixflag=2, x0=x)
    wmix = wmol(x)[u'wmix']
    prop = tprho(((70 - 32) * 5 / 9) + 273.15, 14.7 / 14.50377377 * (10**5) /
                        1000, x)
    testresult += u'check Density of Air'
    truefalse = printresults(0.0749156384666842, prop[u'D'] * wmix * 0.062427974,
                             truefalse)

    #test no. 8
    setup(u'def', u'R32', u'R125')
    x = [0.3, 0.7]
    u'''Use the following line to calculate enthalpies and entropies on a
    reference state based on the currently defined mixture, or to change to
    some other reference state. The routine does not have to be called, but
    doing so will cause calculations to be the same as those produced from
    the graphical interface for mixtures.'''
    setref(ixflag=2, x0=x)
    prop = flsh(u'ps', 10 * 1000, 110, x)
    testresult += u'check enthalpy of R32 / R125'
    truefalse = printresults(23643.993624382, prop[u'h'], truefalse)

    #test no. 9
    setup(u'def', u'ethane', u'butane')
    x = xmole([0.5, 0.5])[u'x']
    setref(ixflag=2, x0=x)
    wmix = wmol(x)[u'wmix']
    prop = flsh(u'dh', 30 * 0.45359237 / 0.028316846592 / wmix, 283 *
                    1.05435026448889 / 0.45359237 * wmix, x)
    testresult += u'check Temperature of Ethene / Butane'
    truefalse = printresults(298.431320311048, ((prop[u't'] - 273.15) * 9 / 5) + 32,
                             truefalse)

    #test no. 10
    setup(u'def', u'ammonia', u'water')
    x = [0.4, 0.6]
    setref(ixflag=2, x0=x)
    prop = flsh(u'tp', ((300 - 32) * 5 / 9) + 273.15, 10000 / 14.50377377 *
                    (10**5) / 1000, x)
    testresult += u'check speed of Sound of Ammonia / water'
    truefalse = printresults(5536.79144924071, prop[u'w'] * 1000 / 25.4 / 12,
                             truefalse)

    #test no. 11
    setup(u'def', u'r218', u'r123')
    x = [0.1, 0.9]
    setref(ixflag=2, x0=x)
    wmix = wmol(x)[u'wmix']
    prop = flsh(u'ph', 7 * 1000, 180 * wmix, x)
    testresult += u'check Density of R218 / R123'
    truefalse = printresults(1.60040403489036, prop[u'D'] * wmix / 1000, truefalse)

    #test no. 12
    setup(u'def', u'methane', u'ethane')
    x = xmole(normalize([40, 60])[u'x'])[u'x']
    wmix = wmol(x)[u'wmix']
    prop = flsh(u'tD', 200, 300 / wmix, x)
    prop = qmass(prop[u'q'], prop[u'xliq'], prop[u'xvap'])
    testresult += u'check quality of methane / ethane'
    truefalse = printresults(0.0386417701326453, prop[u'qkg'], truefalse)

    #test no. 13
    setup(u'def', u'methane', u'ethane')
    x = xmole(normalize([40, 60])[u'x'])[u'x']
    setref(ixflag=2, x0=x)
    prop = flsh(u'tp', 200, 2.8145509 * 1000, x)
    prop = qmass(prop[u'q'], prop[u'xliq'], prop[u'xvap'])
    testresult += u'check quality of methane / ethane'
    truefalse = printresults(0.0386406167132601, prop[u'qkg'], truefalse)
    #NIST = 0.0386406167132601
    #Calculated = 1.0297826927241274

    #test no. 14
    setup(u'def', u'methane', u'ethane')
    x = xmole(normalize([40, 60])[u'x'])[u'x']
    setref(ixflag=2, x0=x)
    prop = flsh(u'tp', 200, 2814.5509, x)
    testresult += u'check quality of methane / ethane'
    truefalse = printresults(0.0500926636198064, prop[u'q'], truefalse)

    #test no. 15
    setup(u'def', u'octane')
    wmix = wmol([1])[u'wmix']
    prop = satt(100 + 273.15, [1])
    Dliq = prop[u'Dliq']
    Dvap = prop[u'Dvap']
    prop = therm(100 + 273.15, Dliq, [1])
    hliq = prop[u'h']
    prop = therm(100 + 273.15, Dvap, [1])
    hvap = prop[u'h']
    testresult += u'check Heat of Vaporization of Octane'
    truefalse = printresults(319.167499870568, (hvap - hliq) / wmix, truefalse)

    #test no. 16
    setup(u'def', u'butane', u'hexane')
    x = [0.25, 0.75]
    setref(ixflag=2, x0=x)
    testresult += u'check viscosity of Butane / Hexane'
    truefalse = printresults(283.724837443674,
                             trnprp(300, flsh(u'th', 300, -21 * wmol(x)[u'wmix'],
                                              x, 2)[u'D'], x)[u'eta'],
                             truefalse)

    #test no. 17
    setup(u'def', u'CO2', u'nitrogen')
    x = xmole([0.5, 0.5])[u'x']
    setref(ixflag=2, x0=x)
    wmix = wmol(x)[u'wmix']
    prop = flsh(u'th', 250, 220 * wmix, x, 2)
    prop = trnprp(250, prop[u'D'], x)
    testresult += u'check Thermal Conductivity of CO2 / Nitrogen'
    truefalse = printresults(120.984794685581, prop[u'tcx'] * 1000, truefalse)

    #test no. 18
    setup(u'def', u'ethane', u'propane')
    prop = satt(300, [0.5, 0.5])
    prop = dielec(300, prop[u'Dvap'], [0.5, 0.5])
    testresult += u'check Dielectric Constant of Ethane / Propane'
    truefalse = printresults(1.03705806204418, prop[u'de'], truefalse)

    #test no. 19
    prop = setup(u'def', u'R410A')
    testresult += u'check Mole Fraction of R410A'
    truefalse = printresults(0.697614699375863, prop[u'x'][0], truefalse)

    #test no. 20
    prop = xmass(prop[u'x'])
    testresult += u'check mass Fraction of R410A'
    truefalse = printresults(0.5, prop[u'xkg'][0], truefalse)

    #test no. 21
    prop = xmole(prop[u'xkg'])
    testresult += u'check mole Fraction of R410A'
    truefalse = printresults(0.697614699375862, prop[u'x'][0], truefalse)

    #test no. 21
    setup(u'def', u'Methane', u'Ethane', u'Propane', u'Butane')
    x = [0.7, 0.2, 0.05, 0.05]
    setref(ixflag=2, x0=x)
    wmix = wmol(x)[u'wmix']
    prop = flsh(u'td', 150, 200 / wmix, x)
    Dliq = prop[u'Dliq']
    wmix = wmol(prop[u'xliq'])[u'wmix']
    testresult += u'check Liquid Density of Methane / Ethane / Propane / Butane'
    truefalse = printresults(481.276038325628, Dliq * wmix, truefalse)

    #restore SetWarning to original value
    sw()

    return(truefalse)


def psliq(p, s, x):
    u"""flsh1 calculations with boundery check, raise RefpropinputError when
    input is outside bounderies

    Inputs:
        p--pressure [kPa]
        s--entropy [J/(mol*K)]
        x--composition [array of mol frac]"""
    #check if input is in critical region
    pcrit = critp(x)[u'pcrit']
    if p > pcrit:
        raise RefpropinputError(u'p value input is critical condition')

    #calculate the properties (t and D)
    prop = flsh1(u'ps', p, s, x, 1)
    t = prop[u't']
    D = prop[u'D']

    #check if input is with liquid stage
    tbub = satp(p, x, 1)[u't']
    if t >= tbub:
        raise RefpropinputError(u'value input is not liquid condition')

    #check if input is with general refprop bounderies
    try:
        limitx(x, u'EOS', t, D, p)
    except RefpropWarning:
        pass

    #get remaining values
    prop = therm(t, D, x)

    #add q
    prop[u'q'] = -1

    #correct input values
    prop[u'p'] = p
    prop[u's'] = s

    #return full properties
    return prop


def psvap(p, s, x):
    u"""flsh1 calculations with boundery check, raise RefpropinputError when
    input is outside bounderies

    Inputs:
        p--pressure [kPa]
        s--entropy [J/(mol*K)]
        x--composition [array of mol frac]"""
    #check if input is in critical region (pressure)
    prop = critp(x)
    pcrit = prop[u'pcrit']
    tcrit = prop[u'tcrit']
    if p > pcrit:
        raise RefpropinputError(u'p value input is critical condition')

    #calculate the properties (t and D)
    prop = flsh1(u'ps', p, s, x, 2)
    t = prop[u't']
    D = prop[u'D']

    #check if input is in critical region (temperature)
    if t > tcrit:
        raise RefpropinputError(u'value input is critical condition')

    #check if input is with gas stage
    tdew = satp(p, x, 2)[u't']
    if t <= tdew:
        raise RefpropinputError(u'value input is not gas condition')

    #check if input is with general refprop bounderies
    try:
        limitx(x, u'EOS', t, D, p)
    except RefpropWarning:
        pass

    #get values
    prop = therm(t, D, x)

    #add q
    prop[u'q'] = 2

    #correct input values
    prop[u'p'] = p
    prop[u's'] = s

    #return full properties
    return prop


def ps2ph(p, s, x):
    u"""flsh2 calculations with boundery check, raise RefpropinputError when
    input is outside bounderies

    Inputs:
        p--pressure [kPa]
        s--entropy [J/(mol*K)]
        x--composition [array of mol frac]"""
    #check if input is in critical region
    pcrit = critp(x)[u'pcrit']
    if p > pcrit:
        raise RefpropinputError(u'p value input is critical condition')

    #calculate the properties
    prop = _abfl2(u'ps', p, s, x)
    D = prop[u'D']
    t = prop[u't']
    Dliq = prop[u'Dliq']
    Dvap = prop[u'Dvap']
    q = prop[u'q']
    xliq = prop[u'xliq']
    xvap = prop[u'xvap']

    #calculate properties at bubble point
    propliq = therm(t, Dliq, xliq)

    #calculate properties at cond. point
    propvap = therm(t, Dvap, xvap)

    #calculate e and h
    prop[u'e'] = (1 - q) * propliq[u'e'] + q * propvap[u'e']
    prop[u'h'] = (1 - q) * propliq[u'h'] + q * propvap[u'h']

    #check if input is within 2 phase stage
    tbub = prop[u'tbub']
    tdew = prop[u'tdew']
    if not tbub < t < tdew:
        raise RefpropinputError(u'value input is not 2-phase condition')

    #check if input is with general refprop bounderies
    try:
        limitx(x, u'EOS', t, D, p)
    except RefpropWarning:
        pass

    #return values
    return prop


def phliq(p, h, x):
    u"""flsh1 calculations with boundery check, raise RefpropinputError when
    input is outside bounderies

    Inputs:
        p--pressure [kPa]
        h--enthalpy [J/mol]
        x--composition [array of mol frac]"""
    #check if input is in critical region
    pcrit = critp(x)[u'pcrit']
    if p > pcrit:
        raise RefpropinputError(u'p value input is critical condition')

    #calculate the properties (t and D)
    prop = flsh1(u'ph', p, h, x, 1)
    t = prop[u't']
    D = prop[u'D']

    #check if input is with liquid stage
    tbub = satp(p, x, 1)[u't']
    if t >= tbub:
        raise RefpropinputError(u'value input is not liquid condition')

    #check if input is with general refprop bounderies
    try:
        limitx(x, u'EOS', t, D, p)
    except RefpropWarning:
        pass

    #get values
    prop = therm(t, D, x)

    #add q
    prop[u'q'] = -1

    #correct input values
    prop[u'p'] = p
    prop[u'h'] = h

    #return full properties
    return prop


def phvap(p, h, x):
    u"""flsh1 calculations with boundery check, raise RefpropinputError when
    input is outside bounderies

    Inputs:
        p--pressure [kPa]
        h--enthalpy [J/mol]
        x--composition [array of mol frac]"""
    #check if input is in critical region (pressure)
    prop = critp(x)
    pcrit = prop[u'pcrit']
    tcrit = prop[u'tcrit']
    if p > pcrit:
        raise RefpropinputError(u'p value input is critical condition')

    #calculate the properties (t and D)
    prop = flsh1(u'ph', p, h, x, 2)
    t = prop[u't']
    D = prop[u'D']

    #check if input is in critical region (temperature)
    if t > tcrit:
        raise RefpropinputError(u'value input is critical condition')

    #check if input is with gas stage
    tdew = satp(p, x, 2)[u't']
    if t <= tdew:
        raise RefpropinputError(u'value input is not gas condition')

    #check if input is with general refprop bounderies
    try:
        limitx(x, u'EOS', t, D, p)
    except RefpropWarning:
        pass

    #get values
    prop = therm(t, D, x)

    #add q
    prop[u'q'] = 2

    #correct input values
    prop[u'p'] = p
    prop[u'h'] = h

    #return full properties
    return prop


def ph2ph(p, h, x):
    u"""flsh2 calculations with boundery check, raise RefpropinputError when
    input is outside bounderies

    Inputs:
        p--pressure [kPa]
        h--enthalpy [J/mol]
        x--composition [array of mol frac]"""
    #check if input is in critical region
    pcrit = critp(x)[u'pcrit']
    if p > pcrit:
        raise RefpropinputError(u'p value input is critical condition')

    #calculate the properties
    prop = _abfl2(u'ph', p, h, x)
    D = prop[u'D']
    t = prop[u't']
    Dliq = prop[u'Dliq']
    Dvap = prop[u'Dvap']
    q = prop[u'q']
    xliq = prop[u'xliq']
    xvap = prop[u'xvap']

    #calculate properties at bubble point
    propliq = therm(t, Dliq, xliq)

    #calculate properties at cond. point
    propvap = therm(t, Dvap, xvap)

    #calculate e and h
    prop[u'e'] = (1 - q) * propliq[u'e'] + q * propvap[u'e']
    prop[u's'] = (1 - q) * propliq[u's'] + q * propvap[u's']

    #check if input is within 2 phase stage
    tbub = prop[u'tbub']
    tdew = prop[u'tdew']
    if not tbub < t < tdew:
        raise RefpropinputError(u'value input is not 2-phase condition')

    #check if input is with general refprop bounderies
    try:
        limitx(x, u'EOS', t, D, p)
    except RefpropWarning:
        pass

    #return values
    return prop


#REFPROP functions
def setup(hrf, *hfld, **_3to2kwargs):
    if 'hfmix' in _3to2kwargs: hfmix = _3to2kwargs['hfmix']; del _3to2kwargs['hfmix']
    else: hfmix = u'HMX.BNC'
    u'''Define models and initialize arrays.
    A call to this routine is required.

    Inputs 'in string format':
        hrf - reference state for thermodynamic calculations
            'def' : Default reference state as specified in fluid file is
                applied to each pure component.
            'nbs' : h,s = 0 at pure component normal boiling point(s).
            'ash' : h,s = 0 for sat liquid at -40 C (ASHRAE convention)
            'iir' : h = 200, s = 1.0 for sat liq at 0 C (IIR convention) Other
                choises are possible but require a separate call to SETREF
        *hfld - file names specifying fluid mixture components
            select from user fluid.FLD and mixture.MIX files at root directory
            input without extention.
            Pseudo-Pure Fluids (PPF) files are required to have the extention
            included
        hfmix--file name [character*255] containing parameters for the binary
            mixture model'''
    global _setup_rec, _setmod_rec, _nc_rec, _setupprop, _gerg04_rec

    _inputerrorcheck(locals())

    #define setup record for Fluidmodel
    _setup_rec = _Setuprecord(copy.copy(locals()), u'_setup_rec')

    defname = sys._getframe(0).f_code.co_name, locals()

    #empty global setup storage for new population
    _setupprop = {}

    #load refprop shared library
    _load()

    _hrf.value = hrf.upper().encode(u'ascii')
    if hfmix == u'HMX.BNC':
        _hfmix.value = (_fpath + u'fluids/HMX.BNC').encode(u'ascii')
    else: _hfmix.value = hfmix.encode(u'ascii')

    fluidname = u''
    listhfld = []

    #create listing of input *hfld (in either list format or *arg string format)
    for each in hfld:
        if each.__class__ is list:
            for other in each:
                listhfld.append(other.upper())
        elif each.__class__ is unicode:
            listhfld.append(each.upper())

    #create RP input format with file directory structure and file extention
    for each in listhfld:
        if _fluidextention()[_fpath + u'fluids/'].__contains__(each):
            if each[-4:] == u'.PPF':
                fluidname += _fpath + u'fluids/' + each + u'|'
            else: fluidname += _fpath + u'fluids/' + each + u'.FLD|'
        elif _fluidextention()[_fpath + u'mixtures/'].__contains__(each):
            fluidname += _fpath + u'mixtures/' + each + u'.MIX|'

    _nc.value = len(listhfld)
    _nc_rec = _Setuprecord(_nc.value, u'_nc_rec')
    _hfld.value = fluidname.encode(u'ascii')

    #determine if SETMOD needs to be called
    if u'_setmod_pre_rec' in _Setuprecord.object_list:
        #call setmod
        ierr, herr, defname_setmod = _setmod(_nc.value,
                                             _setmod_pre_rec.record[u'htype'],
                                             _setmod_pre_rec.record[u'hmix'],
                                             _setmod_pre_rec.record[u'hcomp'])

        _prop(ierr = ierr, herr = herr, defname = defname_setmod)

    #reset SETMOD from record
    elif u'_setmod_rec' in _Setuprecord.object_list:
        _setmod_rec = None

    #determine if GERG04 needs to be called
    if u'_gerg04_pre_rec' in _Setuprecord.object_list:
        ierr, herr, defname_gerg04 = _gerg04(_nc.value,
                                             _gerg04_pre_rec.record[u'ixflag'])

        _prop(ierr = ierr, herr = herr, defname = defname_gerg04)

    #reset GERG04 from record
    elif u'_gerg04_rec' in _Setuprecord.object_list:
        _gerg04_rec = None

    #determine standard mix (handled by setmix) or user defined mixture
    #(handled by setupdll)
    if _hfld.value.decode(u'utf-8').__contains__(u'.MIX|'):
        if len(listhfld) > 1:
            raise RefpropinputError (u'too many standard mixture input, ' +
            u'can only select one')
        for item in listhfld:
            mix = unicode(item)
        return _setmix(mix, hrf, hfmix)
    else:
        if u'hmxnme' in _setupprop:
            _setupprop.__delitem__(u'hmxnme')
        if platform.system() == u'Linux':
            _rp.setup0_(ctypes.byref(_nc),
                        ctypes.byref(_hfld),
                        ctypes.byref(_hfmix),
                        ctypes.byref(_hrf),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(10000),
                        ctypes.c_long(255),
                        ctypes.c_long(3),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.SETUPdll(ctypes.byref(_nc),
                         ctypes.byref(_hfld),
                         ctypes.byref(_hfmix),
                         ctypes.byref(_hrf),
                         ctypes.byref(_ierr),
                         ctypes.byref(_herr),
                         ctypes.c_long(10000),
                         ctypes.c_long(255),
                         ctypes.c_long(3),
                         ctypes.c_long(255))
        _setupprop[u'hfld'], _setupprop[u'nc'] = listhfld, len(listhfld)
        _setupprop[u'hrf'], _setupprop[u'hfmix'] = hrf.upper(), hfmix
        return _prop(ierr = _ierr.value, herr = _herr.value, defname = defname)


def setmod(htype=u'NBS', hmix=u'NBS', *hcomp):
    u'''Set model(s) other than the NIST-recommended ('NBS') ones.

    This subroutine must be called before SETUP; it need not be called at
    all if the default (NIST-recommended) models are desired.

    inputs 'in string format':
        htype - flag indicating which models are to be set [character*3]:
            'EOS':  equation of state for thermodynamic properties
            'ETA':  viscosity
            'TCX':  thermal conductivity
            'STN':  surface tension
            'NBS':  reset all of the above model types and all subsidiary
                component models to 'NBS'; values of hmix and hcomp are ignored
        hmix--mixture model to use for the property specified in htype
            [character*3]:
            ignored if number of components = 1
            some allowable choices for hmix:
                'NBS':  use NIST recommendation for specified fluid/mixture
                'HMX':  mixture Helmholtz model for thermodynamic properties
                'ECS':  extended corresponding states for viscosity or therm. cond.
                'STX':  surface tension mixture model
        hcomp--component model(s) to use for property specified in htype
            [array (1..nc) of character*3]:
                'NBS':  NIST recommendation for specified fluid/mixture
            some allowable choices for an equation of state:
                'FEQ':  Helmholtz free energy model
                'BWR':  pure fluid modified Benedict-Webb-Rubin (MBWR)
                'ECS':  pure fluid thermo extended corresponding states
            some allowable choices for viscosity:
                'ECS':  extended corresponding states (all fluids)
                'VS1':  the 'composite' model for R134a, R152a, NH3, etc.
                'VS2':  Younglove-Ely model for hydrocarbons
                'VS4':  Generalized friction theory of Quinones-Cisneros and
                    Deiters
                'VS5':  Chung et al. (1988) predictive model
            some allowable choices for thermal conductivity:
                'ECS':  extended corresponding states (all fluids)
                'TC1':  the 'composite' model for R134a, R152a, etc.
                'TC2':  Younglove-Ely model for hydrocarbons
                'TC5':  Chung et al. (1988) predictive model
            some allowable choices for surface tension:
                'ST1':  surface tension as f(tau); tau = 1 - T/Tc'''
    global _setmod_pre_rec
    _inputerrorcheck(locals())

    #hcomp correction
    #no input for hcomp
    if len(hcomp) == 0:
        hcomp = []
    #list input for hcomp
    elif hcomp[0].__class__ is list:
        hcomp = hcomp[0]
    #str's input for hcomp
    else:
        hcomp = [each for each in hcomp]

    #define setup record for FluidModel
    _setmod_pre_rec = _Setuprecord(copy.copy(locals()), u'_setmod_pre_rec')


def _setmod(nc, htype, hmix, hcomp):
    global _setmod_rec, _setmod_pre_rec, _setupprop

    #verify multiple model calls
    _checksetupmodel(u'setmod')

    defname = sys._getframe(0).f_code.co_name, locals()

    #define setup record for FluidModel
    if u'_setmod_pre_rec' in _Setuprecord.object_list:
        if htype.upper() == u'NBS':
            if u'_setmod_rec' in _Setuprecord.object_list:
                _setmod_rec = None
            if u'setmod' in _setupprop:
                _setupprop.__delitem__(u'setmod')
        else:
            _setmod_rec = _Setuprecord(_setmod_pre_rec.record, u'_setmod_rec')
            if nc == 1:
                _setmod_rec.record.__delitem__(u'hmix')
            _setupprop[u'setmod'] = _setmod_rec.record

        _setmod_pre_rec = None

    _nc.value = nc
    _htype.value = htype.encode(u'ascii')
    _hmix.value = hmix.encode(u'ascii')
    for each in xrange(len(hcomp)):
        _hcomp[each].value = hcomp[each].encode(u'ascii')
    if platform.system() == u'Linux':
        _rp.setmod_(ctypes.byref(_nc),
                        ctypes.byref(_htype),
                        ctypes.byref(_hmix),
                        ctypes.byref(_hcomp),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(3),
                        ctypes.c_long(3),
                        ctypes.c_long(3),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SETMODdll(ctypes.byref(_nc),
                        ctypes.byref(_htype),
                        ctypes.byref(_hmix),
                        ctypes.byref(_hcomp),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(3),
                        ctypes.c_long(3),
                        ctypes.c_long(3),
                        ctypes.c_long(255))
    return _ierr.value, _herr.value, defname

def gerg04(ixflag=0):
    u'''set the pure model(s) to those used by the GERG 2004 formulation.

    This subroutine must be called before SETUP; it need not be called
    at all if the default (NIST-recommended) models are desired.
    To turn off the GERG settings, call this routine again with iflag=0,
    and then call the SETUP routine to reset the parameters of the equations
    of state.

    inputs:
        ixflag--set to 1 to load the GERG 2004 equations, set to 0 for defaults'''
    global _gerg04_pre_rec

    _inputerrorcheck(locals())

    _gerg04_pre_rec = _Setuprecord(copy.copy(locals()), u'_gerg04_pre_rec')

    if not (ixflag == 0 or ixflag == 1):
        raise RefpropinputError(u'ixflag value for function "gerg04" ' +
                                 u'should either be 0 (default) or 1')

def _gerg04(nc, ixflag):
    global _gerg04_rec, _gerg04_pre_rec, _setupprop

    #verify multiple model calls
    _checksetupmodel(u'gerg04')

    defname = sys._getframe(0).f_code.co_name, locals()

    #define setup record for FluidModel
    if u'_gerg04_pre_rec' in _Setuprecord.object_list:
        if ixflag == 1:
            _gerg04_rec = _Setuprecord(_gerg04_pre_rec.record, u'_gerg04_rec')
            _setupprop[u'gerg04'] = _gerg04_pre_rec.record
        if ixflag == 0:
            if u'_gerg04_rec' in _Setuprecord.object_list:
                _gerg04_rec = None
            if u'gerg04' in _setupprop:
                _setupprop.__delitem__(u'gerg04')
        _gerg04_pre_rec = None

    if ixflag == 1:
        _nc.value = nc
        _ixflag.value = ixflag
        if platform.system() == u'Linux':
            _rp.gerg04_(ctypes.byref(_nc),
                        ctypes.byref(_ixflag),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.GERG04dll(ctypes.byref(_nc),
                          ctypes.byref(_ixflag),
                          ctypes.byref(_ierr),
                          ctypes.byref(_herr),
                          ctypes.c_long(255))
        return _ierr.value, _herr.value, defname
    #system tweak as refprop call gerg04(ixflag=0) does not reset properly
    elif ixflag == 0: return 0, u'', defname


def setref(hrf=u'DEF', ixflag=1, x0=[1], h0=0, s0=0, t0=273, p0=100):
    u'''set reference state enthalpy and entropy

    This subroutine must be called after SETUP; it need not be called at all
    if the reference state specified in the call to SETUP is to be used.

    inputs:
        hrf--reference state for thermodynamic calculations [character*3]
            'NBP':  h,s = 0 at normal boiling point(s)
            'ASH':  h,s = 0 for sat liquid at -40 C (ASHRAE convention)
            'IIR':  h = 200, s = 1.0 for sat liq at 0 C (IIR convention)
            'DEF':  default reference state as specified in fluid file is
                applied to each component (ixflag = 1 is used)
            'OTH':  other, as specified by h0, s0, t0, p0 (real gas state)
            'OT0':  other, as specified by h0, s0, t0, p0 (ideal gas state)
            '???':  change hrf to the current reference state and exit.
        ixflag--composition flag:
            1 = ref state applied to pure components
            2 = ref state applied to mixture icomp
        following input has meaning only if ixflag = 2
            x0--composition for which h0, s0 apply; list(1:nc) [mol frac]
                this is useful for mixtures of a predefined composition, e.g.
                refrigerant blends such as R410A
        following inputs have meaning only if hrf = 'OTH'
            h0--reference state enthalpy at t0,p0 {icomp} [J/mol]
            s0--reference state entropy at t0,p0 {icomp} [J/mol-K]
            t0--reference state temperature [K]
                t0 = -1 indicates saturated liquid at normal boiling point
                    (bubble point for a mixture)
            p0--reference state pressure [kPa]
                p0 = -1 indicates saturated liquid at t0 {and icomp}
                p0 = -2 indicates saturated vapor at t0 {and icomp}'''
    _inputerrorcheck(locals())
    global _setref_rec, _setupprop

    #define setup record for FluidModel
    if hrf.upper() != u'DEF':
        _setref_rec = _Setuprecord(copy.copy(locals()), u'_setref_rec')
    elif u'setref_rec' in _Setuprecord.object_list:
        _setref_rec = None

    defname = sys._getframe(0).f_code.co_name, locals()

    for each in xrange(_maxcomps): _x0[each] = 0
    for each in xrange(len(x0)): _x0[each] = x0[each]
    _hrf.value = hrf.upper().encode(u'ascii')
    _ixflag.value = ixflag
    _h0.value, _s0.value, _t0.value, _p0.value = h0, s0, t0, p0
    if platform.system() == u'Linux':
        _rp.setref_(ctypes.byref(_hrf),
                          ctypes.byref(_ixflag),
                          ctypes.byref(_x0),
                          ctypes.byref(_h0),
                          ctypes.byref(_s0),
                          ctypes.byref(_t0),
                          ctypes.byref(_p0),
                          ctypes.byref(_ierr),
                          ctypes.byref(_herr),
                          ctypes.c_long(3),
                          ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SETREFdll(ctypes.byref(_hrf),
                          ctypes.byref(_ixflag),
                          ctypes.byref(_x0),
                          ctypes.byref(_h0),
                          ctypes.byref(_s0),
                          ctypes.byref(_t0),
                          ctypes.byref(_p0),
                          ctypes.byref(_ierr),
                          ctypes.byref(_herr),
                          ctypes.c_long(3),
                          ctypes.c_long(255))
    if (hrf.upper() != u'DEF' and hrf.upper() != u'NBP' and hrf.upper() != u'ASH'
         and hrf.upper() != u'IIR'):
        href = {}
        if hrf == u'???':
            href[u'hrf'] = [_setupprop[u'setref'][u'hrf'][0], hrf]
            if u'ixflag' in _setupprop[u'setref']:
                href[u'ixflag'] = _setupprop[u'setref'][u'ixflag']
            if u'x' in _setupprop[u'setref']:
                href[u'x0'] = _setupprop[u'setref'][u'x0']
            if u'h0' in _setupprop[u'setref']:
                href[u'h0'] = _setupprop[u'setref'][u'h0']
            if u's0' in _setupprop[u'setref']:
                href[u's0'] = _setupprop[u'setref'][u's0']
            if u't0' in _setupprop[u'setref']:
                href[u't0'] = _setupprop[u'setref'][u't0']
            if u'p0' in _setupprop[u'setref']:
                href[u'p0'] = _setupprop[u'setref'][u'p0']
        else:
            href[u'hrf'] = [hrf.upper()]
            href[u'ixflag'] = ixflag
            if ixflag == 2: href[u'x0'] = x0
            if hrf.upper() == u'OTH':
                href[u'h0'] = h0
                href[u's0'] = s0
                href[u't0'] = t0
                href[u'p0'] = p0
        _setupprop[u'setref'] = href
    elif hrf.upper() != u'DEF':
        _setupprop[u'setref'] = {u'hrf':[hrf.upper()]}
    else:
        if u'setref' in _setupprop:
            _setupprop.__delitem__(u'setref')

    return _prop(ierr = _ierr.value, herr = _herr.value, defname = defname)


def _setmix(hmxnme, hrf, hfmix):
    u'''open a mixture file (e.g., R410A.MIX) and read constituents and mole
    fractions

    inputs:
        hmxnme--mixture file name to be read in [character*255]
        hrf--reference state for thermodynamic calculations [character*3]
            'def' : Default reference state as specified in fluid file is
                applied to each pure component.
            'nbs' : h,s = 0 at pure component normal boiling point(s).
            'ash' : h,s = 0 for sat liquid at -40 C (ASHRAE convention)
            'iir' : h = 200, s = 1.0 for sat liq at o C (IIR convention)
        hfmix--file name [character*255] containing parameters for the binary
            mixture model
    outputs:
        nc--number of fluids in mixture
        hfld--array of file names specifying mixture components that were
            used to call setup. [character*10000 variable]
        x--array of mole fractions for the specified mixture'''
    _inputerrorcheck(locals())
    global _nc_rec, _setupprop

    defname = sys._getframe(0).f_code.co_name, locals()

    _hmxnme.value = (hmxnme + u'.MIX').encode(u'ascii')
    _hfmix.value = hfmix.encode(u'ascii')
    _hrf.value = hrf.upper().encode(u'ascii')
    if platform.system() == u'Linux':
        _rp.setmix_(ctypes.byref(_hmxnme),
                         ctypes.byref(_hfmix),
                         ctypes.byref(_hrf),
                         ctypes.byref(_nc),
                         ctypes.byref(_hfld),
                         _x,
                         ctypes.byref(_ierr),
                         ctypes.byref(_herr),
                         ctypes.c_long(255),
                         ctypes.c_long(255),
                         ctypes.c_long(3),
                         ctypes.c_long(10000),
                         ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SETMIXdll(ctypes.byref(_hmxnme),
                         ctypes.byref(_hfmix),
                         ctypes.byref(_hrf),
                         ctypes.byref(_nc),
                         ctypes.byref(_hfld),
                         _x,
                         ctypes.byref(_ierr),
                         ctypes.byref(_herr),
                         ctypes.c_long(255),
                         ctypes.c_long(255),
                         ctypes.c_long(3),
                         ctypes.c_long(10000),
                         ctypes.c_long(255))
    hfld = []
    _nc_rec = _Setuprecord(_nc.value, u'_nc_rec')
    for each in xrange(_nc.value):
        hfld.append(_name(each + 1))
    x = normalize([_x[each] for each in xrange(_nc.value)])[u'x']
    _setupprop[u'hmxnme'], _setupprop[u'hrf'] = hmxnme, hrf.upper()
    _setupprop[u'nc'], _setupprop[u'hfld'] = _nc.value, hfld
    return _prop(x = x, ierr = _ierr.value, herr = _herr.value,
                        defname = defname)


def critp(x):
    u'''critical parameters as a function of composition

    input:
        x--composition [list of mol frac]
    outputs:
        tcrit--critical temperature [K]
        pcrit--critical pressure [kPa]
        Dcrit--critical density [mol/L]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.critp_(_x,
                   ctypes.byref(_tcrit),
                   ctypes.byref(_pcrit),
                   ctypes.byref(_Dcrit),
                   ctypes.byref(_ierr),
                   ctypes.byref(_herr),
                   ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.CRITPdll(_x,
                     ctypes.byref(_tcrit),
                     ctypes.byref(_pcrit),
                     ctypes.byref(_Dcrit),
                     ctypes.byref(_ierr),
                     ctypes.byref(_herr),
                     ctypes.c_long(255))
    return _prop(x = x, tcrit = _tcrit.value, pcrit = _pcrit.value,
                  Dcrit = _Dcrit.value, ierr = _ierr.value, herr = _herr.value,
                  defname = defname)


def therm(t, D, x):
    u'''Compute thermal quantities as a function of temperature, density and
    compositions using core functions (Helmholtz free energy, ideal gas heat
    capacity and various derivatives and integrals). Based on derivations in
    Younglove & McLinden, JPCRD 23 #5, 1994, Appendix A for
    pressure-explicit equations (e.g. MBWR) and c  Baehr & Tillner-Roth,
    Thermodynamic Properties of Environmentally Acceptable Refrigerants,
    Berlin:  Springer-Verlag (1995) for Helmholtz-explicit equations (e.g.
    FEQ).

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        p--pressure [kPa]
        e--internal energy [J/mol]
        h--enthalpy [J/mol]
        s--entropy [J/mol-K]
        cv--isochoric heat capacity [J/mol-K]
        cp--isobaric heat capacity [J/mol-K]
        w--speed of sound [m/s]
        hjt--isenthalpic Joule-Thompson coefficient [K/kPa]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.therm_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_hjt))
    elif platform.system() == u'Windows':
        _rp.THERMdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_hjt))
    return _prop(x = x, D = D, t = t, p = _p.value, e = _e.value, h = _h.value,
            s = _s.value, cv = _cv.value, cp = _cp.value, w = _w.value,
              hjt = _hjt.value)


def therm0(t, D, x):
    u'''Compute ideal gas thermal quantities as a function of temperature,
    density and compositions using core functions.

    This routine is the same as THERM, except it only calculates ideal gas
    properties (Z=1) at any temperature and density

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        p--pressure [kPa]
        e--internal energy [J/mol]
        h--enthalpy [J/mol]
        s--entropy [J/mol-K]
        cv--isochoric heat capacity [J/mol-K]
        cp--isobaric heat capacity [J/mol-K]
        w--speed of sound [m/s]
        A--Helmholtz energy [J/mol]
        G--Gibbs free energy [J/mol]'''
    _inputerrorcheck(locals())
    _t.value = t
    _D.value = D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.therm0_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_A),
                        ctypes.byref(_G))
    elif platform.system() == u'Windows':
        _rp.THERM0dll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_A),
                        ctypes.byref(_G))
    return _prop(x = x, D = D, t = t, p = _p.value, e = _e.value, h = _h.value,
            s = _s.value, cv = _cv.value, cp = _cp.value, w = _w.value,
            A = _A.value, G = _G.value)


def residual (t, D, x):
    u'''compute the residual quantities as a function of temperature, density,
    and compositions (where the residual is the property minus the ideal gas
    portion).

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        pr--residual pressure [kPa]  (p-rho*R*T)
        er--residual internal energy [J/mol]
        hr--residual enthalpy [J/mol]
        sr--residual entropy [J/mol-K]
        Cvr--residual isochoric heat capacity [J/mol-K]
        Cpr--residual isobaric heat capacity [J/mol-K]
        Ar--residual Helmholtz energy [J/mol]
        Gr--residual Gibbs free energy [J/mol]'''
    _inputerrorcheck(locals())
    _t.value = t
    _D.value = D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.residual_(ctypes.byref(_t),
                            ctypes.byref(_D),
                            _x,
                            ctypes.byref(_pr),
                            ctypes.byref(_er),
                            ctypes.byref(_hr),
                            ctypes.byref(_sr),
                            ctypes.byref(_cvr),
                            ctypes.byref(_cpr),
                            ctypes.byref(_Ar),
                            ctypes.byref(_Gr))
    elif platform.system() == u'Windows':
        _rp.RESIDUALdll(ctypes.byref(_t),
                                ctypes.byref(_D),
                                _x,
                                ctypes.byref(_pr),
                                ctypes.byref(_er),
                                ctypes.byref(_hr),
                                ctypes.byref(_sr),
                                ctypes.byref(_cvr),
                                ctypes.byref(_cpr),
                                ctypes.byref(_Ar),
                                ctypes.byref(_Gr))
    return _prop(x = x, D = D, t = t, pr = _pr.value, er = _er.value,
            hr = _hr.value, sr = _sr.value, cvr = _cvr.value, cpr = _cpr.value,
            Ar = _Ar.value, Gr = _Gr.value)

def therm2(t, D, x):
    u'''Compute thermal quantities as a function of temperature, density and
    compositions using core functions (Helmholtz free energy, ideal gas heat
    capacity and various derivatives and integrals).

    This routine is the same as THERM, except that additional properties are
    calculated

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        p--pressure [kPa]
        e--internal energy [J/mol]
        h--enthalpy [J/mol]
        s--entropy [J/mol-K]
        cv--isochoric heat capacity [J/mol-K]
        cp--isobaric heat capacity [J/mol-K]
        w--speed of sound [m/s]
        Z--compressibility factor (= PV/RT) [dimensionless]
        hjt--isenthalpic Joule-Thompson coefficient [K/kPa]
        A--Helmholtz energy [J/mol]
        G--Gibbs free energy [J/mol]
        xkappa--isothermal compressibility (= -1/V dV/dp = 1/D dD/dp) [1/kPa]
        beta--volume expansivity (= 1/V dV/dt = -1/D dD/dt) [1/K]
        dpdD--derivative dP/dD [kPa-L/mol]
        d2pdD2--derivative d^2p/dD^2 [kPa-L^2/mol^2]
        dpdt--derivative dp/dt [kPa/K]
        dDdt--derivative dD/dt [mol/(L-K)]
        dDdp--derivative dD/dp [mol/(L-kPa)]
        spare1 to 4--space holders for possible future properties'''
    _inputerrorcheck(locals())
    _t.value = t
    _D.value = D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.therm2_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_Z),
                        ctypes.byref(_hjt),
                        ctypes.byref(_A),
                        ctypes.byref(_G),
                        ctypes.byref(_xkappa),
                        ctypes.byref(_beta),
                        ctypes.byref(_dpdD),
                        ctypes.byref(_d2pdD2),
                        ctypes.byref(_dpdt),
                        ctypes.byref(_dDdt),
                        ctypes.byref(_dDdp),
                        ctypes.byref(_spare1),
                        ctypes.byref(_spare2),
                        ctypes.byref(_spare3),
                        ctypes.byref(_spare4))
    elif platform.system() == u'Windows':
        _rp.THERM2dll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_Z),
                        ctypes.byref(_hjt),
                        ctypes.byref(_A),
                        ctypes.byref(_G),
                        ctypes.byref(_xkappa),
                        ctypes.byref(_beta),
                        ctypes.byref(_dpdD),
                        ctypes.byref(_d2pdD2),
                        ctypes.byref(_dpdt),
                        ctypes.byref(_dDdt),
                        ctypes.byref(_dDdp),
                        ctypes.byref(_spare1),
                        ctypes.byref(_spare2),
                        ctypes.byref(_spare3),
                        ctypes.byref(_spare4))
    return _prop(x = x, D = D, t = t, p = _p.value, e = _e.value, h = _h.value,
            s = _s.value, cv = _cv.value, cp = _cp.value, w = _w.value,
            Z = _Z.value, hjt = _hjt.value, A = _A.value, G = _G.value,
            xkappa = _xkappa.value, beta = _beta.value, dpdD = _dpdD.value,
            d2pdD2 = _d2pdD2.value, dpdt = _dpdt.value, dDdt = _dDdt.value,
            dDdp = _dDdp.value)


def therm3(t, D, x):
    u'''Compute miscellaneous thermodynamic properties

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        xkappa--Isothermal compressibility
        beta--Volume expansivity
        xisenk--Isentropic expansion coefficient
        xkt--Isothermal expansion coefficient
        betas--Adiabatic compressibility
        bs--Adiabatic bulk modulus
        xkkt--Isothermal bulk modulus
        thrott--Isothermal throttling coefficient
        pint--Internal pressure
        spht--Specific heat input'''
    _inputerrorcheck(locals())
    _t.value = t
    _D.value = D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.therm3_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_xkappa),
                        ctypes.byref(_beta),
                        ctypes.byref(_xisenk),
                        ctypes.byref(_xkt),
                        ctypes.byref(_betas),
                        ctypes.byref(_bs),
                        ctypes.byref(_xkkt),
                        ctypes.byref(_thrott),
                        ctypes.byref(_pint),
                        ctypes.byref(_spht))
    elif platform.system() == u'Windows':
        _rp.THERM3dll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_xkappa),
                        ctypes.byref(_beta),
                        ctypes.byref(_xisenk),
                        ctypes.byref(_xkt),
                        ctypes.byref(_betas),
                        ctypes.byref(_bs),
                        ctypes.byref(_xkkt),
                        ctypes.byref(_thrott),
                        ctypes.byref(_pint),
                        ctypes.byref(_spht))
    return _prop(x = x, D = D, t = t, xkappa = _xkappa.value,
        beta = _beta.value, xisenk = _xisenk.value, xkt = _xkt.value,
        betas = _betas.value, bs = _bs.value, xkkt = _xkkt.value,
        thrott = _thrott.value, pint = _pint.value, spht = _spht.value)


def fpv(t, D, p, x):
    u'''Compute the supercompressibility factor, Fpv.

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        p--pressure [kPa]
        x--composition [array of mol frac]
    outputs:
        Fpv--sqrt[Z(60 F, 14.73 psia)/Z(T,P)].'''
    #odd either t, d or t, p should be sufficient?
    _inputerrorcheck(locals())
    _t.value = t
    _D.value = D
    _p.value = p
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.fpv_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    ctypes.byref(_p),
                    _x,
                    ctypes.byref(_Fpv))
    elif platform.system() == u'Windows':
        _rp.FPVdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_p),
                        _x,
                        ctypes.byref(_Fpv))
    return _prop(x = x, D = D, t = t, p = p, Fpv = _Fpv.value)


def chempot(t, D, x):
    u'''Compute the chemical potentials for each of the nc components of a
    mixture

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        u--array (1..nc) of the chemical potentials [J/mol].'''
    _inputerrorcheck(locals())
    defname = sys._getframe(0).f_code.co_name, locals()

    _t.value = t
    _D.value = D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.chempot_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        _u,
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.CHEMPOTdll(ctypes.byref(_t),
                            ctypes.byref(_D),
                            _x,
                            _u,
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    return _prop(x = x, D = D, t = t, ierr = _ierr.value, herr = _herr.value,
        u = [_u[each] for each in xrange(_nc_rec.record)], defname = defname)


def purefld(icomp=0):
    u'''Change the standard mixture setup so that the properties of one fluid
    can be calculated as if SETUP had been called for a pure fluid. Calling
    this routine will disable all mixture calculations. To reset the mixture
    setup, call this routine with icomp=0.

    inputs:
        icomp--fluid number in a mixture to use as a pure fluid'''
    global _purefld_rec, _nc_rec

    _inputerrorcheck(locals())

    #define setup record for FluidModel
    if icomp != 0:
        _purefld_rec = _Setuprecord(copy.copy(locals()), u'_purefld_rec')
    else:
        #del record
        if u'_purefld_rec' in _Setuprecord.object_list:
            _purefld_rec = None

    _icomp.value = icomp
    if platform.system() == u'Linux':
        _rp.purefld_(ctypes.byref(_icomp))
    elif platform.system() == u'Windows':
        _rp.PUREFLDdll(ctypes.byref(_icomp))

    return _prop(fixicomp = icomp)


def _name(icomp=1):
    _inputerrorcheck(locals())
    _icomp.value = icomp
    if platform.system() == u'Linux':
        _rp.name_(ctypes.byref(_icomp),
                    ctypes.byref(_hname),
                    ctypes.byref(_hn80),
                    ctypes.byref(_hcas),
                    ctypes.c_long(12),
                    ctypes.c_long(80),
                    ctypes.c_long(12))
    elif platform.system() == u'Windows':
        _rp.NAMEdll(ctypes.byref(_icomp),
                    ctypes.byref(_hname),
                    ctypes.byref(_hn80),
                    ctypes.byref(_hcas),
                    ctypes.c_long(12),
                    ctypes.c_long(80),
                    ctypes.c_long(12))
    return _hname.value.decode(u'utf-8').strip().upper()


def name(icomp=1):
    u'''Provides name information for specified component

    input:
        icomp--component number in mixture; 1 for pure fluid
    outputs:
        hname--component name [character*12]
        hn80--component name--long form [character*80]
        hcas--CAS (Chemical Abstracts Service) number [character*12]'''
    _inputerrorcheck(locals())
    _icomp.value = icomp
    if platform.system() == u'Linux':
        _rp.name_(ctypes.byref(_icomp),
                    ctypes.byref(_hname),
                    ctypes.byref(_hn80),
                    ctypes.byref(_hcas),
                    ctypes.c_long(12),
                    ctypes.c_long(80),
                    ctypes.c_long(12))
    elif platform.system() == u'Windows':
        _rp.NAMEdll(ctypes.byref(_icomp),
                    ctypes.byref(_hname),
                    ctypes.byref(_hn80),
                    ctypes.byref(_hcas),
                    ctypes.c_long(12),
                    ctypes.c_long(80),
                    ctypes.c_long(12))
    return _prop(icomp = icomp,
                        hname = _hname.value.decode(u'utf-8').strip().upper(),
                        hn80 = _hn80.value.decode(u'utf-8').strip().upper(),
                        hcas = _hcas.value.decode(u'utf-8').strip().upper())


def entro(t, D, x):
    u'''Compute entropy as a function of temperature, density and composition
    using core functions (temperature derivative of Helmholtz free energy
    and ideal gas integrals)

    based on derivations in Younglove & McLinden, JPCRD 23 #5, 1994,
    equations A5, A19 - A26

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        s--entropy [J/mol-K]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.entro_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_s))
    elif platform.system() == u'Windows':
        _rp.ENTROdll(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_s))
    return _prop(x = x, D = D, t = t, s = _s.value)


def enthal(t, D, x):
    u'''Compute enthalpy as a function of temperature, density, and
    composition using core functions (Helmholtz free energy and ideal gas
    integrals)

    based on derivations in Younglove & McLinden, JPCRD 23 #5, 1994,
    equations A7, A18, A19

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        h--enthalpy [J/mol]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.enthal_(ctypes.byref(_t),
                     ctypes.byref(_D),
                     _x,
                     ctypes.byref(_h))
    elif platform.system() == u'Windows':
        _rp.ENTHALdll(ctypes.byref(_t),
                     ctypes.byref(_D),
                     _x,
                     ctypes.byref(_h))
    return _prop(x = x, D = D, t = t, h = _h.value)


def cvcp(t, D, x):
    u'''Compute isochoric (constant volume) and isobaric (constant pressure)
    heat capacity as functions of temperature, density, and composition
    using core functions

    based on derivations in Younglove & McLinden, JPCRD 23 #5, 1994,
    equation A15, A16

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        cv--isochoric heat capacity [J/mol-K]
        cp--isobaric heat capacity [J/mol-K]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.cvcp_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_cv),
                    ctypes.byref(_cp))
    elif platform.system() == u'Windows':
        _rp.CVCPdll(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_cv),
                    ctypes.byref(_cp))
    return _prop(x = x, D = D, t = t, cv = _cv.value, cp = _cp.value)


def cvcpk(icomp, t, D):
    u'''Compute isochoric (constant volume) and isobaric (constant pressure)
    heat capacity as functions of temperature for a given component.

    analogous to CVCP, except for component icomp, this is used by transport
    routines to calculate Cv & Cp for the reference fluid (component zero)

    inputs:
        icomp--component number in mixture (1..nc); 1 for pure fluid
        t--temperature [K]
        D--molar density [mol/L]
    outputs:
        cv--isochoric heat capacity [J/mol-K]
        cp--isobaric heat capacity [J/mol-K]'''
    _inputerrorcheck(locals())
    _icomp.value, _t.value, _D.value = icomp, t, D
    if platform.system() == u'Linux':
        _rp.cvcpk_(ctypes.byref(_icomp),
                    ctypes.byref(_t),
                    ctypes.byref(_D),
                    ctypes.byref(_cv),
                    ctypes.byref(_cp))
    elif platform.system() == u'Windows':
        _rp.CVCPKdll(ctypes.byref(_icomp),
                    ctypes.byref(_t),
                    ctypes.byref(_D),
                    ctypes.byref(_cv),
                    ctypes.byref(_cp))
    return _prop(icomp = icomp, D = D, t = t, cv = _cv.value, cp = _cp.value)


def gibbs(t, D, x):
    u'''Compute residual Helmholtz and Gibbs free energy as a function of
    temperature, density, and composition using core functions

    N.B.  The quantity calculated is

    G(T, D) - G0(T, P*) = G(T, D) - G0(T, D) + RTln(RTD/P*)
        where G0 is the ideal gas state and P* is a reference pressure which
        is equal to the current pressure of interest. Since Gr is used only
        as a difference in phase equilibria calculations where the
        temperature and pressure of the phases are equal, the (RT/P*) part of
        the log term will cancel and is omitted.

    "normal" (not residual) A and G are computed by subroutine AG

    based on derivations in Younglove & McLinden, JPCRD 23 #5, 1994,
    equations A8 - A12

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        Ar--residual Helmholtz free energy [J/mol]
        Gr--residual Gibbs free energy [J/mol]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.gibbs_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_Ar),
                    ctypes.byref(_Gr))
    elif platform.system() == u'Windows':
        _rp.GIBBSdll(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_Ar),
                    ctypes.byref(_Gr))
    return _prop(x = x, D = D, t = t, Ar = _Ar.value, Gr = _Gr.value)


def ag(t, D, x):
    u'''Ccompute Helmholtz and Gibbs energies as a function of temperature,
    density, and composition.

    N.B.  These are not residual values (those are calculated by GIBBS).

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        A--Helmholtz energy [J/mol]
        G--Gibbs free energy [J/mol]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.ag_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_A),
                    ctypes.byref(_G))
    elif platform.system() == u'Windows':
        _rp.AGdll(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_A),
                    ctypes.byref(_G))
    return _prop(x = x, D = D, t = t, A = _A.value, G = _G.value)


def press(t, D, x):
    u'''Compute pressure as a function of temperature, density, and
    composition using core functions

    direct implementation of core function of corresponding model

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        p--pressure [kPa]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.press_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_p))
    elif platform.system() == u'Windows':
        _rp.PRESSdll(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_p))
    return _prop(x = x, D = D, t = t, p = _p.value)


def dpdd(t, D, x):
    u'''Compute partial derivative of pressure w.r.t. density at constant
    temperature as a function of temperature, density, and composition

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        dpdD--dP/dD [kPa-L/mol]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dpdd_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_dpdD))
    elif platform.system() == u'Windows':
        _rp.DPDDdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_dpdD))
    return _prop(x = x, D = D, t = t, dpdD = _dpdD.value)


def dpddk(icomp, t, D):
    u'''Compute partial derivative of pressure w.r.t. density at constant
    temperature as a function of temperature and density for a specified
    component

    analogous to dpdd, except for component icomp, this is used by transport
    routines to calculate dP/dD for the reference fluid (component zero)

    inputs:
        icomp--component number in mixture (1..nc); 1 for pure fluid
        t--temperature [K]
        D--molar density [mol/L]
    output:
        dpdD--dP/dD [kPa-L/mol]'''
    _inputerrorcheck(locals())
    _icomp.value, _t.value, _D.value = icomp, t, D
    if platform.system() == u'Linux':
        _rp.dpddk_(ctypes.byref(_icomp),
                    ctypes.byref(_t),
                    ctypes.byref(_D),
                    ctypes.byref(_dpdD))
    elif platform.system() == u'Windows':
        _rp.DPDDKdll(ctypes.byref(_icomp),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_dpdD))
    return _prop(icomp = icomp, D = D, t = t, cv = _dpdD.value)


def dpdd2(t, D, x):
    u'''Compute second partial derivative of pressure w.r.t. density at
    const. temperature as a function of temperature, density, and
    composition.

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        d2pdD2--d^2P/dD^2 [kPa-L^2/mol^2]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dpdd2_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_d2pdD2))
    elif platform.system() == u'Windows':
        _rp.DPDD2dll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_d2pdD2))
    return _prop(x = x, D = D, t = t, d2pdD2 = _d2pdD2.value)


def dpdt(t, D, x):
    u'''Compute partial derivative of pressure w.r.t. temperature at constant
    density as a function of temperature, density, and composition.

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        dpdt--dp/dt [kPa/K]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dpdt_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_dpdt))
    elif platform.system() == u'Windows':
        _rp.DPDTdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_dpdt))
    return _prop(x = x, D = D, t = t, dpt = _dpdt.value)


def dpdtk(icomp, t, D):
    u'''Compute partial derivative of pressure w.r.t. temperature at constant
    density as a function of temperature and density for a specified
    component

    analogous to dpdt, except for component icomp, this is used by transport
    routines to calculate dP/dT

    inputs:
        icomp--component number in mixture (1..nc); 1 for pure fluid
        t--temperature [K]
        D--molar density [mol/L]
    output:
        dpdt--dP/dT [kPa/K]'''
    _inputerrorcheck(locals())
    _icomp.value, _t.value, _D.value = icomp, t, D
    if platform.system() == u'Linux':
        _rp.dpdtk_(ctypes.byref(_icomp),
                    ctypes.byref(_t),
                    ctypes.byref(_D),
                    ctypes.byref(_dpdt))
    elif platform.system() == u'Windows':
        _rp.DPDTKdll(ctypes.byref(_icomp),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_dpdt))
    return _prop(icomp = icomp, D = D, t = t, dpdt = _dpdt.value)


def dddp(t, D, x):
    u'''ompute partial derivative of density w.r.t. pressure at constant
    temperature as a function of temperature, density, and composition.

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        dDdp--dD/dP [mol/(L-kPa)]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dddp_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_dDdp))
    elif platform.system() == u'Windows':
        _rp.DDDPdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_dDdp))
    return _prop(x = x, D = D, t = t, dDdp = _dDdp.value)


def dddt(t, D, x):
    u'''Compute partial derivative of density w.r.t. temperature at constant
    pressure as a function of temperature, density, and composition.

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        dDdt--dD/dT [mol/(L-K)]; (D)/d(t) = -d(D)/dp x dp/dt = -dp/dt /
        (dp/d(D))'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dddt_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_dDdt))
    elif platform.system() == u'Windows':
        _rp.DDDTdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_dDdt))
    return _prop(x = x, D = D, t = t, dDdt = _dDdt.value)


def dcdt(t, x):
    u'''Compute the 1st derivative of C (C is the third virial coefficient) with
    respect to T as a function of temperature and composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        dct--1st derivative of C with respect to T [(L/mol)^2-K]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dcdt_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_dct))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'routine "dcdt" unsupported in Windows')
        #~ _rp.DCDTdll(ctypes.byref(_t),
                        #~ _x,
                        #~ ctypes.byref(_dct))
    return _prop(x = x, t = t, dct = _dct.value)


def dcdt2(t, x):
    u'''Compute the 2nd derivative of C (C is the third virial coefficient) with
    respect to T as a function of temperature and composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        dct2--2nd derivative of C with respect to T [(L/mol-K)^2]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dcdt2_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_dct2))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'routine "dcdt2" unsupported in Windows')
        #~ _rp.DCDT2dll(ctypes.byref(_t),
                        #~ _x,
                        #~ ctypes.byref(_dct))
    return _prop(x = x, t = t, dct2 = _dct2.value)


def dhd1(t, D, x):
    u'''Compute partial derivatives of enthalpy w.r.t. t, p, or D at constant
    t, p, or D as a function of temperature, density, and composition

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        dhdt_D--dh/dt [J/mol-K]
        dhdt_p--dh/dt [J/mol-K]
        dhdD_t--dh/dD [J-L/mol^2]
        dhdD_p--dh/dD [J-L/mol^2]
        dhdp_t--dh/dt [J/mol-kPa]
        dhdp_D--dh/dt [J/mol-kPA]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dhd1_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    ctypes.byref(_dhdt_D),
                    ctypes.byref(_dhdt_p),
                    ctypes.byref(_dhdD_t),
                    ctypes.byref(_dhdD_p),
                    ctypes.byref(_dhdp_t),
                    ctypes.byref(_dhdp_D))
    elif platform.system() == u'Windows':
        _rp.DHD1dll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_dhdt_D),
                        ctypes.byref(_dhdt_p),
                        ctypes.byref(_dhdD_t),
                        ctypes.byref(_dhdD_p),
                        ctypes.byref(_dhdp_t),
                        ctypes.byref(_dhdp_D))
    return _prop(x = x, D = D, t = t, dhdt_D = _dhdt_D.value,
        dhdt_p = _dhdt_p.value, dhdD_t = _dhdD_t.value, dhdD_p = _dhdD_p.value,
        dhdp_t = _dhdp_t.value, dhdtp_D = _dhdp_D.value)


def fgcty(t, D, x):
    u'''Compute fugacity for each of the nc components of a mixture by
    numerical differentiation (using central differences) of the
    dimensionless residual Helmholtz energy

    based on derivations in E.W. Lemmon, MS Thesis, University of Idaho
    (1991); section 3.2

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        f--array (1..nc) of fugacities [kPa]'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.fgcty_(ctypes.byref(_t),
                    ctypes.byref(_D),
                    _x,
                    _f)
    elif platform.system() == u'Windows':
        _rp.FGCTYdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        _f)
    return _prop(x = x, D = D, t = t,
                        f = [_f[each] for each in xrange(_nc_rec.record)])


def fgcty2(t, D, x):
    u'''Compute fugacity for each of the nc components of a mixture by
    analytical differentiation of the dimensionless residual Helmholtz energy.

    based on derivations in the GERG-2004 document for natural gas

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        f--array (1..nc) of fugacities [kPa]

    fgcty2 does not work proper on either Linux and Windows operating platform'''
    raise RefproproutineError(u'function "fgcty2" unsupported in Linux & Windows')
    #fgcty2 returns value of fgcty and next refprop call is being
    #blocked by ctypes
    #~ _inputerrorcheck(locals())
    #~ _t.value, _D.value = t, D
    #~ for each in range(len(x)): _x[each] = x[each]
    #~ if platform.system() == 'Linux':
        #~ _rp.fgcty2_(ctypes.byref(_t),
                        #~ ctypes.byref(_D),
                        #~ _x,
                        #~ _f)
    #~ elif platform.system() == 'Windows':
        #~ _rp.FGCTY2dll(ctypes.byref(_t),
                        #~ ctypes.byref(_D),
                        #~ _x,
                        #~ _f)
    #~ return _prop(x = x, D = D, t = t, f = [_f[each] for each in range(_nc_rec.record)])


def fugcof(t, D, x):
    u'''Compute the fugacity coefficient for each of the nc components of a
    mixture.

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition [array of mol frac]
    outputs:
        f--array (1..nc) of the fugacity coefficients'''
    _inputerrorcheck(locals())
    defname = sys._getframe(0).f_code.co_name, locals()

    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.fugcof_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        _f,
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.FUGCOFdll(ctypes.byref(_t),
                            ctypes.byref(_D),
                            _x,
                            _f,
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    return _prop(x = x, D = D, t = t,
                    f = [_f[each] for each in xrange(_nc_rec.record)],
                    ierr = _ierr.value, herr = _herr.value, defname = defname)


def dbdt(t, x):
    u'''Compute the 2nd derivative of B (B is the second virial coefficient)
    with respect to T as a function of temperature and composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        dbt--2nd derivative of B with respect to T [L/mol-K]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dbdt_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_dbt))
    elif platform.system() == u'Windows':
        _rp.DBDTdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_dbt))
    return _prop(x = x, t = t, dbt = _dbt.value)


def virb(t, x):
    u'''Compute second virial coefficient as a function of temperature and
    composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        b--second virial coefficient [L/mol]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.virb_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_b))
    elif platform.system() == u'Windows':
        _rp.VIRBdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_b))
    return _prop(x = x, t = t, b = _b.value)


def virc(t, x):
    u'''Compute the third virial coefficient as a function of temperature and
    composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        c--third virial coefficient [(L/mol)^2]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.virc_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_c))
    elif platform.system() == u'Windows':
        _rp.VIRCdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_c))
    return _prop(x = x, t = t, c = _c.value)


def vird(t, x):
    u'''Compute the fourth virial coefficient as a function of temperature
    and composition.

    Routine not supported in Windows

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        c--third virial coefficient [(L/mol)^3]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.vird_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_d))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'routine "vird" unsupported in Windows')
        #_rp.VIRDdll(ctypes.byref(_t),
                        #_x,
                        #ctypes.byref(_d))
    return _prop(x = x, t = t, d = _d.value)


def virba (t, x):
    u'''Compute second acoustic virial coefficient as a function of temperature
    and composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        ba--second acoustic virial coefficient [L/mol]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.virba_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_ba))
    elif platform.system() == u'Windows':
        _rp.VIRBAdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_ba))
    return _prop(x = x, t = t, ba = _ba.value)


def virca(t, x):
    u'''Compute third acoustic virial coefficient as a function of temperature
    and composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        ca--third acoustic virial coefficient [(L/mol)^2]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.virca_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_ca))
    elif platform.system() == u'Windows':
        _rp.VIRCAdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_ca))
    return _prop(x = x, t = t, ca = _ca.value)


def satt(t, x, kph=2):
    u'''Iterate for saturated liquid and vapor states given temperature and
    the composition of one phase

    inputs:
        t--temperature [K]
        x--composition [array of mol frac] (phase specified by kph)
        kph--phase flag:
            1 = input x is liquid composition (bubble point)
            2 = input x is vapor composition (dew point)
            3 = input x is liquid composition (freezing point)
            4 = input x is vapor composition (sublimation point)
    outputs:
        p--pressure [kPa]
        Dliq--molar density [mol/L] of saturated liquid
        Dvap--molar density [mol/L] of saturated vapor
            For a pseudo pure fluid, the density of the equilibrium phase is
            not returned. Call SATT twice, once with kph=1 to get pliq and
            Dliq, and once with kph=2 to get pvap and Dvap.
        xliq--liquid phase composition [array of mol frac]
        xvap--vapor phase composition [array of mol frac]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _t.value, _kph.value = t, kph
    for each in xrange(len(x)): _x[each] = x[each]

    #_purefld_rec.record['icomp']
    if platform.system() == u'Linux':
        _rp.satt_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_kph),
                    ctypes.byref(_p),
                    ctypes.byref(_Dliq),
                    ctypes.byref(_Dvap),
                    _xliq,
                    _xvap,
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SATTdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_p),
                        ctypes.byref(_Dliq),
                        ctypes.byref(_Dvap),
                        _xliq,
                        _xvap,
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    xliq = normalize([_xliq[each] for each in xrange(_nc_rec.record)])[u'x']
    xvap = normalize([_xvap[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(t = t, x = x, kph = kph, p = _p.value, Dliq = _Dliq.value,
            Dvap = _Dvap.value, xliq = xliq, xvap = xvap, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def satp(p, x, kph=2):
    u'''Iterate for saturated liquid and vapor states given pressure and the
    composition of one phase.

    inputs:
        p--pressure [kPa]
        x--composition [array of mol frac] (phase specified by kph)
        kph--phase flag:
            1 = input x is liquid composition (bubble point)
            2 = input x is vapor composition (dew point)
            3 = input x is liquid composition (freezing point)
            4 = input x is vapor composition (sublimation point)
    outputs:
        t--temperature [K]
        Dliq--molar density [mol/L] of saturated liquid
        Dvap--molar density [mol/L] of saturated vapor
            For a pseudo pure fluid, the density of the equilibrium phase is
            not returned. Call SATP twice, once with kph=1 to get tliq and
            Dliq, and once with kph=2 to get tvap and Dvap.
        xliq--liquid phase composition [array of mol frac]
        xvap--vapor phase composition [array of mol frac]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _p.value, _kph.value = p, kph
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.satp_(ctypes.byref(_p),
                    _x,
                    ctypes.byref(_kph),
                    ctypes.byref(_t),
                    ctypes.byref(_Dliq),
                    ctypes.byref(_Dvap),
                    _xliq,
                    _xvap,
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SATPdll(ctypes.byref(_p),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_t),
                        ctypes.byref(_Dliq),
                        ctypes.byref(_Dvap),
                        _xliq,
                        _xvap,
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    xliq = normalize([_xliq[each] for each in xrange(_nc_rec.record)])[u'x']
    xvap = normalize([_xvap[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(p = p, x = x, kph = kph, t = _t.value, Dliq = _Dliq.value,
            Dvap = _Dvap.value, xliq = xliq, xvap = xvap, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def satd(D, x, kph=2):
    u'''Iterate for temperature and pressure given a density along the
    saturation boundary and the composition.

    inputs:
        D--molar density [mol/L]
        x--composition [array of mol frac]
        kph--flag specifying desired root for multi-valued inputs
            has meaning only for water at temperatures close to its triple
            point -1 = return middle root (between 0 and 4 C) 1 = return
            highest temperature root (above 4 C) 3 = return lowest temperature
            root (along freezing line)
    outputs:
        t--temperature [K]
        p--pressure [kPa]
        Dliq--molar density [mol/L] of saturated liquid
        Dvap--molar density [mol/L] of saturated vapor
        xliq--liquid phase composition [array of mol frac]
        xvap--vapor phase composition [array of mol frac]
        kr--phase flag:
            1 = input state is liquid
            2 = input state is vapor in equilibrium with liq
            3 = input state is liquid in equilibrium with solid
            4 = input state is vapor in equilibrium with solid
            N.B. kr = 3,4 presently working only for pure components

    either (Dliq, xliq) or (Dvap, xvap) will correspond to the input state
    with the other pair corresponding to the other phase in equilibrium with
    the input state'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _D.value, _kph.value = D, kph
    for each in xrange(len(x)):
        _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.satd_(ctypes.byref(_D),
                    _x,
                    ctypes.byref(_kph),
                    ctypes.byref(_kr),
                    ctypes.byref(_t),
                    ctypes.byref(_p),
                    ctypes.byref(_Dliq),
                    ctypes.byref(_Dvap),
                    _xliq,
                    _xvap,
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SATDdll(ctypes.byref(_D),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_kr),
                        ctypes.byref(_t),
                        ctypes.byref(_p),
                        ctypes.byref(_Dliq),
                        ctypes.byref(_Dvap),
                        _xliq,
                        _xvap,
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    xliq = normalize([_xliq[each] for each in xrange(_nc_rec.record)])[u'x']
    xvap = normalize([_xvap[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(D = D, x = x, kph = kph, kr = _kr.value, t = _t.value,
        p = _p.value, Dliq = _Dliq.value, Dvap = _Dvap.value, xliq = xliq,
        xvap = xvap, ierr = _ierr.value, herr = _herr.value, defname = defname)


def sath(h, x, kph=2):
    u'''Iterate for temperature, pressure, and density given enthalpy along
    the saturation boundary and the composition.

    inputs:
        h--molar enthalpy [J/mol]
        x--composition [array of mol frac]
        kph--flag specifying desired root:
            0 = return all roots along the liquid-vapor line
            1 = return only liquid VLE root
            2 = return only vapor VLE roots
            3 = return liquid SLE root (melting line)
            4 = return vapor SVE root (sublimation line)
    outputs:
        nroot--number of roots.  Set to one for kph=1,3,4 if ierr=0
        k1--phase of first root (1-liquid, 2-vapor, 3-melt, 4-subl)
        t1--temperature of first root [K]
        p1--pressure of first root [kPa]
        D1--molar density of first root [mol/L]
        k2--phase of second root (1-liquid, 2-vapor, 3-melt, 4-subl)
        t2--temperature of second root [K]
        p2--pressure of second root [kPa]
        D2--molar density of second root [mol/L]

    The second root is always set as the root in the vapor at temperatures
    below the maximum enthalpy on the vapor saturation line. If kph is set
    to 2, and only one root is found in the vapor (this occurs when h <
    hcrit) the state point will be placed in k2,t2,p2,d2. If kph=0 and this
    situation occurred, the first root (k1,t1,p1,d1) would be in the liquid
    (k1=1, k2=2).

    N.B. kph = 3,4 presently working only for pure components'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _h.value, _kph.value = h, kph
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.sath_(ctypes.byref(_h),
                    _x,
                    ctypes.byref(_kph),
                    ctypes.byref(_nroot),
                    ctypes.byref(_k1),
                    ctypes.byref(_t1),
                    ctypes.byref(_p1),
                    ctypes.byref(_D1),
                    ctypes.byref(_k2),
                    ctypes.byref(_t2),
                    ctypes.byref(_p2),
                    ctypes.byref(_D2),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SATHdll(ctypes.byref(_h),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_nroot),
                        ctypes.byref(_k1),
                        ctypes.byref(_t1),
                        ctypes.byref(_p1),
                        ctypes.byref(_D1),
                        ctypes.byref(_k2),
                        ctypes.byref(_t2),
                        ctypes.byref(_p2),
                        ctypes.byref(_D2),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(h = h, x = x, kph = kph, nroot = _nroot.value, k1 = _k1.value,
            t1 = _t1.value, p1 = _p1.value, D1 = _D1.value, k2 = _k2.value,
            t2 = _t2.value, p2 = _p2.value, D2 = _D2.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def sate(e, x, kph=2):
    u'''Iterate for temperature, pressure, and density given energy along the
    saturation boundary and the composition.

    inputs:
        e--molar energy [J/mol]
        x--composition [array of mol frac]
        kph--flag specifying desired root:
            0 = return all roots along the liquid-vapor line
            1 = return only liquid VLE root
            2 = return only vapor VLE roots
            3 = return liquid SLE root (melting line)
            4 = return vapor SVE root (sublimation line)
    outputs:
        nroot--number of roots.  Set to one for kph=1,3,4 if ierr=0
        k1--phase of first root (1-liquid, 2-vapor, 3-melt, 4-subl)
        t1--temperature of first root [K]
        p1--pressure of first root [kPa]
        D1--molar density of first root [mol/L]
        k2--phase of second root (1-liquid, 2-vapor, 3-melt, 4-subl)
        t2--temperature of second root [K]
        p2--pressure of second root [kPa]
        D2--molar density of second root [mol/L]

    The second root is always set as the root in the vapor at temperatures
    below the maximum energy on the vapor saturation line. If kph is set to
    2, and only one root is found in the vapor (this occurs when h < hcrit)
    the state point will be placed in k2,t2,p2,d2. If kph=0 and this
    situation occurred, the first root (k1,t1,p1,d1) would be in the liquid
    (k1=1, k2=2).

    N.B. kph = 3,4 presently working only for pure components'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _e.value, _kph.value = e, kph
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.sate_(ctypes.byref(_e),
                _x,
                ctypes.byref(_kph),
                ctypes.byref(_nroot),
                ctypes.byref(_k1),
                ctypes.byref(_t1),
                ctypes.byref(_p1),
                ctypes.byref(_D1),
                ctypes.byref(_k2),
                ctypes.byref(_t2),
                ctypes.byref(_p2),
                ctypes.byref(_D2),
                ctypes.byref(_ierr),
                ctypes.byref(_herr),
                ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SATEdll(ctypes.byref(_e),
                _x,
                ctypes.byref(_kph),
                ctypes.byref(_nroot),
                ctypes.byref(_k1),
                ctypes.byref(_t1),
                ctypes.byref(_p1),
                ctypes.byref(_D1),
                ctypes.byref(_k2),
                ctypes.byref(_t2),
                ctypes.byref(_p2),
                ctypes.byref(_D2),
                ctypes.byref(_ierr),
                ctypes.byref(_herr),
                ctypes.c_long(255))
    return _prop(e = e, x = x, kph = kph, nroot = _nroot.value, k1 = _k1.value,
            t1 = _t1.value, p1 = _p1.value, D1 = _D1.value, k2 = _k2.value,
            t2 = _t2.value, p2 = _p2.value, D2 = _D2.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def sats(s, x, kph=2):
    u'''Iterate for temperature, pressure, and density given entropy along
    the saturation boundary and the composition.

    inputs:
        s--entrophy [J/(mol K)]
        x--composition [array of mol frac]
        kph--flag specifying desired root:
            0 = return all roots along the liquid-vapor line
            1 = return only liquid VLE root
            2 = return only vapor VLE roots
            3 = return liquid SLE root (melting line)
            4 = return vapor SVE root (sublimation line)
    outputs:
        nroot--number of roots.  Set to one for kph=1,3,4 if ierr=0
        k1--phase of first root (1-liquid, 2-vapor, 3-melt, 4-subl)
        t1--temperature of first root [K]
        p1--pressure of first root [kPa]
        D1--molar density of first root [mol/L]
        k2--phase of second root (1-liquid, 2-vapor, 3-melt, 4-subl)
        t2--temperature of second root [K]
        p2--pressure of second root [kPa]
        D2--molar density of second root [mol/L]
        k3--phase of third root (1-liquid, 2-vapor, 3-melt, 4-subl)
        t3--temperature of third root [K]
        p3--pressure of third root [kPa]
        D3--molar density of third root [mol/L]

    The second root is always set as the root in the vapor at temperatures
    below the maximum energy on the vapor saturation line. If kph is set to
    2, and only one root is found in the vapor (this occurs when h < hcrit)
    the state point will be placed in k2,t2,p2,d2. If kph=0 and this
    situation occurred, the first root (k1,t1,p1,d1) would be in the liquid
    (k1=1, k2=2).

    The third root is the root with the lowest temperature. For fluids with
    multiple roots:  When only one root is found in the vapor phase (this
    happens only at very low temperatures past the region where three roots
    are located), the value of the root is still placed in k3,t3,p3,d3. For
    fluids that never have more than one root (when there is no maximum
    entropy along the saturated vapor line), the value of the root is always
    placed in k1,t1,p1,d1.

    N.B. kph = 3,4 presently working only for pure components'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _s.value, _kph.value = s, kph
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.sats_(ctypes.byref(_s),
                    _x,
                    ctypes.byref(_kph),
                    ctypes.byref(_nroot),
                    ctypes.byref(_k1),
                    ctypes.byref(_t1),
                    ctypes.byref(_p1),
                    ctypes.byref(_D1),
                    ctypes.byref(_k2),
                    ctypes.byref(_t2),
                    ctypes.byref(_p2),
                    ctypes.byref(_D2),
                    ctypes.byref(_k3),
                    ctypes.byref(_t3),
                    ctypes.byref(_p3),
                    ctypes.byref(_D3),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SATSdll(ctypes.byref(_s),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_nroot),
                        ctypes.byref(_k1),
                        ctypes.byref(_t1),
                        ctypes.byref(_p1),
                        ctypes.byref(_D1),
                        ctypes.byref(_k2),
                        ctypes.byref(_t2),
                        ctypes.byref(_p2),
                        ctypes.byref(_D2),
                        ctypes.byref(_k3),
                        ctypes.byref(_t3),
                        ctypes.byref(_p3),
                        ctypes.byref(_D3),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(s = s, x = x, kph = kph, nroot = _nroot.value, k1 = _k1.value,
            t1 = _t1.value, p1 = _p1.value, D1 = _D1.value, k2 = _k2.value,
            t2 = _t2.value, p2 = _p2.value, D2 = _D2.value, k3 = _k3.value,
            t3 = _t3.value, p3 = _p3.value, D3 = _D3.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def csatk(icomp, t, kph=2):
    u'''Compute the heat capacity along the saturation line as a function of
    temperature for a given component

    csat can be calculated two different ways:
        Csat = Cp - t(DvDt)(DpDtsat)
        Csat = Cp - beta/D*hvap/(vliq - vvap),
            where beta is the volume expansivity

    inputs:
        icomp--component number in mixture (1..nc); 1 for pure fluid
        t--temperature [K]
        kph--phase flag:
            1 = liquid calculation
            2 = vapor calculation
    outputs:
        p--saturation pressure [kPa]
        D--saturation molar density [mol/L]
        csat--saturation heat capacity [J/mol-K]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _icomp.value, _t.value, _kph.value = icomp, t, kph
    if platform.system() == u'Linux':
        _rp.csatk_(ctypes.byref(_icomp),
                    ctypes.byref(_t),
                    ctypes.byref(_kph),
                    ctypes.byref(_p),
                    ctypes.byref(_D),
                    ctypes.byref(_csat),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.CSATKdll(ctypes.byref(_icomp),
                        ctypes.byref(_t),
                        ctypes.byref(_kph),
                        ctypes.byref(_p),
                        ctypes.byref(_D),
                        ctypes.byref(_csat),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(icomp = icomp, t = t, kph = kph, p = _p.value, D = _D.value,
            csat = _csat.value, ierr = _ierr.value, herr = _herr.value,
            defname = defname)


def dptsatk(icomp, t, kph=2):
    u'''Compute the heat capacity and dP/dT along the saturation line as a
    function of temperature for a given component. See also subroutine
    CSATK.

    inputs:
        icomp--component number in mixture (1..nc); 1 for pure fluid
        t--temperature [K]
        kph--phase flag:
            1 = liquid calculation
            2 = vapor calculation
    outputs:
        p--saturation pressure [kPa]
        D--saturation molar density [mol/L]
        csat--saturation heat capacity [J/mol-K] (same as that called from
            CSATK)
        dpdt--dp/dT along the saturation line [kPa/K]
            (this is not dp/dt "at" the saturation line for the single phase
            state, but the change in saturated vapor pressure as the
            saturation temperature changes.)'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _icomp.value, _t.value, _kph.value = icomp, t, kph
    if platform.system() == u'Linux':
        _rp.dptsatk_(ctypes.byref(_icomp),
                        ctypes.byref(_t),
                        ctypes.byref(_kph),
                        ctypes.byref(_p),
                        ctypes.byref(_D),
                        ctypes.byref(_csat),
                        ctypes.byref(_dpdt),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.DPTSATKdll(ctypes.byref(_icomp),
                            ctypes.byref(_t),
                            ctypes.byref(_kph),
                            ctypes.byref(_p),
                            ctypes.byref(_D),
                            ctypes.byref(_csat),
                            ctypes.byref(_dpdt),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    return _prop(icomp = icomp, t = t, kph = kph, p = _p.value, D = _D.value,
            csat = _csat.value, dpdt = _dpdt.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def cv2pk(icomp, t, D=0):
    u'''Compute the isochoric heat capacity in the two phase (liquid+vapor)
    region.

    inputs:
        icomp--component number in mixture (1..nc); 1 for pure fluid
        t--temperature [K]
        D--density [mol/l] if known
            If D=0, then a saturated liquid state is assumed.
    outputs:
        cv2p--isochoric two-phase heat capacity [J/mol-K]
        csat--saturation heat capacity [J/mol-K]
            (Although there is already a csat routine in REFPROP, it is also
            returned here. However, the calculation speed is slower than
            csat.)'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _icomp.value, _t.value, _D.value = icomp, t, D
    if platform.system() == u'Linux':
        _rp.cv2pk_(ctypes.byref(_icomp),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_cv2p),
                        ctypes.byref(_csat),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.CV2PKdll(ctypes.byref(_icomp),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_cv2p),
                        ctypes.byref(_csat),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(icomp = icomp, t = t, D = D, cv2p = _cv2p.value,
                    csat = _csat.value, ierr = _ierr.value, herr = _herr.value,
                    defname = defname)


def tprho(t, p, x, kph=2, kguess=0, D=0):
    u'''Iterate for density as a function of temperature, pressure, and
    composition for a specified phase.

    The single-phase temperature-pressure flash is called many times by
    other routines, and has been optimized for speed; it requires a specific
    calling sequence.

    ***********************************************************************
    WARNING:
    Invalid densities will be returned for T & P outside range of validity,
    i.e., pressure > melting pressure, pressure less than saturation
    pressure for kph=1, etc.
    ***********************************************************************
    inputs:
        t--temperature [K]
        p--pressure [kPa]
        x--composition [array of mol frac]
        kph--phase flag:
            1 = liquid
            2 = vapor
            0 = stable phase--NOT ALLOWED (use TPFLSH)
                (unless an initial guess is supplied for rho)
            -1 = force the search in the liquid phase
            -2 = force the search in the vapor phase
        kguess--input flag:
            1 = first guess for D provided
            0 = no first guess provided
        D--first guess for molar density [mol/L], only if kguess = 1
    outputs:
        D--molar density [mol/L]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _t.value, _p.value, _kph.value = t, p, kph
    _kguess.value, _D.value = kguess, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.tprho_(ctypes.byref(_t),
                        ctypes.byref(_p),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_kguess),
                        ctypes.byref(_D),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.TPRHOdll(ctypes.byref(_t),
                        ctypes.byref(_p),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_kguess),
                        ctypes.byref(_D),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(t = t, p = p, x = x, kph = kph, kguess = kguess, D = _D.value,
            ierr = _ierr.value, herr = _herr.value, defname = defname)


def flsh(routine, var1, var2, x, kph=1):
    u'''Flash calculation given two independent variables and bulk
    composition

    These routines accept both single-phase and two-phase states as the
    input; if the phase is known, the specialized routines are faster

    inputs:
        routine--set input variables:
            'TP'--temperature; pressure
            'TD'--temperature; Molar Density
            'TH'--temperature; enthalpy
            'TS'--temperature; entropy
            'TE'--temperature; internal energy
            'PD'--pressure; molar density
            'PH'--pressure; enthalpy
            'PS'--pressure; entropy
            'PE'--pressure; internal energy
            'HS'--enthalpy; entropy
            'ES'--internal energy; entropy
            'DH'--molar density; enthalpy
            'DS'--molar density; entropy
            'DE'--molar density; internal energy
            'TQ'--temperature; vapour quality
            'PQ'--pressure; vapour qaulity
        var1, var2--two of the following as indicated by the routine input:
            t--temperature [K]
            p--pressure [kPa]
            e--internal energy [J/mol]
            h--enthalpy [J/mol]
            s--entropy [[J/mol-K]
            q--vapor quality on molar basis [moles vapor/total moles]
                q = 0 indicates saturated liquid
                0 < q < 1 indicates 2 phase state
                q = 1 indicates saturated vapor
                q < 0 or q > 1 are not allowed and will result in warning
        x--overall (bulk) composition [array of mol frac]
        kph--phase flag:
            N.B. only applicable for routine setting 'TE', 'TH' and 'TS'
            1=liquid,
            2=vapor in equilibrium with liq,
            3=liquid in equilibrium with solid,
            4=vapor in equilibrium with solid.
    outputs:
        t--temperature [K]
        p--pressure [kPa]
        D--overall (bulk) molar density [mol/L]
        Dliq--molar density [mol/L] of the liquid phase
        Dvap--molar density [mol/L] of the vapor phase
            if only one phase is present, Dl = Dv = D
        xliq--composition of liquid phase [array of mol frac]
        xvap--composition of vapor phase [array of mol frac]
            if only one phase is present, x = xliq = xvap
        q--vapor quality on a MOLAR basis [moles vapor/total moles]
            q < 0 indicates subcooled (compressed) liquid
            q = 0 indicates saturated liquid
            0 < q < 1 indicates 2 phase state
            q = 1 indicates saturated vapor
            q > 1 indicates superheated vapor
            q = 998 superheated vapor, but quality not defined (t > Tc)
            q = 999 indicates supercritical state (t > Tc) and (p > Pc)
        e--overall (bulk) internal energy [J/mol]
        h--overall (bulk) enthalpy [J/mol]
        s--overall (bulk) entropy [J/mol-K]
        cv--isochoric (constant V) heat capacity [J/mol-K]
        cp--isobaric (constant p) heat capacity [J/mol-K]
        w--speed of sound [m/s]
            cp, cv and w are not defined for 2-phase states in such cases,
            a flag = -9.99998d6 is returned'''##########################################then remove##################
            #same for kph flag which is only applicable for TH, TE and TS
            #Dvap Dliq to remove if single phase
            #xliq xvap to remove if single phase
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _kph.value = kph
    for each in xrange(len(x)): _x[each] = x[each]
    if routine.upper() == u'TP':
        _t.value, _p.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tpflsh_(ctypes.byref(_t),
                            ctypes.byref(_p),
                            _x,
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.TPFLSHdll(ctypes.byref(_t),
                                ctypes.byref(_p),
                                _x,
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_h),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'TD':
        _t.value, _D.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tdflsh_(ctypes.byref(_t),
                            ctypes.byref(_D),
                            _x,
                            ctypes.byref(_p),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.TDFLSHdll(ctypes.byref(_t),
                            ctypes.byref(_D),
                            _x,
                            ctypes.byref(_p),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    elif routine.upper() == u'TH':
        _t.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.thflsh_(ctypes.byref(_t),
                            ctypes.byref(_h),
                            _x,
                            ctypes.byref(_kph),
                            ctypes.byref(_p),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.THFLSHdll(ctypes.byref(_t),
                                ctypes.byref(_h),
                                _x,
                                ctypes.byref(_kph),
                                ctypes.byref(_p),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'TS':
        _t.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tsflsh_(ctypes.byref(_t),
                            ctypes.byref(_s),
                            _x,
                            ctypes.byref(_kph),
                            ctypes.byref(_p),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.TSFLSHdll(ctypes.byref(_t),
                                ctypes.byref(_s),
                                _x,
                                ctypes.byref(_kph),
                                ctypes.byref(_p),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_h),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'TE':
        _t.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.teflsh_(ctypes.byref(_t),
                            ctypes.byref(_e),
                            _x,
                            ctypes.byref(_kph),
                            ctypes.byref(_p),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.TEFLSHdll(ctypes.byref(_t),
                                ctypes.byref(_e),
                                _x,
                                ctypes.byref(_kph),
                                ctypes.byref(_p),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_h),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'PD':
        _p.value, _D.value = var1, var2
        if platform.system() == u'Linux':
            _rp.pdflsh_(ctypes.byref(_p),
                            ctypes.byref(_D),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PDFLSHdll(ctypes.byref(_p),
                                ctypes.byref(_D),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_h),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'PH':
        _p.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.phflsh_(ctypes.byref(_p),
                            ctypes.byref(_h),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PHFLSHdll(ctypes.byref(_p),
                                ctypes.byref(_h),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'PS':
        _p.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.psflsh_(ctypes.byref(_p),
                            ctypes.byref(_s),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PSFLSHdll(ctypes.byref(_p),
                                ctypes.byref(_s),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_h),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'PE':
        _p.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.peflsh_(ctypes.byref(_p),
                            ctypes.byref(_e),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PEFLSHdll(ctypes.byref(_p),
                                ctypes.byref(_e),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_h),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'HS':
        _h.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.hsflsh_(ctypes.byref(_h),
                            ctypes.byref(_s),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_p),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.HSFLSHdll(ctypes.byref(_h),
                                ctypes.byref(_s),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_p),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'ES':
        _e.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.esflsh_(ctypes.byref(_e),
                            ctypes.byref(_s),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_p),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_h),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.ESFLSHdll(ctypes.byref(_e),
                                ctypes.byref(_s),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_p),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_h),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'DH':
        _D.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.dhflsh_(ctypes.byref(_D),
                            ctypes.byref(_h),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_p),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.DHFLSHdll(ctypes.byref(_D),
                                ctypes.byref(_h),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_p),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'DS':
        _D.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.dsflsh_(ctypes.byref(_D),
                            ctypes.byref(_s),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_p),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.DSFLSHdll(ctypes.byref(_D),
                                ctypes.byref(_s),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_p),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_e),
                                ctypes.byref(_h),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'DE':
        _D.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.deflsh_(ctypes.byref(_D),
                            ctypes.byref(_e),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_p),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_q),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.DEFLSHdll(ctypes.byref(_D),
                                ctypes.byref(_e),
                                _x,
                                ctypes.byref(_t),
                                ctypes.byref(_p),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_q),
                                ctypes.byref(_h),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'TQ':
        _t.value, _q.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tqflsh_(ctypes.byref(_t),
                            ctypes.byref(_q),
                            _x,
                            ctypes.byref(ctypes.c_long(1)),
                            ctypes.byref(_p),
                            ctypes.byref(_D),
                            ctypes.byref(_Dliq),
                            ctypes.byref(_Dvap),
                            _xliq,
                            _xvap,
                            ctypes.byref(_e),
                            ctypes.byref(_h),
                            ctypes.byref(_s),
                            ctypes.byref(_cv),
                            ctypes.byref(_cp),
                            ctypes.byref(_w),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.TQFLSHdll(ctypes.byref(_t),
                                ctypes.byref(_q),
                                _x,
                                ctypes.byref(ctypes.c_long(1)),
                                ctypes.byref(_p),
                                ctypes.byref(_D),
                                ctypes.byref(_Dliq),
                                ctypes.byref(_Dvap),
                                _xliq,
                                _xvap,
                                ctypes.byref(_e),
                                ctypes.byref(_h),
                                ctypes.byref(_s),
                                ctypes.byref(_cv),
                                ctypes.byref(_cp),
                                ctypes.byref(_w),
                                ctypes.byref(_ierr),
                                ctypes.byref(_herr),
                                ctypes.c_long(255))
    elif routine.upper() == u'PQ':
        _p.value, _q.value = var1, var2
        if platform.system() == u'Linux':
            _rp.pqflsh_(ctypes.byref(_p),
                        ctypes.byref(_q),
                        _x,
                        ctypes.byref(ctypes.c_long(1)),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_Dliq),
                        ctypes.byref(_Dvap),
                        _xliq,
                        _xvap,
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PQFLSHdll(ctypes.byref(_p),
                        ctypes.byref(_q),
                        _x,
                        ctypes.byref(ctypes.c_long(1)),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_Dliq),
                        ctypes.byref(_Dvap),
                        _xliq,
                        _xvap,
                        ctypes.byref(_e),
                        ctypes.byref(_h),
                        ctypes.byref(_s),
                        ctypes.byref(_cv),
                        ctypes.byref(_cp),
                        ctypes.byref(_w),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    else: raise RefpropinputError(u'Incorrect "routine" input, ' + unicode(routine) +
                                            u' is an invalid input')

    xliq = normalize([_xliq[each] for each in xrange(_nc_rec.record)])[u'x']
    xvap = normalize([_xvap[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(x = x, p = _p.value, q = _q.value, kph = kph, t = _t.value,
            D = _D.value, Dliq = _Dliq.value, Dvap = _Dvap.value, xliq = xliq,
            xvap = xvap, e = _e.value, h = _h.value, s = _s.value, cv = _cv.value,
            cp = _cp.value, w = _w.value, ierr = _ierr.value, herr = _herr.value,
            defname = defname)


def flsh1(routine, var1, var2, x, kph=1, Dmin=0, Dmax=0):
    u'''Flash calculation given two independent variables and bulk
    composition

    These routines accept only single-phase states and outside critical
    region as inputs. They will be faster than the corresponding general
    routines, but will fail if called with an incorrect phase specification.
    The phase-specific subroutines also do not check limits, so may fail if
    called outside the range of the equation of state.

    inputs:
        routine--set input variables:
            'TH'--temperature; enthalpy*
            'TS'--temperature; entropy*
            'TE'--temperature; energy*
            'PD'--pressure; molar density
            'PH'--pressure; entalphy
            'PS'--pressure; entropy
            'PE'--pressure; internal energy*
            'HS'--enthalpy; entropy*
            'DH'--molar density; enthalpy*
            'DS'--molar density; entropy*
            'DE'--molar density; internal energy*
            * routine not supported in Windows
        var1, var2--two of the following as indicated by the routine input:
            t--temperature [K]
            p--pressure [kPa]
            e--internal energy [J/mol]
            h--enthalpy [J/mol]
            s--entropy [[J/mol-K]
        x--overall (bulk) composition [array of mol frac]
        kph--phase flag:
            N.B. only applicable for routine setting 'TE', 'TH' and 'TS'
            1 = liquid,
            2 = vapor
        Dmin--lower bound on density [mol/L]
        Dmax--upper bound on density [mol/L]
    outputs:
        t--temperature [K]
        D--overall (bulk) molar density [mol/L]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _kph.value, _Dmin.value, _Dmax.value = kph, Dmin, Dmax
    for each in xrange(len(x)): _x[each] = x[each]
    if routine.upper() == u'TH':
        _t.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.thfl1_(ctypes.byref(_t),
                            ctypes.byref(_h),
                            _x,
                            ## should add kph
                            ctypes.byref(_Dmin),
                            ctypes.byref(_Dmax),
                            ctypes.byref(_D),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "THFL1" unsupported in Windows')
                #~ _rp.THFL1dll(ctypes.byref(_t),
                            #~ ctypes.byref(_h),
                            #~ _x,
                            #~ ## should add kph
                            #~ ctypes.byref(_Dmin),
                            #~ ctypes.byref(_Dmax),
                            #~ ctypes.byref(_D),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'TS':
        _t.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tsfl1_(ctypes.byref(_t),
                        ctypes.byref(_s),
                        _x,
                        ## should add kph
                        ctypes.byref(_Dmin),
                        ctypes.byref(_Dmax),
                        ctypes.byref(_D),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "TSFL1" unsupported in Windows')
            #~ _rp.TSFL1dll(ctypes.byref(_t),
                        #~ ctypes.byref(_s),
                        #~ _x,
                        #~ ## should add kph
                        #~ ctypes.byref(_Dmin),
                        #~ ctypes.byref(_Dmax),
                        #~ ctypes.byref(_D),
                        #~ ctypes.byref(_ierr),
                        #~ ctypes.byref(_herr),
                        #~ ctypes.c_long(255))
    elif routine.upper() == u'TE':
        _t.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tefl1_(ctypes.byref(_t),
                        ctypes.byref(_e),
                        _x,
                        ##should add kph
                        ctypes.byref(_Dmin),
                        ctypes.byref(_Dmax),
                        ctypes.byref(_D),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "TEFL1" unsupported in Windows')
            #~ #_rp.TEFL1dll(ctypes.byref(_t),
                        #~ #ctypes.byref(_e),
                        #~ #_x,
                        #~ ###should add kph
                        #~ #ctypes.byref(_Dmin),
                        #~ #ctypes.byref(_Dmax),
                        #~ #ctypes.byref(_D),
                        #~ #ctypes.byref(_ierr),
                        #~ #ctypes.byref(_herr),
                        #~ #ctypes.c_long(255))
    elif routine.upper() == u'PD':
        _p.value, _D.value = var1, var2
        if platform.system() == u'Linux':
            _rp.pdfl1_(ctypes.byref(_p),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_t),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PDFL1dll(ctypes.byref(_p),
                            ctypes.byref(_D),
                            _x,
                            ctypes.byref(_t),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    elif routine.upper() == u'PH':
        _p.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.phfl1_(ctypes.byref(_p),
                        ctypes.byref(_h),
                        _x,
                        ctypes.byref(_kph), #why kph
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PHFL1dll(ctypes.byref(_p),
                            ctypes.byref(_h),
                            _x,
                            ctypes.byref(_kph), #why kph
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    elif routine.upper() == u'PS':
        _p.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.psfl1_(ctypes.byref(_p),
                        ctypes.byref(_s),
                        _x,
                        ctypes.byref(_kph), #why kph
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            _rp.PSFL1dll(ctypes.byref(_p),
                            ctypes.byref(_s),
                            _x,
                            ctypes.byref(_kph), #why kph
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    elif routine.upper() == u'PE': #wrong value return
        _p.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.pefl1_(ctypes.byref(_p),
                        ctypes.byref(_e),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "PEFL1" unsupported in Windows')
            _rp.PEFL1dll(ctypes.byref(_p),
                            ctypes.byref(_e),
                            _x,
                            ctypes.byref(_kph),
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
    elif routine.upper() == u'HS':
        _h.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.hsfl1_(ctypes.byref(_h),
                            ctypes.byref(_s),
                            _x,
                            ctypes.byref(_Dmin),
                            ctypes.byref(_Dmax),
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "HSFL1" unsupported in Windows')
            #~ _rp.HSFL1dll(ctypes.byref(_h),
                            #~ ctypes.byref(_s),
                            #~ _x,
                            #~ ctypes.byref(_Dmin),
                            #~ ctypes.byref(_Dmax),
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_D),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'DH':
        _D.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.dhfl1_(ctypes.byref(_D),
                        ctypes.byref(_h),
                        _x,
                        ctypes.byref(_t),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "DHFL1" unsupported in Windows')
            #~ _rp.DHFL1dll(ctypes.byref(_D),
                            #~ ctypes.byref(_h),
                            #~ _x,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'DS':
        _D.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.dsfl1_(ctypes.byref(_D),
                        ctypes.byref(_s),
                        _x,
                        ctypes.byref(_t),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "DSFL1" unsupported in Windows')
            #~ _rp.DSFL1dll(ctypes.byref(_D),
                            #~ ctypes.byref(_s),
                            #~ _x,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'DE':
        _D.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.defl1_(ctypes.byref(_D),
                        ctypes.byref(_e),
                        _x,
                        ctypes.byref(_t),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'routine "DEFL1" unsupported in Windows')
            #~ _rp.DEFL1dll(ctypes.byref(_D),
                        #~ ctypes.byref(_e),
                        #~ _x,
                        #~ ctypes.byref(_t),
                        #~ ctypes.byref(_ierr),
                        #~ ctypes.byref(_herr),
                        #~ ctypes.c_long(255))
    else: raise RefpropinputError(u'Incorrect "routine" input, ' + unicode(routine) +
                                            u' is an invalid input')
    if routine.upper() == u'TH':
        return _prop(x = x, t = var1, Dmin = _Dmin.value, Dmax = _Dmax.value,
                D = _D.value, h = var2, ierr = _ierr.value, herr = _herr.value,
                defname = defname)
    elif routine.upper() == u'TS':
        return _prop(x = x, t = var1, D = _D.value, s = var2, Dmin = _Dmin.value,
                Dmax = _Dmax.value, ierr = _ierr.value, herr = _herr.value,
                defname = defname)
    elif routine.upper() == u'TE':
        return _prop(x = x, t = var1, D = _D.value, e = var2, Dmin = _Dmin.value,
                Dmax = _Dmax.value, ierr = _ierr.value, herr = _herr.value,
                defname = defname)
    elif routine.upper() == u'PD':
        return _prop(x = x, t = _t.value, D = var2, kph = kph, p = var1,
                ierr = _ierr.value, herr = _herr.value, defname = defname)
    elif routine.upper() == u'PH':
        return _prop(x = x, t = _t.value, D = _D.value, kph = kph, p = var1,
                            h = var2, ierr = _ierr.value, herr = _herr.value,
                            defname = defname)
    elif routine.upper() == u'PS':
        return _prop(x = x, t = _t.value, D = _D.value, kph = kph, p = var1,
                        s = var2, ierr = _ierr.value, herr = _herr.value,
                        defname = defname)
    elif routine.upper() == u'PE':
        return _prop(x = x, t = _t.value, D = _D.value, kph = kph, p = var1,
                        e = var2, ierr = _ierr.value, herr = _herr.value,
                        defname = defname)
    elif routine.upper() == u'HS':
        return _prop(x = x, t = _t.value, D = _D.value, h = var1, s = var2,
                ierr = _ierr.value, herr = _herr.value, Dmin = _Dmin.value,
                Dmax = _Dmax.value, defname = defname)
    elif routine.upper() == u'DH':
        return _prop(x = x, t = _t.value, D = var1, h = var2, ierr = _ierr.value,
                herr = _herr.value, defname = defname)
    elif routine.upper() == u'DS':
        return _prop(x = x, t = _t.value, D = var1, s = var2, ierr = _ierr.value,
                herr = _herr.value, defname = defname)
    elif routine.upper() == u'DE':
        return _prop(x = x, t = _t.value, D = var1, e = var2, ierr = _ierr.value,
                herr = _herr.value, defname = defname)


def flsh2(routine, var1, var2, x, kq=1, ksat=0, tbub=0, tdew=0, pbub=0, pdew=0,
            Dlbub=0, Dvdew=0, xbub=None, xdew=None):
    u'''Flash calculation given two independent variables and bulk composition

    These routines accept only two-phase (liquid + vapor) states as inputs.
    They will be faster than the corresponding general routines, but will fail if
    called with an incorrect phase specification.
    The phase-specific subroutines also do not check limits, so may fail if
    called outside the range of the equation of state.

    Some two-phase flash routines have the option to pass the dew and bubble
    point conditions as inputs if these values are known
    (from a previous call to SATT or SATP, for example), these two-phase routines
    will be significantly faster than the corresponding
    general FLSH routines described above. Otherwise, the general routines will
    be more reliable.

    inputs:
        routine--set input variables:
            'TP'--temperature; pressure*
            'DH'--molar density; enthalpy*
            'DS'--molar density; entropy*
            'DE'--molar density; internal energy*
            'TH'--temperature; enthalpy*
            'TS'--temperature; entropy*
            'TE'--temperature; internal energy*
            'TD'--temperature; Molar Density*
            'PD'--pressure; molar density*
            'PH'--pressure; entalphy*
            'PS'--pressure; entropy*
            'PE'--pressure; internal energy*
            'TQ'--temperature; vapour quality*
            'PQ'--pressure; vapour qaulity*
            'DQ'--molar density; vapour quality*/**
            * NOT supported with Windows
            ** return value is incorrect
        var1, var2--two of the following as indicated by the routine input:
            t--temperature [K]
            p--pressure [kPa]
            D--molar density [mol/L]
            e--internal energy [J/mol]
            h--enthalpy [J/mol]
            s--entropy [[J/mol-K]
            q--vapor quality on molar basis [moles vapor/total moles]
        x--overall (bulk) composition [array of mol frac]
        kq--flag specifying units for input quality
            NB only for routine (TQ and PQ)
            kq = 1 quality on MOLAR basis [moles vapor/total moles]
            kq = 2 quality on MASS basis [mass vapor/total mass]
        ksat--flag for bubble and dew point limits
            NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
            0 = dew and bubble point limits computed within routine
            1 = must provide values for following:
                tbub--bubble point temperature [K] at (p,x=z)
                    NB only for routine (PD, PH, PS, PE and PQ)
                tdew--dew point temperature [K] at (p,y=z)
                    NB only for routine (PD, PH, PS, PE and PQ)
                pbub--bubble point pressure [kPa] at (t,x=z)
                    NB only for routine (TH, TS, TE, TD and TQ)
                pdew--dew point pressure [kPa] at (t,y=z)
                    NB only for routine (TH, TS, TE, TD and TQ)
                Dlbub--liquid density [mol/L] at bubble point
                    NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
                Dvdew--vapor density [mol/L] at dew point
                    NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
                xbub--vapor composition [array of mol frac] at bubble point
                    NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
                xdew--liquid composition [array of mol frac] at dew point
                    NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
    outputs:
        t--temperature [K]
        p--pressure [kPa]
        Dliq--molar density [mol/L] of the liquid phase
        Dvap--molar density [mol/L] of the vapor phase
            if only one phase is present, Dl = Dv = D
        xliq--composition of liquid phase [array of mol frac]
        xvap--composition of vapor phase [array of mol frac]
            if only one phase is present, x = xliq = xvap
        q--vapor quality on a MOLAR basis [moles vapor/total moles]
        tbub--bubble point temperature [K] at (p,x=z)
            NB only for routine (PD, PH, PS, PE and PQ)
        tdew--dew point temperature [K] at (p,y=z)
            NB only for routine (PD, PH, PS, PE and PQ)
        pbub--bubble point pressure [kPa] at (t,x=z)
            NB only for routine (TH, TS, TE, TD and TQ)
        pdew--dew point pressure [kPa] at (t,y=z)
            NB only for routine (TH, TS, TE, TD and TQ)
        Dlbub--liquid density [mol/L] at bubble point
            NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
        Dvdew--vapor density [mol/L] at dew point
            NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
        xbub--vapor composition [array of mol frac] at bubble point
            NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)
        xdew--liquid composition [array of mol frac] at dew point
            NB only for routine (TH, TS, TE, TD, PD, PH, PS, PE, TQ and PQ)'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    for each in xrange(len(x)):
        _x[each] = x[each]
        if xdew: _xdew[each] = xdew[each]
        if xbub: _xbub[each] = xbub[each]
    _ksat.value, _tbub.value, _kq.value = ksat, tbub, kq
    _tdew.value, _pbub.value, _pdew.value = tdew, pbub, pdew
    _Dlbub.value, _Dvdew.value = Dlbub, Dvdew
    if routine.upper() == u'TP':
        _t.value, _p.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tpfl2_(ctypes.byref(_t),
                       ctypes.byref(_p),
                       _x,
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "TPFL2" unsupported in Windows')
            #~ _rp.TPFL2dll(ctypes.byref(_t),
                            #~ ctypes.byref(_p),
                            #~ _x,
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'DH':
        _D.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.dhfl2_(ctypes.byref(_D),
                       ctypes.byref(_h),
                       _x,
                       ctypes.byref(_t),
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "DHFL2" unsupported in Windows')
            #~ _rp.DHFL2dll(ctypes.byref(_D),
                            #~ ctypes.byref(_h),
                            #~ _x,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'DS':
        _D.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.dsfl2_(ctypes.byref(_D),
                       ctypes.byref(_s),
                       _x,
                       ctypes.byref(_t),
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "DSFL2" unsupported in Windows')
            #~ _rp.DSFL2dll(ctypes.byref(_D),
                            #~ ctypes.byref(_s),
                            #~ _x,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'DE':
        _D.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.defl2_(ctypes.byref(_D),
                       ctypes.byref(_e),
                       _x,
                       ctypes.byref(_t),
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "DEFL2" unsupported in Windows')
            #~ _rp.DEFL2dll(ctypes.byref(_D),
                            #~ ctypes.byref(_e),
                            #~ _x,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'TH':
        _t.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.thfl2_(ctypes.byref(_t),
                       ctypes.byref(_h),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_pbub),
                       ctypes.byref(_pdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "THFL2" unsupported in Windows')
            #~ _rp.THFL2dll(ctypes.byref(_t),
                            #~ ctypes.byref(_h),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_pbub),
                            #~ ctypes.byref(_pdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'TS':
        _t.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tsfl2_(ctypes.byref(_t),
                       ctypes.byref(_s),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_pbub),
                       ctypes.byref(_pdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "TSFL2" unsupported in Windows')
            #~ _rp.TSFL2dll(ctypes.byref(_t),
                            #~ ctypes.byref(_s),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_pbub),
                            #~ ctypes.byref(_pdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'TE':
        _t.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tefl2_(ctypes.byref(_t),
                       ctypes.byref(_e),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_pbub),
                       ctypes.byref(_pdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "TEFL2" unsupported in Windows')
            #~ _rp.TEFL2dll(ctypes.byref(_t),
                            #~ ctypes.byref(_e),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_pbub),
                            #~ ctypes.byref(_pdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'TD':
        _t.value, _D.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tdfl2_(ctypes.byref(_t),
                       ctypes.byref(_D),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_pbub),
                       ctypes.byref(_pdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "TDFL2" unsupported in Windows')
            #~ _rp.TDFL2dll(ctypes.byref(_t),
                            #~ ctypes.byref(_D),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_pbub),
                            #~ ctypes.byref(_pdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'PD':
        _p.value, _D.value = var1, var2
        if platform.system() == u'Linux':
            _rp.pdfl2_(ctypes.byref(_p),
                       ctypes.byref(_D),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_tbub),
                       ctypes.byref(_tdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_t),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "PDFL2" unsupported in Windows')
            #~ _rp.PDFL2dll(ctypes.byref(_p),
                            #~ ctypes.byref(_D),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_tbub),
                            #~ ctypes.byref(_tdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'PH':
        _p.value, _h.value = var1, var2
        if platform.system() == u'Linux':
            _rp.phfl2_(ctypes.byref(_p),
                       ctypes.byref(_h),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_tbub),
                       ctypes.byref(_tdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_t),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "PHFL2" unsupported in Windows')
            #~ _rp.PHFL2dll(ctypes.byref(_p),
                            #~ ctypes.byref(_h),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_tbub),
                            #~ ctypes.byref(_tdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'PS':
        _p.value, _s.value = var1, var2
        if platform.system() == u'Linux':
            _rp.psfl2_(ctypes.byref(_p),
                       ctypes.byref(_s),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_tbub),
                       ctypes.byref(_tdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_t),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "PSFL2" unsupported in Windows')
            #~ _rp.PSFL2dll(ctypes.byref(_p),
                            #~ ctypes.byref(_s),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_tbub),
                            #~ ctypes.byref(_tdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'PE':
        _p.value, _e.value = var1, var2
        if platform.system() == u'Linux':
            _rp.pefl2_(ctypes.byref(_p),
                       ctypes.byref(_e),
                       _x,
                       ctypes.byref(_ksat),
                       ctypes.byref(_tbub),
                       ctypes.byref(_tdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_t),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_q),
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "PEFL2" unsupported in Windows')
            #~ _rp.PEFL2dll(ctypes.byref(_p),
                            #~ ctypes.byref(_e),
                            #~ _x,
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_tbub),
                            #~ ctypes.byref(_tdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_q),
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'TQ':
        _t.value, _q.value = var1, var2
        if platform.system() == u'Linux':
            _rp.tqfl2_(ctypes.byref(_t),
                       ctypes.byref(_q),
                       _x,
                       ctypes.byref(_kq),
                       ctypes.byref(_ksat),
                       ctypes.byref(_pbub),
                       ctypes.byref(_pdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_p),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "TQLF2" unsupported in Windows')
            #~ _rp.TQFL2dll(ctypes.byref(_t),
                            #~ ctypes.byref(_q),
                            #~ _x,
                            #~ ctypes.byref(ctypes.c_long(1)),
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_pbub),
                            #~ ctypes.byref(_pdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'PQ':
        _p.value, _q.value = var1, var2
        if platform.system() == u'Linux':
            _rp.pqfl2_(ctypes.byref(_p),
                       ctypes.byref(_q),
                       _x,
                       ctypes.byref(_kq),
                       ctypes.byref(_ksat),
                       ctypes.byref(_tbub),
                       ctypes.byref(_tdew),
                       ctypes.byref(_Dlbub),
                       ctypes.byref(_Dvdew),
                       _xbub,
                       _xdew,
                       ctypes.byref(_t),
                       ctypes.byref(_Dliq),
                       ctypes.byref(_Dvap),
                       _xliq,
                       _xvap,
                       ctypes.byref(_ierr),
                       ctypes.byref(_herr),
                       ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "PQFL2" unsupported in Windows')
            #~ _rp.PQFL2dll(ctypes.byref(_p),
                            #~ ctypes.byref(_q),
                            #~ _x,
                            #~ ctypes.byref(ctypes.c_long(1)),
                            #~ ctypes.byref(_ksat),
                            #~ ctypes.byref(_tbub),
                            #~ ctypes.byref(_tdew),
                            #~ ctypes.byref(_Dlbub),
                            #~ ctypes.byref(_Dvdew),
                            #~ _xbub,
                            #~ _xdew,
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    elif routine.upper() == u'DQ':
        _D.value, _q.value = var1, var2
        if platform.system() == u'Linux':
            raise RefproproutineError(u'function "DQFL2" unsupported in Linux')
            #~ _rp.dqfl2_(ctypes.byref(_D),
                        #~ ctypes.byref(_q),
                        #~ _x,
                        #~ ctypes.byref(_kq),
                        #~ ctypes.byref(_t),
                        #~ ctypes.byref(_p),
                        #~ ctypes.byref(_Dliq),
                        #~ ctypes.byref(_Dvap),
                        #~ _xliq,
                        #~ _xvap,
                        #~ ctypes.byref(_ierr),
                        #~ ctypes.byref(_herr),
                        #~ ctypes.c_long(255))
        elif platform.system() == u'Windows':
            raise RefproproutineError(u'function "DQFL2" unsupported in Windows')
            #~ _rp.DQFL2dll(ctypes.byref(_D),
                            #~ ctypes.byref(_q),
                            #~ _x,
                            #~ ctypes.byref(ctypes.c_long(1)),
                            #~ ctypes.byref(_t),
                            #~ ctypes.byref(_p),
                            #~ ctypes.byref(_Dliq),
                            #~ ctypes.byref(_Dvap),
                            #~ _xliq,
                            #~ _xvap,
                            #~ ctypes.byref(_ierr),
                            #~ ctypes.byref(_herr),
                            #~ ctypes.c_long(255))
    else: raise RefpropinputError(u'Incorrect "routine" input, ' +
                                    unicode(routine) +
                                    u' is an invalid input')
    xliq = normalize([_xliq[each] for each in xrange(_nc_rec.record)])[u'x']
    xvap = normalize([_xvap[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
    if routine.upper() in [u'TH', u'TS', u'TE', u'TD', u'PD', u'PH', u'PS', u'PE',
                           u'TQ', u'PQ', u'DQ']:
        xdew = normalize([_xdew[each] for each in xrange(_nc_rec.record)])[u'x']
        xbub = normalize([_xbub[each] for each in xrange(_nc_rec.record)])[u'x']
        if u'_purefld_rec' in _Setuprecord.object_list \
        and len(x) == 1:
            if len(x) != len(xdew):
                xdew = [xdew[_purefld_rec.record[u'icomp'] - 1]]
            if len(x) != len(xbub):
                xbub = [xbub[_purefld_rec.record[u'icomp'] - 1]]
    if routine.upper() == u'TP':
        return _prop(x = x, t = var1, p = var2, Dliq = _Dliq.value,
                      Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                      q = _q.value, ierr = _ierr.value, herr = _herr.value,
                      defname = defname)
    elif routine.upper() == u'DH':
        return _prop(x = x, D = var1, h = var2, Dliq = _Dliq.value,
                      Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                      q = _q.value,t = _t.value, p = _p.value,
                      ierr = _ierr.value, herr = _herr.value, defname = defname)
    elif routine.upper() == u'DS':
        return _prop(x = x, D = var1, s = var2, Dliq = _Dliq.value,
                      Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                      q = _q.value, t = _t.value, p = _p.value,
                      ierr = _ierr.value, herr = _herr.value, defname = defname)
    elif routine.upper() == u'DE':
        return _prop(x = x, D = var1, e = var2, Dliq = _Dliq.value,
                      Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                      q = _q.value, t = _t.value, p = _p.value,
                      ierr = _ierr.value, herr = _herr.value, defname = defname)
    elif routine.upper() == u'TH':
        if ksat == 0:
            return _prop(x = x, t = var1, h = var2, Dliq = _Dliq.value,
                          ksat = ksat, Dvap = _Dvap.value, xliq = xliq,
                          xvap = xvap, q = _q.value, p = _p.value,
                          ierr = _ierr.value, herr = _herr.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xbub = xbub, xdew = xdew, defname = defname)
        elif ksat == 1:
            return _prop(x = x, t = var1, h = var2, Dliq = _Dliq.value,
                          ksat = ksat, Dvap = _Dvap.value, xliq = xliq,
                          xvap = xvap, q = _q.value, p = _p.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xbub = xbub, xdew = xdew, ierr = _ierr.value,
                          herr = _herr.value, defname = defname)
    elif routine.upper() == u'TS':
        if ksat == 0:
            return _prop(x = x, t = var1, s = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, p = _p.value, ierr = _ierr.value,
                          herr = _herr.value, pbub = _pbub.value,
                          pdew = _pdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ksat = ksat, defname = defname)
        elif ksat == 1:
            return _prop(x = x, t = var1, s = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, p = _p.value, pbub = _pbub.value,
                          pdew = _pdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ierr = _ierr.value, herr = _herr.value, ksat = ksat,
                          defname = defname)
    elif routine.upper() == u'TE':
        if ksat == 0:
            return _prop(x = x, t = var1, e = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, p = _p.value, ierr = _ierr.value,
                          herr = _herr.value, pbub = _pbub.value,
                          pdew = _pdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ksat = ksat, defname = defname)
        elif ksat == 1:
            return _prop(x = x, t = var1, e = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, p = _p.value, pbub = _pbub.value,
                          pdew = _pdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ierr = _ierr.value, herr = _herr.value, ksat = ksat,
                          defname = defname)
    elif routine.upper() == u'TD':
        if ksat == 0:
            return _prop(x = x, t = var1, D = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, p = _p.value, ierr = _ierr.value,
                          herr = _herr.value, pbub = _pbub.value,
                          pdew = _pdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ksat = ksat, defname = defname)
        elif ksat == 1:
            return _prop(x = x, t = var1, D = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, p = _p.value, pbub = _pbub.value,
                          pdew = _pdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ierr = _ierr.value, herr = _herr.value, ksat = ksat,
                          defname = defname)
    elif routine.upper() == u'PD':
        if ksat == 0:
            return _prop(x = x, p = var1, D = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, t = _t.value, ierr = _ierr.value,
                          herr = _herr.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ksat = ksat, defname = defname)
            return prop
        elif ksat == 1:
            return _prop(x = x, p = var1, D = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq,    xvap = xvap,
                          q = _q.value, t = _t.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ierr = _ierr.value, herr = _herr.value, ksat = ksat,
                          defname = defname)
    elif routine.upper() == u'PH':
        if ksat == 0:
            return _prop(x = x, p = var1, h = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, t = _t.value, ierr = _ierr.value,
                          herr = _herr.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ksat = ksat, defname = defname)
        elif ksat == 1:
            return _prop(x = x, p = var1, h = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, t = _t.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ierr = _ierr.value, herr = _herr.value, ksat = ksat,
                          defname = defname)
    elif routine.upper() == u'PS':
        if ksat == 0:
            return _prop(x = x, p = var1, s = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, t = _t.value, ierr = _ierr.value,
                          herr = _herr.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ksat = ksat, defname = defname)
        elif ksat == 1:
            return _prop(x = x, p = var1, s = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, t = _t.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ierr = _ierr.value, herr = _herr.value, ksat = ksat,
                          defname = defname)
    elif routine.upper() == u'PE':
        if ksat == 0:
            return _prop(x = x, p = var1, e = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, t = _t.value, ierr = _ierr.value,
                          herr = _herr.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ksat = ksat, defname = defname)
        elif ksat == 1:
            return _prop(x = x, p = var1, e = var2, Dliq = _Dliq.value,
                          Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          q = _q.value, t = _t.value, tbub = _tbub.value,
                          tdew = _tdew.value, Dlbub = _Dlbub.value,
                          Dvdew = _Dvdew.value, xbub = xbub, xdew = xdew,
                          ierr = _ierr.value, herr = _herr.value, ksat = ksat,
                          defname = defname)
    elif routine.upper() == u'TQ':
        if ksat == 0:
            return _prop(x = x, t = var1, q = var2, Dliq = _Dliq.value,
                          kq = kq, Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          p = _p.value, ierr = _ierr.value, herr = _herr.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xbub = xbub, xdew = xdew, ksat = ksat,
                          defname = defname)
        elif ksat == 1:
            return _prop(x = x, t = var1, q = var2, Dliq = _Dliq.value,
                          kq = kq, Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          p = _p.value, pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xbub = xbub, xdew = xdew, ierr = _ierr.value,
                          herr = _herr.value, ksat = ksat, defname = defname)
    elif routine.upper() == u'PQ':
        if ksat == 0:
            return _prop(x = x, p = var1, q = var2, Dliq = _Dliq.value,
                          kq = kq, Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          t = _t.value, ierr = _ierr.value, herr = _herr.value,
                          tbub = _tbub.value, tdew = _tdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xbub = xbub, xdew = xdew, ksat = ksat,
                          defname = defname)
        elif ksat == 1:
            return _prop(x = x, p = var1, q = var2, Dliq = _Dliq.value,
                          kq = kq, Dvap = _Dvap.value, xliq = xliq, xvap = xvap,
                          t = _t.value, tbub = _tbub.value, tdew = _tdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xbub = xbub, xdew = xdew, ierr = _ierr.value,
                          herr = _herr.value, ksat = ksat, defname = defname)
    #~ elif routine.upper() == 'DQ':
        #~ return _prop(x = x, D = var1, q = var2, Dliq = _Dliq.value, kq = kq,
                #~ Dvap = _Dvap.value, xliq = xliq, xvap = xvap, t = _t.value,
                #~ p = _p.value, ierr = _ierr.value, herr = _herr.value, defname = defname)


def _abfl2(routine, var1, var2, x, kq=1, ksat=0, tbub=0, tdew=0, pbub=0,
    pdew=0, Dlbub=0, Dvdew=0, xbub=None, xdew=None):
    u"""General flash calculation given two inputs and composition.  Valid
    properties for the first input are temperature and pressure.  Valid
    properties for the second input are density, energy, enthalpy, entropy,
    or quality.  The character string ab specifies the inputs.  Note that
    the input TP is not allowed here, but is done by calling TPFLSH or
    TPFL2.

    This routine calls TPFL2 within a secant-method iteration for
    pressure to find a solution.  Initial guesses are based on liquid
    density at the bubble point and vapor density at the dew point.

    inputs:
        routine--character*2 string defining the inputs, e.g., 'TD' or 'PQ'
        var1--first property (either temperature or pressure)
        var2--second property (density, energy, enthalpy, entropy, or quality)
        x--overall (bulk) composition [array of mol frac]
        kq--flag specifying units for input quality when b=quality
            kq = 1 [default] quality on MOLAR basis [moles vapor/total moles]
            kq = 2 quality on MASS basis [mass vapor/total mass]
        ksat--flag for bubble and dew point limits
            0 [default] = dew and bubble point limits computed here
            1 = must provide values for the following:
                (for a=pressure):
                    tbub--bubble point temperature [K] at (p,x=z)
                    tdew--dew point temperature [K] at (p,y=z)
                (for a=temperature):
                    pbub--bubble point pressure [kPa] at (t,x=z)
                    pdew--dew point pressure [kPa] at (t,y=z)
                (for either case):
                    Dlbub--liquid density [mol/L] at bubble point
                    Dvdew--vapor density [mol/L] at dew point
                    xbub--vapor composition [array of mol frac] at bubble point
                    xdew--liquid composition [array of mol frac] at dew point

    outputs:
        t--temperature [K]
        p--pressure [kPa]
        D--molar density [mol/L]
        Dliq--molar density [mol/L] of the liquid phase
        Dvap--molar density [mol/L] of the vapor phase
        xliq--composition of liquid phase [array of mol frac]
        xvap--composition of vapor phase [array of mol frac]
        q--vapor quality on a MOLAR basis [moles vapor/total moles]"""

    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    for each in xrange(len(x)):
        _x[each] = x[each]
        if xdew:
            for each in xrange(len(xdew)): _xdew[each] = xdew[each]
        if xbub:
            for each in xrange(len(xbub)): _xbub[each] = xbub[each]
    _ksat.value, _tbub.value, _kq.value = ksat, tbub, kq
    _tdew.value, _pbub.value, _pdew.value = tdew, pbub, pdew
    _Dlbub.value, _Dvdew.value = Dlbub, Dvdew
    _var1.value, _var2.value = var1, var2
    _routine.value = routine.upper().encode(u'ascii')

    if platform.system() == u'Linux':
        _rp.abfl2_(ctypes.byref(_var1),
                   ctypes.byref(_var2),
                   _x,
                   ctypes.byref(_kq),
                   ctypes.byref(_ksat),
                   ctypes.byref(_routine),
                   ctypes.byref(_tbub),
                   ctypes.byref(_tdew),
                   ctypes.byref(_pbub),
                   ctypes.byref(_pdew),
                   ctypes.byref(_Dlbub),
                   ctypes.byref(_Dvdew),
                   _xbub,
                   _xdew,
                   ctypes.byref(_t),
                   ctypes.byref(_p),
                   ctypes.byref(_Dliq),
                   ctypes.byref(_Dvap),
                   _xliq,
                   _xvap,
                   ctypes.byref(_q),
                   ctypes.byref(_ierr),
                   ctypes.byref(_herr),
                   ctypes.c_long(2),
                   ctypes.c_long(255))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'function "ABFL2" unsupported in Windows')

    #define various x values
    xliq = normalize([_xliq[each] for each in xrange(_nc_rec.record)])[u'x']
    xvap = normalize([_xvap[each] for each in xrange(_nc_rec.record)])[u'x']
    xdew = normalize([_xdew[each] for each in xrange(_nc_rec.record)])[u'x']
    xbub = normalize([_xbub[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xdew):
            xdew = [xdew[_purefld_rec.record[u'icomp'] - 1]]
        if len(x) != len(xbub):
            xbub = [xbub[_purefld_rec.record[u'icomp'] - 1]]

    #Dvap and Dliq
    Dvap, Dliq = _Dvap.value, _Dliq.value
    #define q
    if routine.upper()[1] == u'Q':
        q = var2
    else:
        q = _q.value

    #calculate D
    if routine.upper()[1] == u'D':
        D = var2
    else:
        if Dliq == 0:
            D = Dvap
        elif Dvap == 0:
            D = Dliq
        else:
            D = 1 / (((1 / Dvap) * q) + ((1 / Dliq) * (1 - q)))

    #raise error if routine input is incorrect
    if not routine.upper()[0] in u'PT':
        raise RefpropinputError(u'Incorrect "routine" input, ' + unicode(routine) +
                                 u' is an invalid input')
    if not routine.upper()[1] in u'DEHSQ':
        raise RefpropinputError(u'Incorrect "routine" input, ' + unicode(routine) +
                                 u' is an invalid input')

    #return correction on the first input variable
    if routine.upper()[0] == u'P':
        #return correction on the second input variable
        if routine.upper()[1] == u'S':
            return _prop(x = x, t = _t.value, p = var1, s = var2, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, tbub = _tbub.value, tdew = _tdew.value,
                          defname = defname)
        elif routine.upper()[1] == u'H':
            return _prop(x = x, t = _t.value, p = var1, h = var2, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, tbub = _tbub.value, tdew = _tdew.value,
                          defname = defname)
        elif routine.upper()[1] == u'D':
            return _prop(x = x, t = _t.value, p = var1, D = var2, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, tbub = _tbub.value, tdew = _tdew.value,
                          defname = defname)
        elif routine.upper()[1] == u'E':
            return _prop(x = x, t = _t.value, p = var1, e = var2, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, tbub = _tbub.value, tdew = _tdew.value,
                          defname = defname)
        elif routine.upper()[1] == u'Q':
            return _prop(x = x, t = _t.value, p = var1, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, tbub = _tbub.value, tdew = _tdew.value,
                          defname = defname)
    elif routine.upper()[0] == u'T':
        #return correction on the second input variable
        if routine.upper()[1] == u'S':
            return _prop(x = x, t = var1, p = _p.value, s = var2, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, defname = defname)
        elif routine.upper()[1] == u'H':
            return _prop(x = x, t = var1, p = _p.value, h = var2, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, defname = defname)
        elif routine.upper()[1] == u'D':
            return _prop(x = x, t = var1, p = _p.value, D = var2, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, defname = defname)
        elif routine.upper()[1] == u'E':
            return _prop(x = x, t = var1, p = _p.value, e = var2, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, defname = defname)
        elif routine.upper()[1] == u'Q':
            return _prop(x = x, t = var1, p = _p.value, D = D, q = q,
                          Dliq = Dliq, Dvap = Dvap, xliq = xliq, xbub = xbub,
                          xvap = xvap, ksat = ksat, kq = kq,
                          ierr = _ierr.value, herr = _herr.value,
                          pbub = _pbub.value, pdew = _pdew.value,
                          Dlbub = _Dlbub.value, Dvdew = _Dvdew.value,
                          xdew = xdew, defname = defname)


def info(icomp=1):
    u'''Provides fluid constants for specified component

    input:
        icomp--component number in mixture; 1 for pure fluid
    outputs:
        wmm--molecular weight [g/mol]
        ttrp--triple point temperature [K]
        tnbpt--normal boiling point temperature [K]
        tcrit--critical temperature [K]
        pcrit--critical pressure [kPa]
        Dcrit--critical density [mol/L]
        zcrit--compressibility at critical point [pc/(Rgas*Tc*Dc)]
        acf--accentric factor [-]
        dip--dipole moment [debye]
        Rgas--gas constant [J/mol-K]'''
    _inputerrorcheck(locals())
    _icomp.value = icomp
    if platform.system() == u'Linux':
        _rp.info_(ctypes.byref(_icomp),
                    ctypes.byref(_wmm),
                    ctypes.byref(_ttrp),
                    ctypes.byref(_tnbpt),
                    ctypes.byref(_tcrit),
                    ctypes.byref(_pcrit),
                    ctypes.byref(_Dcrit),
                    ctypes.byref(_zcrit),
                    ctypes.byref(_acf),
                    ctypes.byref(_dip),
                    ctypes.byref(_Rgas))
    elif platform.system() == u'Windows':
        _rp.INFOdll(ctypes.byref(_icomp),
                        ctypes.byref(_wmm),
                        ctypes.byref(_ttrp),
                        ctypes.byref(_tnbpt),
                        ctypes.byref(_tcrit),
                        ctypes.byref(_pcrit),
                        ctypes.byref(_Dcrit),
                        ctypes.byref(_zcrit),
                        ctypes.byref(_acf),
                        ctypes.byref(_dip),
                        ctypes.byref(_Rgas))
    return _prop(icomp = icomp, wmm = _wmm.value, ttrp = _ttrp.value,
            tnbpt = _tnbpt.value, tcrit = _tcrit.value, Dcrit = _Dcrit.value,
            zcrit = _zcrit.value, acf = _acf.value, dip = _dip.value,
            Rgas = _Rgas.value)


def rmix2(x):
    u'''Return the gas "constant" as a combination of the gas constants for
    the pure fluids

    inputs:
        x--composition [array of mol frac]
    outputs:
        Rgas--gas constant [J/mol-K]'''
    _inputerrorcheck(locals())
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.rmix2_(_x,
                    ctypes.byref(_Rgas))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'function "rmix2" unsupported in Windows')
        _rp.RMIX2dll(_x,
                        ctypes.byref(_Rgas))
    return _prop(x = x, Rgas = _Rgas.value)


def xmass(x):
    u'''Converts composition on a mole fraction basis to mass fraction

    input:
        x--composition array [array of mol frac]
    outputs:
        xkg--composition array [array of mass frac]
        wmix--molar mass of the mixture [g/mol], a.k.a. "molecular weight"'''
    _inputerrorcheck(locals())
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.xmass_(_x,
                   _xkg,
                   ctypes.byref(_wmix))
    elif platform.system() == u'Windows':
        _rp.XMASSdll(_x,
                     _xkg,
                     ctypes.byref(_wmix))
    xkg = normalize([_xkg[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(x) == 1:
        if len(x) != len(xkg):
            xkg = [xkg[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(x = x, xkg = xkg, wmix = _wmix.value)


def xmole(xkg):
    u'''Converts composition on a mass fraction basis to mole fraction

    input:
        xkg--composition array [array of mass frac]
    outputs:
        x--composition array [array of mol frac]
        wmix--molar mass of the mixture [g/mol], a.k.a. "molecular weight"'''
    _inputerrorcheck(locals())
    for each in xrange(len(xkg)): _xkg[each] = xkg[each]
    if platform.system() == u'Linux':
        _rp.xmole_(_xkg,
                   _x,
                   ctypes.byref(_wmix))
    elif platform.system() == u'Windows':
        _rp.XMOLEdll(_xkg,
                     _x,
                     ctypes.byref(_wmix))
    x = normalize([_x[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and len(xkg) == 1:
        if len(xkg) != len(x):
            x = [x[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(xkg = xkg, x = x, wmix = _wmix.value)


def limitx(x, htype=u'EOS', t=0, D=0, p=0):
    u'''returns limits of a property model as a function of composition
    and/or checks input t, D, p against those limits

    Pure fluid limits are read in from the .FLD files; for mixtures, a
    simple mole fraction weighting in reduced variables is used.

    Attempting calculations below the mininum temperature and/or above the
    maximum density will result in an error. These will often correspond to
    a physically unreasonable state; also many equations of state do not
    extrapolate reliably to lower T's and higher D's.

    A warning is issued if the temperature is above the maximum but below
    1.5 times the maximum; similarly pressures up to twice the maximum
    result in only a warning. Most equations of state may be extrapolated to
    higher T's and P's. Temperatures and/or pressures outside these extended
    limits will result in an error.

    When calling with an unknown temperature, set t to -1 to avoid
    performing the melting line check

    inputs:
        x--composition array [mol frac]
        htype--flag indicating which models are to be checked [character*3]
            'EOS':  equation of state for thermodynamic properties
            'ETA':  viscosity
            'TCX':  thermal conductivity
            'STN':  surface tension
        t--temperature [K]
        D--molar density [mol/L]
        p--pressure [kPa]
            N.B.--all inputs must be specified, if one or more are not
            available, (or not applicable as in case of surface tension)
            use reasonable values, such as:
                t = tnbp
                D = 0
                p = 0
    outputs:
        tmin--minimum temperature for model specified by htyp [K]
        tmax--maximum temperature [K]
        Dmax--maximum density [mol/L]
        pmax--maximum pressure [kPa]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _htype.value = htype.upper().encode(u'ascii')
    for each in xrange(len(x)): _x[each] = x[each]
    _t.value, _D.value, _p.value = t, D, p
    if platform.system() == u'Linux':
        _rp.limitx_(ctypes.byref(_htype),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_p),
                        _x,
                        ctypes.byref(_tmin),
                        ctypes.byref(_tmax),
                        ctypes.byref(_Dmax),
                        ctypes.byref(_pmax),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(3),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.LIMITXdll(ctypes.byref(_htype),
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_p),
                            _x,
                            ctypes.byref(_tmin),
                            ctypes.byref(_tmax),
                            ctypes.byref(_Dmax),
                            ctypes.byref(_pmax),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(3),
                            ctypes.c_long(255))
    return _prop(x = x, t = t, D = D, htype = htype.upper(), p = p,
                  tmin = _tmin.value, tmax = _tmax.value, Dmax = _Dmax.value,
                  pmax = _pmax.value, ierr = _ierr.value, herr = _herr.value,
                  defname = defname)


def limitk(htype=u'EOS', icomp=1, t=u'tnbp', D=0, p=0):
    u'''Returns limits of a property model (read in from the .FLD files) for
    a mixture component and/or checks input t, D, p against those limits

    This routine functions in the same manner as LIMITX except that the
    composition x is replaced by the component number icomp.

    Attempting calculations below the minimum temperature and/or above the
    maximum density will result in an error. These will often correspond to
    a physically unreasonable state; also many equations of state do not
    extrapolate reliably to lower T's and higher D's.

    A warning is issued if the temperature is above the maximum but below
    1.5 times the maximum; similarly pressures up to twice the maximum
    result in only a warning. Most equations of state may be extrapolated to
    higher T's and P's. Temperatures and/or pressures outside these extended
    limits will result in an error.

    inputs:
        htyp--flag indicating which models are to be checked [character*3]
            'EOS':  equation of state for thermodynamic properties
            'ETA':  viscosity
            'TCX':  thermal conductivity
            'STN':  surface tension
        icomp--component number in mixture; 1 for pure fluid
        t--temperature [K]
        D--molar density [mol/L]
        p--pressure [kPa]
            N.B.--all inputs must be specified, if one or more are not
            available, (or not applicable as in case of surface tension) use
            reasonable values, such as:
                t = tnbp (normal boiling point temperature)
                D = 0
                p = 0
    outputs:
        tmin--minimum temperature for model specified by htyp [K]
        tmax--maximum temperature [K]
        Dmax--maximum density [mol/L]
        pmax--maximum pressure [kPa]'''
    if t == u'tnbp':
        t = info(icomp)[u'tnbpt']

    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _htype.value = htype.upper().encode(u'ascii')
    _icomp.value = icomp
    _t.value, _D.value, _p.value = t, D, p

    if platform.system() == u'Linux':
        _rp.limitk_(ctypes.byref(_htype),
                        ctypes.byref(_icomp),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        ctypes.byref(_p),
                        ctypes.byref(_tmin),
                        ctypes.byref(_tmax),
                        ctypes.byref(_Dmax),
                        ctypes.byref(_pmax),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(3),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.LIMITKdll(ctypes.byref(_htype),
                            ctypes.byref(_icomp),
                            ctypes.byref(_t),
                            ctypes.byref(_D),
                            ctypes.byref(_p),
                            ctypes.byref(_tmin),
                            ctypes.byref(_tmax),
                            ctypes.byref(_Dmax),
                            ctypes.byref(_pmax),
                            ctypes.byref(_ierr),
                            ctypes.byref(_herr),
                            ctypes.c_long(3),
                            ctypes.c_long(255))
    return _prop(icomp = icomp, t = t, D = D, htype = htype.upper(),
            p = p, tmin = _tmin.value, tmax = _tmax.value,
            Dmax = _Dmax.value, pmax = _pmax.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def limits(x, htype=u'EOS'):
    u'''Returns limits of a property model as a function of composition.

    Pure fluid limits are read in from the .FLD files; for mixtures, a
    simple mole fraction weighting in reduced variables is used.

    inputs:
        htype--flag indicating which models are to be checked [character*3]
            'EOS':  equation of state for thermodynamic properties
            'ETA':  viscosity
            'TCX':  thermal conductivity
            'STN':  surface tension
        x--composition array [mol frac]
    outputs:
        tmin--minimum temperature for model specified by htyp [K]
        tmax--maximum temperature [K]
        Dmax--maximum density [mol/L]
        pmax--maximum pressure [kPa]'''
    _inputerrorcheck(locals())
    _htype.value = htype.upper().encode(u'ascii')
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.limits_(ctypes.byref(_htype),
                        _x,
                        ctypes.byref(_tmin),
                        ctypes.byref(_tmax),
                        ctypes.byref(_Dmax),
                        ctypes.byref(_pmax),
                        ctypes.c_long(3))
    elif platform.system() == u'Windows':
        _rp.LIMITSdll(ctypes.byref(_htype),
                            _x,
                            ctypes.byref(_tmin),
                            ctypes.byref(_tmax),
                            ctypes.byref(_Dmax),
                            ctypes.byref(_pmax),
                            ctypes.c_long(3))
    return _prop(x = x,
            htype = htype.upper(), tmin = _tmin.value, tmax = _tmax.value,
            Dmax = _Dmax.value, pmax = _pmax.value)


def qmass(q, xliq, xvap):
    u'''converts quality and composition on a mole basis to a mass basis

    inputs:
        q--molar quality [moles vapor/total moles]
            qmol = 0 indicates saturated liquid
            qmol = 1 indicates saturated vapor
            0 < qmol < 1 indicates a two-phase state
            mol < 0 or qmol > 1 are not allowed and will result in warning
        xliq--composition of liquid phase [array of mol frac]
        xvap--composition of vapor phase [array of mol frac]
    outputs:
        qkg--quality on mass basis [mass of vapor/total mass]
        xlkg--mass composition of liquid phase [array of mass frac]
        xvkg--mass composition of vapor phase [array of mass frac]
        wliq--molecular weight of liquid phase [g/mol]
        wvap--molecular weight of vapor phase [g/mol]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _q.value = q
    for each in xrange(len(xliq)):
        _xliq[each] = xliq[each]
    for each in xrange(len(xvap)):
        _xvap[each] = xvap[each]
    if platform.system() == u'Linux':
        _rp.qmass_(ctypes.byref(_q),
                    _xliq,
                    _xvap,
                    ctypes.byref(_qkg),
                    _xlkg,
                    _xvkg,
                    ctypes.byref(_wliq),
                    ctypes.byref(_wvap),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.QMASSdll(ctypes.byref(_q),
                        _xliq,
                        _xvap,
                        ctypes.byref(_qkg),
                        _xlkg,
                        _xvkg,
                        ctypes.byref(_wliq),
                        ctypes.byref(_wvap),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    xlkg = normalize([_xlkg[each] for each in xrange(_nc_rec.record)])[u'x']
    xvkg = normalize([_xvkg[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and (len(xliq) == 1 or len(xvap) == 1):
        if len(xliq) != len(xlkg):
            xlkg = [xlkg[_purefld_rec.record[u'icomp'] - 1]]
        if len(xvap) != len(xvkg):
            xvkg = [xvkg[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(q = q, xliq = xliq, xvap = xvap, qkg = _qkg.value, xlkg = xlkg,
            xvkg = xvkg, wliq = _wliq.value, wvap = _wvap.value,
            ierr = _ierr.value, herr = _herr.value, defname = defname)


def qmole(qkg, xlkg, xvkg):
    u'''Converts quality and composition on a mass basis to a molar basis.

    inputs:
        qkg--quality on mass basis [mass of vapor/total mass]
            qkg = 0 indicates saturated liquid
            qkg = 1 indicates saturated vapor
            0 < qkg < 1 indicates a two-phase state
            qkg < 0 or qkg > 1 are not allowed and will result in warning
        xlkg--mass composition of liquid phase [array of mass frac]
        xvkg--mass composition of vapor phase [array of mass frac]
    outputs:
        q--quality on mass basis [mass of vapor/total mass]
        xliq--molar composition of liquid phase [array of mol frac]
        xvap--molar composition of vapor phase [array of mol frac]
        wliq--molecular weight of liquid phase [g/mol]
        wvap--molecular weight of vapor phase [g/mol]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _qkg.value = qkg
    for each in xrange(len(xlkg)):
        _xlkg[each] = xlkg[each]
    for each in xrange(len(xvkg)):
        _xvkg[each] = xvkg[each]
    if platform.system() == u'Linux':
        _rp.qmole_(ctypes.byref(_qkg),
                    _xlkg,
                    _xvkg,
                    ctypes.byref(_q),
                    _xliq,
                    _xvap,
                    ctypes.byref(_wliq),
                    ctypes.byref(_wvap),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.QMOLEdll(ctypes.byref(_qkg),
                        _xlkg,
                        _xvkg,
                        ctypes.byref(_q),
                        _xliq,
                        _xvap,
                        ctypes.byref(_wliq),
                        ctypes.byref(_wvap),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    xliq = normalize([_xliq[each] for each in xrange(_nc_rec.record)])[u'x']
    xvap = normalize([_xvap[each] for each in xrange(_nc_rec.record)])[u'x']
    if u'_purefld_rec' in _Setuprecord.object_list \
    and (len(xlkg) == 1 or len(xvkg) == 1):
        if len(xlkg) != len(xliq):
            xliq = [xliq[_purefld_rec.record[u'icomp'] - 1]]
        if len(xvkg) != len(xvap):
            xvap = [xvap[_purefld_rec.record[u'icomp'] - 1]]
    return _prop(qkg = qkg, xlkg = xlkg, xvkg = xvkg, q = _q.value, xliq = xliq,
            xvap = xvap, wliq = _wliq.value, wvap = _wvap.value,
            ierr = _ierr.value, herr = _herr.value, defname = defname)


def wmol(x):
    u'''Molecular weight for a mixture of specified composition

    input:
        x--composition array [array of mol frac]
    output (as function value):
        wmix--molar mass [g/mol], a.k.a. "molecular weight'''
    _inputerrorcheck(locals())
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.wmoldll_(_x,
                    ctypes.byref(_wmix))
    elif platform.system() == u'Windows':
        _rp.WMOLdll(_x,
                        ctypes.byref(_wmix))
    return _prop(x = x, wmix = _wmix.value)


def dielec(t, D, x):
    u'''Compute the dielectric constant as a function of temperature,
    density, and composition.

    inputs:
        t--temperature [K]
        d--molar density [mol/L]
        x--composition [array of mol frac]
    output:
        de--dielectric constant'''
    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.dielec_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_de))
    elif platform.system() == u'Windows':
        _rp.DIELECdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_de))
    return _prop(x = x, t = t, D= D, de = _de.value)


def surft(t, x):
    u'''Compute surface tension

    inputs:
        t--temperature [K]
        x--composition [array of mol frac] (liquid phase input only)
    outputs:
        D--molar density of liquid phase [mol/L]
            if D > 0 use as input value
            < 0 call SATT to find density
        sigma--surface tension [N/m]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.surft_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_sigma),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SURFTdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_sigma),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(x = x, t = t, D = _D.value, sigma = _sigma.value,
                    ierr = _ierr.value, herr = _herr.value, defname = defname)


def surten(t, Dliq, Dvap, xliq, xvap):
    u'''Compute surface tension

    inputs:
        t--temperature [K]
        Dliq--molar density of liquid phase [mol/L]
        Dvap--molar density of vapor phase [mol/L]
            if either Dliq or Dvap < 0 call SATT to find densities
        xliq--composition of liquid phase [array of mol frac]
        xvap--composition of liquid phase [array of mol frac]
            (xvap is optional input if Dliq < 0 or Dvap < 0)
    outputs:
        sigma--surface tension [N/m]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _t.value, _Dliq.value, _Dvap.value = t, Dliq, Dvap
    for each in xrange(len(xliq)):
        _xliq[each] = xliq[each]
    for each in xrange(len(xvap)):
        _xvap[each] = xvap[each]
    if platform.system() == u'Linux':
        _rp.surten_(ctypes.byref(_t),
                        ctypes.byref(_Dliq),
                        ctypes.byref(_Dvap),
                        _xliq,
                        _xvap,
                        ctypes.byref(_sigma),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SURTENdll(ctypes.byref(_t),
                        ctypes.byref(_Dliq),
                        ctypes.byref(_Dvap),
                        _xliq,
                        _xvap,
                        ctypes.byref(_sigma),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(t = t, Dliq = Dliq, Dvap = Dvap, xliq = xliq, xvap = xvap,
            sigma = _sigma.value, ierr = _ierr.value, herr = _herr.value,
            defname = defname)


def meltt(t, x):
    u'''Compute the melting line pressure as a function of temperature and
    composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    output:
        p--melting line pressure [kPa]

    Caution
        if two valid outputs the function will returns the highest'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.meltt_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_p),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.MELTTdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(t = t, x = x, p = _p.value, ierr = _ierr.value,
                        herr = _herr.value, defname = defname)


def meltp(p, x):
    u'''Compute the melting line temperature as a function of pressure and
    composition.

    inputs:
        p--melting line pressure [kPa]
        x--composition [array of mol frac]
    output:
        t--temperature [K]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _p.value = p
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.meltp_(ctypes.byref(_p),
                        _x,
                        ctypes.byref(_t),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.MELTPdll(ctypes.byref(_p),
                        _x,
                        ctypes.byref(_t),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(p = p, x = x, t = _t.value, ierr = _ierr.value,
                    herr = _herr.value, defname = defname)


def sublt(t, x):
    u'''Compute the sublimation line pressure as a function of temperature
    and composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    output:
        p--sublimation line pressure [kPa]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.sublt_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_p),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SUBLTdll(ctypes.byref(_t),
                        _x,
                        ctypes.byref(_p),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(t = t, x = x, p = _p.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def sublp(p, x):
    u'''Compute the sublimation line temperature as a function of pressure
    and composition.

    inputs:
        p--melting line pressure [kPa]
        x--composition [array of mol frac]
    output:
        t--temperature [K]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _p.value = p
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.sublp_(ctypes.byref(_p),
                    _x,
                    ctypes.byref(_t),
                    ctypes.byref(_ierr),
                    ctypes.byref(_herr),
                    ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SUBLPdll(ctypes.byref(_p),
                        _x,
                        ctypes.byref(_t),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(p = p, x = x, t = _t.value, ierr = _ierr.value,
                    herr = _herr.value, defname = defname)


def trnprp(t, D, x):
    u'''Compute the transport properties of thermal conductivity and
    viscosity as functions of temperature, density, and composition

    inputs:
        t--temperature [K]
        D--molar density [mol/L]
        x--composition array [mol frac]
    outputs:
        eta--viscosity (uPa.s)
        tcx--thermal conductivity (W/m.K)'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.trnprp_(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_eta),
                        ctypes.byref(_tcx),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.TRNPRPdll(ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_eta),
                        ctypes.byref(_tcx),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(x = x, D = D, t = t, eta = _eta.value, tcx = _tcx.value,
            ierr = _ierr.value, herr = _herr.value, defname = defname)


def getktv(icomp, jcomp):
    u'''Retrieve mixture model and parameter info for a specified binary

    This subroutine should not be called until after a call to SETUP.

    inputs:
        icomp--component i
        jcomp--component j
    outputs:
        hmodij--mixing rule for the binary pair i,j (e.g. LJ1 or LIN)
            [character*3]
        fij--binary mixture parameters [array of dimension nmxpar;
            currently nmxpar is set to 6]; the parameters will vary depending
            on hmodij;
        hfmix--file name [character*255] containing parameters for the binary
            mixture model
        hfij--description of the binary mixture parameters [character*8 array
            of dimension nmxpar] for example, for the Lemmon-Jacobsen model
            (LJ1):
                fij(1) = zeta
                fij(2) = xi
                fij(3) = Fpq
                fij(4) = beta
                fij(5) = gamma
                fij(6) = 'not used'
        hbinp--documentation for the binary parameters [character*255]
            terminated with ASCII null character
        hmxrul--description of the mixing rule [character*255]'''
    _inputerrorcheck(locals())
    _icomp.value, _jcomp.value = icomp, jcomp
    if platform.system() == u'Linux':
        _rp.getktv_(ctypes.byref(_icomp),
                        ctypes.byref(_jcomp),
                        ctypes.byref(_hmodij),
                        _fij,
                        ctypes.byref(_hfmix),
                        _hfij,
                        ctypes.byref(_hbinp),
                        ctypes.byref(_hmxrul),
                        ctypes.c_long(3),
                        ctypes.c_long(255),
                        ctypes.c_long(8),
                        ctypes.c_long(255),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.GETKTVdll(ctypes.byref(_icomp),
                        ctypes.byref(_jcomp),
                        ctypes.byref(_hmodij),
                        _fij,
                        ctypes.byref(_hfmix),
                        _hfij,
                        ctypes.byref(_hbinp),
                        ctypes.byref(_hmxrul),
                        ctypes.c_long(3),
                        ctypes.c_long(255),
                        ctypes.c_long(8),
                        ctypes.c_long(255),
                        ctypes.c_long(255))
    return _prop(icomp = icomp, jcomp = jcomp,
            hmodij = _hmodij.value.decode(u'utf-8'),
            fij = [_fij[each] for each in xrange(_nmxpar)],
            hfmix = _hfmix.value.decode(u'utf-8'),
            hbinp = _hbinp.value.decode(u'utf-8').rstrip(),
            hmxrul = _hmxrul.value.decode(u'utf-8').rstrip(),
            #correction on system error
            #hfij = [_hfij[each].value.decode('utf-8').strip()
            #         for each in range(_nmxpar)])
            hfij = [_hfij[0].value.decode(u'utf-8')[each * 8: each * 8 + 8].strip()
                      for each in xrange(_nmxpar)])


def getmod(icomp, htype):
    u'''Retrieve citation information for the property models used

    inputs:
        icomp--pointer specifying component number
            zero and negative values are used for ECS reference fluid(s)
        htype--flag indicating which model is to be retrieved [character*3]
            'EOS':  equation of state for thermodynamic properties
            'CP0':  ideal part of EOS (e.g. ideal-gas heat capacity)
            'ETA':  viscosity
            'VSK':  viscosity critical enhancement
            'TCX':  thermal conductivity
            'TKK':  thermal conductivity critical enhancement
            'STN':  surface tension
            'DE ':  dielectric constant
            'MLT':  melting line (freezing line, actually)
            'SBL':  sublimation line
            'PS ':  vapor pressure equation
            'DL ':  saturated liquid density equation
            'DV ':  saturated vapor density equation
    outputs:
        hcode--component model used for property specified in htype
            some possibilities for thermodynamic properties:
                'FEQ':  Helmholtz free energy model
                'BWR':  pure fluid modified Benedict-Webb-Rubin (MBWR)
                'ECS':  pure fluid thermo extended corresponding states
            some possibilities for viscosity:
                'ECS':  extended corresponding states (all fluids)
                'VS1':  the 'composite' model for R134a, R152a, NH3, etc.
                'VS2':  Younglove-Ely model for hydrocarbons
                'VS4':  generalized friction theory of Quinones-Cisneros and Dieters
                'VS5':  Chung et al model
            some possibilities for thermal conductivity:
                'ECS':  extended corresponding states (all fluids)
                'TC1':  the 'composite' model for R134a, R152a, etc.
                'TC2':  Younglove-Ely model for hydrocarbons
                'TC5':  predictive model of Chung et al. (1988)
            some possibilities for surface tension:
                'ST1':  surface tension as f(tau); tau = 1 - T/Tc
        hcite--component model used for property specified in htype;
            the first 3 characters repeat the model designation of hcode
            and the remaining are the citation for the source'''
    _inputerrorcheck(locals())
    _icomp.value, _htype.value = icomp, htype.upper().encode(u'ascii')
    if platform.system() == u'Linux':
        _rp.getmod_(ctypes.byref(_icomp),
                        ctypes.byref(_htype),
                        ctypes.byref(_hcode),
                        ctypes.byref(_hcite),
                        ctypes.c_long(3),
                        ctypes.c_long(3),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'routine "getmod" unsupported in Windows')
        _rp.getmod_(ctypes.byref(_icomp),
                        ctypes.byref(_htype),
                        ctypes.byref(_hcode),
                        ctypes.byref(_hcite),
                        ctypes.c_long(3),
                        ctypes.c_long(3),
                        ctypes.c_long(255))
    return _prop(icomp = icomp, htype = htype,
                        hcode = _hcode.value.decode(u'utf-8'),
                        hcite = _hcite.value.decode(u'utf-8').rstrip())


def setktv(icomp, jcomp, hmodij, fij=([0] * _nmxpar), hfmix=u'HMX.BNC'):
    u'''Set mixture model and/or parameters

    This subroutine must be called after SETUP, but before any call to
    SETREF; it need not be called at all if the default mixture parameters
    (those read in by SETUP) are to be used.

    inputs:
        icomp--component
        jcomp--component j
        hmodij--mixing rule for the binary pair i,j [character*3] e.g.:
            'LJ1' (Lemmon-Jacobsen model)
            'LM1' (modified Lemmon-Jacobsen model) or
            'LIN' (linear mixing rules)
            'RST' indicates reset all pairs to values from original call to
                SETUP (i.e. those read from file) [all other inputs are
                ignored]
        fij--binary mixture parameters [array of dimension nmxpar; currently
            nmxpar is set to 6] the parameters will vary depending on hmodij;
            for example, for the Lemmon-Jacobsen model
                (LJ1):
                    fij(1) = zeta
                    fij(2) = xi
                    fij(3) = Fpq
                    fij(4) = beta
                    fij(5) = gamma
                    fij(6) = 'not used'
        hfmix--file name [character*255] containing generalized parameters
            for the binary mixture model; this will usually be the same as the
            corresponding input to SETUP (e.g.,':fluids:HMX.BNC')'''
    global _setktv_rec, _setupprop

    #verify multiple model calls
    _checksetupmodel(u'setktv')

    _inputerrorcheck(locals())

    #define setup record for FluidModel
    if hmodij.upper() != u'RST':
        _setktv_rec = _Setuprecord(copy.copy(locals()), u'_setktv_rec')

    defname = sys._getframe(0).f_code.co_name, locals()

    _icomp.value, _jcomp.value = icomp, jcomp
    _hmodij.value = hmodij.upper().encode(u'ascii')
    if hfmix == u'HMX.BNC':
        _hfmix.value = (_fpath + u'fluids/HMX.BNC').encode(u'ascii')
    else: _hfmix.value = hfmix.encode(u'ascii')
    for each in xrange(_nmxpar): _fij[each] = fij[each]
    if platform.system() == u'Linux':
        _rp.setktv_(ctypes.byref(_icomp),
                        ctypes.byref(_jcomp),
                        ctypes.byref(_hmodij),
                        _fij,
                        ctypes.byref(_hfmix),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(3),
                        ctypes.c_long(255),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SETKTVdll(ctypes.byref(_icomp),
                        ctypes.byref(_jcomp),
                        ctypes.byref(_hmodij),
                        _fij,
                        ctypes.byref(_hfmix),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(3),
                        ctypes.c_long(255),
                        ctypes.c_long(255))
    if hmodij.upper() != u'RST':
        stktv = {}
        stktv[u'icomp'] = icomp
        stktv[u'jcomp'] = jcomp
        stktv[u'hmodij'] = hmodij.upper()
        stktv[u'fij'] = fij
        stktv[u'hfmix'] = hfmix
        _setupprop[u'setktv'] = stktv
    elif hmodij.upper() == u'RST':
        if u'setktv' in _setupprop:
            _setupprop.__delitem__(u'setktv')
        if u'_setktv_rec' in _Setuprecord.object_list:
            _setktv_rec = None

    return _prop(ierr = _ierr.value, herr = _herr.value, defname = defname)


def setaga():
    u'''Set up working arrays for use with AGA8 equation of state.

    input:
        none
    outputs:
        none'''
    global _setaga_rec, _setupprop

    #verify multiple model calls
    _checksetupmodel(u'setaga')

    #define setup record for FluidModel
    _setaga_rec = _Setuprecord(copy.copy(locals()), u'_setaga_rec')

    defname = sys._getframe(0).f_code.co_name, locals()

    if platform.system() == u'Linux':
        _rp.setaga_(ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.SETAGAdll(ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    _setupprop[u'setaga'] = True
    return _prop(ierr = _ierr.value, herr = _herr.value, defname = defname)


def unsetaga():
    u'''Load original values into arrays changed in the call to SETAGA.  This
    routine resets the values back to those loaded when SETUP was called.'''
    global _setaga_rec
    if platform.system() == u'Linux':
        _rp.unsetaga_()
    elif platform.system() == u'Windows':
        _rp.UNSETAGAdll()
    if u'setaga' in _setupprop:
        _setupprop.__delitem__(u'setaga')
    if u'_setaga_rec' in _Setuprecord.object_list:
        _setaga_rec = None
    return _prop()

def preos(ixflag=0):
    u'''Turn on or off the use of the PR cubic equation.

    inputs:
        ixflag--flag specifying use of PR:
            0 - Use full equation of state (Peng-Robinson off)
            1 - Use full equation of state with Peng-Robinson for sat. conditions
                (not currently working)
            2 - Use Peng-Robinson equation for all calculations
            -1 - return value with current usage of PR:  0, 1, or 2.'''
    #return value gives error return on preos
    global _preos_rec, _setupprop

    #verify multiple model calls
    _checksetupmodel(u'preos')

    _inputerrorcheck(locals())

    _ixflag.value = ixflag
    if platform.system() == u'Linux':
        _rp.preos_(ctypes.byref(_ixflag))
    elif platform.system() == u'Windows':
        _rp.PREOSdll(ctypes.byref(_ixflag))
    #return settings
    if ixflag == -1:
        #some unknown reason the value is less 2*32
        return _ixflag.value + 2**32
    #reset all preos values
    elif ixflag == 0:
        if u'preos' in _setupprop:
            _setupprop.__delitem__(u'preos')
        if u'_preos_rec' in _Setuprecord.object_list:
            _preos_rec = None
    else:
        _setupprop[u'preos'] = ixflag
        #define setup record for FluidModel
        _preos_rec = _Setuprecord({u'ixflag':ixflag}, u'_preos_rec')
        return _prop()

def getfij(hmodij):
    u'''Retrieve parameter info for a specified mixing rule

    This subroutine should not be called until after a call to SETUP.

    inputs:
        hmodij--mixing rule for the binary pair i,j (e.g. LJ1 or LIN)
            [character*3]
    outputs:
        fij--binary mixture parameters [array of dimension nmxpar; currently
            nmxpar is set to 6]; the parameters will vary depending on hmodij;
        hfij--description of the binary mixture parameters [character*8
            array of dimension nmxpar]
        hmxrul--description of the mixing rule [character*255]'''
    _inputerrorcheck(locals())
    _hmodij.value = hmodij.upper().encode(u'ascii')
    if platform.system() == u'Linux':
        _rp.getfij_(ctypes.byref(_hmodij),
                        _fij,
                        _hfij,
                        ctypes.byref(_hmxrul),
                        ctypes.c_long(3),
                        ctypes.c_long(8),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.GETFIJdll(ctypes.byref(_hmodij),
                        _fij,
                        _hfij,
                        ctypes.byref(_hmxrul),
                        ctypes.c_long(3),
                        ctypes.c_long(8),
                        ctypes.c_long(255))
    return _prop(hmodij = hmodij.upper(),
            fij = [_fij[each] for each in xrange(_nmxpar)],
            hmxrul = _hmxrul.value.decode(u'utf-8').rstrip(),
            #correction on system error
            #hfij = [_hfij[each].value.decode('utf-8').strip()
            #         for each in range(_nmxpar)])
            hfij = [_hfij[0].value.decode(u'utf-8')[each * 8:each * 8 + 8].strip()
                      for each in xrange(_nmxpar)])


def b12(t, x):
    u'''Compute b12 as a function of temperature and composition.

    inputs:
        t--temperature [K]
        x--composition [array of mol frac]
    outputs:
        b--b12 [(L/mol)^2]'''
    _inputerrorcheck(locals())
    _t.value = t
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.b12_(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_b))
    elif platform.system() == u'Windows':
        _rp.B12dll(ctypes.byref(_t),
                    _x,
                    ctypes.byref(_b))
    return _prop(t = t, x = x, b = _b.value)


def excess(t, p, x, kph=0):
    u'''Compute excess properties as a function of temperature, pressure, and
    composition.

    NOT supported on Windows

    inputs:
        t--temperature [K]
        p--pressure [kPa]
        x--composition [array of mol frac]
        kph--phase flag:
            1 = liquid
            2 = vapor
            0 = stable phase
    outputs:
        D--molar density [mol/L] (if input less than 0, used as initial guess)
        vE--excess volume [L/mol]
        eE--excess energy [J/mol]
        hE--excess enthalpy [J/mol]
        sE--excess entropy [J/mol-K]
        aE--excess Helmholtz energy [J/mol]
        gE--excess Gibbs energy [J/mol]'''
    _inputerrorcheck(locals())
    defname = sys._getframe(0).f_code.co_name, locals()

    _t.value, _p.value, _kph.value = t, p, kph
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.excess_(ctypes.byref(_t),
                        ctypes.byref(_p),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_D),
                        ctypes.byref(_vE),
                        ctypes.byref(_eE),
                        ctypes.byref(_hE),
                        ctypes.byref(_sE),
                        ctypes.byref(_aE),
                        ctypes.byref(_gE),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'function "excess" unsupported in Windows')
        _rp.EXCESSdll(ctypes.byref(_t),
                        ctypes.byref(_p),
                        _x,
                        ctypes.byref(_kph),
                        ctypes.byref(_D),
                        ctypes.byref(_vE),
                        ctypes.byref(_eE),
                        ctypes.byref(_hE),
                        ctypes.byref(_sE),
                        ctypes.byref(_aE),
                        ctypes.byref(_gE),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(t = t, p = p, x = x, kph = kph, D = _D.value, vE = _vE.value,
            eE = _eE.value, hE = _hE.value, sE = _sE.value, aE = _aE.value,
            gE = _gE.value, ierr = _ierr.value, herr = _herr.value,
            defname = defname)


def phiderv(icomp, jcomp, t, D, x):
    u'''Calculate various derivatives needed for VLE determination

    based on derivations in the GERG-2004 document for natural gas

    inputs:
        icomp--component number of which to take derivative
        jcomp--component number of which to take derivative
        t--temperature (K)
        D--density (mol/L)
        x--composition [array of mol frac]
    outputs: (where n is mole number)
        dadn--n*partial(alphar)/partial(ni)                     (Eq. 7.16 in GERG)
        dnadn--partial(n*alphar)/partial(ni)                    (Eq. 7.15 in GERG)

        dtdn--n*[partial(Tred)/partial(ni)]/Tred                (Eq. 7.19 in GERG)
        dvdn--n*[partial(Vred)/partial(ni)]/Vred                (Eq. 7.18 in GERG)
            (=-n*[partial(Dred)/partial(ni)]/Dred)
        daddn--del*n*partial(darddel)/partial(ni)               (Eq. 7.17 in GERG)
            where darddel=partial(alphar)/partial(del)
        d2adnn--n*partial^2(n*alphar)/partial(ni)/partial(nj)   (Eq. 7.46 in GERG)
            the following are at constant tau and/or del
        dadxi--partial(alphar)/partial(xi)                      (Eq. 7.21g in GERG)
        sdadxi--sum[xi*partial(alphar)/partial(xi)]             (Eq. 7.21g in GERG)
        dadxij--partial^2(alphar)/partial(xi)/partial(xj)       (Eq. 7.21i in GERG)
        daddx--del*partial^2(alphar)/partial(xi)/partial(del)   (Eq. 7.21j in GERG)
        daddxii--del*partial^3(alphar)/partial(xi)/partial(xj)/partial(del)

    other calculated variables:
        d2addn--del*par.(n*(par.(alphar)/par.(n)/par.(del)      (Eq. 7.50 in GERG)
        d2adtn--tau*par.(n*(par.(alphar)/par.(n)/par.(tau)      (Eq. 7.51 in GERG)
        d2adxn--par.(n*(par.(alphar)/par.(n)/par.(xj)           (Eq. 7.52 in GERG)
    '''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _icomp.value, _jcomp.value = icomp, jcomp
    _t.value, _D.value = t, D
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.phiderv_(ctypes.byref(_icomp),
                        ctypes.byref(_jcomp),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_dadn),
                        ctypes.byref(_dnadn),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        raise RefproproutineError(u'function "phiderv" unsupported in Windows')
        _rp.PHIDRVdll(ctypes.byref(_icomp),
                        ctypes.byref(_jcomp),
                        ctypes.byref(_t),
                        ctypes.byref(_D),
                        _x,
                        ctypes.byref(_dadn),
                        ctypes.byref(_dnadn),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(icomp = icomp, jcomp = jcomp, t = t, D = D, x = x,
            dadn = _dadn.value, dnadn = _dnadn.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


def cstar(t, p, v, x):
    u'''Calculate the critical flow factor, C*, for nozzle flow of a gas
    (subroutine was originally named CCRIT)

    inputs:
        t--temperature [K]
        p--pressure [kPa]
        v--plenum velocity [m/s] (should generally be set to 0 for
            calculating stagnation conditions)
        x--composition [array of mol frac]
    outputs:
        cs--critical flow factor [dimensionless]
        ts--nozzle throat temperature [K]
        Ds--nozzle throat molar density [mol/L]
        ps--nozzle throat pressure [kPa]
        ws--nozzle throat speed of sound [m/s]'''
    defname = sys._getframe(0).f_code.co_name, locals()

    _inputerrorcheck(locals())
    _v.value = v
    _t.value, _p.value = t, p
    for each in xrange(len(x)): _x[each] = x[each]
    if platform.system() == u'Linux':
        _rp.cstar_(ctypes.byref(_t),
                        ctypes.byref(_p),
                        ctypes.byref(_v),
                        _x,
                        ctypes.byref(_cs),
                        ctypes.byref(_ts),
                        ctypes.byref(_Ds),
                        ctypes.byref(_ps),
                        ctypes.byref(_ws),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    elif platform.system() == u'Windows':
        _rp.CSTARdll(ctypes.byref(_t),
                        ctypes.byref(_p),
                        ctypes.byref(_v),
                        _x,
                        ctypes.byref(_cs),
                        ctypes.byref(_ts),
                        ctypes.byref(_Ds),
                        ctypes.byref(_ps),
                        ctypes.byref(_ws),
                        ctypes.byref(_ierr),
                        ctypes.byref(_herr),
                        ctypes.c_long(255))
    return _prop(t = t, p = p, v = v, x = x, cs = _cs.value, ts = _ts.value,
            Ds = _Ds.value, ps = _ps.value, ws = _ws.value, ierr = _ierr.value,
            herr = _herr.value, defname = defname)


##def satdata(x, nrun=2):
##    '''Calculates the phase boundary of a mixture at a given composition, and
##    the critical point, cricondentherm, and cricondenbar. The use of array
##    xarr2 makes it possible that this can be called multiple times to get
##    better splines.
##
##    inputs:
##        x--composition [array of mol frac]
##        nrun--no off runs to increase accuracy'''
##    defname = sys._getframe(0).f_code.co_name, locals()
##
##    _inputerrorcheck(locals())
##    for each in range(len(x)): _x[each] = x[each]
##    if platform.system() == 'Linux':
##        for each in range(nrun):
##            _rp.satdata_(_x)
##    elif platform.system() == 'Windows':
##        for each in range(nrun):
##            _rp.SATDATAdll(_x)
##    #enable getsatdata
##    #enable setsatdata
##    #return from getsatdata
##    #only works in the beta version



#compilation


if __name__ == u'__main__':
    _test()

##    setup('def', 'water', 'ammonia')
##    print(dir(_rp))
##    satdata([0.4, 0.6])
