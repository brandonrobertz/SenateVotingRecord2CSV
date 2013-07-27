#!/usr/bin/python
""" This tool loads Senate Data directly from the government's website, parses
thru the XML files, and converts into a usable CSV file.
by Brandon Roberts 2012 copyleft GPLv3+."""

import requests
import argparse
import xml.etree.ElementTree as ET
import csv
import re

def fetch( url):
  headers = {"User-Agent": "Mozilla/5.0 (Window NT 6.1; WOW64; rv:17.0)"
                           "Gecko/17.0 Firefox/17.0"}
  loaded = False
  while not loaded:
    try:
      r = requests.get(url, headers=headers, allow_redirects=False)
      if r.status_code == 200:
        return r.text
    except Exception as e:
      print "[!] Error fetching %s\n[!] %s" % (url, e)

def fetch_bills( SENATE, SESSION ):
  """ This first fetches the number of bills in this senate session, then it
      iterates through them and collects the raw xml for each bill's vote.

      Parameters:
        SENATE  : The number of senate to search, i.e., 111
        SESSION : Which senate session? i.e, 1 or 2

      Returns:
        A list of every XML file containing information about every 
        bill voted on for the senate session.
  """
  bills = []
  # Get number of bills from internet
  URLM=( "http://www.senate.gov/legislative/LIS/roll_call_lists/"
         "vote_menu_%s_%s.xml"%(SENATE,SESSION))
  xmlf0 = fetch( URLM)
  
  tree = ET.fromstring(xmlf0)
  # this is the number of bills
  TOTAL_BILLS = int(tree[3][0][0].text)
  
  print "[*] Total Bills in Senate %s Session %s: %s" % (SENATE, SESSION,
                                                         TOTAL_BILLS)
  
  # Get all senate voting files ... this could be multiprocessed, but it's
  # not really worth the effort to me right now
  bills = []
  for b in xrange( 1, TOTAL_BILLS+1):
    b = str(b).zfill(5)
    print( "[ ] Fetching record SENATE: %s SESSION: "
           "%s NUM: %s"%(SENATE, SESSION, b))
    URL=("http://www.senate.gov/legislative/LIS/roll_call_votes/vote%s%s/"
         "vote_%s_%s_%s.xml"%(SENATE, SESSION, SENATE, SESSION, b))
    bill = fetch( URL)
    bills.append( bill)
  return bills

def process_bills( FIRST, LAST, bills):
  """ This returns a particular senator's voting record from raw XML text
      with information about senate bills and their voters.
      
      Parameters:
        FIRST : Senator's first name
        LAST  : Senator's last name
        bills : a list of raw XML strings containing the senate voting records

      Returns:
        A iterable of a particular senators' voting record for each bill.
  """
  print "[*] TOTAL BILLS TO PROCESS %s" % len( bills)
  n = 0
  for bill in bills:
    print "[*] PROCESSING NUM: %s"%n
    n +=1
    tree = ET.fromstring( bill)
    
    # Get votes from this record
    text = tree[7].text
    if text:
      text = re.sub('[^A-Za-z0-9 ]', '', text)
    
    # this next section  loops through all the voters (senators) and looks
    # for a vote from the senator we want
    last = ""
    first= ""
    vote = ""
    for member in tree[17]:
      l = member[1].text # last
      f = member[2].text # first
      v = member[5].text # vote
      if l.lower() == LAST.lower() and f.lower() == FIRST.lower():
        last    = l
        first   = f
        vote    = v
        break

    if vote == "Yea" or vote == "Nay":
      yield text, vote

def voting_record( FIRST, LAST, SENATE, SESSION):
  """ This is a wrapper for the process_bills and fetch_bills functions. Give
      it a Senator's first and last names, the senate number and session and
      it will tell you how the senator voted on particular bills.

      Paramaters:
        FIRST   : Senator's first name
        LAST    : Senator's last name
        SENATE  : The number of senate to search, i.e., 111
        SESSION : Which senate session? i.e, 1 or 2

      Returns:
        A an iterable list of how a senator voted on each bill.
  """
  bills = fetch_bills( SENATE, SESSION )
  print "[*] Processing bills XML"
  return process_bills( FIRST, LAST, bills)

def argz():
  parser = argparse.ArgumentParser()
  desc =("This tool loads Senate Data directly from the government's website,"
         " parses thru the XML files, and converts into a usable CSV file. "
         "It's classified by Yea or Nay vote and "
         "looks at the description of the bill as the string. "
         "by Brandon Roberts 2012 copyleft GPL3+.")
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument("first", type=str, help="first name of politician")
  parser.add_argument("last", type=str, help="last name of politician")
  parser.add_argument("senate", type=str, help="senate ... 111th would be 111")
  parser.add_argument("session", type=str, help="1 or 2")
  parser.add_argument("ofile", type=str, help="file to write csv to")
  return parser.parse_args()

def write_csv( recs, OFILE):
  """ Write our senate voting record to disk.

      Parameters:
        recs  : our iterable list containing a senate voting record
        OFILE : the filename to write the CSV to
  """
  if ".csv" not in OFILE:
    filename = "%s.csv"%OFILE
  else:
    filename = OFILE
  print "[*] Writing to %s"%filename
  header = [ "BILL_SUMMARY", "VOTE"]
  with open(filename, 'wb') as f:
    w = csv.writer(f, header)
    w.writerow( header)
    w.writerows( recs)

def main():
  # do cmd line arguments
  args = argz()
  # our input varz
  SENATE  = args.senate  # 111
  SESSION = args.session # 1
  LAST    = args.last    # "Franken"
  FIRST   = args.first   # "Al"
  OFILE   = args.ofile   # "franken.2009.arff"
  # fetch voting record
  print "[*] Getting %s %s's voting record"%(FIRST, LAST)
  recs = voting_record( FIRST, LAST, SENATE, SESSION)
  # write voting record
  write_csv( recs, OFILE)
  # who woulda thought it was so easy?
  print "[*] Boom Shucka lucka."

if __name__ == "__main__":
  main()