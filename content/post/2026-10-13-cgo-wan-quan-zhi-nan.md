---
title: 'CGo完全指南'
date: 2026-10-13
lastmod: 2026-10-13T09:17:00.000Z
slug: 'cgo-wan-quan-zhi-nan'
tags: ['bdl', 'cgo', 'gcc', 'golang', 'tiptop']
description: 'CGo完全指南 本文由以下 4 篇合并而成： 1. cgo使用报告（主体，含完整示例） 2. TIPTOP GP 设置 CGo 环境 3. Redhat 6.5 GCC 升级到 4.8 4. BDL 调用 golang(cgo) 简单示例 --- 第一部分：CGo 使用报告 环境要求 gcc 版本 ≥4.7.1 示例 最简单 Cgo Go 中调用 C 语言的'
draft: false
---

> 本文由以下 4 篇合并而成：
>
> 1. cgo使用报告（主体，含完整示例）
> 2. TIPTOP GP 设置 CGo 环境
> 3. Redhat 6.5 GCC 升级到 4.8
> 4. BDL 调用 golang(cgo) 简单示例

---

## 第一部分：CGo 使用报告

# 环境要求

gcc 版本 ≥4.7.1

# 示例

## 最简单 Cgo

Go 中调用 C 语言的`println`函数

`import ”C”` 表示启用 CGo

```go
import "C"

func main() {
	println("hello cgo")
}
```

## 导入头文件

`import “C”` 与 C 代码之间无空行

```go
// #include <stdio.h>
import "C"

func main() {
	C.puts(C.CString("你好, GopherChina 2018!\n"))
}
```

## 调用自定义函数

```go
/*
#include <stdio.h>

static void SayHello(const char* s) {
    puts(s);
}
*/
import "C"

func main() {
	C.SayHello(C.CString("Hello, World\n"))
}
```

## 重写 C 模块

```go
// #include "hello.h"
import "C"
import "fmt"

//export SayHello
func SayHello(s *C.char) {
	fmt.Print(C.GoString(s))
}
func main() {
	C.SayHello(C.CString("ok"))
}
```

## Go 面向 C 开放接口

```go
// extern void SayHello(char* s);
import "C"
import "fmt"

func main() {
	C.SayHello(C.CString("Hello, World\n"))
}

//export SayHello
func SayHello(s *C.char) {
	fmt.Print(C.GoString(s))
}
```

## 使用*GoString*代替 char\*

```go
// extern void SayHello(_GoString_ s);
import "C"
import "fmt"

func main() {
	C.SayHello("Hello, World\n")
}

//export SayHello
func SayHello(s string) {
	fmt.Print(s)
}
```

## Go 调用 C 函数

1. 无返回值调用
```go
/*
static int add(int a, int b) {
    return a+b;
}
*/
import "C"

func main() {
    C.add(1, 1)
}
```

1. C 函数可以有两个返回值，第二个返回值为错误代码
```go
/*
static int add(int a, int b) {
    return a+b;
}
*/
import "C"
import "fmt"

func main() {
    v, err := C.add(1, 1)
		// _, err := C.add(1, 1)
		// v, _ := C.add(1, 1)
    fmt.Println(v, err)

    // Output:
    // 4 <nil>
}
```

## 导出 Go 函数

```go
import "C"

//export GoAdd
func GoAdd(a, b C.int) C.int {
    return a+b
}
// 可以导出私有函数
```

```c
// add.h
int c_add(int a, int b);

// add.c
#include "add.h"
#include "_cgo_export.h"

int c_add(int a, int b) {
    return GoAdd(a, b)
}
```

1. **\_GoString\_ 类型导出**
```go
// +build go1.10

// extern void SayHello(_GoString_ s);
import "C"

//export SayHello
func SayHello(s string) {
    fmt.Print(s)
}
```

## Go 中调用 C 的 qsort 函数

