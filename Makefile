all:
	g++ -fPIC -shared -Ofast -march=native -frename-registers Cpart.cpp -o libCpart.so
