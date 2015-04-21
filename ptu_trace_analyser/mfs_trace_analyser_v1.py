# -*- coding: utf-8 -*-
'''
Created on 2015.3.25

@author: wadefu
'''
import sys, os
from pmuptu_intf_decode_v1 import *
from sys import argv

def print_log(log_file_reference, log_str, line):
    log_file_reference.writelines([log_str,'\n',line,'\n\n\n'])
#     print log_str
#     print line

def mfs_trace_analyser(file_name_dir, file_name_list, pmuptu_intf_list):
    
    decode_file_name = ''
    result_dspx_file_open_list = []
    error_index = 4
    log_index = 5   
    count = 0
    total_num = len(file_name_list)
    for file_name in file_name_list:
        file_path_name = file_name_dir + file_name
        
        if len(file_name_list) == 1:
            if file_name[-4:] == '.txt':
                decode_file_name = file_name[:-4]
            else:
                decode_file_name = file_name
#             print file_name_dir
#             print file_name_list
#             print decode_file_name
            for i in range(4):
                result_dspx_file_open_list.append(open(file_name_dir + decode_file_name +'_dsp'+str(i)+'.txt','w+'))
            result_dspx_file_open_list.append(open(file_name_dir + decode_file_name+'_error'+'.txt','w+')) 
            result_dspx_file_open_list.append(open(file_name_dir + decode_file_name+'_log'+'.txt','w+')) 
                
        elif file_name[:16] != decode_file_name:
            decode_file_name = file_name[:16]
            if len(result_dspx_file_open_list) >0:
                for li in result_dspx_file_open_list:
                    li.close()                
            result_dspx_file_open_list = []
            for i in range(4):
                result_dspx_file_open_list.append(open(file_name_dir + decode_file_name +'_dsp'+str(i)+'.txt','w+'))
            result_dspx_file_open_list.append(open(file_name_dir + decode_file_name+'_error'+'.txt','w+'))        
            result_dspx_file_open_list.append(open(file_name_dir + decode_file_name+'_log'+'.txt','w+'))        
                
        mfstrace_file = open(file_path_name, 'r')
        count += 1
    #    line = mfstrace_file.readline()
        if not mfstrace_file:
            log_str = '\n!!Error: can not find file: '+file_name+'\n'
            print log_str
            result_dspx_file_open_list[log_index].writelines([log_str,'\n'])
            mfstrace_file.close()
            continue
        
        log_str = '>>> Start decoding trace '+file_name+'\n'
#        print log_str
        print '>>> Start decoding trace '+file_name+', '+str(count)+'/'+str(total_num)+'\r',
#         for li in result_dspx_file_open_list:
#             li.writelines([log_str,'\n'])
        for result_index in range(5):
            result_dspx_file_open_list[result_index].writelines([log_str,'\n'])
            
        for line in mfstrace_file:
            if len(line) <= 2:
                continue
            if 'WARRING' in line:
                written_str_list = [line]
                line = mfstrace_file.next()
                while len(line) <=2:
                    line = mfstrace_file.next() 
                line_no = line.split('|')[0].strip()
                written_str_list.append('Next line no is: '+line_no+'\n\n')
#                li.writelines(written_str_list) 
                result_dspx_file_open_list[error_index].writelines(written_str_list) 
                                 
            if (('ptuId' in line or 'ptuid' in line) and ('incomingptumsgforwarderptu' in line or 'incomingptumsgforwardertbf' in line or 'incomingptumsgforwardertrx' in line \
            or 'incomingptumsgforwardertrans' in line or 'tdmptuproxy' in line or 'ipptuproxy' in line or 'dmrimpl' in line or 'dmrfortrximpl' in line \
            or 'dmrfortbfimpl' in line or 'dmrfordspimpl' in line or 'dmrforgchimpl' in line or 'ipptuchannelcontroler' in line)) or 'DSP Post-Mortem dump' in line:
                line = line.strip('| \n')
                line_list = line.split('|')
