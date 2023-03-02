# This file is part of BenchExec, a framework for reliable benchmarking:
# https://github.com/sosy-lab/benchexec
#
# SPDX-FileCopyrightText: 2007-2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from benchexec.tools.sv_benchmarks_util import get_data_model_from_task, ILP32, LP64
import benchexec.tools.template
import benchexec.result as result


class Tool(benchexec.tools.template.BaseTool2):
    """
    Symbiotic tool info object
    """

    REQUIRED_PATHS = ["."]

    def executable(self, tool_locator):
        """
        Find the path to the executable file that will get executed.
        This method always needs to be overridden,
        and most implementations will look similar to this one.
        The path returned should be relative to the current directory.
        """
        return tool_locator.find_executable("sym-cpa.py")

    def version(self, executable):
        """
        Determine a version string for this tool, if available.
        """
        return "1.0.0"

    def name(self):
        """
        Return the name of the tool, formatted for humans.
        """
        return "sym-cpa"

    def cmdline(self, executable, options, task, rlimits):
        """
        Compose the command line to execute from the name of the executable
        """

        if task.property_file:
            options = options + [f"--prp={task.property_file}"]

        data_model_param = get_data_model_from_task(task, {ILP32: "--32", LP64: "--64"})
        if data_model_param and data_model_param == "--32" and data_model_param not in options:
            options += [data_model_param]

        return [executable] + options + list(task.input_files_or_identifier)

    def determine_result(self, run):
        if run.was_timeout:
            return result.RESULT_TIMEOUT

        if not run.output:
            return "error (no output)"

        lines = map(lambda l: l.strip(), run.output)
        results = filter(lambda l: l.startswith("RESULT: "), lines)
        results = list(map(lambda s: s.removeprefix("RESULT: "), results))

        if len(results) == 0:
            return result.RESULT_ERROR

        line = results[-1]

        if line == "true":
            return result.RESULT_TRUE_PROP
        elif line == "unknown":
            return result.RESULT_UNKNOWN
        elif line == "done":
            return result.RESULT_DONE
        elif line.startswith("false(valid-deref)"):
            return result.RESULT_FALSE_DEREF
        elif line.startswith("false(valid-free)"):
            return result.RESULT_FALSE_FREE
        elif line.startswith("false(valid-memtrack)"):
            return result.RESULT_FALSE_MEMTRACK
        elif line.startswith("false(valid-memcleanup)"):
            return result.RESULT_FALSE_MEMCLEANUP
        elif line.startswith("false(no-overflow)"):
            return result.RESULT_FALSE_OVERFLOW
        elif line.startswith("false(termination)"):
            return result.RESULT_FALSE_TERMINATION
        elif line.startswith("false"):
            return result.RESULT_FALSE_REACH

        return line
