#coding:utf-8

import os
import sys
import time
import atexit

__all__ = ["log", ]

class LogError(Exception):
    pass

class log(object):
    """日志"""
    fname = None
    path = None
    full = None
    file_handler = None

    # 一些特殊的目录，用于建立操作目录

    @classmethod
    def INIT(cls, **kw):
        """初始化日志句柄
        fname: 日志的文件名头
        path: 日志的存储路径"""
        if "fname" in kw and "/" not in kw["fname"]:
            cls.fname = kw["fname"]
        else:
            # 默认用进程的名称作为日志的名称头
            cls.fname = os.path.basename(sys.argv[0])
        if "path" in kw:
            tmp_p = os.path.abspath(kw["path"])
        else:
            tmp_p = os.getcwd()
        if os.path.exists(tmp_p) and os.access(tmp_p, os.R_OK | os.W_OK):
            cls.path = tmp_p
        elif os.path.exists(tmp_p + "/log") and os.access(tmp_p + "/log", os.R_OK | os.W_OK):
            cls.path = tmp_p + "/log"
        else:
            raise LogError("日志路径不存在或无读写权限")
        cls.full = cls.path + "/" + cls.fname + ".log"
        if os.path.exists(cls.full):
            ctime = time.localtime()
            postfix = "{0}{1:02d}{2:02d}{3:02d}{4:02d}{5:02d}".format(ctime.tm_year, ctime.tm_mon, ctime.tm_mday, ctime.tm_hour, ctime.tm_min, ctime.tm_sec)
            os.rename(cls.full, cls.full + "." + postfix)
        try:
            cls.file_handler = open(cls.full, "wb+", buffering=0)
        except IOError:
            raise LogError("无法创建日志文件，权限不足")
        except Exception as e:
            raise LogError(e)
        try:
            atexit(close_file, cls.file_handler)
        except Exception as e:
            pass

    @staticmethod
    def close_file(f):
        try:
            f.close()
        except Exception(e):
            raise LogError("日志文件未能正确关闭", e)

    @classmethod
    def INFO(cls, *arg):
        if cls.file_handler == None:
            cls.INIT()
        header = None
        if len(arg) > 1:
            header = str(arg[0])
            msg = " ".join(map(str, arg[1:]))
        else:
            msg = str(arg[0])
        ctime = time.localtime()
        m = "[INFO][{0}-{1}-{2}][{3}:{4}:{5}]".format(ctime.tm_year, ctime.tm_mon, ctime.tm_mday, ctime.tm_hour, ctime.tm_min, ctime.tm_sec)
        if header != None:
            m += " [{0}]".format(header)
        m += " {0}\n".format(msg)
        cls.file_handler.write(bytes(m.encode("utf-8")))

    @staticmethod
    def get_frame_info():
        try:
            raise Exception
        except Exception as e:
            f = sys.exc_info()[2].tb_frame.f_back.f_back
            return f.f_code.co_filename, f.f_code.co_name, f.f_lineno

    @classmethod
    def DEBUG(cls, *arg):
        fname, funname, lineno = cls.get_frame_info()
        if cls.file_handler == None:
            cls.INIT()
        header = None
        if len(arg) > 1:
            header = str(arg[0])
            msg = " ".join(map(str, arg[1:]))
        else:
            msg = str(arg[0])
        ctime = time.localtime()
        m = "[DEBUG][{0}-{1}-{2}][{3}:{4}:{5}][{6}][{7}][{8}]".format(ctime.tm_year, ctime.tm_mon, ctime.tm_mday, ctime.tm_hour, ctime.tm_min, ctime.tm_sec, fname, funname, lineno)
        if header != None:
            m += " [{0}]".format(header)
        m += " {0}\n".format(msg)
        cls.file_handler.write(bytes(m.encode("utf-8")))
