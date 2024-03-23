import grpc
from grpc_interceptor import ServerInterceptor
from group_communicator import Member 

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

        req = {"method": method_name, "args":request}
        self.member.send_request_msg( req)
        # x = self.group.await_execution()

        # if x == 200:
        return method(request, context)
        # else:
        # return self._terminator