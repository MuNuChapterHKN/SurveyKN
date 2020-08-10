# -*- coding: utf-8 -*-

import sys
import yaml
from pathlib import Path
from os.path import realpath
from shutil import copy

# The relative path to data-root-config.yml from this script
DATA_ROOT_CONFIG_REL = Path(realpath(__file__)).parent / "data-root-config.yml"
# The relative path to question-store.yml from the data root
QS_FROM_ROOT = Path('AppData/question-store.yml')



def increment_QID(question_id):
    
    """
    Implements the logic for incrementing question identifiers

    Parameters
    ----------
    question_id : String
        3 character question identifier used in the question store

    Returns
    -------
    question_id : String
        3 character question identifier used in the question store, incremented

    """
    
    if question_id[2] != "Z":
        question_id = question_id[0] + question_id[1] + chr(ord(question_id[2])+1)
    elif question_id[1] != "Z":
        question_id = question_id[0] + chr(ord(question_id[1])+1) + "A"
    else:
        question_id = chr(ord(question_id[0])+1) + "A" + "A"
    
    return question_id



def decrement_QID(question_id):
    
    """
    Implements the logic for decrementing question identifiers

    Parameters
    ----------
    question_id : String
        3 character question identifier used in the question store

    Returns
    -------
    question_id : String
        3 character question identifier used in the question store, decremented

    """
    
    if question_id[2] != "A":
        question_id = question_id[0] + question_id[1] + chr(ord(question_id[2])-1)
    elif question_id[1] != "A":
        question_id = question_id[0] + chr(ord(question_id[1])-1) + "Z"
    else:
        question_id = chr(ord(question_id[0])-1) + "Z" + "Z"
    
    return question_id


def add_question_to_store(question_store, question):
    
    """
    Takes a new question and registers it into the question store
    by assigning it its question ID.
    
    Strips any leading(before) or trailing(after) whitespace.
    
    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.
        
    question : String
        The new question that will be given an identifier and
        registered into the store

    Returns
    -------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.
    
    question_id : String
        3 character question identifier of the added question
    """
    
    current_question_count = question_store['COUNT']['current']
    if  current_question_count >= question_store['COUNT']['maximum']:
        print("\nError: Question store at full capacity, ID scheme needs to be extended!")
        sys.exit(1)
    
    # Next question ID in line
    question_id = question_store['NEXTINLINE']
    
    # Create entry
    question_store.update( { question_id : {"current" : question.strip()} } )
    
    # Update next-in-line and current count
    question_store.update( { "NEXTINLINE" : increment_QID(question_id) } )
    question_store["COUNT"].update( { "current" :  (current_question_count + 1) } )
    
    print()
    
    print("Question successfully added:")
    print(question_id + " : " + question + "\n")
    
    return question_store, question_id


def new_question(question_store):
    
    """
    Prompts user for the new question, passes the new question to
    add_question_to_store to be processed
    
    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    """
    
    if len(sys.argv) != 2:
        print("\nError: Too many arguments for inserting a new question.")
        print("Please run as \"question.py new\" or consult the documentation.")
        sys.exit(1)
    
    question = input("Please enter the question: ")
    
    print("\nUpdating the question store...\n")
    
    return  add_question_to_store(question_store, question)[0]
    

def load_from_file(question_store):
    
    """
    Takes the path to the source file from among the command line arguments.
    Assumes every line contains one question.
    For each question calls add_question_to_store.

    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    """
    
    if len(sys.argv) != 3:
        print("\nError: Invalid arguments for loading questions from file.")
        print("Please run as \"question.py fromfile <filepath>\" or consult the documentation.")
        sys.exit(1)
    
    # Expects the file path as the second commandline argument
    filepath = sys.argv[2]
    
    # Reads the file line by line and strips the trailing new lines
    with open(filepath) as fd:
        questions = [line.rstrip('\n') for line in fd]
    
    for question in questions:
        question_store = add_question_to_store(question_store, question)[0]
    
    print("\nSuccessfully loaded the questions from the given file. Updating the question store...")
    
    return question_store

