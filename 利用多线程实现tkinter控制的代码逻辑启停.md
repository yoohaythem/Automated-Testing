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

若是启动代码之后，发现需要临时停止这个线程，由于python不支持线程的直接终止，所以可以通过下面这种模式来实施。

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
  
