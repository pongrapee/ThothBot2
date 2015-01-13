# -*- coding: utf-8 -*-
# coding='utf-8'

global debug
debug=0

from datetime import *
import re

global DayOfWeekListExactMatch
global DayOfWeekListSubstrMatch
global DayOfWeekListRegEx
global MonthOfYearListExactMatch
global MonthOfYearListSubstrMatch
global MonthOfYearListRegEx

global dateformat 
dateformat = "%Y-%m-%d %H:%M:%S"
global dateonlyformat 
dateonlyformat = "%Y-%m-%d"
global timeonlyformat
timeonlyformat = "%H:%M:%S"

def addmonths(date,months,favorEoM): 
	try: 
		if debug:
			print "months ",
			print months
		targetdate = date
		targetmonths = months+targetdate.month 
		if targetmonths%12 == 0:
			# Month must be between 1 and 12 so a modulo remainder of 0 = 12
			targetmonth = 12
		else:
			targetmonth = targetmonths%12
		if debug:
			print "targetmonth ",
			print targetmonth
		if favorEoM == True:
			# Favor matching an End of Month date to an End of Month offset date.
			testdate = date+timedelta(days=1)
			if testdate.day == 1:
				# input date was a last day of month and end of month is favored, so
				# go to the FIRST of the month AFTER, then go back one day.
				targetdate.replace(year=targetdate.year+int((targetmonths+1)/12),month=(targetmonth%12+1),day=1)
				targetdate+=timedelta(days=-1)
			else:
				targetdate.replace(year=targetdate.year+int(targetmonths/12),month=(targetmonth))
		else:
			# Do not favor matching an End of Month date to the offset End of Month.
			targetdate.replace(year=targetdate.year+int(targetmonths/12),month=(targetmonth))
		if debug:
			print "targetdate ",	
			print targetdate
		return targetdate
	except Exception as e:
		# There is an exception if the day of the month we're in does not exist in the target month
		# Go to the FIRST of the month AFTER, then go back one day.
		targetdate.replace(year=targetdate.year+int((targetmonths+1)/12),month=(targetmonth%12+1),day=1)
		targetdate+=timedelta(days=-1) 
		if debug:
			print "targetdate ",	
			print targetdate
		return targetdate

def minusmonths(date,months,favorEoM): 
	try: 
		if debug:
			print "months ",
			print months
		targetdate = date
		if debug:
			print targetdate.month 
		if targetdate.month - months > 0:
			targetmonths = targetdate.month - months
			if targetmonths%12 == 0:
				# Month must be between 1 and 12 so a modulo remainder of 0 = 12
				targetmonth = 12
			else:
				targetmonth = targetmonths%12
		else:
			targetmonths = (months+12)-targetdate.month
			if (targetdate.month - months)%12 == 0:
				# Month must be between 1 and 12 so a modulo remainder of 0 = 12
				targetmonth = 12
			else:
				targetmonth = (targetdate.month - months)%12
		if debug:
			print "targetmonths ",
			print targetmonths		
			print "targetmonth ",
			print targetmonth
		if favorEoM == True:
			# Favor matching an End of Month date to an End of Month offset date.
			testdate = date+timedelta(days=1)
			if testdate.day == 1:
				# input date was a last day of month and end of month is favored, so
				# go to the FIRST of the month AFTER, then go back one day.
				targetdate = targetdate.replace(year=targetdate.year-int((targetmonths-1)/12),month=(targetmonth%12+1),day=1)
				targetdate+=timedelta(days=-1)
			else:
				targetdate = targetdate.replace(year=targetdate.year-int(targetmonths/12),month=(targetmonth))
		else:
			# Do not favor matching an End of Month date to the offset End of Month.
			targetdate = targetdate.replace(year=targetdate.year-int(targetmonths/12),month=(targetmonth))
		if debug:
			print "targetdate ",	
			print targetdate
		return targetdate
	except Exception as e:
		# There is an exception if the day of the month we're in does not exist in the target month
		# Go to the FIRST of the month AFTER, then go back one day.
		targetdate.replace(year=targetdate.year+int((targetmonths+1)/12),month=(targetmonth%12+1),day=1)
		targetdate+=timedelta(days=-1) 
		if debug:
			print "targetdate ",	
			print targetdate
		return targetdate

		
def printkeyvallist (list):
	for k, v in list.items():
		print str(k) + " = " + str(v)

def multisplit(s, seps):
	res = [s]
	for sep in seps:
		s, res = res, []
		for seq in s:
			res += seq.split(sep)
	res = filter(None, res)
	return res