def edit_question(question_store):
    
    """
    Takes the question id of the question whose text is to be edited
    from among the command line arguments.
    Prompts the user for the new text of the question.
    Returns an updated question store dictionary.
    
    Strips any leading(before) or trailing(after) whitespace.

    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
     question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    """
    
    if len(sys.argv) != 3:
        print("\nError: Invalid arguments for editing a question.")
        print("Please run as \"question.py edit <question_id>\" or consult the documentation.")
        sys.exit(1)
    
    question_id = sys.argv[2]
    
    # Check if question is in store
    if question_id in question_store.keys():
        # Prompt user
        print("Current text of the question:")
        print("\t" + question_id + " : " + question_store[question_id]["current"] + "\n")
        print("Enter new text for question:")
        text = input("\t> ")
        
        question_store[question_id]["current"] = text.strip("\n ")
        print("Successfully changed the text of the question. Updating the question store...")
        
    else:
        print("\nError: Question not in store.")
        sys.exit(1)

    return question_store

def delete_last_question(question_store):
    
    """
    Prompts the user for confirmation before deleting the last question from store.
    Returns an updated question store.

    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
     question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    """
    
    if len(sys.argv) != 2:
        print("\nError: Too many arguments for deleting the last question.")
        print("Please run as \"question.py deletelast\" or consult the documentation.")
        sys.exit(1)
    
    question_id = decrement_QID( question_store["NEXTINLINE"] )
        
    # Check if the question has been used in any surveys
    if len(question_store[question_id]) == 1:
        # Prompt user
        print("\nAre you sure you wish to remove this question?")
        print(question_id + " : " + question_store[question_id]["current"] + "\n")
        answer = input("[yes/no] >")
        
        if answer.lower() == "yes":
            del question_store[question_id]
            question_store["NEXTINLINE"] = question_id
            question_store["COUNT"]["current"] = question_store["COUNT"]["current"] - 1
            print("\nSuccessfully deleted the question. Updating the question store...")
        else:
            print("Canceled the request, no questions were deleted.")
    else:
        print("\nError: Failed to remove the question as the question has a history.")
        sys.exit(1)

    return question_store

def print_last(question_store):
    
    """
    Prints the current text of the question that was added last to the store

    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
    None.

    """
    
    if len(sys.argv) != 2:
        print("\nError: Too many arguments for printing the last question.")
        print("Please run as \"question.py last\" or consult the documentation.")
        sys.exit(1)
    
    question_id = question_store["NEXTINLINE"]
    question_id = decrement_QID(question_id)
    print("\n" + question_id + " : " + question_store[question_id]["current"])
    
    return

def print_first_n(question_store):
    
    """
    Prints the first N elements of the store oldest to newest,
    takes N from among the command linearguments. If N is greater
    than the number of questions in store, prints all of the questions in
    store and stops.

    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
    None.

    """
    
    if len(sys.argv) != 3:
        print("\nError: Invalid arguments for printing first n questions.")
        print("Please run as \"question.py listfirst <N>\" or consult the documentation.")
        sys.exit(1)
        
    N = int(sys.argv[2])
    question_id = "AAA"
    
    while N>0:
        if question_id == question_store["NEXTINLINE"]:
            return
        print("\n" + question_id + " : " + question_store[question_id]["current"])
        question_id = increment_QID(question_id)
        N = N - 1
    
    return

def print_last_n(question_store):
    
    """
    Prints the last N elements of the store newest to oldest,
    takes N from among the command linearguments. If N is greater
    than the number of questions in store, prints all of the questions in
    store and stops.

    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
    None.

    """
    
    if len(sys.argv) != 3:
        print("\nError: Invalid arguments for printing last n questions.")
        print("Please run as \"question.py listlast <N>\" or consult the documentation.")
        sys.exit(1)
        
    N = int(sys.argv[2])
    question_id = decrement_QID(question_store["NEXTINLINE"])
    
    while N>0:
        print("\n" + question_id + " : " + question_store[question_id]["current"])
        question_id = decrement_QID(question_id)
        N = N - 1
        if question_id == "AAA":
            return
    
    return

def print_all(question_store):
    
    """
    Prints the list of all questions in store.

    Parameters
    ----------
    question_store : Dictionary
        Contains the question store which was read
        from 'data-root/AppData/question-store.yml'.
        
        The question store holds the mapping between the
        registered questions and their unique identifiers
        as well as the usage history of the questions in surveys.

    Returns
    -------
    None.

    """
    
    if len(sys.argv) != 2:
        print("\nError: Too many arguments for printing all questions.")
        print("Please run as \"question.py listall\" or consult the documentation.")
        sys.exit(1)
    
    question_id = "AAA"
    
    while question_id != question_store["NEXTINLINE"]:
        print("\n" + question_id + " : " + question_store[question_id]["current"])
        question_id = increment_QID(question_id)

    return

