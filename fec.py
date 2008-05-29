#!/usr/bin/python
"""
Library of functions to process and handle Federal Election Commission data available from http://www.fec.gov and its FTP site, ftp://ftp.fec.gov.

The MIT License

Copyright (c) 2008 Derek Willis

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
__author__ = "Derek Willis <dwillis@gmail.com>"
__date__ = "$Date: 2008/05/19 $"
__version__ = "$Revision: 2.2 $"

import re
import urllib
import sys
import string
import urlparse
import datetime

d = datetime.date.today()
dm = str(d.month).zfill(2)
dd = str(d.day).zfill(2)
stringdate=dm+'/'+dd+'/'+str(d.year)


def fec_news():
    """
    Scraping the FEC's news releases to produce an RSS feed using regular expressions. Based on a script by Sam Ruby. 
    The script supports relative urls and the elimination of extraneous whitespace, and produces an RSS 0.91 feed.
    Running this script using versions of Python before 2.3 require importing sre as re and resetting the maximum recursion limit.
    
    Usage from within Python shell: 
    from fec import fec_news
    fec_news()
    """
    # set up needed variables

    date = datetime.date.today()
    year = date.year
    base_url = 'http://www.fec.gov/press/press%s/' % year
    url = base_url + '%sNewsReleases.shtml' % year
    file = 'fecnews.rss'


    # read the content of the FEC's press page

    try:
      page=urllib.urlopen(url).read()
    except IOError:
      page=''
    except AssertionError:
      page=''

    # set up the top of the RSS feed.

    rss="""<?xml version="1.0" encoding="ISO-8859-1"?>
    <rss version="0.91">
    	<channel>
    		<title>FEC News</title>
    		<link>http://www.fec.gov/</link>
    		<description>Press releases and announcements</description>
    		<language>en-us</language>
    """
		
    #define regular expression to grab link, date and title from FEC news
    #releases page, using DOTALL to find multiline text. Since urls are
    #internal, we need to add a prefix to the link for the RSS feed.

    news = re.compile("""valign=.top.>(.*?\d\d\d\d).?</td>.*?<td.valign=.top.>.*?<a href=.(.*?).>(.*?)</a>.*?</td>.*?</tr>""", re.DOTALL)

    #remove additional whitespace like linebreaks and returns from HTML code.
    page = ' '.join(page.split())

    #find first 10 matches
    matches = news.findall(page)
    matches = matches[:10]

    #unpack tuple of matches and add to rss feed
    for (date, link, title) in matches:
                rss+="\n<item>\n<date>%s</date><title>%s</title><link>%s</link>\n</item>\n" % (date,title,urlparse.urljoin(base_url,link))

    #close rss feed                
    rss+="""
    	</channel>
    </rss>
    """

    # if we successfully read the FEC page, write the RSS out to file
    if page:
      fh=open(file,'w')
      fh.write(rss) 
      fh.close()

def today_elec():
    """
    Returns a list of electronic filings for today's date. Could be reworked to create a dictionary using the cmteid as key.
    Dependency: BeautifulSoup for HTML parsing (http://www.crummy.com/software/BeautifulSoup/)
    Usage: today_elec()
    """
    from BeautifulSoup import BeautifulSoup
    params = {'date':stringdate}
    txt=urllib.urlopen("http://query.nictusa.com/cgi-bin/dcdev/forms/", urllib.urlencode(params)).read()
    soup = BeautifulSoup(txt)
    filings = soup.findAll('dt')
    today = []
    for cmte in filings:
        name = cmte('h4')[0]('a')[0].contents[0]
        number_of_filings = len(cmte.contents)/6 # each filing has six elements
        i = 5  # the fifth element in a filing is its title
        for filing in range(number_of_filings):
            title = cmte.contents[i]
            today.append(name+title)
            i += 6
    return today

def cmte_elec(cmte):
    """
    Returns a list of electronic filings for a given committee, using its C-number passed in to the function.
    Dependency: BeautifulSoup for HTML parsing (http://www.crummy.com/software/BeautifulSoup/)
    Usage: cmte_elec('C00224691')
    """
    from BeautifulSoup import BeautifulSoup
    params = {'comid':cmte}
    txt=urllib.urlopen("http://query.nictusa.com/cgi-bin/dcdev/forms/", urllib.urlencode(params)).read()
    soup = BeautifulSoup(txt)
    
    