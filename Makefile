CPP=g++
CPPFLAGS=-std=c++11 -I /usr/local/include
LDFLAGS=-L /usr/local/lib -lboost_program_options
EXE=run_gridwars

OBJ_DIR=obj
SRC_DIR=source

_DEPS=options.hpp
DEPS=$(patsubst %,$(SRC_DIR)/%,$(_DEPS))

_OBJ=main.o options.o
OBJ=$(patsubst %,$(OBJ_DIR)/%,$(_OBJ))

default: debug

debug: CPPFLAGS += -g
debug: build

release: CPPFLAGS += -O2
release: build

build: setup_build $(EXE)
	@echo "Build finished"

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp $(DEPS)
	$(CPP) $(CPPFLAGS) -c -o $@ $<

$(EXE): $(OBJ)
	$(CPP) $(CPPFLAGS) $(LDFLAGS) $^ -o $@

setup_build:
	@mkdir -p $(OBJ_DIR)

.PHONY: clean

clean:
	@echo "Cleaning"
	@rm -f $(OBJ_DIR)/*.o *~ $(SRC_DIR)/*~
