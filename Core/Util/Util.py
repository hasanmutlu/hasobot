import logging
import sys
import os
import subprocess
import shutil
import configparser
import threading


class Util:

    @staticmethod
    def get_abs_file_name(file_name):
        pathname = os.path.realpath(os.path.dirname(sys.argv[0]))
        return "{0}/{1}".format(pathname, file_name)

    @staticmethod
    def execute(command, stdin=None, env=None, cwd=None, shell=True, result=True):
        try:
            process = subprocess.Popen(command, stdin=stdin, env=env, cwd=cwd, stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE, shell=shell)

            if result is True:
                result_code = process.wait()
                p_out = process.stdout.read().decode("unicode_escape")
                p_err = process.stderr.read().decode("unicode_escape")
                return result_code, p_out, p_err
            else:
                return None, None, None
        except Exception as e:
            return 1, "Could not execute command: {0}. Error Message: {1}".format(command, str(e))

    @staticmethod
    def restart_program():
        os.execl(sys.executable, sys.executable, *sys.argv)

    @staticmethod
    def copytree(src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                Util.copytree(s, d, symlinks, ignore)
            else:
                if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                    shutil.copy2(s, d)

    @staticmethod
    def get_setting(name, section='general', cls=str, default=None):
        try:
            data = config[section][name]
            data = cls(data)
            return data
        except Exception as e:
            logging.error(f'Error:{e}')
            return default

    @staticmethod
    def save_settings():
        _lock.acquire()
        try:
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        finally:
            _lock.release()

    @staticmethod
    def set_setting(value, name, section='general'):
        config[section][name] = str(value)
        Util.save_settings()

    @staticmethod
    def capture_video(video_length):
        try:
            if os.path.isfile('out.avi'):
                os.remove('out.avi')
            command = f'ffmpeg -s 640x480 -t {video_length} -i /dev/video0 out.avi'
            process = subprocess.Popen(command, env=None, cwd=None, shell=True)
            result_code = process.wait()
            return str(result_code)
        except Exception as e:
            return 'Could not execute command!'


config = configparser.ConfigParser()
config.read(Util.get_abs_file_name('config.ini'))
_lock = threading.Lock()
