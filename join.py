f = open('art.dat', 'w')
for i in range(0,663):
	data = open('art'+str(i), 'r').read()
	f.write(data)
f.close()
