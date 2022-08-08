#include "nodes.hpp"
#include <fstream>
#include <sstream>
#include <iostream>
#include <cstring>
using std::string;
using std::vector;
using std::cout;
using std::fstream;
using std::stringstream;
enum type {html, python, earwig, globalType};
//opens the file and executes preprocessor code
string file_preprocessor(const char * filepath)
{
	//cout << "FilePath: " << filepath << '\n';
	fstream rootfile(filepath);
	stringstream fileStream;
	fileStream << rootfile.rdbuf();
	string rootfileContents = fileStream.str();
	rootfile.close();
	string parsedFile = tokenize_file(rootfileContents);
	//result = (char*)calloc(strlen(parsedFile.c_str()), sizeof(char));
	return parsedFile;
}
//tokenizes file for fast concatenation
string tokenize_file(string file)
{
	vector<TextNode*> globalScope;
	unsigned int currentType = html;
	string buffer = "";
	char lastCharacter = ' ';
	for (char character : file)
	{
		switch (character)
		{
		case '<':
			break;
		case '?':
			if (lastCharacter == '<' && currentType != python)
			{
				globalScope.push_back(new TextNode(buffer, (unsigned int)currentType));
				buffer = "";
				currentType = python;
			}
			else if (lastCharacter == '<')
			{
				cout << "Error: You have an extra opening python bracket.\n";
			}
			break;
		case '>':
			if (lastCharacter == '?')
			{
				globalScope.push_back(new TextNode(buffer, (unsigned int)currentType));
				buffer = "";
				currentType = html;
			}
			else if (lastCharacter == '@')
			{
				globalScope.push_back(new TextNode(buffer, (unsigned int)currentType));
				buffer = "";
				currentType = html;
			}
			else
			{
				buffer.push_back('>');
			}
			break;
		case '@':
			if (lastCharacter == '<' && currentType != earwig)
			{
				globalScope.push_back(new TextNode(buffer, (unsigned int)currentType));
				buffer = "";
				currentType = earwig;
			}
			else if (lastCharacter == '<')
			{
				cout << "Error: You have an extra opening earwig bracket.\n";
			}
			else
			{
				buffer.push_back('@');
			}
			break;
		
		default:
			if (lastCharacter == '<')
			{
				buffer.push_back('<');
			}
			else if (lastCharacter == '?' && currentType != python)
			{
				buffer.push_back('?');
			}
			else if (lastCharacter == '@' && currentType != earwig)
			{
				buffer.push_back('@');
			}
			buffer.push_back(character);
			break;
		}
		lastCharacter = character;
	}
	TextNode * compilerNode = new TextNode("", (unsigned int)globalType);
	for (std::size_t i = 0; i < globalScope.size(); ++i)
	{
		*compilerNode += *(globalScope[i]);
		delete globalScope[i];
	}
	globalScope.clear();
	//cout << compilerNode->get_data().c_str() << '\n';
	string returnval = std::move(compilerNode->get_data());
	delete compilerNode;
	return returnval;
}