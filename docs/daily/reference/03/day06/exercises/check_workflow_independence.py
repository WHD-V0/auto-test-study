import subprocess
import sys

module = "tests/workflow/test_tasks_extended.py"
a = module + "::test_my_crud"
b = module + "::test_list_user_isolation"
runs = [[a], [module], [module], [a, b], [b, a], [module, "-n", "2"]]
for args in runs:
    print("RUN", " ".join(args), flush=True)
    subprocess.run([sys.executable, "-B", "-m", "pytest", *args, "-q"], check=True)
print("单独、重复、交换顺序、双worker：全部通过")
