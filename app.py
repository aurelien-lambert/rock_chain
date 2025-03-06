import streamlit as st
import pandas as pd
import random

def read_passes(file):
    """
    Reads the CSV file with pandas and returns a DataFrame.
    The DataFrame is then augmented with a unique 'id' column.
    """
    # Adjust encoding if necessary, e.g., encoding='latin-1'
    df = pd.read_csv(file, encoding='latin-1', sep=";")
    df['id'] = df.index  # add a unique identifier for each pass
    return df

def build_graph(df):
    """
    Builds a dictionary mapping each starting point (from the 'Start' column)
    to a list of passes. Each pass is converted to a dictionary.
    """
    graph = {}
    for _, row in df.iterrows():
        start = row['Start']
        if start not in graph:
            graph[start] = []
        graph[start].append(row.to_dict())
    return graph

def search_chain(chain, nb_passes, graph, infinite_loop, initial_start):
    """
    Recursively searches for a chain of passes.

    Parameters:
      - chain: list of passes already selected (each pass is a dictionary)
      - nb_passes: total number of passes desired in the chain
      - graph: dictionary mapping a starting point to available passes
      - infinite_loop: boolean indicating whether the chain should be cyclic 
                       (i.e., the end of the last pass equals the initial start)
      - initial_start: the initial starting value (always 'GD')

    Returns the valid chain found or None if no chain meets the criteria.
    """
    if len(chain) == nb_passes:
        if infinite_loop:
            if chain[-1]['End'] == initial_start:
                return chain
            else:
                return None
        else:
            return chain

    last_pass = chain[-1]
    current_end = last_pass['End']

    # If no pass starts with the current end, abandon this branch
    if current_end not in graph:
        return None

    # Get the candidate passes and shuffle them for randomness
    candidates = list(graph[current_end])
    random.shuffle(candidates)

    for p in candidates:
        # Avoid repeating a pass already used in the chain
        if any(p['id'] == cp['id'] for cp in chain):
            continue
        new_chain = chain + [p]
        result = search_chain(new_chain, nb_passes, graph, infinite_loop, initial_start)
        if result is not None:
            return result  # Valid chain found
    return None

def main():
    st.title("Générateur d'enchainements")

    # Open the CSV file from the local folder
    csv_file = "passes_rock.csv"
    try:
        df = read_passes(csv_file)
    except Exception as e:
        st.error(f"Error reading CSV file '{csv_file}': {e}")
        return

    graph = build_graph(df)
    
    # The chain must start with 'GD'
    initial_start = 'GD'
    if initial_start not in graph:
        st.error(f"No pass starts with {initial_start}.")
        return

    # List available passes starting with 'GD'
    available_passes = graph[initial_start]
    pass_options = [f"{p['Name']}" for i, p in enumerate(available_passes)]

    selected_index = st.selectbox("Passe de départ:", 
                                  range(len(available_passes)),
                                  format_func=lambda i: pass_options[i])
    first_pass = available_passes[selected_index]

    # Let the user set the number of passes and whether they want an infinite loop
    nb_passes = st.number_input("Nombre de passes de l'enchainement:", min_value=1, value=3, step=1)
    infinite_loop = st.checkbox("Boucle infinie ?") 

    if st.button("Générer l'enchainement"):
        found_chain = search_chain([first_pass], nb_passes, graph, infinite_loop, initial_start)
        if found_chain is None:
            st.error("No chain matching the criteria was found.")
        else:
            for i, p in enumerate(found_chain, start=1):
                st.write(f"Passe {i}: {p['Name']}")

if __name__ == '__main__':
    main()
