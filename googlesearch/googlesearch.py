#!/usr/bin/python
import json
import urllib
import sys

def searchgoogle(searchfor):
  query = urllib.urlencode({'q': searchfor})
  url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
  search_response = urllib.urlopen(url)
  search_results = search_response.read()
  results = json.loads(search_results)
  data = results['responseData']
  print '[+] Total results: %s' % data['cursor']['estimatedResultCount']
  hits = data['results']
  print '[+] Top %d hits:' % len(hits)
  for h in hits: 
    print '[+] ', h['url']
  print '[+] For more results, see %s' % data['cursor']['moreResultsUrl']


if __name__ == '__main__':
  if len (sys.argv) < 2:
    print 'Usage: %s <search term>' % sys.argv[0]
    print '  Try using quotes if you want multiple terms'
    print '  Eg %s \"test results\"' % sys.argv[0]
    sys.exit(1) 
  searchgoogle(sys.argv[1])
