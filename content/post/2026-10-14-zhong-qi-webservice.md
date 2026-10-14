---
title: '重启webservice'
date: 2026-10-14
lastmod: 2026-10-14T03:27:00.000Z
slug: 'zhong-qi-webservice'
tags: ['tiptop', 'webservice']
description: 'TIPTOP100 shell systemctl restart httpd.service systemctl restart gas_topprd.service systemctl restart gas_topprd_ws.service systemctl restart gas_toptst.service systemctl restart'
draft: false
---

## TIPTOP100

```bash
systemctl restart httpd.service
systemctl restart gas_topprd.service
systemctl restart gas_topprd_ws.service
systemctl restart gas_toptst.service
systemctl restart gas_topstd.service
systemctl restart gas_toppth.service
```

## TIPTOP GP

- `startws`
- root 登录 `service httpd restart` T100 也可以这么重启(理论)
