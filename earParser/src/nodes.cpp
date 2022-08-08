#include "nodes.hpp"
#include <iostream>
using std::string;
using std::vector;
using std::cout;
//Constructors
TextNode::TextNode(){}

TextNode::TextNode(string _data, unsigned int _type):
data(std::move(_data)),
type(std::move(_type))
{}

TextNode::TextNode(const TextNode& TN)
{
	data = TN.data;
	type = TN.type;
}
//operators
TextNode TextNode::operator+=(TextNode& next)//concatenates node
{
	switch (type)
	{
	case 0:
		switch (next.type)
		{
			case 0:
				cout << "ERROR: There should not be 2 HTML TextNodes next to eachother.\n";
				break;
			case 1:
				data = "\"\"\"" + data + "\"\"\"" + next.data;
				break;
			case 2:
				data = "\"\"\"" + data + "\"\"\"" + next.execute_earNode();
				break;
		}
		break;
	case 1:
		switch (next.type)
		{
			case 0:
				data = data + "\"\"\"" + next.data + "\"\"\"";
				break;
			case 1:
				cout << "ERROR: There should not be 2 PYTHON TextNodes next to eachother.\n";
				break;
			case 2:
				data = data + next.execute_earNode();
				break;
		}
		break;
	case 2:
		switch (next.type)
		{
			case 0:
				data = execute_earNode() + "\"\"\"" + next.data + "\"\"\"";
				break;
			case 1:
				data = execute_earNode() + next.data;
				break;
			case 2:
				cout << "ERROR: There should not be 2 EARWIG TextNodes next to eachother.\n";
				break;
		}
		break;
	default:
		switch (next.type)
		{
			case 0:
				data = data + "\"\"\"" + next.data + "\"\"\"";
				break;
			case 1:
				data = data + next.data;
				break;
			case 2:
				data = data + next.execute_earNode();
				break;
		}
		break;
	}
	return next;
}
TextNode & TextNode::operator=(TextNode rhs)
{
	data = rhs.data;
	return * this;
}

std::ostream& operator<<(std::ostream& out, const TextNode& TN1)
{
	out << TN1.data;
	return out;
}

string & TextNode::get_data()
{
	return this->data;
}

const unsigned int TextNode::get_type()
{
	return this->type;
}

string TextNode::execute_earNode()
{
	return this->data;
}