ThaiNumList = {"๐":0, "๑":1, "๒":2, "๓":3, "๔":4, "๕":5, "๖":6, "๗":7, "๘":8, "๙":9}

def ConvertFromThaiNum (input):
	input = input.decode('utf-8')
	input = input.replace(u"๑", str(1))
	input = input.replace(u"๒", str(2))
	input = input.replace(u"๓", str(3))
	input = input.replace(u"๔", str(4))
	input = input.replace(u"๕", str(5))
	input = input.replace(u"๖", str(6))
	input = input.replace(u"๗", str(7))
	input = input.replace(u"๘", str(8))
	input = input.replace(u"๙", str(9))
	input = input.replace(u"๐", str(0))
	return input.encode('utf-8')
	
def ConvertToThaiNum (input):
	input = input.decode('utf-8')
	input = input.replace(str(1),u"๑")
	input = input.replace(str(2),u"๒")
	input = input.replace(str(3),u"๓")
	input = input.replace(str(4),u"๔")
	input = input.replace(str(5),u"๕")
	input = input.replace(str(6),u"๖")
	input = input.replace(str(7),u"๗")
	input = input.replace(str(8),u"๘")
	input = input.replace(str(9),u"๙")
	input = input.replace(str(0),u"๐")
	return input.encode('utf-8')

#format "Key":{value, exactly_match_only?}
#exact_match_only should be used for short entry to prevent "T" to match every input with "T"

DayOfWeekListExactMatch = {
	"M":1,
	"T":2,
	"W":3,
	"TH":4,
	"F":5,
	"S":6,
	"SU":7,
	
	"จ":1,
	"อ":2,
	"พ":3,
	"พฤ":4,
	"ศ":5,
	"ส":6,
	"อา":7,
	
	"จ.":1,
	"อ.":2,
	"พ.":3,
	"พฤ.":4,
	"ศ.":5,
	"ส.":6,
	"อา.":7
}
	
DayOfWeekListSubstrMatch = {

	"MONDAY":1,
	"TUESDAY":2,
	"WEDNESDAY":3,
	"THURSDAY":4,
	"FRIDAY":5,
	"SATURDAY":6,
	"SUNDAY":7,
	
	"MON":1,
	"TUE":2,
	"WED":3,
	"THU":4,
	"FRI":5,
	"SAT":6,
	"SUN":7,
	
	"วันจันทร์":1,
	"วันอังคาร":2,
	"วันพุธ":3,
	"วันพฤหัสบดี":4,
	"วันพฤหัส":4,
	"วันศุกร์":5,
	"วันเสาร์":6,
	"วันอาทิตย์":7,
	
	"จันทร์":1,
	"อังคาร":2,
	"พุธ":3,
	"พฤหัสบดี":4,
	"พฤหัส":4,
	"ศุกร์":5,
	"เสาร์":6,
	"อาทิตย์":7
}
	
MonthOfYearListExactMatch = {
	"มค":1,
	"กพ":2,
	"มีค":3,
	"เมย":4,
	"พค":5,
	"มิย":6,
	"กค":7,
	"สค":8,
	"กย":9,
	"ตค":10,
	"พย":11,
	"ธค":12,
	
	"ม.ค.":1,
	"ก.พ.":2,
	"มี.ค.":3, 
	"เม.ย.":4,
	"พ.ค.":5,
	"มิ.ย.":6,
	"ก.ค.":7,
	"ส.ค.":8,
	"ก.ย.":9,
	"ต.ค.":10,
	"พ.ย.":11,
	"ธ.ค.":12,
	
	"มค.":1,
	"กพ.":2,
	"มีค.":3,
	"เมย.":4,
	"พค.":5,
	"มิย.":6,
	"กค.":7,
	"สค.":8,
	"กย.":9,
	"ตค.":10,
	"พย.":11,
	"ธค.":12,
	
	"๑":1,
	"๒":2,
	"๓":3,
	"๔":4,
	"๕":5,
	"๖":6,
	"๗":7,
	"๘":8,
	"๙":9,
	"๑๐":10,
	"๑๑":11,
	"๑๒":12,
	
	"เดือน ๑":1,
	"เดือน ๒":2,
	"เดือน ๓":3,
	"เดือน ๔":4,
	"เดือน ๕":5,
	"เดือน ๖":6,
	"เดือน ๗":7,
	"เดือน ๘":8,
	"เดือน ๙":9,
	"เดือน ๑๐":10,
	"เดือน ๑๑":11,
	"เดือน ๑๒":12,
	
	"๐๑":1,
	"๐๒":2,
	"๐๓":3,
	"๐๔":4,
	"๐๕":5,
	"๐๖":6,
	"๐๗":7,
	"๐๘":8,
	"๐๙":9
}
	
