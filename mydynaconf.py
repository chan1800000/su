import os
import sys
from pathlib import Path
from dynaconf import Dynaconf

_BASE_DIR = Path(__file__).parent.parent
_CONFIG_DIR = _BASE_DIR / 'config'
LOG_DIR = _BASE_DIR / 'files' / 'logs'
TOKEN_FILE = _BASE_DIR / 'config' / 'xxl_job.token'
SHELVEDB_FILE = _BASE_DIR / 'DB' / 'SHELVE'

settings_files = [
    _CONFIG_DIR / 'settings.toml',
    _CONFIG_DIR / '.secrets.toml',
]  # 指定加载默认配置的绝对路径

settings = Dynaconf(
    envvar_prefix="CRM",  # 环境变量前缀。设置`MSP_FOO='bar'`，使用`settings.FOO`
    settings_files=settings_files,
    environments=False,  # 启用多层次日志，支持 dev, pro
    load_dotenv=True,  # 加载 .env
    env_switcher="MSP_ENV",  # 用于切换模式的环境变量名称 MSP_ENV=production
    lowercase_read=True,  # 禁用小写访问， settings.name 是不允许的
    includes=[os.path.join(sys.prefix, 'settings.toml')],  # 自定义配置覆盖默认配置
    base_dir=_BASE_DIR,  # 编码传入配置
)