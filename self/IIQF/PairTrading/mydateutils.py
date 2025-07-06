# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:04:25 2020

@author: Abhijit Biswas
"""

import datetime as dt


class DateTimeFunctions:
    
    def Now():
        return dt.datetime.now()
    
    def CurrentDate():
        return dt.datetime.now().date()
    
    def CurrentTime():
        return dt.datetime.now().time()
    
    def CurrentYear():
        return int(dt.datetime.now().strftime("%Y"))
    
    def CurrentMonth():
        return int(dt.datetime.now().strftime("%m"))
    
    def CurrentDay():
        return int(dt.datetime.now().strftime("%d"))
    
    def CurrentDateTimeStr(dateformat = 'yyyy-mm-dd HH:MM:SS'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            dateformat = dateformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            dateformat = dateformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            dateformat = dateformat.replace('o', '%f')
            dateformat = dateformat.replace('wwww', '%A').replace('www', '%a').replace('ww', 'w').replace('w', '%w')
            dateformat = dateformat.replace('AP', '%p')
            
            return dt.datetime.now().strftime(dateformat)
        except ValueError as ve:
            print(ve)
            return None
    
    def CurrentDateStr(dateformat = 'yyyy-mm-dd'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            
            return dt.datetime.now().strftime(dateformat)
        except ValueError as ve:
            print(ve)
            return None
    
    def CurrentTimeStr(timeformat = 'HH:MM:SS'):
        try:
            timeformat = timeformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            timeformat = timeformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            timeformat = timeformat.replace('o', '%f')
            timeformat = timeformat.replace('AP', '%p')
            
            return dt.datetime.now().strftime(timeformat)
        except ValueError as ve:
            print(ve)
            return None
    
    def CurrentYearStr():
        return dt.datetime.now().strftime("%Y")
    
    def CurrentMonthStr():
        return dt.datetime.now().strftime("%m")
    
    def CurrentDayStr():
        return dt.datetime.now().strftime("%d")
    
    def DateAdd(fromdatetime, num, numtype, dateformat = 'yyyy-mm-dd H:M:S'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            dateformat = dateformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            dateformat = dateformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            dateformat = dateformat.replace('o', '%f')
            dateformat = dateformat.replace('wwww', '%A').replace('www', '%a').replace('ww', 'w').replace('w', '%w')
            dateformat = dateformat.replace('AP', '%p')
            
            nextdate = ''
            if (type(fromdatetime) == str):
                fromdatetime = dt.datetime.strptime(fromdatetime, dateformat)

            if (numtype == 'o'):
                nextdate = fromdatetime + dt.timedelta(microseconds = num)
            elif (numtype == 'i'):
                nextdate = fromdatetime + dt.timedelta(milliseconds = num)
            elif (numtype == 's'):
                nextdate = fromdatetime + dt.timedelta(seconds = num)
            elif (numtype == 'm'):
                nextdate = fromdatetime + dt.timedelta(minutes = num)
            elif (numtype == 'h'):
                nextdate = fromdatetime + dt.timedelta(hours = num)
            elif (numtype == 'd'):
                nextdate = fromdatetime + dt.timedelta(days = num)
    
            return nextdate
        except ValueError as ve:
            print(ve)
            return None
    
    
    def DateDiff(fromdatetime, todatetime, difftype, dateformat = 'yyyy-mm-dd H:M:S'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            dateformat = dateformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            dateformat = dateformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            dateformat = dateformat.replace('o', '%f')
            dateformat = dateformat.replace('wwww', '%A').replace('www', '%a').replace('ww', 'w').replace('w', '%w')
            dateformat = dateformat.replace('AP', '%p')
            
            if (type(fromdatetime) == str):
                fromdatetime = dt.datetime.strptime(fromdatetime, dateformat)
            if (type(todatetime) == str):
                todatetime = dt.datetime.strptime(todatetime, dateformat)
                
            if type(fromdatetime) == dt.date:
                fromdatetime = DateTimeFunctions.StrToDateTime(fromdatetime.strftime("%Y-%b-%d") + ' 00:00:00', 'yyyy-mmm-dd HH:MM:SS')
            if type(todatetime) == dt.date:
                todatetime = DateTimeFunctions.StrToDateTime(todatetime.strftime("%Y-%b-%d") + ' 00:00:00', 'yyyy-mmm-dd HH:MM:SS')
            
            diff = (todatetime - fromdatetime).total_seconds()
            if (difftype == 'o'):
                diff = diff * 1000000
            elif (difftype == 'i'):
                diff = diff * 1000
            elif (difftype == 's'):
                diff = diff 
            elif (difftype == 'm'):
                diff = diff / 60
            elif (difftype == 'h'):
                diff = diff / 3600
            elif (difftype == 'd'):
                diff = diff / (3600 * 24)
        
            return diff
        except ValueError as ve:
            print(ve)
            return None
    
    
    def StrToDateTime(strdatetime, dateformat = 'yyyy-mm-dd H:M:S'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            dateformat = dateformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            dateformat = dateformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            dateformat = dateformat.replace('o', '%f')
            dateformat = dateformat.replace('wwww', '%A').replace('www', '%a').replace('ww', 'w').replace('w', '%w')
            dateformat = dateformat.replace('AP', '%p')
            
            dtdatetime = ''
            if (type(strdatetime) == str):
                dtdatetime = dt.datetime.strptime(strdatetime, dateformat)
                
            return dtdatetime
        except ValueError as ve:
            print(ve)
            return None
    
    def StrToDate(strdate, dateformat = 'yyyy-mm-dd'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            dateformat = dateformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            dateformat = dateformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            dateformat = dateformat.replace('o', '%f')
            dateformat = dateformat.replace('wwww', '%A').replace('www', '%a').replace('ww', 'w').replace('w', '%w')
            dateformat = dateformat.replace('AP', '%p')
            
            dtdate = ''
            if (type(strdate) == str):
                dtdate = dt.datetime.strptime(strdate, dateformat).date()
                
            return dtdate
        except ValueError as ve:
            print(ve)
            return None
    
    def StrToTime(strtime, dateformat = 'H:M:S'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            dateformat = dateformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            dateformat = dateformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            dateformat = dateformat.replace('o', '%f')
            dateformat = dateformat.replace('wwww', '%A').replace('www', '%a').replace('ww', 'w').replace('w', '%w')
            dateformat = dateformat.replace('AP', '%p')
            
            tmtime = ''
            if (type(strtime) == str):
                tmtime = dt.datetime.strptime(strtime, dateformat).time()
                
            return tmtime
        except ValueError as ve:
            print(ve)
            return None
    
    def DateToStr(dtdate, dateformat = 'yyyy-mm-dd'):
        try:
            dateformat = dateformat.replace('yyyy', '%Y').replace('yy', '%y')
            dateformat = dateformat.replace('mmmm', '%B').replace('mmm', '%b').replace('mm', 'm').replace('m', '%m')
            dateformat = dateformat.replace('dd', 'd').replace('d', '%d')
            dateformat = dateformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            dateformat = dateformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            dateformat = dateformat.replace('o', '%f')
            dateformat = dateformat.replace('wwww', '%A').replace('www', '%a').replace('ww', 'w').replace('w', '%w')
            dateformat = dateformat.replace('AP', '%p')
            
            strdate = ''
            if (type(dtdate) == dt.date):
                strdate = dt.datetime.strftime(dtdate, dateformat)
            elif (type(dtdate) == dt.datetime):
                strdate = dt.datetime.strftime(dtdate, dateformat)
                
            return strdate
        except ValueError as ve:
            print(ve)
            return None
   
    def TimeToStr(tmtime, timeformat = 'H:M:S'):
        try:
            timeformat = timeformat.replace('HH', 'H').replace('H', '%H').replace('hh', 'h').replace('h', '%I')
            timeformat = timeformat.replace('MM', 'M').replace('M', '%M').replace('ss', 'S').replace('s', 'S').replace('SS', 'S').replace('S', '%S')
            timeformat = timeformat.replace('o', '%f')
            timeformat = timeformat.replace('AP', '%p')
            
            strtime = ''
            if (type(tmtime) == dt.time):
                strtime = dt.datetime.strftime(tmtime, timeformat).time()
                
            return strtime
        except ValueError as ve:
            print(ve)
            return None
        


