# Polysquare CMake Linter #

## Status ##

| Travis CI (Ubuntu) | AppVeyor (Windows) | Coverage | PyPI |
|--------------------|--------------------|----------|------|
|[![Travis](https://travis-ci.org/polysquare/polysquare-cmake-linter.svg?branch=master)](https://travis-ci.org/polysquare/polysquare-cmake-linter)|[![AppVeyor](https://ci.appveyor.com/api/projects/status/0c80f40793wce9un/branch/master?svg=true)](https://ci.appveyor.com/project/smspillaz/polysquare-cmake-linter-935/branch/master)|[![Coveralls](https://coveralls.io/repos/polysquare/polysquare-cmake-linter/badge.png?branch=master)](https://coveralls.io/r/polysquare/polysquare-cmake-linter?branch=master)|[![PyPI](https://pypip.in/version/polysquare-cmake-linter/badge.svg)](https://pypi.python.org/pypi/polysquare-cmake-linter/)|

## Style Guide ##

Polysquare CMake Linter enforces the following style guide:

### Definitions should be namespaced - `structure/namespace` ###

All definitions need to be namespaced, including private definitions. CMake
does not complain on symbol collisions which can lead to unexpected behavior.
Prefer the following form:

    function (namespace_public_function ARGUMENTS)
    endfunction ()

    macro (_namespace_private_macro ARGUMENTS)
    endmacro ()

This check will be inert unless `--namespace NS` is passed on the commandline.

### Single space before open-parens - `style/space_before_func` ###

This is purely aesthetic. In the author's opinion it looks better. Prefer
the following:

    function_call (ARGUMENTS)

instead of:

    function_call(ARGUMENTS)

The open-parens should be followed by just a single space.

### Uppercase variable names only - `style/set_var_case` ###

This is purely aesthetic. Any built-in function that sets a variable must
have an uppercase sink argument.

### Uppercase arguments only - `style/uppercase_args` ###

This is purely aesthetic. Any function or macro definition's arguments must
only be uppercase.

### Lowercase definitions only - `style/lowercase_func` ###

This is purely aesthetic. Any function or macro definition must be lowercase.

### Align arguments to function calls - `style/argument_align` ###

Arguments to a function call must be aligned according to either of the
following rules:

All function arguments on the same line

    function_call (ONE TWO THREE)

All function arguments on a new line must fall on same line as first arg

    function_call (ONE
                   TWO
                   THREE)

Keyword or non-keyword arguments may appear next to a keyword argument where
keyword argument began the line

    function_call (KEYWORD_ONE VALUE TWO
                   KEYWORD_TWO VALUE THREE)

Non-keyword arguments cannot start a line with values:

    # Incorrect
    function_call (ONE
                   ${DEREFERENCE} OTHER)

Keyword values may overflow below last keyword value

    function_call (KEYWORD_ONE VALUE
                               TWO
                   KEYWORD_TWO VALUE
                               THREE)

### Only use double-quotes - `style/doublequotes` ###

This is also purely aesthetic. Only double-quotes should be used when using
quotes to start and end a string. Single quotes can be used internally.
For example, the following is valid.

    function_call ("A sample string 'with single quotes' embedded inside")

### Keep indentation consistent - `style/indent` ###

Nested bodies should be indented consistently. This check will be inert unless
`--indent LEVEL` is passed on the commandline.

### Quote anything that looks like a path - `correctness/quotes` ###

Any "compound literal" (that is a literal which consists of characters other
than alphanumeric characters) which has slashes in it, or dereferences a
variable that ends in the following:

* `PATH`
* `FILE`
* `DIR`
* `DIRECTORY`
* `HEADER`
* `SOURCE`
* `COMMAND`

must be quoted. For example:

    "${PATH_TO_MY_FILE}"
    "${HEADER_FILE_PATH}"
    "${CMAKE_COMMAND}"
    "${CMAKE_CURRENT_SOURCE_DIRECTORY}"

The reason for this is that paths which are separated by spaces may be treated
as separate arguments when passed down the function call chain and this can
lead to unintended behavior. This is especially problematic on Windows, where
the standard directory layout frequently has directories with spaces in their
names.

### Do not have unused private definitions  - `unused/private` ####

Any private definition cannot be unused within a module. A private definition
is any function or macro definition that starts with an underscore. For
example, the following definition must be used:

    function (_private_function)

The following definition can remain unused:

    function (public_function)

### No have unused-but-set variables within a body - `unused/var_in_func` ###

Any "body" (including the body of a function, macro, if, foreach or while
statement) must not set a variable and then not use it later. A variable is
considered to be set if it would be assigned a value as a result of calling
a built-in CMake function.

### No unused private variables within a module - `unused/private_var` ###

Any "private variable" at the top-level of a module (i.e not within a body)
cannot be used and then not used later. A variable is considered to be set
if it would be assigned a value as a result of calling a built-in CMake
function. A variable is considered to be private if it starts with an
underscore.

### Don't use other private definitions `access/other_private` ###

A private definition which was not defined in this module cannot
be used by this module.

### Don't use other private variables `access/private_var` ###

A private variable which was not defined in this module cannot
be used by this module.

This check tries to be smart about detecting where a private
variable was defined in-scope, but it isn't by any means
comprehensive. It will only check parent scopes to the extent
that those parent scopes exist at a structural level and not
at a call-tree level.

In the author's opinion, accessing a variable defined in a
parent scope by a caller is generally bad practice - such
variables should really be passed in as arguments.

## Selectively disabling warnings per-line ##

A warning can be disabled on a line by annotating it with `# NOLINT:`. The
text following the colon can either be the name of a specific warning to
disable, or a wildcard which disables all warnings on that line. For example:

    set (my_variable "Value") # NOLINT:style/set_var_case
    function_call(ARGUMENT) # NOLINT:*

## Command line usage ##

    usage: polysquare-cmake-linter [-h] [--checks]
                                   [--whitelist [WHITELIST [WHITELIST ...]]]
                                   [--blacklist [BLACKLIST [BLACKLIST ...]]]
                                   [--indent INDENT] [--namespace NAMESPACE]
                                   [--fix-what-you-can]
                                   [FILE [FILE ...]]

    Lint for Polysquare style guide

    positional arguments:
      FILE                  read FILE

    optional arguments:
      -h, --help            show this help message and exit
      --checks              list available checks
      --whitelist [WHITELIST [WHITELIST ...]]
                            list of checks that should only be run
      --blacklist [BLACKLIST [BLACKLIST ...]]
                            list of checks that should never be run
      --indent INDENT       Indent level
      --namespace NAMESPACE
                            Namespace for functions
      --fix-what-you-can
