"""Read and write bounded UTF-8 text in the live Host script directory."""

from autojs6 import files, result


output = "m3-host-files-output.txt"
existed_before = files.exists(output)
files.write_text(output, "Host files broker round-trip: 写入成功\n")

result.set(
    {
        "content": files.read_text(output),
        "existedBefore": existed_before,
        "isFile": files.is_file(output),
        "rootIsDirectory": files.is_dir("."),
        "listed": output in files.list(),
    }
)
