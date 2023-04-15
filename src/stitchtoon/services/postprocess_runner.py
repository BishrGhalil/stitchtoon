import os
import subprocess

from ..services.global_logger import logFunc


class PostProcessRunner:
    def run(self, command, **kwargs: dict[str:any]):
        command_args = kwargs.get("postprocess_args", ())
        console_func = kwargs.get("console_func", print)
        return self.call_external_func(command, command_args, console_func)

    @logFunc(inclass=True)
    def call_external_func(self, command, command_args, console_func):
        proc = subprocess.Popen(
            [command, *command_args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
            universal_newlines=True,
            shell=True,
        )
        console_func("Post process started!\n")
        for line in proc.stdout:
            console_func(line)
        console_func("\nPost process finished successfully!\n")
        proc.stdout.close()
        return_code = proc.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)
