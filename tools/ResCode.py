#!/usr/bin/env python
# -*- coding:utf-8 -*-

class ErrorCode:
    '''
    param: SUCCESS = 0
    param: ErrREQUEST = 1       #400 Bad Request,传参格式错误或缺少必填参数
    param: ErrPERMIT = 2        #权限不足
    param: ErrPARAM = 3         #传参内容不正确
    param: ErrOPERATE = 4       #非法操作
    param: ErrDATA = 5          #内部数据错误    
    '''
    SUCCESS = 0
    ErrREQUEST = 1       #400 Bad Request,传参格式错误或缺少必填参数
    ErrPERMIT = 2        #权限不足
    ErrPARAM = 3         #传参内容不正确
    ErrOPERATE = 4       #非法操作
    ErrDATA = 5          #内部数据错误

    msg = {
        SUCCESS: "SUCCESS ",
        ErrREQUEST: "REQUEST PARAM ERROR: ",
        ErrPERMIT: "INSUFFICIENT PERMISSION: ",
        ErrPARAM: "PARAM CONTENT ERROR: ",
        ErrOPERATE: "OPERATE ERROR: ",
        ErrDATA: "INTERNAL ERROR "
    }