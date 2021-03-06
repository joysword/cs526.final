import omegaToolkit
import euclid
import math
import pickle
from datetime import datetime
from caveutil import *
from csv import reader

from CoordinateCalculator import CoordinateCalculator

##############################################################################################################
# GLOBAL VARIABLES
c_SMALLMULTI_NUMBER = 40

g_changeSizeWallText = []

g_changeSize = []
g_changeSizeCenterText = []

g_changeDistCircles = []
g_changeDistCenterPlanets = []
g_changeDistCenterHab = []

g_orbit = []
g_rot = []

g_cen_changeSize = []
g_cen_changeSizeCenterText = []
g_cen_changeDistCircles = []
g_cen_changeDistCenterPlanets = []
g_cen_changeDistCenterHab = []
g_cen_orbit = []
g_cen_rot = []

g_reorder = 0 # status of reorder 0: not; 1: select; 2: moving

g_moveToCenter = 0 # status of bring to center 0: not; 1: in

g_invisOnes = []

g_curOrder = [i for i in xrange(c_SMALLMULTI_NUMBER)]

li_allSys = [] # classes, aaalllllll the systems
dic_boxToSys = {} # dictionary of small multiple boxes
dic_countToSys = {} # dictionary of systems
li_boxOnWall = [] # scenenodes (outlineBox)

li_dotOnWall = []
li_dotOnWall2 = []

li_textUniv = []

text_univ_highlight = None

g_cur_highlight_box = None

g_cur_highlight_box_blue = None

g_cur_highlight_i = -100

g_cur_highlight_i_blue = -100

# whether we are showing the info of a system
g_showInfo = False

# whether we are showing a recent discovery
g_showNews = False

g_curCenSys = None

g_isLoadingFromSavedConfig = False

bgmDeltaT = 0

wallLimit = 247000000 # by default, everything closer than this number can be shown

## global scale factors
g_scale_size = 1.0
g_scale_dist = 1.0
g_scale_time = 1.0

## sets of systems
set_nearest = []
set_most_planets = []
set_farthest = []
set_g_type = []
set_save = [None]*c_SMALLMULTI_NUMBER

## constants

caveRadius = 3.25
c_col_on_wall = 6
c_row_on_wall = 8

WALLLIMIT = 247000000 # wallLimit will change, WALLLIMIT won't

c_scaleWall_size = 0.1
c_scaleWall_dist = 0.0008

c_scaleCenter_size = 0.006
c_scaleCenter_dist = 0.000005
c_scaleCenter_overall = 0.00025

c_scale_center_star = 0.08

c_scaleUniv_size = 0.000002

c_smallLabel_y_cave = 0.09

c_delta_scale = 0.2 # interval between each scale

R_jupiter = 69911 # in KM
R_sun = 695500 # in KM
M_earth = 5.97219e24 # in KG
R_earth = 6371 # in KM

dic_color = {'O':'#99ccf2', 'B':'#b2bfe6', 'A':'#e6e6fc', 'F':'#e6cc8c', 'G':'#ccb359', 'K':'#cc8059', 'M':'#cc1a0d'}

## font size
g_ftszdesk = 0.03
g_ftszcave = 0.03
g_ftszcave_center = 120

## for navigation
isButton7down = False
wandOldPos = Vector3()
wandOldOri = Quaternion()

## unit conversion functions
def M_from_AU(n): # exact
	return n * 149597870700.0
def AU_from_M(n): # exact
	return n / 149597870700.0

def M_from_LY(n): # exact
	return n * 9460730472580800.0
def LY_from_M(n): # exact
	return n / 9460730472580800.0

def AU_from_PC(n): # exact
	return n * 648000.0 / math.pi * n
def PC_from_AU(n): # exact
	return n * math.pi / 648000.0

def M_from_PC(n):
	return M_from_AU(AU_from_PC(n))
def PC_from_M(n):
	return PC_from_AU(AU_from_M(n))

def AU_from_LY(n):
	return AU_from_M(M_from_LY(n))
def LY_from_AU(n):
	return LY_from_M(M_from_AU(n))

def LY_from_PC(n):
	return LY_from_M(M_from_PC(n))
def PC_from_LY(n):
	return PC_from_M(M_from_LY(n))

def KM_from_AU(n): # exact
	return n * 149597870.7

def KM_from_Rj(n):
	return n * R_jupiter

def KG_from_Me(n):
	return n * M_earth

## column names in data file
g_c = {'sys':0, 'name':1, 'star':2, 'size':3, 'distance':4, 'orbit':4, 'texture':5, 'ra':6, 'dec':7, 'app_mag':8, 'class':9, 'type':10, 'num':11, 'day':12, 'year':13, 'inc':14, 'detection':15, 'mass':16, 'binary':16, 'info_s':17, 'info_p':18}

## bolometric correction constant for calculating habitable zone
g_BC = {'B':-2.0,'A':-0.3,'F':-0.15,'G':-0.4,'K':-0.8,'M':-2.0}

def CAVE():
	return caveutil.isCAVE();

##############################################################################################################
# CLASSES
class planet:
	def __getSizeFromMass(self, mass):
			#print 'mass:',mass
			if mass<5e25:
				return 0.5501*(mass**0.2858)*0.001 # to KM
			elif mass<1e27:
				return 7e-8*(mass**0.5609)*0.001 # to KM
			else:
				return 4e8*(mass**-0.0241)*0.001 # to KM

	def __init__(self,size,texture,orbit,name,day,year,inc,detection,mass):
		if cmp(size,'')==0:
			if cmp(mass,'')==0:
				self._mass = 0
				self._size = 0
			else:
				self._mass = float(mass) * M_earth # to KM
				self._size = self.__getSizeFromMass(self._mass)
				#print 'size:',self._size
		else:
			self._size = float(size) * R_jupiter # to KM
			self._mass = 0
		self._texture = texture
		if cmp(orbit,'')==0:
			self._orbit = 0
		else:
			self._orbit = KM_from_AU(float(orbit)) # to KM
		self._name = name
		if cmp(day,'')==0:
			self._day = 0
		else:
			self._day = float(day)
		if cmp(year,'')==0:
			self._year = 0
		else:
			self._year = float(year)
		if cmp(inc,'')==0:
			self._inc = 0
		else:
			self._inc = float(inc)
		if cmp(detection,'')==0:
			self._detection = 'unknown'
		else:
			self._detection = detection

		# if it is earth-sized
		if self._size<1.25*R_earth and self._size>0:
			self._isEarthSized = True
		else:
			self._isEarthSized = False

class star:
	def __init__(self,t,mv,size,n,dis,c,ty,num,ra,dec,infos,infop):
		self._texture = t

		if cmp(mv,'')==0:
			self._mv = 0
		else:
			self._mv = float(mv)

		if cmp(size,'')==0:
			self._size = 0
		else:
			self._size = float(size) * R_sun

		self._name = n

		self._dis = int(dis)

		if cmp(c,'')==0:
			self._class = 'unknown'
		else:
			self._class = c

		if cmp(ty,'')==0:
			self._type = 'unknown'
		else:
			self._type = ty

		self._numChildren = int(num)

		if self._mv==0 or cmp(self._class,'unkown')==0:
			self._habNear = 0
			self._habFar = 0
		else:
			self._habNear, self._habFar = self.getHabZone(self._mv, self._dis, self._class) # in KM

		self._children = []

		self._ra = float(ra[0:2])*15 + float(ra[3:5])*0.25 + float(ra[6:])*0.004166
		self._dec = float(dec[1:3]) + float(dec[4:6])/60.0 + float(dec[7:])/3600.0
		if cmp(dec[0],'-')==0:
			self._dec *= -1.0

		if int(infos)==1:
			self._hasInfo_s = True
		else:
			self._hasInfo_s = False

		if int(infop)==1:
			self._hasInfo_p = True
		else:
			self._hasInfo_p = False

	def addPlanet(self,pla):
		self._children.append(pla)

	def getHabZone(self, mv, dis, classs): # apparent magnitude, distance to us in ly, spectral class
		if cmp(self._name,'Sun') == 0:
			ri = math.sqrt(1.0/1.1)
			ro = math.sqrt(1.0/0.53)
			return KM_from_AU(ri),KM_from_AU(ro)
		else:
			d = dis / 3.26156 # ly to parsec
			#print 'd:',d
			Mv = mv - 5 * math.log10( d/10.0 )
			if not classs in g_BC:
				return 0,0
			Mbol = Mv + g_BC[classs]
			Lstar = math.pow(10, ((Mbol - 4.72)/-2.5))
			ri = math.sqrt(Lstar/1.1)
			ro = math.sqrt(Lstar/0.53)
			return KM_from_AU(ri),KM_from_AU(ro)

class plaSys:
	def __init__(self,star,dis,name,binary,hasInfo_s,hasInfo_p):
		self._star = star
		self._dis = dis
		self._name = name
		if cmp(binary,'')!=0:
			self._binary = ' ('+binary+')'
		else:
			self._binary = ''
		self._hasInfo_s = hasInfo_s
		self._hasInfo_p = hasInfo_p

class Dot:
	def __init__(self):
		self.pos = Vector2(0,0)
		self.sys = None
		self.pla = None
		self.image = None

	def setPosition(self,_pos):
		self.pos = _pos

	def getPosition(self):
		return self.pos

	def setSys(self,_sys):
		self.sys = _sys

	def getSys(self):
		return self.sys

	def setPla(self, _pla):
		self.pla = _pla

	def getPla(self):
		return self.pla

	def setImage(self,_image):
		self.image = _image

	def getImage(self):
		return self.image


##############################################################################################################
# PLAY SOUND
sdEnv = getSoundEnvironment()
sdEnv.setAssetDirectory('syin_p2')

sd_warn = SoundInstance(sdEnv.loadSoundFromFile('warn','sound/warn.wav'))
sd_bgm = SoundInstance(sdEnv.loadSoundFromFile('backgroundmusic','sound/bgm.wav'))
sd_loading = SoundInstance(sdEnv.loadSoundFromFile('load','sound/loading.wav'))

sd_reset = SoundInstance(sdEnv.loadSoundFromFile('reset','sound/reset.wav'))

sd_reo_please = SoundInstance(sdEnv.loadSoundFromFile('reo_please','sound/reorder/please.wav'))
sd_reo_selected = SoundInstance(sdEnv.loadSoundFromFile('reo_selected','sound/reorder/selected.wav'))
sd_reo_done = SoundInstance(sdEnv.loadSoundFromFile('reo_done','sound/reorder/done.wav'))
sd_reo_quit = SoundInstance(sdEnv.loadSoundFromFile('reo_quit','sound/reorder/quit.wav'))
sd_reo_canceled = SoundInstance(sdEnv.loadSoundFromFile('reo_canceled','sound/reorder/canceled.wav'))

sd_mtc_please = SoundInstance(sdEnv.loadSoundFromFile('mtc_please','sound/movetocenter/please.wav'))
sd_mtc_moving = SoundInstance(sdEnv.loadSoundFromFile('mtc_moving','sound/movetocenter/moving.wav'))
sd_mtc_quit = SoundInstance(sdEnv.loadSoundFromFile('mtc_quit','sound/movetocenter/quit.wav'))

sd_sav_saved = SoundInstance(sdEnv.loadSoundFromFile('sav_saved','sound/saveconfig/saved.wav'))
#sd_sav_loading = SoundInstance(sdEnv.loadSoundFromFile('sav_loading','sound/saveconfig/loading.wav'))

def playSound(sd, pos, vol):
	sd.setPosition(pos)
	sd.setVolume(vol)
	sd.setWidth(20)
	#sd.play()

##############################################################################################################
# CREATE MENUS

mm = MenuManager.createAndInitialize()

menu_graph1 = mm.getMainMenu().addSubMenu('change graph 1')
menu_x = menu_graph1.addSubMenu('x axis')
menu_y = menu_graph1.addSubMenu('y axis')
menu_p = menu_graph1.addSubMenu('points')
btn_change_graph = menu_graph1.addButton('update','updateGraph()')

container_x = menu_x.getContainer()
btn_x_1 = Button.create(container_x)
btn_x_2 = Button.create(container_x)
btn_x_3 = Button.create(container_x)
btn_x_4 = Button.create(container_x)
btn_x_5 = Button.create(container_x)
# btn_x_6 = Button.create(container_x)
# btn_x_7 = Button.create(container_x)
# btn_x_8 = Button.create(container_x)
# btn_x_9 = Button.create(container_x)

btn_x_1.setText('Planet Mass')
btn_x_2.setText('Planet Radius')
btn_x_3.setText('Orbital Radius')
btn_x_4.setText('Orbital Period')
btn_x_5.setText('Distance to us')
# btn_x_6.setText('foo bar')
# btn_x_7.setText('foo bar')
# btn_x_8.setText('foo bar')
# btn_x_9.setText('foo bar')

btn_x_1.setCheckable(True)
btn_x_2.setCheckable(True)
btn_x_3.setCheckable(True)
btn_x_4.setCheckable(True)
btn_x_5.setCheckable(True)
# btn_x_6.setCheckable(True)
# btn_x_7.setCheckable(True)
# btn_x_8.setCheckable(True)
# btn_x_9.setCheckable(True)

btn_x_1.setRadio(True)
btn_x_2.setRadio(True)
btn_x_3.setRadio(True)
btn_x_4.setRadio(True)
btn_x_5.setRadio(True)
# btn_x_6.setRadio(True)
# btn_x_7.setRadio(True)
# btn_x_8.setRadio(True)
# btn_x_9.setRadio(True)

btn_x_1.setChecked(True)


container_y = menu_y.getContainer()
btn_y_1 = Button.create(container_y)
btn_y_2 = Button.create(container_y)
btn_y_3 = Button.create(container_y)
btn_y_4 = Button.create(container_y)
btn_y_5 = Button.create(container_y)
# btn_y_6 = Button.create(container_y)
# btn_y_7 = Button.create(container_y)
# btn_y_8 = Button.create(container_y)
# btn_y_9 = Button.create(container_y)

btn_y_1.setText('Planet Mass')
btn_y_2.setText('Planet Radius')
btn_y_3.setText('Orbital Radius')
btn_y_4.setText('Orbital Period')
btn_y_5.setText('Distance to us')
# btn_y_6.setText('foo bar')
# btn_y_7.setText('foo bar')
# btn_y_8.setText('foo bar')
# btn_y_9.setText('foo bar')

btn_y_1.setCheckable(True)
btn_y_2.setCheckable(True)
btn_y_3.setCheckable(True)
btn_y_4.setCheckable(True)
btn_y_5.setCheckable(True)
# btn_y_6.setCheckable(True)
# btn_y_7.setCheckable(True)
# btn_y_8.setCheckable(True)
# btn_y_9.setCheckable(True)

btn_y_1.setRadio(True)
btn_y_2.setRadio(True)
btn_y_3.setRadio(True)
btn_y_4.setRadio(True)
btn_y_5.setRadio(True)
# btn_y_6.setRadio(True)
# btn_y_7.setRadio(True)
# btn_y_8.setRadio(True)
# btn_y_9.setRadio(True)

btn_y_2.setChecked(True)


container_p = menu_p.getContainer()
btn_p_1 = Button.create(container_p)
btn_p_2 = Button.create(container_p)
btn_p_3 = Button.create(container_p)
btn_p_4 = Button.create(container_p)

btn_p_1.setText('detection method')
btn_p_2.setText('radius')
btn_p_3.setText('mass')
btn_p_4.setText('nothing')

btn_p_1.setCheckable(True)
btn_p_2.setCheckable(True)
btn_p_3.setCheckable(True)
btn_p_4.setCheckable(True)

btn_p_1.setRadio(True)
btn_p_2.setRadio(True)
btn_p_3.setRadio(True)
btn_p_4.setRadio(True)

btn_p_4.setChecked(True)


## MENU FOR GRAPH 2
menu_graph2 = mm.getMainMenu().addSubMenu('change graph 2')
menu_x2 = menu_graph2.addSubMenu('x axis')
menu_y2 = menu_graph2.addSubMenu('y axis')
menu_p2 = menu_graph2.addSubMenu('points')
btn_change_graph2 = menu_graph2.addButton('update','updateGraph2()')

container_x2 = menu_x2.getContainer()
btn_x_12 = Button.create(container_x2)
btn_x_22 = Button.create(container_x2)
btn_x_32 = Button.create(container_x2)
btn_x_42 = Button.create(container_x2)
btn_x_52 = Button.create(container_x2)

btn_x_12.setText('Planet Mass')
btn_x_22.setText('Planet Radius')
btn_x_32.setText('Orbital Radius')
btn_x_42.setText('Orbital Period')
btn_x_52.setText('Distance to us')

btn_x_12.setCheckable(True)
btn_x_22.setCheckable(True)
btn_x_32.setCheckable(True)
btn_x_42.setCheckable(True)
btn_x_52.setCheckable(True)

btn_x_12.setRadio(True)
btn_x_22.setRadio(True)
btn_x_32.setRadio(True)
btn_x_42.setRadio(True)
btn_x_52.setRadio(True)

btn_x_22.setChecked(True)

container_y2 = menu_y2.getContainer()
btn_y_12 = Button.create(container_y2)
btn_y_22 = Button.create(container_y2)
btn_y_32 = Button.create(container_y2)
btn_y_42 = Button.create(container_y2)
btn_y_52 = Button.create(container_y2)

btn_y_12.setText('Planet Mass')
btn_y_22.setText('Planet Radius')
btn_y_32.setText('Orbital Radius')
btn_y_42.setText('Orbital Period')
btn_y_52.setText('Distance to us')

btn_y_12.setCheckable(True)
btn_y_22.setCheckable(True)
btn_y_32.setCheckable(True)
btn_y_42.setCheckable(True)
btn_y_52.setCheckable(True)

btn_y_12.setRadio(True)
btn_y_22.setRadio(True)
btn_y_32.setRadio(True)
btn_y_42.setRadio(True)
btn_y_52.setRadio(True)

btn_y_12.setChecked(True)

container_p2 = menu_p2.getContainer()
btn_p_12 = Button.create(container_p2)
btn_p_22 = Button.create(container_p2)
btn_p_32 = Button.create(container_p2)
btn_p_42 = Button.create(container_p2)

btn_p_12.setText('detection method')
btn_p_22.setText('radius')
btn_p_32.setText('mass')
btn_p_42.setText('nothing')

btn_p_12.setCheckable(True)
btn_p_22.setCheckable(True)
btn_p_32.setCheckable(True)
btn_p_42.setCheckable(True)

