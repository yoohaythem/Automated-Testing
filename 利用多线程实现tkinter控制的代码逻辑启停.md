### 利用多线程实现tkinter控制的代码逻辑启停

#### 启动

在利用tkinter控制一段运行时间较长的代码运行时，若是简单的将后端代码封装成函数，并与前端tkinter一起放在主线程中运行，则会导致tkinter界面在后端函数运行之后卡死。所以需要通过如下方法，将代码单独抽出来成为一个独立子线程来运行。

```python
'''界面上点击运行之后，开始运行的函数'''
def _start():
    
    # tkinter界面上的展示变化逻辑
    view(xxx)

    # 后端代码的逻辑函数
    def run():

        func1(xxx)  # 后端执行函数1
        func2(xxx)  # 后端执行函数2
        ……
        funcN(xxx)  # 后端执行函数n

	
    task = Thread(target=run)
    task.start()
```


  
#### 停止

有时启动代码之后，发现需要临时停止这个线程。Python 的多线程模块 threading 并没有直接提供一种有效的方法来强制终止线程。

下面通过_async_raise 和 stop_thread 函数，使用基于底层的方式，利用异常来中断线程的执行。

```python
'''下面三个是线程停止逻辑'''
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


'''界面上点击停止之后，开始运行的函数'''
def _stop():
    
    view1(xxx)   # tkinter界面上的展示变化逻辑
    
    try:
        stop_thread(task)
    except BaseException:
        pass
    
   view2(xxx)   # tkinter界面上的展示变化逻辑
```
  
### 机理解释：

**_async_raise 函数：** 这个函数用于抛出一个指定类型的异常（exctype），以中断线程的正常执行。它的参数包括线程标识符（tid）和异常类型（exctype）。
每个线程在Python解释器中都有一个Thread State，它是一个包含线程执行状态和其他信息的数据结构。当使用 _async_raise 函数抛出异常时，实际上是在修改目标线程的Thread State，使其在下一次检查线程状态时抛出相应的异常。

**stop_thread 函数：** 这个函数调用 _async_raise 函数，将一个 SystemExit 异常抛给目标线程。这将强制线程在执行到异常处理机制时终止。

**_stop 函数：** 当用户在界面上点击停止按钮时，您调用了 _stop 函数。

### 潜在问题：
1. **不稳定性：** 强制中断线程可能会导致Python解释器内部状态的不稳定，从而影响程序的正确性。
2. **资源泄漏：** 由于线程被强制中断，线程内部的清理和资源释放操作可能无法正常执行，导致资源泄漏。
3. **数据一致性：** 如果线程在执行关键任务（如文件写入、数据库操作等）时被强制中断，可能导致数据不一致或损坏。
4. **竞态条件：** 修改线程状态可能会引发竞态条件，导致线程同步问题。
