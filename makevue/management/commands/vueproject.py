from makevue.management.templates import ProjectCommand


class Command(ProjectCommand):
    """
    用于测试manage 命令的类
    """

    def handle(self, *args, **options):
        """
        必须重载的处理函数
        """
        project_name = options.pop('name')
        target = options.pop('directory')
        super().handle(project_name, target, **options)
