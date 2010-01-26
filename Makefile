all:
	python test.py

clean:
	rm -f *.pyc
	rm -f tests/*.pyc
	rm -rf build
	rm -f python-build-stamp-2.5
	rm -rf tvorganise.egg-info
