import logging

__all__ = [
    "LOGGER",
    "add_console_handler"
]

# 创建一个日志 Logger
LOGGER = logging.getLogger("metasequoia_java")
LOGGER.setLevel(logging.INFO)


def add_console_handler(level: int = logging.ERROR,
                        fmt: str = "%(asctime)s - %(name)s - %(pathname)s - %(lineno)d - %(levelname)s - %(message)s"
                        ) -> None:
    """添加控制台日志处理器

    Parameters
    ----------
    level : int
        日志等级
    fmt : str
        日志打印格式
    """
    # 如果日志等级低于 logging.INFO，则需要调整 LOGGER 的日志等级
    if level < logging.INFO:
        LOGGER.setLevel(level)

    # 创建一个写出到控制台的 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 设置日志格式
    formatter = logging.Formatter(fmt)
    console_handler.setFormatter(formatter)

    # 将 Handler 添加给 Logger
    LOGGER.addHandler(console_handler)
