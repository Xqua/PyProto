#!/usr/bin/env python
from xml.dom import minidom
import os
import progressbar
from progressbar import Bar, ProgressBar, ReverseBar, ETA
from time import sleep



class Protocol:
	
	def __init__(self, path):
		self.setting = {"temp" : "C"}
		self.load(path)

	def load(self, path):
		xml = minidom.parse(path)
		self.title = xml.getElementsByTagName('Title')[0].childNodes[0].wholeText
		self.abstract = xml.getElementsByTagName('Abstract')[0].childNodes[0].wholeText
		self.materials = xml.getElementsByTagName('Materials')[0].getElementsByTagName('Item')
		self.get_ids()
		self.steps = xml.getElementsByTagName('Steps')[0].getElementsByTagName('Step')
		self.nb_step = len(self.steps)

	def get_ids(self):
		if len(self.materials) == 0:
			return False
		self.ids = {}
		for el in self.materials:
			Id = el.attributes['id'].value
			if el.hasAttribute('name'):
				name = el.attributes['name'].value
			else:
				name = el.childNodes[0].wholeText
			self.ids[Id] = name

	def Replace_Description(self, txt):
		for Id in self.ids.keys():
			txt = txt.replace('{%'+ Id +'%}', '\033[34m' + self.ids[Id] + '\033[0m')
		return txt

	def get_step(self, i):
		if i > len(self.steps):
			return False
		res = {"Number":i, "Description":None, "Time":None,"Temperature":None, "Repeat":1, "Warning":None}
		step = self.steps[i]
		if step.getElementsByTagName('Description'):
			res['Description'] = self.Replace_Description(step.getElementsByTagName('Description')[0].childNodes[0].wholeText)
		if step.getElementsByTagName('Time'):
			time = step.getElementsByTagName('Time')[0].childNodes[0].wholeText
			time = int(step.getElementsByTagName('Time')[0].childNodes[0].wholeText)
			unit = step.getElementsByTagName('Time')[0].attributes['unit'].value
			if unit.lower() == 'h':
				factor = 3600
			elif unit.lower() == 'm' or unit.lower() == 'mn':
				factor = 60
			elif unit.lower() == 'd':
				factor = 86400
			res['Time'] = time * factor
		if step.getElementsByTagName('Temperature'):
			t = step.getElementsByTagName('Temperature')[0].childNodes[0].wholeText
			unit = step.getElementsByTagName('Temperature')[0].attributes['unit'].value
			if unit.upper() != self.setting['temp']:
				if unit == 'F':
					t = 5/9 * (t-32)
				else:
					t = 9/5 * (t+32) 
			res['Temperature'] = "%s %s" % (t, self.setting['temp'])
		if step.getElementsByTagName('Repeat'):
			res['Repeat'] = int(step.getElementsByTagName('Repeat')[0].childNodes[0].wholeText)
		if step.getElementsByTagName('Warning'):
			res['Warning'] = step.getElementsByTagName('Warning')[0].childNodes[0].wholeText
		return res


		

class Main:
	
	def __init__(self):
		self.proto_path = './Protocols'
		self.list_proto = []
		self.ls = os.listdir(self.proto_path)
		self.Load_List()

	def Load_List(self):
		todel = []
		for i in range(len(self.ls)):
			try:
				xml = minidom.parse(self.proto_path + '/' + self.ls[i])
				title = xml.getElementsByTagName('Title')[0].childNodes[0].wholeText
				abstract = xml.getElementsByTagName('Abstract')[0].childNodes[0].wholeText
				self.list_proto.append((title,abstract))
			except Exception, e:
				print e
				print "file : %s is not XML or does not contain the right informations." % self.ls[i]
				todel.append(i)
		for i in todel:
			del self.ls[i]

	def Run(self):
		print  """Welcome to the protocol XML muxinator ! 
		It takes a poney mashes it and gets you somewhere you've never been !"""
		print "Here is the list of all the protocols you have installed."
		print "Title\tAbstract"
		for i in range(len(self.list_proto)):
			print "%s: %s\t%s" % (i+1, self.list_proto[i][0], self.list_proto[i][1])
		choice = raw_input("Please choose a protocol to follow: ")
		choice = int(choice) - 1
		print "Protocol Selected : \n %s" % self.list_proto[choice][0]
		self.Run_Protocol(choice)

	def Run_Protocol(self, i):
		Proto = Protocol(self.proto_path + '/' + self.ls[i])
		print "For this experiment you will need :"
		self.Display_Materials(Proto)
		for i in range(Proto.nb_step):
			step = Proto.get_step(i)
			self.Display_Step(step)

	def Display_Step(self, step):
		for rep in range(step['Repeat']):
			os.system('clear')
			print "Step Number : %s \n\n" % step['Number']
			if step['Repeat'] > 1:
				print "Repeat : %s/%s\n" % (rep, step['Repeat']) 
			if step['Temperature']:
				print "Temperature for this step is : %s" % step['Temperature']
			else:
				print " "
			if step['Warning']:
				print "\033[01;31m\t\t%s\033[00m" % step['Warning']
			else:
				print " "
			# .Replace_Description(step['Description'])
			print step['Description']
			print "\n\n"
			if step['Time']:
				print "Time for this step is : %s"  % step['Time']
				self.Wait_for('', 'Start Timer ? ')
				self.Timer(step['Time'])
				self.Wait_for('','Next Step ?')
			else:
				self.Wait_for('','Finished ? ')

	def Timer(self, t):
		self.eta = "00-00-00"
		widgets = [Bar('>'), ' ', ETA(), ' ', ReverseBar('<')]
		pbar = ProgressBar(widgets=widgets, maxval=t).start()
		for i in range(t*10):
			try:
			    sleep(.1)
			    pbar.update(i*.1)
			except KeyboardInterrupt:
				break
		pbar.finish()

	def Wait_for(self, answer, message):
		a = answer + "rrr"
		while a.lower() != answer:
			a = raw_input(message)
			
	def Display_Materials(self, Proto):
		os.system('clear')
		for mat in Proto.materials:
			Id = mat.attributes['id'].value
			name = Proto.ids[Id]
			Description = mat.childNodes[0].wholeText
			print "\033[34m%s\033[0m\t%s" % (name, Description)
		self.Wait_for('','Ready ?')

if __name__=='__main__':
	M = Main()
	M.Run()