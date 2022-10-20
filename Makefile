GEM5_ROOT ?= ../

all: mm mm-gem5

clean:
	rm mm mm-gem5

mm: mm.cpp
	g++ -o mm mm.cpp -O2 

mm-gem5: mm.cpp
	g++ -o mm-gem5 -static mm.cpp -O2 -I$(GEM5_ROOT)/include -DGEM5 -L$(GEM5_ROOT)/util/m5/build/x86/out -lm5