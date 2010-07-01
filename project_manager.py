#!/usr/local/bin/python

import calendar, time, pickle, cgi, cgitb, os
cgitb.enable()

compose     = lambda m, n                     : lambda x, m=m, n=n: m(n(x))
link        = lambda href, text, id='', cls='': "<a id='%s' class='%s' href='%s'>%s</a>" % (id, cls, href, text)
wrap        = lambda tag, data, rest=''       : "<%s> %s </%s>" % (tag, data, tag)
label       = lambda name, value=''           : "<label for='%s'>%s</label><input name='%s' value='%s' />" % (name, name, name, value)
submit      = lambda                          : "<input type=submit name=submit value='Submit'>"
hidden      = lambda n, v                     : "<input type=hidden name='%s' value='%s' />" % (n, v)
project     = lambda t                        : {'title': t,'members': [], 'overview': "", 'comments': [], 'tasks': []}
loadproject = lambda p                        : pickle.load(open(p, "rb"))
loaduser    = lambda u                        : pickle.load(open(u, "rb"))
tags        = ('a','b','div','h1','h2','h3','img','p','span')
a, b, div, h1, h2, h3, img, p, span = map(lambda tag: lambda str: wrap(tag, str), tags)

def datepicker(d=1, m=1, y=2007):
	year, month, thedate, x, y, z, a, xx, yy = time.localtime()
	ypart = dselect('year', [x for x in range(2007, 2030)], year)
	mpart = dselect('month',[x for x in range(1, 12)], month)
	dpart = dselect('date', [x for x in range(1, 32)], thedate)
	return "%s %s %s" % (ypart, mpart, dpart)

def dselect(name, lst, default=''):
	select = "<select name='%s'>" % name
	for opt in iter(lst):
		if str(opt) == str(default): selected = "selected='selected'"
		else: selected = ''
		select = select + "<option value='%s' %s > %s</option>" % (opt, selected, opt)
	return (select + "</select>")

def saveproject(p):
	pickle.dump(p, open(p['title'] + ".prj", "wb"))
	return p

def saveuser(u):
    pickle.dump(u, open(u['name'] + ".usr", "wb"))
    return u

def print_header():
	print "Content-Type: text/html\n\n"
	print "<html><head><link type='text/css' rel='stylesheet' href='/project_manager/style.css' />",
	print "<script type='text/javascript' src='/project_manager/core.js' />"
	print "<script type='text/javascript' src='/project_manager/app.js' />"
	print "<script type='text/javascript' src='/project_manager/ajax.js' />"
	print "</head><body>"

def print_footer(): print "</div></body></html>"

def flatten(l):
	if type(l) !=  type([]): return [l]
	if l == []: return l
	return flatten(l[0]) + flatten(l[1:])

def saveform(ob):
	keys = ob.keys()
	post = cgi.FieldStorage()
	for x in iter(post):
		if ob.has_key(x): ob[x] = post[x]
	return ob

def makeform(name, show, hide):
	frm = ""
	for x in show: frm = frm + label(x) + "<br>"
	for x in hide: frm = frm + "<input type='hidden' name='%s' />" % x
	return frm

def show_all_projects():
	projects = os.listdir(".")
	projects = [project(p) for p in projects if os.path.isfile(p) and os.path.splitext(p)[1] in [".prj"]]
	print "<ul id=projectlist><li id=createproject ><a href='?addproject=1'>Create Project</a></li>"
	for p in iter(projects):
		ptitle = os.path.splitext(p['title'])[0]
		print "<li><a href=\"?showproject=%s\">%s</a></li>" % (p['title'], ptitle)
	print "</ul><div id='cnt'>"

def showproject( p , all='normal'):
	print h1(p['title']),"<a href='?showall=%s'>Show All</a> | <a href='?showproject=%s.prj'>Show incomplete</a><a href='?addtask=%s' class='addtask'>Add a task</a>" % (p['title'], p['title'], p['title']), h2("Total hours: %.2f" % (get_project_time(p)))
	print "<div id='members'>"
	if not p.has_key('members'): p['members'] = []
	print h3(" Team members")
	for i in iter(p['members']): print i['name'],", "
	print link('?project=' + p['title'] + '&addmember=1', 'Add a team member')
	print "</div>"
	print " <div id=tasklist>"
	for i in iter(p['tasks']):
		if not i.has_key('status'): i['status'] = 'incomplete'
		if i['status'] == 'completed' and all == 'normal' : continue
		print "<div class=taskline>"
		print " <a class='%s' href='?project=%s&addwork=%s'>Add hours</a>" % (i['status'], p['title'], i['title'])
		print " <a class='%s' href='?project=%s&setstatus=%s'>Complete</a>" % (i['status'], p['title'], i['title'])
		print "<span class='name'>%s</span>" % i['person'],
		print " <span class='task'>%s</span>" % i['title']
		print "</div>"
		print "<div class=timedata>"
		for x in iter(i['time']):
			print "<div>"
			print "<form style='display:inline' action='' method=post >"
			print "Date <span class=date>%s</span> Duration <span class=hours>%.2f</span>" % (x['date'], x['hours'])
			print "<a class=changehours project='%s' task='%s' date='%s' hours='%2.f' href='#' >Change</a>" % (p['title'], i['title'], x['date'], x['hours'])
			print hidden('savechangehours', 1), hidden('project', p['title']), hidden('task', i['title'])
			print "</form>"
			print "</div>"
		print "</div>"
	print "</div>"

