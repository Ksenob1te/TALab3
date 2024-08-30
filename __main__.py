from src import *

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog="PyBison")
    parser.add_argument("-k", "--keepfiles", action="store_true",
                        help="Keep temporary files used in building parse engine lib")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose messages while parser is running")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable garrulous debug messages from parser engine")
    args = parser.parse_args()

    p = Parser(keepfiles=args.keepfiles, verbose=args.verbose)
    print("TYPE IN THE NAME OF THE SCRIPT: ")
    script_name = input()

    with open(f'./{script_name}', 'r') as content_file:
        content = content_file.read()
    compiled_program = p.parse_string(content, debug=False)
    if isinstance(compiled_program, Exception):
        raise compiled_program
    if compiled_program is False:
        raise ValueError("Error in parsing")
    func_list = []
    for statement in compiled_program:
        func_list.append(statement())

    main_func = None
    for func in func_list:
        if func.name == "main":
            main_func = func
            break

    result = methods._function_call(main_func, parameters=[])
    # print(int(result))
    print(global_robot.position)