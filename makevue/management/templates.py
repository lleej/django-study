import os
import posixpath
import shutil
import stat
from os import path

import django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Engine

import makevue

NAME_PROJECT_NAME = 'project_name'
NAME_PROJECT_VERSION = 'project_version'
NAME_PROJECT_AUTHOR = 'project_author'
VALUE_TEMPLATE_DIR = 'vue-template'
VALUE_TEMPLATE_SUFFIX = '-tpl'


class ProjectCommand(BaseCommand):
    """
    拷贝Vue-cli项目的模板文件，生成django后台对应的前端项目
    """
    def add_arguments(self, parser):
        """
        添加命令行参数
        1. Vue项目的名称
        2. Vue项目的目录（相对目录 / 绝对目录）
        """
        parser.add_argument('name', help='Vue项目名称.')
        parser.add_argument('directory', nargs='?', help='Optional destination directory')

    def handle(self, name, target=None, **options):
        """
        命令的处理函数
        :param name: Vue项目名称
        :param target: 项目目录，不提供默认为'getcwd()/../<name>'。可以是相对目录'.'、'..'，也可以使用~或~user等
        :param options: 可选项参数
        """
        self.verbosity = options['verbosity']
        self._validate_name(name)
        target_dir = self._validate_dir(target, name)
        # 生成上下文对象
        context = self._make_context(name, options)
        # 如果django未初始化，则执行初始化
        if not settings.configured:
            settings.configure()
            django.setup()
        # 生成模板文件目录
        template_dir = self._handle_template(VALUE_TEMPLATE_DIR)
        # 从项目模板目录中，拷贝文件到目标目录中
        # 将模板目录中的模板文件(-tpl结尾)中的变量替换为context中的内容
        self._copy_files(context, template_dir, target_dir)

    def _copy_files(self, context, template, target):
        """
        拷贝文件并更新模板文件变量
        :param context: 模板文件中变量的上下文
        :param template: 模板文件目录
        """
        # 模板文件根目录的长度
        prefix_length = len(template) + 1
        for root, dirs, files in os.walk(template):
            # 遍历模板目录下的所有子目录和文件
            relative_dir = root[prefix_length:]
            # 创建子目录
            if relative_dir:
                target_dir = path.join(target, relative_dir)
            else:
                target_dir = target
            if not path.exists(target_dir):
                os.makedirs(target_dir)
            # 拷贝文件
            for filename in files:
                is_template = False
                # 替换后缀是-tpl的文件
                src_path = path.join(root, filename)
                dst_path = path.join(target, relative_dir, filename)
                if dst_path.endswith(VALUE_TEMPLATE_SUFFIX):
                    dst_path = dst_path[:-len(VALUE_TEMPLATE_SUFFIX)]
                    is_template = True
                # 如果目标文件已经存在，不能覆盖
                if path.exists(dst_path):
                    raise CommandError("%s 文件已经存在。" % dst_path)
                # 只渲染模板文件
                if is_template:
                    with open(src_path, 'r', encoding='utf-8') as src_file:
                        content = src_file.read()
                    temp_obj = Engine().from_string(content)
                    content = temp_obj.render(context)
                    with open(dst_path, 'w', encoding='utf-8') as dst_file:
                        dst_file.write(content)
                else:
                    shutil.copyfile(src_path, dst_path)

                if self.verbosity >= 2:
                    self.stdout.write("创建了文件： %s\n" % dst_path)
                try:
                    shutil.copymode(src_path, dst_path)
                    self._make_writeable(dst_path)
                except OSError:
                    self.stderr.write("注意：无法设置 '%s'的访问权限." % new_path, self.style.NOTICE)

    def _handle_template(self, template):
        """
        得到模板文件存放的根目录
        :param template 模板子目录名，不包含根目录
        """
        ori_dir = path.join(makevue.__path__[0], template)
        if path.isdir(ori_dir):
            return ori_dir
        raise CommandError("没有找到项目模板文件的目录 '%s'." % ori_dir)

    def _make_context(self, name, options):
        """
        生成参数上下文对象
        :param name: 项目名称
        :param options: 命令行可选项
        :return: Context()
        """
        context = Context({
            **options,
            NAME_PROJECT_NAME: name,
            NAME_PROJECT_VERSION: makevue.__VERSION__,
            NAME_PROJECT_AUTHOR: makevue.__AUTHOR__,
        }, autoescape=False)
        return context

    def _validate_name(self, name):
        """
        检查项目名称是否有效
        1. 是否提供了一个名称
        2. 名称是否是一个有效的标识符
        如果验证失败，则抛出CommandError()
        """
        # 是否提供了项目名称
        if name is None:
            raise CommandError('必须提供一个项目名称.')
        # 是否是一个有效的名称
        if not name.isidentifier():
            raise CommandError("'%s' 不是有效的项目名称，确保输入的名称有效." % name)

    def _validate_dir(self, target, name):
        """
        检查目标目录是否有效
        1. 如果没有提供target，则使用默认的根目录。当前目录的上一级目录下的name目录
        2. 如果target是一个相对目录，则转换为一个绝对目录
        3. 检查目录是否存在
        任何异常都会抛出CommandError()错误
        """
        if target is None:
            # 没有提供target，则使用默认的目录，即django项目(manage.py所在)目录上级目录下的name目录
            top_dir = path.abspath(path.join(os.getcwd(), '..', name))
        elif '.' in target:
            # 是相对目录
            top_dir = path.abspath(path.join(os.getcwd(), target))
        else:
            # 绝对目录，有可能是~或者~user开头
            top_dir = path.abspath(path.expanduser(target))
        # 目录不能存在，因为有可能会覆盖以前的代码
        if path.exists(top_dir):
            raise CommandError("目标目录 '%s' 已存在！" % top_dir)
        # 保存到对象实例中
        return top_dir

    def _splitext(self, the_path):
        """
        Like os.path.splitext, but takes off .tar, too
        """
        base, ext = posixpath.splitext(the_path)
        if base.lower().endswith('.tar'):
            ext = base[-4:] + ext
            base = base[:-4]
        return base, ext

    def _make_writeable(self, filename):
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)
