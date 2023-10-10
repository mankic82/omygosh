import subprocess

def start_vm(vm_name: str) -> bool:
    try:
        result = subprocess.run(["VBoxManage", "startvm", vm_name], capture_output=True)
        return True
    except FileNotFoundError:
        print("VBoxManage 명령어를 찾을 수 없습니다. VirtualBox가 설치되어 있는지 확인해주세요.")
        return False
    except Exception as e:
        print(f"가상 머신을 시작하는 중에 오류가 발생했습니다: {e}")
        return False

def stop_vm(vm_name: str) -> bool:
    try:
        result = subprocess.run(["VBoxManage", "controlvm", vm_name, "poweroff"])
        return True
    except Exception as e:
        print(f"Error stopping VM: {e}")
        return False

def list_vm() -> list:
    try:
        result = subprocess.run(["VBoxManage", "list", "vms"], capture_output=True, text=True)
        vm_list = result.stdout.strip().split("\n")
        return [vm.split()[0].replace('"', '') for vm in vm_list]
    except Exception as e:
        print(f"Error listing VMs: {e}")
        return []

def snapshot_vm(vm_name: str, snapshot_name: str) -> bool:
    try:
        result = subprocess.run(["VBoxManage", "snapshot", vm_name, "take", snapshot_name])
        return True
    except Exception as e:
        print(f"Error taking snapshot: {e}")
        return False

def rollback_vm(vm_name: str, snapshot_name: str) -> bool:
    try:
        result = subprocess.run(["VBoxManage", "snapshot", vm_name, "restore", snapshot_name])
        return True
    except Exception as e:
        print(f"Error restoring snapshot: {e}")
        return False

if __name__ == "__main__":
    print(f"C:\\Program Files\\Oracle\\VirtualBox")
    vm_list = list_vm() 
    print("CLI로 조회한 가상 머신 목록:")
    for i, vm in enumerate(vm_list, start=1):
        print(f"{i}. {vm}")

    while True:
        try:
            selected_vm_index = int(input("제어할 가상 머신 번호를 입력하세요: ")) - 1
            if 0 <= selected_vm_index < len(vm_list):
                selected_vm_name = vm_list[selected_vm_index]  # 이름만 추출
            else:
                print("유효하지 않은 번호입니다.")
                continue
        except ValueError:
            print("잘못된 번호를 입력했습니다. 숫자를 입력해주세요.")
            continue

        action = input("1: 가상 머신 시작\\n2: 가상 머신 종료\\n3: 스냅샷 생성\\n4: 스냅샷 복구\\n수행할 작업을 선택하세요: ")

        if action == '1':
            print(start_vm(selected_vm_name))
        elif action == '2':
            print(stop_vm(selected_vm_name))
        elif action == '3':
            snapshot_name = input("생성할 스냅샷의 이름을 입력하세요: ")
            print(snapshot_vm(selected_vm_name, snapshot_name))
        elif action == '4':
            snapshot_name = input("복구할 스냅샷의 이름을 입력하세요: ")
            print(rollback_vm(selected_vm_name, snapshot_name))
        else:
            print("잘못된 작업을 선택했습니다.")

        continue_choice = input("계속하시겠습니까? (y/n): ")
        if continue_choice.lower() != 'y':
            break