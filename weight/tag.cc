#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>

#include <assert.h>
#include <pthread.h>

using namespace std;

#include <ltp/postag_dll.h>
#include <ltp/parser_dll.h>

pthread_mutex_t input_mutex;
pthread_mutex_t output_mutex;

struct param {
    void *pos_engine;
    void *parser_engine;
};

void *kernel(void *engine)
{
    string line_str;
    while (true) {
        // input
        pthread_mutex_lock(&input_mutex);
        if (!getline(cin, line_str)) {
            pthread_mutex_unlock(&input_mutex);
            break;
        }
        pthread_mutex_unlock(&input_mutex);
        
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
        postagger_postag(((param *)engine)->pos_engine, seg_vec, pos_vec);
        assert(seg_vec.size() == pos_vec.size());

        // parser
        vector<int> head_vec;
        vector<string> tag_vec;
        parser_parse(((param *)engine)->parser_engine, seg_vec, pos_vec, head_vec, tag_vec);
        assert(seg_vec.size() == head_vec.size());
        assert(seg_vec.size() == tag_vec.size());

        // output
        pthread_mutex_lock(&output_mutex);
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
        pthread_mutex_unlock(&output_mutex);
    }
}

int main(int argc, char *argv[])
{
    ios_base::sync_with_stdio(false);

    if (argc < 2)
        return -1;

    int thread_num = 64;

    void *pos_engine = postagger_create_postagger(argv[1]);
    void *parser_engine = parser_create_parser(argv[2]);
    struct param engine = {pos_engine, parser_engine};
    pthread_mutex_init(&input_mutex, NULL);
    pthread_mutex_init(&output_mutex, NULL);

    vector<pthread_t> tid_vec;
    for (int i = 0; i < thread_num; ++i) {
        pthread_t tid;
        int ret = pthread_create(&tid, NULL, kernel, &engine);
        if (ret) {
            cout << "Create thread error." << endl;
            return 1;
        }
        tid_vec.push_back(tid);
    }
    for (vector<pthread_t>::const_iterator iter = tid_vec.begin(); iter != tid_vec.end(); ++iter) {
        pthread_join(*iter, NULL);
    }
    pthread_mutex_destroy(&input_mutex);
    pthread_mutex_destroy(&output_mutex);
    return 0;
}
