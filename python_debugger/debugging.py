# for tkinter it is best to use multiprocessing instead of threads
import tkinter
import asyncio
import threading
import multiprocessing
import sys
import inspect
import queue
import time
def trace_lines(frame, event, arg):
    """Handler that executes with every line of code"""

    # We only care about *line* and *return* events
    if event != 'line' and event != 'return':
        return

    # Get a reference to the code object and source
    co = frame.f_code
    print(co)
    source = inspect.getsourcelines(co)[0]

    # Send the UI information on the code we're currently executing
#     trace_lines.applicationq.put({ "co": { "file": co.co_filename,
#                                    "name": co.co_name,
#                                    "lineno": str(frame.f_lineno)
#                                    },
#                           "frame": { "lineno": frame.f_lineno,
#                                       "firstlineno": co.co_firstlineno,
#                                       "locals": str(frame.f_locals),
#                                       "source": source
#                                       },
#                            'trace': 'line'
#                           })

    # Wait for a debug command
    file= open("debugging.py","r")
    for index, line in enumerate(file):
        if index == frame.f_lineno-1:
            print(line)
            trace_lines.applicationq.put(line)
    file.close()
    while trace_lines.debugq.empty():
        time.sleep(0.1)
        print("empty")
    cmd = trace_lines.debugq.get()

    if cmd == "step":
        # If stepping through code, return this handler
        return trace_lines

    if cmd == "stop":
        # If stopping execution, raise an exception
        raise StopExecution()

    elif cmd == 'over':
        # If stepping out of code, return the function callback
        return trace_calls

    # print("CODE")
    # print("co_argcount " + str(co.co_argcount))
    # print("co_cellvars " + str(co.co_cellvars))
    # print("co_code " + str(co.co_code))
    # print("co_consts " + str(co.co_consts))
    # print("co_filename " + str(co.co_filename))
    # print("co_firstlineno " + str(co.co_firstlineno))
    # print("co_flags " + str(co.co_flags))
    # print("co_freevars " + str(co.co_freevars))
    # print("co_kwonlyargcount " + str(co.co_kwonlyargcount))
    # print("co_lnotab " + str(co.co_lnotab))
    # print("co_name " + str(co.co_name))
    # print("co_names " + str(co.co_names))
    # print("co_nlocals " + str(co.co_nlocals))
    # print("co_stacksize " + str(co.co_stacksize))
    # print("co_varnames " + str(co.co_varnames))
    #
    # print("FRAME")
    # print("clear " + str(frame.clear))
    # # print("f_back " + str(frame.f_back))
    # # print("f_builtins " + str(frame.f_builtins))
    # # print("f_code " + str(frame.f_code))
    # # print("f_globals " + str(frame.f_globals))
    # print("f_lasti " + str(frame.f_lasti))
    # print("f_lineno " + str(frame.f_lineno))
    # print("f_locals " + str(frame.f_locals))
    # print("f_trace " + str(frame.f_trace))

class StopExecution(Exception):
    """Custom exception for stopping code execution"""

    pass

def trace_calls(frame, event, arg):
    """Handler that executes on every invocation of a function call"""

    # We only care about function call events
    if event != 'call':
        return

    # Get a reference for the code object and function name
    co = frame.f_code
    func_name = co.co_name

    # Only react to the functions we care about
    if func_name in ['sample', 'xyz']:
        # Get the source code from the code object
        source = inspect.getsourcelines(co)[0]

        # Tell the UI to perform an update
#         trace_lines.applicationq.put({ "co": { "file": co.co_filename,
#                                        "name": co.co_name,
#                                        "lineno": str(frame.f_lineno)
#                                        },
#                               "frame": { "lineno": frame.f_lineno,
#                                           "firstlineno": co.co_firstlineno,
#                                           "locals": str(frame.f_locals),
#                                           "source": source
#                                           },
#                               "trace": "call"
#                               })
#         
#         print('Call to %s on line %s of %s' % (func_name, frame.f_lineno, co.co_filename))
        file= open("debugging.py","r")
        for index, line in enumerate(file): #index might start from zero
            if index == frame.f_lineno:
                print(line)
                trace_lines.applicationq.put(line)
        file.close()

        # Wait for a debug command (we stop here right before stepping into or out of a function)
        while trace_lines.debugq.empty():
            time.sleep(0.1)
            print("empty")
        cmd = trace_lines.debugq.get()
        
        print("success",cmd)
        if cmd == 'step':
            # If stepping into the function, return the line callback
            return trace_lines
        elif cmd == 'over':
            # If stepping over, then return nothing
            return

    return

def sample(a, b):
    """The sample function we'll be executing"""
    x = a + b
    y = x * 2
    print('Sample: ' + str(y))

def xyz(a):
    """Another sample function"""

    print("XYZ:" + str(a))




def debug(applicationq, debugq, fn, args):
   
    """Sets up and starts the debugger"""

    # Setup the debug and application queues as properties of the trace_lines functions
    trace_lines.debugq = debugq
    trace_lines.applicationq = applicationq

    # Enable debugging by setting the callback
    sys.settrace(trace_calls)

    # Execute the function we want to debug with its parameters
    fn(*args)

 
    
     
        




#  def mn(q1,q2):
#     def step():
#         q1.put("step")
#         print("put")
#     root= tkinter.Tk()
#     time.sleep(1)
#     button = tkinter.Button(root,text="step")
#     button["command"] = step
#     button.pack()
#     root.mainloop()
class GuiApp(object):
    def __init__(self,debugq, applicationq):
        self.root = tkinter.Tk()
        self.root.geometry('300x100')
        self.debugq= debugq
        self.btn = tkinter.Button(self.root,text= "step")
        self.btn["command"]= self.step
        self.btn.pack()
        self.text_wid = tkinter.Text(self.root,height=100,width=100)
        self.text_wid.pack()
        self.root.after(100,self.CheckQueuePoll,applicationq)


    def step(self):# have to put self -self not defined
        print(self.debugq)
        self.debugq.put("step")
    def CheckQueuePoll(self,c_queue):
        try:
            string = c_queue.get(0)
            self.text_wid.delete("1.0","end")
            
            self.text_wid.insert('end',string)
        except :
            pass
        finally:
            self.root.after(100, self.CheckQueuePoll, c_queue)

 
    
if __name__ == '__main__':
    debugq =multiprocessing.Queue()
    applicationq = multiprocessing.Queue()
    
    
#     root= tkinter.Tk()
#   
#     time.sleep(1)
#     button = tkinter.Button(root,text="step")
#     button["command"] = step
#     button.pack()
    debugq.cancel_join_thread() # or else thread that puts data will not term
    applicationq.cancel_join_thread()
    gui = GuiApp(debugq,applicationq)
    

  
#     p = multiprocessing.Process(target=mn, args=(debugq,applicationq,))
# you cannot pass tkinter objects to arguments
    debugprocess = multiprocessing.Process(target=debug, args=(applicationq, debugq, sample, (2, 3)))
    debugprocess.start()
    gui.root.mainloop()
#     p.start()

   
#     time.sleep(5)
#     while True:
#         count=0
#         if not trace_lines.applicationq.empty():
#             
#             if count == 0:
#                 print(trace_lines.applicationq.get())
   

    # Initialize the debug and application queues for passing messages
    

    # Create the debug process
   
   