```go
/*
#include <stdlib.h>

#define DIM(x) (sizeof(x)/sizeof((x)[0]))

static int compare(const void* a, const void* b) {
    return ( *(int*)a - *(int*)b );
}

static void qsort_proxy(int* values, size_t len, size_t elemsize) {
    qsort(values, len, sizeof(values[0]), compare);
}
*/
import "C"
import "unsafe"
import "fmt"

func main() {
    values := []int32{ 42, 9, 101, 95, 27, 25 };
    C.qsort_proxy(
        (*C.int)(unsafe.Pointer(&values[0])),
        C.size_t(len(values)),
        C.size_t(unsafe.Sizeof(values[0])),
    )
    fmt.Println(values)
}
```

### 在以上基础上比较函数替换为 Go 的函数

```go
/*
#include <stdlib.h>

#define DIM(x) (sizeof(x)/sizeof((x)[0]))

extern int go_qsort_compare(void* a, void* b);

static int compare(const void* a, const void* b) {
    return go_qsort_compare((void*)(a), (void*)(b));
}
static void qsort_proxy(int* values, size_t len, size_t elemsize) {
    qsort(values, len, sizeof(values[0]), compare);
}
*/
import "C"
import "unsafe"
import "fmt"

//export go_qsort_compare
func go_qsort_compare(a, b unsafe.Pointer) C.int {
	pa := (*C.int)(a)
	pb := (*C.int)(b)
	return C.int(*pa - *pb)
}

func main() {
	values := []int32{42, 9, 101, 95, 27, 25}
	C.qsort_proxy(
		(*C.int)(unsafe.Pointer(&values[0])),
		C.size_t(len(values)),
		C.size_t(unsafe.Sizeof(values[0])),
	)
	fmt.Println(values)
}
```

### Go 函数作为参数传入，需要函数类型转换

```go
/*
#include <stdlib.h>

typedef int (*qsort_cmp_func_t)(const void* a, const void* b);
extern int go_qsort_compare(void* a, void* b);
*/
import "C"
import (
	"fmt"
	"unsafe"
)

func main() {
	values := []int32{42, 9, 101, 95, 27, 25}

	C.qsort(unsafe.Pointer(&values[0]),
		C.size_t(len(values)), C.size_t(unsafe.Sizeof(values[0])),
		(C.qsort_cmp_func_t)(unsafe.Pointer(C.go_qsort_compare)),
	)
	fmt.Println(values)
}

//export go_qsort_compare
func go_qsort_compare(a, b unsafe.Pointer) C.int {
	pa := (*C.int)(a)
	pb := (*C.int)(b)
	return C.int(*pb - *pa)
}
```

## Go→C→GO

```go
//main.go
package main

/*
#include <stdlib.h>
void print_str(const char *s);
*/
import "C"
import "unsafe"

func Print(s string) {
	cs := C.CString(s)
	C.print_str(cs)
	C.free(unsafe.Pointer(cs))
}
func main() {
	str1 := "hi how are you\n"
	Print(str1)
}

//export HelloByGo
func HelloByGo(name string) *C.char {
	return C.CString("greeting " + name)
}
```

```c
//exp.c
#include "stdio.h"
#include "stdlib.h"
#include "_cgo_export.h"
void print_str(const char *s)
{
    printf("%s\n", s?s:"nil");
    // C语言调用 Go语言函数
    GoString name;
    name.p = "123";
    name.n = 3;
    char *greeting = HelloByGo(name);
    printf("call go: %s\n", greeting);
    free(greeting);
}
```

```powershell
> go run .
hi how are you

call go: greeting 123
```

## C→GO→C

```c
//hello.c
#include <stdio.h>
int helloFromC() {
    printf("Hi from C\n");
    return 0;
}
```

```go
//main.go
package main

/*
extern int helloFromC();
*/
import "C"
import "fmt"

//export HelloFromGo
func HelloFromGo() {
	fmt.Printf("Hello from Go!\n")
	C.helloFromC()
}
func main() {
}
```

```powershell
go build -o hello.so -buildmode=c-shared .
```

```c
x/main.c
#include <stdio.h>
#include "hello.h"
int main() {
    printf("use hello lib from C:\n");

    HelloFromGo();

    return 0;
}
```

