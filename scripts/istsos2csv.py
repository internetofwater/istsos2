# -*- coding: utf-8 -*-

import urllib
import datetime
import sys
from os import path
import traceback
from datetime import timedelta
    
sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
    import lib.requests as req
    from scripts import istsosutils
    import lib.isodate as iso

except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e

step = timedelta(days=20)
isoop = "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"
    
def makeFile(res, procedure, op, path):
    text = res.text
    text = text.replace("%s," % procedure, "")
    lines = text.split('\n')
    if lines[-1] == '':
        del lines[-1]
    tmpOp = op.replace("x-ist::","x-istsos:1.0:")
    lines[0] = "%s,%s,%s:qualityIndex" % (isoop, tmpOp, tmpOp)    
    if len(lines)>1:
        datenumber = iso.parse_datetime(lines[-1].split(",")[0])       
        print "File: %s/%s_%s.dat" % (path, procedure, datetime.datetime.strftime(datenumber, "%Y%m%d%H%M%S%f"))
        out_file = open("%s/%s_%s.dat" % (path, procedure, datetime.datetime.strftime(datenumber, "%Y%m%d%H%M%S%f")),"w")
        out_file.write("\n".join(lines))
        out_file.close()

    
def execute (args, logger=None):
    
    print "istsos2csv start.."
    
    try:
        
        url = args['url']
        
        procedure = args['procedure']
        observedProperty = args['op']
        
        begin = iso.parse_datetime(args['begin'])
        end = iso.parse_datetime(args['end'])
        
        d = args['d']
            
        params = {
            "request": "GetObservation",
            "offering": "temporary",
            "procedure": procedure,
            "eventTime": None,
            "observedProperty": observedProperty,
            "responseFormat": "text/plain",
            "service": "SOS", 
            "version":"1.0.0",
            "qualityIndex":"True"
        }
        
        tmpBegin = begin
        tmpEnd = end
        if (end-begin)>step:
            tmpEnd = tmpBegin + step
        
        print params

        while tmpEnd <= end:
        
            print ("%s - %s") % (tmpBegin,tmpEnd)

            if tmpBegin == tmpEnd:
                params["eventTime"] = iso.datetime_isoformat(tmpBegin)
            else:
                params["eventTime"] = "%s/%s" % (iso.datetime_isoformat(tmpBegin), iso.datetime_isoformat(tmpEnd))
                
            res = req.get("%s?%s" % (url, urllib.urlencode(params)))
            
            makeFile(res, procedure, observedProperty, d)
            tmpBegin = tmpEnd
            tmpEnd = tmpBegin + step
            
            print " %s ************************** " % iso.datetime_isoformat(tmpEnd)
            
        if tmpBegin < end:
        
            tmpEnd = end
            if tmpBegin == tmpEnd:
                params["eventTime"] = iso.datetime_isoformat(tmpBegin)
            else:
                params["eventTime"] = "%s/%s" % (iso.datetime_isoformat(tmpBegin), iso.datetime_isoformat(tmpEnd))
            
            res = req.get("%s?%s" % (url, urllib.urlencode(params)))
            makeFile(res, procedure, observedProperty, d)
            
            print " %s ************************** " % iso.datetime_isoformat(end)
        
        print "Finish."
        
    except Exception as e:    
        print "ERROR: %s\n\n" % e
        traceback.print_exc()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Export data in CSV format')
        
    parser.add_argument('-b', '--begin',
        action = 'store',
        dest   = 'begin',
        default= '*',
        metavar= '1978-10-08T03:56:00+01:00',
        help   = 'Begin position date of the processing in ISO 8601. If the default value (%(default)s) is used, then the endPosition of the \"destination\" service procedure will be used.')
    
    parser.add_argument('-e', '--end',
        action = 'store',
        dest   = 'end',
        default= '*',
        metavar= '2014-01-27T11:27:00+01:00',
        help   = 'End position date of the processing in ISO 8601. If the default value (%(default)s) is used, then the endPosition of the "source" service procedure will be used.')
        
    parser.add_argument('-p',
        action = 'store',
        dest   = 'procedure',
        help   = 'Procedure name')
        
    parser.add_argument('-o',
        action = 'store',
        dest   = 'op',
        help   = 'Procedure\'s observed property')
    
    parser.add_argument('-u',
        action = 'store',
        dest   = 'url',
        metavar= 'url',
        default= 'http://localhost:80/sos',
        help   = 'IstSOS Server address IP (or domain name) used for all request. (default: %(default)s).')
        
    parser.add_argument('-d',
        action = 'store',
        dest   = 'd',
        default= './',
        help   = 'Csv output folder (default %(default)s).')
    

    args = parser.parse_args()
    #print args.__dict__
    execute(args.__dict__)
