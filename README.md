## 自动化测试最佳实践
### Best practices for automated testing

---

### 介绍
#### introduction

本仓库是关于自动化测试实际使用场景中诞生的一些最佳实践的介绍，旨在提高工作效率，解决一些疑难问题。

This repository is about the introduction of some best practices in the actual use of automated testing, aimed at improving work efficiency and solving some difficult problems.

----

#### 1. 利用多线程实现tkinter控制的代码逻辑启停
##### Use multithreading to achieve code start or stop by tkinter


为了更好地将一些优秀的自动化测试代码提供给大家使用，往往需要对其封装成工具。
于是提升工具的易用性是一件非常重要的事情。

本实践解决了代码和工具界面的**冲突问题**，并做到了通过工具**控制代码启停**。


In order to better provide some excellent automated test code for everyone to use, it is often necessary to package it into a tool. Therefore, improving the usability of tools is a very important thing.

This practice solves the conflict problem between code and tool interface, and realizes the control of code start and stop through tool.

----
#### 2. 基于Python的多语言集成自动化测试框架编写
#### Multi-language integrated automated test framework based on Python
一个项目的产生，往往需要用到多种代码的结合，自动化代码编写也不例外。
如何在以Python为基础编写的自动化代码中，有效的结合其他语言，是值得考虑的问题。

The production of a project often requires the combination of a variety of codes, and automated code writing is no exception.
How to effectively combine other languages in automation code written on the basis of Python is worth considering.

----

#### 3. 基于类装饰器的用例自动化编写
#### Automated testing cases based on class decorators
复制粘贴的自动化代码是有害的。当这种代码变得越来越多，整个自动化项目的代码维护将变得异常困难。
如何解决这样的问题呢？基于类装饰器也许是一个很好的选择。

Copy and paste automation code is harmful. When this code becomes more and more numerous, it becomes extremely difficult to maintain the code for the entire automation project.
How to solve this problem? Class-based decorators might be a good choice.

----

#### 4. 深入理解Python反射机制，重构if...else...代码
#### In-depth understanding of Python reflection mechanism, refactoring if... else... 

if...else...也许是代码里不可或缺的判断，但如何更好地优化他们呢？这篇最佳实践或许能提供给你新的思路。

"if... else...", they may be essential judgments in the code, but how do you optimize them? This best practice article may give you some new ideas.




