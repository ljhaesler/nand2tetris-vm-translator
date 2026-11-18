# Translating Our VM Language into Assembly
This is a markdown file used to specify the exact assembly instructions required
by each VM instruction.

## Arithmetic Instructions
### add (x + y)
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
commands, so I will omit the first four instructions from now on.


### sub (x - y)
The logic above was written assuming that `x` was at the top of the stack, but
according to the spec `y` is considered to be the top of the stack. This is
fine for addition, but for subtraction we'd be performing `y - x` rather than
`x - y`.

```
Fixed for y at top of stack:

@SP
AM=M-1 // -> SP points to y, A fetches y
D=M    // -> D=M=y
A=A-1  // -> A fetches x
       // -> this logic remains unchanged
M=M-D  // -> D=y, M=x, so M=x-y, SP still points to y, which is 'empty' now
```

### and (x & y)
`M=D&M  // -> the same as M&D`

### or (x | y)
`M=D|M  // -> the same as M|D`

### neg (-y)
Because `y` is actually at the top of the stack, we can simplify the
instructions we use here (the same applies to `not`):

```
@SP
A=M-1  // -> SP still points to the top of the stack, A fetches y
M=-M   // -> M=y, so set M to -M
```

### not (!y)
```
@SP
A=M-1
M=!M
```

### eq (x == y) (gt, lt)
This operation is a bit more complex (alongside `gt` and `lt`), because there's
no way in the ALU hardware to test two registers for equality. There is
conditional logic on a single register (if A == 0, for example) for jumping,
but those output pins are tied to MUX16 gates, and we don't have direct access
to them with our registers.

Essentially, we need to test for equality, and if true x=-1, else x=0 (true is
-1 according to the VM spec => `-1 = 0xFFFF` and `0 = 0x0000`)

One way I could imagine doing this is setting up an (EQ) symbol that jumps to
that branch when `x-y == 0`. That branch would then have to set x=-1. This uses
the conditional capabilites of the ALU while allowing us to operate on multiple
registers.

The same logic would be applied for `gt` and `lt`:
- for `gt`: (GT) where if `x-y > 0`, set x=-1
- for `lt`: (LT) where if `x-y < 0`, set x=-1

```
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D  // D=x-y
    @EQ
    D;JEQ  // if x-y=0, x=-1
    @SP
    A=M-1
    M=0    // else x=0
(EQ)
    @SP
    A=M-1
    M=-1
```

The issue with this implementation is that the (EQ) isn't really a full branch,
after M=0 runs, then the (EQ) branch will still run. We'd need to jump to an
(EQ_END) branch after M=0:

```
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D
    @EQ_START
    D;JEQ
    @SP
    A=M-1
    M=0
    @EQ_END
    0;JMP
(EQ_START)
    @SP
    A=M-1
    M=-1
(EQ_END)
```

And here, what happens after these instructions are run? If we run more
instructions after (EQ_END), and there's another `eq` operation, we can't reuse
(EQ_END). We could reuse (EQ_START), but we'd have to tell the branch to jump
back to where it originally jumped from somehow.

```
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D
    M=-1    // assume x=true by default
    @EQ_TRUE
    D;JEQ
    @SP
    A=M-1
    M=0     // if we don't jump, x=false
(EQ_TRUE)
```

Here, we still can't reuse (EQ_TRUE) if multiple `eq` operations are present.
However, we would make each (EQ_TRUE) branch unique:
(EQ_TRUE_0), (EQ_TRUE_1), (EQ_TRUE_2), etc...

This is a relatively simple job for our translator, as we can increment the
amount of `eq` operations inside the program as we parse it. The same logic
applies to both `lt` and `gt`.

## Push/Pop Instructions
