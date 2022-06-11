import os
import os.path as path
import platform
import shutil

from io import BytesIO
from typing import Callable, Tuple

import rarfile
import zipfile
import pyzipper
import PyPDF2

import msoffcrypto as ms
from msoffcrypto import exceptions as msexcept


# Global Variables
PASSED_DIR_NAME = "success"
FAILED_DIR_NAME = "failed"

if os.system("whereis unrar") != 0:
    if platform.system() in ['Darwin']:
        rarfile.UNRAR_TOOL = "./unrar"
    elif platform.system() in ['Windows', 'windows', 'win32']:
        rarfile.UNRAR_TOOL = "./UnRAR.exe"
    else:
        print("There is no suitable unrar tool in system!")
        exit(1)


def getPasswordList(filename: str) -> list:
    """
    获取密码列表, 密码文件为一个文本文件, 每行为一个密码(不含换行)

    Args:
        filename (str): 存放密码的文件路径

    Returns:
        list: 密码列表, 元素为字符串
    """
    with open(filename, "r", encoding="utf-8") as f:
        res = f.readlines()
    return [x.strip() for x in res]


def allpassSame(passlist: str) -> bool:
    """
    判断一个列表中的密码是否完全相同

    Args:
        passlist (str): 密码列表

    Returns:
        bool: 是否完全相同
    """
    if len(passlist) == 0:
        return True

    res = True
    ref = passlist[0]
    for x in passlist[1:]:
        res = res and (ref == x)
    return res


def makeTempDir(prefix: str) -> Tuple[bool, str, str]:
    # 将 PASSED_DIR_NAME, FAILED_DIR_NAME 重新定义为有前缀的格式
    passed_dir = path.join(prefix, PASSED_DIR_NAME)
    failed_dir = path.join(prefix, FAILED_DIR_NAME)
    try:
        os.mkdir(passed_dir)
        os.mkdir(failed_dir)
        return True, passed_dir, failed_dir
    except FileExistsError:
        return False, passed_dir, failed_dir


def func_office(file: str, passwords: list, tar_dir: str) -> bool:
    """
    处理 office 文件

    对 office 文件的处理依赖于包 msoffcrypto, 参照代码:
        https://github.com/nolze/msoffcrypto-tool/blob/master/msoffcrypto/__main__.py

    在本函数中, 如果发现密码正确则会直接将文件写入到 tar_dir 中. 

    Args:
        file (str): 文件路径
        passwords (list): 密码列表

    Returns:
        bool: 是否成功被密码本破译打开
    """
    fname = path.basename(file)
    fin = open(file, "rb")
    try:
        officeF = ms.OfficeFile(fin)
    except Exception as e:
        # 如果打开失败, 可能是没有加密或者不支持的格式, 提供一个警告
        print(f"警告: 文件 \"{fname}\" 可能未加密或不支持此格式")
        shutil.copy(file, os.path.join(tar_dir, fname))
        fin.close()
        return False
        
    usdpwd = ""
    if officeF.is_encrypted():
        passed = False
        for pwd in passwords:
            try:
                officeF.load_key(pwd)
                # 如果密码本中存在正确的密码, 那么置passed为True并退出循环
                bio = BytesIO()
                officeF.decrypt(bio)
                bio.close()
                passed = True
                usdpwd = pwd
                break
            except msexcept.InvalidKeyError:
                continue
    else:
        # 如果文件没有加密, 则置passed为True
        passed = True
    
    # 如果通过检测, 那么将文件转存到文件夹中
    if passed:
        print(fname, usdpwd)
        with open(path.join(tar_dir, fname), "wb") as f:
            officeF.decrypt(f)

    fin.close()
    return passed


