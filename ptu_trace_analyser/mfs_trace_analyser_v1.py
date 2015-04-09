# -*- coding: utf-8 -*-
'''
Created on 2015.3.25

@author: wadefu
'''
import sys
sys.path.append(r'D:\Study\python\python_project\eclipse_workspace\ptu_trace_auto_analyser\src')
#from pmuptu_interface_decode.pmuptu_intf_decode_v1 import pmuptu_basic_struct, pmuptu_struct, write_to_file, struct_name_index, struct_name1_index, msg_name_index, union_item_num_index, struct_redecode_flag_index, struct_field_num_index, struct_total_size_index
from pmuptu_interface_decode.pmuptu_intf_decode_v1 import *
from sys import argv


def mfs_trace_analyser(file_name, pmuptu_intf_list):
    
    mfstrace_file = open(file_name, 'r')
#    line = mfstrace_file.readline()
    if not mfstrace_file:
        print '!!!!!can not find file: '+file_name
        exit()
    result_dspx_file_open_list = []
    for i in range(4):
        result_dspx_file_open_list.append(open(file_name[:-4]+'_dsp'+str(i)+'.txt','w+'))
    
    for line in mfstrace_file:
        if len(line) <= 2:
            continue
        if ('ptuId' in line or 'ptuid' in line) and ('incomingptumsgforwarderptu' in line or 'incomingptumsgforwardertbf' in line or 'incomingptumsgforwardertrx' in line \
        or 'incomingptumsgforwardertrans' in line or 'tdmptuproxy' in line or 'ipptuproxy' in line or 'dmrimpl' in line or 'dmrfortrximpl' in line \
        or 'dmrfortbfimpl' in line or 'dmrfordspimpl' in line or 'dmrforgchimpl' in line or 'ipptuchannelcontroler' in line):
            line = line.strip('\n')
            line_list = line.split('|')
            line_no = line_list[0].strip()                  # record line number
            line_date = line_list[2].strip()                # record line date
            line_time = line_list[3].strip()                # record line time
            line_list1 = line_list[4].split(':')
            line_list1[5] = line_list1[5].strip(' ')
            msg_right_index = line_list1[5].find('(')
            if msg_right_index == -1:
                print 'trace error!!!! lack of "("!!!!! in line '+line_no+' in '+file_name
                for li in result_dspx_file_open_list:
                    li.close()
                exit()
            
            msg_struct_name = line_list1[5][:msg_right_index]           # record msg struct name
            msg_struct_index = line_list[4].find(msg_struct_name)
            if msg_struct_index == -1:
                print 'trace error!!!! can not find msg struct name'
                for li in result_dspx_file_open_list:
                    li.close()
                exit()
            if msg_struct_name[:7] == 'forward':
                msg_struct_name = msg_struct_name[7:]
            msg_struct_content = line_list[4][msg_struct_index:]

            msg_property_right_index = msg_struct_content.find(')')
            if msg_property_right_index == -1:
                print 'trace error!!!! lack of ")"!!!!! in line '+line_no+' in '+file_name
                for li in result_dspx_file_open_list:
                    li.close()
                exit()
            
            msg_property = msg_struct_content[msg_right_index+1:msg_property_right_index]        #record some property of this msg like tbfIndex, trxIndex
            ptuId_index = msg_struct_content.find('ptu', msg_property_right_index)
            if ptuId_index == -1:
                print 'trace error!!!! lack of "ptuId"!!!!! in line '+line_no+' in '+file_name
                for li in result_dspx_file_open_list:
                    li.close()
                exit()
            ptuId = int(msg_struct_content[ptuId_index+6])       #record ptuId
            if ptuId > 3:
                print '!!!!!abnormal case: ptuId > 3, in line '+line_no+' in'+file_name
                continue
            if msg_struct_name == 'TrxSysDefineReq':
                msg_content = msg_struct_content[ptuId_index+10+11:].strip(' ')    #record msg content
                mfstrace_file.next()     # next line is only a \n
                line = mfstrace_file.next()     # next line includes the next part of TrxSysDefineReq
                if not 'TrxSysDefineReq' in line:
                    print '###### can not find the next part of msg TrxSysDefineReq'
                else:
                    msg_content += line.split(':')[-1].strip(' \n')
            else:
                msg_content = msg_struct_content[ptuId_index+10:].strip(' ')    #record msg content
                
            
            temp_index = msg_content.find('[and')
            if temp_index != -1:
                msg_content = msg_content[:temp_index]
            
