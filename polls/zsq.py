# class My:
#     def __init__(self):
#         self.tags = {}
#         self.filters = {}
#
#     def tag(self, name=None, compile_function=None):
#         if name is None and compile_function is None:
#             # @register.tag()
#             return self.tag_function
#         elif name is not None and compile_function is None:
#             if callable(name):
#                 # @register.tag
#                 return self.tag_function(name)
#             else:
#                 # @register.tag('somename') or @register.tag(name='somename')
#                 def dec(func):
#                     return self.tag(name, func)
#
#                 return dec
#         elif name is not None and compile_function is not None:
#             # register.tag('somename', somefunc)
#             self.tags[name] = compile_function
#             return compile_function
#         else:
#             raise ValueError(
#                 "Unsupported arguments to Library.tag: (%r, %r)" %
#                 (name, compile_function),
#             )
#
#     def tag_function(self, func):
#         self.tags[getattr(func, "_decorated_function", func).__name__] = func
#         return func
#
#     def filter(self, name=None, filter_func=None, **flags):
#         """
#         filter 装饰器
#         :param name: 过滤器名称，目的是适应一些关键字名不能作为函数名
#         :param filter_func: filter 的处理函数
#         :param flags: 关键字参数
#         :return: 传入的编译函数
#
#         Register a callable as a template filter. Example:
#
#         @register.filter
#         def lower(value):
#             return value.lower()
#         """
#         # filter 装饰器对装饰器的所有书写格式都进行了处理，可以作为理解装饰器用法的很好的案例
#         # 共考虑到装饰器的三种书写格式
#         if name is None and filter_func is None:
#             # 1. @register.filter()
#             # 解释：
#             # a. 调用filter()函数，传入的参数都是默认值
#             # b. 返回函数filter_func的引用，注意不是调用函数的结果
#             # c. 因为filter_func需要flags参数，所以这里采用闭包，现将flags传入
#             # c. 执行filter_func，被包装的函数作为其参数
#             def dec(func):
#                 return self.filter_function(func, **flags)
#             return dec
#         elif name is not None and filter_func is None:
#             if callable(name):
#                 # 2. @register.filter
#                 return self.filter_function(name, **flags)
#             else:
#                 # @register.filter('somename') or @register.filter(name='somename')
#                 def dec(func):
#                     return self.filter(name, func, **flags)
#                 return dec
#         elif name is not None and filter_func is not None:
#             # register.filter('somename', somefunc)
#             self.filters[name] = filter_func
#             for attr in ('expects_localtime', 'is_safe', 'needs_autoescape'):
#                 if attr in flags:
#                     value = flags[attr]
#                     # set the flag on the filter for FilterExpression.resolve
#                     setattr(filter_func, attr, value)
#                     # set the flag on the innermost decorated function
#                     # for decorators that need it, e.g. stringfilter
#                     if hasattr(filter_func, "_decorated_function"):
#                         setattr(filter_func._decorated_function, attr, value)
#             filter_func._filter_name = name
#             return filter_func
#         else:
#             raise ValueError(
#                 "Unsupported arguments to Library.filter: (%r, %r)" %
#                 (name, filter_func),
#             )
#
#     def filter_function(self, func, **flags):
#         name = getattr(func, "_decorated_function", func).__name__
#         return self.filter(name, func, **flags)
#
#
# register = My()
#
#
# @register.filter
# def do_for(parser, token):
#     return "do_for"
#
#
# @register.filter()
# def do_if(parser, token):
#     return "do_if"
#
#
# @register.filter('else')
# def do_else(parser, token):
#     return "do_else"
#
#
# @register.filter(is_safe=True)
# def do_safe(parser, token):
#     return "do_safe"
#
#
# print(register.filters, register.tags)


# 单例装饰器

# 保存单例的实例，key: cls_name; value: instance
instances = {}


def singleton(cls):
    def get_instance(*args, **kwargs):
        cls_name = cls.__name__
        if cls_name not in instances:
            instance = cls(*args, **kwargs)
            instances[cls_name] = instance
        return instances[cls_name]
    return get_instance


@singleton
class User:
    def __init__(self, name):
        self.name = name


u1 = User('jack')
u1.age = 20

u2 = User('maggie')
u2.name