MonthOfYearListSubstrMatch = {
	"JANUARY":1,
	"FEBRUARY":2,
	"MARCH":3,
	"APRIL":4,
	"MAY":5,
	"JUNE":6,
	"JULY":7,
	"AUGUST":8,
	"SEPTEMBER":9,
	"OCTOBER":10,
	"NOVEMBER":11,
	"DECEMBER":12,
	
	"JAN":1,
	"FEB":2,
	"MAR":3,
	"APR":4,
	"MAY":5,
	"JUN":6,
	"JUL":7,
	"AUG":8,
	"SEP":9,
	"OCT":10,
	"NOV":11,
	"DEC":12,
	
	"มกราคม":1,
	"กุมภาพันธ์":2,
	"มีนาคม":3,
	"เมษายน":4,
	"พฤษภาคม":5,
	"มิถุนายน":6,
	"กรกฎาคม":7,
	"สิงหาคม":8,
	"กันยายน":9,
	"ตุลาคม":10,
	"พฤศจิกายน":11,
	"ธันวาคม":12,
	
	"มกรา":1,
	"กุมภา":2,
	"มีนา":3,
	"เมษา":4,
	"พฤษภา":5,
	"มิถุนา":6,
	"กรกฎา":7,
	"สิงหา":8,
	"กันยา":9,
	"ตุลา":10,
	"พฤศจิกา":11,
	"พฤศจิ":11,
	"ธันวา":12
}

DeltaDayListExact = {
	"วันนี้":0, 
	"TODAY":0,
	
	"เมื่อวานนี้":1,
	"เมื่อวาน":1, 
	"วานนี้":1,
	"YESTERDAY":1,
	"DAY BEFORE":1, 
	
	"วันถัดไป":1,
	"พรุ่งนี้":-1, 
	"วันพรุ่งนี้":-1, 
	"TOMORROW":-1,
	"NEXT DAY":1
}

DeltaMonthListExact = {
	"เดือนนี้":0, 
	"THIS MONTH":0,
	
	"LAST MONTH":1, 
	"PREVIOUS MONTH":1, 
	"PRIOR MONTH":1, 
	"เดือนที่แล้ว":1, 
	
	"NEXT MONTH":1,
	"เดือนหน้า":1
}

DeltaYearListExact = {
	"ปีนี้":0, 
	"THIS YEAR":0,
	
	"LAST YEAR":1, 
	"PREVIOUS YEAR":1, 
	"PRIOR YEAR":1, 
	"ปีที่แล้ว":1, 
	
	"NEXT YEAR":1,
	"ปีหน้า":1
}

DeltaWeekListExact = {
	"อาทิตย์นี้":0, 
	"THIS WEEK":0,
	
	"LAST WEEK":1, 
	"PREVIOUS WEEK":1, 
	"PRIOR WEEK":1, 
	"อาทิตย์ที่แล้ว":1, 
	
	"NEXT WEEK":1,
	"อาทิตย์หน้า":1
}

DeltaHourListExact = {
	"ชั่วโมงนี้":0, 
	"THIS HOUR":0,
	
	"ชั่วโมง":1, 
	"HOUR":1,
	
	# "LAST HOUR":1, 
	# "PREVIOUS HOUR":1, 
	# "PRIOR HOUR":1, 
	# "ชั่วโมงที่แล้ว":1,
	
	# "NEXT HOUR":1,
	# "ชั่วโมงหน้า":1,
	# "ชั่วโมงต่อไป":1
}

DeltaMinuteListExact = {
	"นาทีนี้":0, 
	"THIS MINUTE":0,
	
	"นาที":1, 
	"MINUTE":1,
	
	# "LAST MINUTE":1, 
	# "PREVIOUS MINUTE":1,
	# "PRIOR MINUTE":1, 
	# "PAST MINUTE":1, 
	# "นาทีที่แล้ว":1, 
	
	# "NEXT HOUR":1,
	# "นาทีหน้า":1,
	# "นาทีต่อไป":1
}

DeltaSecondListExact = {
	"วินาทีนี้":0, 
	"THIS SECOND":0,
	
	"วินาที":1, 
	"SECOND":1,
	
	# "LAST SECOND":1, 
	# "PREVIOUS SECOND":1, 
	# "PRIOR SECOND":1, 
	# "PAST SECOND":1,
	# "วินาทีที่แล้ว":1, 
	
	# "NEXT SECOND":1,
	# "วินาทีหน้า":1,
	# "วินาทีต่อไป":1
}

