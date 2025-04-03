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

        self.start_symbol = list(self.grammar.keys())[0]

        self.augment_grammar()
        self._extract_symbols()
        self.compute_first_sets()
        self.compute_follow_sets()
        self.construct_lr0_items()
        self.build_slr_parsing_table()

    def parse_grammar(self, raw_grammar):
        grammar = defaultdict(list)

        for rule in raw_grammar.split(";"):
            rule = rule.strip()
            if not rule:
                continue

            if "->" not in rule:
                st.error(f"Invalid rule format (missing '->') in: {rule}")
                return None

            lhs, rhs = rule.split("->", 1)
            lhs, rhs = lhs.strip(), rhs.strip()

            if not lhs or not rhs:
                st.error(f"Invalid rule with empty LHS or RHS in: {rule}")
                return None

            grammar[lhs] = [p.strip() for p in rhs.split("|")]

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

        self.terminals.add("$")

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
                            prod_symbols = production.split() if production else []
                            new_item = (next_symbol, "", tuple(prod_symbols))
                            if new_item not in new_items:
                                new_items.add(new_item)
                                changed = True

                closure_set = new_items
            return closure_set

        def goto(state, symbol):
            new_items = set()
            for lhs, before_dot, after_dot in state:
                if after_dot and after_dot[0] == symbol:
                    new_before_dot = (before_dot + " " + after_dot[0]).strip()
                    new_after_dot = tuple(after_dot[1:])
                    new_items.add((lhs, new_before_dot, new_after_dot))
            return closure(new_items) if new_items else set()

        initial_prod = self.grammar[self.start_symbol][0]
        initial_symbols = initial_prod.split() if initial_prod else []
        initial_item = (self.start_symbol, "", tuple(initial_symbols))
        start_state = closure({initial_item})

        self.states = [start_state]
        state_map = {frozenset(start_state): 0}
        state_queue = [start_state]

        while state_queue:
            current_state = state_queue.pop(0)
            state_index = state_map[frozenset(current_state)]

            self.parse_table[state_index] = {"action": {}, "goto": {}}

            for symbol in self.terminals | self.non_terminals:
                next_state = goto(current_state, symbol)

                if not next_state:
                    continue

                next_state_frozen = frozenset(next_state)

                if next_state_frozen not in state_map:
                    state_map[next_state_frozen] = len(self.states)
                    self.states.append(next_state)
                    state_queue.append(next_state)

                next_state_index = state_map[next_state_frozen]

                if symbol in self.terminals:
                    self.parse_table[state_index]["action"][symbol] = (
                        "shift",
                        next_state_index,
                    )
                else:
                    self.parse_table[state_index]["goto"][symbol] = next_state_index

        self.lr0_items = self.states

    def build_slr_parsing_table(self):
        for state_idx, state in enumerate(self.states):
            for item in state:
                lhs, before_dot, after_dot = item

                if not after_dot:
                    if lhs == self.start_symbol:
                        self.parse_table[state_idx]["action"]["$"] = ("accept",)
                    else:
                        prod_idx = -1
                        for idx, prod in enumerate(self.grammar[lhs]):
                            if " ".join(before_dot.split()) == prod:
                                prod_idx = idx
                                break

                        for symbol in self.follow[lhs]:
                            if symbol not in self.parse_table[state_idx]["action"]:
                                self.parse_table[state_idx]["action"][symbol] = (
                                    "reduce",
                                    lhs,
                                    prod_idx,
                                )

    def display_parsing_table(self):
        terminals = sorted(list(self.terminals))
        non_terminals = sorted(
            [nt for nt in self.non_terminals if nt != self.start_symbol]
        )

        table_data = []

        for state_idx in range(len(self.states)):
            row_data = {}

            for term in terminals:
                if term in self.parse_table[state_idx]["action"]:
                    action = self.parse_table[state_idx]["action"][term]
                    if action[0] == "shift":
                        row_data[term] = f"s{action[1]}"
                    elif action[0] == "reduce":
                        row_data[term] = (
                            f"r({action[1]} → {self.grammar[action[1]][action[2]]})"
                        )
                    elif action[0] == "accept":
                        row_data[term] = "acc"
                else:
                    row_data[term] = ""

            for nt in non_terminals:
                if nt in self.parse_table[state_idx]["goto"]:
                    row_data[nt] = str(self.parse_table[state_idx]["goto"][nt])
                else:
                    row_data[nt] = ""

            table_data.append(row_data)

        slr_table = pd.DataFrame(
            table_data, index=[f"I{i}" for i in range(len(self.states))]
        )

        action_header = pd.DataFrame(
            [["ACTION"] * len(terminals) + ["GOTO"] * len(non_terminals)],
            columns=terminals + non_terminals,
        )

        st.subheader("SLR Parsing Table")
        st.write("ACTION (Terminals) | GOTO (Non-terminals)")
        st.write(slr_table)

        st.subheader("LR(0) Items")
        items_data = []

        for i, state in enumerate(self.states):
            items_str = []
            for item in state:
                lhs, before_dot, after_dot = item
                if before_dot and after_dot:
                    rhs = f"{before_dot} • {' '.join(after_dot)}"
                elif before_dot:
                    rhs = f"{before_dot} •"
                elif after_dot:
                    rhs = f"• {' '.join(after_dot)}"
                else:
                    rhs = "•"
                items_str.append(f"{lhs} → {rhs}")

            items_data.append({"State": f"I{i}", "Items": "\n".join(items_str)})

        items_df = pd.DataFrame(items_data)
        st.dataframe(items_df, use_container_width=True, height=400)

    def parse_string(self, input_string):
        processed_input = input_string
        for terminal in sorted(self.terminals - {"$"}, key=len, reverse=True):
            processed_input = processed_input.replace(terminal, f" {terminal} ")

        tokens = [t for t in processed_input.split() if t]
        tokens.append("$")

        stack = [0]
        token_index = 0

        parse_steps = []
        parse_steps.append(
            {
                "Step": 0,
                "Action": "Initialize",
                "Stack": str(stack),
                "Input": " ".join(tokens),
                "Details": "Start parsing",
            }
        )

        step_counter = 1

        while True:
            current_state = stack[-1]
            current_token = tokens[token_index]

            if current_token not in self.parse_table[current_state]["action"]:
                error_msg = f"No action defined for token '{current_token}' in state {current_state}"
                parse_steps.append(
                    {
                        "Step": step_counter,
                        "Action": "ERROR",
                        "Stack": str(stack),
                        "Input": " ".join(tokens[token_index:]),
                        "Details": error_msg,
                    }
                )

                steps_df = pd.DataFrame(parse_steps)
                st.table(steps_df)
                return False, error_msg

            action = self.parse_table[current_state]["action"][current_token]

            if action[0] == "shift":
                stack.append(current_token)
                stack.append(action[1])
                token_index += 1

                parse_steps.append(
                    {
                        "Step": step_counter,
                        "Action": f"Shift {current_token}",
                        "Stack": str(stack),
                        "Input": " ".join(tokens[token_index:]),
                        "Details": f"Move to state {action[1]}",
                    }
                )

            elif action[0] == "reduce":
                lhs, prod_idx = action[1], action[2]
                production = self.grammar[lhs][prod_idx]

                if production == "":
                    rhs_len = 0
                else:
                    rhs_len = len(production.split())

                old_stack = stack.copy()

                for _ in range(rhs_len * 2):
                    stack.pop()

                top_state = stack[-1]

                stack.append(lhs)

                if lhs not in self.parse_table[top_state]["goto"]:
                    error_msg = f"No goto defined for {lhs} from state {top_state}"
                    parse_steps.append(
                        {
                            "Step": step_counter,
                            "Action": "ERROR",
                            "Stack": str(stack),
                            "Input": " ".join(tokens[token_index:]),
                            "Details": error_msg,
                        }
                    )

                    steps_df = pd.DataFrame(parse_steps)
                    st.table(steps_df)
                    return False, error_msg

                goto_state = self.parse_table[top_state]["goto"][lhs]
                stack.append(goto_state)

                parse_steps.append(
                    {
                        "Step": step_counter,
                        "Action": f"Reduce by {lhs} → {production}",
                        "Stack": str(stack),
                        "Input": " ".join(tokens[token_index:]),
                        "Details": f"Pop {rhs_len} symbols, push {lhs}, goto state {goto_state}",
                    }
                )

            elif action[0] == "accept":
                parse_steps.append(
                    {
                        "Step": step_counter,
                        "Action": "Accept",
                        "Stack": str(stack),
                        "Input": " ".join(tokens[token_index:]),
                        "Details": "Input string is valid according to the grammar",
                    }
                )

                steps_df = pd.DataFrame(parse_steps)
                st.table(steps_df)
                return True, "Input accepted"

            else:
                error_msg = f"Invalid action: {action}"
                parse_steps.append(
                    {
                        "Step": step_counter,
                        "Action": "ERROR",
                        "Stack": str(stack),
                        "Input": " ".join(tokens[token_index:]),
                        "Details": error_msg,
                    }
                )

                steps_df = pd.DataFrame(parse_steps)
                st.table(steps_df)
                return False, error_msg

            step_counter += 1


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
                success, message = parser.parse_string(input_string)
                if success:
                    st.success(message)
                else:
                    st.error(message)

        except ValueError as e:
            st.error(str(e))
