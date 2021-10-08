import datetime
import os
import traceback


def create_exception_log_message(exc_type, exc_tb, ex):
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    error = '[' + str(datetime.datetime.now()) + ']'
    error += "[Error value: type: " + str(exc_type) + "; file name: " + str(fname) + "; line: " + str(

        exc_tb.tb_lineno) + '; value: ' + str(ex) + "]"
    error += "\n" + traceback.format_exc() + "\n"
    return error