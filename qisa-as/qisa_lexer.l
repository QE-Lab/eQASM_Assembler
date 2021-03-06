%{ /* -*- C++ -*- */
# include <cerrno>
# include <climits>
# include <cstdlib>
# include <string>
# include <cstdio>

/* include for all driver functions */
#include "qisa_driver.h"

/* Forward declarations */
int64_t text_to_long(QISA::QISA_Driver& driver, const char* text, int base);
uint8_t text_to_uint8(QISA::QISA_Driver& driver, const char* text);

// The location of the current token.
static QISA::location loc;
%}

%option reentrant
%option debug
%option nodefault
%option noyywrap
%option nounput
%option noinput
%option case-insensitive

delim         [ \t]
whitesp       {delim}+
digit         [0-9]
alpha         [a-zA-Z]
alphanum      [a-zA-Z0-9]
number        [-]?{digit}*[.]?{digit}+
integer       [-]?{digit}+
hex           "0x"[0-9a-fA-F]+
binary        "0b"[01]+
string        \"[^\"]*\"
q_reg         [qQ]{digit}+
r_reg         [rR]{digit}+
s_reg         [sS]{digit}+
t_reg         [tT]{digit}+
comment       "#"[^\n]*
identifier    {alpha}[a-zA-Z0-9_]*

%{
  /* update location on matching */
  # define YY_USER_ACTION  loc.columns (yyleng);
%}

%%
%{
  // Code run each time yylex is called.
  loc.step ();
%}

 /* Update location on whitespace and comments. */
{whitesp}      { loc.step (); }
{comment}      { loc.step (); }

{q_reg}        { return QISA::QISA_Parser::make_Q_REGISTER(text_to_uint8(driver, yytext+1    ), loc); }
{r_reg}        { return QISA::QISA_Parser::make_R_REGISTER(text_to_uint8(driver, yytext+1    ), loc); }
{s_reg}        { return QISA::QISA_Parser::make_S_REGISTER(text_to_uint8(driver, yytext+1    ), loc); }
{t_reg}        { return QISA::QISA_Parser::make_T_REGISTER(text_to_uint8(driver, yytext+1    ), loc); }
{integer}      { return QISA::QISA_Parser::make_INTEGER(text_to_long(driver,   yytext,   10), loc); }
{hex}          { return QISA::QISA_Parser::make_INTEGER(text_to_long(driver,   yytext+2, 16), loc); }
{binary}       { return QISA::QISA_Parser::make_INTEGER(text_to_long(driver,   yytext+2,  2), loc); }


"\n"           { loc.lines (yyleng); loc.step (); return QISA::QISA_Parser::make_NEWLINE(loc); }
","            { return QISA::QISA_Parser::make_COMMA(loc); }
":"            { return QISA::QISA_Parser::make_COLON(loc); }
"|"            { return QISA::QISA_Parser::make_VBAR(loc); }
"{"            { return QISA::QISA_Parser::make_BRACE_OPEN(loc); }
"}"            { return QISA::QISA_Parser::make_BRACE_CLOSE(loc); }
"("            { return QISA::QISA_Parser::make_PAREN_OPEN(loc); }
")"            { return QISA::QISA_Parser::make_PAREN_CLOSE(loc); }

 /* Branch conditions. */