class ArchiveInterface:
    def __init__(self, filename: str, wrapper: Callable = None):
        self.filename = filename
        _, self.ext = path.splitext(filename)
        if wrapper is not None:
            self.obj = wrapper(filename)
        elif self.ext in [".zip", ".ZIP"]:
                self.obj = zipfile.ZipFile(filename)
        elif self.ext in [".rar", ".RAR"]:
            self.obj = rarfile.RarFile(filename)
        else:
            raise ValueError("Not supported ext-type for auto-inferring")
    
    def infolist(self):
        return self.obj.infolist()
    
    def iszip(self) -> bool:
        return self.ext in [".zip", ".ZIP"]

    def israr(self) -> bool:
        return self.ext in [".rar", ".RAR"]

    def isEncrypted(self, x):
        if self.iszip():
            return x.flag_bits & 0x1
        elif self.israr():
            return x.needs_password()
        else:
            return True

    def open(self, x, pwd: str=None):
        if self.iszip():
            pwd = None if pwd is None else str.encode(pwd)
        if self.israr():
            return self.obj.read(x, pwd=pwd)
        
        return self.obj.open(x, pwd=pwd)

    def extract(self, x, pwd: str=None, path: str=None):
        if self.iszip():
            pwd = None if pwd is None else str.encode(pwd)
        
        return self.obj.extract(x, pwd=pwd, path=path)

    def close(self):
        self.obj.close()


def func_archive(fileIntface: ArchiveInterface, passwords: list, tar_dir: str, auto: bool = False) -> bool:
    """
    处理 归档 文件

    Args:
        file (ArchiveInterface): 归档文件接口对象
        passwords (list): 密码列表
        tar_dir (str): 目标文件夹目录

    Returns:
        bool: 是否成功被密码本破译打开
    """
    fname = os.path.basename(fileIntface.filename)

    if auto:
        try:
            os.mkdir(path.join(tar_dir, fname))
        except:
            pass
    
    # 初始化内部文件的密码对照
    password_note = ""
    passlist = []

    # 是否能够破解所有文件的密码的两个计数器
    all_file = 0
    pas_file = 0

    for zinfo in fileIntface.infolist():
        # 遍历归档文件中的所有文件进行操作
        is_encrypted = fileIntface.isEncrypted(zinfo)
        true_pass = None
        if is_encrypted:
            passed = False
            for pwd in passwords:
                try:
                    if auto:
                        fileIntface.extract(
                            zinfo, 
                            pwd=pwd, 
                            path=path.join(tar_dir, fname)
                        )
                    else:
                        fileIntface.open(
                            zinfo, 
                            pwd=pwd
                        )
                    true_pass = pwd
                    passed = True
                    break
                except Exception as e:
                    # print(e)
                    continue
        else:
            if auto:
                fileIntface.extract(
                    zinfo, 
                    path=path.join(tar_dir, fname)
                )
            passed = True
        
        # 为 password_note 添加条目
        password_note += f"{zinfo.filename}\t{true_pass}\n"
        passlist.append(true_pass)
        # 更新计数器
        all_file += 1
        if passed:
            pas_file += 1

    # 判断提取结果
    if auto:
        if pas_file == 0:
            shutil.rmtree(path.join(tar_dir, fname))
        elif pas_file != all_file:
            os.renames(path.join(tar_dir, fname), path.join(tar_dir, fname) + "_part")
    else:
        if pas_file != 0:
            # 如果存在文件密码正确: 复制压缩包到目标路径, 添加密码本
            shutil.copy(fileIntface.filename, os.path.join(tar_dir, fname))
            need_note = True
            if len(passlist) > 0 and allpassSame(passlist):
                if passlist[0] is None:
                    # 不需要密码, 那么后边不建立密码本
                    fin_pass = ""
                    need_note = False
                else:
                    fin_pass = passlist[0]
                    password_note = f"压缩包密码\t{fin_pass}\n\n" + password_note

            if need_note:
                with open(os.path.join(tar_dir, fname + "_pass.txt"), "w", encoding="utf-8") as f:
                    f.write(password_note)
    
    fileIntface.close()
    # 返回是否完全正确
    return pas_file == all_file


def func_zip_auto(file: str, passwords: list, tar_dir: str) -> bool:
    """
    处理 zip 文件
        会自动解压文件

    Args:
        file (str): 文件路径
        passwords (list): 密码列表
        tar_dir (str): 目标文件夹路径

    Returns:
        bool: 是否成功被密码本破译打开
    """
    return (
        func_archive(ArchiveInterface(file, zipfile.ZipFile), passwords, tar_dir, True) or
        func_archive(ArchiveInterface(file, pyzipper.AESZipFile), passwords, tar_dir, True)
    )


def func_zip(file: str, passwords: list, tar_dir: str) -> bool:
    """
    处理 zip 文件

    Args:
        file (str): 文件路径
        passwords (list): 密码列表
        tar_dir (str): 目标文件夹

    Returns:
        bool: 是否成功被密码本破译打开
    """
    return (
        func_archive(ArchiveInterface(file, zipfile.ZipFile), passwords, tar_dir) or 
        func_archive(ArchiveInterface(file, pyzipper.AESZipFile), passwords, tar_dir)
    )


