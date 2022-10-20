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
This gem5 run script will run a binary passed in via an argument in SE mode.

This script creates a board that has a single x86-based CPU, a two-level cache
hierarchy, and a single channel of DDR4 memory.

If the binary has ROI annotations (`m5_work_begig` and `m5_work_end`) this
script will reset the stats at the beginning of the ROI and it will dump the
stats and exit at the end of the ROI unless `--ignore_roi` is set on the
command line.

After running the binary, the script prints the instructions, simulated time, 
and cycles. More detailed statistics can be found in the output directory
(`m5out/`) by default.
"""

from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.exit_event_generators import (
    reset_stats_generator,
    skip_generator,
    exit_generator,
)

from board import SimpleX86Board, OutOfOrderProcX86Board
from workload import mm_workload

from argparse import ArgumentParser


def setup_arguments():
    parser = ArgumentParser(
        description="Simple script to run the mm binary. By default, this "
        "scripts expects the mm binary will have ROI annotations and it will "
        "only return statistics for the ROI."
    )

    parser.add_argument(
        "--ignore_roi",
        action="store_true",
        default=False,
        help="Ignore the ROI annotations and run the whole workload",
    )

    parser.add_argument(
        "--processor_type",
        choices=["simple", "out-of-order"],
        help="Simple processor is an in-order single cycle CPU.",
        default="simple",
    )

    parser.add_argument(
        "--frequency",
        type=str,
        default="3GHz",
        help="The frequency of the system (processor and caches)",
    )
    parser.add_argument(
        "--l1_size",
        default="32KiB",
        type=str,
        help="Size of the L1D and L1I caches",
    )
    parser.add_argument(
        "--l2_size",
        type=str,
        default="256KiB",
        help="Size of unified L2 cache",
    )

    parser.add_argument(
        "--width",
        type=int,
        help="Width of the out-of-order processor",
        default=4,
    )
    parser.add_argument(
        "--lsq_depth",
        type=int,
        default=64,
        help="Number of entries in the LSQ (split evenly between load and "
        "store) for the out-of-order processor",
    )
    parser.add_argument(
        "--rob_entries",
        type=int,
        default=128,
        help="The number of entires in the reorder buffer of the out-of-order "
        "processor",
    )

    return parser.parse_args()


def print_stats_simple(stats):
    instructions = int(
        stats["board"]["processor"]["cores"]["core"]["exec_context.thread_0"][
            "numInsts"
        ]["value"]
    )
    cycles = int(
        stats["board"]["processor"]["cores"]["core"]["numCycles"]["value"]
    )
    ticks = int(
        stats["simulated_end_time"] - stats["simulated_begin_time"]
    )  # In 10^-12s (ps)

    print(f"Simulated time (ms): {ticks/1e9:0.5f}")
    print(f"Executed instructions: {instructions}")
    print(f"Cycles: {cycles}")


def print_stats_ooo(stats):
    instructions = int(
        stats["board"]["processor"]["cores"]["core"]["committedInsts"]["0"][
            "value"
        ]
    )
    executed_instructions = int(
        stats["board"]["processor"]["cores"]["core"]["numInsts"]["value"]
    )
    cycles = int(
        stats["board"]["processor"]["cores"]["core"]["numCycles"]["value"]
    )
    ticks = int(
        stats["simulated_end_time"] - stats["simulated_begin_time"]
    )  # In 10^-12s (ps)

    print(f"Simulated time (ms): {ticks/1e9:0.5f}")
    print(f"Committed instructions: {instructions}")
    print(f"Executed instructions: {executed_instructions}")
    print(f"Cycles: {cycles}")


if __name__ == "__m5_main__":
    args = setup_arguments()

    if args.processor_type == "simple":
        board = SimpleX86Board(
            clock_frequency=args.frequency,
            l1_size=args.l1_size,
            l2_size=args.l2_size,
        )
    elif args.processor_type == "out-of-order":
        board = OutOfOrderProcX86Board(
            clock_frequency=args.frequency,
            l1_size=args.l1_size,
            l2_size=args.l2_size,
            width=args.width,
            lsq_depth=args.lsq_depth,
            rob_entries=args.rob_entries,
        )
    else:
        raise Exception

    board.set_workload(mm_workload)

    if args.ignore_roi:
        begin_generator = skip_generator()
        end_generator = skip_generator()
    else:
        begin_generator = reset_stats_generator()
        end_generator = exit_generator()

    simulator = Simulator(
        board=board,
        on_exit_event={
            ExitEvent.WORKBEGIN: begin_generator,
            ExitEvent.WORKEND: end_generator,
        },
    )
    simulator.run()

    if args.processor_type == "simple":
        print_stats_simple(simulator.get_stats())
    else:
        print_stats_ooo(simulator.get_stats())