"ALWAYS"       { return QISA::QISA_Parser::make_COND_ALWAYS  (QISA::QISA_Driver::COND_ALWAYS  , loc); }
"NEVER"        { return QISA::QISA_Parser::make_COND_NEVER   (QISA::QISA_Driver::COND_NEVER   , loc); }
"EQ"           { return QISA::QISA_Parser::make_COND_EQ      (QISA::QISA_Driver::COND_EQ      , loc); }
"NE"           { return QISA::QISA_Parser::make_COND_NE      (QISA::QISA_Driver::COND_NE      , loc); }
"EQZ"          { return QISA::QISA_Parser::make_COND_EQZ     (QISA::QISA_Driver::COND_EQZ     , loc); }
"NEZ"          { return QISA::QISA_Parser::make_COND_NEZ     (QISA::QISA_Driver::COND_NEZ     , loc); }
"LT"           { return QISA::QISA_Parser::make_COND_LT      (QISA::QISA_Driver::COND_LT      , loc); }
"LTZ"          { return QISA::QISA_Parser::make_COND_LTZ     (QISA::QISA_Driver::COND_LTZ     , loc); }
"LE"           { return QISA::QISA_Parser::make_COND_LE      (QISA::QISA_Driver::COND_LE      , loc); }
"GT"           { return QISA::QISA_Parser::make_COND_GT      (QISA::QISA_Driver::COND_GT      , loc); }
"GE"           { return QISA::QISA_Parser::make_COND_GE      (QISA::QISA_Driver::COND_GE      , loc); }
"GEZ"          { return QISA::QISA_Parser::make_COND_GEZ     (QISA::QISA_Driver::COND_GEZ     , loc); }
"LTU"          { return QISA::QISA_Parser::make_COND_LTU     (QISA::QISA_Driver::COND_LTU     , loc); }
"LEU"          { return QISA::QISA_Parser::make_COND_LEU     (QISA::QISA_Driver::COND_LEU     , loc); }
"GTU"          { return QISA::QISA_Parser::make_COND_GTU     (QISA::QISA_Driver::COND_GTU     , loc); }
"GEU"          { return QISA::QISA_Parser::make_COND_GEU     (QISA::QISA_Driver::COND_GEU     , loc); }
"CARRY"        { return QISA::QISA_Parser::make_COND_CARRY   (QISA::QISA_Driver::COND_CARRY   , loc); }
"NOTCARRY"     { return QISA::QISA_Parser::make_COND_NOTCARRY(QISA::QISA_Driver::COND_NOTCARRY, loc); }

 /* Classic low-level instructions. */
"NOP"          { return QISA::QISA_Parser::make_NOP(loc); }
"STOP"         { return QISA::QISA_Parser::make_STOP(loc); }
"ADD"          { return QISA::QISA_Parser::make_ADD(loc); }
"SUB"          { return QISA::QISA_Parser::make_SUB(loc); }
"ADDC"         { return QISA::QISA_Parser::make_ADDC(loc); }
"SUBC"         { return QISA::QISA_Parser::make_SUBC(loc); }
"AND"          { return QISA::QISA_Parser::make_AND(loc); }
"OR"           { return QISA::QISA_Parser::make_OR(loc); }
"XOR"          { return QISA::QISA_Parser::make_XOR(loc); }
"NOT"          { return QISA::QISA_Parser::make_NOT(loc); }
"CMP"          { return QISA::QISA_Parser::make_CMP(loc); }
"BR"           { return QISA::QISA_Parser::make_BR(loc); }
"LDI"          { return QISA::QISA_Parser::make_LDI(loc); }
"LDUI"         { return QISA::QISA_Parser::make_LDUI(loc); }
"FBR"          { return QISA::QISA_Parser::make_FBR(loc); }
"FMR"          { return QISA::QISA_Parser::make_FMR(loc); }
"SMIS"         { return QISA::QISA_Parser::make_SMIS(loc); }
"SMIT"         { return QISA::QISA_Parser::make_SMIT(loc); }

 /* Quantum instructions that use the same (single) instruction format. */
"QWAIT"        { return QISA::QISA_Parser::make_QWAIT(loc); }
"QWAITR"       { return QISA::QISA_Parser::make_QWAITR(loc); }

 /* Aliases, that may result in another or more classic low-level instructions. */
