from Core.IService import IService


class SampleService(IService):

    def __init__(self):
        super(SampleService, self).__init__(5)

    def initialize(self):
        print("Sample Service is initialized!")

    def run_service(self):
        print("Sample Service is running!")
