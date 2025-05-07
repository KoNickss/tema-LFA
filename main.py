import itertools

import json

jsfl = open("input.json", "r")

js = json.load(jsfl)

alph = ""

class State:
    id = itertools.count()

    def __init__(self):
        self.name = f"q{next(self.id)}"
        self.transitions = []

    def add_transition(self, symbol, state):
        self.transitions.append((symbol, state))

    def transit(self, symbol):
        ret = set()
        for sym, next_state in self.transitions:
            if sym == symbol:
                ret.add(next_state)
        
        return ret

class NFA:
    output = ""
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept
        self.states = self._collect_states()

    def _collect_states(self):
        visited = set()
        to_visit = [self.start]
        result = []

        while to_visit:
            state = to_visit.pop()
            if state in visited:
                continue
            visited.add(state)
            result.append(state)
            for _, next_state in state.transitions:
                to_visit.append(next_state)

        return result

    def print_nfa(self):
        print("States:")
        for s in self.states:
            labels = []
            if s == self.start:
                labels.append("S")
            if s in self.accept:
                labels.append("F")
            label_str = ", " + ", ".join(labels) if labels else ""
            print(f"    {s.name}{label_str}")
        print("End\n")

        print("Sigma:")
        symbols = set()
        for s in self.states:
            for sym, _ in s.transitions:
                if sym != 'λ':
                    symbols.add(sym)
        for sym in symbols:
            print(f"    {sym}")
        print("End\n")

        print("Transitions:")
        for s in self.states:
            for sym, next_state in s.transitions:
                print(f"    {s.name}, {sym}, {next_state.name}")
        print("End")

    def export_nfa(self):
        self.output = ""
        def print(str):
            self.output = self.output + str + "\n"

        print("States:")
        for s in self.states:
            labels = []
            if s == self.start:
                labels.append("S")
            if s in self.accept:
                labels.append("F")
            label_str = ", " + ", ".join(labels) if labels else ""
            print(f"    {s.name}{label_str}")
        print("End\n")

        print("Sigma:")
        symbols = set()
        for s in self.states:
            for sym, _ in s.transitions:
                if sym != 'λ':
                    symbols.add(sym)
        for sym in symbols:
            print(f"    {sym}")
        print("End\n")

        print("Transitions:")
        for s in self.states:
            for sym, next_state in s.transitions:
                print(f"    {s.name}, {sym}, {next_state.name}")
        print("End")

        return self.output



# Thompson ala

def regex_to_nfa(regex):
    def parse_atom(symbol):
        start = State()
        end = State()
        start.add_transition(symbol, end)
        return NFA(start, [end])

    def concat(nfa1, nfa2):
        nfa1.accept[0].add_transition('λ', nfa2.start)
        return NFA(nfa1.start, nfa2.accept)

    def alternate(nfa1, nfa2):
        start = State()
        end = State()
        start.add_transition('λ', nfa1.start)
        start.add_transition('λ', nfa2.start)
        nfa1.accept[0].add_transition('λ', end)
        nfa2.accept[0].add_transition('λ', end)
        return NFA(start, [end])

    def star(nfa):
        start = State()
        end = State()
        start.add_transition('λ', nfa.start)
        start.add_transition('λ', end)
        nfa.accept[0].add_transition('λ', nfa.start)
        nfa.accept[0].add_transition('λ', end)
        return NFA(start, [end])

    def plus(nfa):
        start = State()
        end = State()
        start.add_transition('λ', nfa.start)
        nfa.accept[0].add_transition('λ', nfa.start)
        nfa.accept[0].add_transition('λ', end)
        return NFA(start, [end])

    def what(nfa):
        start = State()
        end = State()
        start.add_transition('λ', nfa.start)
        start.add_transition('λ', end)
        nfa.accept[0].add_transition('λ', end)
        return NFA(start, [end])

    
    def parse(expr):
        stack = []

        def pop_concat():
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(concat(nfa1, nfa2))

        def pop_alternate():
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(alternate(nfa1, nfa2))

        i = 0
        while i < len(expr):
            c = expr[i]
            if c in alph:
                stack.append(parse_atom(c))
            elif c == '*':
                nfa = stack.pop()
                stack.append(star(nfa))
            elif c == '+':
                nfa = stack.pop()
                stack.append(plus(nfa))
            elif c == '?':
                nfa = stack.pop()
                stack.append(what(nfa))
            elif c == '|':
                pop_alternate()
            elif c == '^':
                pop_concat()
            
            i += 1

        return stack[0]

    return parse(regex)

def insert_concatenation(regex):
    result = ""
    prev = ""
    for curr in regex:
        if prev:
            if (prev in ")*+?"+alph or prev == ')') and (curr in "λ("+alph or curr == '('):
                result += '^'
        result += curr
        prev = curr
    return result

