CXX = g++
CXXFLAGS = -std=c++20 -O2 -Wall
TARGET = partxt
TARGET_EXT = partxt-ext

all: $(TARGET) $(TARGET_EXT)

$(TARGET): partxt.cpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) partxt.cpp

$(TARGET_EXT): partxt-ext.cpp
	$(CXX) $(CXXFLAGS) -o $(TARGET_EXT) partxt-ext.cpp

clean:
	rm -f $(TARGET) $(TARGET_EXT)

.PHONY: all clean
