# Translating Our VM Language into Assembly
This is a markdown file used to specify the exact assembly instructions required
by each VM instruction.

## add (x + y)
```
pseudo: x=RAM[SP--],y=RAM[SP--],x+y,SP++

@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D+M
@SP
M=M+1
```

A shorter (shortest?) version performs arithmetic directly onto the `A`
register, and uses a few unintuitive tricks to perform the full operation in
only five clock cycles:
```
@SP
AM=M-1 // Setting M here has no effect on M in the next clock cycle
       // regardless of what happens, next cycle, M=RAM[A]
       // basically, SP now points to x, and next cycle, M=RAM[SP--]
D=M    // Therefore, M now holds RAM[A] -> D=x
A=A-1  // Currently, both SP and A hold the pointer to our x value
       // The final result requires that SP still point to the memory space of x
       // So we're better off decrementing A instead.
M=D+M  // M holds RAM[A], and A holds the pointer to our y value -> M=y
       // final state:
       // RAM[SP--] = x + y(t-1), and SP holds the pointer to x -> we're done
```

Interestingly, at no point do we actually zero-out x, so it technically still
exists in memory. For our stack machine VM this is irrelevant, because we
simply treat it as if it were empty.

Fundamentally, the first four instructions are used by every arithmetic and
logic command of our VM. Only the last instruction will really vary between
commands.

## 