def FindInList( mappedList=[], key="", exactmatch=1): 
#exactmatch 	0 = substring match allowed ("พุธที่แล้ว" can match with "พุธ" )
#				1 = exact match only
	key = str(key).upper()
	if exactmatch == 1:
		for (k, v) in (mappedList.items()):
			if str(k).upper() == key.upper():
				return v
	else:
		for (k, v) in (mappedList.items()):
			if str(k).upper() == key.upper():
				return v
		for (k, v) in (mappedList.items()):
			if key.find(str(k).upper()) != -1:
				return v			
	return None
	
def DateOfLastorNext( dateinput=1, timeinput=None, today=datetime.today(), returnAsStr=1 ):
	date = None
	indexint = -1
	
	hour = 0
	minute = 0
	second = 0
	
	timefound=0
	
	if timeinput != None and timeinput != str(None):
		timeinput2 = ConvertFromThaiNum (timeinput)
		PM = 0
		if timeinput2.upper().find("PM") != -1:
			PM = 12
		regex = re.compile(ur"(?P<HR>[0-9]*)[:\.](?P<MIN>[0-9]*)", re.I|re.U)
		matchres = regex.search( timeinput2.decode('utf-8') )
		if matchres:
			try:
				hour = int(matchres.group("HR"))
				if hour < 12:
					hour = hour + PM
				minute = int(matchres.group("MIN"))
				timefound=1
			except ValueError:
				pass
	
	if timeinput != None and timeinput != str(None):
		timeinput2 = ConvertFromThaiNum (timeinput)
		PM = 0
		if timeinput2.upper().find("PM") != -1:
			PM = 12
		regex = re.compile(ur"(?P<HR>[0-9]*)[:\.](?P<MIN>[0-9]*)[:\.](?P<SEC>[0-9]*)", re.I|re.U)
		matchres = regex.search( timeinput2.decode('utf-8') )
		if matchres:
			try:
				hour = int(matchres.group("HR"))
				if hour < 12:
					hour = hour + PM
				minute = int(matchres.group("MIN"))
				second = int(matchres.group("SEC"))
				timefound=1
			except ValueError:
				pass
	try:
		indexint = int( dateinput )       
	except ValueError:
		pass
	if indexint >=1 and indexint <=7: 
		#input index is int
		index=indexint
	else: 
		#assume dateinput index is string
		dateinput = str (dateinput).upper()
		index = FindInList( DayOfWeekListExactMatch, dateinput, exactmatch=1 )
		
		if index == None:
			index = FindInList( DayOfWeekListSubstrMatch, dateinput, exactmatch=0 )
			
	if index >=1 and index <=7:	
		index = index - 1 #in Python Monday is 0
		week = 0
		if (	index > today.weekday() or
				(index <= today.weekday() and (
				(str(dateinput).upper().find("ที่แล้ว") != -1 ) or 
				(str(dateinput).upper().find("ก่อน") != -1 ) or
				(str(dateinput).upper().find("ผ่าน") != -1 ) or
				(str(dateinput).upper().find("LAST") != -1 ) or
				(str(dateinput).upper().find("PREVIOUS") != -1 ) or
				(str(dateinput).upper().find("PRIOR") != -1 ) or
				(str(dateinput).upper().find("PAST") != -1 ) or
				(str(dateinput).upper().find("BEFORE") != -1 )))):
			#special case to deal with "พุธที่แล้ว", "อังคารที่แล้ว", "last monday" or days of week that is in last week time frame
			week = -1
		elif (	(str(dateinput).upper().find("หน้า") != -1 ) or 
				(str(dateinput).upper().find("ถัดไป") != -1 ) or
				(str(dateinput).upper().find("ต่อไป") != -1 ) or
				(str(dateinput).upper().find("จะมา") != -1 ) or
				(str(dateinput).upper().find("กำลังมา") != -1 ) or
				(str(dateinput).upper().find("NEXT") != -1 ) or
				(str(dateinput).upper().find("COMING") != -1 )):
			#special case to deal with "พุธที่แล้ว", "อังคารที่แล้ว", "last monday" or days of week that is in last week time frame
			week = +1
		date = today - timedelta(days=today.weekday()) + timedelta(days=index, weeks=week)
	
	if returnAsStr == 1 and date != None:
		if timefound==1:
			date = datetime.strptime( date.strftime(dateonlyformat) + " {0}:{1}:{2}".format(hour, minute,second), dateformat )
			return date.strftime(dateformat)
		else:
			date = datetime.strptime( date.strftime(dateonlyformat) + " 00:00:00", dateformat )
			return date.strftime(dateformat)
	else:
		return date

