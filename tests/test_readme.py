import re
from pathlib import Path

import pytest

FP_README = Path(__file__).parent.parent / "README.md"


def _load_readme_codeblocks():
    # find python code blocks in README.md
    code_blocks = []
    with open(FP_README) as f:
        lines = f.readlines()
        # use regex to find code blocks, match everything between ```python and ```
        re_codeblock = re.compile(r"```python(.*?)```", re.DOTALL)
        code_blocks = re_codeblock.findall("".join(lines))

    code_blocks = [
        code_block.strip()
        for code_block in code_blocks
        if not code_block.strip().startswith("# api docs")
    ]

    return code_blocks


README_CODEBLOCKS = _load_readme_codeblocks()


@pytest.mark.parametrize("code_block_number", range(len(README_CODEBLOCKS)))
def test_readme_codeblock(code_block_number):
    code_block = README_CODEBLOCKS[code_block_number]
    # check that code block is valid python by executing it
    try:
        exec(code_block)
    except Exception as ex:
        raise Exception(
            f"The following code block in README.md failed in its execution: \n\n{code_block}",
        ) from ex
