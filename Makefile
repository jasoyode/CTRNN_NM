OBJS = NeuromodulatedWalkerSearchMain.o TSearch.o CTRNN.o LeggedAgent.o random.o
CC = g++ 
DEBUG = -g
CFLAGS = -Wall -c $(DEBUG)
LFLAGS = -Wall -pthread $(DEBUG)

runExp : $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o runExp

NeuromodulatedWalkerSearchMain.o: NeuromodulatedWalkerSearchMain.cpp TSearch.h CTRNN.h LeggedAgent.h VectorMatrix.h random.h
	$(CC) $(CFLAGS) NeuromodulatedWalkerSearchMain.cpp

TSearch.o: TSearch.cpp TSearch.h VectorMatrix.h random.h
	$(CC) $(CFLAGS) TSearch.cpp

CTRNN.o: CTRNN.h CTRNN.cpp VectorMatrix.h random.h
	$(CC) $(CFLAGS) CTRNN.cpp

LeggedAgent.o : LeggedAgent.cpp LeggedAgent.h random.h CTRNN.h
	$(CC) $(CFLAGS) LeggedAgent.cpp

random.o : random.cpp random.h
	$(CC) $(CFLAGS) random.cpp
	
clean:
	\rm *.o *~ runExp

tar:
	tar cfv runExp.tar NeuromodulatedWalkerSearchMain.cpp TSearch.cpp TSearch.h CTRNN.cpp CTRNN.h LeggedAgent.cpp LeggedAgent.h VectorMatrix.h random.h \
SimpleWalkingMain.cpp cpg.ns WalkerSearchMain.cpp SimpleCTRNNMain.cpp SimpleSearchMain.cpp 
