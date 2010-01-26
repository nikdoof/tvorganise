all:
	python test.py

clean:
	rm *.pyc
	rm test/*.pyc
	rm -rf build

