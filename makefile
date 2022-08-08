sp = earParser/src/
successMSG = .ear handler compiled with default settings.
earwig: $(sp)main.cpp $(sp)nodes.hpp $(sp)nodes.cpp $(sp)tokenizer.cpp
	g++ -Wall -pedantic -std=c++11 -o earwigParser $(sp)main.cpp $(sp)nodes.hpp $(sp)nodes.cpp $(sp)tokenizer.cpp
	echo $(successMSG)