btn_p_12.setRadio(True)
btn_p_22.setRadio(True)
btn_p_32.setRadio(True)
btn_p_42.setRadio(True)

btn_p_42.setChecked(True)

## menu to change scale factor
menu_scale = mm.getMainMenu().addSubMenu('change scale factor')
wgt_scale = menu_scale.addContainer()
container_scale = wgt_scale.getContainer()
container_scale.setLayout(ContainerLayout.LayoutHorizontal)
container_scale.setMargin(0)

lbl_scaleSize = Label.create(container_scale)
lbl_scaleSize.setText('size: ')

container_scaleSizeBtn = Container.create(ContainerLayout.LayoutVertical, container_scale)
container_scaleSizeBtn.setPadding(-4)

btn_scaleSizeUp = Button.create(container_scaleSizeBtn)
btn_scaleSizeUp.setText('+')
btn_scaleSizeUp.setUIEventCommand('changeScale("size", True)')

btn_scaleSizeDown = Button.create(container_scaleSizeBtn)
btn_scaleSizeDown.setText('-')
btn_scaleSizeDown.setUIEventCommand('changeScale("size", False)')

lbl_scaleDist = Label.create(container_scale)
lbl_scaleDist.setText('distance: ')

container_scaleDistBtn = Container.create(ContainerLayout.LayoutVertical, container_scale)
container_scaleDistBtn.setPadding(-4)

btn_scaleDistUp = Button.create(container_scaleDistBtn)
btn_scaleDistUp.setText('+')
btn_scaleDistUp.setUIEventCommand('changeScale("dist", True)')

btn_scaleDistDown = Button.create(container_scaleDistBtn)
btn_scaleDistDown.setText('-')
btn_scaleDistDown.setUIEventCommand('changeScale("dist", False)')

btn_scaleSizeUp.setHorizontalNextWidget(btn_scaleDistUp)
btn_scaleDistUp.setHorizontalPrevWidget(btn_scaleSizeUp)
btn_scaleSizeDown.setHorizontalNextWidget(btn_scaleDistDown)
btn_scaleDistDown.setHorizontalPrevWidget(btn_scaleSizeDown)

## menu to change time speed
menu_speed = mm.getMainMenu().addSubMenu('change time speed')
widget_speed = menu_speed.addContainer()
container_speed = widget_speed.getContainer()
container_speed.setLayout(ContainerLayout.LayoutHorizontal)
container_speed.setMargin(0)

lbl_speed = Label.create(container_speed)
lbl_speed.setText('time speed: ')

container_speedBtn = Container.create(ContainerLayout.LayoutVertical, container_speed)
container_speedBtn.setPadding(-4)

btn_speedUp = Button.create(container_speedBtn)
btn_speedUp.setText('+')
btn_speedUp.setUIEventCommand('changeScale("time", True)')

btn_speedDown = Button.create(container_speedBtn)
btn_speedDown.setText('-')
btn_speedDown.setUIEventCommand('changeScale("time", False)')

lbl_speed_value = Label.create(container_speed)
lbl_speed_value.setText(' '+str(g_scale_time))

## menu to change to four predefined sets of system
menu_preset = mm.getMainMenu().addSubMenu('predefined sets')

btn_nearest = menu_preset.addButton('systems of smallest distance','loadPreset("near")')
btn_farthest = menu_preset.addButton('systems of largest distance','loadPreset("far")')
btn_g_type = menu_preset.addButton('systems with G type stars','loadPreset("g")')
btn_most_planets = menu_preset.addButton('systems with most planets','loadPreset("most")')

## menu to filter small multiples
menu_filter = mm.getMainMenu().addSubMenu('filter small multiples')

menu_type = menu_filter.addSubMenu('type of star')
menu_dis = menu_filter.addSubMenu('distance to us')
menu_pla = menu_filter.addSubMenu('number of planets')

container_type = menu_type.getContainer() # TO DO : see if all these options have systems to show
btn_type_1 = Button.create(container_type)
btn_type_2 = Button.create(container_type)
btn_type_3 = Button.create(container_type)
btn_type_4 = Button.create(container_type)
btn_type_5 = Button.create(container_type)
btn_type_6 = Button.create(container_type)
btn_type_7 = Button.create(container_type)
btn_type_8 = Button.create(container_type)

btn_type_1.setText('O')
btn_type_2.setText('B')
btn_type_3.setText('A')
btn_type_4.setText('F')
btn_type_5.setText('G')
btn_type_6.setText('K')
btn_type_7.setText('M')
btn_type_8.setText('other')

btn_type_1.setCheckable(True)
btn_type_2.setCheckable(True)
btn_type_3.setCheckable(True)
btn_type_4.setCheckable(True)
btn_type_5.setCheckable(True)
btn_type_6.setCheckable(True)
btn_type_7.setCheckable(True)
btn_type_8.setCheckable(True)

btn_type_1.setChecked(True)
btn_type_2.setChecked(True)
btn_type_3.setChecked(True)
btn_type_4.setChecked(True)
btn_type_5.setChecked(True)
btn_type_6.setChecked(True)
btn_type_7.setChecked(True)
btn_type_8.setChecked(True)

container_dis = menu_dis.getContainer()
btn_dis_1 = Button.create(container_dis)
btn_dis_2 = Button.create(container_dis)
btn_dis_3 = Button.create(container_dis)
btn_dis_4 = Button.create(container_dis)

btn_dis_1.setText('0 - 100 ly')
btn_dis_2.setText('101 - 200 ly')
btn_dis_3.setText('200 - 1000 ly')
btn_dis_4.setText('>1000 ly')

btn_dis_1.setCheckable(True)
btn_dis_2.setCheckable(True)
btn_dis_3.setCheckable(True)
btn_dis_4.setCheckable(True)

btn_dis_1.setChecked(True)
btn_dis_2.setChecked(True)
btn_dis_3.setChecked(True)
btn_dis_4.setChecked(True)

container_pla = menu_pla.getContainer()
btn_pla_0 = Button.create(container_pla)
btn_pla_1 = Button.create(container_pla)
btn_pla_2 = Button.create(container_pla)
btn_pla_3 = Button.create(container_pla)
btn_pla_4 = Button.create(container_pla)
btn_pla_5 = Button.create(container_pla)
btn_pla_6 = Button.create(container_pla)
btn_pla_7 = Button.create(container_pla)

btn_pla_0.setText('1')
btn_pla_1.setText('2')
btn_pla_2.setText('3')
btn_pla_3.setText('4')
btn_pla_4.setText('5')
btn_pla_5.setText('6')
btn_pla_6.setText('7')
btn_pla_7.setText('8')

btn_pla_0.setCheckable(True)
btn_pla_1.setCheckable(True)
btn_pla_2.setCheckable(True)
btn_pla_3.setCheckable(True)
btn_pla_4.setCheckable(True)
btn_pla_5.setCheckable(True)
btn_pla_6.setCheckable(True)
btn_pla_7.setCheckable(True)

btn_pla_0.setChecked(True)
btn_pla_1.setChecked(True)
btn_pla_2.setChecked(True)
btn_pla_3.setChecked(True)
btn_pla_4.setChecked(True)
btn_pla_5.setChecked(True)
btn_pla_6.setChecked(True)
btn_pla_7.setChecked(True)

btn_update = menu_filter.addButton('update','updateFilter()')

## menu to save and load configuration
menu_sl = mm.getMainMenu().addSubMenu('save/load configuration')

btn_save = menu_sl.addButton('save current configuration','saveConfig()')
menu_load = menu_sl.addSubMenu('load a configuration')

## button to show info image
btn_info = mm.getMainMenu().addButton('show info (beta)','showInfo()')

## button to move one of the small multiples to center
btn_moveToCenter = mm.getMainMenu().addButton('move to center','startMoveToCenter()')

## button to hide/show small multiples
btn_hideWall = mm.getMainMenu().addButton('hide small multiples','toggleWallVisible()')

## button to reorder the small multiples
btn_reorder = mm.getMainMenu().addButton('reorder small multiples','startReorder()')

## button to reset the scene
btn_reset = mm.getMainMenu().addButton('reset the scene','resetEverything()')

## menu to read recent scientific discoveries
menu_discovery = mm.getMainMenu().addSubMenu('recent discoveries')

btn_discovery_1 = menu_discovery.addButton('New Planets, 3 Are Habitable (Gliese 667 C)','showNews("1")')
btn_discovery_2 = menu_discovery.addButton('New Earth-Sized Exoplanet (Kepler-78b)','showNews("2")')
btn_discovery_3 = menu_discovery.addButton('Richest Planetary System (HD 10180)','showNews("3")')
btn_discovery_4 = menu_discovery.addButton('Most Earth-Like ExoPlanet Possibly Found (Kepler-69c)','showNews("4")')

##############################################################################################################
# INITIALIZE THE SCENE
scene = getSceneManager()
cam = getDefaultCamera()

#set the background to black - kinda spacy
scene.setBackgroundColor(Color(0, 0, 0, 1))

#set the far clipping plane back a bit
setNearFarZ(0.1, 1000000)

sn_root = SceneNode.create('root')
sn_centerSys = SceneNode.create('centerSystems')
sn_cen_sys = SceneNode.create('cen_sys') # another system in center
sn_smallMulti = SceneNode.create('smallMulti')
#sn_allSystems = SceneNode.create('allSystems')
sn_univTrans = SceneNode.create('univTrans')

sn_univParent = SceneNode.create('univParent')
sn_univTrans.addChild(sn_univParent)

sn_root.addChild(sn_centerSys)
sn_root.addChild(sn_smallMulti)
sn_root.addChild(sn_univTrans)
#sn_smallMulti.addChild(sn_allSystems)

# fix small multiples and 3d universe, no move
if CAVE():
	cam.addChild(sn_smallMulti)
	cam.addChild(sn_univTrans)

## Create a point light
light1 = Light.create()
light1.setLightType(LightType.Point)
light1.setColor(Color(1.0, 1.0, 1.0, 1.0))
#light1.setPosition(Vector3(0.0, 1.5, 1.0))
light1.setPosition(Vector3(0.0, 0.0, 0.0))
light1.setEnabled(True)

light2 = Light.create()
light2.setLightType(LightType.Point)
light2.setColor(Color(1.0, 1.0, 1.0, 1.0))
#light2.setPosition(Vector3(0.0, 1.5, 1.0))
light2.setPosition(Vector3(0.0, 0.0, 0.0))
light2.setEnabled(False)

## Load default sphere model
mi = ModelInfo()
mi.name = 'defaultSphere'
mi.path = 'sphere.obj'
scene.loadModel(mi)

## pointer for selecting
pointer = SphereShape.create(0.01,3)
pointer.setEffect('colored -e #ff6600')
pointer.setVisible(False)

ui = UiModule.createAndInitialize()
wf = ui.getWidgetFactory()
uiroot = ui.getUi()

legend_s = wf.createImage('legend_s', uiroot)
legend_p = wf.createImage('legend_p', uiroot)
legend_s.setLayer(WidgetLayer.Front)
legend_p.setLayer(WidgetLayer.Front)
legend_s.setVisible(False)
legend_p.setVisible(False)

#toggleStereo()

InitCamPos = cam.getPosition()
InitCamOri = cam.getOrientation()

playSound(sd_bgm, InitCamPos, 0.05)

if CAVE():
	cam.setControllerEnabled(False)
	cam.getController().setSpeed(0.15)

##############################################################################################################
# LOAD DATA FROM FILE

atLine = 0
f = open('data4.csv','rU')
lines = reader(f)
for p in lines:
	atLine+=1
	if (atLine == 1):
		continue
	#print 'line:',atLine
	#print p
	if int(p[g_c['star']])==1: # star
		# def __init__(self,t,mv,r,n,dis,c,ty,num):
		curStar = star(p[g_c['texture']], p[g_c['app_mag']], p[g_c['size']], p[g_c['name']], p[g_c['distance']], p[g_c['class']], p[g_c['type']], p[g_c['num']], p[g_c['ra']], p[g_c['dec']], p[g_c['info_s']], p[g_c['info_p']])

		curSys = plaSys(curStar,curStar._dis,p[g_c['sys']],p[g_c['binary']],curStar._hasInfo_s,curStar._hasInfo_p)
		li_allSys.append(curSys)

	else: # planet
		# def __init__(self,size,texture,orbit,name,day,year,inc,detection):
		curPla = planet(p[g_c['size']], p[g_c['texture']], p[g_c['orbit']], p[g_c['name']], p[g_c['day']], p[g_c['year']], p[g_c['inc']], p[g_c['detection']], p[g_c['mass']])
		curStar.addPlanet(curPla)

print 'number of systems generated:', len(li_allSys)

##############################################################################################################
# INITIALIZE PREDEFINED SETS

set_nearest = [i for i in xrange(len(li_allSys))]
#print 'nearest:'
#for i in xrange(50):
#	print set_nearest[i]
set_farthest = [(92-i) for i in xrange(len(li_allSys))]
set_farthest[0] = 0
#print 'farthest:'
#for i in xrange(50):
#	print set_farthest[i]
set_g_type = [0,1,5,6,10,12,14,18,19,20,21,23,24,28,29,32,33,34,35,36,37,39,41,43,44,45,47,48,50,53,54,56,57,58,59,60,61,62,63,64,65,67,68,69,70,72,73,75,79,80,82,87,88]
set_most_planets = [0,44,8,87,1,4,6,82,84,85,2,3,9,12,15,46,5,7,10,11,25,26,27,28,35,42,43,57,62,63,70,77,83,88,13,14,16,17,18,19,20,21,22,23,24,29,30,31,32,33,34,36,37,38,39,40,41,45,47,48,49,50,51,52,53,54,55,56,58,59,60,61,64,65,66,67,68,69,71,72,73,74,75,76,78,79,80,81,86,89,90,91]

##############################################################################################################
# INIT 3D UNIVERSE

def getPos(ra,dec,dis):
	x = dis*math.cos(dec)*math.cos(ra)
	y = dis*math.cos(dec)*math.sin(ra)
	z = dis*math.sin(dec)
	return Vector3(x,y,z)

def initUniv(preset):
	global sn_univParent
	global sn_univTrans
	global li_textUniv

	if sn_univParent.numChildren()>0:
		for i in xrange(sn_univParent.numChildren()):
			sn_univParent.removeChildByIndex(0)

	sn_univTrans.setPosition(1.2,1.8,-3)
	li_textUniv = []

	maxDis = 1
	for i in xrange(c_SMALLMULTI_NUMBER):
		if preset[i]!=-1:
			curSys = li_allSys[preset[i]]
			if curSys._dis>maxDis:
				maxDis = curSys._dis

	for i in xrange(c_SMALLMULTI_NUMBER):
		if preset[i]!=-1:
			curSys = li_allSys[preset[i]]
			star = SphereShape.create(math.sqrt(curSys._star._size * c_scaleUniv_size), 4)
			pos = getPos(curSys._star._ra, curSys._star._dec, curSys._star._dis)
			if maxDis>2000:
				pos = pos*1000/maxDis
			elif maxDis>1000:
				pos = pos*600/maxDis
			else:
				pos = pos*140/maxDis
			star.setPosition(pos)

			if curSys._star._class in dic_color.keys():
				star.setEffect('colored -e '+dic_color[curSys._star._class])
				pass
			else:
				star.setEffect('colored -e '+dic_color['G'])
				pass
			sn_univParent.addChild(star)

			t = Text3D.create('fonts/helvetica.ttf', 1, curSys._star._name)
			t.setFontSize(30)
			t.setFixedSize(True)
			t.setPosition(pos.x, pos.y+curSys._star._size * c_scaleUniv_size * 1.2, pos.z)
			t.setFacingCamera(cam)

			# sun text is in red
			if preset[i]==0:
				t.setColor(Color('red'))
			#caveutil.orientWithHead(cam,t)

			sn_univParent.addChild(t)
			li_textUniv.append(t)

	sn_univParent.setScale(0.005,0.005,0.005)

##############################################################################################################
# INITIALIZE SMALL MULTIPLES

def highlight(sys,star,p,t,size):
	if p._isEarthSized and p._orbit>star._habNear and p._orbit<star._habFar:
		t.setColor(Color('red'))
	elif cmp(sys._name, 'Gliese 876')==0 and cmp(p._name,'b')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'55 Cancri')==0 and cmp(p._name,'f')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'Upsilon Andromedae')==0 and cmp(p._name,'d')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'47 Ursae Majoris')==0 and cmp(p._name,'b')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)
	elif cmp(sys._name,'HD 37124')==0 and cmp(p._name,'c')==0:
		t.setColor(Color('red'))
		if CAVE():
			t.setFontSize(size)

