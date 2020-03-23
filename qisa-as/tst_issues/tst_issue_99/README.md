As stated in issue #99, the assembler should support both single and double
quotes when specifying instruction names.

In this directory are two files containing quantum instruction set
specifications, one using single quotes (_'qmap\_single\_quotes.qmap'_) and
one using double quotes (_'qmap\_double\_quotes.qmap'_).

To test the correct implementation:

* `qisa-as -q qmap_single_quotes.qmap --dumpspecs`
* `qisa-as -q qmap_double_quotes.qmap --dumpspecs`

It should give the exact same output (note that the double quotes are not preserved...).