# Shunting Yard ala
def to_postfix(regex):
    precedence = {'?': 5, '+': 4, '*': 3, '^': 2, '|': 1}
    output = []
    stack = []

    for token in regex:
        if token in alph:
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop() 
        elif token in precedence:
            while (stack and stack[-1] != '(' and
                   precedence.get(stack[-1], 0) >= precedence[token]):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())

    return ''.join(output)


def lambdaNfaToDfa(nfa):
    conv = dict()
    seen = dict()
    fein = set()
    def extendState(state, newst, initial):

        if initial:
            if state in seen:
                newst = seen[state]
                return newst
            seen[state] = newst

        if state in nfa.accept:
            fein.add(newst)
        

        if newst not in conv:
            conv[newst] = []
        
        for sym, next_state in state.transitions:
            if sym != 'λ':
                continue
            
            if next_state in conv[newst]:
                continue
            
            conv[newst].append(next_state)
            extendState(next_state, newst, False)
        
        conv[newst].append(state)

        return newst
        

    def connectNewState(newst):
        
        for sym in alph:
            if sym == 'λ':
                continue
            
            tlist = set()
            if newst not in conv:
                continue

            for st in conv[newst]:
                tmp = st.transit(sym)
                tlist = tlist | tmp
            
            new_connected_state = State()

            if len(tlist) == 0:
                continue

            fs = True
            cache = new_connected_state
            for os in tlist:
                new_connected_state = extendState(os, new_connected_state, fs)
                fs = False

            
            newst.add_transition(sym, new_connected_state)
            

            if new_connected_state == newst:
                continue

            if new_connected_state != cache:
                continue

            connectNewState(new_connected_state)



    newstart = State()
    extendState(nfa.start, newstart, True)
    connectNewState(newstart)

    return NFA(newstart, fein)
    
        
            
def callDFATemaUnu(dfastr, entries, expected):
    sigma = []
    delta = dict()
    delta["NaS"] = dict()
    inits = []
    inits.append("NaS")
    finals = []
    states = []


    def initRead(dfastr):
        buf = dfastr

        state = 0
        # 0 - none
        # 1 - state
        # 2 - alphabet
        # 3 - transitions

        for line in buf.split("\n"):

            line = line.strip()

            if line == "End":
                state = 0

            #print(state, line)

            if state == 1:

                lis = line.split(", ")
                statex = lis[0]
                delta[statex] = dict()
                states.append(statex)

                for letter in sigma:
                    delta[statex][letter] = "NaS"
                for token in lis:
                    if token == "F":
                        finals.append(statex)
                    if token == "S":
                        if inits[0] == "NaS":
                            inits[0] = statex
                        else:
                            raise Exception("Multiple init states!")

            if state == 2:
                sigma.append(line.strip())
                delta["NaS"][line.strip()] = "NaS"

            if state == 3:
                lis = line.split(", ")
                delta[lis[0]][lis[1]] = lis[2]

            if line == "States:":
                state = 1

            if line == "Sigma:":
                state = 2

            if line == "Transitions:":
                state = 3


    def feedInput(input1):
        #input1 = input("Feed Input (or '\\' to exit): ")

        if input1 == "\\":
            return -1

        ok = False

        state = inits[0]

        for letter in input1:
            if state not in delta:
                #print("NOT ACCEPTED!")
                ok = True
                return 1

            if letter not in delta[state]:
                #print("NOT ACCEPTED!")
                ok = True
                return 1

            state = delta[state][letter]
            if state == "NaS":
                #print("NOT ACCEPTED!")
                ok = True
                return 1

        for fstat in finals:
            if state == fstat:
                #print("ACCEPTED!")
                ok = True
                return 0

        if ok == False:
            #print("NOT ACCEPTED!")
            return 1


    initRead(dfastr)
    #print(delta)
    oka = 0
    for i in range(len(entries)):
        oka = feedInput(entries[i])
        if oka == 0 and expected[i] == True:
            print("✅ OK!", oka, expected[i])
            continue
        if oka == 1 and expected[i] == False:
            print("✅ OK!", oka, expected[i])
            continue
        
        print("❌ ---ERROR----", oka, expected[i])




for obj in js:

    #print(obj)

    alset = set()

    regex = obj['regex']

    print(f"\n\n{obj['name']}\n\n")

    entries = []
    expected = []

    for p in obj['test_strings']:
        entries.append(p['input'])
        expected.append(p['expected'])

    for c in regex:
        if c not in "+^|*()?":
            alset.add(c)

    for en in alset:
        alph = alph + en


    print(regex)

    regex = insert_concatenation(regex)

    #print(regex)

    regex = to_postfix(regex)

    #print(regex)

    #print("\n\n-------------\n\n")
    nfa = regex_to_nfa(regex)
    #nfa.print_nfa()
    #print("\n\n\n-----------------\n\n\n")
    dfa = lambdaNfaToDfa(nfa)
    #dfa.print_nfa()
    exdfa_txt = dfa.export_nfa()
    callDFATemaUnu(exdfa_txt, entries, expected)

