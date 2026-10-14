---
title: 'Go 设计模式速查手册'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'go-she-ji-mo-shi-su-cha-shou-ce'
tags: ['golang', '设计模式']
description: 'Go 设计模式速查手册 整理自 Refactoring.Guru - Design Patterns in Go (https://refactoring.guru/design-patterns/go) --- 目录 - 创建型模式 (Creational Patterns) ( 创建型模式-creational-patterns) - 1. 单例模式 ('
draft: false
---

> 整理自 \[Refactoring.Guru - Design Patterns in Go\](https://refactoring.guru/design-patterns/go)

---

## 目录

- 创建型模式 (Creational Patterns)

  - 1. 单例模式 (Singleton)
  - 2. 工厂方法模式 (Factory Method)
  - 3. 抽象工厂模式 (Abstract Factory)
  - 4. 建造者模式 (Builder)
  - 5. 原型模式 (Prototype)

- 结构型模式 (Structural Patterns)

  - 6. 适配器模式 (Adapter)
  - 7. 桥接模式 (Bridge)
  - 8. 组合模式 (Composite)
  - 9. 装饰器模式 (Decorator)
  - 10. 外观模式 (Facade)
  - 11. 享元模式 (Flyweight)
  - 12. 代理模式 (Proxy)

- 行为型模式 (Behavioral Patterns)

  - 13. 责任链模式 (Chain of Responsibility)
  - 14. 命令模式 (Command)
  - 15. 迭代器模式 (Iterator)
  - 16. 中介者模式 (Mediator)
  - 17. 备忘录模式 (Memento)
  - 18. 观察者模式 (Observer)
  - 19. 状态模式 (State)
  - 20. 策略模式 (Strategy)
  - 21. 模板方法模式 (Template Method)
  - 22. 访问者模式 (Visitor)
---

## 创建型模式 (Creational Patterns)

### 1. 单例模式 (Singleton)

**意图**: 确保一个类只有一个实例，并提供一个全局访问点。

**说明**: 单例与全局变量几乎有相同的优缺点。虽然它们非常方便，但会破坏代码的模块化。

**Go 实现要点**:

- 使用 `sync.Mutex` 进行双重检查锁定（Double-Check Locking）
- 或使用 `sync.Once` 确保只执行一次
### 方式一: `sync.Mutex + 双重检查锁定

```go
package main

import (
    "fmt"
    "sync"
)

var lock = &sync.Mutex{}

type single struct{}

var singleInstance *single

func getInstance() *single {
    if singleInstance == nil {
        lock.Lock()
        defer lock.Unlock()
        if singleInstance == nil {
            fmt.Println("Creating single instance now.")
            singleInstance = &single{}
        } else {
            fmt.Println("Single instance already created.")
        }
    } else {
        fmt.Println("Single instance already created.")
    }
    return singleInstance
}
```

### 方式二: `sync.Once` (推荐)

```go
package main

import (
    "fmt"
    "sync"
)

var once sync.Once

type single struct{}

var singleInstance *single

func getInstance() *single {
    if singleInstance == nil {
        once.Do(func() {
            fmt.Println("Creating single instance now.")
            singleInstance = &single{}
        })
    } else {
        fmt.Println("Single instance already created.")
    }
    return singleInstance
}
```

### main.go

```go
package main

import "fmt"

func main() {
    for i := 0; i < 30; i++ {
        go getInstance()
    }
    fmt.Scanln()
}
```

**输出**:

```text
Creating single instance now.
Single instance already created.
Single instance already created.
...
```

---

### 2. 工厂方法模式 (Factory Method)

**意图**: 提供一种创建对象的接口，让子类决定实例化哪个类。

**说明**: 由于 Go 缺乏类和继承等 OOP 特性，无法实现经典的工厂方法模式。但可以实现简单工厂（Simple Factory）版本。

**示例**: 使用工厂构建各种类型的武器。

### iGun.go - 产品接口

```go
package main

type IGun interface {
    setName(name string)
    setPower(power int)
    getName() string
    getPower() int
}
```

### gun.go - 具体产品基类

```go
package main

type Gun struct {
    name  string
    power int
}

func (g *Gun) setName(name string) {
    g.name = name
}

func (g *Gun) getName() string {
    return g.name
}

func (g *Gun) setPower(power int) {
    g.power = power
}

func (g *Gun) getPower() int {
    return g.power
}
```

### ak47.go - 具体产品

```go
package main

type Ak47 struct {
    Gun
}

func newAk47() IGun {
    return &Ak47{
        Gun: Gun{
            name:  "AK47 gun",
            power: 4,
        },
    }
}
```

### musket.go - 具体产品

```go
package main

type musket struct {
    Gun
}

func newMusket() IGun {
    return &musket{
        Gun: Gun{
            name:  "Musket gun",
            power: 1,
        },
    }
}
```

### gunFactory.go - 工厂

```go
package main

import "fmt"

func getGun(gunType string) (IGun, error) {
    if gunType == "ak47" {
        return newAk47(), nil
    }
    if gunType == "musket" {
        return newMusket(), nil
    }
    return nil, fmt.Errorf("Wrong gun type passed")
}
```

### main.go

```go
package main

import "fmt"

func main() {
    ak47, _ := getGun("ak47")
    musket, _ := getGun("musket")

    printDetails(ak47)
    printDetails(musket)
}

func printDetails(g IGun) {
    fmt.Printf("Gun: %s
", g.getName())
    fmt.Printf("Power: %d
", g.getPower())
}
```

**输出**:

```text
Gun: AK47 gun
Power: 4
Gun: Musket gun
Power: 1
```

---

### 3. 抽象工厂模式 (Abstract Factory)

**意图**: 创建相关对象家族，而不需要指定它们的具体类。

**示例**: 购买运动套装（鞋子和衬衫），需要同一品牌的产品互相匹配。

### iSportsFactory.go - 抽象工厂接口

```go
package main

import "fmt"

type ISportsFactory interface {
    makeShoe() IShoe
    makeShirt() IShirt
}

func GetSportsFactory(brand string) (ISportsFactory, error) {
    if brand == "adidas" {
        return &Adidas{}, nil
    }
    if brand == "nike" {
        return &Nike{}, nil
    }
    return nil, fmt.Errorf("Wrong brand type passed")
}
```

### adidas.go / nike.go - 具体工厂

```go
package main

// Adidas 具体工厂
type Adidas struct{}

func (a *Adidas) makeShoe() IShoe {
    return &AdidasShoe{
        Shoe: Shoe{logo: "adidas", size: 14},
    }
}

func (a *Adidas) makeShirt() IShirt {
    return &AdidasShirt{
        Shirt: Shirt{logo: "adidas", size: 14},
    }
}

// Nike 具体工厂
type Nike struct{}

func (n *Nike) makeShoe() IShoe {
    return &NikeShoe{
        Shoe: Shoe{logo: "nike", size: 14},
    }
}

func (n *Nike) makeShirt() IShirt {
    return &NikeShirt{
        Shirt: Shirt{logo: "nike", size: 14},
    }
}
```

### iShoe.go / iShirt.go - 抽象产品

```go
package main

// 鞋子接口
type IShoe interface {
    setLogo(logo string)
    setSize(size int)
    getLogo() string
    getSize() int
}

type Shoe struct {
    logo string
    size int
}

func (s *Shoe) setLogo(logo string) { s.logo = logo }
func (s *Shoe) getLogo() string     { return s.logo }
func (s *Shoe) setSize(size int)    { s.size = size }
func (s *Shoe) getSize() int        { return s.size }

// 衬衫接口
type IShirt interface {
    setLogo(logo string)
    setSize(size int)
    getLogo() string
    getSize() int
}

type Shirt struct {
    logo string
    size int
}

func (s *Shirt) setLogo(logo string) { s.logo = logo }
func (s *Shirt) getLogo() string     { return s.logo }
func (s *Shirt) setSize(size int)    { s.size = size }
func (s *Shirt) getSize() int        { return s.size }
```

### 具体产品

```go
package main

// 具体产品通过嵌入基类实现接口
type AdidasShoe struct{ Shoe }
type NikeShoe struct{ Shoe }
type AdidasShirt struct{ Shirt }
type NikeShirt struct{ Shirt }
```

### main.go

```go
package main

import "fmt"

func main() {
    adidasFactory, _ := GetSportsFactory("adidas")
    nikeFactory, _ := GetSportsFactory("nike")

    nikeShoe := nikeFactory.makeShoe()
    nikeShirt := nikeFactory.makeShirt()
    adidasShoe := adidasFactory.makeShoe()
    adidasShirt := adidasFactory.makeShirt()

    printShoeDetails(nikeShoe)
    printShirtDetails(nikeShirt)
    printShoeDetails(adidasShoe)
    printShirtDetails(adidasShirt)
}

func printShoeDetails(s IShoe) {
    fmt.Printf("Logo: %s
Size: %d
", s.getLogo(), s.getSize())
}

func printShirtDetails(s IShirt) {
    fmt.Printf("Logo: %s
Size: %d
", s.getLogo(), s.getSize())
}
```

---

### 4. 建造者模式 (Builder)

**意图**: 允许你逐步构建复杂对象。该模式允许你使用相同的构造代码生成不同类型和表示的对象。

**示例**: 构建不同类型的房子（普通房子和爱斯基摩人冰屋）。

### iBuilder.go - 建造者接口

```go
package main

type IBuilder interface {
    setWindowType()
    setDoorType()
    setNumFloor()
    getHouse() House
}

func getBuilder(builderType string) IBuilder {
    if builderType == "normal" {
        return newNormalBuilder()
    }
    if builderType == "igloo" {
        return newIglooBuilder()
    }
    return nil
}
```

### normalBuilder.go / iglooBuilder.go - 具体建造者

```go
package main

// 普通房子建造者
type NormalBuilder struct {
    windowType string
    doorType   string
    floor      int
}

func newNormalBuilder() *NormalBuilder { return &NormalBuilder{} }
func (b *NormalBuilder) setWindowType() { b.windowType = "Wooden Window" }
func (b *NormalBuilder) setDoorType()   { b.doorType = "Wooden Door" }
func (b *NormalBuilder) setNumFloor()   { b.floor = 2 }
func (b *NormalBuilder) getHouse() House {
    return House{doorType: b.doorType, windowType: b.windowType, floor: b.floor}
}

// 冰屋建造者
type IglooBuilder struct {
    windowType string
    doorType   string
    floor      int
}

func newIglooBuilder() *IglooBuilder { return &IglooBuilder{} }
func (b *IglooBuilder) setWindowType() { b.windowType = "Snow Window" }
func (b *IglooBuilder) setDoorType()   { b.doorType = "Snow Door" }
func (b *IglooBuilder) setNumFloor()   { b.floor = 1 }
func (b *IglooBuilder) getHouse() House {
    return House{doorType: b.doorType, windowType: b.windowType, floor: b.floor}
}
```

### house.go - 产品

```go
package main

type House struct {
    windowType string
    doorType   string
    floor      int
}
```

### director.go - 指挥者

```go
package main

type Director struct {
    builder IBuilder
}

func newDirector(b IBuilder) *Director {
    return &Director{builder: b}
}

func (d *Director) setBuilder(b IBuilder) {
    d.builder = b
}

func (d *Director) buildHouse() House {
    d.builder.setDoorType()
    d.builder.setWindowType()
    d.builder.setNumFloor()
    return d.builder.getHouse()
}
```

### main.go

```go
package main

import "fmt"

func main() {
    normalBuilder := getBuilder("normal")
    iglooBuilder := getBuilder("igloo")

    director := newDirector(normalBuilder)
    normalHouse := director.buildHouse()
    fmt.Printf("Normal House Door Type: %s
", normalHouse.doorType)
    fmt.Printf("Normal House Window Type: %s
", normalHouse.windowType)
    fmt.Printf("Normal House Num Floor: %d
", normalHouse.floor)

    director.setBuilder(iglooBuilder)
    iglooHouse := director.buildHouse()
    fmt.Printf("
Igloo House Door Type: %s
", iglooHouse.doorType)
    fmt.Printf("Igloo House Window Type: %s
", iglooHouse.windowType)
    fmt.Printf("Igloo House Num Floor: %d
", iglooHouse.floor)
}
```

**输出**:

```text
Normal House Door Type: Wooden Door
Normal House Window Type: Wooden Window
Normal House Num Floor: 2

Igloo House Door Type: Snow Door
Igloo House Window Type: Snow Window
Igloo House Num Floor: 1
```

---

### 5. 原型模式 (Prototype)

**意图**: 允许复制现有对象，而无需使代码依赖于它们的类。

**示例**: 操作系统文件系统的递归克隆。文件夹包含文件和文件夹，可以无限嵌套。

### inode.go - 原型接口

```go
package main

type Inode interface {
    print(string)
    clone() Inode
}
```

### file.go - 具体原型（文件）

```go
package main

import "fmt"

type File struct {
    name string
}

func (f *File) print(indentation string) {
    fmt.Println(indentation + f.name)
}

func (f *File) clone() Inode {
    return &File{name: f.name + "_clone"}
}
```

### folder.go - 具体原型（文件夹）

```go
package main

import "fmt"

type Folder struct {
    children []Inode
    name     string
}

func (f *Folder) print(indentation string) {
    fmt.Println(indentation + f.name)
    for _, i := range f.children {
        i.print(indentation + indentation)
    }
}

func (f *Folder) clone() Inode {
    cloneFolder := &Folder{name: f.name + "_clone"}
    var tempChildren []Inode
    for _, i := range f.children {
        copy := i.clone()
        tempChildren = append(tempChildren, copy)
    }
    cloneFolder.children = tempChildren
    return cloneFolder
}
```

### main.go

```go
package main

import "fmt"

func main() {
    file1 := &File{name: "File1"}
    file2 := &File{name: "File2"}
    file3 := &File{name: "File3"}

    folder1 := &Folder{children: []Inode{file1}, name: "Folder1"}
    folder2 := &Folder{children: []Inode{folder1, file2, file3}, name: "Folder2"}

    fmt.Println("
Printing hierarchy for Folder2")
    folder2.print("  ")

    cloneFolder := folder2.clone()
    fmt.Println("
Printing hierarchy for clone Folder")
    cloneFolder.print("  ")
}
```

**输出**:

```text
Printing hierarchy for Folder2
  Folder2
    Folder1
        File1
    File2
    File3

Printing hierarchy for clone Folder
  Folder2_clone
    Folder1_clone
        File1_clone
    File2_clone
    File3_clone
```

---

## 结构型模式 (Structural Patterns)

### 6. 适配器模式 (Adapter)

**意图**: 允许接口不兼容的对象能够协同工作。

**示例**: 客户端期望 Lightning 接口，但有一个 Windows 笔记本电脑只提供 USB 接口。适配器将 Lightning 信号转换为 USB 信号。

### computer.go - 客户端接口

```go
package main

type Computer interface {
    InsertIntoLightningPort()
}
```

### mac.go - 服务（兼容）

```go
package main

import "fmt"

type Mac struct{}

func (m *Mac) InsertIntoLightningPort() {
    fmt.Println("Lightning connector is plugged into mac machine.")
}
```

### windows.go - 不兼容的服务

```go
package main

import "fmt"

type Windows struct{}

func (w *Windows) insertIntoUSBPort() {
    fmt.Println("USB connector is plugged into windows machine.")
}
```

### windowsAdapter.go - 适配器

```go
package main

import "fmt"

type WindowsAdapter struct {
    windowMachine *Windows
}

func (w *WindowsAdapter) InsertIntoLightningPort() {
    fmt.Println("Adapter converts Lightning signal to USB.")
    w.windowMachine.insertIntoUSBPort()
}
```

### client.go

```go
package main

import "fmt"

type Client struct{}

func (c *Client) InsertLightningConnectorIntoComputer(com Computer) {
    fmt.Println("Client inserts Lightning connector into computer.")
    com.InsertIntoLightningPort()
}
```

### main.go

```go
package main

func main() {
    client := &Client{}
    mac := &Mac{}
    client.InsertLightningConnectorIntoComputer(mac)

    windowsMachine := &Windows{}
    windowsMachineAdapter := &WindowsAdapter{windowMachine: windowsMachine}
    client.InsertLightningConnectorIntoComputer(windowsMachineAdapter)
}
```

**输出**:

```text
Client inserts Lightning connector into computer.
Lightning connector is plugged into mac machine.
Client inserts Lightning connector into computer.
Adapter converts Lightning signal to USB.
USB connector is plugged into windows machine.
```

---

### 7. 桥接模式 (Bridge)

**意图**: 将一个大类或一组紧密相关的类拆分为两个独立的类层次结构——抽象和实现——使它们可以独立开发。

**示例**: 两种计算机（Mac、Windows）和两种打印机（Epson、HP），需要在任意组合下工作。

### computer.go / printer.go - 抽象与实现接口

```go
package main

// 抽象层次：计算机
type Computer interface {
    Print()
    SetPrinter(Printer)
}

// 实现层次：打印机
type Printer interface {
    PrintFile()
}
```

### mac.go / windows.go - 精炼抽象

```go
package main

import "fmt"

// Mac
type Mac struct {
    printer Printer
}

func (m *Mac) Print() {
    fmt.Println("Print request for mac")
    m.printer.PrintFile()
}

func (m *Mac) SetPrinter(p Printer) {
    m.printer = p
}

// Windows
type Windows struct {
    printer Printer
}

func (w *Windows) Print() {
    fmt.Println("Print request for windows")
    w.printer.PrintFile()
}

func (w *Windows) SetPrinter(p Printer) {
    w.printer = p
}
```

### epson.go / hp.go - 具体实现

```go
package main

import "fmt"

// Epson
type Epson struct{}

func (p *Epson) PrintFile() {
    fmt.Println("Printing by a EPSON Printer")
}

// HP
type Hp struct{}

func (p *Hp) PrintFile() {
    fmt.Println("Printing by a HP Printer")
}
```

### main.go

```go
package main

import "fmt"

func main() {
    hpPrinter := &Hp{}
    epsonPrinter := &Epson{}

    macComputer := &Mac{}
    macComputer.SetPrinter(hpPrinter)
    macComputer.Print()
    fmt.Println()

    macComputer.SetPrinter(epsonPrinter)
    macComputer.Print()
    fmt.Println()

    winComputer := &Windows{}
    winComputer.SetPrinter(hpPrinter)
    winComputer.Print()
    fmt.Println()

    winComputer.SetPrinter(epsonPrinter)
    winComputer.Print()
    fmt.Println()
}
```

---

### 8. 组合模式 (Composite)

**意图**: 允许你将对象组合成树结构，然后像处理单个对象一样处理这些结构。

**示例**: 文件系统中的文件和文件夹。对文件夹的搜索操作会递归应用到所有子文件和子文件夹。

### component.go - 组件接口

```go
package main

type Component interface {
    search(string)
}
```

### folder.go - 组合（容器）

```go
package main

import "fmt"

type Folder struct {
    components []Component
    name       string
}

func (f *Folder) search(keyword string) {
    fmt.Printf("Serching recursively for keyword %s in folder %s
", keyword, f.name)
    for _, composite := range f.components {
        composite.search(keyword)
    }
}

func (f *Folder) add(c Component) {
    f.components = append(f.components, c)
}
```

### file.go - 叶子

```go
package main

import "fmt"

type File struct {
    name string
}

func (f *File) search(keyword string) {
    fmt.Printf("Searching for keyword %s in file %s
", keyword, f.name)
}

func (f *File) getName() string {
    return f.name
}
```

### main.go

```go
package main

func main() {
    file1 := &File{name: "File1"}
    file2 := &File{name: "File2"}
    file3 := &File{name: "File3"}

    folder1 := &Folder{name: "Folder1"}
    folder1.add(file1)

    folder2 := &Folder{name: "Folder2"}
    folder2.add(file2)
    folder2.add(file3)
    folder2.add(folder1)

    folder2.search("rose")
}
```

**输出**:

```text
Serching recursively for keyword rose in folder Folder2
Searching for keyword rose in file File2
Searching for keyword rose in file File3
Serching recursively for keyword rose in folder Folder1
Searching for keyword rose in file File1
```

---

### 9. 装饰器模式 (Decorator)

**意图**: 允许你通过将对象放入包含行为的特殊包装器对象中来动态地为对象添加新行为。

**示例**: 披萨可以添加不同的配料（芝士、番茄），每个配料都会增加价格。

### pizza.go - 组件接口

```go
package main

type IPizza interface {
    getPrice() int
}
```

### veggieMania.go - 具体组件

```go
package main

type VeggieMania struct{}

func (p *VeggieMania) getPrice() int {
    return 15
}
```

### tomatoTopping.go / cheeseTopping.go - 具体装饰器

```go
package main

// 番茄配料
type TomatoTopping struct {
    pizza IPizza
}

func (c *TomatoTopping) getPrice() int {
    pizzaPrice := c.pizza.getPrice()
    return pizzaPrice + 7
}

// 芝士配料
type CheeseTopping struct {
    pizza IPizza
}

func (c *CheeseTopping) getPrice() int {
    pizzaPrice := c.pizza.getPrice()
    return pizzaPrice + 10
}
```

### main.go

```go
package main

import "fmt"

func main() {
    pizza := &VeggieMania{}

    // 添加芝士配料
    pizzaWithCheese := &CheeseTopping{pizza: pizza}

    // 添加番茄配料
    pizzaWithCheeseAndTomato := &TomatoTopping{pizza: pizzaWithCheese}

    fmt.Printf("Price of veggeMania with tomato and cheese topping is %d
",
        pizzaWithCheeseAndTomato.getPrice())
}
```

**输出**:

```text
Price of veggeMania with tomato and cheese topping is 32
```

---

### 10. 外观模式 (Facade)

**意图**: 为复杂的类、库或框架系统提供简化的（但有限的）接口。

**示例**: 使用信用卡购买披萨涉及多个子系统（账户验证、安全码验证、余额扣款、记账、发送通知）。外观模式将这些复杂性隐藏在一个简单接口后面。

### walletFacade.go - 外观

```go
package main

import "fmt"

type WalletFacade struct {
    account      *Account
    wallet       *Wallet
    securityCode *SecurityCode
    notification *Notification
    ledger       *Ledger
}

func newWalletFacade(accountID string, code int) *WalletFacade {
    fmt.Println("Starting create account")
    walletFacade := &WalletFacade{
        account:      newAccount(accountID),
        securityCode: newSecurityCode(code),
        wallet:       newWallet(),
        notification: &Notification{},
        ledger:       &Ledger{},
    }
    fmt.Println("Account created")
    return walletFacade
}

func (w *WalletFacade) addMoneyToWallet(accountID string, securityCode int, amount int) error {
    fmt.Println("Starting add money to wallet")
    if err := w.account.checkAccount(accountID); err != nil {
        return err
    }
    if err := w.securityCode.checkCode(securityCode); err != nil {
        return err
    }
    w.wallet.creditBalance(amount)
    w.notification.sendWalletCreditNotification()
    w.ledger.makeEntry(accountID, "credit", amount)
    return nil
}

func (w *WalletFacade) deductMoneyFromWallet(accountID string, securityCode int, amount int) error {
    fmt.Println("Starting debit money from wallet")
    if err := w.account.checkAccount(accountID); err != nil {
        return err
    }
    if err := w.securityCode.checkCode(securityCode); err != nil {
        return err
    }
    if err := w.wallet.debitBalance(amount); err != nil {
        return err
    }
    w.notification.sendWalletDebitNotification()
    w.ledger.makeEntry(accountID, "debit", amount)
    return nil
}
```

### 子系统

```go
package main

import "fmt"

// 账户
type Account struct {
    name string
}

func newAccount(accountName string) *Account {
    return &Account{name: accountName}
}

func (a *Account) checkAccount(accountName string) error {
    if a.name != accountName {
        return fmt.Errorf("Account Name is incorrect")
    }
    fmt.Println("Account Verified")
    return nil
}

// 安全码
type SecurityCode struct {
    code int
}

func newSecurityCode(code int) *SecurityCode {
    return &SecurityCode{code: code}
}

func (s *SecurityCode) checkCode(incomingCode int) error {
    if s.code != incomingCode {
        return fmt.Errorf("Security Code is incorrect")
    }
    fmt.Println("SecurityCode Verified")
    return nil
}

// 钱包
type Wallet struct {
    balance int
}

func newWallet() *Wallet {
    return &Wallet{balance: 0}
}

func (w *Wallet) creditBalance(amount int) {
    w.balance += amount
    fmt.Println("Wallet balance added successfully")
}

func (w *Wallet) debitBalance(amount int) error {
    if w.balance < amount {
        return fmt.Errorf("Balance is not sufficient")
    }
    fmt.Println("Wallet balance is Sufficient")
    w.balance = w.balance - amount
    return nil
}

// 账本
type Ledger struct{}

func (s *Ledger) makeEntry(accountID, txnType string, amount int) {
    fmt.Printf("Make ledger entry for accountId %s with txnType %s for amount %d
",
        accountID, txnType, amount)
}

// 通知
type Notification struct{}

func (n *Notification) sendWalletCreditNotification() {
    fmt.Println("Sending wallet credit notification")
}

func (n *Notification) sendWalletDebitNotification() {
    fmt.Println("Sending wallet debit notification")
}
```

### main.go

```go
package main

import (
    "fmt"
    "log"
)

func main() {
    fmt.Println()
    walletFacade := newWalletFacade("abc", 1234)
    fmt.Println()

    err := walletFacade.addMoneyToWallet("abc", 1234, 10)
    if err != nil {
        log.Fatalf("Error: %s
", err.Error())
    }

    fmt.Println()
    err = walletFacade.deductMoneyFromWallet("abc", 1234, 5)
    if err != nil {
        log.Fatalf("Error: %s
", err.Error())
    }
}
```

**输出**:

```text
Starting create account
Account created

Starting add money to wallet
Account Verified
SecurityCode Verified
Wallet balance added successfully
Sending wallet credit notification
Make ledger entry for accountId abc with txnType credit for amount 10

Starting debit money from wallet
Account Verified
SecurityCode Verified
Wallet balance is Sufficient
Sending wallet debit notification
Make ledger entry for accountId abc with txnType debit for amount 5
```

---

### 11. 享元模式 (Flyweight)

**意图**: 允许程序通过在不同对象之间共享公共状态部分来支持大量对象，从而将内存消耗保持在较低水平。

**示例**: CS 游戏中，恐怖分子和反恐精英有不同的服装。5 个恐怖分子共享一套服装，5 个反恐精英共享另一套服装，而不是每人创建一套。

**关键概念**:

- **内部状态 (Intrinsic State)**: 服装，可以被多个对象共享
- **外部状态 (Extrinsic State)**: 玩家位置和武器，每个对象不同
### dress.go - 享元接口

```go
package main

type Dress interface {
    getColor() string
}
```

### terroristDress.go / counterTerroristDress.go - 具体享元

```go
package main

// 恐怖分子服装
type TerroristDress struct {
    color string
}

func (t *TerroristDress) getColor() string {
    return t.color
}

func newTerroristDress() *TerroristDress {
    return &TerroristDress{color: "red"}
}

// 反恐精英服装
type CounterTerroristDress struct {
    color string
}

func (c *CounterTerroristDress) getColor() string {
    return c.color
}

func newCounterTerroristDress() *CounterTerroristDress {
    return &CounterTerroristDress{color: "green"}
}
```

### dressFactory.go - 享元工厂

```go
package main

import "fmt"

const (
    TerroristDressType         = "tDress"
    CounterTerrroristDressType = "ctDress"
)

var (
    dressFactorySingleInstance = &DressFactory{
        dressMap: make(map[string]Dress),
    }
)

type DressFactory struct {
    dressMap map[string]Dress
}

func (d *DressFactory) getDressByType(dressType string) (Dress, error) {
    if d.dressMap[dressType] != nil {
        return d.dressMap[dressType], nil
    }
    if dressType == TerroristDressType {
        d.dressMap[dressType] = newTerroristDress()
        return d.dressMap[dressType], nil
    }
    if dressType == CounterTerrroristDressType {
        d.dressMap[dressType] = newCounterTerroristDress()
        return d.dressMap[dressType], nil
    }
    return nil, fmt.Errorf("Wrong dress type passed")
}

func getDressFactorySingleInstance() *DressFactory {
    return dressFactorySingleInstance
}
```

### player.go - 上下文

```go
package main

type Player struct {
    dress      Dress
    playerType string
    lat        int
    long       int
}

func newPlayer(playerType, dressType string) *Player {
    dress, _ := getDressFactorySingleInstance().getDressByType(dressType)
    return &Player{
        playerType: playerType,
        dress:      dress,
    }
}

func (p *Player) newLocation(lat, long int) {
    p.lat = lat
    p.long = long
}
```

### game.go / main.go

```go
package main

import "fmt"

type game struct {
    terrorists        []*Player
    counterTerrorists []*Player
}

func newGame() *game {
    return &game{
        terrorists:        make([]*Player, 1),
        counterTerrorists: make([]*Player, 1),
    }
}

func (c *game) addTerrorist(dressType string) {
    player := newPlayer("T", dressType)
    c.terrorists = append(c.terrorists, player)
}

func (c *game) addCounterTerrorist(dressType string) {
    player := newPlayer("CT", dressType)
    c.counterTerrorists = append(c.counterTerrorists, player)
}

func main() {
    game := newGame()

    game.addTerrorist(TerroristDressType)
    game.addTerrorist(TerroristDressType)
    game.addTerrorist(TerroristDressType)
    game.addTerrorist(TerroristDressType)

    game.addCounterTerrorist(CounterTerrroristDressType)
    game.addCounterTerrorist(CounterTerrroristDressType)
    game.addCounterTerrorist(CounterTerrroristDressType)

    dressFactoryInstance := getDressFactorySingleInstance()
    for dressType, dress := range dressFactoryInstance.dressMap {
        fmt.Printf("DressColorType: %s
DressColor: %s
", dressType, dress.getColor())
    }
}
```

**输出**:

```text
DressColorType: ctDress
DressColor: green
DressColorType: tDress
DressColor: red
```

---

### 12. 代理模式 (Proxy)

**意图**: 提供一个对象作为真实服务对象的替代品。代理接收客户端请求，做一些工作（访问控制、缓存等），然后将请求传递给服务对象。

**示例**: Nginx 作为应用服务器的代理，提供受控访问、速率限制和请求缓存。

### server.go - 主题接口

```go
package main

type server interface {
    handleRequest(string, string) (int, string)
}
```

### application.go - 真实主题

```go
package main

type Application struct{}

func (a *Application) handleRequest(url, method string) (int, string) {
    if url == "/app/status" && method == "GET" {
        return 200, "Ok"
    }
    if url == "/create/user" && method == "POST" {
        return 201, "User Created"
    }
    return 404, "Not Ok"
}
```

### nginx.go - 代理

```go
package main

type Nginx struct {
    application       *Application
    maxAllowedRequest int
    rateLimiter       map[string]int
}

func newNginxServer() *Nginx {
    return &Nginx{
        application:       &Application{},
        maxAllowedRequest: 2,
        rateLimiter:       make(map[string]int),
    }
}

func (n *Nginx) handleRequest(url, method string) (int, string) {
    allowed := n.checkRateLimiting(url)
    if !allowed {
        return 403, "Not Allowed"
    }
    return n.application.handleRequest(url, method)
}

func (n *Nginx) checkRateLimiting(url string) bool {
    if n.rateLimiter[url] == 0 {
        n.rateLimiter[url] = 1
    }
    if n.rateLimiter[url] > n.maxAllowedRequest {
        return false
    }
    n.rateLimiter[url] = n.rateLimiter[url] + 1
    return true
}
```

### main.go

```go
package main

import "fmt"

func main() {
    nginxServer := newNginxServer()
    appStatusURL := "/app/status"
    createuserURL := "/create/user"

    httpCode, body := nginxServer.handleRequest(appStatusURL, "GET")
    fmt.Printf("
Url: %s
HttpCode: %d
Body: %s
", appStatusURL, httpCode, body)

    httpCode, body = nginxServer.handleRequest(appStatusURL, "GET")
    fmt.Printf("
Url: %s
HttpCode: %d
Body: %s
", appStatusURL, httpCode, body)

    httpCode, body = nginxServer.handleRequest(appStatusURL, "GET")
    fmt.Printf("
Url: %s
HttpCode: %d
Body: %s
", appStatusURL, httpCode, body)

    httpCode, body = nginxServer.handleRequest(createuserURL, "POST")
    fmt.Printf("
Url: %s
HttpCode: %d
Body: %s
", createuserURL, httpCode, body)

    httpCode, body = nginxServer.handleRequest(createuserURL, "GET")
    fmt.Printf("
Url: %s
HttpCode: %d
Body: %s
", createuserURL, httpCode, body)
}
```

**输出**:

```text
Url: /app/status
HttpCode: 200
Body: Ok

Url: /app/status
HttpCode: 200
Body: Ok

Url: /app/status
HttpCode: 403
Body: Not Allowed

Url: /create/user
HttpCode: 201
Body: User Created

Url: /create/user
HttpCode: 404
Body: Not Ok
```

---

## 行为型模式 (Behavioral Patterns)

### 13. 责任链模式 (Chain of Responsibility)

**意图**: 允许将请求沿着处理者链传递，直到其中一个处理请求。

**示例**: 医院应用程序中，患者依次经过接待处、医生、药房、收银台。

### department.go - 处理者接口

```go
package main

type Department interface {
    execute(*Patient)
    setNext(Department)
}
```

### reception.go / doctor.go / medical.go / cashier.go - 具体处理者

```go
package main

import "fmt"

// 接待处
type Reception struct {
    next Department
}

func (r *Reception) execute(p *Patient) {
    if p.registrationDone {
        fmt.Println("Patient registration already done")
        r.next.execute(p)
        return
    }
    fmt.Println("Reception registering patient")
    p.registrationDone = true
    r.next.execute(p)
}

func (r *Reception) setNext(next Department) {
    r.next = next
}

// 医生
type Doctor struct {
    next Department
}

func (d *Doctor) execute(p *Patient) {
    if p.doctorCheckUpDone {
        fmt.Println("Doctor checkup already done")
        d.next.execute(p)
        return
    }
    fmt.Println("Doctor checking patient")
    p.doctorCheckUpDone = true
    d.next.execute(p)
}

func (d *Doctor) setNext(next Department) {
    d.next = next
}

// 药房
type Medical struct {
    next Department
}

func (m *Medical) execute(p *Patient) {
    if p.medicineDone {
        fmt.Println("Medicine already given to patient")
        m.next.execute(p)
        return
    }
    fmt.Println("Medical giving medicine to patient")
    p.medicineDone = true
    m.next.execute(p)
}

func (m *Medical) setNext(next Department) {
    m.next = next
}

// 收银台
type Cashier struct {
    next Department
}

func (c *Cashier) execute(p *Patient) {
    if p.paymentDone {
        fmt.Println("Payment Done")
    }
    fmt.Println("Cashier getting money from patient patient")
}

func (c *Cashier) setNext(next Department) {
    c.next = next
}
```

### patient.go

```go
package main

type Patient struct {
    name              string
    registrationDone  bool
    doctorCheckUpDone bool
    medicineDone      bool
    paymentDone       bool
}
```

### main.go

```go
package main

func main() {
    cashier := &Cashier{}

    medical := &Medical{}
    medical.setNext(cashier)

    doctor := &Doctor{}
    doctor.setNext(medical)

    reception := &Reception{}
    reception.setNext(doctor)

    patient := &Patient{name: "abc"}
    reception.execute(patient)
}
```

**输出**:

```text
Reception registering patient
Doctor checking patient
Medical giving medicine to patient
Cashier getting money from patient patient
```

---

### 14. 命令模式 (Command)

**意图**: 将请求或简单操作转换为对象。转换允许延迟或远程执行命令、存储命令历史等。

**示例**: 电视可以通过遥控器或电视上的按钮打开。两者都嵌入相同的 ON 命令对象。

### command.go - 命令接口

```go
package main

type Command interface {
    execute()
}
```

### device.go - 接收者接口

```go
package main

type Device interface {
    on()
    off()
}
```

### tv.go - 具体接收者

```go
package main

import "fmt"

type Tv struct {
    isRunning bool
}

func (t *Tv) on() {
    t.isRunning = true
    fmt.Println("Turning tv on")
}

func (t *Tv) off() {
    t.isRunning = false
    fmt.Println("Turning tv off")
}
```

### onCommand.go / offCommand.go - 具体命令

```go
package main

// 开机命令
type OnCommand struct {
    device Device
}

func (c *OnCommand) execute() {
    c.device.on()
}

// 关机命令
type OffCommand struct {
    device Device
}

func (c *OffCommand) execute() {
    c.device.off()
}
```

### button.go - 调用者

```go
package main

type Button struct {
    command Command
}

func (b *Button) press() {
    b.command.execute()
}
```

### main.go

```go
package main

func main() {
    tv := &Tv{}

    onCommand := &OnCommand{device: tv}
    offCommand := &OffCommand{device: tv}

    onButton := &Button{command: onCommand}
    onButton.press()

    offButton := &Button{command: offCommand}
    offButton.press()
}
```

**输出**:

```text
Turning tv on
Turning tv off
```

---

### 15. 迭代器模式 (Iterator)

**意图**: 允许顺序遍历复杂数据结构，而不暴露其内部细节。

**示例**: 遍历用户集合。

### collection.go / iterator.go - 集合与迭代器接口

```go
package main

// 集合接口
type Collection interface {
    createIterator() Iterator
}

// 迭代器接口
type Iterator interface {
    hasNext() bool
    getNext() *User
}
```

### userCollection.go / userIterator.go - 具体实现

```go
package main

// 用户集合
type UserCollection struct {
    users []*User
}

func (u *UserCollection) createIterator() Iterator {
    return &UserIterator{users: u.users}
}

// 用户迭代器
type UserIterator struct {
    index int
    users []*User
}

func (u *UserIterator) hasNext() bool {
    if u.index < len(u.users) {
        return true
    }
    return false
}

func (u *UserIterator) getNext() *User {
    if u.hasNext() {
        user := u.users[u.index]
        u.index++
        return user
    }
    return nil
}
```

### user.go

```go
package main

type User struct {
    name string
    age  int
}
```

### main.go

```go
package main

import "fmt"

func main() {
    user1 := &User{name: "a", age: 30}
    user2 := &User{name: "b", age: 20}

    userCollection := &UserCollection{users: []*User{user1, user2}}
    iterator := userCollection.createIterator()

    for iterator.hasNext() {
        user := iterator.getNext()
        fmt.Printf("User is %+v
", user)
    }
}
```

**输出**:

```text
User is &{name:a age:30}
User is &{name:b age:20}
```

---

### 16. 中介者模式 (Mediator)

**意图**: 通过使组件通过特殊的中介者对象间接通信，减少程序组件之间的耦合。

**示例**: 火车站交通系统。列车之间不直接通信，而是通过 `stationManager`（中介者）协调站台使用。

### train.go / mediator.go - 组件与中介者接口

```go
package main

// 列车接口
type Train interface {
    arrive()
    depart()
    permitArrival()
}

// 中介者接口
type Mediator interface {
    canArrive(Train) bool
    notifyAboutDeparture()
}
```

### passengerTrain.go / freightTrain.go - 具体组件

```go
package main

import "fmt"

// 客运列车
type PassengerTrain struct {
    mediator Mediator
}

func (g *PassengerTrain) arrive() {
    if !g.mediator.canArrive(g) {
        fmt.Println("PassengerTrain: Arrival blocked, waiting")
        return
    }
    fmt.Println("PassengerTrain: Arrived")
}

func (g *PassengerTrain) depart() {
    fmt.Println("PassengerTrain: Leaving")
    g.mediator.notifyAboutDeparture()
}

func (g *PassengerTrain) permitArrival() {
    fmt.Println("PassengerTrain: Arrival permitted, arriving")
    g.arrive()
}

// 货运列车
type FreightTrain struct {
    mediator Mediator
}

func (g *FreightTrain) arrive() {
    if !g.mediator.canArrive(g) {
        fmt.Println("FreightTrain: Arrival blocked, waiting")
        return
    }
    fmt.Println("FreightTrain: Arrived")
}

func (g *FreightTrain) depart() {
    fmt.Println("FreightTrain: Leaving")
    g.mediator.notifyAboutDeparture()
}

func (g *FreightTrain) permitArrival() {
    fmt.Println("FreightTrain: Arrival permitted")
    g.arrive()
}
```

### stationManager.go - 具体中介者

```go
package main

type StationManager struct {
    isPlatformFree bool
    trainQueue     []Train
}

func newStationManger() *StationManager {
    return &StationManager{isPlatformFree: true}
}

func (s *StationManager) canArrive(t Train) bool {
    if s.isPlatformFree {
        s.isPlatformFree = false
        return true
    }
    s.trainQueue = append(s.trainQueue, t)
    return false
}

func (s *StationManager) notifyAboutDeparture() {
    if !s.isPlatformFree {
        s.isPlatformFree = true
    }
    if len(s.trainQueue) > 0 {
        firstTrainInQueue := s.trainQueue[0]
        s.trainQueue = s.trainQueue[1:]
        firstTrainInQueue.permitArrival()
    }
}
```

### main.go

```go
package main

func main() {
    stationManager := newStationManger()

    passengerTrain := &PassengerTrain{mediator: stationManager}
    freightTrain := &FreightTrain{mediator: stationManager}

    passengerTrain.arrive()
    freightTrain.arrive()
    passengerTrain.depart()
}
```

**输出**:

```text
PassengerTrain: Arrived
FreightTrain: Arrival blocked, waiting
PassengerTrain: Leaving
FreightTrain: Arrival permitted
FreightTrain: Arrived
```

---

### 17. 备忘录模式 (Memento)

**意图**: 允许在不暴露对象实现细节的情况下捕获和恢复对象的内部状态。

**示例**: 实现对象的撤销-重做操作。

### originator.go - 原发器

```go
package main

type Originator struct {
    state string
}

func (e *Originator) createMemento() *Memento {
    return &Memento{state: e.state}
}

func (e *Originator) restoreMemento(m *Memento) {
    e.state = m.getSavedState()
}

func (e *Originator) setState(state string) {
    e.state = state
}

func (e *Originator) getState() string {
    return e.state
}
```

### memento.go - 备忘录

```go
package main

type Memento struct {
    state string
}

func (m *Memento) getSavedState() string {
    return m.state
}
```

### caretaker.go - 负责人

```go
package main

type Caretaker struct {
    mementoArray []*Memento
}

func (c *Caretaker) addMemento(m *Memento) {
    c.mementoArray = append(c.mementoArray, m)
}

func (c *Caretaker) getMemento(index int) *Memento {
    return c.mementoArray[index]
}
```

### main.go

```go
package main

import "fmt"

func main() {
    caretaker := &Caretaker{mementoArray: make([]*Memento, 0)}
    originator := &Originator{state: "A"}

    fmt.Printf("Originator Current State: %s
", originator.getState())
    caretaker.addMemento(originator.createMemento())

    originator.setState("B")
    fmt.Printf("Originator Current State: %s
", originator.getState())
    caretaker.addMemento(originator.createMemento())

    originator.setState("C")
    fmt.Printf("Originator Current State: %s
", originator.getState())
    caretaker.addMemento(originator.createMemento())

    originator.restoreMemento(caretaker.getMemento(1))
    fmt.Printf("Restored to State: %s
", originator.getState())

    originator.restoreMemento(caretaker.getMemento(0))
    fmt.Printf("Restored to State: %s
", originator.getState())
}
```

**输出**:

```text
Originator Current State: A
Originator Current State: B
Originator Current State: C
Restored to State: B
Restored to State: A
```

---

### 18. 观察者模式 (Observer)

**意图**: 允许你定义一种订阅机制，在对象事件发生时通知多个"观察"该对象的其他对象。

**示例**: 电商网站中，商品缺货时，订阅该商品的客户会收到通知。

### subject.go / observer.go - 主题与观察者接口

```go
package main

// 主题接口
type Subject interface {
    register(observer Observer)
    deregister(observer Observer)
    notifyAll()
}

// 观察者接口
type Observer interface {
    update(string)
    getID() string
}
```

### item.go - 具体主题

```go
package main

import "fmt"

type Item struct {
    observerList []Observer
    name         string
    inStock      bool
}

func newItem(name string) *Item {
    return &Item{name: name}
}

func (i *Item) updateAvailability() {
    fmt.Printf("Item %s is now in stock
", i.name)
    i.inStock = true
    i.notifyAll()
}

func (i *Item) register(o Observer) {
    i.observerList = append(i.observerList, o)
}

func (i *Item) deregister(o Observer) {
    i.observerList = removeFromslice(i.observerList, o)
}

func (i *Item) notifyAll() {
    for _, observer := range i.observerList {
        observer.update(i.name)
    }
}

func removeFromslice(observerList []Observer, observerToRemove Observer) []Observer {
    observerListLength := len(observerList)
    for i, observer := range observerList {
        if observerToRemove.getID() == observer.getID() {
            observerList[observerListLength-1], observerList[i] = observerList[i], observerList[observerListLength-1]
            return observerList[:observerListLength-1]
        }
    }
    return observerList
}
```

### customer.go - 具体观察者

```go
package main

import "fmt"

type Customer struct {
    id string
}

func (c *Customer) update(itemName string) {
    fmt.Printf("Sending email to customer %s for item %s
", c.id, itemName)
}

func (c *Customer) getID() string {
    return c.id
}
```

### main.go

```go
package main

func main() {
    shirtItem := newItem("Nike Shirt")

    observerFirst := &Customer{id: "abc@gmail.com"}
    observerSecond := &Customer{id: "xyz@gmail.com"}

    shirtItem.register(observerFirst)
    shirtItem.register(observerSecond)

    shirtItem.updateAvailability()
}
```

**输出**:

```text
Item Nike Shirt is now in stock
Sending email to customer abc@gmail.com for item Nike Shirt
Sending email to customer xyz@gmail.com for item Nike Shirt
```

---

### 19. 状态模式 (State)

**意图**: 允许对象在其内部状态改变时改变其行为。

**示例**: 自动售货机有四种状态：有商品、无商品、请求商品、已投币。根据当前状态，机器对相同请求的行为不同。

### state.go - 状态接口

```go
package main

type State interface {
    addItem(int) error
    requestItem() error
    insertMoney(money int) error
    dispenseItem() error
}
```

### vendingMachine.go - 上下文

```go
package main

import "fmt"

type VendingMachine struct {
    hasItem       State
    itemRequested State
    hasMoney      State
    noItem        State
    currentState  State
    itemCount     int
    itemPrice     int
}

func newVendingMachine(itemCount, itemPrice int) *VendingMachine {
    v := &VendingMachine{itemCount: itemCount, itemPrice: itemPrice}
    hasItemState := &HasItemState{vendingMachine: v}
    itemRequestedState := &ItemRequestedState{vendingMachine: v}
    hasMoneyState := &HasMoneyState{vendingMachine: v}
    noItemState := &NoItemState{vendingMachine: v}

    v.setState(hasItemState)
    v.hasItem = hasItemState
    v.itemRequested = itemRequestedState
    v.hasMoney = hasMoneyState
    v.noItem = noItemState
    return v
}

func (v *VendingMachine) requestItem() error   { return v.currentState.requestItem() }
func (v *VendingMachine) addItem(count int) error { return v.currentState.addItem(count) }
func (v *VendingMachine) insertMoney(money int) error { return v.currentState.insertMoney(money) }
func (v *VendingMachine) dispenseItem() error  { return v.currentState.dispenseItem() }
func (v *VendingMachine) setState(s State)     { v.currentState = s }

func (v *VendingMachine) incrementItemCount(count int) {
    fmt.Printf("Adding %d items
", count)
    v.itemCount = v.itemCount + count
}
```

### 具体状态

```go
package main

import "fmt"

// 无商品状态
type NoItemState struct {
    vendingMachine *VendingMachine
}

func (i *NoItemState) requestItem() error {
    return fmt.Errorf("Item out of stock")
}
func (i *NoItemState) addItem(count int) error {
    i.vendingMachine.incrementItemCount(count)
    i.vendingMachine.setState(i.vendingMachine.hasItem)
    return nil
}
func (i *NoItemState) insertMoney(money int) error {
    return fmt.Errorf("Item out of stock")
}
func (i *NoItemState) dispenseItem() error {
    return fmt.Errorf("Item out of stock")
}

// 有商品状态
type HasItemState struct {
    vendingMachine *VendingMachine
}

func (i *HasItemState) requestItem() error {
    if i.vendingMachine.itemCount == 0 {
        i.vendingMachine.setState(i.vendingMachine.noItem)
        return fmt.Errorf("No item present")
    }
    fmt.Printf("Item requestd
")
    i.vendingMachine.setState(i.vendingMachine.itemRequested)
    return nil
}
func (i *HasItemState) addItem(count int) error {
    fmt.Printf("%d items added
", count)
    i.vendingMachine.incrementItemCount(count)
    return nil
}
func (i *HasItemState) insertMoney(money int) error {
    return fmt.Errorf("Please select item first")
}
func (i *HasItemState) dispenseItem() error {
    return fmt.Errorf("Please select item first")
}

// 请求商品状态
type ItemRequestedState struct {
    vendingMachine *VendingMachine
}

func (i *ItemRequestedState) requestItem() error {
    return fmt.Errorf("Item already requested")
}
func (i *ItemRequestedState) addItem(count int) error {
    return fmt.Errorf("Item Dispense in progress")
}
func (i *ItemRequestedState) insertMoney(money int) error {
    if money < i.vendingMachine.itemPrice {
        return fmt.Errorf("Inserted money is less. Please insert %d", i.vendingMachine.itemPrice)
    }
    fmt.Println("Money entered is ok")
    i.vendingMachine.setState(i.vendingMachine.hasMoney)
    return nil
}
func (i *ItemRequestedState) dispenseItem() error {
    return fmt.Errorf("Please insert money first")
}

// 已投币状态
type HasMoneyState struct {
    vendingMachine *VendingMachine
}

func (i *HasMoneyState) requestItem() error {
    return fmt.Errorf("Item dispense in progress")
}
func (i *HasMoneyState) addItem(count int) error {
    return fmt.Errorf("Item dispense in progress")
}
func (i *HasMoneyState) insertMoney(money int) error {
    return fmt.Errorf("Item out of stock")
}
func (i *HasMoneyState) dispenseItem() error {
    fmt.Println("Dispensing Item")
    i.vendingMachine.itemCount = i.vendingMachine.itemCount - 1
    if i.vendingMachine.itemCount == 0 {
        i.vendingMachine.setState(i.vendingMachine.noItem)
    } else {
        i.vendingMachine.setState(i.vendingMachine.hasItem)
    }
    return nil
}
```

### main.go

```go
package main

import (
    "fmt"
    "log"
)

func main() {
    vendingMachine := newVendingMachine(1, 10)

    err := vendingMachine.requestItem()
    if err != nil {
        log.Fatalf(err.Error())
    }

    err = vendingMachine.insertMoney(10)
    if err != nil {
        log.Fatalf(err.Error())
    }

    err = vendingMachine.dispenseItem()
    if err != nil {
        log.Fatalf(err.Error())
    }

    fmt.Println()

    err = vendingMachine.addItem(2)
    if err != nil {
        log.Fatalf(err.Error())
    }

    fmt.Println()

    err = vendingMachine.requestItem()
    if err != nil {
        log.Fatalf(err.Error())
    }

    err = vendingMachine.insertMoney(10)
    if err != nil {
        log.Fatalf(err.Error())
    }

    err = vendingMachine.dispenseItem()
    if err != nil {
        log.Fatalf(err.Error())
    }
}
```

**输出**:

```text
Item requestd
Money entered is ok
Dispensing Item

Adding 2 items

Item requestd
Money entered is ok
Dispensing Item
```

---

### 20. 策略模式 (Strategy)

**意图**: 允许你定义一系列算法，将每个算法放入单独的类中，并使它们可以互换。

**示例**: 内存缓存达到最大大小时，可以通过多种算法（LRU、FIFO、LFU）驱逐条目。策略模式将缓存类与这些算法解耦。

### evictionAlgo.go - 策略接口

```go
package main

type EvictionAlgo interface {
    evict(c *Cache)
}
```

### fifo.go / lru.go / lfu.go - 具体策略

```go
package main

import "fmt"

// FIFO 策略
type Fifo struct{}

func (l *Fifo) evict(c *Cache) {
    fmt.Println("Evicting by fifo strtegy")
}

// LRU 策略
type Lru struct{}

func (l *Lru) evict(c *Cache) {
    fmt.Println("Evicting by lru strtegy")
}

// LFU 策略
type Lfu struct{}

func (l *Lfu) evict(c *Cache) {
    fmt.Println("Evicting by lfu strtegy")
}
```

### cache.go - 上下文

```go
package main

type Cache struct {
    storage      map[string]string
    evictionAlgo EvictionAlgo
    capacity     int
    maxCapacity  int
}

func initCache(e EvictionAlgo) *Cache {
    storage := make(map[string]string)
    return &Cache{
        storage:      storage,
        evictionAlgo: e,
        capacity:     0,
        maxCapacity:  2,
    }
}

func (c *Cache) setEvictionAlgo(e EvictionAlgo) {
    c.evictionAlgo = e
}

func (c *Cache) add(key, value string) {
    if c.capacity == c.maxCapacity {
        c.evict()
    }
    c.capacity++
    c.storage[key] = value
}

func (c *Cache) get(key string) {
    delete(c.storage, key)
}

func (c *Cache) evict() {
    c.evictionAlgo.evict(c)
    c.capacity--
}
```

### main.go

```go
package main

func main() {
    lfu := &Lfu{}
    cache := initCache(lfu)

    cache.add("a", "1")
    cache.add("b", "2")
    cache.add("c", "3")

    lru := &Lru{}
    cache.setEvictionAlgo(lru)
    cache.add("d", "4")

    fifo := &Fifo{}
    cache.setEvictionAlgo(fifo)
    cache.add("e", "5")
}
```

**输出**:

```text
Evicting by lfu strtegy
Evicting by lru strtegy
Evicting by fifo strtegy
```

---

### 21. 模板方法模式 (Template Method)

**意图**: 允许你在基类中定义算法的骨架，并让子类覆盖特定步骤而不改变算法的结构。

**示例**: 一次性密码（OTP）功能。无论是短信 OTP 还是邮件 OTP，整个 OTP 流程都相同：生成随机数字 -\> 保存到缓存 -\> 准备内容 -\> 发送通知。

### otp.go - 模板方法

```go
package main

type IOtp interface {
    genRandomOTP(int) string
    saveOTPCache(string)
    getMessage(string) string
    sendNotification(string) error
}

type Otp struct {
    iOtp IOtp
}

func (o *Otp) genAndSendOTP(otpLength int) error {
    otp := o.iOtp.genRandomOTP(otpLength)
    o.iOtp.saveOTPCache(otp)
    message := o.iOtp.getMessage(otp)
    err := o.iOtp.sendNotification(message)
    if err != nil {
        return err
    }
    return nil
}
```

### sms.go / email.go - 具体实现

```go
package main

import "fmt"

// SMS OTP
type Sms struct {
    Otp
}

func (s *Sms) genRandomOTP(len int) string {
    randomOTP := "1234"
    fmt.Printf("SMS: generating random otp %s
", randomOTP)
    return randomOTP
}

func (s *Sms) saveOTPCache(otp string) {
    fmt.Printf("SMS: saving otp: %s to cache
", otp)
}

func (s *Sms) getMessage(otp string) string {
    return "SMS OTP for login is " + otp
}

func (s *Sms) sendNotification(message string) error {
    fmt.Printf("SMS: sending sms: %s
", message)
    return nil
}

// Email OTP
type Email struct {
    Otp
}

func (s *Email) genRandomOTP(len int) string {
    randomOTP := "1234"
    fmt.Printf("EMAIL: generating random otp %s
", randomOTP)
    return randomOTP
}

func (s *Email) saveOTPCache(otp string) {
    fmt.Printf("EMAIL: saving otp: %s to cache
", otp)
}

func (s *Email) getMessage(otp string) string {
    return "EMAIL OTP for login is " + otp
}

func (s *Email) sendNotification(message string) error {
    fmt.Printf("EMAIL: sending email: %s
", message)
    return nil
}
```

### main.go

```go
package main

import "fmt"

func main() {
    smsOTP := &Sms{}
    o := Otp{iOtp: smsOTP}
    o.genAndSendOTP(4)

    fmt.Println("")
    emailOTP := &Email{}
    o = Otp{iOtp: emailOTP}
    o.genAndSendOTP(4)
}
```

**输出**:

```text
SMS: generating random otp 1234
SMS: saving otp: 1234 to cache
SMS: sending sms: SMS OTP for login is 1234

EMAIL: generating random otp 1234
EMAIL: saving otp: 1234 to cache
EMAIL: sending email: EMAIL OTP for login is 1234
```

---

### 22. 访问者模式 (Visitor)

**意图**: 允许你在不修改现有类层次结构的情况下向其添加新行为。

**示例**: 维护一个包含不同形状（正方形、圆形、矩形）的图形库。需要添加 `getArea` 行为，但不想修改现有形状类。

**Go 注意点**: Go 不支持方法重载，因此访问者接口需要为每种形状定义不同的方法名（如 `visitForSquare`、`visitForCircle`）。

### shape.go - 元素接口

```go
package main

type Shape interface {
    getType() string
    accept(Visitor)
}
```

### square.go / circle.go / rectangle.go - 具体元素

```go
package main

// 正方形
type Square struct {
    side int
}

func (s *Square) accept(v Visitor) {
    v.visitForSquare(s)
}

func (s *Square) getType() string {
    return "Square"
}

// 圆形
type Circle struct {
    radius int
}

func (c *Circle) accept(v Visitor) {
    v.visitForCircle(c)
}

func (c *Circle) getType() string {
    return "Circle"
}

// 矩形
type Rectangle struct {
    l int
    b int
}

func (t *Rectangle) accept(v Visitor) {
    v.visitForrectangle(t)
}

func (t *Rectangle) getType() string {
    return "rectangle"
}
```

### visitor.go - 访问者接口

```go
package main

type Visitor interface {
    visitForSquare(*Square)
    visitForCircle(*Circle)
    visitForrectangle(*Rectangle)
}
```

### areaCalculator.go / middleCoordinates.go - 具体访问者

```go
package main

import "fmt"

// 面积计算器
type AreaCalculator struct {
    area int
}

func (a *AreaCalculator) visitForSquare(s *Square) {
    fmt.Println("Calculating area for square")
}

func (a *AreaCalculator) visitForCircle(s *Circle) {
    fmt.Println("Calculating area for circle")
}

func (a *AreaCalculator) visitForrectangle(s *Rectangle) {
    fmt.Println("Calculating area for rectangle")
}

// 中点坐标计算器
type MiddleCoordinates struct {
    x int
    y int
}

func (a *MiddleCoordinates) visitForSquare(s *Square) {
    fmt.Println("Calculating middle point coordinates for square")
}

func (a *MiddleCoordinates) visitForCircle(c *Circle) {
    fmt.Println("Calculating middle point coordinates for circle")
}

func (a *MiddleCoordinates) visitForrectangle(t *Rectangle) {
    fmt.Println("Calculating middle point coordinates for rectangle")
}
```

### main.go

```go
package main

import "fmt"

func main() {
    square := &Square{side: 2}
    circle := &Circle{radius: 3}
    rectangle := &Rectangle{l: 2, b: 3}

    areaCalculator := &AreaCalculator{}

    square.accept(areaCalculator)
    circle.accept(areaCalculator)
    rectangle.accept(areaCalculator)

    fmt.Println()
    middleCoordinates := &MiddleCoordinates{}
    square.accept(middleCoordinates)
    circle.accept(middleCoordinates)
    rectangle.accept(middleCoordinates)
}
```

**输出**:

```text
Calculating area for square
Calculating area for circle
Calculating area for rectangle

Calculating middle point coordinates for square
Calculating middle point coordinates for circle
Calculating middle point coordinates for rectangle
```

---

## 总结

| 类型 | 模式 | 核心思想 |
| --- | --- | --- |
| **创建型** | Singleton | 全局唯一实例 |
|  | Factory Method | 由工厂决定创建哪种产品 |
|  | Abstract Factory | 创建相关对象家族 |
|  | Builder | 逐步构建复杂对象 |
|  | Prototype | 克隆现有对象 |
| **结构型** | Adapter | 接口适配 |
|  | Bridge | 抽象与实现分离 |
|  | Composite | 树形结构统一处理 |
|  | Decorator | 动态添加行为 |
|  | Facade | 简化复杂系统接口 |
|  | Flyweight | 共享对象减少内存 |
|  | Proxy | 控制对象访问 |
| **行为型** | Chain of Responsibility | 请求沿链传递 |
|  | Command | 将请求封装为对象 |
|  | Iterator | 统一遍历接口 |
|  | Mediator | 组件通过中介通信 |
|  | Memento | 保存和恢复状态 |
|  | Observer | 订阅-通知机制 |
|  | State | 状态决定行为 |
|  | Strategy | 算法可互换 |
|  | Template Method | 算法骨架固定，步骤可变 |
|  | Visitor | 为类层次结构添加新行为 |

---

> \*\*参考\*\*: 本文所有代码示例整理自 \[Refactoring.Guru - Design Patterns in Go\](https://refactoring.guru/design-patterns/go)，原始代码仓库位于 \[GitHub - RefactoringGuru/design-patterns-go\](https://github.com/RefactoringGuru/design-patterns-go)
