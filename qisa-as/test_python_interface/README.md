### Python interface for the QISA Assembler
`test_python_interface.py` is used to showcase (and test) the python
interface of the QISA-AS.

The file `../qisa_test_assembly/test_assembly.qisa` is assembled.
The verbose flag is set, so that the instructions are shown as they are
processed.

When the file has been correctly parsed, the resulting instructions are
printed on screen, and saved to a file named `test_assembly.out`.

To demonstrate the dissassembler, this output file (`test_assembly.out`) is
read back in and disassembled.
The output is printed on screen and saved to another file named
`test_disassembly.out`.

Two other functionalities are demonstrated as well: the ability to load new
quantum instructions into QISA-AS, using either a file, or a set of Python
dictionaries.

Once you have built the QISA assembler using the procedure described in the
main README.md file (using the setup.py script), you can run this file as follows:

##### Linux
```
python3 test_python_interface.py
```

##### Windows (PowerShell)
```
python test_python_interface.py
```

### Test QISA_Driver in a loop

In order to check if the assembly and disassembly results remain consistent
between subsequent calls to assemble() and disassemble() without creating a
new instance of QISA_Driver, another test is provided:

* `test_python_interface_loop.py`

It will first assemble the same qisa source file as described above, get
its produced binary instructions, save the assembly results to file and
dissassemble this file.

Then in a loop, it does the same, but at each step it checks if the
generated instructions and dissassembly text match those that were
generated in the initial step.

If no differences have been found in 100 iterations, this program outputs
the following text:

```
====================
=                  =
= ALL TESTS PASSED =
=                  =
====================
```

This program can be run in the same way as described above for
`test_python_interface.py`.
