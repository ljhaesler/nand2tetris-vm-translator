	@SP	// `call` operation
	D=M	// we start by finding the position of callee ARG
	@%(nArgs)s
	D=D-A	// which is at SP-nArgs
	@R13
	M=D

	@%(function)s$ret.%(index)s	// push the returnAddress onto stack
	D=A
	@SP
	A=M
	M=D
	@SP
	M=M+1

	@LCL	// push LCL of caller onto stack
	D=M
	@SP
	A=M
	M=D
	@SP
	M=M+1

	@ARG	// push ARG of caller onto stack
	D=M
	@SP
	A=M
	M=D
	@SP
	M=M+1

	@THIS	// push THIS of caller onto stack
	D=M
	@SP
	A=M
	M=D
	@SP
	M=M+1

	@THAT	// push THAT of caller onto stack
	D=M
	@SP
	A=M
	M=D
	@SP
	M=M+1

	@R13	// reposition ARG (calculated before)
	D=M
	@ARG
	M=D

	@SP	// reposition LCL
	D=M
	@LCL
	M=D

	@%(function)s	// call the function declared by `function.asm`
	0;JMP

(%(function)s$ret.%(index)s) // execution resumes here after `return.asm`
