
import sys
import traceback

from logger.custom_logger import CustomLogger

c_logger = CustomLogger()
logger = c_logger.get_custom_logger("exception_logger")

class DocumentPortalException(Exception):
    def __init__(self, ex_error, ex_details:sys):
        _,_,ex_tb = ex_details.exc_info()
        self.file_name = ex_tb.tb_frame.f_code.co_filename
        self.line_no = ex_tb.tb_lineno    
        self.error_name = str(ex_error)
        self.exp_traceback = "".join(traceback.format_exception(*ex_details.exc_info()))

    def __str__(self):
        return f"{self.file_name} {self.line_no} {self.error_name} {self.exp_traceback  }"

