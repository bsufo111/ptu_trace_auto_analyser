# -*- coding: utf-8 -*-
'''
Created on 2015年3月24日

@author: wadefu
'''
import re
import copy
from pprint import pprint

struct_name_index = 0
struct_name1_index = 1
msg_name_index = 2
union_item_num_index = 3
struct_redecode_flag_index = 3
struct_field_num_index = 4
struct_total_size_index = 5

#struct_index = -1

class pmuptu_basic_struct(object):
    def __init__(self, filename):
        self.basic_struct = []
        self.result = []
        self.pmuptu_filename = filename
        self.pat1 = r'/\*(\*)+\*/'
        self.pat2 = r'BASIC STRUCTURE DESCRIPTION'
        self.pat3 = ''  # for pmu
        self.pat4 = ''  # for ptu
        self.search_list = []
        
        self.pmuptu_decoder()
        self.result = self.basic_struct
        
    def pmuptu_decoder(self):

        pmuptu_file = open(self.pmuptu_filename,'r')
        count=0
        begin_struct_decoder = 0 #0:not begin, 1:betin to decode basic struct, 2:begin to decode pmuptu msg
        struct_index = -1
        find_struct_flag=0   #0:not find, 1:find
        if0case=0
        read_line_noneed = 0   #0:need to call readline(), 1:no need to call readline()
        field_num = 0
        total_size = 0        
        pat1 = self.pat1
        pat2 = self.pat2
        pat3 = self.pat3
        pat4 = self.pat4
        union = []
        find_union_flag = 0
#        result = self.basic_struct
        while True:
            if read_line_noneed == 0:
                line = pmuptu_file.readline()
            read_line_noneed = 0
            if not line: break
            if line.strip(' \n') == '#if 0':
                if0case+=1
                continue
            elif line.strip(' \n') == '#endif':
                if0case-=1
                continue
            if if0case > 0:
                continue
            if re.search(pat1, line):
                line = pmuptu_file.readline()
                if not line: break
                if pat2 in line:
#                     line = pmuptu_file.readline()
#                     if not line: break
#                     if re.search(pat1, line):
                    begin_struct_decoder = 1    # basic struct
                    result = self.basic_struct
                    struct_index = -1           # restart to count
                    union_index = -1
                elif pat3:
                    if pat3 in line:
                        begin_struct_decoder = 2    # pmu-ptu msg struct for PMU
#                        print '!!!!!!!!!!!!!enter into pmu area!!!!!!!!!!!!!'

                        result = self.result
                        struct_index = -1           # restart to count
                        union_index = -1
#                elif pat4:
                    if pat4 in line:
                        begin_struct_decoder = 3    # pmu-ptu msg struct for PTU
#                        print '!!!!!!!!!!!!!enter into ptu area!!!!!!!!!!!!!'
                        result = self.result
                        struct_index = -1           # restart to count
                        union_index = -1
                    
                    
                        
            if begin_struct_decoder >=1:
                if 'typedef' in line and 'union' in line:
                    find_union_flag = 1
                    num = 0
                    union.append([['','','',0]])
                    union_index += 1
                    continue
                
                if 'typedef' in line and 'struct' in line:
                    find_struct_flag=1              #find one struct
                    num=0                           #indicate the index of field in a struct
                    linelist=line.split()
        #            linelist[2]=linelist[2].strip(' {\n')
        #            print linelist[2]
                    result.append([['','','',0,0,0],[]])
                    count+=1
                    struct_index+=1
                    continue
                elif 'typedef' in line and not 'union' in line and not 'enum' in line and begin_struct_decoder == 2:
                    typedef_list_pmu = line.split()
                    typedef_list_pmu[2] = typedef_list_pmu[2].strip(',; ')
                    typedef_decode_list = self.re_decode_one_struct(self.search_list+self.basic_struct+self.result, typedef_list_pmu[1])
                    if not typedef_decode_list: continue
                    typedef_decode_list1 = copy.deepcopy(typedef_decode_list)
#                     print typedef_decode_list1
#                     print typedef_list_pmu
                    write_to_file('test.txt', self.search_list+self.basic_struct+self.result)

                    typedef_decode_list1[0][struct_name_index] = typedef_list_pmu[2]
                    typedef_decode_list1[0][struct_name1_index] = typedef_list_pmu[2]+'_t'
                    result.append(typedef_decode_list1)

