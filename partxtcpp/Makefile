CXX = g++
CXXFLAGS = -std=c++20 -O2 -Wall
TARGET = partxt

all: $(TARGET)

$(TARGET): partxt.cpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) partxt.cpp

clean:
	rm -f $(TARGET)

.PHONY: all clean
