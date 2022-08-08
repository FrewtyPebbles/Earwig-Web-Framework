#include "nodes.hpp"
#include <iostream>
#include <sstream>
using std::cout;
int main(int argc, char const ** argv)
{
	if (argc > 0)
	{
		cout << file_preprocessor(argv[1]);
	}
	return 0;
}