def DecodeYear( year, returnAsStr=1 ):
	convertyear = ConvertFromThaiNum( year )
	try:
		yearint = int( convertyear )       
	except ValueError:
		yearint=0
		
	if yearint > 2100: #พศ (i.e. 2556)
		yearint = yearint - 543 
	elif yearint > 200: #คศ (i.e. 2012)
		pass #this is what we want already
	elif yearint > 70: #short คศ  in 1900's(i.e. 99)
		yearint = yearint + 1900
	elif yearint > 30: #short พศ  in 2500's(i.e. 55)
		yearint = yearint + 2500 - 543
	else: #short คศ in 2000's
		yearint = yearint + 2000
	return yearint

		
def DecodeMonth( month, returnAsStr=1 ):
	indexint = -1
	index = None
	try:
		indexint = int( month )       
	except ValueError:
		pass
	if indexint >=1 and indexint <=12: 
		#input index is int
		index=indexint
	else: 
		#assume input index is string
		index=FindInList( MonthOfYearListExactMatch, month, exactmatch=1 )
		if index == None:
			index=FindInList( MonthOfYearListSubstrMatch, month, exactmatch=0 )
	if index >=1 and index <=12:
		if returnAsStr:
			return str(index)
		else:
			return index
	else:
		return None
		
def DecodeDate( dateinput, returnAsStr=1 ):
	dateinput = str(dateinput)
	convertdate = ConvertFromThaiNum ( dateinput )
	try:
		dateint = int( convertdate )       
	except ValueError:
		dateint=0
	return dateint

def DecodeRelative( input, listtocheck, regextomatch ):
	found = 0
	delta = FindInList( listtocheck, input, exactmatch=1 )
	if delta == None:
		regex = re.compile(regextomatch, re.I|re.U)
		matchres = regex.search( input.decode('utf-8') )
		if matchres:
			try:
				delta = int(matchres.group(1))
				found = 1
			except ValueError:
				delta = None
		if delta == None:
			delta = FindInList( listtocheck, input, exactmatch=0 )
			if delta == None:
				delta = 0
			else:
				found = 1
	else:	
		found = 1
	if found == 1:
		return delta
	else:
		return None
		
