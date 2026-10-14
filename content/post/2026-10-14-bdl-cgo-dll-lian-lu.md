---
title: 'BDL-CGo-DLL链路'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'bdl-cgo-dll-lian-lu'
tags: ['bdl', 'cgo', 'dll', 'tiptop']
description: 'BDL 使用 golang 在用户电脑上操作 使用 golang 逻辑代码，实用 CGo 导出，并使用 cpp 编译位 dll 给 bdl 调用。 代码解析 Go 代码 - 和 CGO 导出 so 库一样，实现功能即可，导出 CGo 的函数名可以不用大写字母开头 go package main import "C" func main() {} //expo'
draft: false
---

> BDL 使用 golang 在用户电脑上操作

> 使用 golang 逻辑代码，实用 CGo 导出，并使用 cpp 编译位 dll 给 bdl 调用。

# 代码解析

## Go 代码

- 和 CGO 导出 so 库一样，实现功能即可，导出 CGo 的函数名可以不用大写字母开头
```go
package main

import "C"

func main() {}

//export versionGo
func versionGo() *C.char {
	return C.CString(baseVersion)
}
```

- 编译，因为导出的函数不仅一个文件，所以应该编译`.`全部 go 文件
```bash
go build -buildmode=c-shared -o cpp/frontbasego.dll .
```

## C++代码

### 申明文件`fronbase.h`

- EXPORT 是要导出`dll`使用的函数，参数和回传值都一致。
- EXPORT 上面是固定的
```cpp
#pragma once
struct frontEndInterface
{
	short (*getParamCount) ();
	short (*getReturnCount) ();
	void (*popInteger) (long&, short&);
	void (*pushInteger) (const long, short);
	void (*popString) (char*, short&, short&);
	void (*pushString) (const char*, short, short);
	void (*getFrontEndEnv) (const char*, char*, short&);
	void (*popWString) (wchar_t*, short&, short&);
	void (*pushWString) (const wchar_t*, short, short);
};
#ifdef WIN32
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT extern "C"
#endif
// 下面时你要实现的函数。
EXPORT void initialize();
EXPORT void finalize();
EXPORT int mysum(const frontEndInterface& fx);
// 软件版本
EXPORT int version(const frontEndInterface& fx);
// 获取文件修改日期
EXPORT int modDate(const frontEndInterface& fx);
```

### 逻辑代码`fronbase.cpp`

```cpp
extern "C"{
#include "frontbasego.h"
}
// 这里导入的是CGo导出的头文件
#include "frontbase.h"
// 申明文件
#include <stdio.h>
#include <string.h>

#define SZ 5000

void initialize() {
}
void finalize() {
}

// 获取base.dll版本
int version(const frontEndInterface& fci) {
    char* ver;
    ver = versionGo();
    fci.pushString(ver,strlen(ver),0);

    return 0;
}

// 文件最后修改日期
int modDate(const frontEndInterface& fci) {
    short isNull,len;
    char file[SZ];
    char* dat;

    if (fci.getParamCount()!=1){
        return -1;
    }
    fci.popString(file,len,isNull);

    if (!isNull){
        dat = modDateGo(file);
        // 相对路径的文件，要加上bin/去判断
        if (strlen(dat) <=5 ){
            // char* 不能直接赋值，用新变量
            char newfile[SZ];
            snprintf(newfile, sizeof(newfile), "bin/%s", file);
            dat = modDateGo(newfile);
        }
    }

    fci.pushString(dat,strlen(dat),0);

    return 0;
}

int main() {
    char* dat;
    char file[] = "frontbase.h";
    dat = modDateGo(file);
    printf(dat);
    return 0;
}
```

- 编译
```powershell
g++ -shared -o frontbase.dll frontbase.cpp -I. -L. -lfrontbasego
# frontbasego 是CGo导出的dll，需要和cpp文件放在同一个目录编译
g++ -o test.exe frontbase.cpp -I. -L. -lfrontbasego
# 这个命令是编译未一个exe执行文件，运行main函数
```

## 示例程序

frontbase.7z

# 使用

## 存放路径

![Pasted image 20260518104244.png](/images/1bce94bc-00.png)

将 CGo 和 C++编译的所有 dll 文件 gdc 的路径。

## BDL 调用

```sql
define res varchar(1000)
define str string

// 参数分别是 dll库名，函数名，参数，返回值
// 参数返回值，可以多个[p_p1,p_p2]传入
call ui.Interface.frontCall("frontbase","version",[],[res])

call ui.Interface.frontCall("frontbase","version",[],[str])
// 调用的时候，可以使用string或者
call ui.Interface.frontCall("frontbase","modDate",["frontbase.dll"],[str])
// 传入文件路径的时候，因为Go接受多种路径，所以"\\"和"/"分隔符都能接受
call ui.Interface.frontCall("frontbase","modDate",["D:/cache/table.json"],[str])

call ui.Interface.frontCall("frontbase","modDate",["D:\\cache\\table.json"],[str])
```

ℹ️

对于 dll 文件较多的情况，可以将 dll 放在一个文件夹中，这个时候 dll 库名，需要修改未相对路径

![Pasted image 20260518104252.png](/images/1bce94bc-01.png)

```sql
call ui.Interface.frontCall("base/frontbase","modDate",["D:\\cache\\table.json"],[str])
// 用相对路径写dll库名也是可以的
```
