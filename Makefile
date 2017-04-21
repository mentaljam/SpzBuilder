#### Functions

# Recursive file search function
rwildcard=$(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2) $(filter $(subst *,%,$2),$d))

# pyuic5 command
ifeq ($(OS),Windows_NT)
    python3 = $(addprefix "$(OSGEO4W_ROOT)",/bin/python3)
    pyuic5 = cmd //c $(python3) -m PyQt5.uic.pyuic
    pylupdate5 = cmd //c $(python3) -m PyQt5.pylupdate_main
else
    pyuic5 = pyuic5
    pylupdate5 = pylupdate5
endif


#### Configuration

# Locales
LOCALES      = ru_RU

# Files for localization
TO_LOCALIZE  = $(PY_FILES) \
			   $(UI_FILES)

# Plugin name
PLUGINNAME   = SpzBuilder

# List ui and uic files
UI_FILES     = $(wildcard ui/*.ui)
UIC_FILES    = $(patsubst ui/%.ui,ui/ui_%.py,$(UI_FILES))

# List ts and qm files
TS_FILES     = $(patsubst %,i18n/SpzBuilder_%.ts,$(LOCALES))
QM_FILES     = $(patsubst %.ts,%.qm,$(TS_FILES))

# List py and pyc files
PY_FILES     = $(call rwildcard,,*.py)
PYC_FILES    = $(patsubst %,%c,$(PY_FILES))

# List images
PNG_FILES	 = $(call rwildcard,,*.png)

# Install files
INSTALL_FILES = $(PY_FILES) \
                $(QM_FILES) \
                $(UIC_FILES) \
                $(PNG_FILES) \
                metadata.txt


#### Targets

default: ui qm

.PHONY : help
help:
	@echo
	@echo "------------------------------"
	@echo "        Build targets"
	@echo "------------------------------"
	@echo ui
	@echo qm
	@echo update_ts
	@echo update_ts_clean
	@echo package
	@echo clean

$(UIC_FILES): ui/ui_%.py : ui/%.ui
	@echo "uic: $@"
	@$(pyuic5) $< -o $@

ui: $(UIC_FILES)

$(QM_FILES): %.qm : %.ts
	@echo "qm:  $@"
	@lrelease -silent $<

qm: $(QM_FILES)

$(TS_FILES):
	@echo "ts:  $@"
	@$(pylupdate5) $(TO_LOCALIZE) -ts $@

update_ts:
	@echo
	@echo "------------------------------"
	@echo "    Updating translations"
	@echo "------------------------------"
	@$(foreach var,$(LOCALES),echo $(var); $(pylupdate5) $(TO_LOCALIZE) -ts $(TS_FILES);)
	@echo done!

update_ts_clean:
	@echo
	@echo "------------------------------"
	@echo "Removing obsolete translations"
	@echo "------------------------------"
	@$(foreach var,$(LOCALES),echo $(var); $(pylupdate5) $(TO_LOCALIZE) -ts $(TS_FILES) -noobsolete;)
	@echo done!

package: $(INSTALL_FILES)
	@echo
	@echo "------------------------------"
	@echo "      Preparing pachage"
	@echo "------------------------------"
	@rm -fv $(wildcard $(PLUGINNAME)*.zip)
	@$(eval ARCHIVE := $(PLUGINNAME)_$(strip $(shell awk -F = '/version/ {print $$2}' metadata.txt)).zip)
	@echo Adding files to $(ARCHIVE):
	@$(eval INSTALL_WITH_PREFIX := $(foreach file,$(INSTALL_FILES), $(PLUGINNAME)/$(file)))
	@cd ..; zip $(PLUGINNAME)/$(ARCHIVE) $(INSTALL_WITH_PREFIX)
	@echo done!

.PHONY : clean
clean:
	@echo
	@echo "------------------------------"
	@echo "           Cleaning"
	@echo "------------------------------"
	@rm -fv $(PYC_FILES)
	@rm -fv $(UIC_FILES)
	@rm -fv $(QM_FILES)
	@rm -fv $(wildcard $(PLUGINNAME)*.zip)
	@echo done!
