%option reentrant bison-bridge bison-locations
%{
#include <stdio.h>
#include <string.h>
#include "Python.h"
#include "tmp.tab.h"
extern void *py_parser;
extern void (*py_input)(PyObject *parser, char *buf, int *result, int max_size);
PyMODINIT_FUNC PyInit_Parser(void) { /* windows needs this function */ }
#define returntoken(tok) *yylval = (void*)PyUnicode_FromString(strdup(yytext)); return (tok);
#define YY_INPUT(buf,result,max_size) { (*py_input)(py_parser, buf, &result, max_size); }
FILE* flex_logs;
char* log_file = "flex.log";
#define flex_log(...) { flex_logs = fopen(log_file, "a+"); fprintf(flex_logs, __VA_ARGS__); fclose(flex_logs); }
%}



assign :=
number [0-9]*
str \"([^\"[:cntrl:]]+)\"
identifier [a-zA-Z][a-zA-Z]*
array array of


%%

{number} { flex_log("Parsed '%s' number\n", yytext); returntoken(NUMBER); }
{assign} { flex_log("Parsed '%s' assign operator\n", yytext); returntoken(EQUALS); }
"integer" { flex_log("Parsed '%s' var_type\n", yytext); returntoken(INTEGER); }
"string" { flex_log("Parsed '%s' var_type\n", yytext); returntoken(STRING); }
"pointer" { flex_log("Parsed '%s' var_type\n", yytext); returntoken(POINTER); }
"array of" { flex_log("Parsed '%s' var_type\n", yytext); returntoken(ARRAY); }
"mutable" { flex_log("Parsed 'mutable'\n"); returntoken(MUTABLE); }
";"    { flex_log("Parsed ';'\n"); returntoken(SEM); }
"+"    { flex_log("Parsed '+'\n"); returntoken(PLUS); }
"-"    { flex_log("Parsed '-'\n"); returntoken(MINUS); }
"*"    { flex_log("Parsed '*'\n"); returntoken(TIMES); }
"/"    { flex_log("Parsed '/'\n"); returntoken(DIVIDE); }
"%"    { flex_log("Parsed '%'\n"); returntoken(MOD); }
"["    { flex_log("Parsed '['\n"); returntoken(LBRACKET); }
"]"    { flex_log("Parsed ']'\n"); returntoken(RBRACKET); }
"&"    { flex_log("Parsed '&'\n"); returntoken(REF); }
"?"   { flex_log("Parsed '?'\n"); returntoken(SIZE); }
"("    { flex_log("Parsed '('\n"); returntoken(LPAREN); }
")"    { flex_log("Parsed ')'\n"); returntoken(RPAREN); }
"="   { flex_log("Parsed '='\n"); returntoken(OP_EQUAL); }
">"   { flex_log("Parsed '>'\n"); returntoken(OP_GREATER); }
"<"   { flex_log("Parsed '<'\n"); returntoken(OP_LESS); }
".append" { flex_log("Parsed '.append'\n"); returntoken(APPEND); }
"start" { flex_log("Parsed 'start'\n"); returntoken(START); }
"finish" { flex_log("Parsed 'finish'\n"); returntoken(FINISH); }
"while" { flex_log("Parsed 'while'\n"); returntoken(WHILE); }
"instead" { flex_log("Parsed 'instead'\n"); returntoken(INSTEAD); }
"break" { flex_log("Parsed 'break'\n"); returntoken(BREAK); }
"checkzero" { flex_log("Parsed 'checkzero'\n"); returntoken(CHECKZERO); }
"call" { flex_log("Parsed 'call'\n"); returntoken(CALL); }
"with" { flex_log("Parsed 'with'\n"); returntoken(WITH); }
"return" { flex_log("Parsed 'return'\n"); returntoken(RETURN); }
","   { flex_log("Parsed ','\n"); returntoken(COMMA); }
"top" { flex_log("Parsed 'top'\n"); returntoken(TOP); }
"bottom" { flex_log("Parsed 'bottom'\n"); returntoken(BOTTOM); }
"left" { flex_log("Parsed 'left'\n"); returntoken(LEFT); }
"right" { flex_log("Parsed 'right'\n"); returntoken(RIGHT); }
"timeshift" { flex_log("Parsed 'timeshift'\n"); returntoken(TIMESHIFT); }
"bind" { flex_log("Parsed 'bind'\n"); returntoken(BIND); }
{str} { flex_log("Parsed %s string\n", yytext); returntoken(STR); }
{identifier} { flex_log("Parsed '%s' identifier\n", yytext); returntoken(IDENTIFIER); }

[ \t\v\f] {}
.      { flex_log("unknown char %c ignored, yytext=0x%lx\n", yytext[0], yytext); /* ignore bad chars */}

%%

int yywrap(yyscan_t scanner) { return(1); }