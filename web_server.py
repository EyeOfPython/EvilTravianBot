#!/usr/bin/python3
'''
Created on 22.07.2014

@author: Tobias Ruck
'''
from http.server import SimpleHTTPRequestHandler
import db
from account import Account
from datetime import datetime
from urllib import parse

class BotWebServer(SimpleHTTPRequestHandler):
    
    enc = "utf-8"
    account = None
    
    def do_GET(self):
        r = []
        self.build_head(r)
        request = parse.urlparse(self.path)
        path = request.path
        query = parse.parse_qs(request.query)
        if path.startswith('/log'):
            self.view_logs(r, query)
        if path.startswith('/status'):
            self.view_status(r, query)
        self.build_body(r)
        
        encoded = '\n'.join(r).encode(self.enc)
        self.send_headers(encoded)
        self.wfile.write(encoded)
        
    def view_logs(self, r, q):
        tfilter = q.get('filter', [''])[0].split(',')
        if 'account' not in q:
            r.append('<form>Account: <input type="text" name="account" /></form>')
            return
        account_name = q['account'][0]
        
        if tfilter and not tfilter[0]:
            tfilter = []
        not_filter = q.get('not_filter', [''])[0].split(',')
        if not_filter and not not_filter[0]:
            not_filter = []
        r.append( str(tfilter) )
        r.append( str(not_filter)  )
        r.append('<table>')
        for log in db.log.find({'log_name': account_name}):
            if tfilter and not all([ f in log['type'] for f in tfilter ]):
                continue
            if not_filter and any([ f in log['type'] for f in not_filter]):
                continue
            log['time'] = datetime(*log['time'])
            r.append( '<tr>')
            r.append( '''
<td>{severity}</td>
<td>{type}</td>
<td>{time}</td>
<td>{title}</td>
<td>{message}</td>'''.format(**log) )
        r.append('</table>')
        
        r.append('''
<form>
filter: <input type="text" name="filter" />
not filter: <input type="text" name="not_filter" />
<input type="submit" text="filter" />
</form>
''')
    
    def view_status(self, r, q):
        if 'vid' in q:
            status = db.status.find_one({'village':q['vid'][0]})
        else:
            for status in db.status.find():
                #print(status)
                r.append( '{name}: <a href="/status?vid={village}">{village}</a><br/>'.format(**status))
            return
        r.append('<h1>Status for %s (%s)</h1>' % (status['name'], status['village']))
        r.append('<table>')
        r.append('<tr><td></td><td>Wood</td><td>Clay</td><td>Iron</td><td>Grain</td></tr>')
        r.append('<tr><td>Resources:</td>%s</tr>' % ''.join('<td>%s</td>' % r for r in status['resources']))
        r.append('<tr><td>Production:</td>%s</tr>' % ''.join('<td>%s</td>' % r for r in status['production']))
        r.append('<tr><td>Storage:</td>%s</tr>' % ''.join('<td>%s</td>' % r for r in status['storage_capacity']))
        r.append('</table>')
        
        def echo_builds(builds):
            r.append('<table>')
            for bid, gid, lvl in builds:
                if gid:
                    r.append('<tr><td>%s</td><td>%s level %s</td>' % (bid, db.buildings[gid]['gname'], lvl))
            r.append('</table>')
        r.append('<div  class="block">')
        r.append('<h2>Resource fields</h2>')
        echo_builds(status['resource_fields'])
        r.append('</div>')
        
        r.append('<div  class="block">')
        r.append('<h2>Buildings</h2>')
        echo_builds(status['buildings'])
        r.append('</div>')
        
        r.append('<div  class="block">')
        r.append('<h2>Build Events</h2>')
        r.append('<table>')
        for event in status['build_events']:
            r.append('<tr><td>%s to level %s</td><td>%s</td></tr>' % (db.buildings[event['building']]['gname'], event['level'], event['time']) )
        r.append('</table>')
        r.append('</div>')
    
    def build_head(self, r):
        title = 'Overview' 
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % self.enc)
        r.append('''
<style>
td { border: 1px solid grey; 
     padding: 2px; }
.block { float: left; width: 300px; }
</style>
'''
                 )
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n')

    def build_body(self, r):
        r.append('\n</body>\n</html>\n')
        
    def send_headers(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % self.enc)
        self.send_header("Content-Length", str(len(text)))
        self.end_headers()
    
if __name__ == '__main__':
    import socketserver
    
    port = 1338
    BotWebServer.account = Account((3, 'de'), 'Gl4ss')
    
    Handler = BotWebServer
    httpd = socketserver.TCPServer(("", port), Handler)
    print("Serve at port", port)
    httpd.serve_forever()