```powershell
cp hello.h x/ && cp hello.so x/
gcc -o main main.c hello.so
```

# 总结

## 函数

```go
C.CString("") // 将go string转为char*
C.puts() // 调用C语言的puts函数输出 C 字符串
C.GoString() // char* 转为 go string
```

## 数据类型

```go
*C.char // string
_GoString_ // == string
```

## 类型转换

### Go 类型

```go
var p unsafe.Pointer = nil        // unsafe
var q uintptr        = uintptr(p) // builtin
```

### C 类型

```go
void     *p = NULL;
uintptr_t q = (uintptr_t)(p); // <stdint.h>
```

### Go unsafe

```go
type ArbitraryType int
type Pointer *ArbitraryType //面向编译器无法保证安全的指针类型转换

func Sizeof(x ArbitraryType) uintptr //值所对应变量在内存中的大小
func Alignof(x ArbitraryType) uintptr //值所对应变量在内存中地址几个字节对齐
func Offsetof(x ArbitraryType) uintptr //结构体中成员的偏移量
```

### C unsafe

```go
typedef void* Pointer; // C指针的安全性永远需要自己负责

sizeof(type or expression); // C 关键字, 语义和 Go 基本一致
offsetof(type, member);     // <stddef.h> // 宏, 展开为表达式, 语义和 Go 基本一致
alignof(type-id);           // C++ 11 // 新特性, 可忽略
```

### 字符串和切片结构

```go
// Go
type reflect.StringHeader struct {
    Data uintptr
    Len  int
}
type reflect.SliceHeader struct {
    Data uintptr
    Len  int
    Cap  int
}
// C
typedef struct { const char *p; GoInt n; } GoString;
typedef struct { void *data; GoInt len; GoInt cap; } GoSlice;
// reflect 包定义的结构和CGO生成的C结构是一致的
// GoString 和 GoSlice 和头部结构是兼容的
```

### int32 与 char\*之间转换

```go
  // int32 => *C.char
	var x = int32(9527)
	var p *C.char = (*C.char)(unsafe.Pointer(uintptr(x)))

	// *C.char => int32
	var q int32 = int32(uintptr(unsafe.Pointer(p)))
	fmt.Printf("%d \n", q)
```

### 两个不同类型之间转换

```go
var p *X
var q *Y

q = (*Y)(unsafe.Pointer(p)) // *X => *Y
p = (*X)(unsafe.Pointer(q)) // *Y => *X
```

### 不同数组类型的转换

```go
// 所有切片拥有相同的头部 reflect.SliceHeader
// 重新构造切片头部即可完成转换
var p []X
var q []Y // q = p

pHdr := (*reflect.SliceHeader)(unsafe.Pointer(&p))
qHdr := (*reflect.SliceHeader)(unsafe.Pointer(&q))

pHdr.Data = qHdr.Data
pHdr.Len = qHdr.Len * unsafe.Sizeof(q[0]) / unsafe.Sizeof(p[0])
pHdr.Cap = qHdr.Cap * unsafe.Sizeof(q[0]) / unsafe.Sizeof(p[0])
```

# 导出

## C 导出 so

```c
// number/number.h
int number_add_mod(int a, int b, int mod);

// number/number.c
int number_add_mod(int a, int b, int mod) {
	return (a+b)%mod;
}
$ gcc -shared -o libnumber.so number.c
```

## Go 导出静态库和动态库

```go
package main

import "C"

func main() {}

//export number_add_mod
func number_add_mod(a, b, mod C.int) C.int {
	return (a + b) % mod
}
$ go build -buildmode=c-archive -o number.a
$ go build -buildmode=c-shared -o number.so
```

---

## 第二部分：TIPTOP GP 设置 CGo 环境

## C 编译器

### GCC 版本确认

RedHat6.5 C 编译器是 GCC，只要版本大于 4.7 即可。

使用 `gcc -v` 查看 gcc 版本。

![Pasted image 20260518104158.png](/images/fedbe135-00.png)

### GCC 版本升级

如果你的版本低于 4.7，无法使用 CGo，需要至少升级到 4.7 才可以。建议直接升级到 4.8。

