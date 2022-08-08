#include <string>
#include <vector>
using std::string;
using std::vector;

class TextNode{
	public:
		//constructors
		TextNode();
		TextNode(string _data, unsigned int _type);
		TextNode(const TextNode& TN);
		//operators
		TextNode operator+=(TextNode & next);
		TextNode& operator=(TextNode rhs);
		friend std::ostream& operator<<(std::ostream& out, const TextNode& TN1);
		//accessors
		string& get_data();
		const unsigned int get_type();
		//parser
		string execute_earNode();
	private:
		//attributes
		string data;
		vector<TextNode*> scope;
		unsigned int type = 0;// 0 is an html TextNode, 1 is a python TextNode, 2 is an earwig TextNode
};

extern "C" string file_preprocessor(const char * filepath);
string tokenize_file(string file);