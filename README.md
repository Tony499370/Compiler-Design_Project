# SLR Parser

A Python-based SLR (Simple LR) parser application built with Streamlit that performs grammar analysis for compiler design.

## Overview

This application takes a context-free grammar as input and performs the following operations:
- Computes FIRST and FOLLOW sets for all non-terminal symbols
- Constructs LR(0) items and states
- Generates ACTION and GOTO tables for SLR parsing
- Presents the results in an interactive web interface

## Features

- Grammar validation and parsing
- Automatic grammar augmentation
- FIRST and FOLLOW set computation
- LR(0) item generation
- SLR parsing table construction
- Interactive UI for input and result visualization

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

- streamlit
- pandas
- collections (Python standard library)