升级步骤见此 TODO，需要有一些 linux 使用经验才可升级，请谨慎，如果有测试主机在测试主机先升级试用。

## Go 编译器

Go 编译器设置比较简单，只要下载上传到服务器解压即可，不需要编译。

### 官网下载

[官网下载地址](https://go.dev/dl/)

![Pasted image 20260518104209.png](/images/fedbe135-01.png)

下载 linux 版本，程序版本大于 go1.10 即可。建议 go1.18 版本以上，可以正常使用 go work

### 解压安装

```bash
<topprod:/u1/usr/tiptop> ls -l go1.22*
-rw-r--r-- 1 tiptop tiptop 68958945 May 28 11:41 go1.22.3.linux-amd64.tar.gz
<topprod:/u1/usr/tiptop> tar -zxvf go1.22.3.linux-amd64.tar.gz -C ./go
```

`./go` 是你要安装的目录位置

```bash
<topprod:/u1/usr/tiptop/go/bin> ls -l ~/go/bin/
total 14572
-rwxr-xr-x 1 tiptop tiptop 12403672 Aug  5  2023 go
-rwxr-xr-x 1 tiptop tiptop  2513259 Aug  5  2023 gofmt
```

`~/go/bin/go`，这个文件就是 go 的编译器

`~/go/bin/go version` 查看当前版本

```bash
<topprod:/u1/usr/tiptop> ~/go/bin/go version
go version go1.21.0 linux/amd64
```

💡

你可以将 go 编译器设置到$PATH 路径，避免每次都要输入路径

## 环境变量

C 语言和 CGo 编译后的文件，都是 so 文件，程序调用时是根据几个环境变量进行查询。

所以有一些环境变量需要知道或者重新设置。

- $FGLLDPATH BDL 运行时会在此路径遍历 so 文件，最终需要 BDL 调用的 so 文件必须包含在此目录下。
- $FGLDIR 目录，此目录是 C 语言 TIPTOP GP 环境下，共享包的位置，最终编译的 so 文件的依赖 so 文件需要放到此目录下。
💡

使用 ln -s 软连接可以不移动文件，将链接文件放到对应目录

## 测试环境设置是否成功

---

## 第三部分：Redhat 6.5 GCC 升级到 4.8

# 升级前版本信息

## red hat

```bash
[root@ERP-AP02 ~]# cat /etc/redhat-release
Red Hat Enterprise Linux Server release 6.5 (Santiago)
```

## GCC

```bash
[root@ERP-AP02 ~]# gcc -v
Using built-in specs.
Target: x86_64-redhat-linux
Configured with: ../configure --prefix=/usr --mandir=/usr/share/man --infodir=/usr/share/info --with-bugurl=http://bugzilla.redhat.com/bugzilla --enable-bootstrap --enable-shared --enable-threads=posix --enable-checking=release --with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions --enable-gnu-unique-object --enable-languages=c,c++,objc,obj-c++,java,fortran,ada --enable-java-awt=gtk --disable-dssi --with-java-home=/usr/lib/jvm/java-1.5.0-gcj-1.5.0.0/jre --enable-libgcj-multifile --enable-java-maintainer-mode --with-ecj-jar=/usr/share/java/eclipse-ecj.jar --disable-libjava-multilib --with-ppl --with-cloog --with-tune=generic --with-arch_32=i686 --build=x86_64-redhat-linux
Thread model: posix
gcc version 4.4.7 20120313 (Red Hat 4.4.7-4) (GCC)
```

```bash
[root@ERP-AP02 ~]# gcc -v
Using built-in specs.
Target: x86_64-redhat-linux
Configured with: ../configure --prefix=/usr --mandir=/usr/share/man --infodir=/usr/share/info --with-bugurl=http://bugzilla.redhat.com/bugzilla --enable-bootstrap --enable-shared --enable-threads=posix --enable-checking=release --with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions --enable-gnu-unique-object --enable-languages=c,c++,objc,obj-c++,java,fortran,ada --enable-java-awt=gtk --disable-dssi --with-java-home=/usr/lib/jvm/java-1.5.0-gcj-1.5.0.0/jre --enable-libgcj-multifile --enable-java-maintainer-mode --with-ecj-jar=/usr/share/java/eclipse-ecj.jar --disable-libjava-multilib --with-ppl --with-cloog --with-tune=generic --with-arch_32=i686 --build=x86_64-redhat-linux
Thread model: posix
gcc version 4.4.7 20120313 (Red Hat 4.4.7-4) (GCC)
```

# 升级顺序

## 安装SCL

[centos-release-scl-rh-1-1.el6.centos.noarch.rpm](https://prod-files-secure.s3.us-west-2.amazonaws.com/b1dbc1f7-4866-487d-86a2-41b94a254a88/fa71a4e6-eea0-402d-beb5-c49f2c53b5f3/centos-release-scl-rh-1-1.el6.centos.noarch.rpm)

`rpm -ivh centos-release-scl-rh-1-1.el6.centos.noarch.rpm`

## 下载源码

wget http:[//ftp.gnu.org/gnu/gcc/gcc-4.8.0/gcc-4.8.0.tar.bz2](https://ftp.gnu.org/gnu/gcc/gcc-4.8.0/gcc-4.8.0.tar.bz2)

tar -jxvf gcc-4.8.0.tar.bz2

## 下载依赖库

cd gcc-4.8.0

./contrib/download\_prerequisites

cd ..

## 建立输出目录

mkdir gcc-build-4.8.0

## 产生makefile文件

cd gcc-build-4.8.0

../gcc-4.8.0/configure --enable-checking=release --enable-languages=c,c++ --disable-multilib

## 编译

make -j4

## 安装

make install

## 切换新版本

updatedb

locate gcc-4.8|tail

ls /usr/local/bin | grep gcc

update-alternatives --install /usr/bin/gcc gcc /usr/local/bin/i686-pc-linux-gnu-gcc 40

---

## 第四部分：BDL 调用 golang(cgo) 简单示例

## golang 编译

```go
package main

import "C"
import "fmt"

//export hello
func hello(){
    fmt.Println("hello world")
}
//export add
func add(a,b int) int {
    return a+b
}
func main(){
}
```

golang中要导出的函数前要增加备注`//export hello`，且必须写有`main`函数。

`import "C"`也是必须导入的。

使用命令

`go build -buildmode=c-shared -o xxx.so yyy` 进行编译产生.so和.h文件，其中xxx是.so的文件名，yyy是项目名称。

如果编译之后未产生.h 文件，说明没有导出任何函数，请检查go源码。

编译产生的.so文件运行时需要，需要加载到`$FGLDIR/lib`目录下，也可以`ln -s`创建软链接。

## C语言封装

BDL调用C语言可以见[BDL调用C语言](https://www.notion.so/call-c_ext-in-4gl)

源码如下：

```c
#include <stdio.h>
#include "f2c/fglExt.h"
#include "libsum.h"

int sum(int);
GoInt Sum(GoInt,GoInt);

UsrFunction usrFunctions[]={
  { "sum", sum, 2, 1 },
  { 0,0,0,0 }
};

int sum(int in_num){
    int s,a=0,b=0;
    popint(&a);
    popint(&b);
    s = Sum(a,b);
    pushint(s);
    return 1;
}
```

1. 产生.o 文件
```bash
gcc -c -I $FGLDIR/include -fPIC demo.c
```

1. 产生.so文件
```bash
gcc -shared -o libsuma.so demo.o  -L $FGLDIR/lib -lfgl -lsum
```

1. 将产生的.so文件放到`$FGLLDPATH`的路径中
## BDL调用

```sql
import libsuma
function main()
    define s integer

    call sum(2,3) returning s
    display sfmt("\\n2+3=%1",s)
end function
```

BDL调用时只要调用libsuma即可，libsum会在libsuma调用后自动加载。

[直接调用的.so](http://xn--gzut30b33azmr38f.so/) 在`$FGLLDPATH`目录，c调用的.so在`$FGLDIR/lib`目录。
