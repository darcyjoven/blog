---
title: 'TIPTOP网络环境要求'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'tiptop-wang-luo-huan-jing-yao-qiu'
tags: ['tiptop', 'vpn', '网络']
description: '- VPN 和内部的网络访问只能是路由或是交换的方式，不能做 NAT - 客户端 telnet 到服务器后，在服务器端通过 echo $FGLSERVER 指令可以看到客户端 VPN 的 IP - 从服务器发起 ping / trace 到客户端 VPN 的 IP 可以正常访问 - 从服务器发起 telnet 客户端 VPN 的 IP 的 6400 端口可以'
draft: false
---

- VPN 和内部的网络访问只能是路由或是交换的方式，不能做 NAT
- 客户端 telnet 到服务器后，在服务器端通过 echo $FGLSERVER 指令可以看到客户端 VPN 的 IP
- 从服务器发起 ping / trace 到客户端 VPN 的 IP 可以正常访问
- 从服务器发起 telnet 客户端 VPN 的 IP 的 6400 端口可以正常访问
目前对客户端电脑的环境要求是 Windows xp，Windows 7、8 ，IE 版本 8 及以上，并且以管理员身份进入操作系统，其中 IE11 要设置兼容性设置，另外对于报表打印或者文档汇出，需要做如下设定：

- 设置 IE 为默认浏览器
- 把 ERP 网址和 CR 网址都加入到受信任站点，将受信任安全级别调到最低
- 如果无法弹出网页，请尝试关闭防火墙以及其他杀毒软件