def settaskstatus(p, t):
	task = gettask(p, t)
	task['status'] = 'completed'
	ts = [x for x in p['tasks'] if x['title'] != t]
	ts.append(task)
	p['tasks'] = ts
	return saveproject(p)

def gettask(p, t):
	return [x for x in p['tasks'] if x['title'] == t][0]

def savemember(project, person):
	if not project.has_key('members'): project['members'] = []
	names = [x['name'] for x in project['members']]
	r = False
	if len(names) > 0: r = reduce(lambda x, y: (x == person) or y, names)
	if r != person: project['members'].append({'name':person})
	return saveproject(project)

def savetask(project, title, person, status='incomplete' ):
	project['tasks'].append( {'person':person, 'title':title, 'status':status, 'time':[]} )
	return saveproject(project)

def savework(project, title, year, month, day, hours):
	date = "%s-%s-%s" % (day, month, year)
	task  = gettask(project, title)
	hours = float(hours)
	tasks = [x for x in project['tasks'] if x['title'] != title]
	samedatelist = [x for x in task['time'] if x['date'] == date]
	samedate = ''
	if len(samedatelist): samedate = samedatelist[0]
	notsamedate = [x for x in task['time'] if x['date'] != date]

	if samedate:
		samedate['hours'] = float(samedate['hours']) + hours
		notsamedate.append(samedate)
		task['time'] = notsamedate
	else:
		task['time'].append( {'date':"%s-%s-%s" % (year, month, day), 'hours':hours} )

	tasks.append( task )
	project['tasks'] = tasks
	return saveproject(project)

def get_project_time(project):
	times = map(lambda x: x['time'], project['tasks'])
	total = 0
	if len(times) > 0:
		hourlist = map(lambda x: x['hours'], flatten(times))
		if len(hourlist) > 0: total = reduce(lambda x, y: x + y, hourlist)
	return total

def showtasks(p):
	for t in p['tasks']:
		print t['title'], "(", t['person'], ")"

def addmember(p):
	print "<p>Project: <b>%s</b></p>" % p
	print "<form name=addmember method=post action=''>"
	print "<fieldset><legend>Add a new member to the %s project</legend>" % p
	print label('person'), submit(), hidden('project', p), hidden('savemember','1')
	print "</form>"

def addtask(p):
	proj = loadproject(p + ".prj")
	people = [m['name'] for m in proj['members']]
	print "<p>Project: <b>%s</b></p>" % p
	print "<fieldset><legend>Add task to %s p</legend>" % p
	print "<form name=addtask method=post action=''>"
	print label('task'), dselect('person', people), submit(), hidden('project', p), hidden('savetask','1')
	print "</fieldset></form>"

def addwork(p, t, change=0):
	print "<p>Project: <b>%s</b></p>" % p
	print "<form name=add_work method=post action=''>"
	print "<fieldset><legend>Task: %s</legend>" % t
	print datepicker(), label('hours'), submit(), hidden('project', p), hidden('task', t), hidden('savework','1')
	print "</form>"

def changehours(p, t, h):
	print "<p>Project: <b>%s</b></p>" % p
	print "<form name=add_work method=post action=''>"
	print "<fieldset><legend>Task: %s</legend>" % t
	print datepicker(), label('hours'), submit(), hidden('project', p), hidden('task', t), hidden('savework','1')
	print "</form>"

def addproject():
	print " <form name=addproject method=post action='' />"
	print label('name'),"<br>"
	print "<label for=overview>About</label><textarea name='overview' class=overview></textarea><br>"
	print submit(), hidden('saveproject','1')
	print "</form>"

def check_post():
	post = cgi.FieldStorage()
	if post.has_key('showproject') : showproject(loadproject(post['showproject'].value))
	if post.has_key('showall')     : showproject(loadproject(post['showall'].value + ".prj"),'showall')
	if post.has_key('addproject')  : p = addproject()
	if post.has_key('saveproject') : showproject(saveproject(project(post['name'].value)))
	if post.has_key('addmember')   : addmember(post['project'].value)
	if post.has_key('addwork')     : addwork(post['project'].value, post['addwork'].value)
	if post.has_key('addtask')     : addtask(post['addtask'].value)

	if post.has_key('savechangehours'):
		p                                      = post['project'].value
		p                                      = loadproject(p + '.prj')
		t                                      = post['task'].value
		d                                      = post['date'].value
		h                                      = float(post['hours'].value)
		task                                   = gettask(p, t)
		times                                  = task['time']
		leavethem                              = [x for x in times if x['date'] != d]
		leavethem.append({'date':d,'hours':h})
		task['time']                           = leavethem
		leavethem                              = [x for x in p['tasks'] if x['title'] != t]
		leavethem.append(task)
		p['tasks'] = leavethem
		showproject(saveproject(p))

	if post.has_key('savemember'):
		p, m = [post[x].value for x in ['project','person']]
		return showproject(savemember(loadproject(p + ".prj"), m))

	if post.has_key('savetask'):
		p, t, person = [post[x].value for x in ['project','task','person']]
		return showproject(savetask(loadproject(p + ".prj"), t, person))

	if post.has_key('savework'):
		p, t, y, m, d, hrs = [post[x].value for x in ['project','task','year','month','date','hours']]
		return showproject(savework(loadproject(p + ".prj"), t, y, m, d, hrs))

	if post.has_key('setstatus'):
		p, t = [post[x].value for x in ['project','setstatus']]
		return showproject(settaskstatus(loadproject(p + ".prj"), t))

def main():
	print_header()
	show_all_projects()
	check_post()
	print_footer()

main()
