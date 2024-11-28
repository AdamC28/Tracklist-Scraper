This is a simple script which I use to scrape album / DJ mix tracklists from Soundcloud and NTS Live.

For each track, it outputs the following fields:
- Track number
- Name
- Duration (only for Soundcloud tracklists)

Each field is separated by a customizable delimiter; this is the pipe "|" by default. This allows for easy conversion to .csv format / other row-column data structures (and for my personal use case, allows the tracklist to be quickly uploaded to certain music databases; e.g: RateYourMusic).