def func_rar_auto(file: str, passwords: list, tar_dir: str) -> bool:
    """
    处理 rar 文件
        会自动解压文件
    
    Args:
        file (str): 文件路径
        passwords (list): 密码列表
        tar_dir (str): 目标文件夹路径

    Returns:
        bool: 是否成功被密码本破译打开
    """
    return func_archive(ArchiveInterface(file), passwords, tar_dir, True)


def func_rar(file: str, passwords: list, tar_dir: str) -> bool:
    """
    处理 rar 文件

    Args:
        file (str): 文件路径
        passwords (list): 密码列表
        tar_dir (str): 目标文件夹路径

    Returns:
        bool: 是否成功被密码本破译打开
    """
    return func_archive(ArchiveInterface(file), passwords, tar_dir)

        
def func_pdf(file: str, passwords: list, tar_dir: str) -> bool:
    """
    处理 pdf 文件

    Args:
        file (str): 文件路径
        passwords (list): 密码列表
        tar_dir (str): 目标文件夹目录

    Returns:
        bool: 是否成功被密码本破译打开
    """
    reader = PyPDF2.PdfFileReader(file)
    fname = os.path.basename(file)
    if reader.isEncrypted:
        passed = False
        for pwd in passwords:
            try:
                reader.decrypt(file, pwd=pwd)
                passed = True
                break
            except :
                continue
    else:
        # 如果文件没有加密, 则置passed为True
        passed = True

        # 如果通过检测, 那么将文件转存到文件夹中
    if passed:
        write_pdf = PyPDF2.PdfFileWriter()
        write_pdf.appendPagesFromReader(reader)
        with open(path.join(tar_dir, fname), "wb") as f:
            write_pdf.write(f)

    return passed


detector = {
    ".zip": func_zip,
    ".docx": func_office,
    ".pdf": func_pdf,
    ".pptx": func_office,
    ".xls": func_office,
    ".xlsx": func_office,
    ".rar": func_rar
}


def each_file(filepath, new_filepath, passwords):
    '''
    读取每个文件夹，将遇到的指定文件统统转移到指定目录中
    :param filepath: 想要获取的文件的目录
    :param new_filepath: 想要转移的指定目录
    :return:
    '''
    l_dir = os.listdir(filepath)  # 读取目录下的文件或文件夹
    failed_files = []

    ok, passed, failed = makeTempDir(new_filepath)

    if not ok:
        print("已存在success/failed文件夹, 其中文件可能被覆盖")
        # print("自动创建文件夹失败, 检查存放文件目录是否正确")
        # exit(0)
        pass

    for one_dir in l_dir:  # 进行循环
        full_path = os.path.join(filepath, one_dir)  # 构造路径
        new_full_path = os.path.join(failed, one_dir)
        if os.path.isfile(full_path):  
            # 如果是文件类型就执行转移操作

            # 根据扩展名选择合适的函数进行处理
            spl = os.path.splitext(full_path)[1]

            if not (spl in detector and detector[spl](full_path, passwords, passed)):
                # 如果打开失败, 则将文件复制到失败路径中
                failed_files.append(one_dir)
                shutil.copy(full_path, new_full_path)

        else:  
            # 不为文件类型就继续递归
            # 如果是文件夹类型就有可能下面还有文件，要继续递归
            res = each_file(full_path, new_filepath, passwords)
            failed_files.extend([f"{one_dir}/{x}" for x in res])
    
    return failed_files


if __name__ == '__main__':
    # pwd_path = input("输入密码库：")
    # old_path = input("输入要提取的文件目录:")
    # new_path = input("输入要存放的文件目录:")
    pwd_path = "./测试1/密码.txt" # "/Users/leonard/Documents/Projects/Temp/enfiles/测试1/密码.txt"
    old_path = "./测试1/" # "/Users/leonard/Documents/Projects/Temp/enfiles/测试1/"
    new_path = "./结果/" # "/Users/leonard/Documents/Projects/Temp/enfiles/2/"
    

    passwords = getPasswordList(pwd_path)

    failed_files = each_file(old_path, new_path, passwords)
    print("\n失败文件列表:")
    for x in failed_files:
        print("\t", x)

    _ = input("input anything to end")


