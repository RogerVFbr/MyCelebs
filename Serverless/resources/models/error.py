class Error:

    def __init__(self, aws_log: str, msg_dev: str, msg_user: str, status_code: int, response_code: int):
        self.aws_log = aws_log
        self.msg_dev = msg_dev
        self.msg_user = msg_user
        self.status_code = status_code
        self.response_code = response_code

