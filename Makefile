# LinuxRogue makefile
# by Ashwin N <ashwin@despammed.com> 

# Define either of KEYS_QWERTY or KEYS_DVORAK below
CFLAGS = -DKEYS_QWERTY -O2

CC = gcc

LDFLAGS = -lncurses 

SRC_DIR := src
OBJ_DIR := obj
BIN_DIR := bin
INC_DIR := include

EXE := $(BIN_DIR)/rogue
SRC := $(wildcard $(SRC_DIR)/*.c)
OBJ := $(SRC:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

.PHONY: all clean

all: $(EXE)

# $(OBJ) | $(BIN_DIR)

$(EXE): $(OBJ) | $(BIN_DIR)
	$(CC) $(OBJ) -o $@ $(LDFLAGS) 

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) -I$(INC_DIR) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(BIN_DIR) $(OBJ_DIR):
	mkdir -p $@

clean:
	@$(RM) -rv $(BIN_DIR) $(OBJ_DIR)

-include $(OBJ:.o=.d)