#                     result.append(typedef_decode_list)
                    count+=1
                    struct_index+=1
#                     result[struct_index][0][struct_name_index] = typedef_list_pmu[2]
#                     result[struct_index][0][struct_name1_index] = typedef_list_pmu[2]+'_t'
                    continue
                if begin_struct_decoder == 3 and 'typedef' in line:
                    typedef_list_ptu = line.split()
                    typedef_list_ptu[2] = typedef_list_ptu[2].strip(',; ')
                    msg_name = typedef_list_ptu[2][:-5]
                    print msg_name
                    typedef_decode_list_ptu = self.re_decode_one_struct(self.search_list+self.basic_struct+self.result, typedef_list_ptu[1])
                    if not typedef_decode_list_ptu: continue
                    typedef_decode_list_ptu[0][msg_name_index] = msg_name
                    
                
                if find_union_flag == 1:
#                    union_list = [['','','',0,0,0],[]]
                    if '}' in line:                     #end of union
                        find_union_flag = 0
                        union_string = line.strip('} ,;\n')
#                        union_list[0][struct_name_index] = union_string
                        union[union_index][0][struct_name_index]=union_string
                        line1 = pmuptu_file.readline()
                        if not line1: break
                        if not ';' in line1 and not 'typedef' in line1:
                            continue
                        elif 'typedef' in line1:
                            line = line1
                            read_line_noneed = 1
                            continue
                        linelist1 = line1.split()
                        if linelist1:
                            union_string1 = linelist1[0].strip(' ;\n')
#                            union_list[0][struct_name1_index]=union_string1
                            union[union_index][0][struct_name1_index] = union_string1              
                        continue
                    elif not ';' in line:
                        continue
                    
                    else:                                #find field of struct
                        linelist2=line.split()
                        linelist2[1]=linelist2[1].strip(' {;\n')
#                        union[union_index][0][union_item_num_index] += 1

                        if linelist2[0] == 'u_byte':
                            size=1
                        elif linelist2[0] == 'u_short':
                            size=2
                        elif linelist2[0] == 'u_int':
                            size=4
                        elif '*' in linelist2[0]:
                            size=4
                        else:                                                        #structure, need to re decode
                            size = 0

                            redecode_list = self.re_decode_one_struct(self.search_list+self.basic_struct, linelist2[0])
                            if redecode_list:
                                
                                size = redecode_list[0][struct_total_size_index]
                                num = redecode_list[0][struct_field_num_index]
                                union[union_index][0].append(num)
                                union[union_index][0].append(size)
                                union[union_index].append(redecode_list[1])
                                union[union_index][0][union_item_num_index] += 1
                                                            
                                continue

                        union[union_index][0].append(1)
                        union[union_index][0].append(size)
                        union[union_index].append([[linelist2[0],linelist2[1],size]])
                        union[union_index][0][union_item_num_index] += 1
                             
                    
                    
                if find_struct_flag == 1:                              
                    if '}' in line:                     #end of struct
                        find_struct_flag=0
                        
                        struct_string=line.strip('} ,;\n')
                        result[struct_index][0][struct_name_index]=struct_string
                        line1 = pmuptu_file.readline()
                        if not line1: break
                        if not ';' in line1 and not 'typedef' in line1:
                            continue
                        elif 'typedef' in line1:
                            line = line1
                            read_line_noneed = 1
                            continue
                        linelist1 = line1.split()
                        if linelist1:
                            struct_string1 = linelist1[0].strip(' ;\n')
                            result[struct_index][0][struct_name1_index]=struct_string1               
                        continue
        #            elif '{' in line and not ';' in line:
                    elif not ';' in line:
                        continue
                    else:                                #find field of struct
                        linelist2=line.split()
                        linelist2[1]=linelist2[1].strip(' {;\n')
#                        result[struct_index][0][struct_field_num_index]+=1         #the number of fields of this struct add 1

                        mul = 1
                        if '[' in linelist2[1]:
                            i = linelist2[1].index('[')
                            j = linelist2[1].index(']')
                            mul = int(linelist2[1][i+1:j])
                            linelist2[1]=linelist2[1][0:i]

                            
                        if linelist2[0] == 'u_byte':
                            size=1
                        elif linelist2[0] == 'u_short':
                            size=2
                        elif linelist2[0] == 'u_int':
                            size=4
                        elif '*' in linelist2[0]:
                            size=4
                        else:                                                        #structure, need to re decode
                            size = 0