#                if 'ptuid' in line_list[-1]:
                    
                if len(line_list) != 5:
                    log_str = '!!ERROR: 1# can not decode this line in file: '+file_name
                    print_log(result_dspx_file_open_list[log_index], log_str, line)
                    continue
#                 if line_list[4].strip(' ')[:3] != 'Dbg':
#                     log_str = '!!ERROR: 2# can not decode this line in file: '+file_name
#                     result_dspx_file_open_list[log_index].writelines([log_str,'\n',line,'\n'])
#                     print log_str
#                     print line
#                     continue                    
                line_no = line_list[0].strip()                  # record line number
                line_date = line_list[2].strip()                # record line date
                line_time = line_list[3].strip()                # record line time
                line_list1 = line_list[4].split(':')
                if len(line_list1) < 6:
                    log_str = '!!ERROR: 3# can not decode this line in file: '+file_name
                    print_log(result_dspx_file_open_list[log_index], log_str, line)
                    continue
                    
                if 'DSP Post-Mortem dump' in line:
                    find_post_mortem = 1
                else:
                    find_post_mortem = 0
                if find_post_mortem == 0:
                    if not ('ptuid' in line_list1[-2] or 'ptuId' in line_list1[-2]):
                        log_str = '!!ERROR: 3# can not decode this line in file: '+file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue
                    line_list1[5] = line_list1[5].strip()
                    msg_right_index = line_list1[5].find('(')
                    if msg_right_index == -1:
                        log_str = '!!ERROR: 4# lack of "(" in line '+line_no+' in '+file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue
                    
                    msg_struct_name = line_list1[5][:msg_right_index]           # record msg struct name
                    msg_struct_index = line_list[4].find(msg_struct_name)
                    if msg_struct_index == -1:
                        log_str = '!!ERROR!!: 5# can not find the already decoded msg struct name'
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue
#                     if msg_struct_name[:7] == 'forward':
#                         msg_struct_name = msg_struct_name[7:]
                    msg_struct_content = line_list[4][msg_struct_index:]
        
                    msg_property_right_index = msg_struct_content.find(')')
                    if msg_property_right_index == -1:
                        log_str = '!!ERROR: 6# lack of ")" in line '+line_no+' in '+file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue
                    
                    msg_property = msg_struct_content[msg_right_index+1:msg_property_right_index]        #record some property of this msg like tbfIndex, trxIndex
                    if len(msg_property) > 70:
                        log_str = '!!ERROR: 7# length of msg_property is too long in line '+line_no+' in '+file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue                        
#                    ptuId_index = msg_struct_content.find('ptu', msg_property_right_index)
                    ptuid_in_str = line_list1[-2].strip()
                    ptuId_index = ptuid_in_str.find('ptu')
                    if ptuId_index == -1:
                        log_str = '!!ERROR: 8# lack of "ptuId" in line '+line_no+' in '+file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue

#                    ptuId = int(msg_struct_content[ptuId_index+6])       #record ptuId
                    if msg_struct_name == 'TrxSysDefineReq':
                        ptuId = int(ptuid_in_str[ptuId_index+6:-11])
                    else:
                        ptuId = int(ptuid_in_str[ptuId_index+6:])
                    if ptuId > 3:
                        log_str = '!!ERROR: 9# abnormal case: ptuId > 3, in line '+line_no+' in '+file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue
                    
                    msg_content = line_list1[-1].strip()    #record msg content
                    
                else:
                    msg_content = line_list1[-1].strip()
                    print msg_content
                    ptuId_index1 = line.find('after DSP') + len('after DSP ')
                    ptuId_index2 = line.find(' anomalyId')
                    ptuId = int(line[ptuId_index1:ptuId_index2])
                    print 'post-mortem ptuid:' + str(ptuId)
                    msg_struct_name = 'SA_DSP_ALARM_IND'    
                    msg_name ='DSP Post-Mortem dump'                       
                    
                
                temp_index = msg_content.find('[and')
                if temp_index != -1:
                    temp_content = msg_content[temp_index:]
                    temp_index1 = temp_content.find("'")
                    temp_num = int(temp_content[5:temp_index1-1])
    #                print '!!!!!![and '+str(temp_num)
                    temp_str = temp_content[temp_index1+1:-9]
                    msg_content = msg_content[:temp_index] + temp_str * temp_num
                  
                date_list =  [i.strip() for i in line_date.split(':')]
                time_list = [j.strip() for j in line_time.split(':')]
    
                   
                if find_post_mortem == 0: 
