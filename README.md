# Compiler Design Project

This project implements an SLR parser using Python and Streamlit. The application allows users to input a grammar, compute FIRST and FOLLOW sets, and parse strings based on the grammar.

## Overview

This application takes a context-free grammar as input and performs the following operations:
- Computes FIRST and FOLLOW sets for all non-terminal symbols
- Constructs LR(0) items and states
- Generates ACTION and GOTO tables for SLR parsing
- Presents the results in an interactive web interface

## Deployment

The application is deployed and accessible at the following link:

[SLR Parser Application](https://tony499370-compiler-design-project-srcindex-2oo1n6.streamlit.app/)

## Features

- Input grammar in the format: `E -> E+T | T ; T -> T*F | F ; F -> (E) | id`
- Compute FIRST and FOLLOW sets for the grammar.
- Display ACTION and GOTO tables.
- Parse input strings based on the grammar and display parsing steps.

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Tony499370/Compiler-Design_Project.git
   cd Compiler-Design_Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run src/index.py
   ```

2. Access the web interface in your browser (typically at `http://localhost:8501`)

3. Enter a grammar in the provided text area using the following format:
   ```
   E -> E + T | T ; T -> T * F | F ; F -> ( E ) | id
   ```
   - Each production rule should be separated by semicolons (`;`)
   - Alternative productions should be separated by pipes (`|`)
   - Terminal symbols should be lowercase
   - Non-terminal symbols should be uppercase

4. Click the "Compute FIRST, FOLLOW & Parsing Table" button to see the results

## How to Use

1. Enter the grammar in the specified format.
2. Enter the string to parse.
3. Click the "Compute FIRST, FOLLOW & Parsing Table" button to see the results.

## Example

For the grammar:
```
E -> E + T | T ; T -> T * F | F ; F -> ( E ) | id
```

The application will:
- Compute FIRST and FOLLOW sets for E, T, and F
- Generate the ACTION and GOTO tables
- Display all results in the web interface

## Technical Details

The parser implements the SLR parsing algorithm which involves:
1. Grammar augmentation by adding a new start symbol
2. Computing FIRST sets (possible first terminals in derivations)
3. Computing FOLLOW sets (possible terminals that can appear after a non-terminal)
4. Constructing LR(0) items and states
5. Building the SLR parsing table using FOLLOW sets for reduction decisions

## Requirements

- Python 3.x
- Streamlit
- Pandas
- collections (Python standard library)
