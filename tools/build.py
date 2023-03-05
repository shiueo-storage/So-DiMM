import os.path
import pathlib
import subprocess
import time

from tools import clear


def build(
    withconsole,
    path,
    file_dict,
    companyname,
    product_version,
    icon,
    plugin_dict,
    include_package_dict,
):
    try:
        clear.code_format_and_make_requirements_txt(path=os.path.dirname(path))
        buildfile_name = path
        Output_dir_name = os.path.join(
            os.path.dirname(path), f"{pathlib.Path(path).stem}_build"
        )

        should_include = []
        if file_dict is not None:
            for i in range(0, len(file_dict)):
                should_include.append(os.path.join(os.path.dirname(path), file_dict[i]))

        command = (
            f"python -m nuitka --clang --show-modules --follow-imports "
            f"--windows-company-name={companyname} --windows-product-version={product_version} "
            f"--output-dir={Output_dir_name} --verbose --assume-yes-for-downloads --onefile "
        )
        for i in range(0, len(should_include)):
            command += f"--include-data-dir={should_include[i]}={file_dict[i]} "
        for i in range(0, len(plugin_dict)):
            command += f"--enable-plugin={plugin_dict[i]} "
        if include_package_dict is not None:
            for i in range(0, len(include_package_dict)):
                command += f"--include-package={include_package_dict[i]} "

        if withconsole:
            if icon is None:
                command = command + f"{buildfile_name}"
            else:
                command = (
                    command + f"--windows-icon-from-ico={icon} " + f"{buildfile_name}"
                )
        else:
            if icon is None:
                command = command + f"--windows-disable-console " + f"{buildfile_name}"
            else:
                command = (
                    command
                    + f"--windows-disable-console "
                    + f"--windows-icon-from-ico={icon} "
                ) + f"{buildfile_name}"

        start = time.time()
        subprocess.run(command, shell=True, check=True)
        end = time.time()

        print(f"{end - start}s 사용됨")
        print(command)
    except Exception as e:
        print(e)
