import pandas as pd
import random

def read_passes(file_name):
    """
    Reads the CSV file with pandas and returns a DataFrame.
    The DataFrame is then augmented with a unique 'id' column.
    """
    # Adjust encoding if necessary, e.g., encoding='latin-1'
    df = pd.read_csv(file_name, encoding='latin-1', sep=";")
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
    file_name = 'passes_rock.csv'
    df = read_passes(file_name)
    graph = build_graph(df)
    
    # The chain must start with 'GD'
    initial_start = 'GD'
    if initial_start not in graph:
        print(f"No pass starts with {initial_start}.")
        return
    
    # List available passes starting with 'GD'
    print("Available passes starting with 'GD':")
    available_passes = graph[initial_start]
    for index, p in enumerate(available_passes):
        print(f"{index}: {p['Name']}")

    # Let the user choose the first pass by index
    try:
        chosen_index = int(input("Select the index of the first pass: "))
        if chosen_index < 0 or chosen_index >= len(available_passes):
            print("Invalid index selected.")
            return
    except ValueError:
        print("Please enter a valid integer index.")
        return

    first_pass = available_passes[chosen_index]

    # Ask the user for the number of passes in the chain
    try:
        nb_passes = int(input("Enter the number of passes in the chain: "))
    except ValueError:
        print("Please enter a valid integer.")
        return

    # Ask the user if they want an infinite loop (start equals end)
    answer = input("Do you want an infinite loop (start equals end)? (yes/no): ").strip().lower()
    infinite_loop = (answer == 'yes')

    # Build the chain starting with the chosen first pass
    found_chain = search_chain([first_pass], nb_passes, graph, infinite_loop, initial_start)

    if found_chain is None:
        print("No chain matching the criteria was found.")
    else:
        print("Chain found:")
        for i, p in enumerate(found_chain, start=1):
            print(f"Pass {i}: Name = {p['Name']}, Start = {p['Start']}, End = {p['End']}")

if __name__ == '__main__':
    main()
