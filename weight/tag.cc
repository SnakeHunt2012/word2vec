#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>

#include <assert.h>

using namespace std;

#include <ltp/postag_dll.h>
#include <ltp/parser_dll.h>

int main(int argc, char *argv[])
{
    ios_base::sync_with_stdio(false);

    if (argc < 2)
        return -1;

    void *pos_engine = postagger_create_postagger(argv[1]);
    void *parser_engine = parser_create_parser(argv[2]);

    string line_str;
    while (getline(cin, line_str)) {
        // routine inspection
        if (count(line_str.begin(), line_str.end(), '\t') != 1)
            continue;

        // ori_str, seg_str
        istringstream line_stream(line_str);
        string ori_str; getline(line_stream, ori_str, '\t');
        string seg_str; getline(line_stream, seg_str, '\t');
        assert(line_stream.eof());

        // seg_vec
        istringstream seg_stream(seg_str);
        vector<string> seg_vec;
        string seg;
        while (seg_stream >> seg)
            seg_vec.push_back(seg);

        // pos
        vector<string> pos_vec;
        postagger_postag(pos_engine, seg_vec, pos_vec);
        assert(seg_vec.size() == pos_vec.size());

        // parser
        vector<int> head_vec;
        vector<string> tag_vec;
        parser_parse(parser_engine, seg_vec, pos_vec, head_vec, tag_vec);
        assert(seg_vec.size() == head_vec.size());
        assert(seg_vec.size() == tag_vec.size());

        // output
        cout << ori_str << "\t";
        bool first_flag = true;
        for (size_t i = 0; i < seg_vec.size(); ++i) {
            if (first_flag)
                first_flag = false;
            else
                cout << " ";
            cout << seg_vec[i] << "/" << pos_vec[i] << "/" << head_vec[i] << "/" << tag_vec[i];
        }
        cout << endl;
    }
    return 0;
}