#                     if msg_struct_name == 'TrxSysDefineReq':
#                         msg_content = msg_struct_content[ptuId_index+10+11:].strip(' ')    #record msg content
#                         mfstrace_file.next()     # next line is only a \n
#                         line = mfstrace_file.next()     # next line includes the next part of TrxSysDefineReq
#                         if not 'TrxSysDefineReq' in line:
#                             print '###### can not find the next part of msg TrxSysDefineReq in file: '+file_name
#                             print 'in line: '+line_no
#                             print line
#                             continue
#                         else:
#                             msg_content += line.split(':')[-1].strip(' \n')
#                     else:
#                         msg_content = msg_struct_content[ptuId_index+10:].strip(' ')    #record msg content
                    
                    if msg_struct_name == 'TrxSysDefineReq':
                        line_next = mfstrace_file.next()     # next line is only a \n
                        if len(line_next) > 2:
                            log_str = '!!ERROR: 10# error of next line of TrxSysDefineReq in line '+line_no+' in '+file_name
                            print_log(result_dspx_file_open_list[log_index], log_str, line)
                            continue 
                        line_next = mfstrace_file.next()         # next line includes the next part of TrxSysDefineReq
                        if not 'TrxSysDefineReq' in line:
                            log_str = '!!ERROR: 11# can not find the next part of msg TrxSysDefineReq in line '+line_no+' in '+file_name
                            print_log(result_dspx_file_open_list[log_index], log_str, line)
                            msg_property += ' ) ( !!! lack of next part !!! '
#                            continue
                        else:
                            tmp_list = line_next.split(':')
                            if len(tmp_list) != 12:
                                log_str = '!!ERROR: 12# next part of msg TrxSysDefineReq is not correct in file '+file_name
                                print_log(result_dspx_file_open_list[log_index], log_str, line_next)
                                msg_property += ' ) ( !!! lack of next part !!! '
                            else:                                                                
                                msg_content += line.split(':')[-1].strip()                        
                    
                    msg_content_len = int(msg_content[:4],16)
                    msg_content_header = msg_content[:16]
                    msg_content_body = msg_content[16:]
