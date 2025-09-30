import winreg


def get_windows_machine_guid():
    try:
        key = r"SOFTWARE\Microsoft\Cryptography"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as h:
            guid, _ = winreg.QueryValueEx(h, "MachineGuid")
            return str(guid)
    except Exception:
        return None


data = get_windows_machine_guid()

print(data)