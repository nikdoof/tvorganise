all:
	./setup.py test

clean:
	rm -f *.pyc
	rm -f tests/*.pyc
	rm -rf build
	rm -f python-build-stamp-2.5
	rm -rf dist

dpkg:
	dpkg-buildpackage