#                     if 2*msg_content_len > len(msg_content):
#                         msg_content_body += '0'*(2*msg_content_len-len(msg_content))
                    msg_name = ''
                    for search_item in pmuptu_intf_list:
                        if msg_content_header[6:8] == search_item[0][msg_type_index]:
                            msg_name = search_item[0][msg_name_index]
                            break
                    if msg_name == '':
                        log_str = '!!ERROR: 13# can not find the struct name: '+msg_struct_name+' in line '+line_no+'in file '+file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue
                    
                    struct_index = 0
                    if search_item[0][union_item_num_index] == 0:
                        if search_item[0][struct_total_size_index] < msg_content_len - 8:
                            log_str = '!!ERROR: 14# msg length is not correct for struct: '+msg_struct_name+'\n'
                            log_str += 'struct length:'+str(search_item[0][struct_total_size_index])+' , trace msg length: '+str(msg_content_len)+'\n'
                            log_str += 'In file: ' + file_name
                            print_log(result_dspx_file_open_list[log_index], log_str, line)
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
                        log_str = '!!ERROR: 15# msg length is not correct for struct: '+msg_struct_name+'\n'
                        log_str += 'trace msg length: '+str(msg_content_len)
                        log_str += 'In file: ' + file_name
                        print_log(result_dspx_file_open_list[log_index], log_str, line)
                        continue
                    
                else:               #find_post_mortem = 1, it's post-mortem line
                    len_str = hex(len(msg_content)/2+2)[2:]
                    len_str = '0'*(4-len(len_str))+len_str
                    msg_content_body = len_str + msg_content
                    msg_content_header =''
                    msg_property = ''
                    struct_index = int(msg_content_body[39]) + 1
                    for search_item in pmuptu_intf_list:
                        if search_item[0][struct_name_index] == msg_struct_name:
                            break
    
                written_str_list = []
                written_str_list.append('-'*100+'\n')
                written_str = line_no+', '+'/'.join(date_list)+','+':'.join(time_list)+', '+msg_name+' ( '+msg_property+' )\n'
                written_str += 'header: '+msg_content_header+'\n'
                written_str += 'content: '+msg_content_body+'\n\n'
                written_str_list.append(written_str)
                
    
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
                    
                    log_str = '!!ERROR: 16# abnormal case in dspAlarmInd: ptuId > 3, in line '+line_no+' in '+file_name
                    print_log(result_dspx_file_open_list[log_index], log_str, line)                    
                    continue
                date_list =  [i.strip() for i in line_date.split(':')]
                time_list = [j.strip() for j in line_time.split(':')]
                written_str_list = []
                written_str_list.append('-'*100+'\n')
                written_str = line_no+', '+'/'.join(date_list)+','+':'.join(time_list)+', '+'DSP_ALARM_IND\n\n'
                written_str += msg_header + '\n\n'+ mfstrace_file.next().strip()[:-2]+'\n'+mfstrace_file.next().strip()+'\n'+mfstrace_file.next().strip()+'\n\n\n'
                written_str_list.append(written_str)
                written_str= ''
                result_dspx_file_open_list[ptuId].writelines(written_str_list)
                                        
        mfstrace_file.close()
#        print '<<< Finish decoding trace '+file_name
        log_str = '<<< Finish decoding trace '+file_name+'\n'
#        print log_str
#         for li in result_dspx_file_open_list:
#             li.writelines([log_str,'\n'])    
        for result_index in range(5):
            result_dspx_file_open_list[result_index].writelines([log_str,'\n'])
            
    for li in result_dspx_file_open_list:
        li.close()
    
    
if __name__ == '__main__':
    
