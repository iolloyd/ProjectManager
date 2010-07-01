#!/usr/bin/ruby

require 'cgi'
require 'cgi/session'

cgi = CGI.new
print cgi.header("type" => "text/html")

def compose(f,g)
    lambda{ |x| f(g(x)) }
end

def xtag (kind,title)
	"<#{kind}>text</#{kind}>"
end

def htmltag
	tags = ['div','p','h1','h2','h3','script']
	tags.each do |t| 
		#{t = lambda { | atts | "<#{t} #{atts.each {|k,a| print k; print a}} > </{t}>" }} 
	end	
end
htmltags()

def br
	print "<br />"
end

def link(href,text,id='',cls='')
    print "<a id='#{id}' class='#{cls}' href='#{href}'>#{text}</a>"
end

def wrap(tag,data)
    print "<#{tag}> #{data} </#{tag}>"
end

def label(n,v='')
    print "<label for='#{n}'>#{n}</label><input name='#{n}' value='#{v}' />"
end

def submit
    print "<input type=submit name=submit value='Submit'>"
end

def hidden(n,v='')
    "<input type=hidden name='#{n}' value='#{v}' />"
end

def get_project_time(project)
	times = project['tasks'].map {|x| x['time']}
	total = 0
	if len(times) > 0
		hourlist = times.flatten!.map {|x| x['hours']}
        total = hourlist.inject {|x,y| x + y} if len(hourlist) > 0
	end
	total
end

def datepicker(d=0,m=0,y=0)
	t = Time.new
	ypart = dselect('year',(2007 .. 2030).to_a, t.year)
	mpart = dselect('month',(1 .. 12).to_a,t.month)
	dpart = dselect('date',(1 .. 31),t.day)
	"#{ypart} #{mpart} #{dpart}"
end

def dselect(name, lst, default='')
	select = "<select name='#{name}'>"
	lst.each {|opt|
		selected = (opt==default) ? "selected='selected'" : selected = ''
		select = select + "<option value='#{opt}' #{selected} >#{opt}</option>"
    }
	select + "</select>"
end

def gettask(project_title, t)
	 p = loadproject(project_title)
	 task = p['tasks'].find {|x| x['title'] = t }
	 print task['title']
	 task
end

def newproject(t)
    p = {'title' => t,'members' => [],'overview' => "",'comments' => [],'tasks' => [] }
	saveproject p
end
def loadproject(p)
    File.open("#{p}.prj") {|f| Marshal.load(f) }
end
def addproject()
	print " <form name=addproject method=post action='' />"
	label("name");br();submit(); hidden("saveproject",1)
	print "</form>"
end
def saveproject(p)
	File.open("#{p['title']}.prj",'w'){|f| Marshal.dump(p,f)}
	loadproject(p)
end
def showproject( p , all='normal')
	print "all is #{all}..."
	un = p['tasks'].find {|x| x['status']=='completed'}
	print "<h1>#{p['title']}</h1>"
	print "<p>#{p['overview']}</p>"
	if p['members'] != []
    	if un
            link("?showall=#{p['title']}",     "Show All",        "showall")
            link("?showproject=#{p['title']}", "Show incomplete", "noshowall")
        end
        link("?addtask=#{p['title']}","Add a task","","addtask")
	end
	print "<div id='members'><h3>Team members</h3>"
	p['members'].each {|i| print "#{i} "}
	link("?project=#{p['title']}&addmember=1", "Add a team member")
	print "</div><div id=tasklist>"
	p['tasks'].each {|i|
		i['status'] = 'incomplete' if not i.has_key?('status')
		continue if (i['status'] == 'completed' and all == "")
		print "<div class=taskline>"
		link("?project=#{p['title']}&addwork=#{i['title']}",   "Add hours", i['status'])
		link("?project=#{p['title']}&setstatus=#{i['title']}", "Complete",  i['status'])
		print "<span class='name'>#{i['person']}</span>"
		print " <span class='task'>#{i['title']}</span></div>"
		print "<div class=timedata>"
		i['time'].each {|x|
			print "<div><form style='displayinline' action='' method=post >"
			print "Date <span class=date>#{x['date']}</span> Duration <span class=hours>#{x['hours']}</span>"
			print "<a class=changehours project='#{p['title']}' task='#{i['title']}' date='#{x['date']}' hours='#{x['hours']}' href='#' >Change</a>"
			hidden('savechangehours',1); hidden('project',p['title']); hidden('task',i['title'])
			print "</form></div>"
        }
		print "</div>"
    }
	print "</div>"
end

def print_header
	print "<html><head>"
	print "<link type='text/css' rel='stylesheet' href='/project_manager/style.css' />"
	['core','app','ajax'].each do |j|
        print "<script type='text/javascript' src='/project_manager/#{j}.js' />"
	end
	print "</head><body>"
end

def print_footer
    print "</div></div></body></html>"
end

def saveform(ob,post)
	keys = ob.keys
	post.each {|x| ob[x] = post[x] if ob.has_key?(x)}
	ob
