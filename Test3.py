from urllib.request import urlopen
from xml.etree.ElementTree import parse

# ipaddress = '192.168.66.101'
# way = 'http://' + ipaddress + '/values.xml'
way = 'http://192.168.66.105/values.xml'
# way = 'https://blogs.oracle.com/oraclepartners/database-7/rss'
var_url = urlopen(way)
xmldoc = parse(var_url)
print(xmldoc)

# for item in xmldoc.iterfind('channel/item'):
for item in xmldoc.iterfind('head'):
    title = item.findtext('title')
    date = item.findtext('pubDate')
    link = item.findtext('link')
    # mac = item.findtext('<MAC>')

    print(title)
    print(date)
    print(link)
    # print(mac)