#     if len(argv) < 3:
#         print 'parameter number error, parameter list should be:'
#         print 'pmu-ptu interface directory, mfs_trace file'
#         exit()
# 
#     mfs_trace_dir = argv[1]
#     pmuptu_intf_dir = argv[2]
#     print argv[0]
#     print argv[1]
#     print argv[2]
#     print
    print
    mfs_trace_dir = raw_input("Please input mfs trace file name or directory name:\n(E.g. D:\\trace\\1.txt or D:\\trace) \n")
    pmuptu_intf_dir = raw_input("Please input pmu-ptu interface files directory name:\n(E.g. D:\\trace\\pmuptu) \n")
    print
    print mfs_trace_dir
    print pmuptu_intf_dir
    if not (mfs_trace_dir and pmuptu_intf_dir):
        print 'Incorrect file name or directory name..'
        exit()
    if pmuptu_intf_dir[-1] != '\\':
        pmuptu_intf_dir += '\\'

    pmuptu_basic = pmuptu_basic_struct(pmuptu_intf_dir + 'pmuptubasicstructure.h')
    
    pmuptu_xdr = pmuptu_struct(pmuptu_intf_dir + 'xdrforsubsystem.h', pmuptu_basic.result)
    
    pmuptu_pm = pmuptu_struct(pmuptu_intf_dir + 'pmuptupmtypes.h', pmuptu_basic.result)    
    
    pmuptu_dsp = pmuptu_struct(pmuptu_intf_dir + 'pmuptudspmsginterface.h', pmuptu_basic.result+pmuptu_xdr.basic_struct+pmuptu_pm.basic_struct)
    
    pmuptu_gch = pmuptu_struct(pmuptu_intf_dir + 'pmuptugchmsginterface.h', pmuptu_basic.result)
    
    pmuptu_pdch = pmuptu_struct(pmuptu_intf_dir + 'pmuptupdchmsginterface.h', pmuptu_basic.result)
    
    pmuptu_tbf = pmuptu_struct(pmuptu_intf_dir + 'pmuptutbfmsginterface.h', pmuptu_basic.result)
    
    pmuptu_trx = pmuptu_struct(pmuptu_intf_dir + 'pmuptutrxmsginterface.h', pmuptu_basic.result+pmuptu_xdr.basic_struct+pmuptu_pm.basic_struct)

    pmuptu_gpu_dsp = pmuptu_gpu_dsp_struct(pmuptu_intf_dir + 'gpu_dspc.h', [])
    pmuptu_alarm = pmuptu_alarm_struct(pmuptu_intf_dir + 'dsp_dsp.h', pmuptu_dsp.result+pmuptu_gpu_dsp.result)
      
    pmuptu_intf_msg_list = pmuptu_dsp.result + pmuptu_gch.result + pmuptu_pdch.result + pmuptu_tbf.result + pmuptu_trx.result + pmuptu_alarm.result
    
    pmuptu_msg_type(pmuptu_intf_dir + 'pmuptumtypeinterface.h', pmuptu_intf_msg_list)
    
    write_to_file(pmuptu_intf_dir + 'pmuptubasicstructure.txt', pmuptu_basic.result)
    write_to_file(pmuptu_intf_dir + 'xdrforsubsystem.txt', pmuptu_xdr.basic_struct)
    write_to_file(pmuptu_intf_dir + 'pmuptupmtypes.txt', pmuptu_pm.basic_struct)
    write_to_file(pmuptu_intf_dir + 'pmuptudspmsginterface.txt', pmuptu_dsp.result)
    write_to_file(pmuptu_intf_dir + 'pmuptugchmsginterface.txt', pmuptu_gch.result)
    write_to_file(pmuptu_intf_dir + 'pmuptupdchmsginterface.txt', pmuptu_pdch.result)    
    write_to_file(pmuptu_intf_dir + 'pmuptutbfmsginterface.txt', pmuptu_tbf.result) 
    write_to_file(pmuptu_intf_dir + 'pmuptutrxmsginterface.txt', pmuptu_trx.result)
    write_to_file(pmuptu_intf_dir + 'gpu_dspc.txt', pmuptu_gpu_dsp.result)
    write_to_file(pmuptu_intf_dir + 'dsp_dsp.txt', pmuptu_alarm.result)

    print
        
    if os.path.isdir(mfs_trace_dir):
        print 'dir: '+mfs_trace_dir
            
        if mfs_trace_dir[-1] != '\\':
            mfs_trace_dir += '\\'
        
        mfs_trace_list = os.listdir(mfs_trace_dir)
        index = 0
        while index < len(mfs_trace_list):
            if os.path.isdir(mfs_trace_dir+mfs_trace_list[index]) or len(mfs_trace_list[index]) < 16 or mfs_trace_list[index][:12] != 'mfs_trace_p_' or 'dsp' in mfs_trace_list[index] or 'error' in mfs_trace_list[index] or 'log' in mfs_trace_list[index]:
                del mfs_trace_list[index]
                index -= 1
            index += 1
        mfs_trace_list.sort()
    else:
#         mfs_trace_list= [mfs_trace_dir]
#         mfs_trace_dir = ''  
        mfs_trace_dir, mfs_trace_file = os.path.split(mfs_trace_dir)
        mfs_trace_list= [mfs_trace_file]
        if mfs_trace_dir[-1] != '\\':
            mfs_trace_dir += '\\'

    print        
    print '###################################################'
    print
    print 'Totally '+str(len(mfs_trace_list))+' mfs_trace files to be decoded'
        
    mfs_trace_analyser(mfs_trace_dir, mfs_trace_list, pmuptu_intf_msg_list)
    print
    print '##################### DONE ########################'
    raw_input('Press enter to exit normally...')
    