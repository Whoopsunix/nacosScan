import requests
import urllib3
from requests.adapters import HTTPAdapter

# 关闭ssl警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class common:
    """
    通用方法
    """

    def __init__(self):
        self.urls = set()

    def login_get_accesstoken(self, url, username, password):
        accesstoken = None
        userinfo = {
            "username": username,
            "password": password
        }
        headers = {"User-Agent": "Nacos-Server", "Content-Type": "application/x-www-form-urlencoded"}

        try:
            configurl = url + "v1/auth/users/login"
            response = requests.post(configurl, headers=headers, data=userinfo, timeout=10, verify=False)
            result_json = response.json()
            Print(result_json).star()
            accesstoken = result_json["accessToken"]
        except Exception as e:
            pass
        return accesstoken

    def urls_format(self, uf):
        for url in uf.readlines():
            try:
                url = url.strip()
                newurl = self.url_format(url)
                if newurl != None:
                    self.urls.add(newurl)
            except Exception as e:
                pass
        return self.urls

    def url_format(self, url):
        """
        url 格式化
        预先解析重定向 防止漏报
        :return:
        """
        final_url = None
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            max_redirects = 3
            session = requests.Session()
            adapter = HTTPAdapter(max_retries=max_redirects)

            session.mount("http://", adapter)
            session.mount("https://", adapter)

            # response = session.get(url, proxies=proxy)
            response = session.get(url, verify=False)
            if response.url != "":
                final_url = response.url
                if not final_url.endswith("/"):
                    final_url = final_url + "/"
        except Exception as e:
            pass
        finally:
            return final_url


class Print:
    def __init__(self, msg):
        self.msg = msg

    def print(self):
        '''
            无改动输出
        :param msg:
        :return:
        '''
        print(self.msg)

    def debug(self, flag):
        if flag:
            print("{}".format(self.msg))

    def info(self):
        '''
            侧重于代码中写死的输出
        :param msg:
        :return:
        '''
        print("\033[32;1m[+] {} [+]\033[0m".format(self.msg))

    def log(self):
        '''
            运行结果的实时输出
        :param msg:
        :return:
        '''
        print("[-] {} [-]".format(self.msg))

    def err(self):
        '''
            异常输出
        :param msg:
        :return:
        '''
        print("\033[31;1m[!] {} [!]\033[0m".format(self.msg))

    def star(self):
        '''
            重要输出
        :param msg:
        :return:
        '''
        print("\033[33;1m[*] {} [*]\033[0m".format(self.msg))

    '''
        开发配置
    '''

    def dev(self):
        flag = True
        if flag:
            print("[dev] {}".format(self.msg))
