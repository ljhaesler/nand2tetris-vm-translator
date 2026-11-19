	@SP	// `lt` operation
	AM=M-1
	D=M
	A=A-1
	D=M-D
	M=-1
	@LT_TRUE_%(qty)s
	D;JLT
	@SP
	A=M-1
	M=0
(LT_TRUE_%(qty)s)
