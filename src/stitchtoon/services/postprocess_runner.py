import os
import subprocess

from ..services.global_logger import logFunc


@logFunc
def postprocess_run(cmd: str, cmd_args: str = (), console=print):
    proc = subprocess.Popen(
        f"{cmd.strip()} {cmd_args.strip()}",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        universal_newlines=True,
        shell=True,
    )
    for line in proc.stdout:
        console(line)
    if not proc.stdout:
        proc.stdout.close()
    return_code = proc.wait()
    if return_code:
        console(str(subprocess.CalledProcessError(return_code, cmd)), "error")
    else:
        console("\n" + "-" * 15 + "\nPost process finished successfully!\n", "success")

    return return_code