def initSmallMulti(preset):

	global li_boxOnWall
	global dic_boxToSys
	global dic_countToSys

	global g_curOrder

	global g_isLoadingFromSavedConfig

	global li_dotOnWall

	global li_dotOnWall2

	li_boxOnWall = []
	dic_boxToSys = {}
	dic_countToSys = {}

	li_dotOnWall = [] # for graph
	li_dotOnWall2 = [] # for graph 2

	print 'start initializing small multiples'
	playSound(sd_loading, cam.getPosition(), 0.5)

	# restore the order if not loading from saved Config
	if g_isLoadingFromSavedConfig:
		print 'loading from saved config'
		g_isLoadingFromSavedConfig = False
	else:
		g_curOrder = [i for i in xrange(c_SMALLMULTI_NUMBER)]

	smallCount = 0

	for col in xrange(0, 8):

		# leave a 'hole' in the center of the cave to see the far planets through
		if col>=3 and col<=5:
			continue

		#print 'col:',col

		for row in xrange(0, 8):

			sn_smallTrans = SceneNode.create('smallTrans'+str(g_curOrder[smallCount]))

			hLoc = (8-col) + 1.5
			degreeConvert = 0.2*math.pi # 36 degrees per column
			sn_smallTrans.setPosition(Vector3(math.sin(hLoc*degreeConvert)*caveRadius, (7-row) * 0.29 + 0.41, math.cos(hLoc*degreeConvert)*caveRadius))
			sn_smallTrans.yaw(hLoc*degreeConvert)
			sn_smallMulti.addChild(sn_smallTrans)

			sn_boxParent = SceneNode.create('boxParent'+str(g_curOrder[smallCount]))
			sn_smallTrans.addChild(sn_boxParent)

			bs_outlineBox = BoxShape.create(2.0, 0.25, 0.001)
			bs_outlineBox.setPosition(Vector3(-0.5, 0, 0.01))
			bs_outlineBox.setEffect('colored -e #01b2f144')
			bs_outlineBox.getMaterial().setTransparent(True)
			sn_boxParent.addChild(bs_outlineBox)

			li_boxOnWall.append(bs_outlineBox)
			set_save[g_curOrder[smallCount]] = preset[g_curOrder[smallCount]]

			dic_boxToSys[bs_outlineBox] = None
			dic_countToSys[g_curOrder[smallCount]] = None

			# if it is not an empty box
			if preset[g_curOrder[smallCount]]!=-1:
				curSys = li_allSys[preset[g_curOrder[smallCount]]]

				dic_boxToSys[bs_outlineBox] = curSys
				dic_countToSys[g_curOrder[smallCount]] = curSys

				sn_smallSys = SceneNode.create('smallSys'+str(g_curOrder[smallCount]))

				## get star
				bs_model = BoxShape.create(100, 25000, 2000)
				bs_model.setPosition(Vector3(0.0, 0.0, 48000))# - thisSystem[name][1] * XorbitScaleFactor * user2ScaleFactor))
				bs_model.setEffect('textured -v emissive -d '+curSys._star._texture)
				sn_smallSys.addChild(bs_model)

				## get habitable zone if it is in the range
				habOuter = curSys._star._habFar
				habInner = curSys._star._habNear

				sn_habiParent = SceneNode.create('habiParent'+str(g_curOrder[smallCount]))

				bs_habi = BoxShape.create(1, 1, 1)

				if habInner < wallLimit:
					if habOuter > wallLimit:
						habOuter = wallLimit
					habCenter = (habOuter+habInner)/2.0
				else:
					habCenter = (habOuter+habInner)/2.0
					bs_habi.setVisible(False)

				bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
				bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
				bs_habi.setEffect('colored -e #00611055')
				bs_habi.getMaterial().setTransparent(True)

				sn_smallSys.addChild(sn_habiParent)
				sn_habiParent.addChild(bs_habi)
					#sn_smallSys.addChild(bs_habi) # child 1

				sn_smallTrans.addChild(sn_smallSys)

				## get planets
				sn_planetParent = SceneNode.create('planetParent'+str(g_curOrder[smallCount]))

				outCounter = 0
				for p in curSys._star._children:
					dot = Dot()
					dot.setSys(curSys)
					dot.setPla(p)
					li_dotOnWall.append(dot)

					dot2 = Dot()
					dot2.setSys(curSys)
					dot2.setPla(p)
					li_dotOnWall2.append(dot2)

					model = StaticObject.create('defaultSphere')
					model.setScale(Vector3(p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size, p._size * c_scaleWall_size * g_scale_size))
					model.setPosition(Vector3(0.0,0.0,48000 - p._orbit * c_scaleWall_dist * g_scale_dist))
					g_changeSize.append(model)
					model.setEffect('textured -v emissive -d '+p._texture)
					sn_planetParent.addChild(model)
					t = Text3D.create('fonts/helvetica.ttf', 1, p._name)
					#print '!!name:',p._name
					if CAVE():
						t.setFontSize(64)
					else:
						t.setFontSize(g_ftszdesk)
					t.setPosition(Vector3(0.0, p._size * c_scaleWall_size * g_scale_size, 48000 - p._orbit * c_scaleWall_dist * g_scale_dist))
					g_changeSizeWallText.append(t)
					t.yaw(0.5*math.pi) # back to face, face to back
					t.getMaterial().setTransparent(False)
					t.getMaterial().setDepthTestEnabled(False)
					t.setFixedSize(True)
					t.setColor(Color('white'))

					highlight(curSys,curSys._star,p,t,76)

					sn_planetParent.addChild(t)
					if p._orbit > wallLimit:
						outCounter+=1
						model.setVisible(False)
						t.setVisible(False)

				sn_smallSys.addChild(sn_planetParent)

				## get text
				if cmp(curSys._name,'Gliese 667')==0:
					t = Text3D.create('fonts/helvetica.ttf', 1, curSys._name+curSys._binary+' | STAR: '+curSys._star._name+' | TYPE: '+curSys._star._type+' | DISTANCE: '+str(curSys._star._dis)+' ly | by: '+curSys._star._children[0]._detection+ '| (RECENT DISCOVERY 1)')
				elif cmp(curSys._name,'Kepler-78')==0:
					t = Text3D.create('fonts/helvetica.ttf', 1, curSys._name+curSys._binary+' | STAR: '+curSys._star._name+' | TYPE: '+curSys._star._type+' | DISTANCE: '+str(curSys._star._dis)+' ly | by: '+curSys._star._children[0]._detection+ '| (RECENT DISCOVERY 2)')
				elif cmp(curSys._name,'HD 10180')==0:
					t = Text3D.create('fonts/helvetica.ttf', 1, curSys._name+curSys._binary+' | STAR: '+curSys._star._name+' | TYPE: '+curSys._star._type+' | DISTANCE: '+str(curSys._star._dis)+' ly | by: '+curSys._star._children[0]._detection+ '| (RECENT DISCOVERY 3)')
				elif cmp(curSys._name,'Kepler-69')==0:
					t = Text3D.create('fonts/helvetica.ttf', 1, curSys._name+curSys._binary+' | STAR: '+curSys._star._name+' | TYPE: '+curSys._star._type+' | DISTANCE: '+str(curSys._star._dis)+' ly | by: '+curSys._star._children[0]._detection+ '| (RECENT DISCOVERY 4)')
				else:
					t = Text3D.create('fonts/helvetica.ttf', 1, curSys._name+curSys._binary+' | STAR: '+curSys._star._name+' | TYPE: '+curSys._star._type+' | DISTANCE: '+str(curSys._star._dis)+' ly | by: '+curSys._star._children[0]._detection)
				if CAVE():
					t.setFontSize(g_ftszcave)
				else:
					t.setFontSize(g_ftszdesk)
				if CAVE():
					t.setPosition(Vector3(0.45, c_smallLabel_y_cave, -0.01))
				else:
					t.setPosition(Vector3(0.3, 0.08, -0.01))
				t.yaw(math.pi) # back to face, face to back
				t.getMaterial().setTransparent(False)
				t.getMaterial().setDepthTestEnabled(False)
				if cmp(curSys._name,'Gliese 667')==0 or cmp(curSys._name,'Kepler-78')==0 or cmp(curSys._name,'HD 10180')==0 or cmp(curSys._name,'Kepler-69')==0:
					t.setColor(Color('red'))
					t.setFontSize(g_ftszcave*1.2)
				elif cmp(curSys._binary,'')!=0:
					t.setColor(Color('orange'))
				else:
					t.setColor(Color('white'))
				sn_smallTrans.addChild(t)

				## get indicator if some planets are outside
				sn_indicatorParent = SceneNode.create('indicatorParent'+str(g_curOrder[smallCount]))

				if cmp(curSys._binary,'')==0:
					t_indi = Text3D.create('fonts/helvetica.ttf', 1, str(outCounter)+' more planet(s) -->>')
				else:
					t_indi = Text3D.create('fonts/helvetica.ttf', 1, str(outCounter)+' more bodies -->>')
				if CAVE():
					t_indi.setFontSize(g_ftszcave)
				else:
					t_indi.setFontSize(g_ftszdesk)
				if CAVE():
					t_indi.setPosition(Vector3(-1.15, -c_smallLabel_y_cave, -0.01))
				else:
					t_indi.setPosition(Vector3(-0.9, 0.08, -0.01))
				t_indi.yaw(math.pi) # back to face, face to back
				t_indi.getMaterial().setTransparent(False)
				t_indi.getMaterial().setDepthTestEnabled(False)
				t_indi.setColor(Color('white'))
				sn_smallTrans.addChild(sn_indicatorParent)
				sn_indicatorParent.addChild(t_indi)

				if outCounter==0:
					t_indi.setVisible(False)

				sn_smallSys.yaw(math.pi/2.0)
				sn_smallSys.setScale(0.00001, 0.00001, 0.00001) #scale for panels - flat to screen

			smallCount += 1

	initUniv(preset)

initSmallMulti(set_nearest)

##############################################################################################################
# INIT 3D SOLAR SYSTEM

def addOrbit(orbit, thick):
	global g_changeDistCircles

	circle = LineSet.create()

	segments = 128
	radius = 1
	thickness = thick   #0.01 for orbit

	a = 0.0
	while a <= 360:
		x = cos(radians(a)) * radius
		y = sin(radians(a)) * radius
		a += 360.0 / segments
		nx = cos(radians(a)) * radius
		ny = sin(radians(a)) * radius

		l = circle.addLine()
		l.setStart(Vector3(x, 0, y))
		l.setEnd(Vector3(nx, 0, ny))
		l.setThickness(thickness)

		circle.setPosition(Vector3(0, 2, -4))

		circle.setEffect('colored -e white')

		# Squish z to turn the torus into a disc-like shape.
		circle.setScale(Vector3(orbit, 1000.0, orbit))

	g_changeDistCircles.append(circle)

	return circle

def initCenter(verticalHeight):
	global g_rot
	global g_orbit
	global g_changeSize
	global g_changeSizeCenterText
	global g_changeDistCircles
	global g_changeDistCenterHab
	global g_changeDistCenterPlanets

	theSys = li_allSys[0]

	#global sn_centerSys

	sn_centerTrans = SceneNode.create('solarSystem')
	sn_centerSys.addChild(sn_centerTrans)

	## the star
	model = StaticObject.create('defaultSphere')
	#model = SphereShape.create(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, 4)
	model.setScale(Vector3(theSys._star._size*c_scaleCenter_size*g_scale_size*c_scale_center_star, theSys._star._size*c_scaleCenter_size*g_scale_size*c_scale_center_star, theSys._star._size*c_scaleCenter_size*g_scale_size*c_scale_center_star))
	model.setPosition(0,850,0)
	#g_changeSize.append(model)
	model.getMaterial().setProgram('textured')
	model.setEffect('textured -v emissive -d '+theSys._star._texture)

	# activePlanets[name] = model

	sunDot = StaticObject.create('defaultSphere')
	#sunDot.setPosition(Vector3(0.0, 0.0, 0.0))
	sunDot.setScale(Vector3(10, 10, 10))
	sn_centerTrans.addChild(sunDot)

	sunLine = LineSet.create()

	l = sunLine.addLine()
	l.setStart(Vector3(0, 0, 0))
	l.setEnd(Vector3(0, 850, 0))
	l.setThickness(1)
	sunLine.setEffect('colored -e white')
	sn_centerTrans.addChild(sunLine)

	sn_planetCenter = SceneNode.create('planetCenter'+theSys._star._name)

	## tilt
	sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._star._name)
	sn_planetCenter.addChild(sn_tiltCenter)
	sn_tiltCenter.addChild(model)

	## rotation
	sn_rotCenter = SceneNode.create('rotCenter'+theSys._star._name)
	sn_rotCenter.setPosition(Vector3(0,0,0))
	sn_rotCenter.addChild(sn_planetCenter)

	#activeRotCenters[name] = rotCenter
	sn_centerTrans.addChild(sn_rotCenter)

	# addOrbit(theSystem[name][1]*orbitScaleFactor*userScaleFactor, 0, 0.01)

	# deal with labelling everything
	v = Text3D.create('fonts/helvetica.ttf', 1, theSys._star._name)
	if CAVE():
		#v.setFontResolution(120)
		v.setFontSize(g_ftszcave_center)
		#v.setFontSize(g_ftszcave*10)
	else:
		#v.setFontResolution(10)
		v.setFontSize(g_ftszdesk*10)
	v.setPosition(Vector3(0, 400, 0))
	#v.setFontResolution(120)

	#v.setFontSize(160)
	v.getMaterial().setDoubleFace(1)
	v.setFixedSize(True)
	v.setColor(Color('white'))
	sn_planetCenter.addChild(v)

	## the planets
	for p in theSys._star._children:
		model = StaticObject.create('defaultSphere')
		#model = SphereShape.create(p._size * c_scaleCenter_size * g_scale_size, 4)
		model.setPosition(Vector3(0.0, 0.0, -p._orbit*g_scale_dist*c_scaleCenter_dist))
		model.setScale(Vector3(p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size))
		g_changeSize.append(model)
		g_changeDistCenterPlanets.append(model)
		model.getMaterial().setProgram('textured')
		model.setEffect('textured -d '+p._texture)

		#activePlanets[name] = model

		#set up for planet name on top of planet
		sn_planetCenter = SceneNode.create('planetCenter'+theSys._name+p._name)

		# deal with the axial tilt of the sun & planets
		sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._name+p._name)
		sn_planetCenter.addChild(sn_tiltCenter)
		sn_tiltCenter.addChild(model)
		sn_tiltCenter.roll(p._inc/180.0*math.pi)

		# deal with rotating the planets around the sun
		sn_rotCenter = SceneNode.create('rotCenter'+theSys._name+p._name)
		#sn_rotCenter.setPosition(Vector3(0,0,0))
		sn_rotCenter.addChild(sn_planetCenter)

		g_orbit.append((sn_rotCenter,p._year))
		g_rot.append((model,p._day))

		#print "!!:",g_orbit[len(g_orbit)-1]

		#activeRotCenters[name] = rotCenter
		sn_centerTrans.addChild(sn_rotCenter)

		circle = addOrbit(p._orbit*g_scale_dist*c_scaleCenter_dist, 0.01)
		sn_centerTrans.addChild(circle)

		# deal with labelling everything
		v = Text3D.create('fonts/helvetica.ttf', 1, p._name)
		if CAVE():
			#v.setFontResolution(120)
			v.setFontSize(g_ftszcave_center)
			#v.setFontSize(g_ftszcave*10)
		else:
			#v.setFontResolution(10)
			v.setFontSize(g_ftszdesk*10)
		v.setPosition(Vector3(0, p._size*c_scaleCenter_size*g_scale_size, -p._orbit*c_scaleCenter_dist*g_scale_dist))
		g_changeSizeCenterText.append(v)
		g_changeDistCenterPlanets.append(v)
		#v.setFontResolution(120)

		v.getMaterial().setDoubleFace(1)
		v.setFixedSize(True)
		v.setColor(Color('white'))
		sn_planetCenter.addChild(v)

	## deal with the habitable zone

	cs_inner = CylinderShape.create(1, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_inner.setEffect('colored -e #000000')
	#cs_inner.getMaterial().setTransparent(True)
	cs_inner.getMaterial().setTransparent(False)
	cs_inner.pitch(-math.pi*0.5)
	cs_inner.setScale(Vector3(1, 1, 1.0))

	cs_outer = CylinderShape.create(1, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_outer.setEffect('colored -e #00ff0055')
	cs_outer.getMaterial().setTransparent(True)
	cs_outer.pitch(-math.pi*0.5)
	cs_outer.setScale(Vector3(1, 1, 0.08))

	sn_habZone = SceneNode.create('habZone'+str(theSys._name))
	sn_habZone.addChild(cs_outer)
	sn_habZone.addChild(cs_inner)

	sn_centerTrans.addChild(sn_habZone)

	#g_changeDistCenterHab.append(sn_habZone)
	g_changeDistCenterHab.append(cs_outer)
	g_changeDistCenterHab.append(cs_inner)

	sn_centerTrans.addChild(light1)

	## add everything to the sn_centerTrans node for scaling and default positioning
	sn_centerTrans.setScale(Vector3(c_scaleCenter_overall, c_scaleCenter_overall, c_scaleCenter_overall))
	sn_centerTrans.setPosition(Vector3(0, verticalHeight, -1.5))

	## end here

initCenter(0.8)

##############################################################################################################
# MAJOR FUNCTIONS

## change the scale factor, if failed return False
def changeScale(name, add):
	global g_scale_size
	global g_scale_dist
	global g_scale_time

	global sn_smallMulti
	global wallLimit

	## dist
	if cmp(name,'dist')==0:
		#print 'enter dist'
		if add: # +
			print 'enter +'
			old = g_scale_dist
			if old<0.05:
				g_scale_dist=0.05
			elif old<0.1:
				g_scale_dist=0.1
			elif old<0.2:
				g_scale_dist=0.2
			else:
				g_scale_dist+=c_delta_scale
			print 'g_scale_dist:',g_scale_dist

			################ CENTER ######
			print 'here1'
			for sn in g_changeDistCircles:
				s = sn.getScale()
				#print 'former:',s
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
				#print 'now:   ',sn.getScale()
			print 'here2'
			for hab in g_changeDistCenterHab:
				s = hab.getScale()
				#print 'former:',s
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
				#print 'now:   ',hab.getScale()
			print 'here3'
			for m in g_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*(g_scale_dist)/(old))
			print 'here4'
			for sn in g_cen_changeDistCircles:
				s = sn.getScale()
				#print 'former:',s
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
				#print 'now:   ',sn.getScale()
			print 'here5'
			for hab in g_cen_changeDistCenterHab:
				s = hab.getScale()
				#print 'former:',s
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
				#print 'now:   ',hab.getScale()
			print 'here6'
			for m in g_cen_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*(g_scale_dist)/(old))

			################# WALL ########
			print 'here7'
			wallLimit*=(old)/(g_scale_dist) # wallLimit will be smaller

			# not work, too slow
			#removeAllChildren(sn_smallMulti)
			#initSmallMulti()
			print 'here8'

			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(i))

				# if not an empty box
				if sn_smallTrans.numChildren()>1:
					sn_smallSys = sn_smallTrans.getChildByName('smallSys'+str(i))
					bs_habi = sn_smallSys.getChildByName('habiParent'+str(i)).getChildByIndex(0)
					t = sn_smallTrans.getChildByName('indicatorParent'+str(i)).getChildByIndex(0)
					sn_planetParent = sn_smallSys.getChildByName('planetParent'+str(i))

					#bs_outlineBox = sn_smallTrans.getChildByName('boxParent'+str(i)).getChildByIndex(0)

					curSys = dic_countToSys[i]
					print 'i:',i
					print 'curSys:',curSys._name
					habInner = curSys._star._habNear
					habOuter = curSys._star._habFar

					if habInner < wallLimit:
						if habOuter > wallLimit:
							habOuter = wallLimit
						habCenter = (habOuter+habInner)/2.0
						#bs_habi.setScale(s.x,s.y,s.z*g_scale_dist/(old))
						bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
						bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
						bs_habi.setVisible(True)
					else:
						bs_habi.setVisible(False)

					outCounter = 0
					for j in xrange(sn_planetParent.numChildren()):
						m = sn_planetParent.getChildByIndex(j)

						p = m.getPosition()
						orbit = (48000 - p.z)/c_scaleWall_dist/(old)
						m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(old))
						if orbit > wallLimit:
							outCounter+=1
							m.setVisible(False)
						else:
							m.setVisible(True)

					if outCounter>0:
						outCounter /= 2 # a model and a text should be considered as one
						if cmp(curSys._binary,'')==0:
							t.setText(str(outCounter)+' more planet(s) -->>')
						else:
							t.setText(str(outCounter)+' more bodies -->>')
						t.setVisible(True)
					else:
						t.setVisible(False)

			print 'done'
			return True
		else: # -
			old = g_scale_dist
			print 'old:',old

			if old<0.01:
				print 'old<0.01'
				return False
			elif old<=0.051:
				print 'old<=0.051'
				g_scale_dist=0.01
			elif old<=0.11:
				print 'old<=0.11'
				g_scale_dist=0.05
			elif old<=0.21:
				print 'old<=0.21'
				g_scale_dist=0.1
			else:
				print 'normal'
				g_scale_dist-=c_delta_scale
			print 'g_scale_dist:',g_scale_dist

			################ CENTER ######
			for sn in g_changeDistCircles:
				s = sn.getScale()
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
			for hab in g_changeDistCenterHab:
				s = hab.getScale()
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
			for m in g_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*(g_scale_dist)/(old))

			for sn in g_cen_changeDistCircles:
				s = sn.getScale()
				#print 'former:',s
				sn.setScale(s.x*(g_scale_dist)/(old), s.y, s.z*(g_scale_dist)/(old))
				#print 'now:   ',sn.getScale()
			for hab in g_cen_changeDistCenterHab:
				s = hab.getScale()
				#print 'former:',s
				hab.setScale(s.x*(g_scale_dist)/(old), s.y*(g_scale_dist)/(old), s.z)
				#print 'now:   ',hab.getScale()
			for m in g_cen_changeDistCenterPlanets:
				m.setPosition(m.getPosition()*(g_scale_dist)/(old))

			################# WALL ########
			wallLimit*=(old)/(g_scale_dist) # wallLimit will be smaller

			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(i))

				if sn_smallTrans.numChildren()>1:
					sn_smallSys = sn_smallTrans.getChildByName('smallSys'+str(i))
					bs_habi = sn_smallSys.getChildByName('habiParent'+str(i)).getChildByIndex(0)
					t = sn_smallTrans.getChildByName('indicatorParent'+str(i)).getChildByIndex(0)
					sn_planetParent = sn_smallSys.getChildByName('planetParent'+str(i))

					curSys = dic_countToSys[i]
					habInner = curSys._star._habNear
					habOuter = curSys._star._habFar

					if habInner < wallLimit:
						if habOuter > wallLimit:
							habOuter = wallLimit
						habCenter = (habOuter+habInner)/2.0
						#bs_habi.setScale(s.x,s.y,s.z*g_scale_dist/(old))
						bs_habi.setScale(4, 25000, (1.0 * (habOuter - habInner)) * c_scaleWall_dist * g_scale_dist)
						bs_habi.setPosition(Vector3(0.0, 0.0, 48000 - habCenter * c_scaleWall_dist * g_scale_dist))
						bs_habi.setVisible(True)
					else:
						bs_habi.setVisible(False)

					outCounter = 0
					for j in xrange(sn_planetParent.numChildren()):
						m = sn_planetParent.getChildByIndex(j)

						p = m.getPosition()
						orbit = (48000 - p.z)/c_scaleWall_dist/(old)
						m.setPosition(p.x, p.y, 48000-(48000-p.z)*(g_scale_dist)/(old))
						if orbit > wallLimit:
							outCounter+=1
							m.setVisible(False)
						else:
							m.setVisible(True)

					if outCounter>0:
						outCounter /= 2 # a model and a text should be considered as one
						if cmp(curSys._binary,'')==0:
							t.setText(str(outCounter)+' more planet(s) -->>')
						else:
							t.setText(str(outCounter)+' more bodies -->>')
						t.setVisible(True)
					else:
						t.setVisible(False)

			print 'done'
			return True

	## size
	elif cmp(name,'size')==0:
		#print 'enter size'
		if add: # +
			#print 'enter +'
			g_scale_size+=c_delta_scale
			#print 'new size:', g_scale_size
			if g_scale_size>30:
				#print '> 5, restore value and return'
				g_scale_size-=c_delta_scale
				return False
			else: # rescale
				#print 'not > 5, applying change'
				#print len(g_changeSize)

				################ BOTH ########
				for m in g_changeSize:
					#print 'model'
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size-c_delta_scale))
					#print 'size_changed +'
				################ CENTER ######
				for t in g_changeSizeCenterText:
					p = t.getPosition()
					#print 'old:',t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size-c_delta_scale), p.z)
					#print 'new:',t.getPosition()
				for m in g_cen_changeSize:
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size-c_delta_scale))
				for t in g_cen_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size-c_delta_scale), p.z)
				################ WALL ########
				for t in g_changeSizeWallText:
					#print '++'
					p = t.getPosition()
					#print 'old:',t.getPosition()
					t.setPosition(Vector3(p.x, p.y*(g_scale_size)/(g_scale_size-c_delta_scale), p.z))
					#print 'new:',t.getPosition()
				return True
		else: # -
			#print 'enter -'
			g_scale_size-=c_delta_scale
			if g_scale_size<c_delta_scale:
				g_scale_size+=c_delta_scale
				return False
			else: # rescale
				################ BOTH ########
				for m in g_changeSize:
					#print 'model'
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size+c_delta_scale))
					#print 'size_changed +'
				################ CENTER ######
				for t in g_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+c_delta_scale), p.z)
				for m in g_cen_changeSize:
					m.setScale(m.getScale()*(g_scale_size)/(g_scale_size+c_delta_scale))
				for t in g_cen_changeSizeCenterText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+c_delta_scale), p.z)
				################ WALL ########
				for t in g_changeSizeWallText:
					p = t.getPosition()
					t.setPosition(p.x, p.y*(g_scale_size)/(g_scale_size+c_delta_scale), p.z)
				return True

	## time
	elif cmp(name,'time')==0:
		if add: # +
			g_scale_time*=2
			if g_scale_time>1024:
				g_scale_time*=0.5
				return False
		else: # -
			g_scale_time*=0.5
			if g_scale_time<0.0625:
				g_scale_time*=2
				return False

		lbl_speed_value.setText(' '+str(g_scale_time))

