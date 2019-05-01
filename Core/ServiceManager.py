from typing import Optional
from Core.IService import IService
from Core.Util.ImportUtil import ImportUtil


class ServiceManager:
    __service_list__ = []

    @staticmethod
    def load_services():
        ServiceManager.__service_list__.clear();
        services_folder_path = "Files/Services"
        imported_classes = ImportUtil.import_classes_from_folder(services_folder_path)
        for class_ in imported_classes:
            service_thread = class_[1]()
            ServiceManager.__service_list__.append({"name": class_[0], "thread": service_thread})

    @staticmethod
    def start_services():
        for service in ServiceManager.__service_list__:
            service["thread"].start()

    @staticmethod
    def stop_services():
        for service in ServiceManager.__service_list__:
            service["thread"].stop()

    @staticmethod
    def get_service_by_name(service_name: str) -> Optional[IService]:
        threads_found = [thread for thread in ServiceManager.__service_list__ if thread["name"] == service_name]
        if len(threads_found) > 0:
            return threads_found[0]["thread"]
        else:
            return None

    @staticmethod
    def start_service_by_name(service_name: str):
        service_thread = ServiceManager.get_service_by_name(service_name)
        if service_thread is not None:
            if service_thread.is_alive() is False:
                service_thread.start()

    @staticmethod
    def stop_service_by_name(service_name: str):
        service_thread = ServiceManager.get_service_by_name(service_name)
        if service_thread is not None:
            if service_thread.is_alive():
                service_thread.stop()
                service_thread.join()
