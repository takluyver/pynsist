class Comment(object):
    def __init__(self, content):
        self.content = content

    def generate(self, state=None):
        yield "; " + self.content

def _should_quote(arg):
    return (' ' in arg) or ('$' in arg)

def assemble_line(parts):
    quoted_parts = [("%s" % p) if _should_quote(p) else p
                    for p in parts if p is not None]
    return ' '.join(quoted_parts)

class Instruction(object):
    def __init__(self, name, *parameters):
        self.name = name
        self.parameters = parameters

    def generate(self, state=None):
        yield assemble_line([self.name] + list(self.parameters))

def make_instruction_class(name):
    def __init__(self, *parameters):
        Instruction.__init__(self, name, *parameters)

    return type(name, (Instruction,), {'__init__': __init__})

File = make_instruction_class('File')

class Scope(object):
    def __init__(self, contents=None):
        self.contents = contents or []

    def generate_children(self, state=None):
        for child in self.contents:
            for line in child.generate(state):
                yield '  ' + line

class Section(Scope):
    def __init__(self, name=None, index_var=None, selected=True, contents=None):
        super(Section, self).__init__(contents)
        self.name = name
        self.index_var = index_var
        self.selected = selected

    def generate(self, state=None):
        parts = ['Section',
                 None if self.selected else '/o',
                 self.name, self.index_var]

        yield assemble_line(parts)
        for line in self.generate_children(state):
            yield line
        yield 'SectionEnd'
        yield ''  # Blank line after a section

class SectionGroup(Scope):
    def __init__(self, name, index_var=None, expanded=False, contents=None):
        super(SectionGroup, self).__init__(contents)
        self.name = name
        self.expanded = expanded
        self.index_var = index_var

    def generate(self, state=None):
        parts = ['SectionGroup',
                 '/e' if self.expanded else None,
                 self.name, self.index_var]
        yield assemble_line(parts)
        for line in self.generate_children(state):
            yield line
        yield 'SectionGroupEnd'

class Function(Scope):
    def __init__(self, name, contents=None):
        super(Function, self).__init__(contents)
        self.name = name

    def generate(self, state=None):
        yield assemble_line(['Function', self.name])
        for line in self.generate_children(state):
            yield

class Label(object):
    def __init__(self, name):
        self.name = name

    def generate(self, scope):
        yield self.name + ":"

class Conditional(object):
    # e.g. IfSilent, IntCmp
    def __init__(self, name, *parameters, ifbody=None, elsebody=None):
        self.name = name
        self.parameters = parameters
        self.ifbody = ifbody or []
        self.elsebody = elsebody or []

    def generate(self, state):
        if_counter = state.get('if_counter', 1)
        state['if_counter'] = if_counter + 1
        yield assemble_line([self.name] + self.parameters + ["0",
                     ("else%d" if self.elsebody else "endif%d") % if_counter])
        for child in self.ifbody:
            for line in child.generate(state):
                yield "  " + line

        if self.elsebody:
            yield ("  Goto endif%d" % if_counter)
            yield ("else%d:" % if_counter)
            for child in self.elsebody:
                for line in child.generate(state):
                    yield "  " + line

        yield ("endif%d:" % if_counter)


class CompilerCommand(object):
    def __init__(self, name, *parameters):
        self.name = name
        self.parameters = parameters

    def generate(self, state=None):
        yield "!" + assemble_line([self.name] + list(self.parameters))

class CompilerConditional(object):
    # ifdef etc
    def __init__(self, name, parameters, ifbody=None, elsebody=None):
        self.name = name
        self.parameters = parameters
        self.ifbody = ifbody or []
        self.elsebody = elsebody or []

    def generate(self, state=None):
        yield "!" + assemble_line([self.name] + self.parameters)
        for child in self.ifbody:
            for line in child.generate(state):
                yield '  ' + line
        if self.elsebody:
            yield "!else"
            for child in self.elsebody:
                for line in child.generate(state):
                    yield '  ' + line

        yield "!endif"

def make_compiler_command_class(name):
    def __init__(self, *parameters):
        CompilerCommand.__init__(self, name, *parameters)

    return type(name, (CompilerCommand,), {'__init__': __init__})

define = make_compiler_command_class('define')
insertmacro = make_compiler_command_class('insertmacro')

class Macro(Scope):
    def __init__(self, name, parameters):
        super(Macro, self).__init__()
        self.name = name
        self.parameters = parameters

    def generate(self, state=None):
        yield "!" + assemble_line([self.name] + self.parameters)
        for line in self.generate_children(state):
            yield "  " + line
        yield "!macroend"

class Document(object):
    def __init__(self, children=None):
        self.children = children or []

    def generate(self, state):
        for child in self.children:
            for line in child.generate(state):
                yield line

    def write(self, fileobj_or_path):
        if isinstance(fileobj_or_path, str):
            with open(fileobj_or_path, 'w') as f:
                return self.write(f)

        for line in self.generate(state={}):
            fileobj_or_path.write(line + '\n')