def DecodeSpecialTimeFormat ( dateinput=None, timeinput=None, today=datetime.now() ):
	
	hour = 0
	minute = 0
	second = 0
	
	timefound=0
	
	if timeinput != None and timeinput != str(None):
		timeinput2 = ConvertFromThaiNum (timeinput)
		PM = 0
		if timeinput2.upper().find("PM") != -1:
			PM = 12
		regex = re.compile(ur"(?P<HR>[0-9]*)[:\.](?P<MIN>[0-9]*)", re.I|re.U)
		matchres = regex.search( timeinput2.decode('utf-8') )
		if matchres:
			try:
				hour = int(matchres.group("HR"))
				if hour < 12:
					hour = hour + PM
				minute = int(matchres.group("MIN"))
				timefound=1
			except ValueError:
				pass
	
	if timeinput != None and timeinput != str(None):
		timeinput2 = ConvertFromThaiNum (timeinput)
		PM = 0
		if timeinput2.upper().find("PM") != -1:
			PM = 12
		regex = re.compile(ur"(?P<HR>[0-9]*)[:\.](?P<MIN>[0-9]*)[:\.](?P<SEC>[0-9]*)", re.I|re.U)
		matchres = regex.search( timeinput2.decode('utf-8') )
		if matchres:
			try:
				hour = int(matchres.group("HR"))
				if hour < 12:
					hour = hour + PM
				minute = int(matchres.group("MIN"))
				second = int(matchres.group("SEC"))
				timefound=1
			except ValueError:
				pass
	
	dateinput = str(dateinput).upper()
	direction = 1
	modifierfound = 0
	if 	(	(str(dateinput).upper().find("ก่อน") != -1) or
			(str(dateinput).upper().find("แล้ว") != -1) or
			(str(dateinput).upper().find("ผ่าน") != -1) or
			(str(dateinput).upper().find("AGO") != -1) or
			(str(dateinput).upper().find("LAST") != -1) or
			(str(dateinput).upper().find("PREVIOUS") != -1) or
			(str(dateinput).upper().find("PRIOR") != -1) or
			(str(dateinput).upper().find("PAST") != -1) or
			(str(dateinput).upper().find("BEFORE") != -1) 
		):
		modifierfound = 1
		direction = -1
	if 	(	(str(dateinput).upper().find("หน้า") != -1 ) or 
			(str(dateinput).upper().find("ถัดไป") != -1 ) or
			(str(dateinput).upper().find("ต่อไป") != -1 ) or
			(str(dateinput).upper().find("จะมา") != -1 ) or
			(str(dateinput).upper().find("กำลังมา") != -1 ) or
			(str(dateinput).upper().find("NEXT") != -1 ) or
			(str(dateinput).upper().find("COMING") != -1 ) or
			(str(dateinput).upper().find("AFTER") != -1 )
		):
		direction = 1
		modifierfound = 1

	if modifierfound == 0:
		 direction = -1
		
	found = 0
	finegrain = 0
	
	deltayears =  DecodeRelative( input=dateinput, listtocheck=DeltaYearListExact, regextomatch=ur"([0-9]*) (YEAR|ปี|YR)")
	if deltayears == None:
		deltayears = 0
	else:
		found = 1
	
	deltamonths =  DecodeRelative( input=dateinput, listtocheck=DeltaMonthListExact, regextomatch=ur"([0-9]*) (MONTH|เดือน|MTH)")
	if deltamonths == None:
		deltamonths = 0
	else:
		found = 1
	
	deltaweeks =  DecodeRelative( input=dateinput, listtocheck=DeltaWeekListExact, regextomatch=ur"([0-9]*) (WEEK|อาทิตย์|WK)")
	if deltaweeks == None:
		deltaweeks = 0
	else:
		found = 1
	
	deltadays =  DecodeRelative( input=dateinput, listtocheck=DeltaDayListExact, regextomatch=ur"([0-9]*) (DAY|วัน)")
	if deltadays == None:
		deltadays = 0
	else:
		found = 1
	
	deltahours =  DecodeRelative( input=dateinput, listtocheck=DeltaHourListExact, regextomatch=ur"([0-9]*) (ชั่วโมง|ชม|HOUR|HR)")
	if deltahours == None:
		deltahours = 0
	else:
		found = 1
		finegrain = 1
		
	#special case for "นาที / วินาที"
	specialinput= dateinput
	specialinput = specialinput.replace("วินาที", "seconds")
	deltaminutes =  DecodeRelative( input=specialinput, listtocheck=DeltaMinuteListExact, regextomatch=ur"([0-9]*) (นาที|MINUTE|MIN)")
	if deltaminutes == None:
		deltaminutes = 0
	else:
		found = 1
		finegrain = 1
	
	deltaseconds =  DecodeRelative( input=dateinput, listtocheck=DeltaSecondListExact, regextomatch=ur"([0-9]*) (วินาที|SECOND|SEC)")
	if deltaseconds == None:
		deltaseconds = 0
	else:
		found = 1
		finegrain = 1
	
	if ( found == 0 ):
		return None
	else:
		relativetime = today + timedelta( 
					weeks=(deltaweeks*direction),
					days=(deltadays*direction),
					hours=(deltahours*direction),
					minutes=(deltaminutes*direction),
					seconds=(deltaseconds*direction))

		if deltamonths > 0 : 
			#def addmonths(date,months,favorEoM): 
			if debug:
				print "==deltamonths=="
				print "original",
				print relativetime
			if direction > 0:
				relativetime = addmonths ( relativetime, deltamonths, True )
			else:
				relativetime = minusmonths ( relativetime, deltamonths, True )
			if debug:
				print "new",
				print relativetime
		if deltayears > 0 : 
			if direction > 0:
				relativetime = addmonths ( relativetime, deltayears*12, True )
			else:
				relativetime = minusmonths ( relativetime, deltayears*12, True )
		if timefound==1:
			date = datetime.strptime( relativetime.strftime(dateonlyformat) + " {0}:{1}:{2}".format(hour, minute,second), dateformat )
			return date.strftime(dateformat)
		else: 
			if finegrain:
				return relativetime.strftime(dateformat)
			else:
				date = datetime.strptime( relativetime.strftime(dateonlyformat) + " 00:00:00", dateformat )
				return date.strftime(dateformat)
					
