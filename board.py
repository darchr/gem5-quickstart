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
This file defines a simple X86-based board with pre-configured values for the
memory, cache hierarchy, and processor. This board will only work in gem5's SE
mode. The clock frequency is 3 GHz for all components. The frequency is
optionally parameterized.

*Processor*: Single core processor. The core in a single-cycle processor which
executes every instruction in a single cycle except for memory instructions.
Instructions are fetched in-order and take at least 1 cycle to be fetched.

*Cache hierarchy*: Two-level hierarchy with 32 KiB split L1 I/D caches and a 
256 KiB L2 cache. All caches use a simple stride prefetcher. Optionally, the
L1 and L2 cache sizes are parameterized.

*Memory*: Single channel DDR4 2400 DIMM (32 GiB).
"""

from gem5.isas import ISA
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)

from gem5.components.memory.single_channel import SingleChannelDDR4_2400

from processor import OutOfOrderProcessor


class SimpleX86Board(SimpleBoard):
    def __init__(
        self,
        clock_frequency="3GHz",
        l1_size="32KiB",
        l2_size="256KiB",
        processor=SimpleProcessor(cpu_type=CPUTypes.TIMING, isa=ISA.X86, num_cores=1),
    ):
        memory = SingleChannelDDR4_2400()

        cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
            l1d_size=l1_size,
            l1i_size=l1_size,
            l2_size=l2_size,
        )

        super().__init__(
            clk_freq=clock_frequency,
            processor=processor,
            memory=memory,
            cache_hierarchy=cache_hierarchy,
        )


class OutOfOrderProcX86Board(SimpleX86Board):
    def __init__(
        self,
        clock_frequency="3GHz",
        l1_size="32KiB",
        l2_size="256KiB",
        width=4,
        lsq_depth=64,
        rob_entries=128,
    ):
        super().__init__(
            clock_frequency=clock_frequency,
            l1_size=l1_size,
            l2_size=l2_size,
            processor=OutOfOrderProcessor(
                width=width,
                lsq_depth=lsq_depth,
                rob_entries=rob_entries,
            ),
        )
