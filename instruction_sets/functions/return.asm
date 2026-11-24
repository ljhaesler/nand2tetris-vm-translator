@LCL	// `return` operation
D=M
@R13	// store the end of the frame
M=D
@5
A=D-A
D=M
@R14	// store the returnAddress
M=D

@SP	// get the return value
AM=M-1
D=M
@ARG	// store it at ARG[0]
A=M
M=D
@ARG
D=M
@SP	// move SP to after ARG[0]
M=D+1

@R13	// get frame-1, which is where we stored THAT of caller
AM=M-1
D=M
@THAT	// restore THAT of caller
M=D

// do the same for THIS,ARG,LCL
@R13
AM=M-1
D=M
@THIS
M=D

@R13
AM=M-1
D=M
@ARG
M=D

@R13
AM=M-1
D=M
@LCL
M=D

@R14	// jump to returnAddress
A=M
0;JMP
