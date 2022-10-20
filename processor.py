# Copyright (c) 2022 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This file defines a single core out of order processor for X86.

The width, LSQ depth, and reorder buffer entries are parameterized. Other
configuration parameters have default values. See 
`gem5/src/cpu/o3/BaseO3CPU.py` for defaults
"""

from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes

from m5.objects import X86O3CPU

class OutOfOrderCore(BaseCPUCore):
    """
    An out of order core for X86.
    The LSQ depth (split equally between loads and stores), the width of the
    core, and the number of entries in the reorder buffer are configurable.
    """
    def __init__(self, core_id, lsq_depth, width, rob_entries):
        super().__init__(core=X86O3CPU(cpu_id=core_id), isa=ISA.X86)
        self.core.fetchWidth = width
        self.core.decodeWidth = width
        self.core.renameWidth = width
        self.core.dispatchWidth = width
        self.core.wbWidth = width
        self.core.issueWidth = width
        self.core.commitWidth = width
        self.core.squashWidth = width

        self.core.LQEntries = lsq_depth / 2
        self.core.SQEntries = lsq_depth / 2

        self.core.numROBEntries = rob_entries


class OutOfOrderProcessor(BaseCPUProcessor):
    """
    A single core out of order processor for X86.
    The LSQ depth (split equally between loads and stores), the width of the
    core, and the number of entries in the reorder buffer are configurable.
    """

    def __init__(self, lsq_depth=32, width=4, rob_entries=128):
        self._cpu_type = CPUTypes.O3
        super().__init__(
            cores=[
                OutOfOrderCore(
                    core_id=0,
                    lsq_depth=lsq_depth,
                    width=width,
                    rob_entries=rob_entries,
                )
            ]
        )
