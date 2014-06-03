import fnmatch
import os


path="/test"#/00-04-25"
i=0

for folder in os.listdir('.'+path):
	for file in os.listdir('.'+path+'/'+folder):
		if fnmatch.fnmatch(file, 'politics*.raw'):
			try:				
				data = open('.'+path+'/'+folder+'/'+file, 'r').read()
				f = open('./test1/politics/politics'+str(i), 'w')
				f.write(data)
			except Exception, e:
				print e
			finally:
				f.close()
			i=i+1
