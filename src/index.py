import streamlit as st
import pandas as pd
from collections import defaultdict

class SLRParser:
    def __init__(self, grammar_input):
        self.grammar = self.parse_grammar(grammar_input)
        if not self.grammar:
            raise ValueError("Invalid grammar input. Please check the format.")

        self.terminals = set()
        self.non_terminals = set()
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.lr0_items = []
        self.states = []
        self.parse_table = {}
        self.goto_table = {}

        self.start_symbol = list(self.grammar.keys())[0]

        self.augment_grammar()
        self._extract_symbols()
        self.compute_first_sets()
        self.compute_follow_sets()
        self.construct_lr0_items()
        self.build_slr_parsing_table()

    def parse_grammar(self, raw_grammar):
        grammar = defaultdict(list)

        for rule in raw_grammar.split(';'):
            rule = rule.strip()
            if not rule:
                continue

            if '->' not in rule:
                st.error(f"Invalid rule format (missing '->') in: {rule}")
                return None

            lhs, rhs = rule.split('->', 1)
            lhs, rhs = lhs.strip(), rhs.strip()

            if not lhs or not rhs:
                st.error(f"Invalid rule with empty LHS or RHS in: {rule}")
                return None

            grammar[lhs] = [p.strip() for p in rhs.split('|')]

        if not grammar:
            st.error("No valid grammar rules found.")
            return None

        return grammar

    def augment_grammar(self):
        new_start = self.start_symbol + "'"
        self.grammar[new_start] = [self.start_symbol]
        self.start_symbol = new_start

    def _extract_symbols(self):
        for lhs, productions in self.grammar.items():
            self.non_terminals.add(lhs)
            for production in productions:
                for symbol in production.split():
                    if symbol.isupper():
                        self.non_terminals.add(symbol)
                    else:
                        self.terminals.add(symbol)

        self.terminals.add('$')

    def compute_first_sets(self):
        def first(symbol):
            if symbol in self.terminals:
                return {symbol}
            if self.first[symbol]:  
                return self.first[symbol]

            result = set()
            for production in self.grammar[symbol]:
                if production == "":  
                    result.add("ε")
                else:
                    for sym in production.split():
                        if sym == symbol:
                            break
                        sym_first = first(sym)
                        result.update(sym_first - {"ε"})
                        if "ε" not in sym_first:
                            break
                    else:
                        result.add("ε")

            self.first[symbol] = result
            return result

        for nt in self.non_terminals:
            first(nt)

    def compute_follow_sets(self):
        self.follow[self.start_symbol].add("$")

        changed = True
        while changed:
            changed = False
            for lhs, productions in self.grammar.items():
                for production in productions:
                    trailer = self.follow[lhs].copy()
                    for symbol in reversed(production.split()):
                        if symbol in self.non_terminals:
                            if trailer - self.follow[symbol]:
                                self.follow[symbol].update(trailer)
                                changed = True
                            if "ε" in self.first[symbol]:
                                trailer.update(self.first[symbol] - {"ε"})
                            else:
                                trailer = self.first[symbol]
                        else:
                            trailer = {symbol}

    def construct_lr0_items(self):
        def closure(items):
            closure_set = set(items)
            changed = True

            while changed:
                changed = False
                new_items = set(closure_set)

                for lhs, before_dot, after_dot in closure_set:
                    if after_dot and after_dot[0] in self.non_terminals:
                        next_symbol = after_dot[0]
                        for production in self.grammar[next_symbol]:
                            new_item = (next_symbol, "", tuple(production.split()))
                            if new_item not in new_items:
                                new_items.add(new_item)
                                changed = True

                closure_set = new_items
            return closure_set

        def goto(state, symbol):
            new_items = set()
            for lhs, before_dot, after_dot in state:
                if after_dot and after_dot[0] == symbol:
                    new_items.add((lhs, before_dot + " " + after_dot[0], tuple(after_dot[1:])))
            return closure(new_items)

        initial_item = (self.start_symbol, "", tuple(self.grammar[self.start_symbol][0].split()))
        start_state = closure({initial_item})
        self.states.append(start_state)

        state_queue = [start_state]
        state_map = {frozenset(start_state): 0}

        while state_queue:
            state = state_queue.pop(0)
            self.lr0_items.append(state)
            state_index = state_map[frozenset(state)]

            transitions = {}
            symbols = self.terminals | self.non_terminals

            for symbol in symbols:
                next_state = goto(state, symbol)
                if next_state:
                    frozen_next_state = frozenset(next_state)
                    if frozen_next_state not in state_map:
                        state_map[frozen_next_state] = len(self.states)
                        self.states.append(next_state)
                        state_queue.append(next_state)
                    transitions[symbol] = state_map[frozen_next_state]

            self.goto_table[state_index] = transitions

    def build_slr_parsing_table(self):
        self.action_table = {state_index: {} for state_index in range(len(self.states))}

        for state_index, state in enumerate(self.lr0_items):
            for item in state:
                lhs, before_dot, after_dot = item

                if lhs == self.start_symbol and not after_dot:
                    self.action_table[state_index]['$'] = ("ACCEPT",)
                elif after_dot:
                    next_symbol = after_dot[0]
                    if next_symbol in self.terminals:
                        next_state = self.goto_table[state_index].get(next_symbol)
                        if next_state is not None:
                            self.action_table[state_index][next_symbol] = ("SHIFT", next_state)
                else:
                    for terminal in self.follow[lhs]:
                        self.action_table[state_index][terminal] = ("REDUCE", lhs)

    def display_parsing_table(self):
        action_table_str = {
            state: {symbol: " ".join(map(str, action)) if action else "" for symbol, action in actions.items()}
            for state, actions in self.action_table.items()
        }
        action_table_df = pd.DataFrame(action_table_str).fillna("")

        goto_table_str = {
            state: {symbol: str(target) if target is not None else "" for symbol, target in transitions.items()}
            for state, transitions in self.goto_table.items()
        }
        goto_table_df = pd.DataFrame(goto_table_str).fillna("")

        st.subheader("ACTION Table")
        st.write(action_table_df)

        st.subheader("GOTO Table")
        st.write(goto_table_df)

    def parse_string(self, input_string):
        for terminal in sorted(self.terminals, key=len, reverse=True):  
            input_string = input_string.replace(terminal, f" {terminal} ")

        input_string = input_string.split()
        input_string.append("$")

        stack = [0]
        pointer = 0

        st.write("### Parsing Steps")
        st.write(f"Initial Stack: {stack}, Input: {' '.join(input_string)}")

        while True:
            current_state = stack[-1]
            current_symbol = input_string[pointer]

            action = self.action_table.get(current_state, {}).get(current_symbol)

            if not action:
                st.write(f"DEBUG: Current Stack: {stack}")
                st.write(f"DEBUG: Current Input: {' '.join(input_string[pointer:])}")
                return f"Error: Unexpected symbol '{current_symbol}' at position {pointer}."

            if action[0] == "SHIFT":
                stack.append(current_symbol)
                stack.append(action[1])
                pointer += 1
                st.write(f"SHIFT: Stack: {stack}, Input: {' '.join(input_string[pointer:])}")
            elif action[0] == "REDUCE":
                lhs = action[1]
                rhs = self.grammar[lhs][0]

                if rhs == "ε":
                    rhs_length = 0
                else:
                    rhs_length = len(rhs.split())

                if len(stack) < rhs_length * 2:
                    st.write(f"DEBUG: Current Stack: {stack}")
                    st.write(f"DEBUG: Current Input: {' '.join(input_string[pointer:])}")
                    return f"Error: Stack underflow during REDUCE operation for production {lhs} → {rhs}."

                for _ in range(rhs_length * 2):
                    stack.pop()

                stack.append(lhs)
                goto_state = self.goto_table[stack[-2]].get(lhs)
                if goto_state is None:
                    st.write(f"DEBUG: Current Stack: {stack}")
                    st.write(f"DEBUG: Current Input: {' '.join(input_string[pointer:])}")
                    return f"Error: No GOTO state for symbol '{lhs}'."
                stack.append(goto_state)
                st.write(f"REDUCE: Stack: {stack}, Input: {' '.join(input_string[pointer:])}")
            elif action[0] == "ACCEPT":
                return "The string is successfully parsed and is valid!"
            else:
                st.write(f"DEBUG: Current Stack: {stack}")
                st.write(f"DEBUG: Current Input: {' '.join(input_string[pointer:])}")
                return f"Error: Invalid action '{action}' encountered."

st.title("SLR Parser")
st.write("Enter grammar in the format: E -> E+T | T ; T -> T*F | F ; F -> (E) | id")

grammar_input = st.text_area("Enter Grammar:")
input_string = st.text_input("Enter String to Parse:")

if st.button("Compute FIRST, FOLLOW & Parsing Table"):
    if grammar_input:
        try:
            parser = SLRParser(grammar_input)
            st.subheader("FIRST Sets")
            for nt, first_set in parser.first.items():
                st.write(f"FIRST({nt}) = {first_set}")

            st.subheader("FOLLOW Sets")
            for nt, follow_set in parser.follow.items():
                st.write(f"FOLLOW({nt}) = {follow_set}")

            parser.display_parsing_table()

            if input_string:
                st.subheader("String Parsing")
                result = parser.parse_string(input_string)
                st.write(result)

        except ValueError as e:
            st.error(str(e))