#            print line_no+', '+line_date+', '+line_time+', '+msg_struct_name+', '+msg_property+', '+str(ptuId)+', '+msg_content
            
#             written_str_list = [line_no+', '+line_date+', '+line_time+', '+msg_struct_name+', '+msg_property+', '+str(ptuId)+', '+msg_content, '\n']
#             result_dspx_file_open_list[ptuId].writelines(written_str_list) 
              
            date_list =  [i.strip() for i in line_date.split(':')]
            time_list = [j.strip() for j in line_time.split(':')]
#             print date_list
#             print time_list    
             
            msg_content_len = int(msg_content[:4],16)
            msg_content_header = msg_content[:16]
            msg_content_body = msg_content[16:]
            if 2*msg_content_len > len(msg_content):
                msg_content_body += '0'*(2*msg_content_len-len(msg_content))
#             print msg_content_len
#             print msg_content_header
#             written_str_list = [line_no+', '+'/'.join(date_list)+','+':'.join(time_list)+', ']
#             result_dspx_file_open_list[ptuId].writelines(written_str_list)
            msg_name = ''
#             for search_item in pmuptu_intf_list:
#                 if msg_struct_name.lower() == search_item[0][struct_name_index].lower() or msg_struct_name.lower() == search_item[0][struct_name1_index].lower():
#                     msg_name = search_item[0][msg_name_index]
#                     break
            for search_item in pmuptu_intf_list:
                if msg_content_header[6:8] == search_item[0][msg_type_index]:
                    msg_name = search_item[0][msg_name_index]
                    break
            
            if msg_name == '':
                print 'can not find the struct name: '+msg_struct_name
                continue
            written_str_list = []
            written_str_list.append('-'*100+'\n')
            written_str = line_no+', '+'/'.join(date_list)+','+':'.join(time_list)+', '+msg_name+' ( '+msg_property+' )\n\n'
            written_str += 'header: '+msg_content_header+'\n\n'
            written_str_list.append(written_str)
            
            struct_index = 0
            if search_item[0][union_item_num_index] == 0:
                if search_item[0][struct_total_size_index] < msg_content_len - 8:
                    print msg_struct_name+':'
                    print 'msg length is not correct: struct length:'+str(search_item[0][struct_total_size_index])+' , trace msg length: '+str(msg_content_len)
                    continue
                else:
                    struct_index = 1
            else:
                for ii in range(int(search_item[0][union_item_num_index])):
                    if msg_content_len - 8 <= search_item[0][struct_total_size_index+ii*2]:
                        struct_index = 1+ii
                        break
                    else:
                        continue
            if struct_index == 0:
                print msg_struct_name+':'
                print 'msg length is not correct:  trace msg length: '+str(msg_content_len)
                continue
            written_str = ''
            i = 0
            for field_item in search_item[struct_index]:
#                 if i >= len(msg_content_body):
#                     written_str += field_item[1]+' :  '+'0'*field_item[2]*2+' '*10
#                 else:
#                     written_str += field_item[1]+' :  '+msg_content_body[i:i+field_item[2]*2]+' '*10
                if i >= len(msg_content_body):
                    break
                else:
#                    written_str += field_item[1]+' :  '+msg_content_body[i:i+field_item[2]*2]+' '*10
                    str_in_line = field_item[1]+' :  '+msg_content_body[i:i+field_item[2]*2]      # +' '*10
                    if len(written_str)+len(str_in_line) > 150:
                        written_str_list.append(written_str+'\n')
                        written_str= ''
                    written_str += str_in_line+' '*10

                    
                i += field_item[2]*2        # field size * 2
