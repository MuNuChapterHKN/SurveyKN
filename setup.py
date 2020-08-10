# -*- coding: utf-8 -*-

import sys
import yaml
import shutil
from pathlib import Path
from os.path import realpath
from question import fresh_question_store

DATA_ROOT_CONFIG_REL = Path(realpath(__file__)).parent / "data-root-config.yml"
DATA_ROOT_NAME = "SurveyKN-dataroot"
WIN_MAX_PATH_LENGTH = 200

def create_fresh_directory_tree(new_path):
    
    """
    Creates a fresh directory tree at the location pointed to by new_path.
    During the creation of the tree calls fresh_question_store from question.py
    to initialize the question store.
    Creates the data-root-config.yml file that contains the pointer to the data root.
    
    Current directory tree:
        
        HKDataRoot
        |-- Surveys
        |-- Visuals
        |-- Templates
        |-- AppData
    
    
    The function is currently written to support a one level directory tree,
    should the directory structure need to be updated to go deeper this function
    should be updated appropriately.

    Parameters
    ----------
    new_path : pathlib.Path object
        The path object that points to the parent directory in which the fresh
        tree will be created.

    Returns
    -------
    None.

    """
    
    # If in the future the fresh tree includes more levels
    # this needs to be turned into a dictionary of dictionaries
    # a function can be written to automatically generate the
    # directories
    directory_tree = ["Surveys",
                      "Visuals",
                      "Templates",
                      "AppData"]
    
    data_root = new_path / DATA_ROOT_NAME
    try:
        data_root.mkdir()
    except FileExistsError:
        print("\nError: The directory " + DATA_ROOT_NAME + " already exists at given location")
        sys.exit(1)
    
    for directory in directory_tree:
        directory_path = data_root / directory
        directory_path.mkdir()
    
    app_data = data_root / "AppData"
    fresh_question_store(app_data)
    
    with open(DATA_ROOT_CONFIG_REL, "w") as fd:
        data_root_config = { "root" : data_root.absolute().resolve().__str__() }
        yaml.dump(data_root_config, fd)
    
    print("\nSuccesfully created the fresh directory tree at the given location and updated the configuration.")
    
    return

def redirect_dataroot_pointer(old_path, new_path):
    
    """
    Only changes the pointer to the data root in data-root-config.yml
    Does NOT move or copy any data to the target directory.

    Parameters
    ----------
    old_path : pathlib.Path object
        The path object that points to the path that used to be the data root
    new_path : pathlib.Path object
        The path object that points to the path that will host the new data root

    Returns
    -------
    None.

    """
    data_root = new_path / DATA_ROOT_NAME
    
    print("The data root pointer will be changed from\n\n" + old_path.absolute().resolve().__str__() \
          + "\n\nto\n\n" + data_root.absolute().resolve().__str__() + "\n\n" \
          + "WARNING: This action will NOT copy or move any data, for the system to function properly the new destination must also have the appropriate files" \
          + "\nDo you wish to proceed?")
    answer = input("[yes/no] > ")
    
    if answer.lower() == "yes":
        with open(DATA_ROOT_CONFIG_REL, "w") as fd:
            data_root_config = { "root" : data_root.absolute().resolve().__str__() }
            yaml.dump(data_root_config, fd)
        print("Data root pointer successfully updated.")
    else:
        print("Cancelled request, no changes were made.")
    
    return

def move_directory_tree(old_path, new_path):
    
    """
    Moves the data root and all of its contents to at the location pointed to by new_path.
    Calls shutil.move
    
    Parameters
    ----------
    old_path : pathlib.Path object
        The path object that points to the path that used to be the data root
    new_path : pathlib.Path object
        The path object that points to the path where the data root will be moved

    Returns
    -------
    None.

    """
    
    data_root = new_path / DATA_ROOT_NAME
    
    print("The data root and all its contents will be moved from\n\n" + old_path.absolute().resolve().__str__() \
          + "\n\nto\n\n" + data_root.absolute().resolve().__str__() + "\n\n" \
          + "\nDo you wish to proceed?")
    answer = input("[yes/no] > ")
    
    if answer.lower() == "yes":
        print("\nMoving...\n\n")
        shutil.move(old_path.absolute().resolve().__str__(), data_root.absolute().resolve().__str__())
        
        with open(DATA_ROOT_CONFIG_REL, "w") as fd:
                data_root_config = { "root" : data_root.absolute().resolve().__str__() }
                yaml.dump(data_root_config, fd)
        
        print("Successfully moved the data root and updated the configuration.")
    else:
        print("Cancelled request, no changes were made.")    
    
    return

