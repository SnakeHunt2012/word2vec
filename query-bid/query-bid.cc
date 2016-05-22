#include <stdio.h>
#include <stdlib.h>
#include <argp.h>

using namespace std;

const char *argp_program_version = "query-bid 1.0";
const char *argp_program_bug_address = "<huangjingwen@360.cn>";

static char prog_doc[] = "Find the most relevent bidwords for each given query."; /* Program documentation. */
static char args_doc[] = "QUERY_FILE BIDWORD_FILE"; /* A description of the arguments we accept. */

/* Keys for options without short-options. */
#define OPT_HASH_LENGTH          1
#define OPT_HASH_NUMBER          2
#define OPT_HAMMING_DISTANCE     3
#define OPT_SIMILARITY_THRESHOLD 4
#define OPT_DEBUG                5
#define OPT_PROFILE              6
#define OPT_PARTITION            7

/* The options we understand. */
static struct argp_option options[] = {
    {"verbose", 'v', 0, 0, "produce verbose output"},
    {"quite",   'q', 0, 0, "don't produce any output"},
    {"silent",  's', 0, OPTION_ALIAS},

    {0,0,0,0, "The following options are about algorithm:" },
    
    {"hash-length",          OPT_HASH_LENGTH,          "LENGTH",   0, "hash length"},
    {"hash-number",          OPT_HASH_NUMBER,          "NUMBER",   0, "hash number"},
    {"hamming-distance",     OPT_HAMMING_DISTANCE,     "DISTANCE", 0, "hamming distance"},
    {"similarity-threshold", OPT_SIMILARITY_THRESHOLD, "SCORE",    0, "only bidwords with similarity more than SCORE will be output"},

    {0,0,0,0, "The following options are about output format:" },
    
    {"output",    'o',           "FILE", 0, "output to FILE instead of standard output"},
    {"debug",     OPT_DEBUG,          0, 0, "output similarity score for every bidwords and length of candidate set (before and after filtering)"},
    {"profile",   OPT_PROFILE,        0, 0, "output similarity score for every bidwords"},
    {"partition", OPT_PARTITION,      0, 0, "output partition information"},
    
    { 0 }
};

/* Used by main to communicate with parse_opt. */
struct arguments
{
    char *query_file, *bidword_file, *output_file;
    bool verbose, silent, debug, profile, partition;
    int hash_length, hash_number, hamming_distance;
    double similarity_threshold;
};

/* Parse a single option. */
static error_t parse_opt(int key, char *arg, struct argp_state *state)
{
    struct arguments *arguments = (struct arguments *) state->input;
    switch (key)
        {
        case 'v':
            arguments->verbose = true;
            break;
        case 'q': case 's':
            arguments->silent = true;
            break;
        case 'o':
            arguments->output_file = arg;
            break;
        case OPT_HASH_LENGTH:
            arguments->hash_length = atoi(arg);
            break;
        case OPT_HASH_NUMBER:
            arguments->hash_number = atoi(arg);
            break;
        case OPT_HAMMING_DISTANCE:
            arguments->hamming_distance = atoi(arg);
            break;
        case OPT_SIMILARITY_THRESHOLD:
            arguments->similarity_threshold = atof(arg);
            break;
        case OPT_DEBUG:
            arguments->debug = true;
            break;
        case OPT_PROFILE:
            arguments->profile = true;
            break;
        case OPT_PARTITION:
            arguments->partition = true;
            break;
            
        case ARGP_KEY_ARG:
            if (state->arg_num == 0) arguments->query_file = arg;
            if (state->arg_num == 1) arguments->bidword_file = arg;
            if (state->arg_num >= 2) argp_usage(state);
            break;
            
        case ARGP_KEY_END:
            if (state->arg_num < 2) argp_usage(state);
            break;
            
        case ARGP_KEY_NO_ARGS:
            argp_usage(state);
            break;
            
        default:
            return ARGP_ERR_UNKNOWN;
        }
    return 0;
}

/* Our argp parser. */
static struct argp argp = { options, parse_opt, args_doc, prog_doc };

int main(int argc, char *argv[])
{
    struct arguments arguments;
    arguments.query_file = NULL;
    arguments.bidword_file = NULL;
    arguments.output_file = NULL;
    arguments.verbose = false;
    arguments.silent = true;
    arguments.debug = false;
    arguments.profile = false;
    arguments.partition = false;
    arguments.hash_length = 13;
    arguments.hash_number = 1;
    arguments.hamming_distance = 2;
    arguments.similarity_threshold = 0.5;
    argp_parse(&argp, argc, argv, 0, 0, &arguments);

    fprintf(stderr, "query_file: %s\n", arguments.query_file);
    fprintf(stderr, "bidword_file: %s\n", arguments.bidword_file);
    fprintf(stderr, "output_file: %s\n", arguments.output_file);
    fprintf(stderr, "verbose: %d\n", arguments.verbose);
    fprintf(stderr, "silent: %d\n", arguments.silent);
    fprintf(stderr, "debug: %d\n", arguments.debug);
    fprintf(stderr, "profile: %d\n", arguments.profile);
    fprintf(stderr, "partition: %d\n", arguments.partition);
    fprintf(stderr, "hash_length: %d\n", arguments.hash_length);
    fprintf(stderr, "hash_number: %d\n", arguments.hash_number);
    fprintf(stderr, "hamming_distance: %d\n", arguments.hamming_distance);
    fprintf(stderr, "similarity_threshold: %f\n", arguments.similarity_threshold);

    return 0;
}