#                 if len(written_str) > 150:
#                     written_str_list.append(written_str+'\n')
#                     written_str= ''
            written_str_list.append(written_str+'\n')
            written_str_list.append('\n\n')
            written_str= ''
            result_dspx_file_open_list[ptuId].writelines(written_str_list)                
        elif 'dspAlarmInd' in line:
            line = line.strip('\n')
            line_list = line.split('|')
            line_no = line_list[0].strip()                  # record line number
            line_date = line_list[2].strip()                # record line date
            line_time = line_list[3].strip()                # record line time                   
            msg_header = line[line.find('dspAlarmInd'):]
            ptuId = int(msg_header.split()[1][4:])
            if ptuId > 3:
                print '!!!!!abnormal case: ptuId > 3, in line '+line_no+' in'+file_name
                continue
            written_str_list = []
            written_str_list.append('-'*100+'\n')
            written_str = line_no+', '+'/'.join(date_list)+','+':'.join(time_list)+', '+'DSP_ALARM_IND\n\n'
            written_str += msg_header + '\n\n'+ mfstrace_file.next().strip()[:-2]+'\n'+mfstrace_file.next().strip()+'\n'+mfstrace_file.next().strip()+'\n\n\n'
            written_str_list.append(written_str)
            written_str= ''
            result_dspx_file_open_list[ptuId].writelines(written_str_list)
                                    
#         else:
#             continue
                
    for li in result_dspx_file_open_list:
        li.close()
    
    
if __name__ == '__main__':
    
#     if len(argv) < 3:
#         print 'parameter number error, parameter list should be:'
#         print 'pmu-ptu interface directory, mfs_trace file'
#         exit()
#     pmuptu_intf_dir = argv[2]
#     mfs_trace_file = argv[1]
    pmuptu_intf_dir = r'pmuptu\\'
    mfs_trace_file = r'mfs_trace_p_3_53.old.03-17-13-00-31.txt'
#     print argv[0]
#     print argv[1]
#     print argv[2]

    pmuptu_basic = pmuptu_basic_struct(pmuptu_intf_dir + 'pmuptubasicstructure.h')
#    print_struct(pmuptu_basic.result)
    
    pmuptu_xdr = pmuptu_struct(pmuptu_intf_dir + 'xdrforsubsystem.h', pmuptu_basic.result)
    
    pmuptu_pm = pmuptu_struct(pmuptu_intf_dir + 'pmuptupmtypes.h', pmuptu_basic.result)    
    
    pmuptu_dsp = pmuptu_struct(pmuptu_intf_dir + 'pmuptudspmsginterface.h', pmuptu_basic.result+pmuptu_xdr.basic_struct+pmuptu_pm.basic_struct)
    
    pmuptu_gch = pmuptu_struct(pmuptu_intf_dir + 'pmuptugchmsginterface.h', pmuptu_basic.result)
    
    pmuptu_pdch = pmuptu_struct(pmuptu_intf_dir + 'pmuptupdchmsginterface.h', pmuptu_basic.result)
    
    pmuptu_tbf = pmuptu_struct(pmuptu_intf_dir + 'pmuptutbfmsginterface.h', pmuptu_basic.result)
#    print_struct(pmuptu_tbf.basic_struct)
#    print_struct(pmuptu_tbf.result)
    
    pmuptu_trx = pmuptu_struct(pmuptu_intf_dir + 'pmuptutrxmsginterface.h', pmuptu_basic.result+pmuptu_xdr.basic_struct+pmuptu_pm.basic_struct)
#     print_struct(pmuptu_trx.basic_struct)
#     print_struct(pmuptu_trx.result)
#     pprint(pmuptu_trx.basic_struct)
      
    pmuptu_intf_msg_list = pmuptu_dsp.result + pmuptu_gch.result + pmuptu_pdch.result + pmuptu_tbf.result + pmuptu_trx.result
    
    pmuptu_msg_type(pmuptu_intf_dir + 'pmuptumtypeinterface.h', pmuptu_intf_msg_list)
    write_to_file('pmuptubasicstructure.txt', pmuptu_basic.result)
    write_to_file('xdrforsubsystem.txt', pmuptu_xdr.basic_struct)
    write_to_file('pmuptupmtypes.txt', pmuptu_pm.basic_struct)
    write_to_file('pmuptudspmsginterface.txt', pmuptu_dsp.result)
    write_to_file('pmuptugchmsginterface.txt', pmuptu_gch.result)
    write_to_file('pmuptupdchmsginterface.txt', pmuptu_pdch.result)    
    write_to_file('pmuptutbfmsginterface.txt', pmuptu_tbf.result) 
    write_to_file('pmuptutrxmsginterface.txt', pmuptu_trx.result)
    
        
#    mfs_trace_analyser(r'mfs_trace_p_3_54.old.03-06-07-26-48.txt', pmuptu_intf_msg_list)
    mfs_trace_analyser(mfs_trace_file, pmuptu_intf_msg_list)
    
    