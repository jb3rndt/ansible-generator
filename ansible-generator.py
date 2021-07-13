import platform
from settings import plugins
import importlib

def loadPlugins(platform):
    return [importlib.import_module(f'ansgen.plugins.{platform}.{plugin}','.').Plugin() for plugin in plugins[platform]]

def main():
    if platform.system() == 'Linux':
        from ansgen.unixgenerator import generate_unix_playbook
        generate_unix_playbook(loadPlugins(platform.system()))
    elif platform.system() == 'Windows':
        from ansgen.windowsgenerator import generate_windows_playbook
        generate_windows_playbook(loadPlugins(platform.system()))
    else:
        print(f"Unsupported Platform: {platform.system()}\nTerminating without changes...")


if __name__ == "__main__":
    main()