"SHL1"         { return QISA::QISA_Parser::make_SHL1(loc); }
"NAND"         { return QISA::QISA_Parser::make_NAND(loc); }
"NOR"          { return QISA::QISA_Parser::make_NOR(loc); }
"XNOR"         { return QISA::QISA_Parser::make_XNOR(loc); }
"BRA"          { return QISA::QISA_Parser::make_BRA(loc); }
"GOTO"         { return QISA::QISA_Parser::make_GOTO(loc); }
"BRN"          { return QISA::QISA_Parser::make_BRN(loc); }
"BEQ"          { return QISA::QISA_Parser::make_BEQ(loc); }
"BNE"          { return QISA::QISA_Parser::make_BNE(loc); }
"BLT"          { return QISA::QISA_Parser::make_BLT(loc); }
"BLE"          { return QISA::QISA_Parser::make_BLE(loc); }
"BGT"          { return QISA::QISA_Parser::make_BGT(loc); }
"BGE"          { return QISA::QISA_Parser::make_BGE(loc); }
"BLTU"         { return QISA::QISA_Parser::make_BLTU(loc); }
"BLEU"         { return QISA::QISA_Parser::make_BLEU(loc); }
"BGTU"         { return QISA::QISA_Parser::make_BGTU(loc); }
"BGEU"         { return QISA::QISA_Parser::make_BGEU(loc); }
"COPY"          { return QISA::QISA_Parser::make_COPY(loc); }
"MOV"         { return QISA::QISA_Parser::make_MOV(loc); }
"MULT2"        { return QISA::QISA_Parser::make_MULT2(loc); }


 /* Bundle separator */
"BS"           { return QISA::QISA_Parser::make_BS(loc); }

 /* Specifies a conditional single qubit quantum instruction. */
"C,"           { return QISA::QISA_Parser::make_COND_Q_INSTR_ST(loc); }


 /* Directives */

 /* Define a new symbol. Acts as a named constant. */
".def_sym"     { return QISA::QISA_Parser::make_DIR_DEF_SYMBOL(loc); }

 /* Assign a name to a register. */
".register"    { return QISA::QISA_Parser::make_DIR_REGISTER(loc); }

{string}       { return QISA::QISA_Parser::make_STRING(yytext, loc); }
{identifier}   { return QISA::QISA_Parser::make_IDENTIFIER(yytext, loc); }

\r             { /* ignore carriage returns. */ }
.              { return QISA::QISA_Parser::make_JUNK(yytext, loc); }

 /* This is a trick to always generate an extra new line at the end of file.
  * It prevents the parser to give an error message in case the last line of a file is not properly terminated.
  * The idea comes from: https://stackoverflow.com/a/1779949
  */
<<EOF>> { if (driver.hadEOF())
           {
             return QISA::QISA_Parser::make_END(loc);
           }
           else
           {
             driver.haveEOF();
             return QISA::QISA_Parser::make_NEWLINE(loc);
           }
        }

%%

int64_t text_to_long(QISA::QISA_Driver& driver, const char* text, int base)
{
  errno = 0;
  int64_t n = strtol (text, NULL, base);

  if (errno == ERANGE)
    driver.error (loc, "value is out of range for int64_t");
  return n;
}


uint8_t text_to_uint8(QISA::QISA_Driver& driver, const char* text)
{
  errno = 0;
  long n = strtol (text, NULL, 10);

  if ((errno == ERANGE) ||
      (n < 0) ||
      (n > 255))
    driver.error (loc, "value is out of range for uint8_t");

  return (uint8_t)n;
}



bool
QISA::QISA_Driver::scanBegin(yyscan_t* flex_scanner)
{
  yylex_init(flex_scanner);

  // This is needed to make the yy_flex_debug and yyin macros work.
  struct yyguts_t * yyg = (struct yyguts_t*)*flex_scanner;

  // Initialize the static variable loc.
  // Otherwise, the current location keeps increasing each time
  // a new file is processed.
  loc = location();

  yy_flex_debug = _traceScanning;

  if (!(yyin = fopen (_filename.c_str (), "r")))
  {
    error("Cannot open file '" + _filename + "': " + strerror(errno));

    // Return false to indicate failure;
    return false;
  }

  fseek (yyin, 0, SEEK_END);
  size_t size = ftell(yyin);

  if (size == 0) {
    error("File '" + _filename + "' is empty!");

    // Return false to indicate failure;
    return false;
  }

  rewind(yyin);

  // Return true to indicate success;
  return true;
}

void
QISA::QISA_Driver::scanEnd(yyscan_t flex_scanner)
{
  // This is needed to make the yyin macro work.
  struct yyguts_t * yyg = (struct yyguts_t*)flex_scanner;

  fclose (yyin);

  yylex_destroy(flex_scanner);
}