end

def makeform(name,show,hide)
	frm = ""
	show.each {|x| frm += label(x) + "<br>"}
	hide.each {|x| frm += "<input type='hidden' name='#{x}' />"}
	frm
end


def showtasks(p)
	p['tasks'].each {|t| print t['title'] + "(" + t['person'] + ")"}
end

def show_all_projects()
	projects = Dir.entries('.').find_all {|p| p.split(".")[1] == "prj"}
	print "<ul id=projectlist><li id=createproject ><a href='?addproject=1'>Create Project</a></li>"
	projects.each {|p|
		p = p.split(".")[0]
		print "<li><a href='?showproject=#{p}'>#{p}</a></li>"
    }
	print "</ul><div id='cnt'>"
end

def addmember(p)
	print "<p>Project <b>#{p}</b></p>"
	print "<form name=addmember method=post action=''>"
	print "<fieldset><legend>Add a new member to the #{p} project</legend>"
	print label('person')
	print submit()
	print hidden('project',p)
	print hidden('savemember','1')
	print "</form>"
end
def savemember(project,person)
    project['members'] = [] if not project.has_key?('members')
	names = project['members'] << person
	names.uniq!
    project['members'] = names
	saveproject(project)
end


def addtask(p)
	proj = loadproject(p)
	people = proj['members']
	print "<p>Project <b>#{p}</b></p>"
	print "<fieldset><legend>Add task to the #{p} project</legend>"
	print "<form name=addtask method=post action=''>"
	print "Task <input name='task' />"
	print " New team member <select name='person'>"
	people.each {|x| print "<option value=#{x}>#{x}</option>" }
	print "</select> "
	print "<input type=submit name=submit value=submit />"
	print hidden('project',p)
	print hidden('savetask','1')
	print "</fieldset></form>"
end

def savetask(project, title, person, status='incomplete' )
	project = loadproject(project)
	project['tasks'] << {'person' => person, 'title' => title, 'status' => status, 'time' => []}
	print "Project is #{project}<br>"
	project = saveproject(project)
	print "and now Project is #{project}<br>"
end

def settaskstatus(p,t)
	task = gettask(p,t)
	p = loadproject(p)
	task['status'] = 'completed'
	tasks = p['tasks'].find_all {|x| x['title'] != t }
	p['tasks'] = tasks << task
	saveproject(p)
end


def addwork(p,t)
	print "<p>Project: <b>#{p}</b></p>"
	print "<form name=add_work method=post action=''>"
	print "<fieldset><legend>Task: <b>#{t}</b></legend>"
	print datepicker
	print label('hours')
	print submit
	print hidden('project',p)
	print hidden('task',t)
	print hidden('savework','1')
	print "</form>"
end
def savework(project,title,y,m,d,hours)
	date = "#{d}-#{m}-#{y}"
	task  = project['tasks'].find {|x| x['title'] == title }
	tasks = project['tasks'].find_all {|x| x['title'] != title}
	samedate = (task) ? task['time'].find {|x| x['date'] == date} : false
	notsamedate = task['time'].find_all {|x| x['date'] != samedate['date'] }
	if samedate
		samedate['hours'] = samedate['hours'].to_f + hours.to_f
		task['time'] = notsamedate << samedate
	else
		task['time'] << {'date' => date, 'hours' => hours}
    end
	project['tasks'] = tasks << task
	saveproject(project)
end


def check_post(post)
	if post.has_key?('showproject')  
        project = loadproject(post['showproject'])
	end
	if post.has_key?('showall')  
        project = loadproject(post['showall'])  
	end
	if post.has_key?('saveproject')
        project = newproject(post['name'])
	end
	if post.has_key?('addmember')
        project = addmember(post['project'])
	end
	if post.has_key?('addproject')
        project = addproject
    end

	if post.has_key?('addwork')
        project = addwork(post['project'], post['addwork'])
	end
	if post.has_key?('addtask')
        project = addtask(post['addtask'])
    end
	if post.has_key?('savechangehours')
		t,d,h = post['task'],post['date'],post['hours']
		task = gettask(p,t)
		task['time'] = task['time'].find_all {|x| x['date'] != d} << {'date' => d,'hours' => h}
		p['tasks'] = p['tasks'].find_all {|x| x['title'] != t} << task
		project = saveproject(p)
	end

	if post.has_key?('savemember')
		project = savemember(post['project'],post['person'])
	end

	if post.has_key?('savetask')
		project = savetask(post['project'],post['task'],post['person'])
	end

	if post.has_key?('savework')
		p,t,y,m,d,hrs = post['project'],post['task'],post['year'],post['month'],post['date'],post['hours']
		project = savework(p,t,y,m,d,hrs)
	end
	if post.has_key?('setstatus')
		project = settaskstatus(post['project'],post['setstatus'])
	end
	show = post['showall']	
	showproject(project,show)
end

print_header
show_all_projects
check_post(cgi)
print_footer
