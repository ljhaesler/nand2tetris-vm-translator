(%(function)s)	// `function` operation
	@%(nVars)s
	D=A
	@R13
	M=D
	@%(function)s.InitEnd
	D;JEQ

(%(function)s.InitStart)
	@SP
	A=M
	M=0
	@SP
	M=M+1
	@R13
	MD=M-1
	@%(function)s.InitStart
	D;JGT

(%(function)s.InitEnd)
	// function execution code starts here
