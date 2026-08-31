# Thin wrapper so you can run `make start` (etc.) from inside this
# assistant's own directory without passing APP= by hand. Loads this
# assistant's .env for its APP_KEY, then delegates the target to the
# root Makefile, which does the actual work.
#
# e.g. `make start` here == `make -C ../.. start APP=banking_assistant`
# from the repo root.

ROOT := ../..
ROOT_ABS := $(abspath $(ROOT))

-include .env

APP_KEY := $(APP_KEY)
WORKING_DIR := $(patsubst $(ROOT_ABS)/%,%,$(CURDIR))

%:
	$(MAKE) -C $(ROOT) $@ APP_KEY=$(APP_KEY) WORKING_DIR=$(WORKING_DIR)
