
all: ../nord/g2/modules.py ../nord/nm1/modules.py

../nord/g2/modules.py: g2db.py
	./g2db.py
	python ../nord/g2/modules.py >../g2db.txt

../nord/nm1/modules.py: nmdb.py
	./nmdb.py
	python ../nord/nm1/modules.py >../nmdb.txt