def addCenter(verticalHeight, theSys):
	global g_cen_rot
	global g_cen_orbit
	global g_cen_changeSize
	global g_cen_changeSizeCenterText
	global g_cen_changeDistCircles
	global g_cen_changeDistCenterHab
	global g_cen_changeDistCenterPlanets

	print ('start adding new center')

	sn_centerSys.addChild(sn_cen_sys)

	removeAllChildren(sn_cen_sys)
	sn_centerTrans = SceneNode.create('centerTrans'+theSys._name)
	sn_cen_sys.addChild(sn_centerTrans)

	g_cen_orbit = []
	g_cen_rot = []
	g_cen_changeSize = []
	g_cen_changeSizeCenterText = []
	g_cen_changeDistCircles = []
	g_cen_changeDistCenterHab = []
	g_cen_changeDistCenterPlanets = []

	## the star
	model = StaticObject.create('defaultSphere')
	#model = SphereShape.create(theSys._star._size*c_scaleCenter_size*g_scale_size*0.02, 4)
	model.setScale(Vector3(theSys._star._size*c_scaleCenter_size*g_scale_size*c_scale_center_star, theSys._star._size*c_scaleCenter_size*g_scale_size*c_scale_center_star, theSys._star._size*c_scaleCenter_size*g_scale_size*c_scale_center_star))
	model.setPosition(0,1000,0)
	#g_cen_changeSize.append(model)
	model.getMaterial().setProgram('textured')
	model.setEffect('textured -v emissive -d '+theSys._star._texture)

	# activePlanets[name] = model

	sunDot = StaticObject.create('defaultSphere')
	#sunDot.setPosition(Vector3(0.0, 0.0, 0.0))
	sunDot.setScale(Vector3(10, 10, 10))
	sn_centerTrans.addChild(sunDot)

	sunLine = LineSet.create()

	l = sunLine.addLine()
	l.setStart(Vector3(0, 0, 0))
	l.setEnd(Vector3(0, 1000, 0))
	l.setThickness(1)
	sunLine.setEffect('colored -e white')
	sn_centerTrans.addChild(sunLine)

	sn_planetCenter = SceneNode.create('planetCenter'+theSys._star._name)

	## tilt
	sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._star._name)
	sn_planetCenter.addChild(sn_tiltCenter)
	sn_tiltCenter.addChild(model)

	## rotation
	sn_rotCenter = SceneNode.create('rotCenter'+theSys._star._name)
	sn_rotCenter.setPosition(Vector3(0,0,0))
	sn_rotCenter.addChild(sn_planetCenter)

	#activeRotCenters[name] = rotCenter
	sn_centerTrans.addChild(sn_rotCenter)

	# addOrbit(theSystem[name][1]*orbitScaleFactor*userScaleFactor, 0, 0.01)

	# deal with labelling everything
	v = Text3D.create('fonts/helvetica.ttf', 1, theSys._star._name)
	if CAVE():
		#v.setFontResolution(120)
		v.setFontSize(g_ftszcave_center)
		#v.setFontSize(g_ftszcave*10)
	else:
		#v.setFontResolution(10)
		v.setFontSize(g_ftszdesk*10)
	v.setPosition(Vector3(0, 500, 0))
	#v.setFontResolution(120)

	#v.setFontSize(160)
	v.getMaterial().setDoubleFace(1)
	v.setFixedSize(True)
	v.setColor(Color('white'))
	sn_planetCenter.addChild(v)

	## the planets
	for p in theSys._star._children:
		model = StaticObject.create('defaultSphere')
		#model = SphereShape.create(p._size * c_scaleCenter_size * g_scale_size, 4)
		model.setScale(Vector3(p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size, p._size * c_scaleCenter_size * g_scale_size))
		model.setPosition(Vector3(0.0, 0.0, -p._orbit*g_scale_dist*c_scaleCenter_dist))
		g_cen_changeSize.append(model)
		g_cen_changeDistCenterPlanets.append(model)
		model.getMaterial().setProgram('textured')
		model.setEffect('textured -d '+p._texture)

		#activePlanets[name] = model

		#set up for planet name on top of planet
		sn_planetCenter = SceneNode.create('planetCenter'+theSys._name+p._name)

		# deal with the axial tilt of the sun & planets
		sn_tiltCenter = SceneNode.create('tiltCenter'+theSys._name+p._name)
		sn_planetCenter.addChild(sn_tiltCenter)
		sn_tiltCenter.addChild(model)
		sn_tiltCenter.roll(p._inc/180.0*math.pi)

		# deal with rotating the planets around the sun
		sn_rotCenter = SceneNode.create('rotCenter'+theSys._name+p._name)
		#sn_rotCenter.setPosition(Vector3(0,0,0))
		sn_rotCenter.addChild(sn_planetCenter)

		g_cen_orbit.append((sn_rotCenter,p._year))
		g_cen_rot.append((model,p._day))

		#print "!!:",g_orbit[len(g_orbit)-1]

		#activeRotCenters[name] = rotCenter
		sn_centerTrans.addChild(sn_rotCenter)

		circle = addOrbit(p._orbit*g_scale_dist*c_scaleCenter_dist, 0.01)
		sn_centerTrans.addChild(circle)

		# deal with labelling everything
		v = Text3D.create('fonts/helvetica.ttf', 1, p._name)
		if CAVE():
			#v.setFontResolution(120)
			v.setFontSize(g_ftszcave_center)
			#v.setFontSize(g_ftszcave)
		else:
			#v.setFontResolution(10)
			v.setFontSize(g_ftszdesk*10)
		v.setPosition(Vector3(0, p._size*c_scaleCenter_size*g_scale_size, -p._orbit*c_scaleCenter_dist*g_scale_dist))
		g_cen_changeSizeCenterText.append(v)
		g_cen_changeDistCenterPlanets.append(v)
		#v.setFontResolution(120)

		v.getMaterial().setDoubleFace(1)
		v.setFixedSize(True)
		v.setColor(Color('white'))
		sn_planetCenter.addChild(v)

		# highlight habitable candidates
		highlight(theSys,theSys._star,p,v,g_ftszcave_center*1.2)

	## deal with the habitable zone

	cs_inner = CylinderShape.create(1, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, theSys._star._habNear*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_inner.setEffect('colored -e #ff000055')
	cs_inner.getMaterial().setTransparent(True)
	#cs_inner.getMaterial().setTransparent(False)
	cs_inner.pitch(-math.pi*0.5)
	cs_inner.setScale(Vector3(1, 1, 1.0))

	cs_outer = CylinderShape.create(1, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, theSys._star._habFar*c_scaleCenter_dist*g_scale_dist, 10, 128)
	cs_outer.setEffect('colored -e #00ff0055')
	cs_outer.getMaterial().setTransparent(True)
	cs_outer.pitch(-math.pi*0.5)
	cs_outer.setScale(Vector3(1, 1, 0.1))

	sn_habZone = SceneNode.create('habZone'+str(theSys._name))
	sn_habZone.addChild(cs_outer)
	sn_habZone.addChild(cs_inner)

	sn_centerTrans.addChild(sn_habZone)

	#g_changeDistCenterHab.append(sn_habZone)
	g_cen_changeDistCenterHab.append(cs_outer)
	g_cen_changeDistCenterHab.append(cs_inner)

	sn_centerTrans.addChild(light2)
	light2.setEnabled(True)

	## add everything to the sn_centerTrans node for scaling and default positioning
	sn_centerTrans.setScale(Vector3(c_scaleCenter_overall, c_scaleCenter_overall, c_scaleCenter_overall))
	sn_centerTrans.setPosition(Vector3(0, verticalHeight, -1.5))

	print ('end adding new center')
	## end here

##############################################################################################################
# UTILITITIES FUNCTIONS

## recursively get all inivisible nodes below this node
def getInvisChildren(node):
	global g_invisOnes

	if node.numChildren()>0:
		for i in xrange(node.numChildren()):
			getInvisChildren(node.getChildByIndex(i))
	if node.isVisible()==False:
		g_invisOnes.append(node)

def toggleWallVisible():
	global sn_smallMulti
	global g_invisOnes

	global btn_hideWall

	if sn_smallMulti.isVisible(): # hide
		#print 'hiding everything on wall'
		getInvisChildren(sn_smallMulti)
		#print '# of nodes invisible:', len(g_invisOnes)
		sn_smallMulti.setChildrenVisible(False)
		sn_smallMulti.setVisible(False)
		#print 'hiding done'
		btn_hideWall.setText('show small multiples')
	else: # show
		#print 'recovering everything on wall'
		sn_smallMulti.setChildrenVisible(True)
		sn_smallMulti.setVisible(True)
		#print '# of nodes invisible:',len(g_invisOnes)
		for node in g_invisOnes:
			node.setVisible(False)
		#print 'they are invis now'
		g_invisOnes = []
		#print 'recovering done'
		btn_hideWall.setText('hide small multiples')

def removeAllChildren(sn):
	if sn.numChildren()>0:
		for i in xrange(sn.numChildren()):
			sn.removeChildByIndex(0)

def resetWall(set_):
	global sn_smallMulti

	#print ('start removing all children of sn_smallMulti')
	removeAllChildren(sn_smallMulti)
	#print ('done removing')

	#print 'start initSmallMulti'
	initSmallMulti(set_)
	#print 'done resetting'

	updateGraph()
	updateGraph2()

def resetCenter():
	global sn_centerSys

	removeAllChildren(sn_centerSys)

	initCenter(1)

def resetEverything():
	global g_scale_time
	global g_scale_size
	global g_scale_dist

	global g_orbit
	global g_rot
	global g_changeSize
	global g_changeSizeCenterText
	global g_changeDistCircles
	global g_changeDistCenterHab
	global g_changeDistCenterPlanets

	global g_changeSizeWallText

	global g_cen_orbit
	global g_cen_rot
	global g_cen_changeSize
	global g_cen_changeSizeCenterText
	global g_cen_changeDistCircles
	global g_cen_changeDistCenterHab
	global g_cen_changeDistCenterPlanets

	global wallLimit

	global g_reorder
	global g_moveToCenter
	global g_invisOnes

	global g_isLoadingFromSavedConfig

	g_isLoadingFromSavedConfig = False

	g_scale_size = 1
	g_scale_dist = 1
	g_scale_time = 1

	g_orbit = []
	g_rot = []
	g_changeSize = []
	g_changeSizeCenterText = []
	g_changeDistCircles = []
	g_changeDistCenterHab = []
	g_changeDistCenterPlanets = []

	g_changeSizeWallText = []

	g_cen_orbit = []
	g_cen_rot = []
	g_cen_changeSize = []
	g_cen_changeSizeCenterText = []
	g_cen_changeDistCircles = []
	g_cen_changeDistCenterHab = []
	g_cen_changeDistCenterPlanets = []

	wallLimit = WALLLIMIT

	g_reorder = 0
	g_moveToCenter = 0
	g_invisOnes = []

	cam.setPosition(InitCamPos)
	cam.setOrientation(InitCamOri)
	print 'initCamPos:',InitCamPos
	print 'initCamOri:',InitCamOri
	#cam.setPosition(Vector3(0,0,0))
	#cam.setOrientation(Quaternion(0,0,0,0))

	playSound(sd_reset, cam.getPosition(), 0.5)

	resetCenter()
	resetWall(set_nearest)

def startReorder():
	global g_reorder
	global pointer

	g_reorder = 1
	pointer.setVisible(True)
	mm.getMainMenu().hide()
	print 'now in reorder mode'
	playSound(sd_reo_please,cam.getPosition(),0.5)

def startMoveToCenter():
	global g_moveToCenter
	global pointer

	g_moveToCenter = 1
	pointer.setVisible(True)
	#print 'start moving to center'
	#print 'closing menu'
	mm.getMainMenu().hide()
	#print 'done'
	playSound(sd_mtc_please,cam.getPosition(),0.5)

def pointingCallback(node, distance):
	print 'yawing!'
	node.yaw(math.pi*0.2)

def loadPreset(s):
	global sn_smallMulti

	if cmp(s,'near')==0:
		resetWall(set_nearest)
	elif cmp(s,'far')==0:
		resetWall(set_farthest)
	elif cmp(s,'g')==0:
		resetWall(set_g_type)
	elif cmp(s,'most')==0:
		resetWall(set_most_planets)
	else:
		resetWall(set_nearest)

def saveConfig():
	global menu_load
	global set_save

	print 'start saving'
	li = [None]*c_SMALLMULTI_NUMBER
	t = datetime.now().strftime("%m-%d-%y %H:%M:%S")
	filename = t[0]+t[1]+t[3]+t[4]+t[6]+t[7]+t[9]+t[10]+t[12]+t[13]+t[15]+t[16]
	#print "time:",t
	#print 'file:',filename
	with open(filename, 'w') as f:
		pickle.dump(set_save,f)
		#print 'f:'
		#print f

	filename1 = str(-int(filename))
	#print 'file1:',filename1
	with open(filename1, 'w') as f:
		pickle.dump(g_curOrder,f)
	#print 'saved to '+t

	print 'saved g_curOrder'
	for i in xrange(len(g_curOrder)):
		print 'g_curOrder['+str(i)+']:',g_curOrder[i]

	menu_load.addButton(t,'loadConfig('+str(filename)+')')
	playSound(sd_sav_saved, cam.getPosition(), 0.5)

def loadConfig(filename):
	global set_save
	global sn_smallMulti

	global g_curOrder

	global g_isLoadingFromSavedConfig

	#print 'filename:', filename

	f = open(str(filename), 'r')

	#with open(filename, 'r') as f:
	set_save = pickle.load(f)

	f = open(str(-int(filename)), 'r')
	g_curOrder = pickle.load(f)

	print 'loading g_curOrder'
	for i in xrange(len(g_curOrder)):
		print 'g_curOrder['+str(i)+']:',g_curOrder[i]

	g_isLoadingFromSavedConfig = True

	resetWall(set_save)

def updateFilter():
	print 'start updating'
	res = []

	res.append(0)

	for i in xrange(1,len(li_allSys)):
		print 'testing system', i
		sys = li_allSys[i]

		## check type
		if cmp(sys._star._class,'O')==0:
			if btn_type_1.isChecked()==False:
				continue
		elif cmp(sys._star._class,'B')==0:
			if btn_type_2.isChecked()==False:
				continue
		elif cmp(sys._star._class,'A')==0:
			if btn_type_3.isChecked()==False:
				continue
		elif cmp(sys._star._class,'F')==0:
			if btn_type_4.isChecked()==False:
				continue
		elif cmp(sys._star._class,'G')==0:
			if btn_type_5.isChecked()==False:
				continue
		elif cmp(sys._star._class,'K')==0:
			if btn_type_6.isChecked()==False:
				continue
		elif cmp(sys._star._class,'M')==0:
			if btn_type_7.isChecked()==False:
				continue
		else:
			if btn_type_8.isChecked()==False:
				continue

		## check distance
		if sys._dis<=100:
			if btn_dis_1.isChecked()==False:
				continue
		elif sys._dis<=200:
			if btn_dis_2.isChecked()==False:
				continue
		elif sys._dis<=1000:
			if btn_dis_3.isChecked()==False:
				continue
		else:
			if btn_dis_4.isChecked()==False:
				continue

		## check number of planets
		if cmp(sys._binary,'')==0:
			if sys._star._numChildren==1:
				if btn_pla_0.isChecked()==False:
					continue
			elif sys._star._numChildren==2:
				if btn_pla_1.isChecked()==False:
					continue
			elif sys._star._numChildren==3:
				if btn_pla_2.isChecked()==False:
					continue
			elif sys._star._numChildren==4:
				if btn_pla_3.isChecked()==False:
					continue
			elif sys._star._numChildren==5:
				if btn_pla_4.isChecked()==False:
					continue
			elif sys._star._numChildren==6:
				if btn_pla_5.isChecked()==False:
					continue
			elif sys._star._numChildren==7:
				if btn_pla_6.isChecked()==False:
					continue
			else:
				if btn_pla_7.isChecked()==False:
					continue
		else:
			if sys._star._numChildren==2: # actual 1
				if btn_pla_0.isChecked()==False:
					continue
			elif sys._star._numChildren==3: # actual 2
				if btn_pla_1.isChecked()==False:
					continue
			elif sys._star._numChildren==4: # actual 3
				if btn_pla_2.isChecked()==False:
					continue
			elif sys._star._numChildren==5: # actual 4
				if btn_pla_3.isChecked()==False:
					continue
			elif sys._star._numChildren==6: # actual 5
				if btn_pla_4.isChecked()==False:
					continue
			elif sys._star._numChildren==7: # actual 6
				if btn_pla_5.isChecked()==False:
					continue
			elif sys._star._numChildren==8: # actual 7
				if btn_pla_6.isChecked()==False:
					continue
			else: # actual 8
				if btn_pla_7.isChecked()==False:
					continue

		#print 'need to add'
		res.append(i)
		#print 'added'

	#print 'done testing'
	if len(res)<c_SMALLMULTI_NUMBER:
		#print 'added less then 48 systems, filling up using None'
		for i in xrange(len(res),c_SMALLMULTI_NUMBER):
			res.append(-1)
		#print 'done filling up'
	#print 'start resetting the wall'
	resetWall(res)

def showInfo():
	global g_showInfo

	g_showInfo = True

	if g_curCenSys!=None:
		if g_curCenSys._hasInfo_s:
			legend_s.setData(loadImage('pic_s/'+g_curCenSys._name.replace(' ','_')+'.png'))
			legend_s.setSize(legend_s.getSize()*1.5)
		else:
			legend_s.setData(loadImage('pic_s/no_info.png'))
		if g_curCenSys._hasInfo_p:
			legend_p.setData(loadImage('pic_p/'+g_curCenSys._name.replace(' ','_')+'.png'))
			legend_p.setSize(legend_p.getSize()*1.5)
		else:
			legend_p.setData(loadImage('pic_p/no_info.png'))
		legend_s.setVisible(True)
		legend_p.setVisible(True)
		legend_s.setPosition(Vector2(15100,0))
		legend_p.setPosition(Vector2(15000 - legend_p.getSize()[0],800))

		print 'done loading image'

def showNews(s):
	global g_curCenSys
	global g_showNews

	g_showNews = True

	mm.getMainMenu().hide()

	if cmp(s,'1')==0:
		addCenter(1.3,li_allSys[4])
		g_curCenSys = li_allSys[4]

		legend_s.setData(loadImage('news/1.png'))
		legend_s.setSize(legend_s.getSize()*1.6)

		legend_s.setVisible(True)
		legend_s.setPosition(Vector2(15100,0))

	elif cmp(s,'2')==0:
		addCenter(1.3,li_allSys[32])
		g_curCenSys = li_allSys[32]

		legend_s.setData(loadImage('news/2.png'))
		legend_s.setSize(legend_s.getSize()*1.6)

		legend_s.setVisible(True)
		legend_s.setPosition(Vector2(15100,0))

	elif cmp(s,'3')==0:
		addCenter(1.3,li_allSys[45])
		g_curCenSys = li_allSys[45]

		legend_s.setData(loadImage('news/3.png'))
		legend_s.setSize(legend_s.getSize()*1.6)

		legend_s.setVisible(True)
		legend_s.setPosition(Vector2(15100,0))

	elif cmp(s,'4')==0:
		addCenter(1.3,li_allSys[89])
		g_curCenSys = li_allSys[89]

		legend_s.setData(loadImage('news/4.png'))
		legend_s.setSize(legend_s.getSize()*1.6)

		legend_s.setVisible(True)
		legend_s.setPosition(Vector2(15100,0))

##############################################################################################################
# FINAL STUFF

## create graph 1 container
container_g1 = Container.create(ContainerLayout.LayoutFree, ui.getUi())
container_g1.setStyleValue('fill', '#32ed8b55')
container_g1.setStyleValue('border', '4 #2acee9ff')
if CAVE():
	container_g1.setSize(Vector2(2732-4, 1536-4))
	container_g1.setPadding(0)
	container_g1.setPosition(Vector2(21856+2,0+2))
else:
	container_g1.setSize(Vector2(2728*0.2, 1532*0.2))
	container_g1.setPadding(2)
	container_g1.setPosition(Vector2(20, 20))
container_g1.setBlendMode(WidgetBlendMode.BlendNormal)
container_g1.setAlpha(1.0)
container_g1.setAutosize(False)

## create graph 1
graph1 = Container.create(ContainerLayout.LayoutFree, container_g1)
graph1.setPosition(Vector2(200,50))
if CAVE():
	graph1.setSize(Vector2(2478, 1332))
else:
	graph1.setSize(Vector2((2732-4-104)*0.2, (1536-4-104)*0.2))
# graph1.setClippingEnabled(True)
graph1.setAutosize(False)

## create x label
xlabel1 = Label.create(container_g1)
xlabel1.setAutosize(False)
xlabel1.setSize(Vector2(container_g1.getWidth(), 50 ))
xlabel1.setText('')
xlabel1.setColor(Color('white'))
xlabel1.setStyleValue('align', 'middle-center')
if CAVE():
	xlabel1.setFont('fonts/arial.ttf 76')
else:
	xlabel1.setFont('fonts/arial.ttf 14')
xlabel1.setCenter(Vector2(container_g1.getSize().x*0.5,container_g1.getSize().y-50))
xlabel1.setAutosize(False)

## create y label
ylabel1 = Label.create(container_g1)
ylabel1.setText('')
ylabel1.setColor(Color('white'))
# ylabel1.setSize(Vector2(container_g1.getWidth(), 50 ))
ylabel1.setSize(Vector2(50, container_g1.getHeight()))
ylabel1.setAutosize(False)
ylabel1.setStyleValue('align', 'middle-center')
if CAVE():
	ylabel1.setFont('fonts/arial.ttf 76')
else:
	ylabel1.setFont('fonts/arial.ttf 14')
ylabel1.setCenter(Vector2(40,container_g1.getHeight()*0.5))
#ylabel1.setStyleValue('align', 'middle-center')
ylabel1.setRotation(-90)

## create p label
plabel1 = Label.create(container_g1)
plabel1.setText('')
plabel1.setColor(Color('white'))
if CAVE():
	plabel1.setFont('fonts/arial.ttf 76')
else:
	plabel1.setFont('fonts/arial.ttf 14')
plabel1.setCenter(Vector2(container_g1.getSize().x*0.5,50))

## create x axis
xaxis = Container.create(ContainerLayout.LayoutFree, container_g1)
xaxis.setSize(Vector2(graph1.getWidth(), 2))
xaxis.setStyleValue('border', '4 #ffffffff')
xaxis.setAutosize(False)
xaxis.setPosition(Vector2(graph1.getPosition().x,graph1.getPosition().y+graph1.getHeight()))

## create y axis
yaxis = Container.create(ContainerLayout.LayoutFree, container_g1)
yaxis.setSize(Vector2(2, graph1.getHeight()))
yaxis.setStyleValue('border', '4 #ffffffff')
yaxis.setAutosize(False)
yaxis.setPosition(Vector2(graph1.getPosition().x,graph1.getPosition().y))

## create graph 2 container
container_g2 = Container.create(ContainerLayout.LayoutFree, ui.getUi())
container_g2.setStyleValue('fill', '#32ed8b55')
container_g2.setStyleValue('border', '4 #2acee9ff')
if CAVE():
	container_g2.setSize(Vector2(2732-4, 1536-4))
	container_g2.setPadding(0)
	container_g2.setPosition(Vector2(21856+2,0+2+1536))
else:
	container_g2.setSize(Vector2(2728*0.2, 1532*0.2))
	container_g2.setPadding(2)
	container_g2.setPosition(Vector2(20, 20+400))
container_g2.setBlendMode(WidgetBlendMode.BlendNormal)
container_g2.setAlpha(1.0)
container_g2.setAutosize(False)

## create graph 2
graph2 = Container.create(ContainerLayout.LayoutFree, container_g2)
graph2.setPosition(Vector2(200,50))
if CAVE():
	graph2.setSize(Vector2(2478, 1332))
else:
	graph2.setSize(Vector2((2732-4-104)*0.2, (1536-4-104)*0.2))
# graph2.setClippingEnabled(True)
graph2.setAutosize(False)

## create x label
xlabel2 = Label.create(container_g2)
xlabel2.setAutosize(False)
xlabel2.setSize(Vector2(container_g2.getWidth(), 50 ))
xlabel2.setText('')
xlabel2.setColor(Color('white'))
xlabel2.setStyleValue('align', 'middle-center')
if CAVE():
	xlabel2.setFont('fonts/arial.ttf 76')
else:
	xlabel2.setFont('fonts/arial.ttf 14')
xlabel2.setCenter(Vector2(container_g2.getSize().x*0.5,container_g2.getSize().y-50))
xlabel2.setAutosize(False)

## create y label
ylabel2 = Label.create(container_g2)
ylabel2.setText('')
ylabel2.setColor(Color('white'))
# ylabel1.setSize(Vector2(container_g1.getWidth(), 50 ))
ylabel2.setSize(Vector2(50, container_g1.getHeight()))
ylabel2.setAutosize(False)
ylabel2.setStyleValue('align', 'middle-center')
if CAVE():
	ylabel2.setFont('fonts/arial.ttf 76')
else:
	ylabel2.setFont('fonts/arial.ttf 14')
ylabel2.setCenter(Vector2(40,container_g2.getHeight()*0.5))
#ylabel1.setStyleValue('align', 'middle-center')
ylabel2.setRotation(-90)

## create p label
plabel2 = Label.create(container_g2)
plabel2.setText('')
plabel2.setColor(Color('white'))
if CAVE():
	plabel2.setFont('fonts/arial.ttf 76')
else:
	plabel2.setFont('fonts/arial.ttf 14')
plabel2.setCenter(Vector2(container_g2.getSize().x*0.5,50))

## create x axis
xaxis2 = Container.create(ContainerLayout.LayoutFree, container_g2)
xaxis2.setSize(Vector2(graph2.getWidth(), 2))
xaxis2.setStyleValue('border', '4 #ffffffff')
xaxis2.setAutosize(False)
xaxis2.setPosition(Vector2(graph2.getPosition().x,graph2.getPosition().y+graph2.getHeight()))

## create y axis
yaxis2 = Container.create(ContainerLayout.LayoutFree, container_g2)
yaxis2.setSize(Vector2(2, graph2.getHeight()))
yaxis2.setStyleValue('border', '4 #ffffffff')
yaxis2.setAutosize(False)
yaxis2.setPosition(Vector2(graph2.getPosition().x,graph2.getPosition().y))

## highlight a box
def highlight_box(box, highlight):
	if box!=None:
		if highlight:
			box.setEffect('colored -e #e2747144')
			box.getMaterial().setTransparent(True)
		else:
			box.setEffect('colored -e #01b2f144')
			box.getMaterial().setTransparent(True)

## highlight a box to blue
def highlight_box_blue(box, highlight):
	if box!=None:
		if highlight:
			box.setEffect('colored -e #3274cc44')
			box.getMaterial().setTransparent(True)
		else:
			box.setEffect('colored -e #01b2f144')
			box.getMaterial().setTransparent(True)

# test if need highlight
def needHighlight(sys,star,p):
	if p._isEarthSized and p._orbit>star._habNear and p._orbit<star._habFar:
		return True
	elif cmp(sys._name, 'Gliese 876')==0 and cmp(p._name,'b')==0:
		return True
	elif cmp(sys._name,'55 Cancri')==0 and cmp(p._name,'f')==0:
		return True
	elif cmp(sys._name,'Upsilon Andromedae')==0 and cmp(p._name,'d')==0:
		return True
	elif cmp(sys._name,'47 Ursae Majoris')==0 and cmp(p._name,'b')==0:
		return True
	elif cmp(sys._name,'HD 37124')==0 and cmp(p._name,'c')==0:
		return True

	elif cmp(sys._binary,'')!=0:
		return True

	elif cmp(curSys._name,'Gliese 667')==0 or cmp(curSys._name,'Kepler-78')==0 or cmp(curSys._name,'HD 10180')==0 or cmp(curSys._name,'Kepler-69')==0:
		return True

	return False

img_radial = loadImage('textures/detec/rad.png')
img_transit = loadImage('textures/detec/transit.jpg')
img_imaging = loadImage('textures/detec/imag.png')
img_other = loadImage('textures/detec/other.png')
img_unknown = loadImage('textures/detec/unknown.png')

img_star = loadImage('textures/dot/Circle_Grey.png')
img_select = loadImage('textures/dot/select.png')
img_highlight = loadImage('textures/dot/Circle_Red.png')
'''textures/dot/star.png'''
'''textures/dot/dot.png'''

def updateGraph():

	global li_dotOnWall
	global graph1
	global xlabel1
	global ylabel1
	global plabel1

	# global graph2
	# global xlabel2
	# global ylabel2
	# global plabel2

	print 'start updating Graph'

	if graph1.getNumChildren()>0:
		for i in xrange(graph1.getNumChildren()):
			graph1.removeChild(graph1.getChildByIndex(0))

	max_mass = 0
	max_size = 0
	max_orbit = 0
	max_year = 0
	max_dis = 0

	for i in xrange(len(li_dotOnWall)):
		p = li_dotOnWall[i].getPla()
		star = li_dotOnWall[i].getSys()._star
		if p._mass>max_mass:
			max_mass = p._mass
		if p._size>max_size:
			max_size = p._size
		if p._orbit>max_orbit:
			max_orbit = p._orbit
		if p._year>max_year:
			max_year = p._year
		if star._dis>max_dis:
			max_dis = star._dis

	min_mass = max_mass
	min_size = max_size
	min_orbit = max_orbit
	min_year = max_year
	min_dis = max_dis

	for i in xrange(len(li_dotOnWall)):
		p = li_dotOnWall[i].getPla()
		star = li_dotOnWall[i].getSys()._star
		if p._mass>0 and p._mass<min_mass:
			min_mass = p._mass
		if p._size>0 and p._size<min_size:
			min_size = p._size
		if p._orbit>0 and p._orbit<min_orbit:
			min_orbit = p._orbit
		if p._year>0 and p._year<min_year:
			min_year = p._year
		if star._dis>0 and star._dis<min_dis:
			min_dis = star._dis

	minx = 0
	miny = 0

	print 'min_mass:',min_mass

	''' get min for x (0-1)'''
	## mass
	if btn_x_1.isChecked():
		if min_mass>0:
			minx = math.log10( min_mass )*1.0/math.log10( (max_mass) )
		else:
			minx = 0
	## radius
	elif btn_x_2.isChecked():
		if min_size>0:
			minx = math.log10( (min_size) )*1.0/math.log10( (max_size) )
		else:
			minx = 0
	## orbit R (orbit)
	elif btn_x_3.isChecked():
		if min_orbit>0:
			minx = math.log10( (min_orbit) )*1.0/math.log10( (max_orbit) )
		else:
			minx = 0
	## orbit P (year)
	elif btn_x_4.isChecked():
		if min_year>0:
			minx = math.log10( min_year*8760 )*1.0/math.log10( max_year*8760 )
		else:
			minx = 0
	## dis to us
	elif btn_x_5.isChecked():
		if min_dis>0:
			minx = math.log10(min_dis)*1.0/math.log10(max_dis)
		else:minx = 0

	''' get min for y (0-1)'''
	## mass
	if btn_y_1.isChecked():
		if min_mass>0:
			miny = math.log10( (min_mass) )*1.0/math.log10( (max_mass) )
		else:
			miny = 0
	## radius
	elif btn_y_2.isChecked():
		if min_size>0:
			miny = math.log10( (min_size) )*1.0/math.log10( (max_size) )
		else:
			miny = 0
	## orbit R (orbit)
	elif btn_y_3.isChecked():
		if min_orbit>0:
			miny = math.log10( (min_orbit) )*1.0/math.log10( (max_orbit) )
		else:
			miny = 0
	## orbit P (year)
	elif btn_y_4.isChecked():
		if min_year>0:
			miny = math.log10( min_year*8760 )*1.0/math.log10( max_year*8760 )
		else:
			miny = 0
	## dis to us
	elif btn_y_5.isChecked():
		if min_dis>0:
			miny = math.log10(min_dis)*1.0/math.log10(max_dis)
		else:
			miny = 0

	# print 'minx:',minx
	# print 'miny:',miny
	
	for i in xrange(len(li_dotOnWall)):
		p = li_dotOnWall[i].getPla()
		star = li_dotOnWall[i].getSys()._star

		img = Image.create(graph1)

		posx = 0
		posy = 0

		# BTN_P
		## detection method
		if btn_p_1.isChecked():
			# print 'detection method'
			plabel1.setText('detection method')
			if cmp(p._detection,'unknown')==0:
				img.setData(img_unknown)
			elif cmp(p._detection,'Radial Velocity')==0:
				img.setData(img_radial)
			elif cmp(p._detection,'Transit')==0:
				img.setData(img_transit)
			elif cmp(p._detection,'Imaging')==0:
				img.setData(img_imaging)
			elif cmp(p._detection,'Pulsar Timing')==0:
				img.setData(img_other)
			elif cmp(p._detection,'Eclipse Timing Variations')==0:
				img.setData(img_other)
			elif cmp(p._detection,'Microlensing')==0:	
				img.setData(img_other)
			if CAVE():
				img.setSize(Vector2(45,45))
			else:
				img.setSize(Vector2(9,9))
		## radius
		elif btn_p_2.isChecked():
			# print 'radius'
			plabel1.setText('radius')
			if needHighlight(li_dotOnWall[i].getSys(),star,p):
				img.setData(img_highlight)
			else:
				img.setData(img_star)
			if p._size>0:
				if CAVE():
					img.setSize(Vector2(math.log10( (p._size) )*100.0/math.log10( (max_size) ),math.log10( (p._size) )*100.0/math.log10( (max_size) )))
					# img.setSize(Vector2(p._size*100.0/max_size,p._size*100.0/max_size))
				else:
					img.setSize(Vector2(math.log10((p._size) )*20.0/math.log10( (max_size) ),math.log10( (p._size) )*20.0/math.log10( ( max_size ) )))
					# img.setSize(Vector2(p._size*20.0/max_size,p._size*20.0/max_size))
			else:
				img.setSize(Vector2(1,1))
			# print 'img size:',img.getSize()
		## mass
		elif btn_p_3.isChecked():
			# print 'mass'
			plabel1.setText('mass')
			if needHighlight(li_dotOnWall[i].getSys(),star,p):
				img.setData(img_highlight)
			else:
				img.setData(img_star)
			if p._mass>0:
				if CAVE():
					# img.setSize(Vector2(math.log10( (p._mass) )*100.0/math.log10( (max_mass) ),math.log10( (p._mass) )*100.0/math.log10( (max_mass) ) ))
					img.setSize(Vector2(p._mass*100.0/max_mass,p._mass*100.0/max_mass))
				else:
					# img.setSize(Vector2(math.log10( (p._mass) )*20.0/math.log10( (max_mass) ),math.log10( (p._mass) )*20.0/math.log10( (max_mass) ) ))
					img.setSize(Vector2(p._mass*20.0/max_mass,p._mass*20.0/max_mass))
			else:
				img.setSize(Vector2(1,1))
			print 'img size:',img.getSize()
		else:
			plabel1.setText('')
			if needHighlight(li_dotOnWall[i].getSys(),star,p):
				img.setData(img_highlight)
			else:
				img.setData(img_star)
			if CAVE():
				img.setSize(Vector2(45,45))
			else:
				img.setSize(Vector2(9,9))

		# BTN_X
		## mass
		if btn_x_1.isChecked():
			xlabel1.setText('planet mass (kg)')
			if p._mass>0:
				posx = math.log10( (p._mass) )*1.0/math.log10( (max_mass) )
			else:
				posx = 0
		## radius
		elif btn_x_2.isChecked():
			xlabel1.setText('planet radius (km)')
			if p._size>0:
				posx = math.log10( (p._size) )*1.0/math.log10( (max_size) )
			else:
				posx = 0
		## orbit R (orbit)
		elif btn_x_3.isChecked():
			xlabel1.setText('orbital radius (km)')
			if p._orbit>0:
				posx = math.log10( (p._orbit) )*1.0/math.log10( (max_orbit) )
			else:
				posx = 0
		## orbit P (year)
		elif btn_x_4.isChecked():
			xlabel1.setText('orbital period (hour)')
			if p._year>0:
				posx = math.log10( p._year*8760 )*1.0/math.log10( max_year*8760 )
			else:
				posx = 0
		## dis to us
		elif btn_x_5.isChecked():
			xlabel1.setText('distance to the Sun (lightyear)')
			if star._dis>0:
				posx = math.log10(star._dis)*1.0/math.log10(max_dis)
			else:
				posx = 0

		# BTN_Y
		## mass
		if btn_y_1.isChecked():
			ylabel1.setText('planet mass (kg)')
			if p._mass>0:
				posy = math.log10( (p._mass) )*1.0/math.log10( (max_mass) )
			else:
				posy = 0
		## radius
		elif btn_y_2.isChecked():
			ylabel1.setText('planet radius (km)')
			if p._size>0:
				posy = math.log10( (p._size) )*1.0/math.log10( (max_size) )
			else:
				posy = 0
		## orbit R (orbit)
		elif btn_y_3.isChecked():
			ylabel1.setText('orbital radius (km)')
			if p._orbit>0:
				posy = math.log10( (p._orbit) )*1.0/math.log10( (max_orbit) )
			else:
				posy = 0
		## orbit P (year)
		elif btn_y_4.isChecked():
			ylabel1.setText('orbital period (hour)')
			if p._year>0:
				posy = math.log10( p._year*8760 )*1.0/ math.log10( max_year*8760 )
			else:
				posy = 0	
		## dis to us
		elif btn_y_5.isChecked():
			ylabel1.setText('distance to the Sun (lightyear)')
			if star._dis>0:
				posy = math.log10(star._dis)*1.0/math.log10(max_dis)
			else:
				posy = 0

		xx = 0
		yy = graph1.getHeight()

		if posx != 0:
			# if posx<minx:
			# 	print 'posx, minx:', minx, posx
			xx = 0.8 * graph1.getWidth() * (posx-minx)/(1-minx) + 0.1 * graph1.getWidth()
		if posy != 0:
			yy = 0.8 * graph1.getHeight() * ( 1 - (posy-miny)/(1-miny) ) + 0.1 * graph1.getHeight()
		img.setCenter( Vector2(xx,yy) )
		# print 'x,y:',xx,yy
		li_dotOnWall[i].setImage(img)

	## draw numbers on x axis
	### 0.1 min
	xnum1_1 = Label.create(graph1)
	
	## mass
	if btn_x_1.isChecked():
		xnum1_1.setText( str( round(min_mass,2) ) )
		# print 'round:',round(float(KG_from_Me(min_mass)),2)
		# print 'xnum1_1:',xnum1_1.getText()
	## radius
	elif btn_x_2.isChecked():
		xnum1_1.setText( str( round((min_size),2) ) )
	## orbit R (orbit)
	elif btn_x_3.isChecked():
		xnum1_1.setText( str( round((min_orbit),2) ) )
	## orbit P (year)
	elif btn_x_4.isChecked():
		xnum1_1.setText( str( min_year*8760 ) )
	## dis to us
	elif btn_x_5.isChecked():
		xnum1_1.setText( str( min_dis ) )

	xnum1_1.setCenter(Vector2( 0.1 * graph1.getWidth(), graph1.getHeight() + 20  ))
	xnum1_1.setAutosize(False)
	xnum1_1.setFont('fonts/helvetica.ttf 30')
	xnum1_1.setColor(Color('white'))

	### 0.1 + 0.8/3
	xnum1_2 = Label.create(graph1)

	## mass
	if btn_x_1.isChecked():
		if max_mass>0:
			xnum1_2.setText( str( round(math.pow(10, math.log10((max_mass)) * (minx+(1-minx)/3.0) ),2) ) )
		else:
			xnum1_2.setText('0.0')
	## radius
	elif btn_x_2.isChecked():
		if max_size>0:
			xnum1_2.setText( str( round(math.pow(10, math.log10((max_size)) * (minx+(1-minx)/3.0) ),2) ) )
		else:
			xnum1_2.setText('0.0')
	## orbit R (orbit)
	elif btn_x_3.isChecked():
		if max_orbit>0:
			xnum1_2.setText( str( round(math.pow(10, math.log10((max_orbit)) * (minx+(1-minx)/3.0) ),2) ) )
		else:
			xnum1_2.setText('0.0')
	## orbit P (year)
	elif btn_x_4.isChecked():
		xnum1_2.setText( str( round(math.pow(10, max_year*8760.0 * (minx+(1-minx)/3.0) ),2) ) )
	## dis to us
	elif btn_x_5.isChecked():
		xnum1_2.setText( str( round(math.pow(10, max_dis* (minx+(1-minx)/3.0) ),2) ) )

	xnum1_2.setCenter(Vector2( (0.1+0.8/3) * graph1.getWidth(), graph1.getHeight() + 20  ))
	xnum1_2.setFont('fonts/helvetica.ttf 30')
	xnum1_2.setAutosize(False)
	xnum1_2.setColor(Color('white'))

	### 0.9 - 0.8/3
	xnum1_3 = Label.create(graph1)

	## mass
	if btn_x_1.isChecked():
		if max_mass>0:
			xnum1_3.setText( str( round(math.pow(10, math.log10((max_mass))*(minx+2*(1-minx)/3.0) ),2) ) )
		else:
			xnum1_3.setText('0.0')
	## radius
	elif btn_x_2.isChecked():
		if max_size>0:
			xnum1_3.setText( str( round(math.pow(10, math.log10((max_size))*(minx+2*(1-minx)/3.0)),2) ) )
		else:
			xnum1_3.setText('0.0')
	## orbit R (orbit)
	elif btn_x_3.isChecked():
		if max_orbit>0:
			xnum1_3.setText( str( round(math.pow(10, math.log10((max_orbit))*(minx+2*(1-minx)/3.0)),2) ) )
		else:
			xnum1_3.setText('0.0')
	## orbit P (year)
	elif btn_x_4.isChecked():
		xnum1_3.setText( str( round(math.pow(10, max_year*8760.0*(minx+2*(1-minx)/3.0) ),2) ) )
	## dis to us
	elif btn_x_5.isChecked():
		xnum1_3.setText( str( round(math.pow(10, max_dis*(minx+2*(1-minx)/3.0) ),2) ) )

	xnum1_3.setCenter(Vector2( (0.9-0.8/3) * graph1.getWidth(), graph1.getHeight() + 20  ))
	xnum1_3.setFont('fonts/helvetica.ttf 30')
	xnum1_3.setAutosize(False)
	xnum1_3.setColor(Color('white'))

	### 0.9 max
	xnum1_4 = Label.create(graph1)

	## mass
	if btn_x_1.isChecked():
		xnum1_4.setText( str( round((max_mass),2) ) )
	## radius
	elif btn_x_2.isChecked():
		xnum1_4.setText( str( round((max_size),2) ) )
	## orbit R (orbit)
	elif btn_x_3.isChecked():
		xnum1_4.setText( str( round((max_orbit),2) ) )
	## orbit P (year)
	elif btn_x_4.isChecked():
		xnum1_4.setText( str( round(max_year*8760,2) ) )
	## dis to us
	elif btn_x_5.isChecked():
		xnum1_4.setText( str( max_dis ) )

	xnum1_4.setCenter(Vector2( 0.9 * graph1.getWidth(), graph1.getHeight() + 20  ))
	xnum1_4.setFont('fonts/helvetica.ttf 30')
	xnum1_4.setAutosize(False)
	xnum1_4.setColor(Color('white'))

	## draw numbers on y axis
	### 0.1 min
	ynum1_1 = Label.create(graph1)
	## mass
	if btn_y_1.isChecked():
		ynum1_1.setText( str( round((min_mass),2) ) )
	## radius
	elif btn_y_2.isChecked():
		ynum1_1.setText( str( round((min_size),2) ) )
	## orbit R (orbit)
	elif btn_y_3.isChecked():
		ynum1_1.setText( str( round((min_orbit),2) ) )
	## orbit P (year)
	elif btn_y_4.isChecked():
		ynum1_1.setText( str( round(min_year*8760,2) ) )
	## dis to us
	elif btn_y_5.isChecked():
		ynum1_1.setText( str( min_dis ) )

	ynum1_1.setCenter(Vector2(-25,0.9 * graph1.getHeight()))
	ynum1_1.setFont('fonts/helvetica.ttf 30')
	ynum1_1.setColor(Color('white'))
	ynum1_1.setAutosize(False)
	ynum1_1.setRotation(-90)

	### 0.1 + 0.8/3
	ynum1_2 = Label.create(graph1)

	## mass
	if btn_y_1.isChecked():
		if max_mass>0:
			ynum1_2.setText( str( round(math.pow(10, math.log10((max_mass)) * (miny+(1-miny)/3.0) ),2) ) )
		else:
			ynum1_2.setText('0.0')
	## radius
	elif btn_y_2.isChecked():
		if max_size>0:
			ynum1_2.setText( str( round(math.pow(10, math.log10((max_size)) * (miny+(1-miny)/3.0) ),2) ) )
		else:
			ynum1_2.setText('0.0')
	## orbit R (orbit)
	elif btn_y_3.isChecked():
		if max_orbit>0:
			ynum1_2.setText( str( round(math.pow(10, math.log10((max_orbit)) * (miny+(1-miny)/3.0) ),2) ) )
		else:
			ynum1_2.setText('0.0')
	## orbit P (year)
	elif btn_y_4.isChecked():
		ynum1_2.setText( str( round(math.pow(10, max_year*8760.0 * (miny+(1-miny)/3.0) ),2) ) )
	## dis to us
	elif btn_y_5.isChecked():
		ynum1_2.setText( str( round(math.pow(10, max_dis* (miny+(1-miny)/3.0) ),2) ) )

	ynum1_2.setCenter(Vector2( -25,(0.9-0.8/3) * graph1.getHeight() ))
	ynum1_2.setFont('fonts/helvetica.ttf 30')
	ynum1_2.setAutosize(False)
	ynum1_2.setColor(Color('white'))
	ynum1_2.setRotation(-90)

	### 0.9 - 0.8/3
	ynum1_3 = Label.create(graph1)

	## mass
	if btn_y_1.isChecked():
		if max_mass>0:
			ynum1_3.setText( str( round(math.pow(10, math.log10((max_mass))*(miny+2.0*(1-miny)/3.0) ),2) ) )
		else:
			ynum1_3.setText('0.0')
	## radius
	elif btn_y_2.isChecked():
		if max_size>0:
			ynum1_3.setText( str( round(math.pow(10, math.log10((max_size))*(miny+2.0*(1-miny)/3.0)),2) ) )
		else:
			ynum1_3.setText('0.0')
	## orbit R (orbit)
	elif btn_y_3.isChecked():
		if max_orbit>0:
			ynum1_3.setText( str( round(math.pow(10, math.log10((max_orbit))*(miny+2.0*(1-miny)/3.0)),2) ) )
		else:
			ynum1_3.setText('0.0')
	## orbit P (year)
	elif btn_y_4.isChecked():
		ynum1_3.setText( str( round(math.pow(10, max_year*8760.0*(miny+2.0*(1-miny)/3.0) ),2) ) )
	## dis to us
	elif btn_y_5.isChecked():
		ynum1_3.setText( str( round(math.pow(10, max_dis*(miny+2.0*(1-miny)/3.0) ),2) ) )

	ynum1_3.setCenter(Vector2( -25,(0.1+0.8/3) * graph1.getHeight() ))
	ynum1_3.setFont('fonts/helvetica.ttf 30')
	ynum1_3.setColor(Color('white'))
	ynum1_3.setAutosize(False)
	ynum1_3.setRotation(-90)

	### 0.9 max
	ynum1_4 = Label.create(graph1)

	## mass
	if btn_y_1.isChecked():
		ynum1_4.setText( str( round((max_mass),2) ) )
	## radius
	elif btn_y_2.isChecked():
		ynum1_4.setText( str( round((max_size),2) ) )
	## orbit R (orbit)
	elif btn_y_3.isChecked():
		ynum1_4.setText( str( round((max_orbit),2) ) )
	## orbit P (year)
	elif btn_y_4.isChecked():
		ynum1_4.setText( str( round(max_year*8760,2) ) )
	## dis to us
	elif btn_y_5.isChecked():
		ynum1_4.setText( str( max_dis ) )

	ynum1_4.setCenter(Vector2( -25, 0.1 * graph1.getHeight()))
	ynum1_4.setFont('fonts/helvetica.ttf 30')
	ynum1_4.setColor(Color('white'))
	ynum1_4.setAutosize(False)
	ynum1_4.setRotation(-90)

	print 'done'

def updateGraph2():

	global li_dotOnWall2
	global graph2
	global xlabel2
	global ylabel2
	global plabel2

	print 'start updating Graph 2'

	if graph2.getNumChildren()>0:
		for i in xrange(graph2.getNumChildren()):
			graph2.removeChild(graph2.getChildByIndex(0))

	max_mass = 0
	max_size = 0
	max_orbit = 0
	max_year = 0
	max_dis = 0

	for i in xrange(len(li_dotOnWall2)):
		p = li_dotOnWall2[i].getPla()
		star = li_dotOnWall2[i].getSys()._star
		if p._mass>max_mass:
			max_mass = p._mass
		if p._size>max_size:
			max_size = p._size
		if p._orbit>max_orbit:
			max_orbit = p._orbit
		if p._year>max_year:
			max_year = p._year
		if star._dis>max_dis:
			max_dis = star._dis

	min_mass = max_mass
	min_size = max_size
	min_orbit = max_orbit
	min_year = max_year
	min_dis = max_dis

	for i in xrange(len(li_dotOnWall2)):
		p = li_dotOnWall2[i].getPla()
		star = li_dotOnWall2[i].getSys()._star
		if p._mass>0 and p._mass<min_mass:
			min_mass = p._mass
		if p._size>0 and p._size<min_size:
			min_size = p._size
		if p._orbit>0 and p._orbit<min_orbit:
			min_orbit = p._orbit
		if p._year>0 and p._year<min_year:
			min_year = p._year
		if star._dis>0 and star._dis<min_dis:
			min_dis = star._dis

	minx = 0
	miny = 0

	# print 'min_mass:',min_mass

	''' get min for x (0-1)'''
	## mass
	if btn_x_12.isChecked():
		if min_mass>0:
			minx = math.log10( min_mass )*1.0/math.log10( (max_mass) )
		else:
			minx = 0
	## radius
	elif btn_x_22.isChecked():
		if min_size>0:
			minx = math.log10( (min_size) )*1.0/math.log10( (max_size) )
		else:
			minx = 0
	## orbit R (orbit)
	elif btn_x_32.isChecked():
		if min_orbit>0:
			minx = math.log10( (min_orbit) )*1.0/math.log10( (max_orbit) )
		else:
			minx = 0
	## orbit P (year)
	elif btn_x_42.isChecked():
		if min_year>0:
			minx = math.log10( min_year*8760 )*1.0/math.log10( max_year*8760 )
		else:
			minx = 0
	## dis to us
	elif btn_x_52.isChecked():
		if min_dis>0:
			minx = math.log10(min_dis)*1.0/math.log10(max_dis)
		else:minx = 0

	''' get min for y (0-1)'''
	## mass
	if btn_y_12.isChecked():
		if min_mass>0:
			miny = math.log10( (min_mass) )*1.0/math.log10( (max_mass) )
		else:
			miny = 0
	## radius
	elif btn_y_22.isChecked():
		if min_size>0:
			miny = math.log10( (min_size) )*1.0/math.log10( (max_size) )
		else:
			miny = 0
	## orbit R (orbit)
	elif btn_y_32.isChecked():
		if min_orbit>0:
			miny = math.log10( (min_orbit) )*1.0/math.log10( (max_orbit) )
		else:
			miny = 0
	## orbit P (year)
	elif btn_y_42.isChecked():
		if min_year>0:
			miny = math.log10( min_year*8760 )*1.0/math.log10( max_year*8760 )
		else:
			miny = 0
	## dis to us
	elif btn_y_52.isChecked():
		if min_dis>0:
			miny = math.log10(min_dis)*1.0/math.log10(max_dis)
		else:
			miny = 0
	
	for i in xrange(len(li_dotOnWall2)):
		p = li_dotOnWall2[i].getPla()
		star = li_dotOnWall2[i].getSys()._star

		img = Image.create(graph2)

		posx = 0
		posy = 0

		# BTN_P
		## detection method
		if btn_p_12.isChecked():
			# print 'detection method'
			plabel2.setText('detection method')
			if cmp(p._detection,'unknown')==0:
				img.setData(img_unknown)
			elif cmp(p._detection,'Radial Velocity')==0:
				img.setData(img_radial)
			elif cmp(p._detection,'Transit')==0:
				img.setData(img_transit)
			elif cmp(p._detection,'Imaging')==0:
				img.setData(img_imaging)
			elif cmp(p._detection,'Pulsar Timing')==0:
				img.setData(img_other)
			elif cmp(p._detection,'Eclipse Timing Variations')==0:
				img.setData(img_other)
			elif cmp(p._detection,'Microlensing')==0:	
				img.setData(img_other)
			if CAVE():
				img.setSize(Vector2(45,45))
			else:
				img.setSize(Vector2(9,9))
		## radius
		elif btn_p_22.isChecked():
			# print 'radius'
			plabel2.setText('radius')
			if needHighlight(li_dotOnWall2[i].getSys(),star,p):
				img.setData(img_highlight)
			else:
				img.setData(img_star)
			if p._size>0:
				if CAVE():
					img.setSize(Vector2(math.log10( KM_from_Rj(p._size) )*100.0/math.log10( KM_from_Rj(max_size) ),math.log10( KM_from_Rj(p._size) )*100.0/math.log10( KM_from_Rj(max_size) )))
					# img.setSize(Vector2(p._size*100.0/max_size,p._size*100.0/max_size))
				else:
					img.setSize(Vector2(math.log10(KM_from_Rj(p._size) )*20.0/math.log10( KM_from_Rj(max_size) ),math.log10( KM_from_Rj(p._size) )*20.0/math.log10( KM_from_Rj( max_size ) )))
					# img.setSize(Vector2(p._size*20.0/max_size,p._size*20.0/max_size))
			else:
				img.setSize(Vector2(1,1))
			print 'img size:',img.getSize()
		## mass
		elif btn_p_32.isChecked():
			# print 'mass'
			plabel2.setText('mass')
			if needHighlight(li_dotOnWall2[i].getSys(),star,p):
				img.setData(img_highlight)
			else:
				img.setData(img_star)
			if p._mass>0:
				if CAVE():
					# img.setSize(Vector2(math.log10( (p._mass) )*100.0/math.log10( (max_mass) ),math.log10( (p._mass) )*100.0/math.log10( (max_mass) ) ))
					img.setSize(Vector2(p._mass*100.0/max_mass,p._mass*100.0/max_mass))
				else:
					# img.setSize(Vector2(math.log10( (p._mass) )*20.0/math.log10( (max_mass) ),math.log10( (p._mass) )*20.0/math.log10( (max_mass) ) ))
					img.setSize(Vector2(p._mass*20.0/max_mass,p._mass*20.0/max_mass))
			else:
				img.setSize(Vector2(1,1))
			print 'img size:',img.getSize()
		else:
			plabel2.setText('')
			if needHighlight(li_dotOnWall2[i].getSys(),star,p):
				img.setData(img_highlight)
			else:
				img.setData(img_star)
			if CAVE():
				img.setSize(Vector2(45,45))
			else:
				img.setSize(Vector2(9,9))

		# BTN_X
		## mass
		if btn_x_12.isChecked():
			xlabel2.setText('planet mass (kg)')
			if p._mass>0:
				posx = math.log10( (p._mass) )*1.0/math.log10( (max_mass) )
			else:
				posx = 0
		## radius
		elif btn_x_22.isChecked():
			xlabel2.setText('planet radius (km)')
			if p._size>0:
				posx = math.log10( (p._size) )*1.0/math.log10( (max_size) )
			else:
				posx = 0
		## orbit R (orbit)
		elif btn_x_32.isChecked():
			xlabel2.setText('orbital radius (km)')
			if p._orbit>0:
				posx = math.log10( (p._orbit) )*1.0/math.log10( (max_orbit) )
			else:
				posx = 0
		## orbit P (year)
		elif btn_x_42.isChecked():
			xlabel2.setText('orbital period (hour)')
			if p._year>0:
				posx = math.log10( p._year*8760 )*1.0/math.log10( max_year*8760 )
			else:
				posx = 0
		## dis to us
		elif btn_x_52.isChecked():
			xlabel2.setText('distance to the Sun (lightyear)')
			if star._dis>0:
				posx = math.log10(star._dis)*1.0/math.log10(max_dis)
			else:
				posx = 0

		# BTN_Y
		## mass
		if btn_y_12.isChecked():
			ylabel2.setText('planet mass (kg)')
			if p._mass>0:
				posy = math.log10( (p._mass) )*1.0/math.log10( (max_mass) )
			else:
				posy = 0
		## radius
		elif btn_y_22.isChecked():
			ylabel2.setText('planet radius (km)')
			if p._size>0:
				posy = math.log10( (p._size) )*1.0/math.log10( (max_size) )
			else:
				posy = 0
		## orbit R (orbit)
		elif btn_y_32.isChecked():
			ylabel2.setText('orbital radius (km)')
			if p._orbit>0:
				posy = math.log10( (p._orbit) )*1.0/math.log10( (max_orbit) )
			else:
				posy = 0
		## orbit P (year)
		elif btn_y_42.isChecked():
			ylabel2.setText('orbital period (hour)')
			if p._year>0:
				posy = math.log10( p._year*8760 )*1.0/ math.log10( max_year*8760 )
			else:
				posy = 0	
		## dis to us
		elif btn_y_52.isChecked():
			ylabel2.setText('distance to the Sun (lightyear)')
			if star._dis>0:
				posy = math.log10(star._dis)*1.0/math.log10(max_dis)
			else:
				posy = 0

		xx = 0
		yy = graph2.getHeight()

		if posx != 0:
			# if posx<minx:
			# 	print 'posx, minx:', minx, posx
			xx = 0.8 * graph2.getWidth() * (posx-minx)/(1-minx) + 0.1 * graph2.getWidth()
		if posy != 0:
			yy = 0.8 * graph2.getHeight() * ( 1 - (posy-miny)/(1-miny) ) + 0.1 * graph2.getHeight()
		img.setCenter( Vector2(xx,yy) )
		# print 'x,y:',xx,yy
		li_dotOnWall2[i].setImage(img)

	## draw numbers on x axis
	### 0.1 min
	xnum2_1 = Label.create(graph2)
	
	## mass
	if btn_x_12.isChecked():
		xnum2_1.setText( str( round((min_mass),2) ) )
	## radius
	elif btn_x_22.isChecked():
		xnum2_1.setText( str( round((min_size),2) ) )
	## orbit R (orbit)
	elif btn_x_32.isChecked():
		xnum2_1.setText( str( round((min_orbit),2) ) )
	## orbit P (year)
	elif btn_x_42.isChecked():
		xnum2_1.setText( str( min_year*8760 ) )
	## dis to us
	elif btn_x_52.isChecked():
		xnum2_1.setText( str( min_dis ) )

	xnum2_1.setCenter(Vector2( 0.1 * graph2.getWidth(), graph2.getHeight() + 20  ))
	xnum2_1.setAutosize(False)
	xnum2_1.setFont('fonts/helvetica.ttf 30')
	xnum2_1.setColor(Color('white'))

	### 0.1 + 0.8/3
	xnum2_2 = Label.create(graph2)

	## mass
	if btn_x_12.isChecked():
		if max_mass>0:
			xnum2_2.setText( str( round(math.pow(10, math.log10((max_mass))*(minx+(1-minx)/3.0) ),2) ))
		else:
			xnum2_2.setText('0.0')
	## radius
	elif btn_x_22.isChecked():
		if max_size>0:
			xnum2_2.setText( str( round(math.pow(10, math.log10((max_size))*(minx+(1-minx)/3.0) ),2) ))
		else:
			xnum2_2.setText('0.0')
	## orbit R (orbit)
	elif btn_x_32.isChecked():
		if max_orbit>0:
			xnum2_2.setText( str( round(math.pow(10, math.log10((max_orbit))*(minx+(1-minx)/3.0) ),2) ))
		else:
			xnum2_2.setText('0.0')
	## orbit P (year)
	elif btn_x_42.isChecked():
		xnum2_2.setText( str( round(math.pow(10, max_year*8760.0*(minx+(1-minx)/3.0 ) ),2) ))
	## dis to us
	elif btn_x_52.isChecked():
		xnum2_2.setText( str( round(math.pow(10, max_dis*(minx+(1-minx)/3.0 ) ),2)))

	xnum2_2.setCenter(Vector2( (0.1+0.8/3) * graph2.getWidth(), graph2.getHeight() + 20  ))
	xnum2_2.setFont('fonts/helvetica.ttf 30')
	xnum2_2.setAutosize(False)
	xnum2_2.setColor(Color('white'))

	### 0.9 - 0.8/3
	xnum2_3 = Label.create(graph2)

	## mass
	if btn_x_12.isChecked():
		if max_mass>0:
			xnum2_3.setText( str( round(math.pow(10, math.log10((max_mass))*(minx+2*(1-minx)/3.0) ),2) ))
		else:
			xnum2_3.setText('0.0')
	## radius
	elif btn_x_22.isChecked():
		if max_size>0:
			xnum2_3.setText( str( round(math.pow(10, math.log10((max_size))*(minx+2*(1-minx)/3.0) ),2) ))
		else:
			xnum2_3.setText('0.0')
	## orbit R (orbit)
	elif btn_x_32.isChecked():
		if max_orbit>0:
			xnum2_3.setText( str( round(math.pow(10, math.log10((max_orbit))*(minx+2*(1-minx)/3.0) ),2) ))
		else:
			xnum2_3.setText('0.0')
	## orbit P (year)
	elif btn_x_42.isChecked():
		xnum2_3.setText( str( round(math.pow(10, max_year*8760.0*(minx+2*(1-minx)/3.0 ) ),2) ))
	## dis to us
	elif btn_x_52.isChecked():
		xnum2_3.setText( str( round(math.pow(10, max_dis*(minx+2*(1-minx)/3.0 ) ),2) ))

	xnum2_3.setCenter(Vector2( (0.9-0.8/3) * graph2.getWidth(), graph2.getHeight() + 20  ))
	xnum2_3.setFont('fonts/helvetica.ttf 30')
	xnum2_3.setAutosize(False)
	xnum2_3.setColor(Color('white'))

	### 0.9 max
	xnum2_4 = Label.create(graph2)

	## mass
	if btn_x_12.isChecked():
		xnum2_4.setText( str( round((max_mass),2) ) )
	## radius
	elif btn_x_22.isChecked():
		xnum2_4.setText( str( round((max_size),2) ) )
	## orbit R (orbit)
	elif btn_x_32.isChecked():
		xnum2_4.setText( str( round((max_orbit),2) ) )
	## orbit P (year)
	elif btn_x_42.isChecked():
		xnum2_4.setText( str( round(max_year*8760,2) ) )
	## dis to us
	elif btn_x_52.isChecked():
		xnum2_4.setText( str( max_dis ) )

	xnum2_4.setCenter(Vector2( 0.9 * graph2.getWidth(), graph2.getHeight() + 20  ))
	xnum2_4.setFont('fonts/helvetica.ttf 30')
	xnum2_4.setAutosize(False)
	xnum2_4.setColor(Color('white'))

	## draw numbers on y axis
	### 0.1 min
	ynum2_1 = Label.create(graph2)
	## mass
	if btn_y_12.isChecked():
		ynum2_1.setText( str( round((min_mass),2) ) )
	## radius
	elif btn_y_22.isChecked():
		ynum2_1.setText( str( round((min_size),2) ) )
	## orbit R (orbit)
	elif btn_y_32.isChecked():
		ynum2_1.setText( str( round((min_orbit),2) ) )
	## orbit P (year)
	elif btn_y_42.isChecked():
		ynum2_1.setText( str( round(min_year*8760,2) ) )
	## dis to us
	elif btn_y_52.isChecked():
		ynum2_1.setText( str( min_dis ) )

	ynum2_1.setCenter(Vector2(-25,0.9 * graph2.getHeight()))
	ynum2_1.setFont('fonts/helvetica.ttf 30')
	ynum2_1.setColor(Color('white'))
	ynum2_1.setAutosize(False)
	ynum2_1.setRotation(-90)

	### 0.1 + 0.8/3
	ynum2_2 = Label.create(graph2)

	## mass
	if btn_y_12.isChecked():
		if max_mass>0:
			ynum2_2.setText( str( round(math.pow(10, math.log10((max_mass)) * (miny+(1-miny)/3.0) ),2) ) )
		else:
			ynum2_2.setText('0.0')
	## radius
	elif btn_y_22.isChecked():
		if max_size>0:
			ynum2_2.setText( str( round(math.pow(10, math.log10((max_size)) * (miny+(1-miny)/3.0) ),2) ) )
		else:
			ynum2_2.setText('0.0')
	## orbit R (orbit)
	elif btn_y_32.isChecked():
		if max_orbit>0:
			ynum2_2.setText( str( round(math.pow(10, math.log10((max_orbit)) * (miny+(1-miny)/3.0) ),2) ) )
		else:
			ynum2_2.setText('0.0')
	## orbit P (year)
	elif btn_y_42.isChecked():
		ynum2_2.setText( str( round(math.pow(10, max_year*8760.0 * (miny+(1-miny)/3.0) ),2) ) )
	## dis to us
	elif btn_y_52.isChecked():
		ynum2_2.setText( str( round(math.pow(10, max_dis* (miny+(1-miny)/3.0) ),2) ) )

	ynum2_2.setCenter(Vector2( -25,(0.9-0.8/3) * graph2.getHeight() ))
	ynum2_2.setFont('fonts/helvetica.ttf 30')
	ynum2_2.setAutosize(False)
	ynum2_2.setColor(Color('white'))
	ynum2_2.setRotation(-90)

	### 0.9 - 0.8/3
	ynum2_3 = Label.create(graph2)

	## mass
	if btn_y_12.isChecked():
		if max_mass>0:
			ynum2_3.setText( str( round(math.pow(10, math.log10((max_mass))*(miny+2.0*(1-miny)/3.0) ),2) ) )
		else:
			ynum2_3.setText('0.0')
	## radius
	elif btn_y_22.isChecked():
		if max_size>0:
			ynum2_3.setText( str( round(math.pow(10, math.log10((max_size))*(miny+2.0*(1-miny)/3.0)),2) ) )
		else:
			ynum2_3.setText('0.0')
	## orbit R (orbit)
	elif btn_y_32.isChecked():
		if max_orbit>0:
			ynum2_3.setText( str( round(math.pow(10, math.log10((max_orbit))*(miny+2.0*(1-miny)/3.0)),2) ) )
		else:
			ynum2_3.setText('0.0')
	## orbit P (year)
	elif btn_y_42.isChecked():
		ynum2_3.setText( str( round(math.pow(10, max_year*8760.0*(miny+2.0*(1-miny)/3.0) ),2) ) )
	## dis to us
	elif btn_y_52.isChecked():
		ynum2_3.setText( str( round(math.pow(10, max_dis*(miny+2.0*(1-miny)/3.0) ),2) ) )

	ynum2_3.setCenter(Vector2( -25,(0.1+0.8/3) * graph2.getHeight() ))
	ynum2_3.setFont('fonts/helvetica.ttf 30')
	ynum2_3.setColor(Color('white'))
	ynum2_3.setAutosize(False)
	ynum2_3.setRotation(-90)

	### 0.9 max
	ynum2_4 = Label.create(graph2)

	## mass
	if btn_y_12.isChecked():
		ynum2_4.setText( str( round((max_mass),2) ) )
	## radius
	elif btn_y_22.isChecked():
		ynum2_4.setText( str( round((max_size),2) ) )
	## orbit R (orbit)
	elif btn_y_32.isChecked():
		ynum2_4.setText( str( round((max_orbit),2) ) )
	## orbit P (year)
	elif btn_y_42.isChecked():
		ynum2_4.setText( str( round(max_year*8760,2) ) )
	## dis to us
	elif btn_y_52.isChecked():
		ynum2_4.setText( str( max_dis ) )

	ynum2_4.setCenter(Vector2( -25, 0.1 * graph2.getHeight()))
	ynum2_4.setFont('fonts/helvetica.ttf 30')
	ynum2_4.setColor(Color('white'))
	ynum2_4.setAutosize(False)
	ynum2_4.setRotation(-90)

	print 'done'

updateGraph()
updateGraph2()

def showInfoForDot(dot):
	global g_showInfo

	g_showInfo = True

	if dot.getSys()._hasInfo_s:
		legend_s.setData(loadImage('pic_s/'+dot.getSys()._name.replace(' ','_')+'.png'))
		legend_s.setSize(legend_s.getSize()*1.5)
	else:
		legend_s.setData(loadImage('pic_s/no_info.png'))
	if dot.getSys()._hasInfo_p:
		legend_p.setData(loadImage('pic_p/'+dot.getSys()._name.replace(' ','_')+'.png'))
		legend_p.setSize(legend_p.getSize()*1.5)
	else:
		legend_p.setData(loadImage('pic_p/no_info.png'))
	legend_s.setVisible(True)
	legend_p.setVisible(True)
	legend_s.setPosition(Vector2(15100,0))
	legend_p.setPosition(Vector2(15000 - legend_p.getSize()[0],800))

	print 'done loading image'

##############################################################################################################
# EVENT FUNCTION

laser = Image.create(ui.getUi())
laser.setData(loadImage('pointer.png'))
laser.setCenter(Vector2(25000,100))
laser.setSize(Vector2(128,128))
laser.setVisible(True)

def onEvent():
	global g_scale_size
	global g_scale_dist
	global g_scale_time

	global g_reorder
	global g_moveToCenter

	global pointer

	global isButton7down
	global wandOldPos
	global wandOldOri

	global num_reorder
	global box_reorder

	global sn_smallMulti

	global li_textUniv

	global text_univ_highlight

	global g_curOrder

	global g_curCenSys

	global g_showInfo
	global g_showNews

	global g_cur_highlight_box
	global g_cur_highlight_box_blue

	global g_cur_highlight_i
	global g_cur_highlight_i_blue

	global laser

	global li_dotOnWall

	e = getEvent()

	if e.getServiceType()==ServiceType.Wand:
		wandPos = e.getPosition()
		wandOri = e.getOrientation()
		refVec = Vector3(0.0, 0.0, -1.0)
		v = wandOri*refVec

		loc = CoordinateCalculator()
		loc.set_position(wandPos.x, wandPos.y, wandPos.z)
		loc.set_orientation(v.x, v.y, v.z)
		loc.calculate()
		twod_x = int(loc.get_x() * 24588)
		twod_y = int(loc.get_y() *  3072)

		#laser.setCenter(Vector2(twod_x,twod_y))

		if container_g1.hitTest(Vector2(twod_x,twod_y)):
			laser.setCenter(Vector2(twod_x,twod_y))
			for i in xrange(len(li_dotOnWall)):
				dot = li_dotOnWall[i]
				if dot.getImage()!=None:					
					dot.getImage().setScale(1)
					if dot.getImage().hitTest(Vector2(twod_x, twod_y)):
						dot.getImage().setScale(2)
						# show info
						if e.isButtonDown(EventFlags.Button2):
							showInfoForDot(dot)
							e.setProcessed()
							return None
						# highlight and bring to center
						elif e.isButtonDown(EventFlags.Button3):
							for node, sys in dic_boxToSys.iteritems():
								if sys == dot.getSys():
									highlight_box(node,True)
									addCenter(1.3,sys)
									e.setProcessed()
									return None						

			e.setProcessed()
			return None
		else:
			laser.setCenter(Vector2(25000,0))

		if container_g2.hitTest(Vector2(twod_x,twod_y)):
			laser.setCenter(Vector2(twod_x,twod_y))
			for i in xrange(len(li_dotOnWall2)):
				dot = li_dotOnWall2[i]
				if dot.getImage()!=None:
					dot.getImage().setScale(1)
					if dot.getImage().hitTest(Vector2(twod_x, twod_y)):
						dot.getImage().setScale(2)
						# show info
						if e.isButtonDown(EventFlags.Button2):
							showInfoForDot(dot)
							e.setProcessed()
							return None
						# highlight and bring to center
						elif e.isButtonDown(EventFlags.Button3):
							for node, sys in dic_boxToSys.iteritems():
								if sys == dot.getSys():
									highlight_box(node,True)
									addCenter(1.3,sys)
									e.setProcessed()
									return None						

			e.setProcessed()
			return None
		else:
			laser.setCenter(Vector2(25000,0))

	## normal operations
	if g_reorder==0 and g_moveToCenter==0 and g_showInfo==False and g_showNews==False:
		#print 'normal operation'
		if e.isButtonDown(EventFlags.ButtonLeft) or e.isKeyDown(ord('j')):
			#print 'start dist -'
			if not changeScale('dist',False):
				playSound(sd_warn, e.getPosition(), 0.5)
		elif e.isButtonDown(EventFlags.ButtonRight) or e.isKeyDown(ord('l')):
			#print 'start dist +'
			if not changeScale('dist',True):
				playSound(sd_warn, e.getPosition(), 0.5)
		elif e.isButtonDown(EventFlags.ButtonUp) or e.isKeyDown(ord('i')):
			#print 'start size +'
			if not changeScale('size',True):
				playSound(sd_warn, e.getPosition(), 0.5)
		elif e.isButtonDown(EventFlags.ButtonDown) or e.isKeyDown(ord('k')):
			#print 'start size -'
			if not changeScale('size',False):
				playSound(sd_warn, e.getPosition(), 0.5)
		elif e.isKeyDown(ord('u')):
			#print 'start time -'
			if not changeScale('time',False):
				playSound(sd_warn, e.getPosition(), 0.5)
		elif e.isKeyDown(ord('o')):
			#print 'start time +'
			if not changeScale('time',True):
				playSound(sd_warn, e.getPosition(), 0.5)

		## navigation
		elif (e.isButtonDown(EventFlags.Button7)):
			if isButton7down==False:
				isButton7down = True
				wandOldPos = e.getPosition()
				wandOldOri = e.getOrientation()
				#print "wandOldPos:",wandOldPos
				#print "wandOldOri:",wandOldOri
		elif (e.isButtonUp(EventFlags.Button7)):
			isButton7down = False
		elif e.getServiceType() == ServiceType.Wand:
			if isButton7down:
				#print 'button7isdown'
				trans = e.getPosition()-wandOldPos
				#cam.setPosition( cam.convertLocalToWorldPosition( trans*cam.getController().getSpeed() ) )
				cam.translate( trans*cam.getController().getSpeed(), Space.Local)
				oriVecOld = quaternionToEuler(wandOldOri)
				oriVec = quaternionToEuler(e.getOrientation())
				cam.rotate( oriVec-oriVecOld, 2*math.pi/180, Space.Local )

	elif g_showInfo:
		#print 'showing info'
		if e.isButtonDown(EventFlags.Button3) or e.isButtonDown(EventFlags.Button2):
			legend_p.setVisible(False)
			legend_s.setVisible(False)
			g_showInfo=False

	elif g_showNews:
		#print 'showing news'
		if e.isButtonDown(EventFlags.Button3) or e.isButtonDown(EventFlags.Button2):
			#print 'here'
			legend_p.setVisible(False)
			legend_s.setVisible(False)
			g_showNews=False
		elif e.isButtonDown(EventFlags.ButtonUp):
			#print 'here11'
			pos = legend_s.getPosition()
			#print pos
			legend_s.setPosition(Vector2(pos[0],pos[1]+100))
			#print legend_s.getPosition()
			e.setProcessed()
		elif e.isButtonDown(EventFlags.ButtonDown):
			#print 'here22'
			pos = legend_s.getPosition()
			#print pos
			legend_s.setPosition(Vector2(pos[0],pos[1]-100))
			#print legend_s.getPosition()
			e.setProcessed()

	## move to center
	elif g_moveToCenter==1:
		if e.isButtonDown(EventFlags.Button3):
			e.setProcessed()
			g_moveToCenter=0
			pointer.setVisible(False)
			playSound(sd_mtc_quit, cam.getPosition(), 0.5)
			print ('quit move to center mode')
			# quit highlight
			highlight_box(g_cur_highlight_box,False)
			g_cur_highlight_box = None
		else:
			r = getRayFromEvent(e)
			for i in xrange(c_SMALLMULTI_NUMBER):
				node = li_boxOnWall[i]
				hitData = hitNode(node, r[1], r[2])
				if hitData[0]:
					if node!=g_cur_highlight_box:
						# print '\n'
						# print 'node != g_cur_highlight_box: node:',node,'g_cur: ',g_cur_highlight_box
						# print 'node name:',node.getParent().getName()
						# if g_cur_highlight_box!=None:
						# 	print 'g_cur name:',g_cur_highlight_box.getParent().getName()
						highlight_box(node,True)
						highlight_box(g_cur_highlight_box,False)
						g_cur_highlight_box=node
						print 'change'
						# print 'node',node
						# print 'g_cur_highlight_box',g_cur_highlight_box
						# print 'node name:',node.getParent().getName()
						# if g_cur_highlight_box!=None:
						# 	print 'g_cur name:',g_cur_highlight_box.getParent().getName()
						# print '\n'
					pointer.setPosition(hitData[1])
					if e.isButtonDown(EventFlags.Button2):
						e.setProcessed()
						if dic_boxToSys[node]!=None:
							if text_univ_highlight!=None:
								text_univ_highlight.setColor(Color('white'))
							li_textUniv[i].setColor(Color('red'))
							text_univ_highlight = li_textUniv[i]
							addCenter(1.3,dic_boxToSys[node])
							g_curCenSys = dic_boxToSys[node]
							pointer.setVisible(False)
							g_moveToCenter=0
							playSound(sd_mtc_moving, cam.getPosition(), 0.5)
							# quit highlight
							highlight_box(g_cur_highlight_box,False)
							g_cur_highlight_box = None
					break

	## choose to reorder
	elif g_reorder==1:
		# quit reorder mode
		if e.isButtonDown(EventFlags.Button3):
			e.setProcessed()
			g_reorder=0
			pointer.setVisible(False)
			playSound(sd_reo_quit, cam.getPosition(), 0.5)
			if g_cur_highlight_i != -100:
				highlight_box(sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[g_cur_highlight_i])).getChildByName('boxParent'+str(g_curOrder[g_cur_highlight_i])).getChildByIndex(0),False)
				g_cur_highlight_i=-100
			if g_cur_highlight_i_blue != -100:
				highlight_box(sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[g_cur_highlight_i_blue])).getChildByName('boxParent'+str(g_curOrder[g_cur_highlight_i_blue])).getChildByIndex(0),False)
				g_cur_highlight_i_blue=-100
			print 'quit reorder mode'
			# quit highlight
		else:
			r = getRayFromEvent(e)
			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[i]))
				node = sn_smallTrans.getChildByName('boxParent'+str(g_curOrder[i])).getChildByIndex(0)
				hitData = hitNode(node, r[1], r[2])
				if hitData[0]==True:
					if i!=g_cur_highlight_i: #if g_cur_highlight_box==None or node.getParent()!=g_cur_highlight_box.getParent():
						highlight_box(node,True)
						if g_cur_highlight_i!=-100:
							highlight_box(sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[g_cur_highlight_i])).getChildByName('boxParent'+str(g_curOrder[g_cur_highlight_i])).getChildByIndex(0),False)#final_highlight_box(g_cur_highlight_box,False)
						g_cur_highlight_i=i # g_cur_highlight_box = node
					pointer.setPosition(hitData[1])
					# select a box
					if e.isButtonDown(EventFlags.Button2):
						e.setProcessed()
						g_reorder=2
						highlight_box_blue(node,True)
						g_cur_highlight_i_blue = i
						print 'box color changed to BLUE'
						num_reorder = i # record this node's order
						box_reorder = node # record this node
						playSound(sd_reo_selected, cam.getPosition(), 0.5)
					break

	## move to reorder
	elif g_reorder==2:
		# cancel selection
		if e.isButtonDown(EventFlags.Button3):
			e.setProcessed()
			g_reorder=1
			playSound(sd_reo_canceled, cam.getPosition(), 0.5)
 			print ('cenceled')
 			# quit highlight blue
 			highlight_box_blue(sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[g_cur_highlight_i_blue])).getChildByName('boxParent'+str(g_curOrder[g_cur_highlight_i_blue])).getChildByIndex(0),False)
			g_cur_highlight_i_blue = -100
			print 'BLUE CANCELED'
 		else:
			r = getRayFromEvent(e)
			for i in xrange(sn_smallMulti.numChildren()):
				sn_smallTrans = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[i]))
				node = sn_smallTrans.getChildByName('boxParent'+str(g_curOrder[i])).getChildByIndex(0)
				hitData = hitNode(node, r[1], r[2])
				if hitData[0]:
					if i!=g_cur_highlight_i and i!=g_cur_highlight_i_blue:#if node!=g_cur_highlight_box and node!=g_cur_highlight_box_blue:
						highlight_box(node,True)
						if g_cur_highlight_i!=-100 and g_cur_highlight_i!=g_cur_highlight_i_blue:
							highlight_box(sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[g_cur_highlight_i])).getChildByName('boxParent'+str(g_curOrder[g_cur_highlight_i])).getChildByIndex(0),False)
						g_cur_highlight_i=i
						print 'RED CHANGED'
					pointer.setPosition(hitData[1])
			 		# select another box
			 		if e.isButtonDown(EventFlags.Button2):
			 			e.setProcessed()
			 			if i != num_reorder:
			 				#node.setEffect('colored -e #3274cc44') # change color to mark it
			 				curPos = sn_smallTrans.getPosition()
			 				curOri = sn_smallTrans.getOrientation()
			 				if i<num_reorder:
			 					for j in xrange(i,num_reorder):
			 						n = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[j]))
			 						n1 = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[j+1]))
			 						n.setPosition(n1.getPosition())
			 						n.setOrientation(n1.getOrientation())
			 					n = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[num_reorder]))
			 					n.setPosition(curPos)
			 					n.setOrientation(curOri)

			 					# update g_curOrder
			 					tmpNum = g_curOrder[num_reorder]
			 					j = num_reorder
		 						while j>i:
		 							g_curOrder[j]=g_curOrder[j-1]
		 							j-=1
		 						g_curOrder[i]=tmpNum

			 				else: # num_reorder<i
			 					j = i
			 					while j>num_reorder:
			 						n = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[j]))
			 						n1 = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[j-1]))
			 						n.setPosition(n1.getPosition())
			 						n.setOrientation(n1.getOrientation())
			 						j-=1
			 					n = sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[num_reorder]))
			 					n.setPosition(curPos)
			 					n.setOrientation(curOri)

			 					#update g_curOrder
			 					tmpNum = g_curOrder[num_reorder]
			 					for j in xrange(num_reorder,i):
			 						g_curOrder[j]=g_curOrder[j+1]
			 					g_curOrder[i]=tmpNum
			 					for j in xrange(c_SMALLMULTI_NUMBER):
			 						print 'g_curOrder['+str(j)+']:',g_curOrder[j]
			 				playSound(sd_reo_done, cam.getPosition(), 0.5)
			 				g_reorder=1
			 				# quit highlight
			 				highlight_box_blue(sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[g_cur_highlight_i_blue])).getChildByName('boxParent'+str(g_curOrder[g_cur_highlight_i_blue])).getChildByIndex(0),False)
			 				g_cur_highlight_i_blue = -100
			 				print 'BLUE CANCELED'
			 				highlight_box(sn_smallMulti.getChildByName('smallTrans'+str(g_curOrder[g_cur_highlight_i])).getChildByName('boxParent'+str(g_curOrder[g_cur_highlight_i])).getChildByIndex(0),False)
			 				g_cur_highlight_i = -100
			 				print 'RED CANCELED'
			 		break

		# for node in li_boxOnWall:
		# 	hitData = hitNode(node, r[1], r[2])
		# 	if hitData[0]:
		# 		pointer.setPosition(hitData[1])
		# 		if e.isButtonDown(EventFlags.Button3):
		# 			e.setProcessed()
		# 			g_reorder=1
		#			box_reorder.setEffect('colored -e #01b2f144') # restore original color
		# 			playSound(sd_reo_canceled, cam.getPosition(), 0.5)
		# 			playSound(sd_reo_please, cam.getPosition(), 0.5)
		# 		elif e.isButtonDown(EventFlags.Button2):
		# 			if node != box_reorder:

		# 	break