def DecodeExactDate ( dateinput="", timeinput="", today=datetime.now(),preferreddateformat="D-M-Y"):	
	dateinput = str(dateinput).upper()
	finaldatetime=None
	
	hour = 0
	minute = 0
	second = 0
	
	timefound=0
	
	if timeinput != None and timeinput != str(None):
		timeinput2 = ConvertFromThaiNum (timeinput)
		PM = 0
		if timeinput2.upper().find("PM") != -1:
			PM = 12
		regex = re.compile(ur"(?P<HR>[0-9]*)[:\.](?P<MIN>[0-9]*)", re.I|re.U)
		matchres = regex.search( timeinput2.decode('utf-8') )
		if matchres:
			try:
				hour = int(matchres.group("HR"))
				if hour < 12:
					hour = hour + PM
				minute = int(matchres.group("MIN"))
				timefound=1
			except ValueError:
				pass
	
	if timeinput != None and timeinput != str(None):
		timeinput2 = ConvertFromThaiNum (timeinput)
		PM = 0
		if timeinput2.upper().find("PM") != -1:
			PM = 12
		regex = re.compile(ur"(?P<HR>[0-9]*)[:\.](?P<MIN>[0-9]*)[:\.](?P<SEC>[0-9]*)", re.I|re.U)
		matchres = regex.search( timeinput2.decode('utf-8') )
		if matchres:
			try:
				hour = int(matchres.group("HR"))
				if hour < 12:
					hour = hour + PM
				minute = int(matchres.group("MIN"))
				second = int(matchres.group("SEC"))
				timefound=1
			except ValueError:
				pass
	
	dateinput = str(dateinput).upper()
	dateinput = dateinput.decode('utf-8')
	dateinput = dateinput.replace(u"พ.ศ."," ")
	dateinput = dateinput.replace(u"พศ."," ")
	dateinput = dateinput.replace(u"พศ"," ")
	dateinput = dateinput.replace(u"ค.ศ."," ")
	dateinput = dateinput.replace(u"คศ."," ")
	dateinput = dateinput.replace(u"คศ"," ")
	dateinput = dateinput.encode('utf-8')
	
	dateraw = ""
	datedecode = None
	monthraw = ""
	monthdecode = None
	yearraw = ""
	yeardecode = None
	
	splitedtext = multisplit(dateinput, [" ","-","/","\\",","])
	if debug:
		print splitedtext
		
	if len (splitedtext) < 2:
		return finaldatetime
	
	formattotrylist = { 0:"D-M-Y", 1:"D-M-Y", 2:"M-D-Y", 3:"Y-M-D", 4:"D-M", 5:"M-D" }
	
	if debug:
		print "preferreddateformat = ",
		print preferreddateformat
	formattotrylist[0] = preferreddateformat
	
	currentyear = datetime.now().strftime("%Y")
	validfound = 0
	for i in range(len(formattotrylist.items())):
		if debug:
			print formattotrylist[i]
		for j in range(len(splitedtext)-1):
			currentdateformat = formattotrylist[i]
			if currentdateformat == "D-M-Y" and len (splitedtext) > 2 and j+2 < len (splitedtext):
				dateraw = splitedtext[j]
				monthraw = splitedtext[j+1]
				yearraw = splitedtext[j+2]
			elif currentdateformat == "M-D-Y" and len (splitedtext) > 2 and j+2 < len (splitedtext):
				monthraw = splitedtext[j]
				dateraw = splitedtext[j+1]
				yearraw = splitedtext[j+2]
			elif currentdateformat == "Y-M-D" and len (splitedtext) > 2 and j+2 < len (splitedtext):
				yearraw = splitedtext[j]
				monthraw = splitedtext[j+1]
				dateraw = splitedtext[j+2]
			elif currentdateformat == "D-M" and j+1 < len (splitedtext):
				yearraw = currentyear
				dateraw = splitedtext[j]
				monthraw = splitedtext[j+1]
			elif currentdateformat == "M-D" and j+1 < len (splitedtext):
				yearraw = currentyear
				monthraw = splitedtext[j]
				dateraw = splitedtext[j+1]
				
				
			yeardecode 	= DecodeYear ( yearraw, returnAsStr=0)
			monthdecode 	= DecodeMonth( monthraw, returnAsStr=0 )
			if monthdecode == None:
				monthdecode = 0
			datedecode	= DecodeDate  ( dateraw, returnAsStr=0 )
			
			if debug:
				print 
				print "DateFormat: " + currentdateformat
				print "Year: " + str(yearraw) + " = " + str(yeardecode)
				print "Month: " + str(monthraw) + " = " + str(monthdecode)
				print "Date: " + str(dateraw) + " = " + str(datedecode)
				print str(yeardecode) + "-" + str(monthdecode) + "-" + str(datedecode)

			if 	( 	int(datedecode) >= 1 and int(datedecode) <= 31 and
					int(monthdecode) >= 1 and int(monthdecode) <= 12 and
					int(yeardecode) >= 1 and int(yeardecode) <= 2100 ):
				
				if( (currentdateformat == "D-M" or currentdateformat == "M-D") and
					date(yeardecode, monthdecode, datedecode) > date.today() ):
					yeardecode -= 1
				
				if debug: 
					print "Valid DateTime"
				if timefound == 1:
					finaldatetime = datetime.strptime("{0}-{1}-{2} {3}:{4}:{5}".format(yeardecode, monthdecode, datedecode, hour, minute, second), dateformat)
				else:
					finaldatetime = datetime.strptime("{0}-{1}-{2} 00:00:00".format(yeardecode, monthdecode, datedecode), dateformat)
				
				validfound=1
				break
			else:
				if debug: 
					print "Invalid DateTime"
		if validfound == 1:
			break
	return str(finaldatetime)
	
