import __main__ as _m
import settings as _s

todo = [] #[<timestamp>, <ref: func_name>, <bool: max overtime (if we missed calling it, should we still try now?) (if 0, always complete)>, <task id>,[*<args>],{"<kwarg name>":<kwarg val>}]
l=_m.threading.Lock()

disable_sched = False
funcs = {}

# try:
#     funcs["rem"]=_m.helper.remind_from_sched
# except:
#     _m.startup_errors.append(_m.log_format("error loading rem schedule function"))
#     disable_sched=True

try:
    funcs["daily_quote"]=_m.quotes_etc.quote_from_sched
except:
    _m.startup_errors.append(_m.log_format("error loading rem schedule function"))
    disable_sched=True

try:
    funcs["daily_activity_check"] = _m.tracker.check_from_sched
except:
    _m.startup_errors.append(_m.log_format("error loading activity schedule function"))
    disable_sched=True


async def run_task(func, *args, **kwargs):
    if _m.asyncio.iscoroutinefunction(func):
        await func(*args, **kwargs)
    else:
        func(*args, **kwargs)

def check(l):
    if not disable_sched:
        while True:
            l.acquire()
            todo = _m.perma_data["tasks"]
            l.release()
            _m.time.sleep(5)
            #print("checking tasks...")
            current_time = _m.time.time()
            l.acquire()
            tn = 0
            while tn < len(todo):
                # try:
                t = todo[tn]
                if t[0] <= current_time:
                    if t[2] == 0 or t[0] + t[2] >= current_time:
                        # Schedule the task on the main event loop
                        future = _m.asyncio.run_coroutine_threadsafe(
                            run_task(funcs[t[1]], *t[4], **t[5]), 
                            _m.client.loop
                        )
                        # Optionally wait for the result
                        try:
                            future.result(timeout=60)  # 60 second timeout
                        except Exception as e:
                            _m.schedule_errors.append(_m.log_format(f"Task execution failed: {e}"))
                    del todo[tn]
                    tn -= 1
                    _m.perma_data["tasks"] = todo
                    _m.helper.save_sticky_data("tasks")
                # except Exception as e:
                    # _m.schedule_errors.append(_m.log_format(f"scheduled task errored. task info: {t}, error: {e}"))
                tn += 1
            l.release()
        
        
def new_task(timestamp,ref_name,max_overtime=0,args=[],kwargs={}):
    global todo, l
    l.acquire()
    task_id = _m.uuid.uuid4()
    todo.append([timestamp,ref_name,max_overtime,task_id,args,kwargs])
    _m.perma_data["tasks"] = todo
    _m.helper.save_sticky_data("tasks")
    l.release()
    return task_id
    
def new_task_no_lock(timestamp,ref_name,max_overtime=0,args=[],kwargs={}):
    global todo, l
    #l.acquire()
    task_id = _m.uuid.uuid4()
    todo.append([timestamp,ref_name,max_overtime,task_id,args,kwargs])
    _m.perma_data["tasks"] = todo
    _m.helper.save_sticky_data("tasks")
    #l.release()
    return task_id
    
    
def start():
    if not disable_sched:
        global todo, l
        l.acquire()
        todo = _m.perma_data["tasks"]
        l.release()
        schedthread = _m.threading.Thread(target=check, args=[l])
        schedthread.daemon = True
        schedthread.start()
        #print(new_task(_m.time.time(),"meal"))