setEventFunction(onEvent)

##############################################################################################################
# UPDATE FUNCTION

def onUpdate(frame, t, dt):
	global g_orbit
	global g_rot
	global g_scale_time

	global bgmDeltaT

	# ALL THINGS IN 3D ROTATE AS TIME PASSES BY
	for o,y in g_orbit:
		#i[0].yaw(dt/40*g_scale_time*(1.0/i[1])
		o.yaw(dt/40*g_scale_time*(1.0/y))
	for o,d in g_rot:
		#i[0].yaw(dt/40*g_scale_time*365*(1.0/i[1]))
		o.yaw(dt/40*365*g_scale_time*(1.0/d))

	for o,y in g_cen_orbit:
		#i[0].yaw(dt/40*g_scale_time*(1.0/i[1])
		if y==0:
			continue
		o.yaw(dt/40*g_scale_time*(1.0/y))
	for o,d in g_cen_rot:
		#i[0].yaw(dt/40*g_scale_time*365*(1.0/i[1]))
		if d==0:
			continue
		o.yaw(dt/40*365*g_scale_time*(1.0/d))

	# 3d universe
	sn_univParent.yaw(dt/20)

	# replay bgm
	if t-bgmDeltaT>=68:
		print "replaying bgm"
		bgmDeltaT = t
		playSound(sd_bgm,InitCamPos,0.05)

setUpdateFunction(onUpdate)