def copy_directory_tree(old_path, new_path):
    
    """
    Copies the data root and all of its contents to at the location pointed to by new_path.
    Calls shutil.copytree
    
    This function doesn't update the configuration, in order to start working with the
    copy of the data root, one must call setup.py redirect in order to update the configuration
    
    Parameters
    ----------
    old_path : pathlib.Path object
        The path object that points to the data root
    new_path : pathlib.Path object
        The path object that points to the path where a copy of the data root will be generated

    Returns
    -------
    None.

    """
    
    data_root = new_path / DATA_ROOT_NAME
    
    print("\n\nThe data root and all its contents will be copied from\n\n" + old_path.absolute().resolve().__str__() \
          + "\n\nto\n\n" + data_root.absolute().resolve().__str__() + "\n\n" \
          + "\nDo you wish to proceed?")
    answer = input("[yes/no] > ")
    
    if answer.lower() == "yes":
        print("\nCopying...\n\n")
        shutil.copytree(old_path.absolute().resolve().__str__(), data_root.absolute().resolve().__str__())
        
        print("Successfully copied the data root.")
        print("NOTICE: The configuration isn't updated, if you wish to base the data root at the new location you need to redirect the pointer using setup.py redirect")
    else:
        print("Cancelled request, no changes were made.")    
    
    return

def prompt_user_for_path():
    
    """
    Prompts the user for the target path.
    
    The function also takes into consideration that Windows has a 260 character upper limit on file
    paths and conducts the necessary checks.

    Returns
    -------
    new_path : pathlib.Path object
        The target path given by user

    """
    
    # While true is used here in order to imitate 'do while' in Python
    while True:
        if sys.platform.startswith("win") or sys.platform == "cygwin":
            new_path_string = input("\nPlease enter the new data root path, the absolute path should not be longer than " + str(WIN_MAX_PATH_LENGTH) + " characters\n>")
            new_path = Path(new_path_string)
            
            # Check for the character limit on the absolute path
            while len(new_path.absolute().resolve().__str__()) > WIN_MAX_PATH_LENGTH:
                print("\nError: The absolute path is longer than " + str(WIN_MAX_PATH_LENGTH) + " characters!")
                print("The Windows operating system has a maximum path length we musn't surpass.")
                new_path_string = input("Please enter the new data root path, the absolute path should not be longer than " + str(WIN_MAX_PATH_LENGTH) + " characters\n>")
        else:
            new_path_string = input("\nPlease enter the new data root path\n>")
            new_path = Path(new_path_string)
        
        if new_path.is_dir():
            break
        
        print("\nError: The given path is not a valid directory, please try again\n")
    
    return new_path

def main():
    
    """
    Responsible for managing the directory structure.
    
    - setup.py fresh (prompts user for the root, builds a fresh directory tree at the given root, creates question store, updates pointer)
    - setup.py redirect (prompts user for the new root, updates pointer)
    - setup.py move (prompts user for the new root, moves the tree along with the data to new location, updates pointer)
    - setup.py copy (prompts user for the new root, copies the tree along with the data to new location, does NOT update the pointer)
    - setup.py help (prints the docstring)

    Returns
    -------
    None.

    """
    
    if len(sys.argv) == 1 or sys.argv[1] == "help":
        print(main.__doc__)
        return
    
    switch = { "redirect" : redirect_dataroot_pointer,
               "move" : move_directory_tree,
               "copy" : copy_directory_tree }
    
    if not sys.argv[1] in switch.keys() and not sys.argv[1] == "fresh":
        print("\nError: Unrecognized option, please check the documentation.")
        sys.exit(1)
    
    new_path = prompt_user_for_path()
    
    if sys.argv[1] == "fresh":
        create_fresh_directory_tree(new_path)
    else:
        with open(DATA_ROOT_CONFIG_REL, "r+") as fd:
            old_path_string = yaml.safe_load(fd)["root"]
        
        old_path = Path(old_path_string)
        switch[sys.argv[1]](old_path, new_path)
    
    return


if __name__ == "__main__":
    main()
    
