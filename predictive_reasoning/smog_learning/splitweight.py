correlation_no = ['0','1','2','3','01','02','03','12','13','23','012','013','023','123','0123']

weightfile = open("samples/consistent_weight_010.txt","r")

lines = weightfile.readlines()
for i in range(len(correlation_no)):
	print "dealing with correlation_"+ correlation_no[i] +"...."
	f = open("different_correlation/consistent_weight_010_"+ correlation_no[i] +".txt","w")
	for line in lines:
		correlation = ""
		row = line.split(": ")
		correlation = row[0] + ": "
		dates = row[1].split(";")
		for date in dates:
			if date != '\n':
				cors = date.split("#")
				cur_cor = cors[i]
				correlation = correlation + cur_cor + ";"
		correlation += '\n'
		f.write(correlation)
	f.close()