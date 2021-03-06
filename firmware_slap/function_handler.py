import r2pipe
import argparse
import IPython
from tqdm import tqdm
from termcolor import colored


def get_function_information(file_name):
    func_list = []

    r2_ins = r2pipe.open(file_name, flags=["-2"])
    '''
    Commands = ['aa', 'afr', '& aap', '& aac', '& aar', '& aaE',
            '& aaf', '& aas', '& aae', '& aav', '&&', 'afva', 'afta']
    
    for command in tqdm(Commands, desc="Analysis Running"):
        r2_ins.cmd(command)
    '''

    r2_ins.cmd('aaa')
    try:
        func_list = r2_ins.cmdj('aflj')
    except:
        func_list = []
    r2_ins.quit()
    return func_list


def get_arg_funcs(file_name):
    return [
        x for x in get_function_information(file_name)
        if len(x) > 0 and 'nargs' in x.keys() and x['nargs'] > 0
    ]


def get_base_addr(file_name):
    r2_ins = r2pipe.open(file_name, flags=["-2"])
    return r2_ins.cmdj('ij')['bin']['baddr']


def get_func_args(func):
    arg_list = []
    for var in (func['bpvars'] + func['regvars']):
        if 'arg' in var['kind']:
            arg_list.append(var)
        elif 'arg' in var['name'] and 'reg' in var['kind']:
            arg_list.append(var)
    return arg_list

def print_function(func):

    is_ghidra = False 

    # Function is a ghidra one
    if 'HiFuncProto' in func.keys():
        is_ghidra = True
        prototype = func['HiFuncProto']
        code = func['c_code']
    file_name = func['file_name']
    func_name = func['name']
    bug = func['result']

    if not func['result']:
        return

    bug_type = bug['type']
    print(
        colored("{} found in {} at {}".format(bug_type, file_name, func_name),
                'red',
                attrs=['bold']))

    import re
    if is_ghidra:
        print(colored(prototype, 'cyan', attrs=['bold']))
    for arg in bug['args']:
        data = arg['value']
        # data = re.sub('\\\\x[0-9][0-9]', '', data)
        print(
            colored("\t{} : {}".format(arg['base'], data),
                    'white',
                    attrs=['bold']))
    if 'Injected_Location' in bug.keys():
        print(colored("Injected Memory Location", 'cyan', attrs=['bold']))

        data = bug['Injected_Location']['Data']
        # data = re.sub('\\\\x[0-9][0-9]', '', data)

        print(colored("\t{}".format(data), 'white', attrs=['bold']))
    print(colored("Tainted memory values", 'cyan', attrs=['bold']))
    for mem_val in bug['mem']:
        print(
            colored("{}".format(mem_val['BBL_DESC']['DESCRIPTION']),
                    'yellow',
                    attrs=['bold']))
        if 'DATA_ADDRS' in mem_val.keys():
            print(
                colored("\tMemory load addr {}".format(
                    mem_val['DATA_ADDRS'][0]),
                        'white',
                        attrs=['bold']))
        # data = re.sub('\\\\x[0-9][0-9]', '', mem_val['DATA'])
        # print(
        #    colored("\tMemory load value {}".format(data),
        #            'white',
        #            attrs=['bold']))
        print()


def test():
    parser = argparse.ArgumentParser()

    parser.add_argument("File")

    args = parser.parse_args()

    info = get_function_information(args.File)

    arg_funcs = [x for x in info if x['nargs'] > 0]

    IPython.embed()


if __name__ == "__main__":
    test()
