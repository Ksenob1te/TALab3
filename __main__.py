from src import *




if __name__ == '__main__':
    print("TYPE IN THE NAME OF THE SCRIPT: ")
    script_name = input()
    result = methods._function_call(compile_script(script_name), parameters=[])
    # print(int(result))
    print(global_robot.position)