def print_history(question_store):
    
    """
    Takes the question ID from among the commandline arguments, prints history of
    the related question.

    Parameters
    ----------
    question_store : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    if len(sys.argv) != 3:
        print("\nError: Invalid arguments for printing the history of a question.")
        print("Please run as \"question.py historyof <question_id>\" or consult the documentation.")
        sys.exit(1)
        
    question_id = sys.argv[2]
    
    for survey in question_store[question_id].keys():
        print("[" + survey + "] " + question_store[question_id][survey])
    
    return

def copy_store():
    
    """
    Takes the destination path from among the command line arguments. Makes a copy
    of the question store at the destination. The path can be either that of a directory
    or that of a file.

    Returns
    -------
    None.

    """
    
    if len(sys.argv) != 3:
        print("\nError: Invalid arguments for making a copy of the question store.")
        print("Please run as \"question.py getcopy <path/to/destination>\" or consult the documentation.")
        sys.exit(1)
    
    # Get data-root from the config file
    with open(DATA_ROOT_CONFIG_REL, "r") as fd:
        data_root = yaml.safe_load(fd)['root']
    
    source = data_root / QS_FROM_ROOT
    destination = Path(sys.argv[2])
        
    try:
        copy(source, destination)
    except IOError as e:
        print("Unable to copy file. %s" % e)
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info())
        sys.exit(1)
        
    print("Successfully created a copy of the question store")
    return

def fresh_question_store(target_directory):
    
    """
    Sets up the question store at the target directory.
    
    Currently only used by setup.py while setting up a fresh tree.

    Parameters
    ----------
    target_directory : pathlib.Path object
        The parent directory in which the question store will be created.

    Returns
    -------
    None.

    """
    
    question_store = {"NEXTINLINE" : "AAA", \
                      "COUNT" : { "current" : 0, "maximum" : 17576 } }
    
    with open(target_directory / "question-store.yml", 'w') as fd:
        yaml.dump(question_store, fd)
        
    return


def main():
    
    """
    Manages the question-store, every question that is used or will be used in a survey
    must be registered into the store in order for the system to function properly.
    
    The registry kept on the questions makes it possible to compare the answers to
    the same questions from different surveys even if the exact wording of the
    question changes over time.
    
    The question store, located at (data-root)/AppData/question-store.yml, keeps track
    of the entire usage history of each question
    
    - question.py new (generates a new question identifier, asks for the question, puts the key value pair into the question store and prints them)
    - question.py fromfile <path/to/file> (registers the questions contained in the source file)
    - question.py edit <question_id> (used for updating the current text of the question)
    - question.py deletelast (prompts for confirmation, then deletes the question entry IF there is no history)
    - question.py last (prints last key value pair)
    - question.py listfirst <N> (lists the first N key value pairs)
    - question.py listlast <N> (lists the last N key value pairs)
    - question.py listall (lists all of the key value pairs in store)
    - question.py historyof <question_id> (lists all of the wordings of the question that were used in the past)
    - question.py getcopy <path/to/dest> (creates copy of the store at the destination, the destination can be a file or a directory)
    - question.py help (prints the docstring)
    
    Returns
    -------
    None.

    """
    
    if len(sys.argv) == 1 or sys.argv[1] == "help":
        print(main.__doc__)
        return
    
    command = sys.argv[1]
    
    if command == 'getcopy':
        copy_store()
    else:
        switch = { "new" : new_question,
                   "fromfile" : load_from_file,
                   "edit" : edit_question,
                   "deletelast" : delete_last_question,
                   "last" : print_last,
                   "listfirst" : print_first_n,
                   "listlast" : print_last_n,
                   "listall" : print_all,
                   "historyof" : print_history }
        
        if sys.argv[1] in switch.keys():
            with open(DATA_ROOT_CONFIG_REL, "r") as fd:
                data_root = yaml.safe_load(fd)['root']
            
            with open(data_root / QS_FROM_ROOT, "r") as fd:
                question_store = yaml.safe_load(fd)
                switch[command](question_store)
            
            if command.startswith("list") or command == "historyof" or command == "last":
                return
            
            with open(data_root / QS_FROM_ROOT, "w") as fd:
                yaml.dump(question_store, fd)
                print("\nDone.")
        else:
            print("\nError: Unrecognized option, please check the documentation.")
            sys.exit(1)
    return

if __name__ == "__main__":
    main()
    