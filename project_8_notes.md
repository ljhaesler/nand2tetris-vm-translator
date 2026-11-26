# Project 8: Revisited
By the end of project 8, very broadly, the VM translator is expected to:
- either convert a folder of `.vm` files into a single Hack assembly `.asm`
- or convert a single `.vm` file into a single Hack assembly `.asm`
- handle three branching operations:
    - `label LABEL`, which simply drops a label to the current position in code.
    - `goto LABEL`, which jumps unconditionally to a label
    - `if-goto LABEL`, which jumps if the top value popped from the stack ≠ 0
- handle three function operations:
    - `function functionName nVars`, which declares a function.
    - `call functionName nArgs`, which calls a given function.
    - `return`, which returns from the current function

## A folder of `.vm` files vs. a single `.vm` file 
Essentially, the spec states that the translator accepts a folder of `.vm`
files, or a single `.vm` file. If it's a folder, the bare minimum this folder
has to contain is a `Sys.vm` file, even though we mustn't check for it. This
`Sys.vm` must contain a `Sys.init` function, which we also don't check for,
which is what our bootstrap logic calls. Bootstrapping simply involves moving
SP to MEM[256] and calling `Sys.init`.

In reality, the `Sys.init` function is *supposed* to be an OS call, but we
haven't implemented any OS logic, so it simply doesn't exist. In order to
account for this, our translator has to handle the `Sys.vm` file described
before, which defines the `Sys.init` function for us. This `Sys.init` function,
when implemented as an OS call, is *supposed* to initialise the OS, and finally
call a `Main.main` function, which is defined inside a `Main.vm` file.
This is the entry point for our program.

The implemenation of our VM translator is agnostic towards a `Main.vm` file and
the `Main.main` function its *supposed* to define, because that's a contract
that's meant to be fulfilled at the Jack-level. It is also agnostic towards a
`Sys.vm` and `Sys.init`, because `Sys.init` is *supposed* to be defined on the
OS level.

In addition, even though the `Sys.init` OS call will always expect that a
`Main.main` function exists, nothing will ever check for this. And even though
the bootstrap code injected by our translator expects a `Sys.init` function to
exist *somewhere*, nothing wil check for it.

The real, final 'contract', is *supposed* to be:
- The VM translator **always** injects bootstrap code
- The `Sys.init` OS call **always** inits the OS and calls `Main.main`
- A compiled Jack program **always** contains a `Main.vm` file with a `main`
function.

But nothing will ever ensure this contract: it's purely just convention. Even
though everything needs to be done in exactly this way for the final computer to
actually work.

In summary, in the final computer, this translator will:
- Never use the single `.vm` file functionality -> always bootstrap
- Never check if there is a `Sys.vm` or a `Main.vm` file.
- Never require a `Sys.vm` file
- It *will* require that a `Main.vm` file with a `main` function exists, but it
will never check for it.

Therefore, all the translator needs to do is:
- if directory -> bootstrap, read all `.vm` files and assemble them.
- else -> do not bootstrap, read a single `.vm` file and assemble it.

## Functions & Branching: Logic and Naming Conventions
### Branching with Labels
In the spec a label can exist inside or outside of a function. In the final
computer, a label will **always** exist inside of a function. We expect a label
follow the syntax: `Xxx.foo$bar`, where `Xxx` is the file name, from `Xxx.vm`,
`foo` is the function name, and `bar` is the label name.

Sometimes, for testing, a label will be standalone, meaning it should simply use
`bar`. I use `$bar` for simplicity.

### Declaring a Function with Labels
This logic applies to `function functionName nVars`.

Essentially, the place where a function is declared is also where, immediately
after the label, we will initialise that function. Initialising a function
involves ensuring that all of the addresses in memory that the function will
use as variables are set to 0. If we don't do this, we run the risk of a
function trying to read from a variable it expects to equal 0, when in memory
it simply isn't.

In addition, the label used by the function has a specific syntax: `Xxx.foo`,
where `Xxx` is the file name, from `Xxx.vm`, and `foo` is the function name.

### Calling a Function with Labels
Logic applies to `call functionName nArgs`.

'Calling' a function means doing quite a few things. I start by storing the
address of the first ARG defined for the `callee` function into `@R13`, but the
spec suggests finding this value at the end instead. Fundamentally this doesn't
change anything. As a clear list:

