import glob
import importlib
import os


class ImportUtil:
    @staticmethod
    def import_class_by_file_name(file_name: str):
        folder_path = os.path.dirname(file_name)
        base_name = str(os.path.basename(file_name))
        class_name: str = base_name.split(".")[0]
        module_name = class_name
        if folder_path != '':
            module_path = folder_path.replace("/", ".")
            module_name = "{0}.{1}".format(module_path, class_name)
        class_module = importlib.import_module(module_name)
        imported_class = getattr(class_module, class_name)
        return class_name, imported_class

    @staticmethod
    def import_classes_from_folder(folder_path: str):
        result = []
        if os.path.isdir(folder_path):
            file_names = [file_name for file_name in glob.glob(folder_path + "/*.py")]
            for file_name in file_names:
                class_name, imported_class = ImportUtil.import_class_by_file_name(file_name)
                result.append((class_name, imported_class))
        return result
