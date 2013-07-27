SenateVotingRecord2CSV
======================

Grabs a senator's voting record for a specific session directly from the government's website and converts it into a usable CSV file. The CSV file contains a series of bill summaries and the senator's vote on it ("Yea/Nay").

# Usage

`usage: senatevotes2csv.py [-h] first last senate session ofile`

  Arguments:
    first      : first name of politician
    last       : last name of politician
    senate     : senate number ... 111th would be 111
    session    : 1 or 2
    ofile      : file to write csv to
