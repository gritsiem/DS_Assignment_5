import grpc
from grpc_interceptor import ServerInterceptor
from group_communicator import Member 

class Request:
    def __init__(self, method_name:str, args: dict) -> None:
        self.method = method_name
        self.args = args
class OrderInterceptor(ServerInterceptor):
    def __init__(self,addr, pid):
        print(addr,pid)
        self.member = Member(addr, pid)

    def intercept(
            self,
            method,
            request,
            context,
            method_name):
        
        if method_name.find("GetUserDB")!=-1:
            return method(request, context)

        req = Request(method_name, request)
        lsn = self.member.send_request_msg( req)
        # self.group.await_execution(lsn)

        # if x == 200:
        return method(request, context)
        # else:
        # return self._terminator