CC=gcc
CC_FLAGS=-c -Werror -Wall -Wextra -fPIC
EMCC_FLAGS=-Wall -Werror -Wextra -I libtetris/src -DRECORD_TRANSACTIONS
EXE_NAME=tetris
OUTPUT_DIR=output
SRC_DIR=src
BUILD_DIR=build
EMSDK_REPO=https://github.com/emscripten-core/emsdk.git
SOURCE_FILES=$(SRC_DIR)/wasm.c libtetris/src/libtetris.c libtetris/src/bag.c libtetris/src/piece.c libtetris/src/framebuffer.c

SHELL:=/usr/bin/env bash

all: wasm

output:
	mkdir -p $(OUTPUT_DIR)/www
	mkdir -p $(BUILD_DIR)

submodule:
	git submodule update --remote --init

lib:
	cd libtetris; make lib; cd ..

wasm: output font $(OUTPUT_DIR)/www/index.html $(OUTPUT_DIR)/www/style.css $(OUTPUT_DIR)/www/game.js $(OUTPUT_DIR)/www/background.jpg venv

font:
	cp $(SRC_DIR)/html_template/digital-7.mono.ttf $(OUTPUT_DIR)/www/

$(OUTPUT_DIR)/www/style.css: $(SRC_DIR)/html_template/style.css
	cp $(SRC_DIR)/html_template/style.css $(OUTPUT_DIR)/www/style.css
$(OUTPUT_DIR)/www/game.js: $(SRC_DIR)/html_template/game.js
	cp $(SRC_DIR)/html_template/game.js $(OUTPUT_DIR)/www/game.js
$(OUTPUT_DIR)/www/background.jpg: $(SRC_DIR)/html_template/background.jpg
	cp $(SRC_DIR)/html_template/background.jpg $(OUTPUT_DIR)/www/background.jpg
$(OUTPUT_DIR)/www/index.html: libtetris emsdk $(SRC_DIR)/html_template/template.html
	source $(BUILD_DIR)/emsdk/emsdk_env.sh && emcc $(EMCC_FLAGS) $(SOURCE_FILES) -o $(OUTPUT_DIR)/www/index.html --shell-file $(SRC_DIR)/html_template/template.html -s NO_EXIT_RUNTIME=1 -s "EXPORTED_RUNTIME_METHODS=['ccall']"

emsdk:
ifeq ("$(wildcard $(BUILD_DIR)/emsdk)","")
	@echo "Cloning EMSDK repo"
	git clone $(EMSDK_REPO) $(BUILD_DIR)/emsdk
else
	@echo "Updating EMSDK repo"
	cd $(BUILD_DIR)/emsdk && git pull
endif
	$(BUILD_DIR)/emsdk/emsdk install latest
	$(BUILD_DIR)/emsdk/emsdk activate latest

clean:
	rm -rf $(OUTPUT_DIR)

venv:
ifeq ("$(wildcard $(BUILD_DIR)/.venv)","")
	python3 -m venv $(BUILD_DIR)/.venv
else
	@echo "Virtual environment exists."
endif
	source $(BUILD_DIR)/.venv/bin/activate && pip install websockets
	@echo "To run the websocket server run \`make start\`"

start: lib
	source $(BUILD_DIR)/.venv/bin/activate && python3 src/db.py

update:
	git pull

install: update wasm
	cp output/www/* /var/www/tetris/

