
all: ../nord/g2/modules.py ../nord/nm1/modules.py

../nord/g2/modules.py: g2db.py module_table.txt param_table.txt
	./g2db.py
	python ../nord/g2/modules.py >../g2db.txt

../nord/nm1/modules.py: nmdb.py patch303.txt
	./nmdb.py
	python ../nord/nm1/modules.py >../nmdb.txt

