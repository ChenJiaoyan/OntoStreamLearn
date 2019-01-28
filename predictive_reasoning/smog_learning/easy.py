import csv
f = open("result3.txt","r")
g = open("result_tmp.csv","w")
writer = csv.writer(g)
lines = f.readlines()
flag = 0
cur = 0
row = []
for line in lines:
	flag = flag + 1	
	if flag % 2 == 1:
		continue
	row.append(line.strip())
	if len(row) == 9:
		writer.writerow(row)
		row = []
	