def DecodeDateTime ( input=str(""), today=datetime.now(), preferreddateformat="" ):
	
	global debug
	
	input = str(input).upper()
	input = input.decode('utf-8')
	input = input.replace('&NBSP;',' ') #&nbsp;
	input = input.replace(u" "," ") #&nbsp
	input = input.encode('utf-8')
	
	if debug:
		print "DecodeDateTime input = " + str(input)
	dateinput = ""
	timeinput = ""
	found = 0
	
	input = str(input)
	dateinput = input
	
	if found == 0:
		regex = re.compile(ur"(?P<TIME>[0-9]+[:\.][0-9]+[:\.][0-9]*[ ]*(PM|AM)?)", re.I|re.U)
		matchres = regex.search( input.decode('utf-8') )
		if matchres:
			timeinput = matchres.group("TIME").encode('utf-8')
			dateinput = dateinput.decode('utf-8')
			dateinput = dateinput.replace(timeinput," ")
			dateinput = dateinput.encode('utf-8')
			if debug:
				print "Groups are"
				print matchres.groups()
			found = 3
	
	if found == 0:
		regex = re.compile(ur"(?P<TIME>[0-9]+[:\.][0-9]+[ ]*(PM|AM)?)", re.I|re.U)
		matchres = regex.search( input.decode('utf-8') )
		if matchres:
			timeinput = matchres.group("TIME").encode('utf-8')
			dateinput = dateinput.decode('utf-8')
			dateinput = dateinput.replace(timeinput," ")
			dateinput = dateinput.encode('utf-8')
			if debug:
				print "Groups are"
				print matchres.groups()
			found = 4
	
	if found == 0:
		dateinput = input
		timeinput = None
		found = 10
		
	if debug:	
		print "found = " + str(found)
		print "date is " + str(dateinput)
		print "time is " + str(timeinput)
	
	#remove st nd rd th from date input
	regex = re.compile(ur"(?P<ORDINAL>[0-9]+(ST|ND|RD|TH))", re.I|re.U)
	matchres = regex.search( input.decode('utf-8') )
	if matchres:
		tobereplace = matchres.group("ORDINAL").encode('utf-8')
		regex = re.compile(ur"(?P<NOORDINAL>[0-9]+)(ST|ND|RD|TH)", re.I|re.U)
		matchres = regex.search( input.decode('utf-8') )
		if matchres:
			replacewith = matchres.group("NOORDINAL").encode('utf-8')
			dateinput = dateinput.decode('utf-8')
			dateinput = dateinput.replace(tobereplace,replacewith)
			dateinput = dateinput.encode('utf-8')
	
	defaultdatetime = datetime.now().strftime(dateformat)
	exactdatetime = DecodeExactDate( dateinput=dateinput, timeinput=timeinput, today=today, preferreddateformat=preferreddateformat )
	if exactdatetime != None and exactdatetime != str(None):
		if debug:
			print "ExactDateTime Found : " + str( exactdatetime )
		return str(exactdatetime)
	if debug:
		print "ExactDateTime Not Found"
	
	relativedatetime = DecodeSpecialTimeFormat( dateinput=dateinput,  timeinput=timeinput, today=today )
	if relativedatetime != None and relativedatetime != str(None):
		if debug:
			print "RelativeDateTime Found : " + str( relativedatetime )
		return str(relativedatetime)
	if debug:
		print "RelativeDateTime Not Found"
	
	dayofweek = DateOfLastorNext( dateinput=dateinput, timeinput=timeinput, today=today )
	if dayofweek != None and dayofweek != str(None):
		if debug:
			print "DayOfWeek Found : " + str( dayofweek )
		return str(dayofweek)
	if debug:
		print "dayofweek Not Found"
	
	# Holidays
	# Lunar Calendar
	
	if debug:
		print "returning defaultdatetime"
	return str(defaultdatetime)