#                            print linelist2[1]
                            redecode_list = self.re_decode_one_struct(self.search_list+self.basic_struct+union, linelist2[0])
                            if redecode_list:
                                if redecode_list[0][union_item_num_index] == 0:
                                                                    
                                    size = redecode_list[0][struct_total_size_index]*mul
                                    num = redecode_list[0][struct_field_num_index]*mul
                                    if mul == 1:                                                                       
                                        for subitem in redecode_list[1]:
                                            result[struct_index][1].append(subitem)
#                                            result[struct_index][1].append([subitem[0], linelist2[1]+'.'+subitem[1],subitem[2]])
                                        
                                    else:
                                        for k in range(mul):
                                            for subitem in redecode_list[1]:
                                                result[struct_index][1].append([subitem[0],linelist2[1]+'['+str(k)+']'+'.'+subitem[1],subitem[2]])
                                    result[struct_index][0][struct_total_size_index] += size
                                    result[struct_index][0][struct_field_num_index] += num         #the number of fields of this struct add num
                                    
                                    continue
                                else:
                                    result[struct_index][0][union_item_num_index] = redecode_list[0][union_item_num_index]
                                    for m in range(redecode_list[0][union_item_num_index]):
                                        if m < redecode_list[0][union_item_num_index]-1:
                                            union_copy = copy.deepcopy(result[struct_index][1+m])
                                            result[struct_index].append(union_copy)
                                            result[struct_index][0].append(result[struct_index][0][struct_field_num_index+m*2])
                                            result[struct_index][0].append(result[struct_index][0][struct_total_size_index+m*2])
                                        for subitem in redecode_list[1+m]:
                                            result[struct_index][1+m].append(subitem)
                                        result[struct_index][0][struct_field_num_index+m*2] += redecode_list[0][struct_field_num_index+m*2]
                                        result[struct_index][0][struct_total_size_index+m*2] += redecode_list[0][struct_total_size_index+m*2]
                                    continue   

                        result[struct_index][1].append([linelist2[0],linelist2[1],size*mul])
                        result[struct_index][0][struct_total_size_index] += size*mul
                        result[struct_index][0][struct_field_num_index] += 1         #the number of fields of this struct add 1
        pmuptu_file.close()
        print self.pmuptu_filename
        print count
        print
        pprint(union)

    def re_decode_one_struct(self, search_list, struct_name):
        for item in search_list:
            if item[0][struct_name_index] == struct_name or item[0][struct_name1_index] == struct_name:
                return item        # [['','',0,0,0],[]]
        return []

class pmuptu_struct(pmuptu_basic_struct):
    def __init__(self, filename, basic_structure):
        self.basic_struct = []
        self.result = []
        self.pmuptu_filename = filename
        self.pat1 = r'/\*(\*)+\*/'
        self.pat2 = r'STRUCTURE DEFINITION'
        self.pat3 = r'MESSAGE DESCRIPTION FOR PMU'  # for pmu
        self.pat4 = r'MESSAGE DESCRIPTION FOR PTU'  # for ptu
        self.search_list = basic_structure        
        self.pmuptu_decoder()
        
def print_struct(struct_list):
    if not struct_list:
        print '###################'
        print '# No item in list #'
        print '###################'
        return
    for i in struct_list:
        print i[0]
        for m in range(i[0][union_item_num_index]):
            for j in i[1+m]:
                print '    ',j
            print
        print '------------------------------------'