- Find the first `ARG`, at `SP - nArgs`, store it `@R13`
- Find the `returnAddress`, push it to the stack.
- Push the address pointing to LCL onto the stack -> `@SP = @LCL, SP++`
- Same for ARG -> `@SP = @ARG, SP++`
- Same for THIS -> `@SP = @THIS, SP++`
- Same for THAT -> `@SP = @THAT, SP++`
- Point ARG to `@R13` -> `@ARG = @R13`
- Point LCL to where SP is currently pointing -> `@LCL = @SP`
- Jump to a label declared via `function functionName nVars` -> `0;JMP`

This sets up the stack frame that the `callee` function will use, which starts
at LCL, and SP = LCL. The stack frame of the `caller` function starts just
after the last ARG of the `callee` and ends at LCL. This is very important for
the `return` operation: the very end of the `caller` stack frame is at LCL.

The two important concepts here are:
- how exactly the `returnAddress` is implemented
- what the syntax of the `returnAddress` looks like
- where exactly the `callee` `ARG` segment is located

#### `returnAddress` Implementation and Syntax
As for the `returnAddress`, its label, in assembly, is actually dropped
immediately after the `0;JMP`. We can do this because our assembler works in
two stages:
- The first stage parses out labels only, and stores their exact location in
memory, starting from MEM[16]. For example, MEM[22] might store `2442`.
- The second stage, among other things, translates unique labels into their raw
address values. For example, `@Xxx.foo$ret.1` might get translated to `@22`.

Essentially, when our `returnAddress` for `@Xxx.foo$ret.1` is pushed to the
stack, this is a pointer to the address of the instruction situated immediately
after `0;JMP`. For example, if `@Xxx.foo$ret.1 = @22`, then `MEM[22] = 2442`,
and `2442` is the address at which execution has to resume.

In order to pull this off, each label has to follow a specific syntax:
`@Xxx.foo$ret.i`. Fundamentally, we need each return label to be unique,
because the same function can be called multiple times, and returning to the
same spot without any extra logic would just create a loop. Therefore, we need
`i` to be a unique number for every new return label.

The way I implemented this was simply by incrementing a value in the translator
by 1 every time there is any `call` operation. We *could* keep track of whether
or not the same function is being called multiple times, and only increment on
that condition, but that seems a lot more complicated than it needs to be.

#### The Logic Behind the `callee` `ARG` Segment
If we consider that a function will necessarily be pushing and popping values
from the stack, we can simply say that the top `nArgs` values of the stack will
be used as the arguments for the `callee`. When the `callee` returns, the
`caller` expects that the very top of the stack will contain the return value.
This is a simple enough contract:

The `caller` function pushes `nArgs` arguments onto the stack, and 'prepares'
them for the `callee`. They're technically separated into an `ARG` segment, but
fundamentally, from the `caller` perspective, these args are just the top of
the stack. Once execution is handed to the `callee`, its job is to write a
return value to the stack. It does so at `ARG[0]`: inside the context of the
`caller` function. All the `callee` needs to do from here is point SP to the
address just after `ARG`. Then, when the `caller` resumes executing, all it
sees is a return value at the top of the stack.

### Returning from a Function with Labels
Logic applies to `return`

'Returning' from a function will restore the stack frame of the `caller`, as
mentioned above.

We then have to ensure that the `caller` gets the return value from the
`callee`. The function will always push the intended return value to the top of
the stack, so we simply need to pop it, and store it somewhere the `caller` can
read. 

Finally, we jump to the stored `returnAddress`. During the `call` operation,
LCL was set to point at the very end of this frame. Therefore, to restore our
`caller` stack frame, we can just work from LCL backwards.

- Store the address at LCL into `@R13` -> `@LCL = @R13`
- Find the `returnAddress`, store it in `@R14` -> `@R14 = @R13 - 5`
- Pop the return value, store it at ARG[0], point SP to ARG+1
- Restore THAT: `@THAT = MEM[@R13 - 1]`
- Restore THIS: `@THIS = MEM[@R13 - 2]`
- Restore ARG : `@ARG  = MEM[@R13 - 3]`
- Restore LCL : `@LCL  = MEM[@R13 - 4]`
- Finally, jump to the return address: `A=MEM[@R14], 0;JMP`

When execution is returned to the `caller`, all it sees is that the return value
is at the top of SP. Everything else has been restored to how it was before
execution was passed to the `callee`.
