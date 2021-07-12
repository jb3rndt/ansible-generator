import platform


def main():
    if platform.system() == 'Linux':
        from ansgen.unixgenerator import generate_unix_playbook
        generate_unix_playbook()
    elif platform.system() == 'Windows':
        from ansgen.windowsgenerator import generate_windows_playbook
        generate_windows_playbook()
    else:
        print(f"Unsupported Platform: {platform.system()}\nTerminating without changes...")


if __name__ == "__main__":
    main()