def write_to_file(file_name, struct_list):
    if not struct_list:
        print '##########################################'
        print '# No item in list, '+file_name+' #'
        print '##########################################'
        return
    file = open(file_name,'w+')
    if not file:
        print 'No this file: '+file_name
        return
    for struct_item in struct_list:
        file.writelines(['\n'])
        if struct_item[0][msg_name_index]:
            msg_str = struct_item[0][msg_name_index]+', '
        else:
            msg_str = ''
        header_str = struct_item[0][struct_name_index]+', '+struct_item[0][struct_name1_index]+', '+msg_str+str(struct_item[0][union_item_num_index])
        if struct_item[0][union_item_num_index] > 0:
            for i in range(struct_item[0][union_item_num_index]):
                header_str += (', '+str(struct_item[0][struct_field_num_index+i*2])+', '+str(struct_item[0][struct_total_size_index+i*2]))
        else:
            header_str += (', '+str(struct_item[0][struct_field_num_index])+', '+str(struct_item[0][struct_total_size_index]))  
                  
        file.writelines([header_str,'\n'])
        
        if struct_item[0][union_item_num_index] > 0:
            for j in range(struct_item[0][union_item_num_index]):
                
                for field_item in struct_item[1+j]:
        #            print field_item
                    format_field = '    %-*s%-*s%*d' % (12, field_item[0], 30, field_item[1], 6, field_item[2])
        #            file.writelines(['    '+field_item[0]+'    '+field_item[1]+'            '+str(field_item[2]),'\n'])
                    file.writelines([format_field, '\n'])
                file.writelines(['--------------------------------------------------------------------------', '\n'])
        else:
            for field_item in struct_item[1]:
    #            print field_item
                format_field = '    %-*s%-*s%*d' % (12, field_item[0], 30, field_item[1], 6, field_item[2])
    #            file.writelines(['    '+field_item[0]+'    '+field_item[1]+'            '+str(field_item[2]),'\n'])
                file.writelines([format_field, '\n'])
            file.writelines(['--------------------------------------------------------------------------', '\n'])            

def write_to_file1(file_name, struct_list):
    if not struct_list:
        print '##########################################'
        print '# No item in list, '+file_name+' #'
        print '##########################################'
        return
    file = open(file_name,'w+')
    if not file:
        print 'No this file: '+file_name
        return
    for struct_item in struct_list:
        file.writelines(['\n'])
        file.writelines([struct_item[0][struct_name_index]+', '+struct_item[0][struct_name1_index],'\n'])
        for field_item in struct_item[1]:
#            print field_item
            format_field = '    %-*s%-*s%*d' % (12, field_item[0], 30, field_item[1], 6, field_item[2])
#            file.writelines(['    '+field_item[0]+'    '+field_item[1]+'            '+str(field_item[2]),'\n'])
            file.writelines([format_field, '\n'])                         

if __name__ == '__main__':
    pmuptu_basic = pmuptu_basic_struct(r'pmuptu\pmuptubasicstructure.h')
#    print_struct(pmuptu_basic.result)
    write_to_file('pmuptubasicstructure.txt', pmuptu_basic.result)
    
    pmuptu_xdr = pmuptu_struct(r'pmuptu\xdrforsubsystem.h', pmuptu_basic.result)
    write_to_file('xdrforsubsystem.txt', pmuptu_xdr.basic_struct)
    
    pmuptu_pm = pmuptu_struct(r'pmuptu\pmuptupmtypes.h', pmuptu_basic.result)
    write_to_file('pmuptupmtypes.txt', pmuptu_pm.basic_struct)
    
    pmuptu_dsp = pmuptu_struct(r'pmuptu\pmuptudspmsginterface.h', pmuptu_basic.result+pmuptu_xdr.basic_struct+pmuptu_pm.basic_struct)
    write_to_file('pmuptudspmsginterface.txt', pmuptu_dsp.result)
    
    pmuptu_gch = pmuptu_struct(r'pmuptu\pmuptugchmsginterface.h', pmuptu_basic.result)
    write_to_file('pmuptugchmsginterface.txt', pmuptu_gch.result)
    
    pmuptu_pdch = pmuptu_struct(r'pmuptu\pmuptupdchmsginterface.h', pmuptu_basic.result)
    write_to_file('pmuptupdchmsginterface.txt', pmuptu_pdch.result)    
    
    pmuptu_tbf = pmuptu_struct(r'pmuptu\pmuptutbfmsginterface.h', pmuptu_basic.result)
#    print_struct(pmuptu_tbf.basic_struct)
#    print_struct(pmuptu_tbf.result)
    write_to_file('pmuptutbfmsginterface.txt', pmuptu_tbf.result) 
    
    pmuptu_trx = pmuptu_struct(r'pmuptu\pmuptutrxmsginterface.h', pmuptu_basic.result+pmuptu_xdr.basic_struct+pmuptu_pm.basic_struct)
    write_to_file('pmuptutrxmsginterface.txt', pmuptu_trx.result)
#     print_struct(pmuptu_trx.basic_struct)
#     print_struct(pmuptu_trx.result)
#     pprint(pmuptu_trx.basic_struct)
    
    
