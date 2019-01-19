set i=0
:while1
	set j=50
	:while2
		python SGD_weight_eva_2.py %i% %j%
		echo %i% %j%
		set /A j=%j%+5
		if %j%==95 goto :end2
		goto :while2
	:end2
	set /A i=%i%+1
	if %i%==15 goto :end1
	goto :while1
:end1
