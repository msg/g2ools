
all: ../nord/g2/modules.py ../nord/nm1/modules.py ../nord/units.py \
		../nord/convert/table.py ../dxtable.py

../nord/g2/modules.py: g2db.py module_table.txt param_table.txt
	./g2db.py
	python ../nord/g2/modules.py >../g2db.txt

../nord/nm1/modules.py: nmdb.py patch303.txt
	./nmdb.py
	python ../nord/nm1/modules.py >../nmdb.txt

../nord/units.py: unitsdb.py nm1adsrtime.txt g2adsrtime.txt \
	nm1fltfreq.txt g2fltfreq.txt nm1logictime.txt g2logictime.txt \
	nm1levamp.txt g2levamp.txt ratios.txt g2glidetime.txt \
	nm1smoothtime.txt
	./unitsdb.py

../nord/convert/table.py: gentab.py mix2-1b.txt spectral.txt nm1pitch.txt \
		kbt.txt notescale.txt glide.txt fmb.txt wavewrap.txt \
		logicdel.txt lphpfreq.txt
	./gentab.py

../dxtable.py: dxgen.py dxlfo.txt dxamodsens.txt dxlfodelay.txt dxpitcheg.txt \
		dxpmodsens.txt
	./dxgen.py
